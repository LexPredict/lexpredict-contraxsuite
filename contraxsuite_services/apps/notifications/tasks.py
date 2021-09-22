"""
    Copyright (C) 2017, ContraxSuite, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    You can also be released from the requirements of the license by purchasing
    a commercial license from ContraxSuite, LLC. Buying such a license is
    mandatory as soon as you develop commercial activities involving ContraxSuite
    software without disclosing the source code of your own applications.  These
    activities include: offering paid services to customers as an ASP or "cloud"
    provider, processing documents on the fly in a web application,
    or shipping ContraxSuite within a closed source product.
"""
# -*- coding: utf-8 -*-

import datetime
import numbers
import pickle
import time
import uuid
from typing import Optional, Any, Set, Dict, Tuple, List, Callable

import tzlocal
from billiard.exceptions import SoftTimeLimitExceeded
from celery import shared_task
from celery.utils.log import get_task_logger
from dateutil.parser import parse
from django.db import connection
from django.db.models import Prefetch, Min
from django.utils.timezone import now
from psycopg2 import InterfaceError, OperationalError

from apps.celery import app
from apps.common.collection_utils import chunks
from apps.common.models import ObjectStorage
from apps.common.redis import push
from apps.common.sql_commons import fetch_bool, SQLClause
from apps.document.models import Document, DocumentField, DocumentType
from apps.notifications.document_notification import DocumentNotification
from apps.notifications.models import DocumentDeletedEvent, DocumentLoadedEvent, \
    DocumentChangedEvent, DocumentAssignedEvent, DocumentNotificationSubscription, \
    DocumentDigestConfig, WebNotificationStorage
from apps.notifications.notifications import render_digest, RenderedDigest, \
    RenderedNotification, DocumentNotificationSource
from apps.notifications.notification_renderer import NotificationRenderer
from apps.rawdb.field_value_tables import build_field_handlers
from apps.rawdb.constants import FIELD_CODE_ASSIGNEE_ID
from apps.rawdb.rawdb.rawdb_field_handlers import RawdbFieldHandler
from apps.rawdb.signals import DocumentEvent
from apps.task.tasks import ExtendedTask, call_task, CeleryTaskLogger
from apps.task.utils.task_utils import TaskUtils
from apps.users.models import User
import task_names

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


MODULE_NAME = __name__

CACHE_DOC_NOTIFICATION_PREFIX = 'DocumentNotification_'

logger = get_task_logger(__name__)


class SendDigest(ExtendedTask):
    name = 'Send Digest'
    soft_time_limit = 6000
    default_retry_delay = 10
    retry_backoff = True
    autoretry_for = (SoftTimeLimitExceeded, InterfaceError, OperationalError,)
    max_retries = 3
    priority = 9

    PARAM_CONFIG = 'config'
    PARAM_CONFIG_ID = 'config_id'
    PARAM_USER = 'user'
    PARAM_USER_ID = 'user_id'
    PARAM_USER_IDS = 'user_ids'
    PARAM_RUN_DATE = 'run_date'
    PARAM_RUN_EVEN_IF_NOT_ENABLED = 'run_even_if_not_enabled'

    def process(self, **kwargs):
        self.log_info(f'SendDigest kwargs are: {kwargs}')
        if self.PARAM_CONFIG in kwargs:
            config_id = kwargs[self.PARAM_CONFIG]['pk']
        else:
            config_id = kwargs[self.PARAM_CONFIG_ID]

        ptr_user = kwargs.get(self.PARAM_USER, None)
        if ptr_user:
            user_ids = {ptr_user['pk']}
        elif kwargs.get(self.PARAM_USER_ID, None):
            user_ids = {kwargs.get(self.PARAM_USER_ID)}
        else:
            user_ids = kwargs.get(self.PARAM_USER_IDS)

        run_date = kwargs.get(self.PARAM_RUN_DATE)
        run_date_specified = run_date is not None

        if isinstance(run_date, str):
            run_date = parse(run_date)

        run_date = run_date or datetime.datetime.now(tz=tzlocal.get_localzone())

        run_even_if_not_enabled = bool(kwargs.get(self.PARAM_RUN_EVEN_IF_NOT_ENABLED))

        config = DocumentDigestConfig.objects \
            .filter(pk=config_id).select_related('for_user').first()  # type: DocumentDigestConfig
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
        elif config.for_user_id is not None:
            users_qr = User.objects.get(pk=config.for_user_id)
        else:
            self.log_error('{what} #{config_id} should specify for_user.'
                           .format(what=DocumentDigestConfig.__name__, config_id=config.pk))
            return

        log = CeleryTaskLogger(self)
        for user in users_qr:  # type: User
            if config.for_user_id != user.id:
                self.log_error('{what} #{what_id} is not applicable for user {user_name} (#{user_id})'
                               .format(what=DocumentDigestConfig.__name__,
                                       what_id=config.pk,
                                       user_name=user.name,
                                       user_id=user.pk))
                continue

            try:
                digest = render_digest(config=config, dst_user=user, run_date=run_date)
                if digest:
                    digest.send(log)
            except Exception as e:
                self.log_error(f'Unable to send {RenderedDigest}.\n'
                               f'Config: #{config.pk}\n'
                               f'Dst user: {user.name} #{user.pk}\n'
                               f'Run date: {run_date}', exc_info=e)
                raise Exception('Error while rendering digest') from e


