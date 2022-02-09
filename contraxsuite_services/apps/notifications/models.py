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
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Set

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.deletion import CASCADE
from django.dispatch import receiver
from django.urls import reverse

from apps.common.model_utils.improved_django_json_encoder import ImprovedDjangoJSONEncoder
from apps.common.redis import lpush, llen, lrange, ltrim, push, pop
from apps.common.signals import post_bulk_create
from apps.common.singleton import Singleton
from apps.common.sql_commons import SQLClause
from apps.document.models import DocumentType, DocumentField
from apps.rawdb.constants import FIELD_CODE_CREATE_DATE, FIELD_CODE_IS_REVIEWED, \
    FIELD_CODE_IS_COMPLETED, FIELD_CODE_ASSIGNEE_ID, FIELD_CODE_ASSIGN_DATE
from apps.rawdb.field_value_tables import query_documents, \
    DocumentQueryResults
from apps.rawdb.rawdb.query_parsing import SortDirection
from apps.users.models import User
from apps.websocket.websockets import Websockets
from apps.websocket.channel_message import ChannelMessage
from apps.websocket import channel_message_types as message_types

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from task_names import TASK_NAME_DOCUMENT_CHANGED


class DocFilter:
    code = None
    title = None
    period_aware = False
    subject = None
    header = None
    message_if_no_docs = None

    def prepare_documents(self,
                          document_type: DocumentType,
                          user: User,
                          field_codes: List[str],
                          period_start: datetime.datetime,
                          period_end: datetime.datetime) -> Optional[DocumentQueryResults]:
        return None


class DocFilterUncompletedDocuments(DocFilter):
    code = 'uncompleted_documents'
    title = 'Uncompleted documents of the destination user'
    period_aware = False
    subject = 'Contraxsuite: digest of uncompleted documents'
    header = 'The following uncompleted documents are assigned to you ({{ to_user.name }}):'
    message_if_no_docs = '''There are no uncompleted documents assigned to you ({{ to_user.name }}).'''

    def prepare_documents(self,
                          document_type: DocumentType,
                          user: User,
                          field_codes: List[str],
                          period_start: datetime.datetime,
                          period_end: datetime.datetime) -> DocumentQueryResults:
        return query_documents(requester=None,
                               document_type=document_type,
                               field_codes=field_codes,
                               order_by=[(FIELD_CODE_ASSIGN_DATE, SortDirection.ASC)],
                               filters_sql=SQLClause('{assignee_id} = %s and {f} = False'
                                                     .format(assignee_id=FIELD_CODE_ASSIGNEE_ID,
                                                             f=FIELD_CODE_IS_COMPLETED), [user.pk]),
                               return_total_count=False,
                               return_reviewed_count=False,
                               limit=1000)


class DocFilterNonReviewedDocuments(DocFilter):
    code = 'non_reviewed_documents'
    title = 'Non-reviewed documents of the destination user'
    period_aware = False
    subject = 'Contraxsuite: digest of non-reviewed documents'
    header = 'The following non-reviewed documents are assigned to you ({{ to_user.name }}):'
    message_if_no_docs = '''There are no non-reviewed documents assigned to you ({{ to_user.name }}).'''

    def prepare_documents(self,
                          document_type: DocumentType,
                          user: User,
                          field_codes: List[str],
                          period_start: datetime.datetime,
                          period_end: datetime.datetime) -> DocumentQueryResults:
        return query_documents(requester=None,
                               document_type=document_type,
                               field_codes=field_codes,
                               order_by=[(FIELD_CODE_ASSIGN_DATE, SortDirection.ASC)],
                               filters_sql=SQLClause('{assignee_id} = %s and {f} = False'
                                                     .format(assignee_id=FIELD_CODE_ASSIGNEE_ID,
                                                             f=FIELD_CODE_IS_REVIEWED), [user.pk]),
                               return_total_count=False,
                               return_reviewed_count=False,
                               limit=1000)


