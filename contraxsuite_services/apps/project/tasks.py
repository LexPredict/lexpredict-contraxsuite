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
import mimetypes
import os
import re
import tarfile
import time
import zipfile
from typing import Optional, Dict, Any, List

# Third-party imports
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from celery.states import FAILURE, PENDING, SUCCESS
from psycopg2 import InterfaceError, OperationalError

# Django imports
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.http import HttpRequest
from django.utils.timezone import now

# Project imports
import task_names
from apps.analyze.ml.cluster import ClusterDocuments
from apps.analyze.ml.features import EmptyDataSetError
from apps.celery import app
from apps.common.file_storage import get_file_storage
from apps.common.models import Action
from apps.document import signals
from apps.document.constants import DocumentGenericField
from apps.document.field_detection import field_detection
from apps.document.models import Document, DocumentType, TextUnit, FieldAnnotation, FieldAnnotationFalseMatch, \
    FieldAnnotationStatus
from apps.document.repository.base_document_repository import BaseDocumentRepository
from apps.document.repository.document_repository import DocumentRepository
from apps.project.models import Project, ProjectClustering, UploadSession
from apps.project.notifications import notify_active_upload_sessions, \
    notify_cancelled_upload_session, notify_update_project_document_fields_completed
from apps.project.utils.unique_name import UniqueNameBuilder
from apps.rawdb.constants import FIELD_CODE_STATUS_ID
from apps.task.tasks import CeleryTaskLogger, Task, purge_task, ExtendedTask
from apps.task.utils.task_utils import TaskUtils
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


THIS_MODULE = __name__
file_storage = get_file_storage()


class ClusterProjectDocuments(ExtendedTask):
    """
    Cluster Project Documents
    """
    name = 'Cluster Project Documents'

    soft_time_limit = 3 * 3600
    default_retry_delay = 10
    retry_backoff = True
    autoretry_for = (SoftTimeLimitExceeded, InterfaceError, OperationalError)
    max_retries = 3

    project_clustering_id = None

    min_log_interval_seconds = 60 * 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_times = {}  # type: Dict[str, Any]

    def process(self, **kwargs):

        n_clusters = kwargs.get('n_clusters', 3)
        method = kwargs.get('method', 'kmeans')
        cluster_by = kwargs.get('cluster_by', 'term')

        self.project_clustering_id = kwargs.get('project_clustering_id')
        project_clustering = ProjectClustering.objects.get(pk=self.project_clustering_id)
        project_clustering.status = PENDING
        project_clustering.task = self.task
        project_clustering.save()

        project = project_clustering.project

        self.log_info('Start clustering documents for project id={}'.format(project.id))
        self.log_info('Clustering method: "{}", n_clusters={}'.format(method, n_clusters))
        self.log_info('Cluster by: {}'.format(str(cluster_by)))

        self.set_push_steps(4)

        self.push()

        # clear previous clusters, their tasks and cluster sessions
        project.drop_clusters(exclude_task_ids={self.request.id},
                              exclude_project_clustering_id=self.project_clustering_id)
        self.push()

        cluster_model = ClusterDocuments(project_id=project.id,
                                         cluster_algorithm=method,
                                         n_clusters=n_clusters,
                                         cluster_by=cluster_by,
                                         use_default_name=True,
                                         log_message=self.log_wo_flooding)
        result = cluster_model.run()

        project_clustering.metadata = result.metadata
        project_clustering.save()
        project_clustering.document_clusters.add(*result.metadata['cluster_obj_ids'])

        self.push()
        self.log_info('Clustering completed. Updating document cache.')

        log = CeleryTaskLogger(self)
        for doc in Document.objects.filter(project__pk=project.id):
            signals.fire_document_changed(sender=self,
                                          log=log,
                                          document=doc,
                                          changed_by_user=None,
                                          system_fields_changed=False,
                                          user_fields_changed=False,
                                          generic_fields_changed=[DocumentGenericField.cluster_id.value])

        project_clustering.status = SUCCESS
        project_clustering.save()

        self.push()
        self.log_info('Finished.')
        return result.metadata

    def on_failure(self, exc, task_id, args, kwargs, exc_traceback):
        if self.project_clustering_id:
            project_clustering = ProjectClustering.objects.get(pk=self.project_clustering_id)
            project_clustering.status = FAILURE

            exc_str = str(exc)
            message_head = 'Clustering failed. '
            message_body = 'Unexpected error while clustering. Try again later.'
            low_features_message = 'Not enough data points for features ' \
                                   'of chosen "cluster by". Try adding documents, reducing number ' \
                                   'of clusters, or changing "cluster by" feature selection.'

            if ('max_df corresponds to < documents than min_df' in exc_str) or \
                    ('Number of samples smaller than number of clusters' in exc_str) or \
                    (re.search(r'n_samples=\d+ should be >= n_clusters=\d+', exc_str)) or \
                    (re.search(r'n_components=\d+ must be between 0 and min', exc_str)):
                message_body = low_features_message
            elif re.search(r'n_components=\d+ must be between \d+ and n_features=\d+', exc_str):
                message_body = 'Chosen documents look very similar,' \
                               ' clustering algorithm is not able to form clusters.'
            elif isinstance(exc, EmptyDataSetError):
                message_body = low_features_message
            else:
                message_body += ' \nOriginal issue is: "{}"'.format(exc_str)

            project_clustering.reason = message_head + message_body
            project_clustering.save()

        super().on_failure(exc, task_id, args, kwargs, exc_traceback)

    def log_wo_flooding(self, msg: str, msg_key='') -> None:
        if msg_key:
            last_call = self.log_times.get(msg_key)
            if last_call:
                if (datetime.datetime.now() - last_call).total_seconds() < self.min_log_interval_seconds:
                    return
        self.log_info(msg)
        if msg_key:
            self.log_times[msg_key] = datetime.datetime.now()


