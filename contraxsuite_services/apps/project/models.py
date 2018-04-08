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
import itertools
import uuid

# Django imports
from django.db import models
from django.db.models import Count
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.postgres.fields import JSONField

# Project imports
from apps.common.models import ReviewStatus
from apps.document.models import DocumentType
from apps.task.models import Task
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.8/LICENSE"
__version__ = "1.0.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def all_reviewers_and_managers():
    return {'role__in': ['reviewer', 'manager']}


class TaskQueue(models.Model):
    """TaskQueue object model

    TaskQueue is a class used to record zero or more documents assigned to zero or more
    reviewers within one project.
    """
    # Description
    description = models.TextField(null=True, db_index=True)

    # Document list
    documents = models.ManyToManyField('document.Document', blank=True)

    # Completed document set
    completed_documents = models.ManyToManyField(
        'document.Document', related_name='completed_documents_task_queue', blank=True)

    # Reviewer set
    reviewers = models.ManyToManyField(
        User, limit_choices_to=all_reviewers_and_managers, blank=True)

    class Meta(object):
        ordering = ['description']

    def __str__(self):
        """"
        String representation
        """
        return "TaskQueue (pk={0}, documents={1}, reviewers={2}, description={3})" \
            .format(self.pk, self.documents.count(), self.reviewers.count(), self.description)

    @property
    def completed(self):
        """
        Bool, check whether 100% documents are completed
        """
        return self.documents.exists() and not self.documents.difference(
            self.completed_documents.all())

    def progress(self, as_dict=False):
        """
        Get % of completed documents in TaskQueue.
        :param as_dict:
        :return:
        """
        total_docs = self.documents.count()
        completed_docs = self.documents.intersection(
            self.completed_documents.all()).distinct().count()
        progress = 0 if not total_docs else round(completed_docs / total_docs * 100, 2)
        if as_dict:
            return dict(
                total_documents_count=total_docs,
                completed_documents_count=completed_docs,
                progress=progress
            )
        return progress

    @property
    def completed_date(self):
        if not self.completed:
            return None
        return self.taskqueuehistory_set.filter(
            action='complete_document').latest('date').date

    @property
    def complete_history(self):
        history = []
        for d in self.documents.all():
            if not self.completed_documents.filter(pk=d.pk).exists():
                d.complete_history = None
            else:
                d.complete_history = d.taskqueuehistory_set.filter(
                    task_queue=self, action='complete_document').latest('date')
            history.append(d)
        return history

    def document_complete_history(self, document_pk):
        if self.completed_documents.filter(pk=document_pk).exists():
            return TaskQueueHistory.objects.filter(
                documents__pk=document_pk,
                task_queue=self,
                action='complete_document').latest('date')
        else:
            return None


class TaskQueueHistory(models.Model):
    """TaskQueueHistory object model

    TaskQueueHistory is a class used to record the history of actions within
    a task queue, including document completion.
    """
    # Task queue
    task_queue = models.ForeignKey(TaskQueue, db_index=True)

    # Affected documents
    documents = models.ManyToManyField('document.Document', blank=True)

    # Date
    date = models.DateTimeField(auto_now_add=True)

    # User
    user = models.ForeignKey(User, db_index=True)

    # Action
    action = models.CharField(max_length=30, db_index=True, blank=True, null=True)

    class Meta(object):
        verbose_name_plural = 'Task Queues History'
        ordering = ['-date']

    def __str__(self):
        """"
        String representation
        """
        return "TaskQueueHistory (pk={0}, action={1}, date={2})" \
            .format(self.pk, self.action, self.date)


@receiver(m2m_changed, sender=TaskQueue.documents.through)
def documents_changed(instance, action, pk_set, **kwargs):
    if action.startswith('post_'):
        tqh = TaskQueueHistory.objects.create(
            task_queue=instance,
            user=instance.request_user,
            action='%s_document' % action[5:]
        )
        tqh.documents.add(*list(pk_set))
        if action == 'post_remove':
            # remove the same document from completed
            instance.completed_documents.remove(*list(pk_set))


@receiver(m2m_changed, sender=TaskQueue.completed_documents.through)
def completed_documents_changed(instance, action, pk_set, **kwargs):
    if action.startswith('post_'):
        # mark document completed
        if action.endswith('add'):
            action = 'complete_document'
        # unmark document completed - reopen
        elif instance.documents.filter(pk__in=pk_set).exists():
            action = 'reopen_documents'
        # remove document from task queue
        else:
            return
        tqh = TaskQueueHistory.objects.create(
            task_queue=instance,
            user=instance.request_user,
            action=action
        )
        tqh.documents.add(*list(pk_set))


