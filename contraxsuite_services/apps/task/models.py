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
# Standard imports
from dataclasses import dataclass
from traceback import format_exc
from typing import Generator, Dict, Any, List, Set
from uuid import getnode as get_mac

# Third-party imports
from celery import states
from celery.states import PENDING, FAILURE, REVOKED, IGNORED, SUCCESS
from dateutil import parser as date_parser
# Django imports
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models, DatabaseError
from django.db.models.deletion import CASCADE
from django.utils.translation import ugettext_lazy as _
from elasticsearch import Elasticsearch

# Project imports
from apps.common.fields import StringUUIDField, TruncatingCharField
from apps.common.logger import CsLogger
from apps.common.model_utils.improved_django_json_encoder import ImprovedDjangoJSONEncoder
from apps.common.processes import terminate_processes_by_ids
from apps.common.utils import fast_uuid
from apps.task.celery_backend.managers import TaskManager
from apps.task.celery_backend.utils import now
from apps.users.models import User
from contraxsuite_logging import write_task_log

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


logger = CsLogger.get_logger(__name__)
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
    timestamp: datetime.datetime = None
    log_level: str = None
    task_name: str = None
    task_id: str = None
    main_task_id: str = None
    stack_trace: str = None
    com_docker_swarm_task_id: str = None


