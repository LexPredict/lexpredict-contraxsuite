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
import logging
from typing import List, Dict

from celery.states import FAILURE, PENDING

from apps.common.contraxsuite_urls import kibana_root_url
from apps.task.app_vars import ENABLE_ALERTS, ALERT_DEFAULT_INTERVAL
from apps.task.celery_backend.utils import now
from apps.task.models import TaskConfig, Task

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


server_logger = logging.getLogger("django.server")


class TaskRecord:
    def __init__(self,
                 task_id: str,
                 task_name: str,
                 message: str,
                 task_status: str,
                 task_started: datetime,
                 task_ended: datetime,
                 user_id: str,
                 stack_trace: str = '',
                 error_message: str = '',
                 kibana_ref: str = ''):
        self.task_id = task_id
        self.task_name = task_name
        self.message = message
        self.task_status = task_status
        self.task_started = task_started
        self.task_ended = task_ended
        self.stack_trace = stack_trace
        self.error_message = error_message
        self.user_id = user_id
        self.kibana_ref = kibana_ref

    def make_log_key_val(self) -> Dict[str, str]:
        r = {
            'log_elastalert': 'task_failed',
            'log_task_id': self.task_id,
            'log_task_name': self.task_name,
            'log_message': self.message,
            'log_task_status': self.task_status,
            'log_task_started': self.task_started,
            'log_task_ended': self.task_ended,
            'log_user_id': self.user_id,
            'log_stack_trace': self.stack_trace or '',
            'log_error_message': self.error_message or '',
            'log_kibana_ref': self.kibana_ref or ''
        }
        return r


class TaskMonitor:
    MESSAGE_COOLDOWN_SECONDS = 30

    @classmethod
    def report_on_failed_tasks(cls) -> None:
        """
        Find top-level tasks that are not completed for a long time or are in failed state
        and report on each of these tasks by one email
        """
        if not ENABLE_ALERTS.val:
            return
        configs = list(TaskConfig.objects.filter(notify_on_fail=True))
        if not configs:
            return

        all_names = [c.name for c in configs]
        now_time = now()
        # we wait N seconds for the log records to be stored
        failed_before = now_time - datetime.timedelta(seconds=cls.MESSAGE_COOLDOWN_SECONDS)
        failed_tasks = list(Task.objects.filter(status=FAILURE,
                                                parent_task_id__isnull=True,
                                                failure_reported=False,
                                                name__in=all_names,
                                                date_done__lt=failed_before))  # type: List[Task]

        default_watch_mins = ALERT_DEFAULT_INTERVAL.val
        name_by_interval = {c.watchdog_minutes or default_watch_mins: c.name for c in configs}
        for interval in name_by_interval:
            task_name = name_by_interval[interval]
            max_start = now_time - datetime.timedelta(minutes=interval)
            failed_tasks += Task.objects.filter(
                status=PENDING,
                parent_task_id__isnull=True,
                failure_reported=False, name=task_name, date_work_start__lt=max_start)

        if not failed_tasks:
            return
        # notify admin on failed tasks
        cls.send_emails_on_failed_tasks(failed_tasks)

    @classmethod
    def send_emails_on_failed_tasks(cls, tasks: List[Task]) -> None:
        try:
            for task in tasks:
                detail = cls.get_task_detail(task)
                msg = f'Task "{task.name}" {detail.message}'
                extra = detail.make_log_key_val()
                server_logger.error(msg, extra)
        finally:
            task_ids = [t.pk for t in tasks]
            Task.objects.filter(pk__in=task_ids).update(failure_reported=True)

    @classmethod
    def get_task_detail(cls, task: Task) -> TaskRecord:
        reason = f'is started at {task.date_work_start} and not finished yet' if task.status == PENDING else 'is failed'
        r = TaskRecord(task.pk, task.name, reason, task.status,
                       task.date_work_start or task.date_start,
                       task.date_done or task.own_date_done,
                       task.user_id)
        for record in task.get_task_log_from_elasticsearch():
            r.kibana_ref = kibana_root_url(record.record_id, record.file_index, add_protocol=False)
            if not hasattr(record, 'stack_trace') or not hasattr(record, 'message') \
                    or record.log_level != 'ERROR':
                continue
            r.error_message = record.message
            r.stack_trace = record.stack_trace
            break
        return r
