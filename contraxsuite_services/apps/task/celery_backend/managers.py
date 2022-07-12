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

from __future__ import absolute_import, unicode_literals

import copy
import datetime
import warnings
from functools import wraps
from itertools import count, groupby
from traceback import format_exception
from typing import Tuple, Dict

from celery.beat import SchedulingError
from celery.states import READY_STATES, SUCCESS, UNREADY_STATES, \
    FAILURE, ALL_STATES, PENDING
from django.conf import settings
from django.db import connections, router, transaction, models, connection
from django.db.models import F, Q, Value
from django.db.utils import IntegrityError, InterfaceError, OperationalError

from apps.common.logger import CsLogger
from apps.task.celery_backend.utils import now
from apps.task.task_visibility import TaskVisibility
from apps.task.utils.task_utils import TaskUtils
from task_names import TASK_FRIENDLY_NAME

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


try:
    from celery.utils.time import maybe_timedelta
except ImportError:  # pragma: no cover
    from celery.utils.timeutils import maybe_timedelta  # noqa

W_ISOLATION_REP = """
Polling results with transaction isolation level 'repeatable-read'
within the same transaction may give outdated results.

Be sure to commit the transaction for each poll iteration.
"""

celery_task_logger = CsLogger.get_logger('apps.task.models')


class TxIsolationWarning(UserWarning):
    """Warning emitted if the transaction isolation level is suboptimal."""


def transaction_retry(max_retries=1):
    """Decorator to retry database operations.

    For functions doing database operations, adding
    retrying if the operation fails.

    Keyword Arguments:
        max_retries (int): Maximum number of retries.  Default one retry.
    """

    def _outer(fun):

        @wraps(fun)
        def _inner(*args, **kwargs):
            _max_retries = kwargs.pop('exception_retry_count', max_retries)
            for retries in count(0):
                try:
                    return fun(*args, **kwargs)
                except SchedulingError as e:
                    log_task_failure(e, *args, **kwargs)
                    TaskUtils.prepare_task_execution()
                    if retries >= _max_retries:
                        raise
                except InterfaceError as e:
                    log_task_failure(e, *args, **kwargs)
                    TaskUtils.prepare_task_execution()
                    if retries >= _max_retries:
                        raise
                except OperationalError as e:
                    log_task_failure(e, *args, **kwargs)
                    TaskUtils.prepare_task_execution()
                    if retries >= _max_retries:
                        raise
                except Exception as e:  # pragma: no cover
                    # Depending on the database backend used we can experience
                    # various exceptions. E.g. psycopg2 raises an exception
                    # if some operation breaks the transaction, so saving
                    # the task result won't be possible until we rollback
                    # the transaction.
                    log_task_failure(e, *args, **kwargs)
                    if retries >= _max_retries:
                        raise

        return _inner

    return _outer


def log_task_failure(exc_info, *args, **kwargs):
    if 'task_id' not in kwargs:
        return
    try:
        task_id = kwargs['task_id']
        msg = 'Uncaught exception'
        celery_task_logger.error(msg, exc_info,
                                 extra={'log_task_id': task_id})
        print(f'logged for task {task_id}')
    except Exception as e:
        print(f'Error while logging: {e}')


