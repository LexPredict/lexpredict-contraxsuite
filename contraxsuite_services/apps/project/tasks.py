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
# Third-party imports
from typing import Optional, Set, Callable, Dict, Any

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from celery.states import FAILURE, PENDING, SUCCESS
# Django imports
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.db.models import Q
from django.http import HttpRequest
from django.utils.timezone import now
from psycopg2 import InterfaceError, OperationalError

# Project imports
import task_names
from apps.analyze.ml.cluster import ClusterDocuments
from apps.analyze.ml.features import EmptyDataSetError
from apps.celery import app
from apps.common.file_storage import get_file_storage
from apps.document import signals
from apps.document.constants import DocumentGenericField
from apps.document.field_detection import field_detection
from apps.document.models import Document, DocumentType
from apps.document.repository.base_document_repository import BaseDocumentRepository
from apps.document.repository.document_repository import DocumentRepository
from apps.project.models import Project, ProjectClustering, UploadSession
from apps.project.notifications import notify_active_upload_sessions, notify_cancelled_upload_session
from apps.task.tasks import BaseTask, CeleryTaskLogger, Task, purge_task, _call_task_func, ExtendedTask
from apps.task.utils.task_utils import TaskUtils
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


THIS_MODULE = __name__
file_storage = get_file_storage()


class ClusterProjectDocuments(BaseTask):
    """
    Cluster Project Documents
    """
    name = 'Cluster Project Documents'

    soft_time_limit = 3 * 3600
    default_retry_delay = 10
    retry_backoff = True
    autoretry_for = (SoftTimeLimitExceeded, InterfaceError, OperationalError)
    max_retries = 3

    queue = 'high_priority'

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