class DocFilterAssignedDocuments(DocFilter):
    code = 'new_assigned_documents'
    title = 'Documents assigned to the destination user during the period'
    period_aware = True
    subject = '''{% if documents.documents|length == 1 %}Contraxsuite: document assigned to you: {{ documents.documents[0].document_name }}{% else %}Contraxsuite: {{documents.documents|length}} documents assigned to you{% endif %}'''
    header = 'The following documents have been assigned to you ({{ to_user.name }}):'
    message_if_no_docs = '''There are no new documents assigned to you ({{ to_user.name }}) during the digest period.'''

    def prepare_documents(self,
                          document_type: DocumentType,
                          user: User,
                          field_codes: List[str],
                          period_start: datetime.datetime,
                          period_end: datetime.datetime) -> DocumentQueryResults:
        return query_documents(requester=None,
                               document_type=document_type,
                               field_codes=field_codes,
                               order_by=[(FIELD_CODE_ASSIGN_DATE, SortDirection.ASC)],
                               filters_sql=SQLClause(
                                   '{assignee_id} = %s and {f} >= %s and {f} <= %s'
                                       .format(assignee_id=FIELD_CODE_ASSIGNEE_ID, f=FIELD_CODE_ASSIGN_DATE),
                                   [user.pk, period_start, period_end]),
                               return_total_count=False,
                               return_reviewed_count=False,
                               limit=1000)


class DocFilterLoadedDocuments(DocFilter):
    code = 'loaded_documents'
    title = 'Documents loaded into the projects the user has access to'
    period_aware = True
    subject = '''{% if documents.documents|length == 1 %}Contraxsuite: document loaded: {{documents.documents[0].document_name}}{% else %}Contraxsuite: {{documents.documents|length}} documents loaded{% endif %}'''
    header = 'The following documents have been loaded into the projects to which you ({{ to_user.name }}) have access:'
    message_if_no_docs = '''There are no new documents loaded during the digest period into the projects to which you ({{ to_user.name }}) have access.'''

    def prepare_documents(self,
                          document_type: DocumentType,
                          user: User,
                          field_codes: List[str],
                          period_start: datetime.datetime,
                          period_end: datetime.datetime) -> DocumentQueryResults:
        return query_documents(requester=user,
                               document_type=document_type,
                               field_codes=field_codes,
                               order_by=[(FIELD_CODE_ASSIGN_DATE, SortDirection.ASC)],
                               filters_sql=SQLClause(
                                   '{f} >= %s and {f} <= %s'.format(f=FIELD_CODE_CREATE_DATE),
                                   [period_start, period_end]),
                               return_total_count=False,
                               return_reviewed_count=False,
                               limit=1000)


DOC_FILTERS = [DocFilterAssignedDocuments(), DocFilterLoadedDocuments(),
               DocFilterNonReviewedDocuments(), DocFilterUncompletedDocuments()]

DOC_FILTERS_BY_CODE = {df.code: df for df in DOC_FILTERS}  # type: Dict[str, DocFilter]
DOC_FILTER_CHOICES = ((df.code, df.title) for df in DOC_FILTERS)


class DigestPeriod:
    code = None
    title = None

    def prepare_period(self, config: 'DocumentDigestConfig',
                       dst_user: User,
                       run_date: datetime.datetime) -> Tuple[datetime.datetime, datetime.datetime]:
        pass


class PeriodAfterLastRun(DigestPeriod):
    code = 'after_last_run'
    title = 'After last run'

    def prepare_period(self, config: 'DocumentDigestConfig', dst_user: User, run_date: datetime.datetime) \
            -> Tuple[datetime.datetime, datetime.datetime]:
        period_start = DocumentDigestSendDate.objects \
            .filter(config=config, to=dst_user).order_by('-date').values_list('date', flat=True).first()

        if not period_start:
            period_start = (run_date - datetime.timedelta(days=run_date.weekday())) \
                .replace(hour=0, minute=0, second=0, microsecond=0)

        return period_start.astimezone(dst_user.get_time_zone()), run_date.astimezone(dst_user.get_time_zone())


