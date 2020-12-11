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
from typing import Set, Dict

from celery.states import UNREADY_STATES, PENDING, SUCCESS, FAILURE, REVOKED
# Django imports
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.mail import send_mail
from django.db import models, connection
from django.db.models import Q
from django.db import transaction
from django.db.models import Count, Max, Sum
from django.db.models.deletion import CASCADE, SET_NULL
from django.db.models.signals import m2m_changed, post_save, post_delete
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.timezone import now
from guardian.shortcuts import assign_perm, get_content_type

# Project imports
from apps.common import redis
from apps.common.fields import StringUUIDField
from apps.common.models import get_default_status
from apps.document.models import DocumentType
from apps.extract.models import Term
from apps.project import signals
from apps.rawdb.repository.raw_db_repository import doc_fields_table_name
from apps.task.models import Task
from apps.users.models import User, CustomUserObjectPermission
from apps.users.permissions import *

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


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
    reviewers = models.ManyToManyField(User, blank=True)

    class Meta:
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
    task_queue = models.ForeignKey(TaskQueue, db_index=True, on_delete=CASCADE)

    # Affected documents
    documents = models.ManyToManyField('document.Document', blank=True)

    # Date
    date = models.DateTimeField(auto_now_add=True)

    # User
    user = models.ForeignKey(User, db_index=True, on_delete=CASCADE)

    # Action
    action = models.CharField(max_length=30, db_index=True, blank=True, null=True)

    class Meta:
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