class QuerySet(models.QuerySet):
    def filter_metadata(self, **kwargs):
        opts = {'metadata__%s' % k: v for k, v in kwargs.items()}
        return self.filter(**opts)

    def progress(self, get_completed=False):
        """
        Detailed Progress of tasks
        """
        result = {'{}-{}'.format(i['name'], i['id']): dict(i)
                  for i in self.values('id', 'name', 'progress', 'completed')} or None
        if get_completed:
            if result:
                progress_values = [i['progress'] for i in result.values()]
                completed = ((sum(progress_values) / len(progress_values)) == 100) \
                    if progress_values else None
            else:
                completed = None
            result = (result, completed)
        return result

    def progress_groups(self, get_completed=False):
        """
        Detailed Progress of tasks grouped by metadata
        """
        data = [{'progress': i['progress'],
                 'completed': i['completed'],
                 'metadata': i['metadata'].items()}
                for i in self.values('progress', 'completed', 'metadata')]
        result = []
        for metadata, grouped_data in groupby(
                sorted(data, key=lambda i: i['metadata']),
                key=lambda i: i['metadata']):
            progress_data = [i['progress'] for i in grouped_data]
            group_progress = round(sum(progress_data) / len(progress_data),
                                   2) if progress_data else 0
            metadata = dict(metadata)
            metadata['progress'] = group_progress
            metadata['completed'] = group_progress == 100
            result.append(metadata)
        if get_completed:
            if result:
                completed = all([i['completed'] for i in result])
            else:
                completed = None
            result = (result, completed)
        return result

    def completed(self):
        """
        Tasks completed or not (None if no tasks at all)
        """
        tasks_progress = self.progress()
        if tasks_progress is None:
            return None
        progress_values = [i['progress'] for i in tasks_progress.values()]
        return ((sum(progress_values) / len(progress_values)) == 100) if progress_values else None


