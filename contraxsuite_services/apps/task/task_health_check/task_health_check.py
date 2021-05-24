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

from dataclasses import dataclass
from time import time
from typing import Set, List, Dict, Any, Callable

from celery.app.control import Inspect
from django.conf import settings
from django.db.models import F

from apps.celery import app
from apps.common.log_utils import ProcessLogger
from apps.task.models import Task

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


TASK_BAD_HEALTH_CHECK_RETRIES = 3
IGNORE_WORKER_KINDS = {'beat'}


@dataclass
class CeleryStats:
    # Ids of tasks seen at any worker.
    tasks_on_workers: Set[str]

    free_workers_available_of_any_kind: bool


def get_celery_stats() -> CeleryStats:
    task_ids = set()
    i = Inspect(app=app)

    all_workers = set()
    workers_with_tasks = set()

    def collect_task_ids(worker_tasks: Dict[str, List[Dict[str, Any]]]):
        if worker_tasks:
            for worker_name, worker_tasks in worker_tasks.items():
                all_workers.add(worker_name)
                if not worker_tasks:
                    continue
                workers_with_tasks.add(worker_name)
                for t in worker_tasks:
                    if not t:
                        continue
                    task_ids.add(t.get('id'))

    collect_task_ids(i.active())
    collect_task_ids(i.scheduled())
    collect_task_ids(i.reserved())

    workers_without_tasks = all_workers.difference(workers_with_tasks)
    all_worker_kinds = {worker_name[:worker_name.index('@')] for worker_name in all_workers}
    free_workers_available_kinds = {worker_name[:worker_name.index('@')]
                                    for worker_name in workers_without_tasks}

    all_worker_kinds.difference_update(IGNORE_WORKER_KINDS)
    free_workers_available_kinds.difference_update(IGNORE_WORKER_KINDS)

    return CeleryStats(tasks_on_workers=task_ids,
                       free_workers_available_of_any_kind=all_worker_kinds and
                                                          (free_workers_available_kinds == all_worker_kinds))


def check_task_health(log: ProcessLogger,
                      restart_task_func: Callable[[str], None]):
    """
    Find and process unhealthy tasks - the tasks which are hanging in PENDING while there is at least one
    free worker of each kind (default, high).
    This is intended to wait silently until all other tasks processed and next re-send the hanged PENDING tasks.


    Goal state: if there are PENDING tasks which are not known by any worker
                - there should not be free workers of all types.
    """
    start_time = time()

    inspect_start_time = time()
    celery_stats = get_celery_stats()
    inspect_time_spent = time() - inspect_start_time

    if not celery_stats.free_workers_available_of_any_kind:
        log.info(f'Task health check: there are no workers at all or at least some kind of worker is still busy.\n'
                 f'Not checking for the hanged tasks.'
                 f'Celery inspect time: {inspect_time_spent:.3f}s\n'
                 )
        return

    query_time_start = time()

    # There is at least one free worker of each kind.
    # This means there should be no PENDING tasks not known to workers.
    # Increasing bad health check counter for the PENDING tasks not known to workers.
    Task.objects \
        .filter(own_status='PENDING', bad_health_check_num__lt=TASK_BAD_HEALTH_CHECK_RETRIES) \
        .exclude(queue=settings.CELERY_QUEUE_SERIAL) \
        .exclude(name__in=settings.EXCLUDE_FROM_TRACKING) \
        .exclude(pk__in=celery_stats.tasks_on_workers) \
        .update(bad_health_check_num=F('bad_health_check_num') + 1)

    # Set bad counter to zero for all tasks on workers
    Task.objects \
        .filter(pk__in=celery_stats.tasks_on_workers) \
        .exclude(bad_health_check_num=0) \
        .update(bad_health_check_num=0)

    # Restarts those having the counter >= threshold

    to_restart = list(Task.objects
                      .filter(own_status='PENDING', bad_health_check_num=TASK_BAD_HEALTH_CHECK_RETRIES)
                      .values_list('pk', 'name'))

    query_time_spent = time() - query_time_start

    restarted_tasks = []
    could_not_restart_tasks = []
    for task_id, task_name in to_restart:
        try:
            restart_task_func(task_id)
            restarted_tasks.append((task_id, task_name))
        except Exception as ex:
            log.error(f'Unable to restart task {task_name} ({task_id})', exc_info=ex)
            could_not_restart_tasks.append((task_id, task_name))

    restarted_msg = '\n'.join(task_id + " " + task_name
                              for task_id, task_name in restarted_tasks) if restarted_tasks else 'no'
    problem_restarting_msg = '\n'.join(task_id + " " + task_name
                                       for task_id, task_name in could_not_restart_tasks) if restarted_tasks else 'no'
    log.info(f'Checked task health. Found {len(to_restart)} unhealthy tasks.\n'
             f'Total time: {time() - start_time:.3f}s\n'
             f'Celery inspect time: {inspect_time_spent:.3f}s\n'
             f'DB query time: {query_time_spent:.3f}s\n'
             f'Restarted tasks:\n{restarted_msg}\n'
             f'Could not restart tasks:\n{problem_restarting_msg}', extra={'log_unhealthy_tasks': bool(to_restart)})
