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
import datetime
import itertools

# Third-party inports
from simple_history.models import HistoricalRecords

# Django imports
from django.contrib.postgres.fields import JSONField
from django.db import models, transaction
from django.utils import timezone
from django.dispatch import receiver
from django_celery_results.models import TaskResult

# Project imports
from apps.users.models import User


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.8/LICENSE"
__version__ = "1.0.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class Task(models.Model):
    """Task object

    Task object designed to record the metadata around distributed celery tasks."""

    # Task name
    name = models.CharField(max_length=100, db_index=True)

    # celery task ID
    celery_task_id = models.CharField(max_length=36, db_index=True)

    # celery task
    celery_task_result = models.ForeignKey(TaskResult, blank=True, null=True, db_index=True)

    # Task start date
    date_start = models.DateTimeField(default=datetime.datetime.now, db_index=True)

    # Task requesting user
    user = models.ForeignKey(User, db_index=True, blank=True, null=True)

    # Task log
    log = models.TextField(blank=True, null=True)

    # Task error status
    has_error = models.BooleanField(default=False)

    # Task statistics
    subtasks_total = models.IntegerField(default=0, blank=True, null=True)
    subtasks_processed = models.IntegerField(default=0, blank=True, null=True)

    # additional data for a task
    metadata = JSONField(blank=True, null=True)

    # if task is visible
    visible = models.BooleanField(default=True)

    # Task history
    history = HistoricalRecords()

    # Task date done
    _date_done = models.DateTimeField(blank=True, null=True)

    # task last status
    _status = models.CharField(max_length=10, db_index=True, blank=True, null=True)

    # task last time
    _time = models.CharField(max_length=36, blank=True, null=True)

    # task last progress
    _progress = models.PositiveSmallIntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return "Task (name={}, celery_id={})" \
            .format(self.name, self.celery_task_id)

    def save(self, *args, **kwargs):
        """
        Do not track each update
        """
        self.skip_history_when_saving = True
        try:
            if not self.celery_task.pk:
                self.celery_task.save()
            ret = super().save(*args, **kwargs)
        finally:
            del self.skip_history_when_saving
        return ret

    @property
    def celery_task(self):
        celery_task = self.celery_task_result or \
                      TaskResult.objects.get_task(task_id=self.celery_task_id)
        # if not celery_task.id:
        #     return None
        return celery_task

    @property
    def status(self):
        if self._status == 'SUCCESS':
            status = 'SUCCESS'
        else:
            status = self.celery_task.status
            if status == 'SUCCESS' and self.subtasks_total:
                if self.progress == 100:
                    status = 'SUCCESS'
                else:
                    status = 'PENDING'
            if self._status != status:
                self._status = status
                self.save()
        return status

    @classmethod
    def disallow_start(cls, name):
        return any([t.status == 'PENDING' for t in Task.objects.filter(name=name)])

    @property
    def date_done(self):
        if self._date_done:
            result = self._date_done
        elif self.status == 'SUCCESS':
            if self.subtasks_processed:
                result = self.celery_task.date_done
            elif self.subtasks_total:
                result = TaskResult.objects.filter(task_id__startswith='%s_' % self.id) \
                    .latest('date_done').date_done
            else:
                result = self.celery_task.date_done
        elif self.status == 'FAILURE':
            result = self.celery_task.date_done
        else:
            result = None
        if result:
            self._date_done = result
            self.save()
        return result

    @property
    def time(self):
        if self.date_done and self._time:
            result = self._time
        else:
            status = self.status
            if status == 'PENDING' or not self.date_done:
                end_date = timezone.now()
            else:
                end_date = self.date_done
            result = str(end_date - self.date_start).split('.')[0]
            if status == 'SUCCESS':
                self._time = result
                self.save()
        return result

    @property
    def processed(self):
        if self.subtasks_processed:
            processed = self.subtasks_processed
        else:
            processed = TaskResult.objects.filter(task_id__startswith='%s_' % self.id).count()
        return processed

    @property
    def progress(self):
        if self._progress == 100:
            return 100
        if not self.subtasks_total:
            return 0
        save = False
        progress = round(self.processed / int(self.subtasks_total) * 100)
        if not self.subtasks_processed and progress == 100:
            self.subtasks_processed = self.subtasks_total
            save = True
        if self._progress != progress:
            self._progress = progress
            save = True
        if save:
            self.save()
        return progress

    def push(self, amount=1):
        self.subtasks_processed = (self.subtasks_processed or 0) + amount
        self.save()

    @classmethod
    def push_(cls, task_id, amount=1):
        with transaction.atomic():
            task = cls.objects.select_for_update().get(id=task_id)
            task.push()

    def force_complete(self):
        self.subtasks_total = 1
        self.subtasks_processed = 1
        self.save()

    @property
    def uncompleted_subtasks(self):
        return int(self.subtasks_total) - self.processed

    @classmethod
    def special_tasks(cls, filter_opts):
        """
        Get tasks related with key/value
        """
        opts = {'metadata__%s' % k: v for k, v in filter_opts.items()}
        return cls.objects \
            .filter(**opts) \
            .select_related('celery_task_result')

    @classmethod
    def special_tasks_progress(cls, filter_opts):
        """
        Detailed Progress of task
        """
        return {'{}-{}'.format(i.name, i.id):
                    {'name': i.name,
                     'id': i.id,
                     'progress': i.progress,
                     'completed': i.progress == 100}
                for i in cls.special_tasks(filter_opts)} or None

    @classmethod
    def special_tasks_progress_groups(cls, filter_opts):
        """
        Detailed Progress of tasks grouped by metadata
        """
        data = [{'progress': i.progress,
                 'completed': i.progress == 100,
                 'metadata': i.metadata.items()}
                for i in cls.special_tasks(filter_opts)]
        result = []
        for metadata, grouped_data in itertools.groupby(
                sorted(data, key=lambda i: i['metadata']),
                key=lambda i: i['metadata']):
            progress_data = [i['progress'] for i in grouped_data]
            group_progress = round(sum(progress_data) / len(progress_data), 2) if progress_data else 0
            metadata = dict(metadata)
            metadata['progress'] = group_progress
            metadata['completed'] = group_progress == 100
            result.append(metadata)
        return result

    @classmethod
    def special_tasks_completed(cls, filter_opts):
        """
        tasks completed or not (None if no tasks at all)
        """
        tasks_progress = cls.special_tasks_progress(filter_opts)
        if tasks_progress is None:
            return None
        progress_values = [i['progress'] for i in tasks_progress.values()]
        return ((sum(progress_values) / len(progress_values)) == 100) if progress_values else None

    @classmethod
    def delete_special_tasks(cls, kwargs):
        tasks = cls.special_tasks(kwargs)
        for task in tasks:
            sub_tasks = TaskResult.objects.filter(task_id__startswith='{}_'.format(task.id))
            if sub_tasks.exists():
                sub_tasks.delete()
            if task.celery_task:
                task.celery_task.delete()
            task.delete()