class TaskManager(models.Manager):
    _last_id = None

    def get_queryset(self):
        return QuerySet(self.model, using=self._db)

    def get_task(self, task_id):
        """Get result for task by ``task_id``.

        Keyword Arguments:
            exception_retry_count (int): How many times to retry by
                transaction rollback on exception.  This could
                happen in a race condition if another worker is trying to
                create the same task.  The default is to retry once.
        """
        try:
            return self.get(id=task_id)
        except self.model.DoesNotExist:
            if self._last_id == task_id:
                self.warn_if_repeatable_read()
            self._last_id = task_id
            return self.model(id=task_id)

    @transaction_retry(max_retries=2)
    def init_task(self,
                  task_id: str,
                  task_name: str,
                  main_task_id: str,
                  parent_task_id: str,
                  description: str = None,
                  args: Tuple = None,
                  kwargs: Dict = None,
                  queue: str = None,
                  priority: int = None,
                  source_data=None,
                  run_after_sub_tasks_finished=False,
                  run_if_parent_task_failed=False):

        if description and len(description) > 1020:
            description = description[:1020]

        display_name = TASK_FRIENDLY_NAME.get(task_name) or task_name

        obj, created = self.get_or_create(id=task_id, defaults={
            'name': task_name,
            'display_name': display_name,
            'description': description,
            'main_task_id': main_task_id,
            'parent_task_id': parent_task_id,
            'date_start': now(),
            'args': args,
            'kwargs': kwargs,
            'queue': queue,
            'priority': priority,
            'restart_count': 0,
            'bad_health_check_num': 0,
            'source_data': source_data,
            'status': PENDING,
            'own_status': PENDING,
            'progress': 0,
            'own_progress': 0,
            'failure_reported': False,
            'run_after_sub_tasks_finished': run_after_sub_tasks_finished,
            'run_if_parent_task_failed': run_if_parent_task_failed})
        if not created:
            # If the task model is already created then this is a retry of a failed task
            # We need to clear its status and progress
            obj.description = description
            obj.date_done = None
            obj.own_date_done = None
            obj.status = PENDING
            obj.own_status = PENDING
            obj.progress = 0
            obj.own_progress = 0
            # obj.save()
            # Instead of unconditional .save() we update only the specified fields
            # and only if they are different in the database.
            self.filter(id=task_id) \
                .exclude(date_done__isnull=True,
                         own_date_done__isnull=True,
                         status=PENDING,
                         own_status=PENDING,
                         progress=0,
                         own_progress=0,
                         description=description) \
                .update(date_done=None,
                        own_date_done=None,
                        status=PENDING,
                        own_status=PENDING,
                        progress=0,
                        own_progress=0,
                        description=description)

        else:
            if settings.DEBUG_LOG_TASK_RUN_COUNT:
                with connection.cursor() as cursor:
                    cursor.execute(f'''
    insert into task_taskstatentry (task_name, run_counter) 
    values ('{task_name}', 1) 
    on conflict (task_name) do update set run_counter = task_taskstatentry.run_counter + 1;
                    ''')

        return obj

    @transaction_retry(max_retries=2)
    def update_progress(self,
                        task_id,
                        progress: int):
        self.filter(id=task_id).update(own_progress=progress)

    @transaction_retry(max_retries=2)
    def increase_progress(self,
                          task_id,
                          progress_increase: int):
        self.filter(id=task_id).update(
            own_progress=F('own_progress') + progress_increase)

    @transaction_retry(max_retries=2)
    def set_push_steps(self, task_id, push_steps: int):
        self.filter(id=task_id).update(push_steps=push_steps)

    @transaction_retry(max_retries=2)
    def start_processing(self, task_id, worker):
        self.filter(id=task_id).update(date_work_start=now(), worker=worker)

    @transaction_retry(max_retries=2)
    def increase_run_count(self, task_id):
        task_qs = self.filter(id=task_id)
        if task_qs.exists():
            task_qs.update(run_count=F('run_count') + 1)
            return task_qs.last().run_count

    @transaction_retry(max_retries=2)
    def set_log_extra(self, task_id, log_extra):
        self.filter(id=task_id).update(log_extra=log_extra)

    @transaction_retry(max_retries=2)
    def set_failure_processed(self, task_id, v: bool):
        self.filter(id=task_id).update(failure_processed=v)

    @transaction_retry(max_retries=2)
    def push(self, task_id):
        self.filter(id=task_id).update(
            own_progress=F('own_progress') + Value(100) / F('push_steps'))

    NON_FAILED_STATES = set(ALL_STATES) - {FAILURE}

    def main_tasks(self, show_failed_excluded_from_tracking: bool = False):
        excluded = TaskVisibility.get_excluded_from_tracking()
        qr = self.filter(Q(main_task__isnull=True) | Q(main_task_id=F('id')))
        if not show_failed_excluded_from_tracking:
            qr = qr.exclude(name__in=excluded)
        else:
            qr = qr.exclude(Q(name__in=excluded) & Q(status__in=self.NON_FAILED_STATES))
        return qr

    def parent_tasks(self, show_failed_excluded_from_tracking: bool = False):
        excluded = TaskVisibility.get_excluded_from_tracking()
        qr = self.filter(Q(has_sub_tasks=True) | Q(main_task__isnull=True) | Q(main_task_id=F('id')))
        if not show_failed_excluded_from_tracking:
            qr = qr.exclude(name__in=excluded)
        else:
            qr = qr.exclude(Q(name__in=excluded) & Q(status__in=self.NON_FAILED_STATES))
        return qr

    def unready_main_tasks(self):
        return self.main_tasks().filter(Q(status__isnull=True) | Q(status__in=UNREADY_STATES))

    def unready_parent_tasks(self):
        return self.parent_tasks().filter(Q(status__isnull=True) | Q(status__in=UNREADY_STATES))

    def succeed_main_tasks(self):
        return self.main_tasks().filter(status=SUCCESS)

    def succeed_parent_tasks(self):
        return self.parent_tasks().filter(status=SUCCESS)

    @classmethod
    def _prepare_task_result(cls, result):
        if result and isinstance(result, dict) and result.get('exc_message') \
                and isinstance(result['exc_message'], tuple):
            values = []
            for value in result['exc_message']:
                value = ''.join(format_exception(None, value, None)) if isinstance(value, BaseException) else value
                values.append(value)
            result = copy.copy(result)
            result['exc_message'] = tuple(values)
        return result

    @transaction_retry(max_retries=2)
    def store_result(self,
                     task_id: str,
                     main_task_id: str,
                     task_name: str,
                     result,
                     status: str,
                     traceback=None, metadata=None):
        date_now = now()
        result = TaskManager._prepare_task_result(result)

        initial_values = {
            'name': task_name,
            'main_task_id': main_task_id,
            'own_status': status,
            'date_start': date_now,
            'own_date_done': date_now if status in READY_STATES else None,
            'result': result,
            'restart_count': 0,
            'bad_health_check_num': 0,
            'traceback': traceback,
            'celery_metadata': metadata,
        }

        if initial_values['own_status'] in READY_STATES:
            initial_values['own_progress'] = 100

        if main_task_id and main_task_id != task_id:  # this is a sub-task
            initial_values['status'] = initial_values.get('own_status')
            initial_values['date_done'] = initial_values.get('own_date_done')
            initial_values['progress'] = initial_values.get('own_progress')

        try:
            obj, created = self.get_or_create(id=task_id, defaults=initial_values)

            if not created:
                update_fields = set()
                if task_name and not obj.name:
                    obj.name = task_name
                    update_fields.add('name')

                # Main task id should be assigned in init_task or on initial store result.
                # If the task is already initialized with main_task_id = None - here it can be rewritten
                # with some value by Celery itself.
                obj.own_status = status
                update_fields.add('own_status')
                if status in READY_STATES:
                    obj.own_progress = 100
                    update_fields.add('own_progress')

                if obj.own_date_done is None:
                    obj.own_date_done = now() if status in READY_STATES else None
                    update_fields.add('own_date_done')

                obj.result = result
                update_fields.add('result')

                if obj.traceback != traceback:
                    obj.traceback = traceback
                    update_fields.add('traceback')

                if obj.celery_metadata != metadata:
                    obj.celery_metadata = metadata
                    update_fields.add('celery_metadata')

                if not obj.has_sub_tasks:
                    obj.status = obj.own_status
                    obj.date_done = obj.own_date_done
                    obj.progress = obj.own_progress
                    update_fields.update({'status', 'date_done', 'progress'})

                obj.save(update_fields=update_fields)

        except IntegrityError:
            print('Orphan sub-task detected: {0}'.format(initial_values))
            obj = self.model(**initial_values)

        return obj

    def warn_if_repeatable_read(self):
        # copy-pasted from django-celery-results
        if 'mysql' in self.current_engine().lower():
            cursor = self.connection_for_read().cursor()
            if cursor.execute('SELECT @@tx_isolation'):
                isolation = cursor.fetchone()[0]
                if isolation == 'REPEATABLE-READ':
                    warnings.warn(TxIsolationWarning(W_ISOLATION_REP.strip()))

    def connection_for_write(self):
        return connections[router.db_for_write(self.model)]

    def connection_for_read(self):
        return connections[self.db]

    def current_engine(self):
        try:
            return settings.DATABASES[self.db]['ENGINE']
        except AttributeError:
            return settings.DATABASE_ENGINE

    def get_all_expired(self, expires):
        """Get all expired task results."""
        return self.filter(own_date_done__lt=now() - maybe_timedelta(expires))

    def delete_expired(self, expires):
        """Delete all expired results."""
        meta = self.model._meta
        with transaction.atomic():
            self.get_all_expired(expires).update(hidden=True)
            cursor = self.connection_for_write().cursor()
            cursor.execute(
                'DELETE FROM {0.db_table} WHERE hidden=%s'.format(meta),
                (True,),
            )

    def filter_metadata(self, **kwargs):
        opts = {'metadata__%s' % k: v for k, v in kwargs.items()}
        return self.main_tasks().filter(**opts)

    def get_active_user_tasks(self) -> QuerySet:
        excluded = TaskVisibility.get_excluded_from_tracking()
        execution_delay = now() - datetime.timedelta(seconds=settings.USER_TASK_EXECUTION_DELAY)
        start_date_limit = now() - datetime.timedelta(seconds=3 * 24 * 60 * 60)
        return self \
            .filter(Q(main_task__isnull=True) | Q(main_task_id=F('id'))) \
            .filter(status__in=UNREADY_STATES) \
            .exclude(name__in=excluded) \
            .filter(Q(date_start__isnull=True) | Q(date_start__gt=start_date_limit)) \
            .filter(Q(date_work_start__isnull=True) | Q(date_work_start__gt=execution_delay))

    def active_tasks_exist(self, task_name: str, execution_delay: datetime.datetime,
                           activity_filter: QuerySet = None) -> bool:
        has_activity = None
        work_dates = self.filter(name=task_name, status__in=UNREADY_STATES).values_list('date_work_start', flat=True)
        for date_work_start in work_dates:
            if date_work_start is None or date_work_start > execution_delay:
                return True
            if activity_filter and has_activity is None:
                has_activity = activity_filter.exists()
                if has_activity:
                    return True
        return False
