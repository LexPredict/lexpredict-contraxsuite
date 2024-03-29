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

# Project imports
from apps.common.models import AppVar

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


REMOVE_READY_TASKS_DELAY_IN_HOURS = AppVar.set(
    'Task', 'remove_ready_tasks_delay_in_hours', 48,
    'Delete ready tasks from the database after this number of hours after the task is finished')

REMOVE_FAILED_TASKS_DELAY_IN_DAYS = AppVar.set(
    'Task', 'remove_failed_tasks_delay_in_days', 30,
    'Delete failed tasks from the database after this number of days after the task is failed')

REMOVE_PENDING_TASKS_DELAY_IN_DAYS = AppVar.set(
    'Task', 'remove_pending_tasks_delay_in_days', 30,
    'Delete pending tasks from the database after this number of days after the task is started')

ENABLE_ALERTS = AppVar.set(
    'Task', 'enable_alerts', False,
    'Enable email alerts for failed / hanged tasks')

ALERT_DEFAULT_INTERVAL = AppVar.set(
    'Task', 'alert_default_interval', 60,
    'Default interval (minutes) before notify on pending task')

DISK_USAGE_PCNT_KEY = 'disk_usage_pcnt'

DISK_USAGE = AppVar.set(
    'Task', 'disk_usage', 0,
    'Disk usage percent, should be set dynamically by CRON task.')

FREE_DISK_SPACE = AppVar.set(
    'Task', 'free_disk', 10,
    'Free Disk space Gb, should be set dynamically by CRON task.')

DISK_USAGE_BLOCK_TASKS = AppVar.set(
    'Task', 'disk_usage_block_tasks', 85,
    'Block starting tasks and purge existing tasks if disk usage is greater then value.')

MIN_FREE_DISK_BLOCK_TASKS = AppVar.set(
    'Task', 'min_free_disk_block_tasks', 5,
    'Block starting tasks and purge existing tasks if free disk space is less then value.')

TASK_DIALOG_FREEZE_MS = AppVar.set(
    'Task', 'task_dialog_freeze_ms', 100,
    'Time interval (ms) for the new task window to load.')

EXTRA_EXCLUDED_FROM_TRACKING = AppVar.set(
    'Task', 'extra_excluded_from_tracking', '',
    'Task names to exclude from tracking, comma separated')

EXTRA_ALLOWED_FOR_TRACKING = AppVar.set(
    'Task', 'extra_allowed_for_tracking', '',
    'Task names to allow for tracking, comma separated')

ENABLE_TASK_HEALTH_CHECK = AppVar.set(
    'Task', 'enable_task_health_check', True,
    'Experimental. Enable special health check process which detect hanged tasks and restarts them')
