import datetime
from collections import defaultdict
from typing import Optional, Any
from typing import Set, Dict, Tuple, List
from dateutil.parser import parse

import tzlocal
from billiard.exceptions import SoftTimeLimitExceeded
from celery import shared_task
from django.conf import settings
from django.db import connection
from django.db.models import Prefetch
from psycopg2 import InterfaceError, OperationalError

from apps.celery import app
from apps.common.errors import render_error
from apps.common.log_utils import ProcessLogger
from apps.common.sql_commons import fetch_bool, SQLClause
from apps.document.models import Document, DocumentField
from apps.rawdb.field_value_tables import FIELD_CODE_ASSIGNEE_ID, build_field_handlers
from apps.rawdb.rawdb.field_handlers import FieldHandler
from apps.rawdb.signals import DocumentEvent
from apps.task.tasks import BaseTask, ExtendedTask, call_task
from apps.task.tasks import CeleryTaskLogger
from apps.users.models import User
from .models import DocumentDeletedEvent, DocumentLoadedEvent, DocumentChangedEvent, \
    DocumentAssignedEvent, DocumentNotificationSubscription
from .models import DocumentDigestConfig
from .notifications import render_digest, RenderedDigest, render_notification

MODULE_NAME = __name__


class SendDigest(BaseTask):
    name = 'Send Digest'
    soft_time_limit = 6000
    default_retry_delay = 10
    retry_backoff = True
    autoretry_for = (SoftTimeLimitExceeded, InterfaceError, OperationalError,)
    max_retries = 3

    PARAM_CONFIG = 'config'
    PARAM_CONFIG_ID = 'config_id'
    PARAM_USER = 'user'
    PARAM_USER_IDS = 'user_ids'
    PARAM_RUN_DATE = 'run_date'
    PARAM_RUN_EVEN_IF_NOT_ENABLED = 'run_even_if_not_enabled'

    def process(self, **kwargs):
        if self.PARAM_CONFIG in kwargs:
            config_id = kwargs[self.PARAM_CONFIG]['pk']
        else:
            config_id = kwargs[self.PARAM_CONFIG_ID]

        if self.PARAM_USER in kwargs:
            user_ids = {kwargs[self.PARAM_USER]['pk']}
        else:
            user_ids = kwargs.get(self.PARAM_USER_IDS)

        run_date = kwargs.get(self.PARAM_RUN_DATE)
        run_date_specified = run_date is not None

        if isinstance(run_date, str):
            run_date = parse(run_date)

        run_date = run_date or datetime.datetime.now(tz=tzlocal.get_localzone())

        run_even_if_not_enabled = bool(kwargs.get(self.PARAM_RUN_EVEN_IF_NOT_ENABLED))

        config = DocumentDigestConfig.objects \
            .filter(pk=config_id).select_related('for_role', 'for_user').first()  # type: DocumentDigestConfig
        if not config:
            self.log_error('{1} not found: #{0}'.format(config_id, DocumentDigestConfig.__name__))
            return

        if not config.enabled and not run_even_if_not_enabled:
            self.log_info('{1} #{0} is disabled.'.format(config_id, DocumentDigestConfig.__name__))
            return

        tz_msg = ' at timezone {0}'.format(run_date.tzname()) if run_date_specified else ''
        self.log_info('Rendering and sending {what} #{pk} ({doc_filter}) for date "{run_date}" to {n} users{tz_msg}'
                      .format(what=DocumentDigestConfig.__name__,
                              pk=config.pk, doc_filter=config.documents_filter, n=len(user_ids), run_date=run_date,
                              tz_msg=tz_msg))

        if user_ids:
            users_qr = User.objects.filter(pk__in=user_ids)
        elif config.for_role_id is not None:
            users_qr = User.objects.filter(role_id=config.for_role_id)
        elif config.for_user_id is not None:
            users_qr = User.objects.get(pk=config.for_user_id)
        else:
            self.log_error('{what} #{config_id} specifies neither for_user nor for_role.'
                           .format(what=DocumentDigestConfig.__name__, config_id=config.pk))
            return

        log = CeleryTaskLogger(self)
        for user in users_qr:  # type: User
            if config.for_user_id != user.id and (config.for_role_id is None or config.for_role_id != user.role_id):
                self.log_error('{what} #{what_id} is not applicable for user {user_name} (#{user_id})'
                               .format(what=DocumentDigestConfig.__name__,
                                       what_id=config.pk,
                                       user_name=user.get_full_name(),
                                       user_id=user.pk))
                continue

            try:
                digest = render_digest(config=config, dst_user=user, run_date=run_date)
                if digest:
                    digest.send(log)
            except:
                msg = render_error('Unable to send {what}.\n'
                                   'Config: #{config_id}\n'
                                   'Dst user: {user_name} #{user_id}\n'
                                   'Run date: {run_date}'.format(what=RenderedDigest,
                                                                 config_id=config.pk,
                                                                 user_name=user.get_full_name(),
                                                                 user_id=user.pk,
                                                                 run_date=run_date))
                self.log_error(msg)


