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
from celery.states import PENDING, READY_STATES
from dataclasses import dataclass
from dateutil import parser as date_parser

# Django imports
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
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
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


logger = logging.getLogger(__name__)
es = Elasticsearch(hosts=settings.ELASTICSEARCH_CONFIG['hosts'])


class TaskConfig(models.Model):
    name = models.CharField(max_length=100, db_index=True, primary_key=True)

    soft_time_limit = models.PositiveIntegerField(blank=True, null=True)


ALL_STATES = sorted(states.ALL_STATES)
ALL_STATES_SET = set(ALL_STATES)
TASK_STATE_CHOICES = sorted(zip(ALL_STATES, ALL_STATES))


@dataclass
class TaskLogEntry:
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

    objects = TaskManager()

    def __str__(self):
        return "Task (name={}, celery_id={})" \
            .format(self.name, self.id)

    def is_suагаb_task(self):
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
                            'log_task_id', 'log_task_name', 'log_stack_trace']
            }
            es_res = es.search(size=10000,
                               index=settings.LOGGING_ELASTICSEARCH_INDEX_TEMPLATE,
                               body=es_query)
            for hit in es_res['hits']['hits']:
                doc = hit['_source']

                yield TaskLogEntry(timestamp=date_parser.parse(doc['@timestamp']),
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

    def save(self, *args, **kwargs):
        if self.own_progress > 100:
            self.own_progress = 100
        if self.progress > 100:
            self.progress = 100
        if self.own_status in READY_STATES:
            self.own_progress = 100
        if self.status in READY_STATES:
            self.progress = 100
        super().save(*args, **kwargs)