class ReassignProjectClusterDocuments(ExtendedTask):
    """
    Reassign Project Cluster Documents
    """
    name = 'Reassign Project Cluster Documents'

    def process(self, **kwargs):
        project_id = kwargs.get('project_id')
        project_clustering_id = kwargs.get('project_clustering_id')
        reassign_cluster_ids = kwargs.get('cluster_ids')
        new_project_id = kwargs.get('new_project_id')
        new_project = Project.objects.get(pk=new_project_id)

        documents = Document.objects.filter(documentcluster__pk__in=reassign_cluster_ids)

        self.set_doc_unique_name_and_project(documents, new_project, new_project.type)

        self.run_if_task_or_sub_tasks_failed(
            ReassignProjectClusterDocuments.rollback,
            (project_clustering_id, project_id, new_project_id, reassign_cluster_ids))

        self.run_sub_tasks(
            'Reassign Each Document from Cluster',
            ReassignProjectClusterDocuments.reassign_document,
            list(documents.values_list('pk')))

        self.run_after_sub_tasks_finished(
            'Finalize Reassigning Cluster Documents',
            ReassignProjectClusterDocuments.finalize,
            [(project_clustering_id, new_project_id, reassign_cluster_ids)])
        # TODO: metadata[project_id] in tasks related with reassigned documents

    def set_doc_unique_name_and_project(self,
                                        documents,
                                        new_project: Project,
                                        new_doc_type: DocumentType) -> None:

        def strict_check_unique_name(doc_new_name: str) -> bool:
            from apps.project.api.v1 import UploadSessionViewSet
            return UploadSessionViewSet.can_upload_file(new_project, doc_new_name, 1) is True

        project_doc_names = set(Document.all_objects.filter(
            project_id=new_project.pk).values_list('name', flat=True))
        for doc_id, doc_name in documents.values_list('pk', 'name'):
            new_name = UniqueNameBuilder.make_doc_unique_name(
                doc_name, project_doc_names, strict_check_unique_name)
            if new_name != doc_name:
                Document.all_objects.filter(pk=doc_id).update(name=new_name)
        documents.update(project_id=new_project.pk, document_type=new_doc_type)
        doc_ids = [d.pk for d in documents]
        text_units = TextUnit.objects.filter(document_id__in=doc_ids)
        text_units.update(project_id=new_project.pk)

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=6000,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError),
                 max_retries=3)
    def reassign_document(task, document_id):
        document = Document.objects.get(pk=document_id)
        signals.document_deleted.send(task.__class__, user=None, document=document)
        log = CeleryTaskLogger(task)
        dfvs = field_detection.detect_and_cache_field_values_for_document(
            log=log,
            document=document,
            system_fields_changed=True,
            generic_fields_changed=True,
            task=field_detection.detect_and_cache_field_values_for_document)

        task.log_info(
            f'Detected {len(dfvs)} field values for document ' + f'#{document.id} ({document.name})')

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=6000,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError),
                 max_retries=3)
    def rollback(task, project_clustering_id, project_id, new_project_id, reassign_cluster_ids):
        """
        Undo reassigning, update ProjectClustering.metadata
        """
        task.log_error('Rollback Reassigning Document Cluster documents.')
        log = CeleryTaskLogger(task)

        p_cl = ProjectClustering.objects.get(id=project_clustering_id)

        # get reassigned documents queryset
        documents = Document.objects.filter(documentcluster__pk__in=reassign_cluster_ids)

        # update rawdb cache for target doc type
        for document in documents:
            signals.document_deleted.send(task.__name__, user=None, document=document)

        # get back Doc Type to Generic Doc Type
        documents.update(project_id=project_id, document_type=DocumentType.generic())

        # update rawdb cache forGeneric Doc Type
        for document in documents:
            signals.document_changed.send(task.__name__, log=log, document=document)

        # update info about reassignings in metadata
        reassignings = p_cl.metadata.get('reassigning', [])
        reassigning = {
            'date': now().isoformat(),
            'new_project_id': new_project_id,
            'cluster_ids': reassign_cluster_ids,
            'status': FAILURE,
        }
        reassignings.append(reassigning)
        p_cl.metadata['reassigning'] = reassignings
        p_cl.save()

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=6000,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError),
                 max_retries=3,
                 priority=9)
    def finalize(self, project_clustering_id, new_project_id, reassign_cluster_ids):
        """
        Update ProjectClustering.metadata:
        - reassigning
        - reassigned_cluster_ids
        - clusters_data
        - points_data
        (cluster_obj_ids remains the same to track initial clusters history)
        """
        p_cl = ProjectClustering.objects.get(pk=project_clustering_id)

        # get reassigned documents queryset
        documents = Document.objects.filter(documentcluster__pk__in=reassign_cluster_ids)

        # set info about reassigning into metadata
        reassignings = p_cl.metadata.get('reassigning', [])
        reassigning = {
            'date': now().isoformat(),
            'new_project_id': new_project_id,
            'cluster_ids': reassign_cluster_ids,
            'status': SUCCESS
        }
        reassignings.append(reassigning)
        p_cl.metadata['reassigning'] = reassignings
        reassigned_cluster_ids = list(set(
            p_cl.metadata.get('reassigned_cluster_ids', []) + reassign_cluster_ids))
        p_cl.metadata['reassigned_cluster_ids'] = reassigned_cluster_ids

        # remove reassigned clusters from metadata
        p_cl.metadata['clusters_data'] = {i: j for i, j in p_cl.metadata['clusters_data'].items()
                                          if j['cluster_obj_id'] not in reassigned_cluster_ids}

        # remove reassigned documents points from metadata
        reassigned_document_ids = documents.values_list('pk', flat=True)
        p_cl.metadata['points_data'] = [i for i in p_cl.metadata['points_data']
                                        if int(i['document_id']) not in reassigned_document_ids]
        p_cl.save()