class PeriodThisDay(DigestPeriod):
    code = 'this_day'
    title = 'This day'

    def prepare_period(self, config: 'DocumentDigestConfig', dst_user: User, run_date: datetime.datetime) \
            -> Tuple[datetime.datetime, datetime.datetime]:
        day_start = run_date.replace(hour=0, minute=0, second=0, microsecond=0)
        return day_start.astimezone(dst_user.get_time_zone()), run_date.astimezone(dst_user.get_time_zone())


class PeriodPrevDay(DigestPeriod):
    code = 'prev_day'
    title = 'Previous day'

    def prepare_period(self, config: 'DocumentDigestConfig', dst_user: User, run_date: datetime.datetime) \
            -> Tuple[datetime.datetime, datetime.datetime]:
        this_day_start = run_date.replace(hour=0, minute=0, second=0, microsecond=0)
        prev_day_start = this_day_start - datetime.timedelta(days=1)
        return prev_day_start.astimezone(dst_user.get_time_zone()), this_day_start.astimezone(dst_user.get_time_zone())


class PeriodThisWeek(DigestPeriod):
    code = 'this_week'
    title = 'This week'

    def prepare_period(self, config: 'DocumentDigestConfig', dst_user: User,
                       run_date: datetime.datetime) \
            -> Tuple[datetime.datetime, datetime.datetime]:
        period_start = (run_date - datetime.timedelta(days=run_date.weekday())) \
            .replace(hour=0, minute=0, second=0, microsecond=0)
        return period_start.astimezone(dst_user.get_time_zone()), \
               run_date.astimezone(dst_user.get_time_zone())


class PeriodPrevWeek(DigestPeriod):
    code = 'prev_week'
    title = 'Previous week'

    def prepare_period(self, config: 'DocumentDigestConfig', dst_user: User,
                       run_date: datetime.datetime) \
            -> Tuple[datetime.datetime, datetime.datetime]:
        this_week_start = (run_date - datetime.timedelta(days=run_date.weekday())) \
            .replace(hour=0, minute=0, second=0, microsecond=0)
        prev_week_start = this_week_start - datetime.timedelta(days=7)
        return prev_week_start.astimezone(dst_user.get_time_zone()), \
               this_week_start.astimezone(dst_user.get_time_zone())


DIGEST_PERIODS = [PeriodAfterLastRun(), PeriodPrevDay(), PeriodPrevWeek(), PeriodThisDay(),
                  PeriodThisWeek()]

DIGEST_PERIODS_BY_CODE = {p.code: p for p in DIGEST_PERIODS}  # type: Dict[str, DigestPeriod]
DIGEST_PERIOD_CHOICES = ((p.code, p.title) for p in DIGEST_PERIODS)

TEMPLATE_CONTEXT_HINT = '''to_user: User, event_initiator: User, documents: List[Dict[str, Any]], 
    period_start: datetime, period_end: datetime'''


def document_digest_config_generic_fields_default():
    return ['status_name']