def _as_ints(csv: str):
    return {int(s.strip()) for s in csv.split(',')} if csv else None


def _send_digest_scheduled(run_date: datetime) -> bool:
    with connection.cursor() as cursor:
        sql = '''select exists(select id from task_task 
        where name = %s and (kwargs->>'run_date')::timestamptz = %s)'''
        return fetch_bool(cursor, SQLClause(sql, [SendDigest.name, run_date]))


@shared_task(base=ExtendedTask,
             bind=True,
             name=task_names.TASK_NAME_TRIGGER_DIGESTS,
             soft_time_limit=600,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError),
             max_retries=0)
def trigger_digests(_task):
    now_local = datetime.datetime.now(tz=tzlocal.get_localzone())
    user_ids_to_timezones = {}  # type: Dict[int, datetime.tzinfo]
    all_user_ids = set()  # type: Set[int]

    for user_id, timezone in User.objects.values_list('pk', 'timezone'):
        timezone = timezone or tzlocal.get_localzone()
        user_ids_to_timezones[user_id] = timezone
        all_user_ids.add(user_id)

    for config_id, for_user_id, \
        run_at_month, run_at_day_of_month, run_at_day_of_week, run_at_hour, run_at_minute \
            in DocumentDigestConfig.objects \
            .filter(enabled=True) \
            .values_list('pk', 'for_user_id', 'run_at_month', 'run_at_day_of_month',
                         'run_at_day_of_week', 'run_at_hour', 'run_at_minute'):

        run_at_month = _as_ints(run_at_month)
        run_at_day_of_month = _as_ints(run_at_day_of_month)
        run_at_day_of_week = _as_ints(run_at_day_of_week)
        run_at_hour = _as_ints(run_at_hour)
        run_at_minute = int(run_at_minute)

        for_user_ids = set()
        if for_user_id:
            for_user_ids.add(for_user_id)

        tz_to_user_ids_delta_date = {}  # type: Dict[str, Tuple[Set[int], int, datetime.datetime]]

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


def send_notification(package_id: str,
                      event: str,
                      document_id: int,
                      field_values: Dict[str, Any],
                      changes: Dict[str, Tuple[Any, Any]] = None,
                      changed_by_user: User = None):
    ntf = DocumentNotification(
        event=event,
        document_id=document_id,
        field_values=field_values,
        package_id=package_id,
        changes=changes,
        changed_by_user_id=changed_by_user.pk)
    EmailNotificationPool.push_notification(ntf, event)


def process_notifications_on_document_change(
        log_routine: Callable[[str], None],
        document_event: str,
        document_id: int,
        fields_before: Optional[Dict],
        fields_after: Optional[Dict],
        changed_by_user_id: int):
    document_type_id = Document.all_objects.filter(pk=document_id).values_list(
        'document_type', flat=True).first()  # type: str
    document_type = DocumentType.objects.get(pk=document_type_id)  # type: DocumentType
    changed_by_user = User.objects.get(pk=changed_by_user_id)  # type: User
    field_handlers = build_field_handlers(document_type,
                                          include_annotation_fields=False)  # List[RawdbFieldHandler]
    field_handlers_by_field_code = {h.field_code: h for h in field_handlers}  # Dict[str, RawdbFieldHandler]

    log_msgs = []
    package_id = uuid.uuid4().hex

    if document_event == DocumentEvent.CREATED.value or fields_before is None:
        if fields_after.get(FIELD_CODE_ASSIGNEE_ID) is not None:
            send_notification(package_id=package_id,
                              event=DocumentAssignedEvent.code,
                              document_id=document_id,
                              field_values=fields_after,
                              changed_by_user=changed_by_user)

        send_notification(package_id=package_id,
                          event=DocumentLoadedEvent.code,
                          document_id=document_id,
                          field_values=fields_after,
                          changed_by_user=changed_by_user)
    elif document_event == DocumentEvent.DELETED.value:
        send_notification(package_id=package_id,
                          event=DocumentDeletedEvent.code,
                          document_id=document_id,
                          field_values=fields_before,
                          changed_by_user=changed_by_user)
    else:
        changes = {}
        for field_code, old_value in fields_before.items():
            if field_code not in field_handlers_by_field_code:
                continue
            new_value = fields_after.get(field_code)
            if not values_look_equal(old_value, new_value):
                changes[field_code] = (old_value, new_value)
                log_msgs.append(format_values_difference(field_code, old_value, new_value))

        if not changes:
            return

        if len(log_msgs) > 0:
            msgs_str = 'Following fields are different:\n    ' + '\n    '.join(log_msgs)
            log_routine(msgs_str)

        if FIELD_CODE_ASSIGNEE_ID in changes:
            send_notification(package_id=package_id,
                              event=DocumentAssignedEvent.code,
                              document_id=document_id,
                              field_values=fields_after,
                              changes=changes,
                              changed_by_user=changed_by_user)

        send_notification(package_id=package_id,
                          event=DocumentChangedEvent.code,
                          document_id=document_id,
                          field_values=fields_after,
                          changes=changes,
                          changed_by_user=changed_by_user)