class CleanProject(ExtendedTask):
    """
    Cleanup Project - remove unassigned docs, sessions, clusters, etc.
    Only for "Multiple Contract Type"
    """
    name = 'Clean Project'
    document_chunk_size = 100

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.document_repository = kwargs['repository'] \
            if 'repository' in kwargs \
            else DocumentRepository()  # type:BaseDocumentRepository

    def process(self, **kwargs):
        project_id = kwargs.get('_project_id')
        delete = bool(kwargs.get('delete'))
        safe_delete = kwargs.get('safe_delete')
        if safe_delete is None:
            safe_delete = True
        project = Project.all_objects.get(pk=project_id)

        # get doc ids and remove docs' source files
        proj_doc_ids = self.document_repository.get_project_document_ids(project_id)
        file_paths = self.document_repository.get_all_document_source_paths(proj_doc_ids)
        try:
            from apps.document.sync_tasks.document_files_cleaner import DocumentFilesCleaner
            DocumentFilesCleaner.delete_document_files(file_paths)
        except Exception as e:
            self.log_error(f'Unable to clean document files: {file_paths}', exc_info=e)

        # delete documents
        from apps.document.repository.document_bulk_delete \
            import get_document_bulk_delete

        doc_bulk_delete = get_document_bulk_delete(safe_delete, user=self.task.user)
        proj_doc_count = len(proj_doc_ids)
        for start_pos in range(0, len(proj_doc_ids), self.document_chunk_size):
            end_pos = min([proj_doc_count, start_pos + self.document_chunk_size])
            doc_bulk_delete.delete_documents(proj_doc_ids[start_pos:end_pos])
            self.log_info('Deleted {}-{} documents from total {} from project #{}'.format(
                start_pos, end_pos, proj_doc_count, project_id
            ))

        # delete project itself
        project.cleanup(delete=delete)
        self.log_info('Cleaned up project #{} itself'.format(project_id))

        # store data about cleanup in ProjectCleanup Task
        if not kwargs.get('skip_task_updating'):
            task_model = self.task
            task_model.metadata = {
                'task_name': 'clean-project',
                '_project_id': project_id  # added "_" to avoid detecting task as project task
            }
            task_model.save()