class ProjectManager(models.Manager):
    use_in_migrations = True

    def get_queryset(self):
        return super(ProjectManager, self).get_queryset().filter(delete_pending=False)

    def qs_owners_reviewers_super_reviewers_by_doc_id(self, doc_id: int) -> models.QuerySet:
        from apps.document.models import Document
        project_query = Document.all_objects.filter(pk=doc_id).order_by().values_list('project_id', flat=True)
        try:
            project_id = project_query[0]
        except Exception as e:
            raise RuntimeError(
                f'qs_owners_reviewers_super_reviewers_by_doc_id: no documents found for doc_id="{doc_id}"') from e

        return User.objects.filter(Q(project_owners__pk=project_id) |
                                   Q(project_junior_reviewers__pk=project_id) |
                                   Q(project_reviewers__pk=project_id) |
                                   Q(project_super_reviewers__pk=project_id))


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

    # Reviewers who can upload docs
    super_reviewers = models.ManyToManyField(User, related_name="project_super_reviewers", blank=True)

    # Reviewers who can edit only assigned docs
    junior_reviewers = models.ManyToManyField(User, related_name="project_junior_reviewers", blank=True)

    # Status
    status = models.ForeignKey('common.ReviewStatus', default=get_default_status,
                               blank=True, null=True, on_delete=CASCADE)

    # Whether send or not email notification when upload is started
    send_email_notification = models.BooleanField(default=False, db_index=True)

    # selected for Delete admin task
    delete_pending = models.BooleanField(default=False, null=False)

    # project level setting for Hide Clause Review
    hide_clause_review = models.BooleanField(default=True, null=False)

    # Document types for a Project
    type = models.ForeignKey(
        'document.DocumentType',
        default=DocumentType.generic_pk,
        null=True, blank=True, db_index=True, on_delete=CASCADE)

    all_objects = models.Manager()

    objects = ProjectManager()

    class Meta:
        ordering = ['name']
        permissions = (
            ('view_documents', 'View project documents'),
            ('recluster_project', 'Re-cluster project documents'),
            ('add_project_user', 'Add project user'),
            ('add_project_document', 'Add project document'),
            ('detect_field_values', 'Detect field values in a project'),
            ('individual_assign', 'Assign document'),
            ('bulk_assign', 'Bulk assign documents'),
            ('bulk_update_status', 'Bulk update document status'),
            ('view_project_stats', 'View project stats'),
            ('change_document_field_values', 'Change field values in project documents'),
            ('change_document_status', 'Change status of individual document in a project'),
            ('delete_documents', 'Delete project documents'),
        )

    def __str__(self):
        """"
        String representation
        """
        return "Project (pk={0}, name={1})" \
            .format(self.pk, self.name)

    def _fire_saved(self, old_instance=None):
        signals.project_saved.send(self.__class__, user=None, instance=self, old_instance=old_instance)

    @property
    def available_assignees(self):
        # TODO: do not use union as it doesn't work with filters
        return self.owners.all() \
            .union(self.junior_reviewers.all()) \
            .union(self.super_reviewers.all()) \
            .union(self.reviewers.all()) \
            .distinct()

    @property
    def all_document_set(self):
        from apps.document.models import Document
        return Document.all_objects.filter(project=self)

    def save(self, **kwargs):
        if not self.type:
            self.type = DocumentType.generic()
        old_instance = Project.objects.filter(pk=self.pk).first()
        res = super().save(**kwargs)
        self._fire_saved()
        with transaction.atomic():
            transaction.on_commit(lambda: self._fire_saved(old_instance))
        return res

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

    def last_session(self, create=True, created_by=None):
        session = self.uploadsession_set.order_by('created_date').last()
        if not session and create:
            _ = UploadSession.objects.create(project=self, created_by=created_by)
            return self.last_session(created_by=created_by)
        return session

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
        return self.task_set.all()

    def project_tasks_progress(self, get_completed=False):
        """
        Detailed Progress of project tasks like Clustering
        """
        return self.project_tasks.progress(get_completed=get_completed)

    @property
    def project_tasks_completed(self):
        """
        Whether project tasks completed or not (None if no project tasks at all)
        """
        return self.project_tasks.completed()

    def drop_clusters(self, exclude_task_ids: Set = None, exclude_project_clustering_id: int = None):
        project = self
        # Stop running tusks
        from apps.task.tasks import purge_task
        from apps.project.tasks import ClusterProjectDocuments
        task_qr = project.project_tasks \
            .filter(name=ClusterProjectDocuments.name, status__in=UNREADY_STATES)  # type: QuerySet
        if exclude_task_ids:
            task_qr = task_qr.exclude(pk__in=exclude_task_ids)

        for task in task_qr:
            purge_task(task.pk, wait=True, timeout=1.5)
        # delete DocumentClusters
        for pcl in project.projectclustering_set.all():
            pcl.document_clusters.all().delete()
        # delete ProjectClustering
        project.projectclustering_set.exclude(id=exclude_project_clustering_id).delete()
        # delete ClusterProjectDocuments Tasks
        to_delete_qr = project.project_tasks.filter(name=ClusterProjectDocuments.name,
                                                    status__in=[SUCCESS, PENDING])  # type: QuerySet
        if exclude_task_ids:
            to_delete_qr = to_delete_qr.exclude(pk__in=exclude_task_ids)
        to_delete_qr.delete()

    def cleanup(self, delete=False):

        project = self

        # delete prev. CleanProject Task
        Task.objects.filter_metadata(task_name='clean-project',
                                     _project_id=project.pk).delete()

        # delete prev. Reassigning Task
        Task.objects.filter_metadata(task_name='reassigning',
                                     old_project_id=project.pk).delete()

        # delete clusters/tasks
        project.drop_clusters()

        # delete Project Tasks
        project.project_tasks.delete()

        # delete UploadSession Tasks
        for ups in project.uploadsession_set.all():
            ups.document_set.update(upload_session=None)
            ups.session_tasks.delete()

        # delete UploadSessions
        project.uploadsession_set.all().delete()

        # delete Documents
        # project.document_set.all().delete()

        # delete project itself
        if delete:
            project.delete()

    def get_team(self):
        return self.owners.all() \
            .union(self.reviewers.all()) \
            .union(self.super_reviewers.all()) \
            .union(self.junior_reviewers.all())

    def reset_project_team_perms(self):
        """
        Needed in case if a user team status is changed, in this case
        a signal which creates new permission may precede a signal which deletes that permission
        in this case we'll loose user permissions
        """
        if self.owners.exists():
            for perm_name in owner_project_permissions:
                assign_perm(perm_name, self.owners.all(), self)

        if self.super_reviewers.exists():
            for perm_name in super_reviewer_project_permissions:
                assign_perm(perm_name, self.super_reviewers.all(), self)

        reviewers = self.reviewers.difference(self.super_reviewers.all())
        if reviewers.exists():
            for perm_name in reviewer_project_permissions:
                assign_perm(perm_name, reviewers, self)

        if self.junior_reviewers.exists():
            for perm_name in junior_reviewer_project_permissions:
                assign_perm(perm_name, self.junior_reviewers.all(), self)

    def clean_up_assignees(self, removed_user_ids):
        if not removed_user_ids:
            return

        documents_qs = self.document_set.filter(assignee_id__in=removed_user_ids)
        if documents_qs.exists():
            document_ids = list(documents_qs.values_list('pk', flat=True))
            documents_qs.update(assignee=None)
            from apps.rawdb.tasks import plan_reindex_tasks_in_chunks
            from apps.document.repository.document_field_repository import DocumentFieldRepository
            from apps.document.constants import DocumentSystemField

            field_repo = DocumentFieldRepository()
            field_repo.update_docs_assignee(document_ids, None)
            plan_reindex_tasks_in_chunks(document_ids, None,
                                         cache_system_fields=[DocumentSystemField.assignee.value],
                                         cache_generic_fields=False, cache_user_fields=False)

        from apps.document.models import FieldAnnotation, FieldAnnotationFalseMatch
        FieldAnnotation.objects.filter(
            document__project=self, assignee_id__in=removed_user_ids).update(assignee=None)
        FieldAnnotationFalseMatch.objects.filter(
            document__project=self, assignee_id__in=removed_user_ids).update(assignee=None)