class DocumentDigestConfig(models.Model):
    template_name = 'document_digest'

    DAY_OF_WEEK_CHOICES = (
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
        (7, 'Sunday')
    )

    enabled = models.BooleanField(null=False, blank=False, default=False)

    document_type = models.ForeignKey(DocumentType, blank=False, null=False, on_delete=CASCADE)

    documents_filter = models.CharField(max_length=100, blank=False, null=False, choices=DOC_FILTER_CHOICES)

    still_send_if_no_docs = models.BooleanField(null=False, blank=False, default=False)

    message_if_no_docs = models.CharField(max_length=1024, null=True, blank=True, help_text='''Template of the 
        message replacing the header and the document table in case the document filter returned no documents.  
        Jinja2 syntax. Leave empty for using the default. Example: {0}'''.format(DocFilterLoadedDocuments
                                                                                 .message_if_no_docs))

    period = models.CharField(max_length=100, blank=True, null=True, choices=DIGEST_PERIOD_CHOICES)

    for_user = models.ForeignKey(User, null=True, blank=True, on_delete=CASCADE)

    subject = models.CharField(max_length=1024, null=True, blank=True, help_text='''Template of the email subject in 
    Jinja2 syntax. Leave empty for using the default. Example: {0}'''.format(DocFilterLoadedDocuments.subject))

    header = models.CharField(max_length=2048, null=True, blank=True, help_text='''Template of the header
    in Jinja2 syntax. Leave empty for using the default. Example: {0}'''.format(DocFilterLoadedDocuments.header))

    generic_fields = JSONField(encoder=ImprovedDjangoJSONEncoder,
                               default=document_digest_config_generic_fields_default)

    user_fields = models.ManyToManyField(DocumentField, blank=True, help_text='''Fields of the documents to 
    render in the email. Should match the specified document type. Leave empty for rendering all fields.
    ''')

    run_at_month = models.CharField(null=True, blank=True, max_length=100,
                                    help_text='''One or more comma separated month numbers (1 - 12). 
                                    Leave empty to run at every month. 
                                    Example: 1,3,5.''')

    run_at_day_of_month = models.CharField(null=True, blank=True, max_length=100,
                                           help_text='''One or more comma separated day of month numbers (1 - 31).
                                           Leave empty to run at every day.
                                           Days missing in a particular month are ignored.
                                           Example: 1, 10, 20, 30''')

    run_at_day_of_week = models.CharField(null=True, blank=True, max_length=100,
                                          help_text='''One or more comma separated day of ISO week day numbers 
                                          (1 Mon - 7 Sunday). Example: 1,3,5 (Monday, Wednesday, Friday)''')

    run_at_hour = models.CharField(null=True, blank=True, max_length=100,
                                   help_text='''One or more comma separated hours (0 - 23).
                                    Leave empty for running every hour.
                                    Example: 9''')

    run_at_minute = models.CharField(null=False, blank=False, max_length=2, default='0',
                                     help_text='''Minute of hour to run at (0 - 59). 
                                   Should be used to shuffle server load. 
                                   Example: 30''')

    def __str__(self):
        return '{document_type}: {documents_filter} for period {period} (#{pk})' \
            .format(pk=self.pk,
                    document_type=self.document_type.code,
                    documents_filter=self.documents_filter,
                    period=self.period)


class DocumentDigestSendDate(models.Model):
    config = models.ForeignKey(DocumentDigestConfig, null=False, blank=False, db_index=True,
                               on_delete=CASCADE)

    to = models.ForeignKey(User, null=False, blank=False, db_index=True, on_delete=CASCADE)

    date = models.DateTimeField(blank=False, null=False, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['config', 'to', '-date']),
        ]

    @staticmethod
    def store_digest_sent(config: DocumentDigestConfig, to: User, date: datetime.datetime):
        DocumentDigestSendDate.objects.create(config=config, to=to, date=date)
        DocumentDigestSendDate.objects.filter(config=config, to=to, date__lt=date).delete()


class DocumentEvent:
    code = None
    title = None
    default_subject = None
    default_header = None
    default_bulk_subject = None
    default_bulk_header = None


class DocumentLoadedEvent:
    code = 'document_loaded'
    title = 'Document loaded'
    default_subject = 'Document loaded: {{ document.document_name }}'
    default_header = 'Document "{{ document.document_name }}" has been loaded into the system'
    default_bulk_subject = 'Documents loaded ({{ documents|length }})'
    default_bulk_header = '{{ documents|length }} document(s) have been loaded into the system'


class DocumentDeletedEvent:
    code = 'document_deleted'
    title = 'Document deleted'
    default_subject = 'Document deleted: {{ document.document_name }}'
    default_header = 'Document "{{ document.document_name }}" has been deleted from system'
    default_bulk_subject = 'Documents deleted ({{ documents|length }})'
    default_bulk_header = '{{ documents|length }} document(s) have been deleted from system'


