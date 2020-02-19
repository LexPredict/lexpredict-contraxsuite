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

# Standard imports
import logging
from datetime import datetime
from traceback import format_exc
from typing import Generator

# Third-party imports
from celery import states
from celery.states import PENDING, READY_STATES, FAILURE, REVOKED, IGNORED, SUCCESS
from dataclasses import dataclass
from dateutil import parser as date_parser

# Django imports
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models, DatabaseError
from django.db.models.deletion import CASCADE
from django.utils.translation import ugettext_lazy as _
from elasticsearch import Elasticsearch

# Project imports
from apps.common.fields import StringUUIDField, TruncatingCharField
from apps.common.model_utils.hr_django_json_encoder import HRDjangoJSONEncoder
from apps.common.utils import fast_uuid
from apps.task.celery_backend.managers import TaskManager
from apps.task.celery_backend.utils import now
from apps.users.models import User
from contraxsuite_logging import write_task_log

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

from task_names import TASK_FRIENDLY_NAME

logger = logging.getLogger(__name__)
es = Elasticsearch(hosts=settings.ELASTICSEARCH_CONFIG['hosts'])


class TaskConfig(models.Model):
    name = models.CharField(max_length=100, db_index=True, primary_key=True)

    soft_time_limit = models.PositiveIntegerField(blank=True, null=True)

    notify_on_fail = models.BooleanField(default=False, db_index=True)

    watchdog_minutes = models.PositiveIntegerField(blank=True, null=False, default=60)


ALL_STATES = sorted(states.ALL_STATES)
ALL_STATES_SET = set(ALL_STATES)
TASK_STATE_CHOICES = sorted(zip(ALL_STATES, ALL_STATES))

FAIL_READY_STATES = frozenset({FAILURE, REVOKED, IGNORED})


@dataclass
class TaskLogEntry:
    file_index: str
    record_id: str
    message: str
    timestamp: datetime = None
    log_level: str = None
    task_name: str = None
    task_id: str = None
    main_task_id: str = None
    stack_trace: str = None