class CleanProjects(ExtendedTask):
    """
    Run Cleanup Project for all the projects, passed by ids in arguments
    """
    name = 'Clean Projects'

    def process(self, **kwargs):
        project_ids = kwargs.get('_project_ids')
        delete = bool(kwargs.get('delete'))
        safe_delete = bool(kwargs.get('safe_delete'))

        clean_args = [{'_project_id': i,
                       'delete': delete,
                       'safe_delete': safe_delete} for i in project_ids]

        self.run_sub_tasks_class_based('Clean Project',
                                       CleanProject,
                                       clean_args)


class CancelUpload(ExtendedTask):
    """
    Cancel Upload Session - remove session, remove uploaded files, Documents, Tasks, reindex.
    """
    name = 'Cancel Upload'
    priority = 9

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.track_start = None  # type: Optional[datetime.datetime]

    def process(self, **kwargs):
        session_id = kwargs['session_id']
        session = UploadSession.objects.get(pk=session_id)

        # 1. Purge Tasks
        self.track_timelog('')
        session_tasks = Task.objects.main_tasks().filter(upload_session_id=session_id)
        if self.task and self.task.upload_session_id:
            session_tasks = session_tasks.exclude(pk=self.task.pk)
        self.log_info(f'Purge {session_tasks.count()} session tasks.')
        for a_task in session_tasks:
            try:
                # celery_task = AsyncResult(a_task.pk)
                # revoke_task(celery_task)
                purge_task(a_task.id, log_func=self.log_info)
            except:
                # case when task is already deleted as subtask
                pass
        self.track_timelog('1 - purge tasks')

        # 2. Remove Documents+
        document_ids = \
            list(Document.objects.filter(upload_session_id=session_id).values_list('pk', flat=True))
        self.log_info(f'Remove {len(document_ids)} documents')
        from apps.document.repository.document_bulk_delete import get_document_bulk_delete

        # TODO: WHY it fails with
        # psycopg2.errors.ForeignKeyViolation: update or delete
        # on table "document_textunit" violates foreign key constraint
        attempts = 3
        delay = 60
        attempts_made = 0
        delete_manager = get_document_bulk_delete(user=self.task.user)
        error_logged = False

        for attempt in range(1, attempts + 1):
            attempts_made += 1
            try:
                delete_manager.delete_documents(document_ids)
                break
            except Exception as e:
                if not error_logged:
                    self.log_error('Error while deleting documents', exc_info=e)
                    error_logged = True
                self.log_info(f'Attempt #{attempt} of {attempts} to delete documents failed, retry')

                time.sleep(delay)
        self.track_timelog(f'2 - bulk delete for {len(document_ids)} documents')
        if attempts_made > 1:
            self.log_error(f'{attempts_made} of {attempts} tried to delete documents')

        # 3. Remove files
        file_storage_exists = file_storage.document_exists(session_id)
        self.log_info(f'File Storage exists: {file_storage_exists}')

        files_removed, failed_removing = (0, 0)
        if file_storage_exists:
            files = file_storage.list_documents(session_id)
            self.log_info(f'Remove {len(files)} files from File Storage.')
            for file_path in files:
                file_storage.delete_document(file_path)
            try:
                file_storage.delete_document(session_id)
                files_removed += 1
            except:
                # TODO: removing folders through LocalStorage is not implemented
                failed_removing += 1

        self.track_timelog(f'3 - remove files ({files_removed} removed, {failed_removing} failed)')

        # 4. Remove Upload Session
        if not session:
            raise Exception(f"Couldn't find session by id ({session_id})")

        self.log_info(f'Send WS notification that session uid="{session_id}" is cancelled.')
        notify_cancelled_upload_session(session, kwargs.get('user_id'), document_ids)

        self.log_info(f'Remove session uid="{session_id}".')
        Task.objects.filter(upload_session_id=session_id).update(upload_session=None)
        session.delete()
        self.track_timelog('4 - delete session')

    def track_timelog(self, msg: str):
        now_time = datetime.datetime.now()
        if not msg:
            self.track_start = now_time
            return
        delta = now_time - self.track_start
        self.write_log(f'{msg}: {delta}')
        self.track_start = now_time