class DocumentChangedEvent:
    code = 'document_changed'
    title = TASK_NAME_DOCUMENT_CHANGED
    default_subject = 'Document changed: {{ document.document_name }} '
    default_header = 'Document "{{ document.document_name }}" has been changed'
    default_bulk_subject = 'Documents changed ({{ documents|length }})'
    default_bulk_header = '{{ documents|length }} document(s) have been changed'


class DocumentAssignedEvent:
    code = 'document_assigned'
    title = 'Document assigned'
    default_subject = 'Document assigned: {{ document.document_name }}'
    default_header = 'Document "{{ document.document_name }}" assigned to ' \
                     '{{ document.assignee_name }}'
    default_bulk_subject = 'Documents assigned ({{ documents|length }})'
    default_bulk_header = '{{ documents|length }} document(s) have been assigned'


class NotificationRecipients:
    code = None
    title = None

    def resolve(self, subscription: 'DocumentNotificationSubscription',
                document_fields: Dict[str, Any]) \
            -> Optional[List[User]]:
        pass


class CurrentAssignee(NotificationRecipients):
    code = 'current_assignee'
    title = 'Current assignee'

    def resolve(self, subscription: 'DocumentNotificationSubscription',
                document_fields: Dict[str, Any]) \
            -> Optional[List[User]]:
        assignee_id = document_fields.get(FIELD_CODE_ASSIGNEE_ID)
        return [User.objects.get(pk=assignee_id)] if assignee_id is not None else None


class SpecifiedUser(NotificationRecipients):
    code = 'specified_user'
    title = 'Specified user'

    def resolve(self,
                subscription: 'DocumentNotificationSubscription',
                document_fields: Dict[str, Any]) -> Optional[List[User]]:
        return [subscription.specified_user]


NOTIFICATION_RECIPIENTS = [CurrentAssignee(), SpecifiedUser()]
NOTIFICATION_RECIPIENTS_BY_CODE = {
    d.code: d for d in NOTIFICATION_RECIPIENTS
}  # type: Dict[str, NotificationRecipients]
NOTIFICATION_RECIPIENTS_CHOICES = ((d.code, d.title) for d in NOTIFICATION_RECIPIENTS)

DOCUMENT_EVENTS = [DocumentLoadedEvent(), DocumentChangedEvent(), DocumentAssignedEvent()]
DOCUMENT_EVENTS_BY_CODE = {e.code: e for e in DOCUMENT_EVENTS}
DOCUMENT_EVENTS_CHOICES = ((e.code, e.title) for e in DOCUMENT_EVENTS)


def document_notification_subscription_generic_fields_default():
    return ['status_name']


