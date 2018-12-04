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
import sys
from traceback import format_exc

# Third-party imports
from celery import states
from dateutil import parser as date_parser
from elasticsearch import Elasticsearch

# Django imports
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Project imports
from apps.common.utils import fast_uuid
from apps.common.fields import StringUUIDField
from apps.task.celery_backend.managers import TaskManager
from apps.task.celery_backend.utils import now
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.6/LICENSE"
__version__ = "1.1.6"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

logger = logging.getLogger(__name__)
es = Elasticsearch(hosts=settings.ELASTICSEARCH_CONFIG['hosts'])


class TaskConfig(models.Model):
    name = models.CharField(max_length=100, db_index=True, primary_key=True)

    soft_time_limit = models.PositiveIntegerField(blank=True, null=True)


ALL_STATES = sorted(states.ALL_STATES)
TASK_STATE_CHOICES = sorted(zip(ALL_STATES, ALL_STATES))


class Task(models.Model):
    """Task object

    Task object designed to record the metadata around distributed celery tasks."""

    id = models.CharField(
        max_length=255, unique=True, db_index=True, null=False, blank=False, primary_key=True,
        default=fast_uuid
    )

    main_task = models.ForeignKey('self', blank=True, null=True)

    name = models.CharField(max_length=100, db_index=True, null=True, blank=True)
    description = models.CharField(max_length=1024, db_index=False, null=True, blank=True)
    date_start = models.DateTimeField(default=now, db_index=True)
    date_work_start = models.DateTimeField(blank=True, null=True, db_index=True)
    user = models.ForeignKey(User, db_index=True, blank=True, null=True)
    celery_metadata = JSONField(blank=True, null=True)
    metadata = JSONField(blank=True, null=True)
    kwargs = JSONField(blank=True, null=True, db_index=True)
    sequential_tasks = JSONField(blank=True, null=True, db_index=True)
    sequential_tasks_started = models.BooleanField(default=False, db_index=True)
    group_id = StringUUIDField(blank=True, null=True, db_index=True)
    source_data = models.TextField(blank=True, null=True)
    visible = models.BooleanField(default=True)
    run_count = models.IntegerField(blank=False, null=False, default=0)
    worker = models.CharField(max_length=1024, db_index=True, null=True, blank=True)

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

    project = models.ForeignKey('project.Project', blank=True, null=True, db_index=True)
    upload_session = models.ForeignKey('project.UploadSession', blank=True, null=True, db_index=True)
    run_after_sub_tasks_finished = models.BooleanField(editable=False, default=False)

    objects = TaskManager()

    def __str__(self):
        return "Task (name={}, celery_id={})" \
            .format(self.name, self.id)

    def is_sub_task(self):
        return self.main_task_id and self.main_task_id != self.id

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
        return Task.objects.filter(name=name, status='PENDING').exists()

    @classmethod
    def special_tasks(cls, filter_opts):
        """
        Get tasks related with key/value
        """
        opts = {'metadata__%s' % k: v for k, v in filter_opts.items()}
        return cls.objects.main_tasks().filter(**opts)

    def write_log(self, message, level='info', **kwargs):
        message = str(message)
        extra = {
            'log_task_id': self.id,
            'log_main_task_id': self.main_task_id or self.id,
            'log_task_name': self.name,
            'log_user_id': self.user.id if self.user else None,
            'log_user_login': self.user.username if self.user else None
        }

        if self.log_extra:
            extra.update(dict(self.log_extra))

        if kwargs:
            extra.update(kwargs)

        try:
            getattr(logger, level)(message, extra=extra)

            return True
        except Exception as exception:
            trace = format_exc()
            exc_class, exception, _ = sys.exc_info()
            exception_str = '%s: %s' % (exc_class.__name__, str(exception))

            logger.error(
                'Exception caught while trying to log a message:\n{0}\n{1}'.format(exception_str,
                                                                                   trace),
                extra=extra)
            pass

    def get_task_log_from_elasticsearch(self):
        try:
            es_query = {
                'sort': ['@timestamp'],
                'query': {
                    'bool': {
                        'must': [
                            {'match': {'log_main_task_id': self.id}},
                        ]
                    }
                },
                '_source': ['@timestamp', 'level', 'message', 'log_task_id', 'log_main_task_id']
            }
            es_res = es.search(size=1000,
                               index=settings.LOGGING_ELASTICSEARCH_INDEX_TEMPLATE,
                               body=es_query)
            logs = []
            for hit in es_res['hits']['hits']:
                doc = hit['_source']
                timestamp = date_parser.parse(doc['@timestamp'])
                timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')

                level = doc['level']
                if not level:
                    level = 'INFO'

                message = doc['message']

                # log_add = '{2: <9} {0} | {1}'.format(timestamp, message, level.upper())
                log_add = 'Main task: {3} | Sub-task: {4}\n{2: <9} {0} | {1}'.format(timestamp,
                                                                                     message,
                                                                                     level.upper(),
                                                                                     doc[
                                                                                         'log_main_task_id'],
                                                                                     doc[
                                                                                         'log_task_id'])
                logs.append(log_add)
            return str('\n'.join(logs))
        except:
            return 'Unable to fetch logs from ElasticSearch:\n{0}'.format(format_exc())

    @property
    def log(self):
        return self.get_task_log_from_elasticsearch()