class EmailNotificationPool:
    DOC_NOTIFICATION_EVENTS = {
        DocumentLoadedEvent.code,
        DocumentDeletedEvent.code,
        DocumentChangedEvent.code,
        DocumentAssignedEvent.code
    }

    batch_size = 10

    batch_seconds = 15

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 name=task_names.TASK_NAME_CHECK_EMAIL_POOL,
                 soft_time_limit=60,
                 max_retries=3,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 default_retry_delay=10)
    def check_email_pool(_task) -> None:
        log = CeleryTaskLogger(_task)
        errors = []  # type: List[Tuple[str, Any]]
        for event in EmailNotificationPool.DOC_NOTIFICATION_EVENTS:
            cache_key = f'{CACHE_DOC_NOTIFICATION_PREFIX}{event}'
            try:
                cached_msgs_count = ObjectStorage.objects.filter(pk__startswith=cache_key).count()
                if not cached_msgs_count:
                    continue
                if cached_msgs_count < EmailNotificationPool.batch_size:
                    lastest_msg_time = ObjectStorage.objects.filter(
                        pk__startswith=cache_key).aggregate(Min('last_updated'))
                    lastest_msg_time = [lastest_msg_time[k] for k in lastest_msg_time][0]
                    delta = now() - lastest_msg_time
                    if delta.seconds < EmailNotificationPool.batch_seconds:
                        continue

                ntfs = []  # type:List[DocumentNotification]
                for raw_msg in ObjectStorage.objects.filter(pk__startswith=cache_key):  # type: ObjectStorage
                    try:
                        msg = pickle.loads(raw_msg.data)  # type: DocumentNotification
                        ntfs.append(msg)
                    except Exception as e:
                        er_msg = 'send_notifications_packet() - error unpickling raw_msg.data'
                        log.error(er_msg)
                        errors.append((er_msg, e,))

                if not ntfs:
                    continue
            except Exception as e:
                log.error(f'Error in check_email_pool(), extracting pool messages: {e}')
                continue
            try:
                log.info(f'send_notifications_packet({len(ntfs)})')
                EmailNotificationPool.send_notifications_packet(ntfs, event, _task)
            except Exception as e:
                log.error(f'Error in check_email_pool(), sending package: {e}')
                errors.append(('Error in check_email_pool(), sending package', e))

            try:
                ObjectStorage.objects.filter(pk__startswith=cache_key).delete()
            except Exception as e:
                log.error(f'Error in check_email_pool(), deleting pool objects: {e}')
                errors.append(('Error in check_email_pool(), deleting pool objects', e))
                continue
        if errors:
            er_msg = '\n'.join([m for m, _ in errors])
            raise RuntimeError(er_msg) from errors[0][1]

    @staticmethod
    def push_notification(msg: DocumentNotification,
                          event: str) -> None:
        cache_key = f'{CACHE_DOC_NOTIFICATION_PREFIX}{event}_{uuid.uuid4().hex}'
        ObjectStorage.update_or_create(
            key=cache_key,
            value_obj=msg)

    @staticmethod
    def send_notifications_packet(ntfs: List[DocumentNotification],
                                  event: str,
                                  task: ExtendedTask):
        documents_data = list(Document.all_objects.filter(
            pk__in={d.document_id for d in ntfs}))  # type: List[Document]
        doc_type_by_id = {dt.document_type.pk: dt.document_type for dt in documents_data}
        doc_types = [doc_type_by_id[pk] for pk in doc_type_by_id]

        doc_by_id = {}  # type: Dict[int, Document]
        for doc in documents_data:
            doc_by_id[doc.pk] = doc

        users = User.objects.filter(pk__in={d.changed_by_user_id for d in ntfs})
        user_by_id = {u.pk: u for u in users}

        handlers_by_doctype = {d: build_field_handlers(d, include_annotation_fields=False)
                               for d in doc_types}  # type:Dict[str, List[RawdbFieldHandler]]

        log = CeleryTaskLogger(task)

        # { (doc_type, event,) : [notification0, notification1, ...], ... }
        messages_by_subscr_key = {}  # type: Dict[Tuple[str, str], List[DocumentNotification]]
        # { (doc_type, event,) : [DocumentNotificationSubscription0, ... ], ... }
        subscr_by_key = {}  # type: Dict[Tuple[str, str], List[DocumentNotificationSubscription]]

        for ntf in ntfs:
            if ntf.document_id not in doc_by_id:
                continue
            document = doc_by_id[ntf.document_id]
            key = (document.document_type, ntf.event,)
            if key in messages_by_subscr_key:
                messages_by_subscr_key[key].append(ntf)
            else:
                subscriptions = DocumentNotificationSubscription.objects \
                    .filter(enabled=True,
                            document_type=document.document_type,
                            event=event,
                            recipients__isnull=False) \
                    .select_related('specified_user') \
                    .prefetch_related(Prefetch('user_fields',
                                               queryset=DocumentField.objects.order_by('order')))
                subscr_by_key[key] = subscriptions
                messages_by_subscr_key[key] = [ntf]

        notifications_to_send = []  # type: List[RenderedNotification]
        errors = []  # type: List[Tuple[str, Any]]

        for key in messages_by_subscr_key:
            messages = messages_by_subscr_key[key]
            subscriptions = subscr_by_key[key]
            for sub in subscriptions:
                for msg_pack in chunks(messages, sub.max_stack):
                    # render pack of notifications or just one notification
                    if len(msg_pack) < 2:
                        # render single notification
                        if msg_pack[0].document_id not in doc_by_id or \
                                not doc_by_id[msg_pack[0].document_id]:
                            raise Exception(f'Error in send_notifications_packet(1): doc '
                                            f'with id={msg_pack[0].document_id} was not obtained')
                        document = doc_by_id[msg_pack[0].document_id]
                        handlers = handlers_by_doctype[document.document_type]
                        user = user_by_id[msg_pack[0].changed_by_user_id]

                        try:
                            notification = NotificationRenderer.render_notification(
                                msg_pack[0].package_id,
                                sub,
                                DocumentNotificationSource(
                                    document=document,
                                    field_handlers=handlers,
                                    field_values=msg_pack[0].field_values,
                                    changes=msg_pack[0].changes,
                                    changed_by_user=user),
                                log_routine=log.error)
                            if notification:
                                notifications_to_send.append(notification)
                        except Exception as e:
                            msg = '''Error in send_notifications_packet(1),
                                     sending render_notification()'''
                            errors.append((msg, e,))
                            log.error(msg, exc_info=e)
                    else:
                        not_sources = []  # List[DocumentNotificationSource
                        # render pack of notifications in a single message
                        for msg in msg_pack:
                            if msg.document_id not in doc_by_id or \
                                    not doc_by_id[msg.document_id]:
                                raise Exception(f'Error in send_notifications_packet({len(msg_pack)}: doc '
                                                f'with id={msg.document_id} was not obtained')

                            document = doc_by_id[msg.document_id]
                            handlers = handlers_by_doctype[document.document_type]
                            user = user_by_id[msg.changed_by_user_id]
                            not_src = DocumentNotificationSource(
                                document=document,
                                field_handlers=handlers,
                                field_values=msg.field_values,
                                changes=msg.changes,
                                changed_by_user=user)
                            not_sources.append(not_src)
                        try:
                            notifications = NotificationRenderer.render_notification_pack(
                                [m.package_id for m in msg_pack],
                                sub, not_sources)
                            notifications_to_send += notifications
                        except Exception as e:
                            msg = '''Error in send_notifications_packet(),
                                     sending render_notification()'''
                            errors.append((msg, e,))
                            log.error(msg, exc_info=e)

        errors_note = '' if not errors else f', {len(errors)} errors'
        log.info(f'notification.send({len(notifications_to_send)}){errors_note}')
        for notification in notifications_to_send:
            notification.send(log=log)
        if errors:
            msg = '\n'.join([m for m, _ in errors])
            if len(errors) > 1:
                msg += f'\n{len(errors)} errors totally.'
            raise RuntimeError(msg) from errors[0][1]


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

    if isinstance(a, numbers.Number) and isinstance(b, numbers.Number):
        a = float(a)
        b = float(b)

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


@app.task
def send_web_notifications():
    """Collects web notifications, that are in storage, in packs and sends them through websocket
    """
    TaskUtils.prepare_task_execution()
    storage = WebNotificationStorage()
    push(storage.REDIS_IS_COLLECTING_TASKS_KEY, 'False')
    notifications = storage.extract()
    for notification in notifications:
        notification.send()
    logger.info(f"{len(notifications)} web notification messages was sent to users")
