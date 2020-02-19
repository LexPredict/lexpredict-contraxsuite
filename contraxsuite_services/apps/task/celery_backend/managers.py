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
from typing import Tuple

from celery import signature
from celery.result import AsyncResult
from celery.states import READY_STATES, PROPAGATE_STATES, SUCCESS, UNREADY_STATES, FAILURE, ALL_STATES, PENDING
from django.conf import settings
from django.db import connections, router, transaction, models
from django.db.models import F, Q, Value
from django.db.utils import IntegrityError

from apps.task.celery_backend.task_utils import precedence_propagating_exceptions, \
    precedence_non_propagating_exceptions, revoke_task
from apps.task.celery_backend.utils import now

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
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
                except Exception:  # pragma: no cover
                    # Depending on the database backend used we can experience
                    # various exceptions. E.g. psycopg2 raises an exception
                    # if some operation breaks the transaction, so saving
                    # the task result won't be possible until we rollback
                    # the transaction.
                    if retries >= _max_retries:
                        raise

        return _inner

    return _outer


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

    EXCLUDE_FROM_TRACKING = settings.EXCLUDE_FROM_TRACKING

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
                  source_data=None,
                  run_after_sub_tasks_finished=False,
                  run_if_parent_task_failed=False):

        if description and len(description) > 1020:
            description = description[:1020]

        obj, created = self.get_or_create(id=task_id, defaults={
            'name': task_name,
            'description': description,
            'main_task_id': main_task_id,
            'parent_task_id': parent_task_id,
            'date_start': now(),
            'args': args,
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
            obj.date_done = None
            obj.own_date_done = None
            obj.status = PENDING
            obj.own_status = PENDING
            obj.progress = 0
            obj.own_progress = 0
            obj.save()

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
        self.filter(id=task_id).update(run_count=F('run_count') + 1)

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
        qr = self.filter(Q(main_task__isnull=True) | Q(main_task_id=F('id')))
        if not show_failed_excluded_from_tracking:
            qr = qr.exclude(name__in=self.EXCLUDE_FROM_TRACKING)
        else:
            qr = qr.exclude(Q(name__in=self.EXCLUDE_FROM_TRACKING) & Q(status__in=self.NON_FAILED_STATES))
        return qr

    def parent_tasks(self, show_failed_excluded_from_tracking: bool = False):
        qr = self.filter(Q(has_sub_tasks=True) | Q(main_task__isnull=True) | Q(main_task_id=F('id')))
        if not show_failed_excluded_from_tracking:
            qr = qr.exclude(name__in=self.EXCLUDE_FROM_TRACKING)
        else:
            qr = qr.exclude(Q(name__in=self.EXCLUDE_FROM_TRACKING) & Q(status__in=self.NON_FAILED_STATES))
        return qr

    def unready_main_tasks(self):
        return self.main_tasks().filter(Q(status__isnull=True) | Q(status__in=UNREADY_STATES))

    def unready_parent_tasks(self):
        return self.parent_tasks().filter(Q(status__isnull=True) | Q(status__in=UNREADY_STATES))

    def succeed_main_tasks(self):
        return self.main_tasks().filter(status=SUCCESS)

    def succeed_parent_tasks(self):
        return self.parent_tasks().filter(status=SUCCESS)

    def run_after_sub_tasks(self, parent_task_id: str):
        for task_id, name, metadata, main_task_id, title, priority \
                in self.filter(parent_task_id=parent_task_id, run_after_sub_tasks_finished=True) \
                .values_list('id', 'name', 'metadata', 'main_task_id', 'title', 'priority'):
            options = metadata['options']
            options['task_id'] = task_id
            options['parent_id'] = None
            options['main_task_id'] = None
            options['title'] = title
            options['run_after_sub_tasks_finished'] = False
            options['run_if_parent_task_failed'] = False
            priority = priority
            from apps.task.tasks import get_queue_by_task_priority
            queue = get_queue_by_task_priority(priority)
            task = signature(name, args=metadata['args'], **options)

            from apps.task.tasks import update_parent_task
            task.apply_async(priority=priority, queue=queue, link=update_parent_task.s(parent_task_id))

    def run_if_task_failed(self, parent_task_id: str):
        for task_id, name, metadata, main_task_id, title, priority \
                in self.filter(parent_task_id=parent_task_id, run_if_parent_task_failed=True) \
                .values_list('id', 'name', 'metadata', 'main_task_id', 'title', 'priority'):
            options = metadata['options']
            options['task_id'] = task_id
            options['parent_id'] = None
            options['main_task_id'] = None
            options['title'] = title
            options['run_after_sub_tasks_finished'] = False
            options['run_if_parent_task_failed'] = False
            priority = priority
            from apps.task.tasks import get_queue_by_task_priority
            queue = get_queue_by_task_priority(priority)
            task = signature(name, args=metadata['args'], **options)
            from apps.task.tasks import update_parent_task
            task.apply_async(priority=priority, queue=queue,
                             link=update_parent_task.s(parent_task_id))

    def update_parent_task(self, parent_task_id: str):
        all_task_info_rows = self.filter(
            Q(id=parent_task_id) | Q(parent_task_id=parent_task_id)) \
            .exclude(name__in=self.EXCLUDE_FROM_TRACKING)

        total_status_non_propagating_exceptions = None  # None, 'SUCCESS', ...
        total_status_propagating_exceptions = None
        found_propagating_exceptions = False
        total_progress = 0  # 0 ... 100
        total_done = True
        total_date_done = None
        no_tasks_or_all_finished = True
        has_non_started_deferred_tasks = False
        has_non_started_fail_handler_tasks = False
        has_uncompleted_deferred_tasks = False
        has_uncompleted_fail_handler_tasks = False

        for task_id, \
            propagate_exceptions, \
            has_sub_tasks, \
            status, progress, date_done, \
            own_status, own_progress, own_date_done, \
            task_should_be_run_after_all_main_and_sub_tasks_finished, \
            task_should_be_run_if_parent_task_failed in all_task_info_rows \
                .values_list('id',
                             'propagate_exceptions',
                             'has_sub_tasks',
                             'status', 'progress', 'date_done',
                             'own_status', 'own_progress', 'own_date_done',
                             'run_after_sub_tasks_finished', 'run_if_parent_task_failed'):
            if task_id == parent_task_id:
                # The following flags make sense for calculating status of the parent task of the current parent task.
                # If they are set on the current task (task.id == parent_task.id)
                # then they should not be taken into account.
                task_should_be_run_after_all_main_and_sub_tasks_finished = False
                task_should_be_run_if_parent_task_failed = False

            # if this is a sub-task of the parent task (not itself)
            # and it also has child tasks
            if not has_sub_tasks or task_id == parent_task_id:
                status, progress, date_done = own_status, own_progress, own_date_done

            # cleanup progress: completed tasks are assumed to have 100%, None => 0
            progress = progress or 0

            # check if there are unprocessed success/fail handlers
            if task_should_be_run_after_all_main_and_sub_tasks_finished:
                # status is assigned when the task is send
                has_non_started_deferred_tasks = status is None or has_non_started_deferred_tasks
                has_uncompleted_deferred_tasks = status not in READY_STATES or has_uncompleted_deferred_tasks
            elif task_should_be_run_if_parent_task_failed:
                has_non_started_fail_handler_tasks = status is None or has_non_started_fail_handler_tasks
                has_uncompleted_fail_handler_tasks = status not in READY_STATES or has_uncompleted_fail_handler_tasks
            else:
                no_tasks_or_all_finished = no_tasks_or_all_finished and (status in READY_STATES)

            if (not task_should_be_run_after_all_main_and_sub_tasks_finished
                and not task_should_be_run_if_parent_task_failed) \
                    or status in PROPAGATE_STATES:
                # calculate total status of the parent task
                if propagate_exceptions:
                    found_propagating_exceptions = True
                    total_status_propagating_exceptions = status \
                        if total_status_propagating_exceptions is None \
                        else max(total_status_propagating_exceptions,
                                 status,
                                 key=precedence_propagating_exceptions)
                else:
                    total_status_non_propagating_exceptions = status \
                        if total_status_non_propagating_exceptions is None \
                        else max(total_status_non_propagating_exceptions,
                                 status,
                                 key=precedence_non_propagating_exceptions)

            total_progress += progress

            # if there is at least one date_done = None then we are not done
            if date_done is None:
                total_done = False

            # if we still did not got any date_done = None (meaning we are done)
            # then calc total date done as the max date done we got
            if total_done:
                total_date_done = max(total_date_done, date_done) if total_date_done else date_done
            else:
                total_date_done = None

        # TODO: just progress
        total_progress = (total_progress / len(all_task_info_rows)) if len(all_task_info_rows) else total_progress  # 100

        if total_status_propagating_exceptions in PROPAGATE_STATES:
            # we have error in an important sub-task
            total_status = total_status_propagating_exceptions
        elif found_propagating_exceptions:
            # we don't have errors in important sub-tasks
            # but there were important sub-tasks and we should take their statuses into account
            # (this is mostly to take care of None state in total_status_propagating_exceptions
            # meaning PENDING)
            total_status = max(total_status_propagating_exceptions,
                               total_status_non_propagating_exceptions,
                               key=precedence_non_propagating_exceptions)
        else:
            # we did not see any important sub-tasks and should not take into account
            # None in total_status_propagating_exceptions
            total_status = total_status_non_propagating_exceptions

        if total_status in READY_STATES:
            total_progress = 100

        if no_tasks_or_all_finished:

            def mark_main_task_completed():
                # TODO Support "propagating exception" flag properly
                # Parent task should not crash if the child was not marked as "propagating exception"
                # (important/critical)
                # For now it is made crashing always if any sub-task crashes.
                completed = total_status in READY_STATES
                date_done = total_date_done or (now() if completed else None)
                self.filter(id=parent_task_id).update(date_done=date_done,
                                                      status=total_status,
                                                      completed=completed,
                                                      progress=total_progress)
                try:
                    main_task = self.get(id=parent_task_id)  # type: Task
                    if main_task.parent_task_id is not None:
                        from apps.task.tasks import update_parent_task
                        update_parent_task.apply_async((main_task.parent_task_id,))

                    if total_status != SUCCESS:
                        main_task.write_log('{0} #{1}: some/all of sub-tasks have been crashed'.format(
                            main_task.name, parent_task_id), level='error')
                except:
                    import logging
                    logging.error('Was unable to log SUCCESS/FAILURE to task log. Task id: {0}'
                                  .format(parent_task_id))

                if total_status in PROPAGATE_STATES:
                    revoke_task(AsyncResult(parent_task_id))

            if total_status in PROPAGATE_STATES:  # if something failed
                # drop all success handlers for them to not participate in the further status calculations
                self.filter(main_task_id=parent_task_id, run_after_sub_tasks_finished=True) \
                    .delete()
                if has_non_started_fail_handler_tasks:
                    self.run_if_task_failed(parent_task_id)
                elif not has_uncompleted_fail_handler_tasks:
                    mark_main_task_completed()

            else:  # if everything succeeded
                # drop all fail handlers for them to not participate in the further status calculations
                self.filter(main_task_id=parent_task_id, run_if_parent_task_failed=True) \
                    .delete()
                if has_non_started_deferred_tasks:
                    self.run_after_sub_tasks(parent_task_id)
                elif not has_uncompleted_deferred_tasks:
                    mark_main_task_completed()

    @classmethod
    def _prepare_task_result(cls, result):
        if result and isinstance(result, dict) and result.get('exc_message') \
                and isinstance(result['exc_message'], tuple):
            values = list()
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
                if task_name and not obj.name:
                    obj.name = task_name

                # Main task id should be assigned in init_task or on initial store result.
                # If the task is already initialized with main_task_id = None - here it can be rewritten
                # with some value by Celery itself.
                obj.set_own_status(status)

                if obj.own_date_done is None:
                    obj.own_date_done = now() if status in READY_STATES else None

                obj.result = result
                obj.traceback = traceback
                obj.celery_metadata = metadata

                # if not obj.has_sub_tasks:
                #     obj.status = obj.own_status
                #     obj.date_done = obj.own_date_done
                #     obj.progress = obj.own_progress

                obj.save()
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
        execution_delay = now() - datetime.timedelta(seconds=settings.USER_TASK_EXECUTION_DELAY)
        start_date_limit = now() - datetime.timedelta(seconds=3 * 24 * 60 * 60)
        return self \
            .filter(Q(main_task__isnull=True) | Q(main_task_id=F('id'))) \
            .filter(status__in=UNREADY_STATES) \
            .exclude(name__in=settings.EXCLUDE_FROM_TRACKING) \
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