class DocumentNotificationSubscription(models.Model):
    template_name = 'document_notification'

    enabled = models.BooleanField(null=False, blank=False, default=False)

    document_type = models.ForeignKey(DocumentType, blank=False, null=False, on_delete=CASCADE)

    event = models.CharField(max_length=100, blank=False, null=False,
                             choices=DOCUMENT_EVENTS_CHOICES)

    recipients = models.CharField(max_length=100, blank=False, null=False,
                                  choices=NOTIFICATION_RECIPIENTS_CHOICES)

    specified_user = models.ForeignKey(User, blank=True, null=True, on_delete=CASCADE)

    recipients_cc = models.CharField(max_length=1024, blank=True, null=True, help_text='''Semi-colon separated list of 
    emails to add as CC to each notification email.''')

    subject = models.CharField(max_length=1024, null=True, blank=True, help_text='''Template of the email subject in 
        Jinja2 syntax. Leave empty for using the default. Example: {0}'''.format(DocumentLoadedEvent.default_subject))

    header = models.CharField(max_length=2048, null=True, blank=True,
                              help_text='''Template of the header in Jinja2 syntax. Leave empty for using the default. 
                              Example: {0}'''.format(DocumentLoadedEvent.default_header))

    generic_fields = JSONField(encoder=ImprovedDjangoJSONEncoder,
                               default=document_notification_subscription_generic_fields_default,
                               blank=True, null=True)

    user_fields = models.ManyToManyField(DocumentField, blank=True, help_text='''Fields of the documents to 
        render in the email. Should match the specified document type. Leave empty for rendering all fields.
        ''')

    max_stack = models.IntegerField(blank=True, default=1, null=False,
                                    help_text='Messages limit per email.')

    def get_recipients_info(self) -> Optional[NotificationRecipients]:
        if not self.recipients:
            return None
        return NOTIFICATION_RECIPIENTS_BY_CODE.get(self.recipients)

    def resolve_recipients(self, document_fields: Dict[str, Any]) -> Optional[Set[User]]:
        recipients_info = self.get_recipients_info()

        if not recipients_info:
            return None

        return recipients_info.resolve(self, document_fields)

    @classmethod
    def get_addrs(cls, semicolon_separated) -> Optional[Set[str]]:
        if not semicolon_separated:
            return None
        return {addr.strip() for addr in semicolon_separated.split(';')}

    def get_cc_addrs(self):
        return self.get_addrs(self.recipients_cc)

    def get_event_info(self) -> Optional[DocumentEvent]:
        if not self.event:
            return None
        return DOCUMENT_EVENTS_BY_CODE.get(self.event)


@Singleton
class WebNotificationStorage:
    REDIS_KEY = 'web_notification_list'
    NOTIFICATION_BATCH_SIZE = 10
    # CRITICAL_NOTIFICATION_BATCH_SIZE is to control situations when there are too much \
    # notifications in the storage or celery was crashed
    CRITICAL_NOTIFICATION_BATCH_SIZE = 100
    SEND_TIME_DELAY_SECONDS = 2
    REDIS_IS_COLLECTING_TASKS_KEY = 'is_collecting_web_notifications'

    def process(self, web_notification_message):
        from apps.notifications.tasks import send_web_notifications
        self.add(web_notification_message)
        # sometimes redis value has additional bytes, that's why `in` is used
        if 'True' not in (pop(self.REDIS_IS_COLLECTING_TASKS_KEY) or '') \
                or llen(self.REDIS_KEY) >= self.CRITICAL_NOTIFICATION_BATCH_SIZE:
            push(self.REDIS_IS_COLLECTING_TASKS_KEY, 'True')
            send_web_notifications.apply_async(countdown=self.SEND_TIME_DELAY_SECONDS)

    def add(self, web_notification_message):
        lpush(self.REDIS_KEY, web_notification_message)

    def extract(self):
        if llen(self.REDIS_KEY) > self.NOTIFICATION_BATCH_SIZE:
            notification_messages = lrange(self.REDIS_KEY, start=0,
                                           end=self.NOTIFICATION_BATCH_SIZE-1)
            ltrim(self.REDIS_KEY, start=self.NOTIFICATION_BATCH_SIZE, end=-1)
        else:
            notification_messages = lrange(self.REDIS_KEY, start=0, end=-1, delete=True)
        return notification_messages