@app.task(name=task_names.TASK_NAME_TRACK_SESSION_COMPLETED, bind=True)
def track_session_completed(_celery_task):
    """
    Filter sessions where users were notified that upload job started
    i.e. a user set "send email notifications" flag,
    filter sessions where users were not notified that a session job is completed and
    check that upload job is completed,
    send notification email.

    Track uncompleted session and send WS notification.
    """
    TaskUtils.prepare_task_execution()

    sessions_for_ws_notification = list(UploadSession.objects.exclude(completed=True))

    if sessions_for_ws_notification:
        for session in sessions_for_ws_notification:
            session.check_and_set_completed()
        notify_active_upload_sessions(sessions_for_ws_notification)

    from apps.project.api.v1 import ProjectViewSet
    for session in UploadSession.objects.filter(pk__in=[i.pk for i in sessions_for_ws_notification],
                                                completed=True,
                                                project__type__code=DocumentType.GENERIC_TYPE_CODE):
        ProjectViewSet._cluster(project=session.project, user_id=session.created_by.id)
        # TODO: move it in "cluster" task? Or better just count a try? Either use API ProjectViewSet.cluster
        Action.objects.create(
            user_id=session.created_by.id,
            name='Cluster Project',
            message='Cluster Project with default parameters',
            view_action='cluster',
            object_pk=session.project.pk,
            content_type=ContentType.objects.get_for_model(Project),
            model_name='Project',
            app_label='project')

    for session in UploadSession.objects.filter(
            notified_upload_started=True,
            notified_upload_completed=False):
        if session.check_and_set_completed():
            session.notify_upload_completed()