class Task(models.Model):
    """Task object

    Task object designed to record the metadata around distributed celery tasks."""

    id = models.CharField(
        max_length=255, unique=True, db_index=True, null=False, blank=False, primary_key=True,
        default=fast_uuid
    )

    main_task = models.ForeignKey('self', blank=True, null=True, on_delete=CASCADE, related_name='all_sub_tasks')
    parent_task = models.ForeignKey('self', blank=True, null=True, on_delete=CASCADE, related_name='straight_sub_tasks')

    name = models.CharField(max_length=100, db_index=True, null=True, blank=True)
    display_name = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=1024, db_index=False, null=True, blank=True)
    date_start = models.DateTimeField(default=now, db_index=True)
    date_work_start = models.DateTimeField(blank=True, null=True, db_index=True)
    user = models.ForeignKey(User, db_index=True, blank=True, null=True, on_delete=CASCADE)
    celery_metadata = JSONField(blank=True, null=True)
    metadata = JSONField(blank=True, null=True)
    args = JSONField(blank=True, null=True, db_index=False, encoder=HRDjangoJSONEncoder)
    kwargs = JSONField(blank=True, null=True, db_index=True)
    group_id = StringUUIDField(blank=True, null=True, db_index=True)
    source_data = models.TextField(blank=True, null=True)
    visible = models.BooleanField(default=True)
    run_count = models.IntegerField(blank=False, null=False, default=0)
    worker = models.CharField(max_length=1024, db_index=True, null=True, blank=True)
    priority = models.IntegerField(blank=False, null=False, default=0)

    own_date_done = models.DateTimeField(blank=True, null=True)
    own_status = models.CharField(
        _('state'),
        max_length=50, default=states.PENDING,
        choices=TASK_STATE_CHOICES,
        db_index=True,
        null=True,
        blank=True
    )
    own_progress = models.PositiveSmallIntegerField(default=0, blank=True, null=True)

    result = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)
    traceback = models.TextField(_('traceback'), blank=True, null=True)
    hidden = models.BooleanField(editable=False, default=False, db_index=True)
    propagate_exceptions = models.BooleanField(editable=False, default=False, db_index=True)

    status = models.CharField(max_length=50, default=states.PENDING,
                              choices=TASK_STATE_CHOICES, db_index=True, null=True,
                              blank=True)
    progress = models.PositiveIntegerField(default=0, null=True, blank=True)
    completed = models.BooleanField(null=False, blank=False, default=False)

    date_done = models.DateTimeField(blank=True, null=True)

    title = models.CharField(max_length=1024, db_index=False, null=True, blank=True)

    log_extra = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)
    push_steps = models.IntegerField(null=True, blank=True, default=1)
    failure_processed = models.BooleanField(null=False, blank=False, default=False)

    project = models.ForeignKey('project.Project', blank=True, null=True, db_index=True, on_delete=CASCADE)
    upload_session = models.ForeignKey('project.UploadSession', blank=True,
                                       null=True, db_index=True, on_delete=CASCADE)
    run_after_sub_tasks_finished = models.BooleanField(editable=False, default=False)

    run_if_parent_task_failed = models.BooleanField(editable=False, default=False)

    has_sub_tasks = models.BooleanField(editable=False, default=False)

    call_stack = TruncatingCharField(max_length=1024, db_index=True, null=True, blank=True)

    failure_reported = models.BooleanField(null=False, default=False, db_index=True)

    objects = TaskManager()

    def __str__(self):
        return "Task (name={}, celery_id={})" \
            .format(self.name, self.id)

    def is_sub_task(self):
        return self.parent_task_id and self.parent_task_id != self.id

    @property
    def has_error(self) -> bool:
        return self.status == states.FAILURE

    @property
    def duration(self):
        if not self.date_start:
            return None
        date_done = self.date_done or now()
        duration = date_done - self.date_start
        return duration

    @property
    def subtasks(self):
        return Task.objects.filter(main_task=self)

    @classmethod
    def disallow_start(cls, name):
        return Task.objects.filter(name=name, status=PENDING).exists()

    @classmethod
    def special_tasks(cls, filter_opts):
        """
        Get tasks related with key/value
        """
        opts = {'metadata__%s' % k: v for k, v in filter_opts.items()}
        return cls.objects.main_tasks().filter(**opts)

    def write_log(self, message, level='info', exc_info: Exception = None, **kwargs):
        message = str(message)

        extra = dict()

        if self.log_extra:
            extra.update(dict(self.log_extra))

        if kwargs:
            extra.update(kwargs)

        write_task_log(self.id, message, level,
                       main_task_id=self.main_task_id or self.id,
                       task_name=self.name,
                       user_id=self.user.id if self.user else None,
                       user_login=self.user.username if self.user else None,
                       exc_info=exc_info,
                       log_extra=extra)

    def get_task_log_from_elasticsearch(self) -> Generator[TaskLogEntry, None, None]:
        try:
            es_query = {
                'sort': ['@timestamp'],
                'query': {
                    'bool': {
                        'must': [
                            {'term': {'log_main_task_id': {'value': f'{self.id}'}}},
                        ]
                    }
                },
                '_source': ['@timestamp', 'level', 'message', 'log_main_task_id',
                            'log_task_id', 'log_task_name', 'log_stack_trace', '_id']
            }
            es_res = es.search(size=10000,
                               index=settings.LOGGING_ELASTICSEARCH_INDEX_TEMPLATE,
                               body=es_query)
            for hit in es_res['hits']['hits']:
                doc = hit['_source']

                yield TaskLogEntry(file_index=hit['_index'],
                                   record_id=hit['_id'],
                                   timestamp=date_parser.parse(doc['@timestamp']),
                                   log_level=doc.get('level'),
                                   task_name=doc.get('log_task_name'),
                                   task_id=doc.get('log_task_id'),
                                   main_task_id=doc.get('log_main_task_id'),
                                   stack_trace=doc.get('log_stack_trace'),
                                   message=doc.get('message'))

        except:
            yield TaskLogEntry(message='Unable to fetch logs from ElasticSearch:\n{0}'.format(format_exc()))

    def set_own_status(self, status: str) -> None:
        if status not in ALL_STATES_SET:
            title_str = f"{self.name}, id='{self.pk}'"
            raise RuntimeError(f'Trying to set "{status}" for task {title_str}')
        self.own_status = status
        if status in READY_STATES:
            self.own_progress = 100

    def on_task_completed(self, succeeded: bool):
        if self.has_sub_tasks:
            self.own_progress = 100
            self.own_status = SUCCESS if succeeded else FAILURE
            self.own_date_done = self.own_date_done or now()
            self.save()
            return
        self.update_progress(100, succeeded)

    def update_progress(self,
                        new_progress: int,
                        succeeded: bool = True):
        new_progress = self.ensure_correct_progress(new_progress)
        if new_progress == self.progress:
            return
        self.progress = min(new_progress, 100)
        if self.progress == 100:
            self.status = SUCCESS if succeeded else FAILURE
            if self.own_status not in READY_STATES:
                self.own_status = self.status

            now_time = now()
            self.own_date_done = self.own_date_done or now_time
            self.date_done = self.date_done or now_time
        try:
            self.save(update_fields=['progress', 'own_progress', 'status', 'own_status',
                                     'date_done', 'own_date_done'])
        except DatabaseError:
            # task itself might have been deleted
            pass

        # propagate changes to parent tasks
        parent_task = self.parent_task  # type: Task
        if not parent_task:
            return

        progresses = [p for p in Task.objects.filter(
            parent_task_id=parent_task.pk).values_list('progress', flat=True)]
        if progresses:
            parent_progress = int((sum(progresses) + parent_task.own_progress) / (len(progresses) + 1))
            parent_task.update_progress(parent_progress)

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = TASK_FRIENDLY_NAME.get(self.name) or self.name
        if self.progress > 100:
            self.progress = 100
        if self.status in FAIL_READY_STATES:
            self.progress = 100
            self.own_status = self.status
            self.date_done = self.date_done or now()

        if self.status in READY_STATES:
            self.own_status = self.status
            self.progress = 100
            self.date_done = self.date_done or now()
        if self.own_status in READY_STATES:
            self.own_progress = 100
            self.own_date_done = self.own_date_done or now()

        super().save(*args, **kwargs)

    def ensure_correct_progress(self, new_progress: int) -> int:
        if new_progress > 100:
            new_progress = 100
        if self.status in FAIL_READY_STATES or self.own_status in FAIL_READY_STATES:
            new_progress = 100
        return new_progress