@receiver(post_delete, sender=Project)
def delete_cached_terms(sender, instance, **kwargs):
    from apps.extract.dict_data_cache import CACHE_KEY_TERM_STEMS_PROJECT_PTN, DbCache
    DbCache.clean_cache(CACHE_KEY_TERM_STEMS_PROJECT_PTN.format(instance.pk))
    redis.r.delete(CACHE_KEY_TERM_STEMS_PROJECT_PTN.format(instance.pk))


@receiver(post_save, sender=Project)
def reviewers_total(sender, instance, **kwargs):

    # TODO: add junior_reviewers into reviewers? it'd better keep all of them separate

    all_reviewers_pk = set(instance.reviewers.values_list('pk', flat=True))
    super_reviewers_pk = set(instance.super_reviewers.values_list('pk', flat=True))
    extra_pk = super_reviewers_pk - all_reviewers_pk
    if extra_pk:
        instance.reviewers.add(*extra_pk)


@receiver(post_delete, sender=Project)
def delete_perms_on_project_removed(sender, instance, **kwargs):
    ctype = get_content_type(Project)
    CustomUserObjectPermission.objects.filter(content_type=ctype, object_pk=instance.pk).delete()


@receiver(m2m_changed, sender=Project.junior_reviewers.through)
def remove_junior_reviewers_perms(instance, action, pk_set, **kwargs):
    if action == 'post_remove':
        users = User.objects.filter(pk__in=pk_set)
        if action == 'post_remove':
            for perm_name in junior_reviewer_project_permissions:
                remove_perm(perm_name, users, instance)


@receiver(m2m_changed, sender=Project.reviewers.through)
def remove_reviewers_perms(instance, action, pk_set, **kwargs):
    if action == 'post_remove':
        users = User.objects.filter(pk__in=pk_set)
        if action == 'post_remove':
            for perm_name in reviewer_project_permissions:
                remove_perm(perm_name, users, instance)