class WebNotificationTypes(Enum):
    DOCUMENT_ASSIGNED = {
        'type': "document_assigned",
        'template': 'Document "{document}" was assigned to {assignee} by {action_creator}',
        'template_keywords': ['document', 'assignee', 'action_creator'],
        'link_type': 'document',
    }
    DOCUMENT_UNASSIGNED = {
        'type': "document_unassigned",
        'template': 'Document "{document}" was unassigned from {assignee} by {action_creator}',
        'template_keywords': ['document', 'assignee', 'action_creator'],
        'link_type': 'project-grid',
    }
    CLAUSES_ASSIGNED = {
        'type': "clauses_assigned",
        'template': '{count} clause{plural} assigned to {assignee} by {action_creator} in project '
                    '"{project}"',
        'template_keywords': ['count', 'plural', 'assignee', 'action_creator', 'project'],
        'link_type': 'project-clause-grid',
    }
    CLAUSES_UNASSIGNED = {
        'type': "clauses_unassigned",
        'template': '{count} clause{plural} unassigned from {assignee} by {action_creator} in '
                    'project "{project}"',
        'template_keywords': ['count', 'plural', 'assignee', 'action_creator', 'project'],
        'link_type': 'project-grid',
    }
    DOCUMENTS_UPLOADED = {
        'type': "documents_uploaded",
        'template': '{count} document{plural} uploaded to project "{project}"',
        'template_keywords': ['count', 'plural', 'project'],
        'link_type': 'project-grid',
    }
    DOCUMENT_DELETED = {
        'type': "document_deleted",
        'template': 'Document "{document}" was deleted from project "{project}"',
        'template_keywords': ['document', 'project'],
        'link_type': 'project-grid',
    }
    DOCUMENT_ADDED = {
        'type': "document_added",
    }
    DOCUMENT_STATUS_CHANGED = {
        'type': "document_status_updated",
        'template': 'Status for document "{document}" was changed to {status} by {action_creator}',
        'template_keywords': ['document', 'status', 'action_creator'],
        'link_type': 'document',
    }
    CLUSTER_IMPORTED = {
        'type': "cluster_imported",
        'template': 'Cluster "{cluster}", with {documents_count} documents, was imported '
                    'to project "{project}"',
        'template_keywords': ['cluster', 'documents_count', 'project'],
        'link_type': 'project-grid',
    }
    FIELD_VALUE_DETECTION_COMPLETED = {
        'type': "field_value_detection_completed",
        'template': 'Field Value Detection task has completed for project "{project}"',
        'template_keywords': ['project', ],
        'link_type': 'project-grid',
    }
    CUSTOM_TERM_SET_SEARCH_FINISHED = {
        'type': "custom_term_set_search_finished",
        'template': 'Custom Term Set search has finished for project "{project}"',
        'template_keywords': ['project', ],
        'link_type': 'project-grid',
    }
    CUSTOM_COMPANY_TYPE_SEARCH_FINISHED = {
        'type': "custom_company_type_search_finished",
        'template': 'Custom Company Type search has finished for project "{project}"',
        'template_keywords': ['project', ],
        'link_type': 'project-grid',
    }
    DOCUMENT_SIMILARITY_SEARCH_FINISHED = {
        'type': "document_similarity_search_finished",
        'template': 'Document Similarity Search has finished for project "{project}"',
        'template_keywords': ['project', ],
        'link_type': 'project-grid',
    }
    TEXT_UNIT_SIMILARITY_SEARCH_FINISHED = {
        'type': "text_unit_similarity_search_finished",
        'template': 'Text Unit Similarity Search has finished for project "{project}"',
        'template_keywords': ['project', ],
        'link_type': 'project-grid',
    }

    @classmethod
    def choices(cls):
        return tuple((i.name, i.type()) for i in cls)

    @classmethod
    def get_plural(cls, count):
        return "s were" if count > 1 else " was"

    @classmethod
    def get_type_by_value(cls, value):
        for i in cls:
            if i.type() == value:
                return i
        return None

    def __str__(self):
        return self.type()

    def type(self):
        return self.value.get('type', '')

    def message_template(self):
        return self.value.get('template', '')

    def message_template_keywords(self):
        return self.value.get('template_keywords', [])

    def redirect_link_type(self):
        return self.value.get('link_type', '')

    def check_message_data(self, message_data):
        # Prepare web notification message data object
        message_template_keywords = self.message_template_keywords()
        message_data_keys = message_data.keys()

        # Remove redundant keywords
        for i in message_data_keys:
            if i not in message_template_keywords:
                del message_data[i]
        # Add missing keywords
        for i in message_template_keywords:
            if i not in message_data_keys:
                message_data[i] = ''

        return message_data