class Project(models.Model):
    """Project object model

    Project is a class used to record zero or more task queues
    with zero or more reviewers and documents.
    """
    # Project name
    name = models.CharField(max_length=100, db_index=True)

    # Project description
    description = models.TextField(blank=True, null=True)

    # Task queue set
    task_queues = models.ManyToManyField(TaskQueue, blank=True)

    # Owners set
    owners = models.ManyToManyField(User, related_name="project_owners", blank=True)

    # Reviewers team
    reviewers = models.ManyToManyField(User, related_name="project_reviewers", blank=True)

    # Status
    status = models.ForeignKey(ReviewStatus, default=ReviewStatus.initial_status_pk(),
                               blank=True, null=True)

    # Document types for a Project
    type = models.ForeignKey(
        'document.DocumentType',
        default=DocumentType.generic_pk,
        null=True, blank=True, db_index=True)

    class Meta(object):
        ordering = ['name']

    def __str__(self):
        """"
        String representation
        """
        return "Project (pk={0}, name={1})" \
            .format(self.pk, self.name)

    def save(self, **kwargs):
        if not self.type:
            self.type = DocumentType.generic()
        return super().save(**kwargs)

    def progress(self, as_dict=False):
        """
        Get % of completed documents in Project's TaskQueues
        :param as_dict:
        :return:
        """
        total_docs = sum(self.task_queues.annotate(s=Count('documents')).values_list('s', flat=True))
        completed_docs = sum(self.task_queues.annotate(s=Count('completed_documents')).values_list('s', flat=True))
        progress = 0 if not total_docs else round(completed_docs / total_docs * 100, 2)
        if as_dict:
            return dict(
                total_documents_count=total_docs,
                completed_documents_count=completed_docs,
                progress=progress
            )
        return progress

    @property
    def progress_as_dict(self):
        return self.progress(as_dict=True)

    @property
    def completed(self):
        """
        Bool, check whether project is 100% completed
        """
        return self.progress() == 100

    @property
    def completed_date(self):
        if not self.completed:
            return None
        return TaskQueueHistory.objects.filter(
            task_queue__project=self,
            task_queue__action='complete_document') \
            .latest('date').date

    @property
    def project_tasks(self):
        """
        Get tasks related with Project
        """
        return Task.special_tasks({'project_id': str(self.pk)})

    @property
    def project_tasks_progress(self):
        """
        Detailed Progress of project tasks like Clustering
        """
        return Task.special_tasks_progress({'project_id': str(self.pk)})

    @property
    def project_tasks_completed(self):
        """
        Whether project tasks completed or not (None if no project tasks at all)
        """
        return Task.special_tasks_completed({'project_id': str(self.pk)})


class UploadSession(models.Model):
    """
    UploadSession object to store info about uploading project documents.
    """

    # Unique id
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Project
    project = models.ForeignKey(Project, db_index=True)

    created_date = models.DateTimeField(auto_now_add=True, db_index=True)

    created_by = models.ForeignKey(
        User, related_name="created_%(class)s_set", null=True, blank=True, db_index=True)

    completed = models.BooleanField(default=False, db_index=True)

    class Meta(object):
        ordering = ['project_id', 'created_date']

    def __str__(self):
        """"
        String representation
        """
        return "Upload Session (pk={0}, project_id={1})" \
            .format(self.pk, self.project.pk)

    @property
    def session_tasks(self):
        """
        Get tasks related with session
        """
        return Task.special_tasks({'session_id': str(self.pk)})

    @property
    def document_progress_data(self):
        """
        Progress per document per task
        """
        return [{'file_name': i.metadata['file_name'],
                 'task_name': i.name,
                 'task_progress': 100 if i.status == 'SUCCESS' else 0}
                for i in self.session_tasks if i.metadata.get('file_name')]

    @property
    def document_tasks_progress(self):
        """
        Progress per document
        """
        result = {}
        tasks_number = 3 if self.project.type else 2
        for file_name, task_progress_data in itertools.groupby(
                sorted(self.document_progress_data, key=lambda i: i['file_name']),
                key=lambda i: i['file_name']):
            document_progress = round(
                sum([int(i['task_progress'])
                     for i in task_progress_data][:tasks_number]) / tasks_number, 2)
            result[file_name] = document_progress
        return result

    @property
    def document_tasks_progress_total(self):
        """
        Total Progress of custom document tasks
        """
        _p = list(self.document_tasks_progress.values())
        return round(sum(_p) / float(len(_p)), 2) if _p else 0

    @property
    def status(self):
        """
        Get session status - one of 'Parsed', 'Parsing'
        set 'completed'
        """
        # no tasks started / no files processed
        if not self.session_tasks.exists():
            status = None
        else:
            document_tasks_completed = self.document_tasks_progress_total == 100
            status = 'Parsed' if document_tasks_completed else 'Parsing'
            if status == 'Parsed':
                self.completed = True
            self.save()
        return status


@receiver(models.signals.post_save, sender=UploadSession)
def save_upload(sender, instance, created, **kwargs):
    """
    Store created_by from request
    """
    if hasattr(instance, 'request_user'):
        models.signals.post_save.disconnect(save_upload, sender=sender)
        if created:
            instance.created_by = instance.request_user
        instance.save()
        models.signals.post_save.connect(save_upload, sender=sender)


class ProjectClustering(models.Model):

    project = models.ForeignKey(Project)

    document_clusters = models.ManyToManyField('analyze.DocumentCluster', blank=True)

    task = models.ForeignKey('task.Task', blank=True, null=True)

    metadata = JSONField(default={}, blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        """"
        String representation
        """
        return "Project Clustering (pk={0}, project_id={1})" \
            .format(self.pk, self.project.pk)

    @property
    def completed(self):
        if self.task:
            return self.task.progress == 100
        return None