@receiver(m2m_changed, sender=Project.super_reviewers.through)
def remove_super_reviewers_perms(instance, action, pk_set, **kwargs):
    if action == 'post_remove':
        users = User.objects.filter(pk__in=pk_set)
        if action == 'post_remove':
            for perm_name in super_reviewer_project_permissions:
                remove_perm(perm_name, users, instance)


@receiver(m2m_changed, sender=Project.owners.through)
def remove_owners_perms(instance, action, pk_set, **kwargs):
    if action == 'post_remove':
        users = User.objects.filter(pk__in=pk_set)
        if action == 'post_remove':
            for perm_name in owner_project_permissions:
                remove_perm(perm_name, users, instance)


class UploadSession(models.Model):
    """
    UploadSession object to store info about uploading project documents.
    """
    # temporary variables to prevent recalculating while one db request session
    _document_tasks_progress = None

    # Unique id
    uid = StringUUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Project
    project = models.ForeignKey(Project, null=True, blank=True, db_index=True, on_delete=CASCADE)

    created_date = models.DateTimeField(auto_now_add=True, db_index=True)

    created_by = models.ForeignKey(
        User, related_name="created_%(class)s_set",
        null=True, blank=True, db_index=True, on_delete=CASCADE)

    completed = models.NullBooleanField(null=True, blank=True, db_index=True)

    notified_upload_started = models.BooleanField(default=False, db_index=True)
    notified_upload_completed = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['project_id', 'created_date']

    def __str__(self):
        """"
        String representation
        """
        return "Upload Session (pk={0}, project_id={1})" \
            .format(self.pk, self.project.pk if self.project else None)

    @property
    def session_tasks(self):
        """
        Get tasks related with session
        """
        return self.task_set.main_tasks()

    @property
    def session_tasks_progress(self):
        """
        Progress per document per task
        """
        return [{'file_name': i['metadata']['file_name'],
                 'task_id': i['pk'],
                 'task_name': i['name'],
                 'task_status': i['status'],
                 'task_progress': i['progress']}
                for i in self.session_tasks.values('pk', 'metadata', 'name', 'status', 'progress')
                if i['metadata'].get('file_name')]

    def document_tasks_progress(self, details=False):
        """
        Progress per document (avg session document tasks progress)
        """
        result = self.document_set.annotate(document_id=models.F('id')) \
            .values('document_id', 'name', 'file_size', 'processed')
        for i in result:
            i['tasks_overall_status'] = SUCCESS if i['processed'] is True else None
        result = {i['name']: i for i in result}

        from apps.project.tasks import LoadArchive
        session_tasks_progress = [i for i in sorted(self.session_tasks_progress, key=lambda i: i['file_name'])
                                  if i['task_name'] != LoadArchive.name]
        for file_name, task_progress_data in itertools.groupby(
                session_tasks_progress,
                key=lambda i: i['file_name']):
            task_progress_data = list(task_progress_data)
            document_progress = round(sum([int(i.get('task_progress') or 0) for i in task_progress_data]), 2)
            task_statuses = {i['task_status'] for i in task_progress_data}
            if None in task_statuses or PENDING in task_statuses:
                task_status = PENDING
            elif task_statuses == {SUCCESS}:
                task_status = SUCCESS
            else:
                task_status = FAILURE

            file_data = result.get(file_name, {'document_id': None, 'file_size': None, 'processed': False})
            file_data.update({'file_name': file_name, 'tasks_overall_status': task_status,
                              'document_progress': document_progress if task_status == PENDING else 100.0})

            if details:
                file_data['task_progress_data'] = task_progress_data

            result[file_name] = file_data
        # store result for further processing in status() and document_tasks_progress_total()
        self._document_tasks_progress = result
        return result

    def get_document_loading_progress(self) -> Dict[str, int]:
        from apps.task.tasks import LoadDocuments
        # from apps.project.tasks import LoadArchive
        load_tasks_total = Task.objects.filter(
            name__in=[LoadDocuments.name],
            upload_session_id=self.pk).count()

        docs = self.document_set.all()
        doc_type = self.project.type

        docs_count = docs.count()
        docs_count = max(load_tasks_total, docs_count)
        doc_ids = list(docs.values_list('pk', flat=True))

        docs_cached = 0
        if doc_ids:
            doc_ids_str = ','.join([str(id) for id in doc_ids])
            cache_table_name = doc_fields_table_name(doc_type.code)
            with connection.cursor() as cursor:
                cursor.execute(f'''SELECT COUNT(*) FROM "{cache_table_name}" WHERE document_id IN ({doc_ids_str});''')
                row = cursor.fetchone()
                docs_cached = row[0]

        # total progress is a weighted sum
        result = {'task_count': load_tasks_total,
                  'docs_count': docs_count,
                  'docs_cached': docs_cached}
        progress = 0

        if docs_count > 0:
            numerator = result['docs_cached']
            progress = round(100 * numerator / docs_count, 1)
        result['progress'] = progress
        return result

    @property
    def document_tasks_progress_total(self):
        """
        Total Progress of session document tasks (i.e. session progress)
        """
        document_tasks_progress = self._document_tasks_progress or self.document_tasks_progress()
        _p = [i.get('document_progress', 100 if i['processed'] is True else (i.get('tasks_overall_status') != PENDING) * 100)
              for i in document_tasks_progress.values()]
        return round(sum(_p) / float(len(_p)), 2) if _p else 0

    @property
    def documents_total_size(self):
        return self.document_set.aggregate(Sum('file_size')).get('file_size__sum')

    @property
    def status(self):
        """
        Verbose status - one of 'Parsed', 'Parsing'
        """
        if self.completed is None:
            return None
        return 'Parsed' if self.completed else 'Parsing'

    def status_check(self):
        """
        The same as status() - but make check if session is completed
        """
        self.check_and_set_completed()
        return self.status

    def check_and_set_completed(self):
        """
        Check and set "completed"
        """
        if self.completed:
            return True
        if not self.session_tasks.exists():
            # session tasks already deleted but documents exist-i.e. session has ended some time ago
            if self.document_set.exists():
                completed = True
            # no documents uploaded into session and more that 1 day passed
            elif (now() - self.created_date).days >= 1:
                completed = True
            else:
                return None
        else:
            completed = not self.session_tasks.filter(status=PENDING).exists()
        if self.completed != completed:
            self.completed = completed
            self.save()
        return completed

    def notify_upload_started(self):
        ctx = {'session': self}
        to = [self.created_by.email]
        subject = 'ContraxSuite: Batch upload job is started'
        text_message = render_to_string("email/notify_upload_started.txt", ctx)
        html_message = render_to_string("email/notify_upload_started.html", ctx)
        from apps.notifications.mail_server_config import MailServerConfig
        from apps.common.app_vars import SUPPORT_EMAIL
        backend = MailServerConfig.make_connection_config()
        send_mail(subject=subject, message=text_message, from_email=SUPPORT_EMAIL.val or settings.DEFAULT_FROM_EMAIL,
                  recipient_list=to, html_message=html_message, connection=backend)
        self.notified_upload_started = True
        self.save()

    def notify_upload_completed(self):
        ctx = {'session': self,
               'data': self.document_tasks_progress().values(),
               'completed_at': self.session_tasks.values('date_done').aggregate(m=Max('date_done'))['m']}
        to = [self.created_by.email]
        subject = 'ContraxSuite: Batch upload job is completed'
        text_message = render_to_string("email/notify_upload_completed.txt", ctx)
        html_message = render_to_string("email/notify_upload_completed.html", ctx)
        from apps.notifications.mail_server_config import MailServerConfig
        backend = MailServerConfig.make_connection_config()
        from apps.common.app_vars import SUPPORT_EMAIL
        send_mail(subject=subject, message=text_message, from_email=SUPPORT_EMAIL.val or settings.DEFAULT_FROM_EMAIL,
                  recipient_list=to, html_message=html_message, connection=backend)
        self.notified_upload_completed = True
        self.save()