class WebNotificationMessage(models.Model):
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    message_data = JSONField(blank=True, null=True)
    notification_type = models.CharField(max_length=100, db_index=True, null=True, blank=True,
                                         choices=WebNotificationTypes.choices(),
                                         help_text='Notification type')
    message = models.TextField(blank=True, null=True)
    redirect_link = JSONField(blank=True, null=True)

    class Meta:
        verbose_name = 'web notification message'
        verbose_name_plural = 'web notification messages'
        db_table = 'web_notification_message'

    def save(self, *args, **kwargs):
        # autoupdate message field value
        if self.pk is not None:
            try:
                orig = WebNotificationMessage.objects.get(pk=self.pk)
            except WebNotificationMessage.DoesNotExist:
                return
            if orig.notification_type != self.notification_type \
                    or orig.message_data != self.message_data:
                self.message = self.get_notification_message_template().format(**self.message_data)
        else:
            self.message = self.get_notification_message_template().format(**self.message_data)
        super().save(*args, **kwargs)

    def get_notification_message_template(self):
        return WebNotificationTypes.get_type_by_value(self.notification_type).message_template()

    def get_recipients_ids(self):
        return list(self.notifications.all().values_list('recipient_id', flat=True))

    @classmethod
    def bulk_create_notification_messages(cls, notifications: list):
        """
        Creates multiple WebNotificationMessages and proper WebNotifications at a time
        """
        web_notifications = []
        web_notification_recipients = []
        for message_data, redirect_link, notification_type, recipients in notifications:
            web_notifications.append(WebNotificationMessage(message_data=message_data,
                                                            redirect_link=redirect_link,
                                                            notification_type=notification_type))
            web_notification_recipients.append({
                'message_data': message_data,
                'notification_type': notification_type,
                'recipients': recipients
            })
        if web_notifications:
            WebNotificationMessage.objects.bulk_create(web_notifications,
                                                       recipients=web_notification_recipients)

    def send(self):
        data = {
            'id': self.id,
            'message_data': self.message_data,
            'message_template': WebNotificationTypes.get_type_by_value(
                self.notification_type).message_template(),
            'notification_type': self.notification_type,
            'redirect_link': self.redirect_link,
            'created_date': self.created_date,
        }
        message = ChannelMessage(message_types.CHANNEL_MSG_TYPE_WEB_NOTIFICATION_ADDED, data)
        Websockets().send_to_users_by_ids(user_ids=self.get_recipients_ids(), message_obj=message)


@receiver(post_bulk_create, sender=WebNotificationMessage)
def generate_web_notifications(sender, queryset, *args, **kwargs):
    recipients = kwargs.get('kwargs', {}).get('recipients', [])
    notifications = []
    for recipient in recipients:
        notification = WebNotificationMessage.objects.filter(
            message_data=recipient['message_data'],
            notification_type=recipient['notification_type']).last()
        if notification:
            notifications.extend([
                WebNotification(recipient_id=i, notification=notification)
                for i in recipient['recipients']])
    WebNotification.objects.bulk_create(notifications)


class WebNotification(models.Model):
    LAST_NOTIFICATIONS_COUNT = 15

    recipient = models.ForeignKey(User, blank=True, null=True, on_delete=CASCADE)
    is_seen = models.BooleanField(default=False)
    notification = models.ForeignKey(WebNotificationMessage, db_index=True, on_delete=CASCADE,
                                     related_name="notifications")

    class Meta:
        verbose_name = 'web notification'
        verbose_name_plural = 'web notifications'
        db_table = 'web_notification'


@receiver(post_bulk_create, sender=WebNotification)
def process_web_notification(sender, queryset, *args, **kwargs):
    storage = WebNotificationStorage()
    notification_messages_ids = set([item.notification_id for item in queryset])
    notification_messages = WebNotificationMessage.objects.filter(id__in=notification_messages_ids)
    for message in notification_messages:
        storage.process(message)