class ReassignProjectClusterDocuments(BaseTask):
    """
    Reassign Project Cluster Documents
    """
    name = 'Reassign Project Cluster Documents'
    reg_name_copy_part = re.compile(r'\scopy\s\d{2,2}$')

    def process(self, **kwargs):
        project_id = kwargs.get('project_id')
        project_clustering_id = kwargs.get('project_clustering_id')
        reassign_cluster_ids = kwargs.get('cluster_ids')
        new_project_id = kwargs.get('new_project_id')
        new_project = Project.objects.get(pk=new_project_id)

        p_cl = ProjectClustering.objects.get(id=project_clustering_id)

        documents = Document.objects.filter(documentcluster__pk__in=reassign_cluster_ids)
        # if reassign unclustered
        if 0 in reassign_cluster_ids:
            documents = Document.objects.filter(Q(documentcluster__pk__in=reassign_cluster_ids) |
                                                Q(id__in=p_cl.metadata['unclustered_item_ids']))

        self.ensure_document_unique_names(documents, new_project, new_project.type)

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

    def ensure_document_unique_names(self,
                                     documents,
                                     new_project: Project,
                                     new_doc_type: DocumentType) -> None:

        def strict_check_unique_name(doc_new_name: str) -> bool:
            from apps.project.api.v1 import UploadSessionViewSet
            return UploadSessionViewSet.can_upload_file(new_project,
                                                        doc_new_name, 1) is True

        project_doc_names = set(Document.all_objects.filter(
            project_id=new_project.pk).values_list('name', flat=True))
        for doc_id, doc_name in documents.values_list('pk', 'name'):
            new_name = self.make_doc_unique_name(
                doc_name, project_doc_names, strict_check_unique_name)
            if new_name != doc_name:
                Document.all_objects.filter(pk=doc_id).update(name=new_name)
        documents.update(project_id=new_project.pk, document_type=new_doc_type)

    @staticmethod
    def make_doc_unique_name(doc_name: str,
                             project_doc_names: Set[str],
                             unique_strict_check: Optional[Callable[[str], bool]] = None):

        def new_name_is_unique(new_name: str) -> bool:
            if new_name in project_doc_names:
                return False
            if unique_strict_check and not unique_strict_check(new_name):
                return False
            return True

        if new_name_is_unique(doc_name):
            return doc_name

        # make document a unique name
        name, ext = os.path.splitext(doc_name)
        # ... try filename w/o " copy 01"
        name = ReassignProjectClusterDocuments.reg_name_copy_part.sub('', name)
        new_name = name + ext
        counter = 1
        while not new_name_is_unique(new_name):
            new_name = f'{name} copy {counter:02d}{ext}'
            counter += 1
        return new_name

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
            generic_fields_changed=True)

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
        # if reassign unclustered
        if 0 in reassign_cluster_ids:
            documents = Document.objects.filter(Q(documentcluster__pk__in=reassign_cluster_ids) |
                                                Q(id__in=p_cl.metadata['unclustered_item_ids']))

        # update rawdb cache for target doc type
        for document in documents:
            signals.document_deleted.send(task.__name__, user=None, document=document)

        # get back Doc Type to Generic Doc Type
        documents.update(project_id=project_id, document_type=DocumentType.generic())

        # update rawdb cache forGeneric Doc Type
        for document in documents:
            signals.document_changed.send(task.__name__, log=log, document=document)

        # if reassign unclustered - update info about unclustered documents
        if 0 in reassign_cluster_ids:
            unclustered_documents = Document.objects.filter(project_id=project_id, documentcluster=None)
            p_cl.metadata['unclustered_item_ids'] = list(unclustered_documents.values_list('pk', flat=True))
            p_cl.metadata['unclustered_item_names'] = list(unclustered_documents.values_list('name', flat=True))

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
        - unclustered_item_ids
        - unclustered_item_names
        (cluster_obj_ids remains the same to track initial clusters history)
        """
        p_cl = ProjectClustering.objects.get(pk=project_clustering_id)

        # get reassigned documents queryset
        documents = Document.objects.filter(documentcluster__pk__in=reassign_cluster_ids)
        # if reassign unclustered
        if 0 in reassign_cluster_ids:
            documents = Document.objects.filter(Q(documentcluster__pk__in=reassign_cluster_ids) |
                                                Q(id__in=p_cl.metadata['unclustered_item_ids']))

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
        # if reassign unclustered
        if 0 in reassign_cluster_ids:
            p_cl.metadata['unclustered_item_ids'] = []
            p_cl.metadata['unclustered_item_names'] = []
        p_cl.save()


class CleanProject(BaseTask):
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

        doc_bulk_delete = get_document_bulk_delete(safe_delete)
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


class CleanProjects(BaseTask):
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


class CancelUpload(BaseTask):
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
        session_tasks = Task.objects.main_tasks().filter(metadata__session_id=session_id)
        self.log_info(f'Purge {session_tasks.count()} session tasks.')
        for a_task in session_tasks:
            try:
                purge_task(a_task.id, log_func=lambda m: self.log_info(m))
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
        delete_manager = get_document_bulk_delete()
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
        notify_cancelled_upload_session(session, kwargs.get('user_id'))

        self.log_info(f'Remove session uid="{session_id}".')
        project = session.project
        session.delete()
        self.track_timelog('4 - delete session')

        # 5. Reindex Project
        self.log_info(f'Reindex project id="{project.id}" documents.')
        from apps.rawdb.tasks import reindex_all_project_documents
        _call_task_func(reindex_all_project_documents, (project.pk,), None)
        self.track_timelog('5 - reindex project')

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

    for session in UploadSession.objects.filter(
            notified_upload_started=True,
            notified_upload_completed=False):
        if session.check_and_set_completed():
            session.notify_upload_completed()


class LoadArchive(BaseTask):
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

        if archive_type == 'zip':
            return self.process_zip()

        elif archive_type == 'tar':
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
        api_view = UploadSessionViewSet(request=request, kwargs={'pk': self.session_id})
        kwargs.update({'user_id': self.user_id, 'force': self.force})
        api_view.upload_file(**kwargs)

    def process_zip(self):
        with file_storage.get_document_as_local_fn(self.source_path) as (local_file_path, _):
            with zipfile.ZipFile(local_file_path) as zip_file:
                zip_file_filelist = zip_file.filelist

                self.log_info('Start extracting {} documents from {}'.format(
                    len(zip_file_filelist), local_file_path))

                for n, a_file in enumerate(zip_file_filelist):
                    if a_file.is_dir():
                        continue
                    file_size = a_file.file_size
                    file_name = os.path.basename(a_file.filename)
                    mime_type = self.get_mime_type(file_name)

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
                            directory_path=self.directory_path)

    def process_tar(self):
        with file_storage.get_document_as_local_fn(self.source_path) as (local_file_path, _):
            with tarfile.TarFile(local_file_path) as tar_file:
                tar_file_members = tar_file.getmembers()

                self.log_info('Start extracting {} documents from {}'.format(
                    len(tar_file_members), local_file_path))

                for n, a_file in enumerate(tar_file_members):
                    if a_file.isdir():
                        continue
                    file_size = a_file.size
                    file_name = os.path.basename(a_file.name)
                    mime_type = self.get_mime_type(file_name)

                    self.log_info(
                        'Extract/start LoadDocument for {} of {} files: name={}, size={}, mime_type={}'.format(
                            n + 1, len(tar_file_members), file_name, file_size, mime_type))

                    with TemporaryUploadedFile(file_name, mime_type, file_size, 'utf-8') as tempfile:
                        tempfile.file = tar_file.extractfile(a_file)

                        self.upload_file(
                            file_name=file_name,
                            file_size=file_size,
                            contents=tempfile,
                            directory_path=self.directory_path)


app.register_task(ClusterProjectDocuments())
app.register_task(ReassignProjectClusterDocuments())
app.register_task(CleanProject())
app.register_task(CleanProjects())
app.register_task(CancelUpload())
app.register_task(LoadArchive())