@receiver(models.signals.post_save, sender=UploadSession)
def save_upload(sender, instance, created, **kwargs):
    """
    Store created_by from request
    """
    if hasattr(instance, 'request_user'):
        models.signals.post_save.disconnect(save_upload, sender=sender)
        if created and not instance.created_by:
            instance.created_by = instance.request_user
            instance.save()
        models.signals.post_save.connect(save_upload, sender=sender)


class ProjectClustering(models.Model):
    project = models.ForeignKey(Project, on_delete=CASCADE)

    document_clusters = models.ManyToManyField('analyze.DocumentCluster', blank=True)

    task = models.ForeignKey('task.Task', blank=True, null=True, on_delete=SET_NULL)

    metadata = JSONField(default=dict, blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True, db_index=True)

    status = models.CharField(max_length=10, blank=True, null=True)

    reason = models.TextField(blank=True, null=True)

    def __str__(self):
        """"
        String representation
        """
        return "Project Clustering (pk={0}, project_id={1}, status={2})" \
            .format(self.pk, self.project.pk, self.status)

    @property
    def completed(self):
        if self.task:
            return self.task.progress == 100
        return None

    def set_status_by_task(self):
        if not self.task:
            return
        new_status = self.status

        if self.task.status in {FAILURE, REVOKED}:
            new_status = FAILURE
        elif self.status == SUCCESS:
            new_status = SUCCESS
        elif self.status in UNREADY_STATES:
            new_status = PENDING
        if new_status == self.status:
            return
        self.status = new_status
        self.save(update_fields=['status'])