def _as_ints(csv: str):
    return {int(s.strip()) for s in csv.split(',')} if csv else None


def _send_digest_scheduled(run_date: datetime) -> bool:
    with connection.cursor() as cursor:
        sql = '''select exists(select id from task_task 
        where name = %s and (kwargs->>'run_date')::timestamptz = %s)'''
        return fetch_bool(cursor, SQLClause(sql, [SendDigest.name, run_date]))


@shared_task(base=ExtendedTask,
             bind=True,
             name=settings.TASK_NAME_TRIGGER_DIGESTS,
             soft_time_limit=600,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError),
             max_retries=0)
def trigger_digests(_task):
    now_local = datetime.datetime.now(tz=tzlocal.get_localzone())
    role_ids_to_user_ids = defaultdict(set)  # type: Dict[int, Set[int]]
    user_ids_to_timezones = dict()  # type: Dict[int, datetime.tzinfo]
    all_user_ids = set()  # type: Set[int]

    for user_id, role_id, timezone in \
            User.objects.all().values_list('pk', 'role_id', 'timezone'):  # type: int, int, datetime.tzinfo
        role_ids_to_user_ids[role_id].add(user_id)
        timezone = timezone or tzlocal.get_localzone()
        user_ids_to_timezones[user_id] = timezone
        all_user_ids.add(user_id)

    for config_id, for_user_id, for_role_id, \
        run_at_month, run_at_day_of_month, run_at_day_of_week, run_at_hour, run_at_minute \
            in DocumentDigestConfig \
            .objects \
            .filter(enabled=True) \
            .values_list('pk', 'for_user_id', 'for_role_id',
                         'run_at_month', 'run_at_day_of_month', 'run_at_day_of_week', 'run_at_hour', 'run_at_minute'):

        run_at_month = _as_ints(run_at_month)
        run_at_day_of_month = _as_ints(run_at_day_of_month)
        run_at_day_of_week = _as_ints(run_at_day_of_week)
        run_at_hour = _as_ints(run_at_hour)
        run_at_minute = int(run_at_minute)

        for_user_ids = set()
        if for_user_id:
            for_user_ids.add(for_user_id)
        if for_role_id:
            for_user_ids.update(role_ids_to_user_ids[for_role_id])

        tz_to_user_ids_delta_date = dict()  # type: Dict[str, Tuple[Set[int], int, datetime.datetime]]

        for user_id in for_user_ids:
            timezone = user_ids_to_timezones[user_id]  # type: datetime.tzinfo
            now_in_tz = now_local.astimezone(timezone)

            if run_at_month and now_in_tz.month not in run_at_month:
                continue
            if run_at_day_of_month and now_in_tz.day not in run_at_day_of_month:
                continue
            if run_at_day_of_week and now_in_tz.isoweekday() not in run_at_day_of_week:
                continue
            if run_at_hour and now_in_tz.hour not in run_at_hour:
                continue

            tz_name = timezone.tzname(dt=None)
            if tz_name not in tz_to_user_ids_delta_date:
                if run_at_minute is None:
                    run_date_in_tz = now_in_tz
                    delta = 0
                else:
                    run_date_in_tz = now_in_tz.replace(minute=run_at_minute, second=0, microsecond=0)
                    delta = (run_date_in_tz - now_in_tz).total_seconds() if run_date_in_tz > now_in_tz else 0
                tz_to_user_ids_delta_date[tz_name] = ({user_id}, delta, run_date_in_tz)
            else:
                tz_to_user_ids_delta_date[tz_name][0].add(user_id)

        for tz_name, user_ids_delta_run_date in tz_to_user_ids_delta_date.items():
            user_ids, delta, run_date_in_tz = user_ids_delta_run_date  # type: Set[int], int, datetime.datetime
            if not _send_digest_scheduled(run_date_in_tz):
                call_task(SendDigest.name,
                          module_name=MODULE_NAME,
                          **{SendDigest.PARAM_USER_IDS: user_ids,
                             SendDigest.PARAM_CONFIG_ID: config_id,
                             SendDigest.PARAM_RUN_DATE: run_date_in_tz,
                             'countdown': delta})