class TaskStatEntry(models.Model):
    task_name = models.CharField(max_length=256, primary_key=True, unique=True, null=False, blank=False)

    run_counter = models.IntegerField(default=0, null=False, blank=False)


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

    queue = models.CharField(max_length=256, db_index=True, blank=True, null=True)
    priority = models.IntegerField(null=True, blank=True)

    restart_count = models.IntegerField(null=False, blank=False, default=0)

    # no DB indexes here because task args/kwargs can be quite large and do not fit into Postgres max index size
    args = JSONField(blank=True, null=True, db_index=False, encoder=ImprovedDjangoJSONEncoder)
    kwargs = JSONField(blank=True, null=True, db_index=False, encoder=ImprovedDjangoJSONEncoder)

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

    result = JSONField(blank=True, null=True, encoder=ImprovedDjangoJSONEncoder)
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

    log_extra = JSONField(blank=True, null=True, encoder=ImprovedDjangoJSONEncoder)
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

    spawned_processes = JSONField(blank=True, null=True, encoder=ImprovedDjangoJSONEncoder)

    bad_health_check_num = models.IntegerField(null=False, blank=False, default=0)

    objects = TaskManager()

    weight = models.PositiveIntegerField(default=100, null=True, blank=True)

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

        extra = {}

        if self.log_extra:
            extra.update(dict(self.log_extra))

        if kwargs:
            extra_kwargs = kwargs.pop('extra', None)
            if extra_kwargs:
                extra.update(extra_kwargs)
            else:
                extra.update(kwargs)

        write_task_log(self.id, message, level,
                       main_task_id=self.main_task_id or self.id,
                       task_name=self.name,
                       user_id=self.user.id if self.user else None,
                       user_login=self.user.username if self.user else None,
                       exc_info=exc_info,
                       log_extra=extra)

    def get_task_log_from_elasticsearch(self,
                                        include_systemwide_errors: bool = False,
                                        sw_ers_minute_interval: int = 5,
                                        records_limit: int = 0) -> List[TaskLogEntry]:
        query = {
            'bool': {
                'must': [
                    {'term': {'log_main_task_id': {'value': f'{self.pk}'}}},
                ]
            }
        }
        # docker.container.labels.com_docker_swarm_task_id:"y2pjcbg0pztbmo75z4udjgsuv" AND ERROR
        records = list(self.get_task_log_from_elasticsearch_by_query(query, records_limit))
        # search for extra errors not bound for this very task
        if include_systemwide_errors:
            records += self.append_task_failure_records(records, sw_ers_minute_interval)
            records.sort(key=lambda r: r.timestamp)
        return records

    @classmethod
    def append_task_failure_records(cls,
                                    records: List[TaskLogEntry],
                                    sw_ers_minute_interval: int) -> List[TaskLogEntry]:
        """
        Search for errors on swarm nodes where the task resided
        for N minutes interval after the task finished.
        :param sw_ers_minute_interval: minutes to look in logs after the task's completed
        :param records: task's log records
        :return: extra error log records
        """
        error_extra_seconds = sw_ers_minute_interval * 60
        swarm_task_ids = set()  # type: Set[str]
        record_ids = set()  # type: Set[str]
        last_time = None
        for resp in records:
            record_ids.add(resp.record_id)
            last_time = max(resp.timestamp, last_time) if last_time else resp.timestamp
            if resp.com_docker_swarm_task_id:
                swarm_task_ids.add(resp.com_docker_swarm_task_id)

        if not swarm_task_ids:
            return []

        should_clause = []
        for swarm_task_id in swarm_task_ids:
            should_clause.append({'term': {
                'docker.container.labels.com_docker_swarm_task_id': {'value': swarm_task_id}}})
        query = {
            'bool': {
                'should': should_clause,
                'must': [{
                    "wildcard": {"message": "*error*"}
                },
                    {
                        "range": {
                            "@timestamp": {
                                "gte": last_time,
                                "lte": last_time + datetime.timedelta(0, error_extra_seconds)
                            }
                        }
                    }]
            }
        }
        error_records = []
        for resp in cls.get_task_log_from_elasticsearch_by_query(query):
            if resp.record_id not in record_ids:
                if 'WorkerLostError' in resp.message:
                    resp.log_level = 'ERROR'
                    error_records.append(resp)
        return error_records

    @classmethod
    def get_task_log_from_elasticsearch_by_query(
            cls,
            query: Dict[str, Any],
            limit: int = 0) -> Generator[TaskLogEntry, None, None]:
        limit = limit or 10000
        try:
            es_query = {
                'sort': ['@timestamp'],
                'query': query,
                '_source': ['@timestamp', 'level', 'message', 'log_main_task_id',
                            'log_task_id', 'log_task_name', 'log_stack_trace',
                            '_id', 'docker']
            }
            es_res = es.search(size=limit,
                               index=settings.LOGGING_ELASTICSEARCH_INDEX_TEMPLATE,
                               body=es_query)
            for hit in es_res['hits']['hits']:
                doc = hit['_source']
                docker_data = doc.get('docker')
                try:
                    docker_swarm_task_id = docker_data['container']['labels']['com_docker_swarm_task_id']
                except:
                    docker_swarm_task_id = ''

                yield TaskLogEntry(file_index=hit['_index'],
                                   record_id=hit['_id'],
                                   message=doc.get('message'),
                                   timestamp=date_parser.parse(doc['@timestamp']),
                                   log_level=doc.get('level'),
                                   task_name=doc.get('log_task_name'),
                                   task_id=doc.get('log_task_id'),
                                   main_task_id=doc.get('log_main_task_id'),
                                   stack_trace=doc.get('log_stack_trace'),
                                   com_docker_swarm_task_id=docker_swarm_task_id)
        except GeneratorExit:
            return
        except:
            yield TaskLogEntry(
                file_index='',
                record_id='',
                message='Unable to fetch logs from ElasticSearch:\n{0}'.format(format_exc()))

    def update_progress(self,
                        new_progress: int,
                        succeeded: bool = True):
        new_progress = min(new_progress, 100)
        self.own_progress = new_progress
        if self.own_progress == 100:
            self.own_status = SUCCESS if succeeded else FAILURE
            now_time = now()
            self.own_date_done = self.own_date_done or now_time

        try:
            if self.has_sub_tasks:
                self.save(update_fields=['own_progress', 'own_status', 'own_date_done'])
            else:
                self.status = self.own_status
                self.progress = self.own_progress
                self.date_done = self.own_date_done
                self.save(update_fields=['progress', 'own_progress',
                                         'status', 'own_status',
                                         'date_done', 'own_date_done'])
        except DatabaseError:
            # task itself might have been deleted
            pass

    # We don't propagate changes to the parent tasks here because it is done in a serial manner
    # in a Celery-beat task - see apps.task.celery_backend.managers.update_parent_task().
    # update_parent_task() should be the only method to manipulate with the parent-child status updates.
    # Otherwise we will get the logic duplication and confusion.
    # If putting something here please take into account that we have:
    # - sub-task hierarchy;
    # - sub-tasks started when all other sub-tasks succeeded;
    # - sub-tasks started when some other sub-task failed;
    # - status of the parent task calculated based on its sub-tasks/fail-handler/success-handler;
    # - progress of the parent task calculated based on its sub-tasks/fail-handler/success-handler.

    def set_visible(self, vis: bool):
        if vis == self.visible:
            return
        self.visible = vis
        self.save(update_fields=['visible'])

    def store_spawned_process(self, pid: int):
        adr_pid = (get_mac(), pid,)
        if self.spawned_processes:
            self.spawned_processes.append(adr_pid)
        else:
            self.spawned_processes = [adr_pid]
        self.save(update_fields=('spawned_processes',))

    def terminate_spawned_processes(
            self, terminate_where: str):
        """
        terminate_where could be either "locally" or "everywhere"
        """
        try:
            self.terminate_spawned_processes_unsafe(terminate_where)
        except Exception as e:
            self.write_log(f'Error in terminate_spawned_processes({terminate_where}): {e}')

    def terminate_spawned_processes_unsafe(
            self, terminate_where: str):
        from apps.task.tasks import call_terminate_processes_task
        if not self.spawned_processes:
            return

        if terminate_where == 'locally':
            pids = [p for adr, p in self.spawned_processes]
            terminate_processes_by_ids(pids, self.write_log)
            return

        # terminate on all nodes
        proc_by_adr = {}
        for adr, p in self.spawned_processes:
            if adr in proc_by_adr:
                proc_by_adr[adr].append(p)
            else:
                proc_by_adr[adr] = [p]

        for adr in proc_by_adr:
            pids = proc_by_adr[adr]
            call_terminate_processes_task(adr, pids)


class ReindexRoutine(models.Model):
    TARGET_TABLE = 'TABLE'

    TARGET_INDEX = 'INDEX'

    # name of the DB index / table to reindex, e.g. 'analyze_textunitvector_transformer_id'
    index_name = models.CharField(max_length=512, db_index=True, null=False,
                                  help_text='Table or index name to reindex')

    # entity to reindex: 'INDEX' or 'TABLE'
    target_entity = models.CharField(
        max_length=24,
        db_index=True,
        null=False,
        default=TARGET_INDEX,
        choices=[(TARGET_INDEX, 'index'), (TARGET_TABLE, 'table')],
        help_text='Indicates what DB entity to reindex: index or table'
    )

    # crontab format string like '0 1 * * *'. Flags are separated by spaces.
    # '0 0 0 0 0' means reindexing is turned off
    schedule = models.CharField(max_length=24, db_index=True, null=False,
                                help_text='crontab-format string, time is UTC+0')

    def __str__(self):
        return f'REINDEX {self.target_entity} "{self.index_name}" at "{self.schedule}"'

    def __repr__(self):
        return self.__str__()
