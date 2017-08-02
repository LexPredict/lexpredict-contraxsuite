# -*- coding: utf-8 -*-

# Standard imports
import datetime

# Django imports
from django.db import models
from django.utils import timezone
from django_celery_results.models import TaskResult

# Project imports
from apps.users.models import User


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0/LICENSE.pdf"
__version__ = "1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@lexpredict.com"


class Task(models.Model):
    """Task object

    Task object designed to record the metadata around distributed celery tasks."""

    # Task name
    name = models.CharField(max_length=100, db_index=True)

    # celery task ID
    celery_task_id = models.CharField(max_length=36, db_index=True)

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

    def __str__(self):
        return "Task (name={}, celery_id={})" \
            .format(self.name, self.celery_task_id)

    @property
    def celery_task(self):
        return TaskResult.objects.get_task(task_id=self.celery_task_id)

    @property
    def status(self):
        initial = self.celery_task.status
        if initial == 'SUCCESS' and self.subtasks_total:
            if self.progress == 100:
                return 'SUCCESS'
            else:
                return 'PENDING'
        return self.celery_task.status

    @property
    def date_done(self):
        if self.status == 'SUCCESS':
            if self.subtasks_processed:
                date_done = self.celery_task.date_done
            elif self.subtasks_total:
                date_done = TaskResult.objects.filter(task_id__startswith='%s_' % self.id) \
                    .latest('date_done').date_done
            else:
                date_done = TaskResult.objects.get(task_id=self.celery_task_id).date_done
            return date_done
        return None

    @property
    def time(self):
        if self.status == 'PENDING':
            end_date = timezone.now()
        elif self.subtasks_processed:
            end_date = self.celery_task.date_done
        elif self.subtasks_total:
            try:
                end_date = TaskResult.objects.filter(task_id__startswith='%s_' % self.id) \
                    .latest('date_done').date_done
            except TaskResult.DoesNotExist:
                end_date = self.date_start
        else:
            end_date = self.celery_task.date_done

        return str(end_date - self.date_start).split('.')[0]

    @property
    def processed(self):
        if self.subtasks_processed:
            processed = self.subtasks_processed
        else:
            processed = TaskResult.objects.filter(task_id__startswith='%s_' % self.id).count()
        return processed

    @property
    def progress(self):
        if not self.subtasks_total:
            return 0
        return round(self.processed / int(self.subtasks_total) * 100)

    def push(self):
        self.subtasks_processed = (self.subtasks_processed or 0) + 1
        self.save()

    @property
    def uncompleted_subtasks(self):
        return int(self.subtasks_total) - self.processed