class ProjectTermConfiguration(models.Model):
    """
    This object allows for the configuration of project-specific terms,
    i.e., enabling/disabling terms for individual project.
    """
    # Project link
    project = models.OneToOneField(Project, db_index=True, on_delete=CASCADE)

    # Term link
    terms = models.ManyToManyField('extract.Term', db_index=True)

    class Meta:
        ordering = ['project__name']

    def __str__(self):
        return "ProjectTermConfiguration (project={})" \
            .format(self.project)

    def excluded_terms(self):
        all_terms = Term.objects.all()
        project_terms = self.terms.all()
        return all_terms.difference(project_terms)


@receiver(m2m_changed, sender=ProjectTermConfiguration.terms.through)
def cache_terms(instance, action, pk_set, **kwargs):
    # cache project terms only in case if terms have changed, i.e. pk_set != {}
    if action.startswith('post') and pk_set:
        from apps.extract.dict_data_cache import cache_term_stems
        cache_term_stems(instance.project.pk)


@receiver(post_delete, sender=ProjectTermConfiguration)
def delete_cached_terms_2(sender, instance, **kwargs):
    from apps.extract.dict_data_cache import CACHE_KEY_TERM_STEMS_PROJECT_PTN, DbCache
    DbCache.clean_cache(CACHE_KEY_TERM_STEMS_PROJECT_PTN.format(instance.project.pk))
    redis.r.delete(CACHE_KEY_TERM_STEMS_PROJECT_PTN.format(instance.project.pk))


class UserProjectsSavedFilter(models.Model):
    """
    Selected by a User projects (saved filter)
    Used in Explorer UI to limit Documents/other querysets
    """
    projects = models.ManyToManyField(Project, db_index=True)

    user = models.OneToOneField('users.User', db_index=True, on_delete=CASCADE)

    def __str__(self):
        return "UserProjectsSavedFilter (user={})".format(self.user)