class LoadArchive(ExtendedTask):
    """
    Load Documents from archive
    """
    name = 'Load Archive'
    session_id = source_path = force = user_id = None

    soft_time_limit = 6000
    default_retry_delay = 10
    retry_backoff = True
    autoretry_for = (SoftTimeLimitExceeded, InterfaceError, OperationalError)
    max_retries = 3

    def process(self, **kwargs):
        self.session_id = kwargs.get('session_id')
        self.source_path = kwargs.get('source_path')
        self.force = kwargs.get('force')
        self.user_id = kwargs.get('user_id')
        self.directory_path = kwargs.get('directory_path')
        archive_type = kwargs.get('archive_type')

        self.task.metadata.update({
            'session_id': self.session_id,
            'file_name': os.path.basename(self.source_path),
            'progress': [],
            'progress_sent': False
        })
        self.task.save(update_fields={'metadata'})

        if archive_type == 'zip':
            return self.process_zip()

        if archive_type == 'tar':
            return self.process_tar()

        # else fail silently - it should be caught in API view

        self.log_info('Remove processed archive {}'.format(self.source_path))
        file_storage.delete_document(self.source_path)

    @staticmethod
    def get_mime_type(file_name):
        mime_type, _ = mimetypes.guess_type(file_name)
        if mime_type is None:
            mime_type = 'application/text'
        return mime_type

    def upload_file(self, **kwargs):
        from apps.project.api.v1 import UploadSessionViewSet
        request = HttpRequest()
        request.user = User.objects.get(pk=self.user_id)
        api_view = UploadSessionViewSet(
            request=request, action='upload', kwargs={'pk': self.session_id})
        kwargs.update({'user_id': self.user_id, 'force': self.force})
        resp = api_view.upload_file(**kwargs)
        self.task.metadata['progress'].append(
            dict(
                file_name=kwargs.get('file_name'),
                directory_path=kwargs.get('directory_path'),
                response_status_code=resp.status_code,
                response_data=resp.data['status'] if isinstance(resp.data, dict) and 'status' in resp.data
                else resp.data
            )
        )
        self.task.save(update_fields={'metadata'})

    def process_zip(self):
        with file_storage.get_document_as_local_fn(self.source_path) as (local_file_path, _):
            with zipfile.ZipFile(local_file_path) as zip_file:
                zip_file_filelist = [i for i in zip_file.filelist if not i.is_dir()]

                self.log_info('Start extracting {} documents from {}'.format(
                    len(zip_file_filelist), local_file_path))

                for n, a_file in enumerate(zip_file_filelist):
                    file_size = a_file.file_size
                    file_name = os.path.basename(a_file.filename)
                    file_rel_path = os.path.dirname(a_file.filename)
                    mime_type = self.get_mime_type(file_name)
                    if file_rel_path:
                        directory_path = os.path.join(self.directory_path or '', file_rel_path)
                    else:
                        directory_path = self.directory_path

                    self.log_info(
                        'Extract/start LoadDocument for {} of {} files: name={}, size={}, mime_type={}'.format(
                            n + 1, len(zip_file_filelist), file_name, file_size, mime_type))

                    with TemporaryUploadedFile(file_name, mime_type, file_size, 'utf-8') as tempfile:
                        tempfile.file = zip_file.open(a_file)
                        tempfile.file.seek = lambda *args: 0

                        self.upload_file(
                            file_name=file_name,
                            file_size=file_size,
                            contents=tempfile,
                            directory_path=directory_path)

    def process_tar(self):
        with file_storage.get_document_as_local_fn(self.source_path) as (local_file_path, _):
            with tarfile.open(local_file_path) as tar_file:
                tar_file_members = [i for i in tar_file.getmembers() if not i.isdir()]

                self.log_info('Start extracting {} documents from {}'.format(
                    len(tar_file_members), local_file_path))

                for n, a_file in enumerate(tar_file_members):
                    file_size = a_file.size
                    file_name = os.path.basename(a_file.name)
                    mime_type = self.get_mime_type(file_name)
                    file_rel_path = os.path.dirname(a_file.name)
                    if file_rel_path:
                        directory_path = os.path.join(self.directory_path or '', file_rel_path)
                    else:
                        directory_path = self.directory_path

                    self.log_info(
                        'Extract/start LoadDocument for {} of {} files: name={}, size={}, mime_type={}'.format(
                            n + 1, len(tar_file_members), file_name, file_size, mime_type))

                    with TemporaryUploadedFile(file_name, mime_type, file_size, 'utf-8') as tempfile:
                        tempfile.file = tar_file.extractfile(a_file)

                        self.upload_file(
                            file_name=file_name,
                            file_size=file_size,
                            contents=tempfile,
                            directory_path=directory_path)