def send_notification(log: ProcessLogger,
                      already_sent_user_ids: Set,
                      event: str,
                      document: Document,
                      field_handlers: List[FieldHandler],
                      field_values: Dict[str, Any],
                      changes: Dict[str, Tuple[Any, Any]] = None,
                      changed_by_user: User = None):
    document_type = document.document_type
    subscriptions = DocumentNotificationSubscription.objects \
        .filter(enabled=True, document_type=document_type, event=event, recipients__isnull=False) \
        .select_related('specified_user', 'specified_role') \
        .prefetch_related(Prefetch('user_fields', queryset=DocumentField.objects.all().order_by('order')))
    for s in subscriptions:  # type: DocumentNotificationSubscription
        notification = render_notification(already_sent_user_ids=already_sent_user_ids,
                                           subscription=s,
                                           document=document,
                                           field_handlers=field_handlers,
                                           field_values=field_values,
                                           changes=changes,
                                           changed_by_user=changed_by_user)
        if notification:
            already_sent_user_ids.update({u.id for u in notification.dst_users})
            notification.send(log=log)


@shared_task(base=ExtendedTask,
             bind=True,
             soft_time_limit=600,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError),
             max_retries=0)
def process_notifications_on_document_change(task: ExtendedTask,
                                             document_event: str,
                                             document_id,
                                             fields_before: Optional[Dict],
                                             fields_after: Optional[Dict],
                                             changed_by_user_id):
    log = CeleryTaskLogger(task)

    document = Document.objects.filter(pk=document_id).select_related('document_type').first()  # type: Document
    document_type = document.document_type
    changed_by_user = User.objects.get(pk=changed_by_user_id)
    field_handlers = build_field_handlers(document_type, include_suggested_fields=False)
    field_handlers_by_field_code = {h.field_code: h for h in field_handlers}  # Dict[str, FieldHandler]
    already_sent_user_ids = set()

    log_msgs = []

    if document_event == DocumentEvent.CREATED.value:
        if fields_after.get(FIELD_CODE_ASSIGNEE_ID) is not None:
            send_notification(event=DocumentAssignedEvent.code,
                              log=log,
                              already_sent_user_ids=already_sent_user_ids,
                              document=document,
                              field_handlers=field_handlers,
                              field_values=fields_after,
                              changed_by_user=changed_by_user)

        send_notification(event=DocumentLoadedEvent.code,
                          log=log,
                          already_sent_user_ids=already_sent_user_ids,
                          document=document,
                          field_handlers=field_handlers,
                          field_values=fields_after,
                          changed_by_user=changed_by_user)
    elif document_event == DocumentEvent.DELETED.value:
        send_notification(event=DocumentDeletedEvent.code,
                          log=log,
                          already_sent_user_ids=already_sent_user_ids,
                          document=document,
                          field_handlers=field_handlers,
                          field_values=fields_before,
                          changed_by_user=changed_by_user)
    else:
        changes = dict()
        for field_code, old_value in fields_before.items():
            if field_code not in field_handlers_by_field_code \
                    or field_handlers_by_field_code[field_code].is_suggested:
                continue
            new_value = fields_after.get(field_code)
            if not values_look_equal(old_value, new_value):
                changes[field_code] = (old_value, new_value)
                log_msgs.append(format_values_difference(field_code, old_value, new_value))

        if not changes:
            return

        if len(log_msgs) > 0:
            msgs_str = 'Following fields are different:\n    ' + '\n    '.join(log_msgs)
            log = CeleryTaskLogger(task)
            log.info(msgs_str)


        if FIELD_CODE_ASSIGNEE_ID in changes:
            send_notification(event=DocumentAssignedEvent.code,
                              log=log,
                              already_sent_user_ids=already_sent_user_ids,
                              document=document,
                              field_handlers=field_handlers,
                              field_values=fields_after,
                              changes=changes,
                              changed_by_user=changed_by_user)

        send_notification(event=DocumentChangedEvent.code,
                          log=log,
                          already_sent_user_ids=already_sent_user_ids,
                          document=document,
                          field_handlers=field_handlers,
                          field_values=fields_after,
                          changes=changes,
                          changed_by_user=changed_by_user)


app.register_task(SendDigest())


def format_values_difference(field_code: str, old_value, new_value) -> str:
    tp = old_value.__class__.__name__ if old_value is not None \
        else new_value.__class__.__name__ if new_value is not None \
        else 'None'
    return '%s (%s): [%s], [%s]' % (field_code, tp, str(old_value), str(new_value))


def values_look_equal(a, b) -> bool:
    if a == b:
        return True

    if (isinstance(a, str) and not a and not b) or (isinstance(b, str) and not b and not a):
        return True

    import numbers
    if isinstance(a, numbers.Number) and isinstance(b, numbers.Number):
        delta = abs(a - b)
        da = 0 if a == 0 else 100 * delta / abs(a)
        db = 0 if b == 0 else 100 * delta / abs(b)
        dmax = max(da, db)
        # delta less than 0.001%
        return dmax < 0.001

    try:
        sa = str(a)
        sb = str(b)
        if sa == sb:
            return True
    except:
        pass
    return False