class SetAnnotationsStatus(ExtendedTask):
    """
    Load Documents from archive
    """
    name = task_names.TASK_NAME_SET_ANNOTATIONS_STATUS

    soft_time_limit = 6000
    default_retry_delay = 10
    retry_backoff = True
    autoretry_for = (SoftTimeLimitExceeded, InterfaceError, OperationalError)
    max_retries = 3

    def process(self, **kwargs):
        ant_uids = kwargs.get('ids')
        status_id = kwargs.get('status_id')

        # for preventing "connection already closed"
        TaskUtils.prepare_task_execution()
        ann_status = FieldAnnotationStatus.objects.get(pk=status_id)
        user = User.objects.get(pk=kwargs.get('user_id'))

        true_annotations = FieldAnnotation.objects.filter(uid__in=ant_uids)
        false_annotations = FieldAnnotationFalseMatch.objects.filter(uid__in=ant_uids)

        if ann_status.is_rejected:
            from apps.document.repository.document_field_repository import DocumentFieldRepository
            field_repo = DocumentFieldRepository()
            for ant in true_annotations:
                field_repo.delete_field_annotation_and_update_field_value(ant, user)
        else:
            import apps.document.repository.document_field_repository as dfr
            field_repo = dfr.DocumentFieldRepository()
            field_repo.update_field_annotations_by_ant_ids(
                ant_uids, [(f'{FIELD_CODE_STATUS_ID}', status_id)])

            if false_annotations:
                for false_ant in false_annotations:
                    field_repo.restore_field_annotation_and_update_field_value(
                        false_ant, status_id, user)

        ant_docs = set(FieldAnnotation.objects.filter(
            uid__in=ant_uids).values_list('document_id', flat=True))
        false_ant_docs = set(FieldAnnotationFalseMatch.objects.filter(
            uid__in=ant_uids).values_list('document_id', flat=True))
        ant_docs.update(false_ant_docs)
        Document.reset_status_from_annotations(ann_status=ann_status,
                                               document_ids=list(ant_docs))


class UpdateProjectDocumentsFields(ExtendedTask):
    """
    Mass Update fields in project documents
    """
    name = 'Update Project Documents Fields'

    soft_time_limit = 6000
    default_retry_delay = 10
    retry_backoff = True
    autoretry_for = (SoftTimeLimitExceeded, InterfaceError, OperationalError)
    max_retries = 3

    def process(self, **kwargs):
        project_id = kwargs.get('project_id')
        document_ids = kwargs.get('document_ids')
        fields_data = kwargs.get('fields_data')
        on_existing_value = kwargs.get('on_existing_value', 'replace_all')

        self.log_info(f'Update fields in {len(document_ids)} documents in project #{project_id}')

        from apps.document.repository.document_field_repository import DocumentFieldRepository
        from apps.document.tasks import DetectFieldValues

        field_repo = DocumentFieldRepository()
        documents = list(Document.objects.filter(id__in=document_ids).only('pk'))
        fields = set()
        subtask_args = []

        for document in documents:
            _fields = [f.code for f, _ in
                       field_repo.update_field_values(document, self.task.user, fields_data, on_existing_value)]
            fields.update(_fields)
            data = {'document_id': document.pk,
                    'do_not_write': False,
                    'updated_field_codes': _fields}
            subtask_args.append((data,))

        self.log_info(f'Cache and update field values for fields [{fields}]')

        self.run_sub_tasks('Detect Field Values',
                           DetectFieldValues.detect_field_values_for_document,
                           subtask_args)

        self.run_after_sub_tasks_finished(
            'Notify update project documents fields completed',
            UpdateProjectDocumentsFields.notify_task_completed,
            [(self.task.pk, project_id, document_ids, list(fields))])

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=6000,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3,
                 priority=9)
    def convert(task: ExtendedTask,
                document_id: int,
                file_name: str,
                file_path: str):
        with file_storage.get_document_as_local_fn(file_path) as (local_file_path, _):
            from apps.task.tasks import LoadDocuments
            task.log_info(f'Convert PDF to PDF-A, document id={document_id}, file_name={file_name}')
            document: Document = Document.objects.get(id=document_id)
            alt_source_path = LoadDocuments.convert_pdf2pdfa(task=task,
                                                             local_file_path=local_file_path,
                                                             source_path=file_path,
                                                             project_id=document.project.id,
                                                             fail_silently=False,
                                                             force=True)
            if alt_source_path:
                document.alt_source_path = alt_source_path
                document.save()

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=6000,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3,
                 priority=9)
    def notify_task_completed(task: ExtendedTask,
                              task_id,
                              project_id: int,
                              document_ids: List[int],
                              fields: List[str]):
        notify_update_project_document_fields_completed(
            task_id, project_id, document_ids, fields)


app.register_task(ClusterProjectDocuments())
app.register_task(ReassignProjectClusterDocuments())
app.register_task(CleanProject())
app.register_task(CleanProjects())
app.register_task(CancelUpload())
app.register_task(LoadArchive())
app.register_task(SetAnnotationsStatus())
app.register_task(UpdateProjectDocumentsFields())
