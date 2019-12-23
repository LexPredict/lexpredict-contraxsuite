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
import json
import mimetypes
import os
import tarfile
import zipfile
from typing import BinaryIO, Union

import rest_framework.views
from celery.states import PENDING, SUCCESS
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.db import connection, transaction
from django.db.models import Count, Subquery
from django.http import JsonResponse, HttpRequest
from django.urls import path, include
# Third-party imports
from rest_framework import serializers, routers, viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response

# Project imports
import apps.common.mixins
from apps.analyze.models import DocumentCluster
from apps.common.file_storage import get_file_storage
from apps.common.log_utils import render_error
from apps.common.models import ReviewStatus
from apps.common.url_utils import as_bool
from apps.common.utils import get_api_module
from apps.common.utils import safe_to_int
from apps.document.app_vars import MAX_ARCHIVE_SIZE, MAX_DOCUMENT_SIZE, FORCE_REWRITE_DOC
from apps.document.constants import DOCUMENT_TYPE_PK_GENERIC_DOCUMENT
from apps.document.models import Document, DocumentType, DocumentField
from apps.document.tasks import plan_process_documents_status_changed, \
    plan_process_documents_assignee_changed
from apps.project.models import Project, TaskQueue, UploadSession, ProjectClustering
from apps.project.tasks import ReassignProjectClusterDocuments, ClusterProjectDocuments, \
    CleanProject, CancelUpload, LoadArchive
from apps.task.models import Task
from apps.task.tasks import call_task, purge_task, LoadDocuments
from apps.task.utils.logger import get_django_logger
from apps.users.models import User

# Django imports

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


common_api_module = get_api_module('common')
users_api_module = get_api_module('users')
ALREADY_EXISTS = 'Already exists'


class PatchedListView(rest_framework.views.APIView):
    def get(self, request, *args, **kwargs):
        data = self.get_json_data(**kwargs)
        return JsonResponse(data, safe=False)


# --------------------------------------------------------
# Task Queue Views
# --------------------------------------------------------


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['pk', 'name', 'description', 'document_type']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'username', 'role']


class TaskQueueSerializer(serializers.ModelSerializer):
    documents = serializers.PrimaryKeyRelatedField(
        queryset=Document.objects.all(), many=True, required=False)
    documents_data = DocumentSerializer(
        source='documents', many=True, read_only=True)
    completed_documents = serializers.PrimaryKeyRelatedField(
        queryset=Document.objects.all(), many=True, required=False)
    completed_documents_data = DocumentSerializer(
        source='completed_documents', many=True, read_only=True)
    reviewers = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False)
    reviewers_data = UserSerializer(
        source='reviewers', many=True, read_only=True)
    progress = serializers.SerializerMethodField()
    data = serializers.SerializerMethodField()

    class Meta:
        model = TaskQueue
        fields = ['pk', 'description',
                  'documents', 'documents_data',
                  'completed_documents', 'completed_documents_data',
                  'reviewers', 'reviewers_data', 'progress', 'data']

    def get_progress(self, obj):
        return obj.progress(as_dict=True)

    def get_data(self, obj):
        data = {}
        request_data = self.context['request'].GET
        only_completed = request_data.get('only_completed')
        only_assigned = request_data.get('only_assigned')
        with_documents = request_data.get('with_documents')
        document_pk = request_data.get('document_id')

        completed = obj.completed
        if (only_completed and not completed) or \
                (only_assigned and completed):
            return []
        if document_pk:
            complete_history = obj.document_complete_history(document_pk)
            if complete_history:
                data['complete_date'] = complete_history.date
                data['complete_user'] = complete_history.user.username
        elif with_documents:
            documents = []
            for num, document in enumerate(obj.complete_history):
                document_data = dict(
                    pk=obj.pk,
                    num=num + 1,
                    name=document.name,
                    description=document.description,
                    type=document.document_type,
                    complete_date=None,
                    complete_user=None,
                )
                if document.complete_history:
                    document_data.update(dict(
                        complete_date=document.complete_history.date,
                        complete_user=document.complete_history.user.username))
                documents.append(document_data)
            data['documents'] = documents
        return data

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        request_data = self.context['request'].data

        # add/remove document
        add_document = request_data.get('add_document')
        if add_document:
            instance.documents.add(add_document)
        remove_document = request_data.get('remove_document')
        if remove_document:
            instance.documents.remove(remove_document)

        # mark document completed / reopen document
        complete_document = request_data.get('complete_document')
        if complete_document:
            instance.completed_documents.add(complete_document)
        open_document = request_data.get('open_document')
        if open_document:
            instance.completed_documents.remove(open_document)

        # add cluster document to a TaskQueue
        cluster_id = request_data.get('add_documents_from_cluster')
        if cluster_id:
            cluster_doc_ids = DocumentCluster.objects \
                .get(pk=cluster_id) \
                .documents \
                .values_list('pk', flat=True)
            instance.documents.add(*cluster_doc_ids)

        return instance


class TaskQueueViewSet(apps.common.mixins.JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: Task Queue List
    retrieve: Retrieve Task Queue
    create: Create Task Queue
    update: Update Task Queue\n
        PUT params:
            - pk: int
            - description: str
            - documents: list[int]
            - completed_documents: list[int]
            - reviewers: list[int]
        Optional params for add/remove document from/to a TaskQueue:
            - add_document: int
            - remove_document: int
        Optional params for complete/reopen document in a TaskQueue:
            - complete_document: int
            - open_document: int
        Optional param to add documents from DocumentCluster:
            - add_documents_from_cluster: int (cluster id)
    partial_update: Partial Update Task Queue
    delete: Delete Task Queue
    """
    queryset = TaskQueue.objects.all()
    serializer_class = TaskQueueSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_reviewer:
            qs = qs.filter(reviewers=self.request.user)
        return qs


# --------------------------------------------------------
# Project Views
# --------------------------------------------------------

def project_progress(obj):
    if not hasattr(obj, 'project_current_documents_count'):
        obj.project_current_documents_count = obj.document_set.count()
    if not hasattr(obj, 'project_reviewed_documents_count'):
        obj.project_reviewed_documents_count = obj.document_set.filter(
            status__group__is_active=False).count()

    stats = {
        'project_current_documents_count': obj.project_current_documents_count,
        'project_reviewed_documents_count': obj.project_reviewed_documents_count}

    if obj.type.is_generic():

        if not hasattr(obj, 'project_clusters_count'):
            obj.project_clusters_count = obj.projectclustering_set.last() \
                .document_clusters.count() \
                if obj.projectclustering_set.exists() else 0

        if not hasattr(obj, 'project_clusters_documents_count'):
            obj.project_clusters_documents_count = obj.projectclustering_set.last() \
                .document_clusters.aggregate(c=Count('documents'))['c'] \
                if obj.projectclustering_set.exists() else 0

        stats.update({
            'project_clusters_documents_count': obj.project_clusters_documents_count,
            'project_clusters_count': obj.project_clusters_count,
        })

    return stats


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ['uid', 'code', 'title']


class ProjectDetailSerializer(serializers.ModelSerializer):
    status = serializers.PrimaryKeyRelatedField(
        queryset=ReviewStatus.objects.all(), many=False, required=False)
    status_data = common_api_module.ReviewStatusSerializer(
        source='status', many=False, read_only=True)
    owners = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False)
    owners_data = users_api_module.UserSerializer(
        source='owners', many=True, read_only=True)
    reviewers = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False)
    reviewers_data = users_api_module.UserSerializer(
        source='reviewers', many=True, read_only=True)
    super_reviewers = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False)
    super_reviewers_data = users_api_module.UserSerializer(
        source='super_reviewers', many=True, read_only=True)
    type = serializers.PrimaryKeyRelatedField(
        queryset=DocumentType.objects.all(), many=False, required=False)
    type_data = DocumentTypeSerializer(source='type', many=False)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['pk', 'name', 'description',
                  'send_email_notification',
                  'status', 'status_data',
                  'owners', 'owners_data',
                  'reviewers', 'reviewers_data',
                  'super_reviewers', 'super_reviewers_data',
                  'type', 'type_data', 'progress']

    def get_progress(self, obj):
        return project_progress(obj)


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['pk', 'name', 'description', 'type', 'send_email_notification']


class ProjectUpdateSerializer(ProjectDetailSerializer):
    class Meta(ProjectDetailSerializer.Meta):
        model = Project
        fields = ['pk', 'name', 'description', 'status', 'send_email_notification',
                  'owners', 'reviewers', 'super_reviewers', 'type']


class ProjectListSerializer(ProjectDetailSerializer):
    class Meta:
        model = Project
        fields = ['pk', 'name', 'status', 'status_data', 'type', 'type_data']


class ProjectStatserializer(ProjectDetailSerializer):
    total_documents_count = serializers.SerializerMethodField()
    reviewed_documents_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['pk', 'name', 'status', 'total_documents_count', 'reviewed_documents_count']

    def get_total_documents_count(self, obj):
        return obj.document_set.count()

    def get_reviewed_documents_count(self, obj):
        return obj.document_set.filter(status__group__is_active=False).count()


def require_generic_contract_type(func):
    def decorator(cls, *args, **kwargs):
        project = cls.get_object()
        cls.object = project
        if project.type and not project.type.is_generic():
            raise APIException('Allowed for projects with "Generic Contract Type" only')
        return func(cls, *args, **kwargs)

    decorator.__doc__ = func.__doc__
    return decorator


class ProjectPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_reviewer:
            if request.method == 'GET' or view.action in ['cluster', 'set_status', 'assign_documents']:
                return True
            return False
        return True

    def has_object_permission(self, request, view, obj):
        # Warn! self.get_object() initializes this check! so include it in custom view func!
        if request.user.is_reviewer:
            return obj.reviewers.filter(pk=request.user.pk).exists()
        return True


class ProjectPermissionViewMixin:
    permission_classes = (IsAuthenticated, ProjectPermissions)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_reviewer:
            qs = qs.filter(reviewers=self.request.user)
        return qs


class ProjectViewSet(apps.common.mixins.APILoggingMixin,
                     ProjectPermissionViewMixin,
                     apps.common.mixins.APIActionMixin,
                     apps.common.mixins.JqListAPIMixin,
                     viewsets.ModelViewSet):
    """
    list: Project List
    retrieve: Retrieve Project
    create: Create Project
    update: Update Project
    partial_update: Partial Update Project
    delete: Delete Project
    """

    queryset = Project.objects.all()

    def dispatch(self, request, *args, **kwargs):
        self.initialize_request(request, *args, **kwargs)
        if self.action == 'retrieve':
            request.needs_action_logging = True
        return super().dispatch(request, *args, **kwargs)

    def perform_create(self, serializer):
        project = super().perform_create(serializer)
        project.owners.add(self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return ProjectCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProjectUpdateSerializer
        elif self.action == 'list':
            return ProjectListSerializer
        elif self.action == 'stats':
            return ProjectStatserializer
        return ProjectDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('type').prefetch_related('status')
        if self.action != 'list':
            qs = qs.prefetch_related('owners', 'owners__role',
                                     'super_reviewers', 'super_reviewers__role',
                                     'reviewers', 'reviewers__role')
        return qs

    def get_extra_data(self, queryset):
        return {'available_statuses': common_api_module.ReviewStatusSerializer(
            ReviewStatus.objects.select_related('group'), many=True).data}

    @action(detail=True, methods=['get'])
    def progress(self, request, **kwargs):
        """
        Get current progress of all project sessions / clusterings
        """
        # permissions check
        project = self.get_object()

        project_sessions = project.uploadsession_set

        # renew status for completed=False sessions
        for session in project_sessions.filter(completed=False):
            session.status_check()

        # get completed sessions as bool
        project_has_completed_sessions = project_sessions.filter(completed=True).exists()
        project_uncompleted_sessions = project_sessions.filter(completed=False)

        # get just LAST recent session
        user_uncompleted_session = project_uncompleted_sessions.filter(
            created_by=request.user).order_by('created_date').last()
        other_uncompleted_session = project_uncompleted_sessions.exclude(
            created_by=request.user).order_by('created_date').last()

        # get this user opened sessions progress
        user_uncompleted_session_progress = None
        if user_uncompleted_session:
            session_progress = user_uncompleted_session.document_tasks_progress_total
            if session_progress != 100:
                user_uncompleted_session_progress = {
                    'session_id': user_uncompleted_session.pk,
                    'document_tasks_progress_total': session_progress,
                    'documents_total_size': user_uncompleted_session.documents_total_size}
            else:
                project_has_completed_sessions = True

        # get other users opened sessions progress
        other_uncompleted_session_progress = None
        if other_uncompleted_session:
            session_progress = other_uncompleted_session.document_tasks_progress_total
            if session_progress != 100:
                other_uncompleted_session_progress = {
                    'session_id': other_uncompleted_session.pk,
                    'document_tasks_progress_total': other_uncompleted_session.document_tasks_progress_total,
                    'documents_total_size': other_uncompleted_session.documents_total_size}
            else:
                project_has_completed_sessions = True

        result = dict(
            project_has_completed_sessions=project_has_completed_sessions,
            user_uncompleted_session_progress=user_uncompleted_session_progress,
            other_uncompleted_session_progress=other_uncompleted_session_progress)

        # add info about clustering
        if project.type.is_generic():
            if user_uncompleted_session_progress is not None or other_uncompleted_session_progress is not None:
                clustering = 'WAITING'
            else:
                clustering = self.clustering_status(request).data
                # define if project should be re-clustered
                project_total_documents_count = project.document_set.count()
                project_clusters_documents_count = clustering.get('project_clusters_documents_count', 0)
                require_clustering = project_total_documents_count != project_clusters_documents_count
                result['require_clustering'] = require_clustering
            result['clustering'] = clustering

        return Response(result)

    @require_generic_contract_type
    def cluster(self, request, **kwargs):
        """
        Cluster Project Documents\n
            Params:
                - method: str[KMeans, MiniBatchKMeans, Birch, DBSCAN]
                - n_clusters: int
                - force: bool (optional) - force clustering if uncompleted tasks exist
        """
        project = getattr(self, 'object', None) or self.get_object()

        if not request.data.get('force') == 'true':
            if project.uploadsession_set.filter(completed=False).exists():
                raise APIException('Project has uncompleted upload sessions.')
            elif not project.uploadsession_set.filter(completed=True).exists():
                raise APIException("Project hasn't completed upload sessions.")

        pending_clustering_task_ids = Task.objects \
            .filter(name=ClusterProjectDocuments.name, project=project, status=PENDING)\
            .values_list('pk', flat=True)
        for task_id in pending_clustering_task_ids:
            purge_task(task_id)

        project_clustering = ProjectClustering.objects.create(project=project)

        try:
            n_clusters = int(request.data.get('n_clusters', 3))
        except ValueError:
            n_clusters = 3

        # json data is used when API is activated via swagger either by passing json directly
        if request.content_type == 'application/json':
            cluster_by = request.data.get('cluster_by', ['term'])
        # either use form data from UI
        else:
            cluster_by = request.data.getlist('cluster_by', ['term'])

        task_id = call_task(
            ClusterProjectDocuments,
            user_id=request.user.id,
            project_id=project.id,
            project_clustering_id=project_clustering.id,
            method=request.data.get('method', 'kmeans'),
            metadata={'project_id': project.id},
            cluster_by=cluster_by,
            n_clusters=n_clusters)

        return Response({'task_id': task_id,
                         'project_clustering_id': project_clustering.id})

    @require_generic_contract_type
    def clustering_status(self, request, **kwargs):
        """
        Last Clustering task status/data\n
            Params:
                - project_clustering_id: int (optional) - return last if not provided
        """
        project = getattr(self, 'object', None) or self.get_object()
        project_clustering_id = request.GET.get('project_clustering_id')

        clustering = project.projectclustering_set \
            .select_related('project', 'task') \
            .annotate(project_clusters_documents_count=Count('document_clusters__documents', distinct=True))

        if project_clustering_id:
            clustering = clustering.get(pk=project_clustering_id)
        else:
            clustering = clustering.last()

        if not clustering:
            return Response({'details': 'Cluster session not found'}, status=404)

        data = ProjectClusteringSerializer(clustering).data

        reassigned_cluster_ids = clustering.metadata.get('reassigned_cluster_ids', [])
        reassigning_data = clustering.metadata.get('reassigning')

        for cluster in data['document_clusters']:
            cluster['reassigned'] = False
            cluster['reassigned_to_project_id'] = None

            try:
                if cluster['pk'] in reassigned_cluster_ids:
                    cluster['reassigned'] = True
                    cluster_reassigning_data = [i for i in reassigning_data
                                                if cluster['pk'] in i['cluster_ids']]

                    # In case of previous errors we can have more than one reassigning stored.
                    # This is wrong but the system should continue working.
                    # if len(cluster_reassigning_data) != 1:
                    #    raise APIException('Found more than one reassigning of cluster id={}'
                    #                        .format(cluster['pk']))
                    cluster['reassigned_to_project_id'] = cluster_reassigning_data[0]['new_project_id']

                cluster['cluster_terms'] = data['metadata']['clusters_data'][str(cluster['cluster_id'])][
                    'cluster_terms']

            except KeyError:
                pass

        return Response(data)

    @action(detail=True, methods=['post'], url_path='send-clusters-to-project')
    # @require_generic_contract_type
    def send_clusters_to_project(self, request, **kwargs):
        """
        Send clusters to another Project\n
            Params:
                - cluster_ids: list[int]
                - project_id: int
        """
        project = self.get_object()
        cluster_ids = [int(i) for i in request.POST.getlist('cluster_ids')]
        project_clustering = project.projectclustering_set.last()
        if not project_clustering:
            raise APIException('Project Clustering object not found')
        reassigned_cluster_ids = project_clustering.metadata.get('reassigned_cluster_ids', [])
        already_reassigned_clusters = set(cluster_ids) & set(reassigned_cluster_ids)
        if already_reassigned_clusters:
            raise APIException('Cluster(s) id=({}) is/are already reassigned to another project'
                               .format(', '.join(str(i) for i in already_reassigned_clusters)))

        new_project_id = int(request.POST.get('project_id'))
        call_task(
            ReassignProjectClusterDocuments,
            cluster_ids=cluster_ids,
            project_id=project.id,
            new_project_id=new_project_id,
            user_id=request.user.id)

        return Response('OK')

    @action(detail=True, methods=['post'])
    # @require_generic_contract_type
    def cleanup(self, request, **kwargs):
        """
        Clean project (Generic Contract Type project)
        """
        delete = json.loads(request.data.get('delete', 'true'))

        call_task(
            CleanProject,
            _project_id=int(kwargs['pk']),
            delete=delete,
            user_id=request.user.id)

        return Response('OK')

    @action(detail=True, methods=['post'])
    def mark_delete(self, request, **kwargs):
        """
        Method marks the whole project (remove_all=True) / the project's documents (remove_all=False)
        for deleting. These marked documents (and the project) will become hidden in API.
        Documents, listed in excluded_ids list, will not be marked for deleting.\n
            Params:
                - all: bool - mark all filtered by a user documents
                - remove_all: bool - mark project+documents
                - excluded_ids: list[int]
        """
        return self.mark_unmark_for_delete(True, request, **kwargs)

    @action(detail=True, methods=['post'])
    def unmark_delete(self, request, **kwargs):
        """
        Method removes soft delete sign from project only (remove_all=False) or
        from the project and the project's documents (remove_all=True)
            Body params:
                - all: bool - unmark all filtered by a user documents
                - remove_all: bool - unmark project+documents
                - exclude_document_ids: List[int]
        """
        return self.mark_unmark_for_delete(False, request, **kwargs)

    def mark_unmark_for_delete(self, delete_pending: bool, request, **kwargs) -> Response:
        included_ids = []
        project_id = int(kwargs['pk'])
        remove_filtered_documents = request.data.get('all', False)
        remove_all = request.data.get('remove_all', False)
        excluded_ids = request.data.get('exclude_document_ids', [])

        if remove_filtered_documents or excluded_ids:
            remove_all = False

        if remove_filtered_documents:
            included_ids = self.get_document_queryset().values_list('id', flat=True)

        from apps.document.sync_tasks.soft_delete_document_task import SoftDeleteDocumentsSyncTask
        count_deleted = SoftDeleteDocumentsSyncTask().process(
            document_ids=included_ids,
            excluded_ids=excluded_ids,
            project_id=project_id,
            delete_all_in_project=remove_all,
            delete_not_undelete=delete_pending)
        if remove_all:
            proj = Project.all_objects.get(pk=project_id)  # type: Project
            proj.delete_pending = delete_pending
            proj.save()
        return Response({"count_deleted": count_deleted}, status=200)

    @action(detail=True, methods=['get'])
    def assignees(self, request, **kwargs):
        """
        Get assignees data
        """
        # permissions check
        project = self.get_object()

        result = []
        for user in project.reviewers.all().union(project.owners.all()).distinct():
            docs = project.document_set.filter(assignee=user)
            result.append({
                'assignee_id': user.id,
                'assignee_name': user.get_full_name(),
                'documents_count': docs.count(),
                'document_ids': docs.values_list('pk', flat=True)})
        return Response(result)

    def get_document_queryset(self):
        """
        Re-use DocumentsAPIView and SavedFilter to fetch all filtered project documents
        """
        project = self.get_object()
        user = self.request.user
        from apps.rawdb.api.v1 import DocumentsAPIView
        return DocumentsAPIView.simulate_get(user, project, return_ids=False)

    @action(detail=True, methods=['post'])
    def assign_documents(self, request, **kwargs):
        """
        Bulk assign batch of documents to a review team member\n
            Params:
                document_ids: list[int]
                all: any value - update all documents if any value
                no_document_ids: list[int] - exclude those docs from action (if "all" is set)
                assignee_id: int
            Returns:
                int (number of reassigned documents)
        """
        self.get_object()    # noqa: permissions check
        assignee_id = request.data.get('assignee_id')

        if request.data.get('all'):
            documents = self.get_document_queryset()
            if request.data.get('no_document_ids'):
                documents = documents.exclude(pk__in=request.data.get('no_document_ids'))
            document_ids = documents.values_list('pk', flat=True)
        else:
            document_ids = request.data.get('document_ids')

        plan_process_documents_assignee_changed(doc_ids=document_ids,
                                                new_assignee_id=assignee_id,
                                                changed_by_user_id=request.user.pk)
        return Response({'success': len(document_ids)})

    @action(detail=True, methods=['post'])
    def set_status(self, request, **kwargs):
        """
        Bulk set status for batch of documents\n
            Params:
                document_ids: list[int]
                all: any value - update all documents if any value
                status_id: int
            Returns:
                int (number of reassigned documents)
        """
        # permissions check
        project = self.get_object()
        status_id = request.data.get('status_id')

        if request.data.get('all'):
            documents = self.get_document_queryset()
            if request.data.get('no_document_ids'):
                documents = documents.exclude(pk__in=request.data.get('no_document_ids'))
            document_ids = documents.values_list('pk', flat=True)
        else:
            document_ids = request.data.get('document_ids')

        documents = Document.objects \
            .filter(project=project, pk__in=document_ids)

        import apps.document.repository.document_field_repository as dfr
        field_repo = dfr.DocumentFieldRepository()

        with transaction.atomic():
            is_active = ReviewStatus.objects.get(pk=status_id).is_active
            modified_fields = field_repo.get_modified_field_ids(
                documents, is_active)
            DocumentField.objects.filter(
                pk__in=Subquery(modified_fields)).update(dirty=True)
            ret = documents.update(status=status_id)

        plan_process_documents_status_changed(document_ids, status_id, request.user.pk)

        return Response({'success': ret})

    @action(detail=False, methods=['get'])
    def recent(self, request, **kwargs):
        """
        Get recent N projects\n
            Params:
                n: int - default is 5
        """
        last_n = int(request.GET.get('n', 5))
        content_type_id = ContentType.objects.get_for_model(Project).id
        user_id = request.user.pk

        sql = '''
            SELECT
              p1.id project_id,
              p1.name project_name,
              CASE WHEN p1.type_id = %s THEN TRUE ELSE FALSE END AS is_generic,
              (SELECT count(d1.id)
               FROM document_document d1
               WHERE d1.project_id = p1.id) extracted_doc_count,
              (SELECT count(d2.id)
               FROM document_document d2
               WHERE d2.project_id = p1.id AND
                     d2.status_id IN (SELECT rs.id
                                        FROM common_reviewstatus rs INNER JOIN common_reviewstatusgroup rsg
                                            ON rs.group_id = rsg.id
                                        WHERE rsg.is_active = FALSE)) reviewed_doc_count
            FROM project_project p1
            INNER JOIN common_action ca
                ON NOT p1.delete_pending AND ca.content_type_id = %s AND ca.user_id = %s AND ca.object_pk = p1.id :: VARCHAR
            {}
            GROUP BY p1.id
            ORDER BY max(ca.date) DESC
            LIMIT %s
        '''

        # limit query for reviewers - only if a reviewer is in project user groups
        # (owners, super_reviewers or reviewers)
        reviewer_subquery = '''
            LEFT JOIN project_project_reviewers ppr
                ON p1.id = ppr.project_id
            LEFT JOIN project_project_super_reviewers ppsr
                ON p1.id = ppsr.project_id
            LEFT JOIN project_project_owners ppo
                ON p1.id = ppo.project_id
            WHERE ppr.user_id = {user_id} OR ppsr.user_id = {user_id} OR ppo.user_id = {user_id}
        '''.format(user_id=user_id)
        sql = sql.format(reviewer_subquery if request.user.is_reviewer else '')

        result = list()
        with connection.cursor() as cursor:
            cursor.execute(sql, [DOCUMENT_TYPE_PK_GENERIC_DOCUMENT, content_type_id, user_id, last_n])
            for project_id, project_name, is_generic, extracted_doc_count, reviewed_doc_count in cursor.fetchall():
                result.append({
                    'name': project_name,
                    'pk': project_id,
                    'is_generic': is_generic,
                    'progress': {
                        'project_current_documents_count': extracted_doc_count,
                        'project_reviewed_documents_count': reviewed_doc_count
                    }
                })

        return Response(result)


# --------------------------------------------------------
# UploadSession Views
# --------------------------------------------------------

class UploadSessionSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), many=False, required=False)
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=False, required=False)
    upload_files = serializers.DictField(required=False, read_only=True)

    class Meta:
        model = UploadSession
        fields = ['uid', 'project', 'created_by', 'upload_files']


class UploadSessionDetailSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(many=False)
    project = ProjectDetailSerializer(many=False, required=False)
    document_type = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = UploadSession
        fields = ['uid', 'project', 'created_by', 'created_date', 'document_type', 'progress']

    def get_progress(self, obj):
        return obj.document_tasks_progress(details=True)

    def get_document_type(self, obj):
        return DocumentTypeSerializer(obj.project.type, many=False).data if obj.project else None


class UploadSessionPermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_reviewer:
            if view.action in ['upload', 'batch_upload'] and \
                    not obj.project.super_reviewers.filter(pk=request.user.pk).exists():
                return False
            return obj.project.reviewers.filter(pk=request.user.pk).exists()
        return True


class UploadSessionPermissionViewMixin:
    permission_classes = (IsAuthenticated, UploadSessionPermissions)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_reviewer:
            qs = qs.filter(project__reviewers=self.request.user)
        return qs


class UploadSessionViewSet(UploadSessionPermissionViewMixin,
                           apps.common.mixins.APIActionMixin,
                           apps.common.mixins.JqListAPIMixin,
                           viewsets.ModelViewSet):
    """
    list: Session Upload List
    retrieve: Retrieve Session Upload
    create: Create Session Upload
    update: Update Session Upload
    partial_update: Partial Update Session Upload
    delete: Delete Session Upload
    """
    queryset = UploadSession.objects.all()
    http_method_names = ['get', 'post', 'delete']

    def get_serializer_class(self):
        if self.action == 'create':
            return UploadSessionSerializer
        return UploadSessionDetailSerializer

    @staticmethod
    @transaction.atomic
    def can_upload_file(project: Project, file_name: str, file_size: int):
        """
        Check whether a file is new and should be uploaded
        :param project: Project
        :param file_name: file name
        :param file_size: file size in bytes
        :return: bool
        """
        # 1. if a Document of file name and size already uploaded and parsed
        if Document.objects.filter(
                project=project,
                name=file_name,
                file_size=file_size,
                documentmetadata__metadata__upload_status='DONE').exists():
            return 'exists'

        # 2. if a Document of file name and size already uploaded and parsed BUT soft-deleted
        if Document.all_objects.filter(
                delete_pending=True,
                project=project,
                name=file_name,
                file_size=file_size,
                documentmetadata__metadata__upload_status='DONE').exists():
            return 'delete_pending'

        # 3. if a Document is not created yet or flag 'upload_status="DONE"' is not set yet
        # so parsing is in progress
        # and Task for file name and size exists with appropriate status
        # 3.1. if task has completed at this moment and that's why step#1 was missed
        if Task.objects.main_tasks().filter(
                name=LoadDocuments.name,
                upload_session__project=project,
                metadata__file_name=file_name,
                metadata__file_size=file_size,
                status__in=(PENDING, SUCCESS)).exists():
            return 'processing'

        # 4. VERY RARE: if a file of name and size already exists but LD Task is not created yet
        # but LD Task object itself is created immediately after storing a file
        # So - skipping this check, load: True

        # 5. Other RARE cases:
        #     a) size doesn't match:
        #         - if a Document exists: it's another document, load: True
        #         - elif a Task exists: it's another document, load: True
        #         - else:
        #             = it's another document - load: True
        #             = it's the same document, in storing on disk process - load: False (TODO)
        #             = it's the same document but uploading was interrupted - load: True

        # since we does double check in /upload method, - skip RARE cases for now
        return True

    def create(self, request, *args, **kwargs):
        project = Project.objects.get(pk=request.data.get('project'))
        response = super().create(request, *args, **kwargs)

        upload_files = request.data.pop('upload_files', None)

        if upload_files:

            force_rename = request.data.get('force')
            if force_rename is None:
                force_rename = FORCE_REWRITE_DOC.val

            do_upload_files = dict()
            upload_unique_files = list()
            exists = list()
            delete_pending = list()
            processing = list()

            for file_path, file_size in upload_files.items():
                file_name = os.path.basename(file_path)
                status = self.can_upload_file(project, os.path.basename(file_path), file_size)

                if (force_rename and status != 'delete_pending') or \
                        (status is True and (file_name, file_size) not in upload_unique_files):
                    do_upload_files[file_path] = True
                    upload_unique_files.append((file_name, file_size))
                else:
                    do_upload_files[file_path] = False
                    if status == 'exists':
                        exists.append(file_path)
                    elif status == 'delete_pending':
                        delete_pending.append(file_path)
                    elif status == 'processing':
                        processing.append(file_path)

            data = dict(
                upload_files=do_upload_files,
                exists=exists,
                delete_pending=delete_pending,
                processing=processing
            )
            response.data.update(data)
        return response

    @action(detail=True, methods=['get'])
    def progress(self, request, pk):
        """
        Get Progress for a session per files (short form)
        """
        session = self.get_object()
        session.check_and_set_completed()
        document_tasks_progress = session.document_tasks_progress()
        result = {'project_id': session.project.pk if session.project else None,
                  'document_tasks_progress': document_tasks_progress or None,
                  'document_tasks_progress_total': session.document_tasks_progress_total,
                  'documents_total_size': session.documents_total_size,
                  'session_status': session.status}
        return Response(result)

    @action(detail=False, methods=['get'])
    def status(self, request, **kwargs):
        """
        Get status of Upload Sessions
            Params:
                - project_id: int
        """
        qs = self.queryset
        project_id = request.GET.get('project_id')
        if project_id:
            qs = qs.filter(project_id=project_id)
        result = {i.pk: i.status_check() for i in qs}
        return Response(result)

    @classmethod
    def _notify_upload_started(cls, session: UploadSession) -> None:
        try:
            session.notify_upload_started()
        except Exception as exc:
            get_django_logger().exception(exc)

    def upload_file(self,
                    file_name: str,
                    file_size: int,
                    contents: Union[BinaryIO, HttpRequest],
                    force: bool,
                    user_id: int,
                    directory_path: str) -> Response:
        if file_size > MAX_DOCUMENT_SIZE.val * 1024 * 1024:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=f'File size is greater than allowed max {MAX_DOCUMENT_SIZE.val} Mb')

        try:
            session = self.get_object()
        except (UploadSession.DoesNotExist, ValidationError):
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data='Wrong upload session uid.')

        project = session.project
        force_rename = force or FORCE_REWRITE_DOC.val

        if not force_rename and self.can_upload_file(project, file_name, file_size) is not True:
            # raise APIException('File already uploaded or uploading in progress.')
            return Response(status=201, data='Loaded')

        try:
            stor = get_file_storage()

            source_path = stor.sub_path_join(session.pk, file_name)

            # check file name is unique
            from apps.document.sync_tasks.ensure_new_paths_unique_task import EnsureNewPathsUnique
            en_task = EnsureNewPathsUnique(
                lambda msg: get_django_logger().error(msg))

            try:
                unique = en_task.ensure_new_file_unique(project=project,
                                                        source_path=source_path,
                                                        doc_name=file_name,
                                                        rename_old_document=force_rename)
                if not unique:
                    return Response(status=status.HTTP_409_CONFLICT, data=ALREADY_EXISTS)
            except Exception as e:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                data='Failed to remove files with the same name, original exception is: {}'.format(str(e)))

            try:
                stor.mk_doc_dir(session.pk)
            except:
                # ignore if dir exists
                # ignoring other errors too - it will crash on next step anyways
                pass
            stor.write_document(rel_file_path=source_path, contents_file_like_object=contents, content_length=file_size)

            # Code for running locators and detecting field values has been moved to LoadDocuments task
            # for the unification purposes between old and new ui.

            call_task(
                LoadDocuments,
                source_data=source_path,
                user_id=user_id,
                session_id=session.pk,
                run_standard_locators=True,
                metadata={'session_id': session.pk, 'file_name': file_name, 'file_size': file_size},
                linked_tasks=None,
                directory_path=directory_path)

            if project.send_email_notification \
                    and not session.notified_upload_started:
                self._notify_upload_started(session)

        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            data=render_error('Unable to load file', caused_by=e))

        return Response(status=status.HTTP_201_CREATED, data='Loaded')

    @action(detail=True, methods=['post'])
    def files(self, request: HttpRequest, pk: str):
        file_size = request.headers.get('Content-Length')
        if not file_size:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='Please provide Content-Length header')

        file_name = request.headers.get('File-Name')
        if not file_name:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='Please provide File-Name header')

        return self.upload_file(file_name=file_name,
                                file_size=safe_to_int(file_size),
                                contents=request,
                                user_id=request.user.id,
                                force=as_bool(request.GET, 'force', False))

    def upload_archive(self, request, file_, archive_type):

        if file_.size > MAX_ARCHIVE_SIZE.val * 1024 * 1024:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=f'Archive size is greater than allowed max {MAX_ARCHIVE_SIZE.val} Mb')

        try:
            session = self.get_object()
        except (UploadSession.DoesNotExist, ValidationError):
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data='Wrong upload session uid.')

        stor = get_file_storage()
        try:
            stor.mk_doc_dir(session.pk)
        except:
            # ignore if dir exists
            # ignoring other errors too - it will crash on next step anyways
            pass
        source_path = stor.sub_path_join(session.pk, file_.name)

        try:
            file_.seek(0)
            stor.write_document(source_path, contents_file_like_object=file_,
                                content_length=file_.size)
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            data=render_error('Unable to load file', caused_by=e))

        call_task(
            LoadArchive,
            archive_type=archive_type,
            source_path=source_path,
            user_id=request.user.id,
            session_id=session.pk,
            force=as_bool(request.POST, 'force', False)
        )

        return Response(status=status.HTTP_200_OK, data='Loaded')

    def is_zip(self, file_):
        if zipfile.is_zipfile(file_) and \
                mimetypes.guess_type(file_.name)[0] in settings.ARCHIVES['zip']['allowed_mime_types']:
            ext = os.path.basename(file_.name).split('.', 1)
            if len(ext) == 2 and ext[1] in settings.ARCHIVES['zip']['allowed_extensions']:
                return True
        return False

    def is_tar(self, file_):
        if (hasattr(file_, 'temporary_file_path') and tarfile.is_tarfile(file_.temporary_file_path())) or \
                mimetypes.guess_type(file_.name)[0] in settings.ARCHIVES['tar']['allowed_mime_types']:
            ext = os.path.basename(file_.name).split('.', 1)
            if len(ext) == 2 and ext[1] in settings.ARCHIVES['tar']['allowed_extensions']:
                return True
        return False

    @action(detail=True, methods=['post'])
    def upload(self, request, pk: str):
        """
        Upload a File\n
            Params:
                - file: file object
                - force: bool (optional) - whether rewrite existing file and Document
        """
        file_ = request.FILES.dict().get('file')

        if not file_:
            raise APIException('File not found.')

        if self.is_zip(file_):
            return self.upload_archive(request, file_, archive_type='zip')
        if self.is_tar(file_):
            return self.upload_archive(request, file_, archive_type='tar')
        file_.seek(0)

        resp = self.upload_file(file_name=file_.name,
                                file_size=file_.size,
                                contents=file_.file,
                                user_id=request.user.id,
                                force=as_bool(request.POST, 'force', False),
                                directory_path=request.POST.get('directory_path'))

        # workaround for old frontend usage which checks status based on string constants in response data
        # and not on the status codes
        if resp.status_code == status.HTTP_201_CREATED:
            resp.status_code = status.HTTP_200_OK
        return resp

    @action(detail=True, methods=['post'])
    def batch_upload(self, request, **kwargs):
        """
        Upload files from given sub-folder in media/data/documents folder\n
            Params:
                - source_path: relative path to a folder with documents
        """
        session = self.get_object()
        session_id = session.pk
        project = session.project
        folder_name = request.POST.get('folder') or request.POST.get('source_path')

        if not session_id or not folder_name:
            raise ValidationError('Provide session id and folder name.')

        file_list = get_file_storage().list_documents(folder_name)
        # TODO: limit file size - see def upload()
        for file_path in file_list:
            file_name = os.path.basename(file_path)

            # Code for running locators and detecting field values has been moved to LoadDocuments task
            # for the unification purposes between old and new ui.

            call_task(
                LoadDocuments,
                source_data=file_path,
                user_id=request.user.id,
                session_id=session_id,
                metadata={'session_id': session_id, 'file_name': file_name},
                run_standard_locators=True,
                linked_tasks=None)

        if project.send_email_notification and not session.notified_upload_started:
            self._notify_upload_started(session)

        return Response('Started')

    @action(detail=True, methods=['post'])
    def _batch_upload(self, request, **kwargs):
        """
        Upload batch of files\n
            Params:
                - folder (source_path): str - absolute path to a directory containing files
                - force: bool (optional) - whether rewrite existing file and Document
        """
        # permissions check
        _ = self.get_object()

        # TODO: limit file size - see def upload()
        folder_name = request.POST.get('folder') or request.POST.get('source_path')
        kwargs['folder'] = folder_name
        if folder_name:
            dir_path = os.path.join(settings.MEDIA_ROOT,
                                    settings.FILEBROWSER_DOCUMENTS_DIRECTORY,
                                    folder_name)
            files = os.listdir(dir_path)
            for file_name in files:
                a_file = File(open(os.path.join(dir_path, file_name)), name=file_name)
                request.FILES['file'] = a_file
                try:
                    self.upload(request, **kwargs)
                except APIException as e:
                    if ALREADY_EXISTS in str(e):
                        pass

            return Response('Uploading of {} files started'.format(len(files)))

        return Response('No folder specified', status=400)

    @action(methods=['delete'], url_path='cancel', detail=True)
    def cancel_upload(self, request, **kwargs):
        """
        Delete a file from session\n
            Params:
                - filename: str
        """
        session_id = self.get_object().pk

        call_task(
            CancelUpload,
            user_id=request.user.id,
            session_id=session_id)

        return Response('Canceled')

    @action(methods=['delete'], url_path='delete-file', detail=True)
    def delete_file(self, request, **kwargs):
        """
        Delete a file from session\n
            Params:
                - filename: str
        """
        session_id = self.get_object().pk
        file_name = request.POST.get('filename')

        if not file_name:
            raise APIException('Provide a file name.')

        try:
            storage = FileSystemStorage(
                location=os.path.join(
                    settings.MEDIA_ROOT,
                    settings.FILEBROWSER_DOCUMENTS_DIRECTORY,
                    session_id))

            if storage.exists(file_name):
                storage.delete(file_name)
                file_tasks = Task.objects \
                    .filter(metadata__session_id=session_id) \
                    .filter(metadata__file_name=file_name)
                for file_task in file_tasks:
                    if file_task.metadata.get('file_name') == file_name:
                        purge_task(file_task.id)
                Document.objects \
                    .filter(upload_session_id=session_id, name=file_name) \
                    .delete()
                return Response('Deleted')
            raise APIException("File doesn't exist")

        except Exception as e:
            raise APIException(str(e))


# --------------------------------------------------------
# Project Clustering Views
# --------------------------------------------------------

analyze_api_module = get_api_module('analyze')


class ProjectSerializer(ProjectDetailSerializer):
    class Meta(ProjectDetailSerializer.Meta):
        model = Project
        fields = ['pk', 'name', 'progress']


class DocumentClusterSerializer(analyze_api_module.DocumentClusterSerializer):
    class Meta(analyze_api_module.DocumentClusterSerializer.Meta):
        model = DocumentCluster
        fields = ['pk', 'cluster_id', 'self_name', 'name', 'documents_count']


class ProjectClusteringSerializer(serializers.ModelSerializer):
    document_clusters = DocumentClusterSerializer(many=True, read_only=True)
    project_clusters_documents_count = serializers.IntegerField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = ProjectClustering
        fields = ['pk', 'document_clusters', 'metadata', 'created_date',
                  'status', 'reason',
                  'project_clusters_documents_count']

    def get_status(self, obj):
        # 1. task purged
        if not obj.task and obj.status == PENDING:
            return
        # 2. task started, but status is not set yet
        if obj.status is None and obj.task:
            return obj.task.status
        return obj.status


class ProjectClusteringViewSet(apps.common.mixins.JqListAPIMixin, viewsets.ReadOnlyModelViewSet):
    """
    list: ProjectCluster List
    retrieve: ProjectCluster Details
    """
    queryset = ProjectClustering.objects.all()
    serializer_class = ProjectClusteringSerializer

    def get_queryset(self):
        qs = super().get_queryset() \
            .prefetch_related('document_clusters') \
            .select_related('project', 'task') \
            .annotate(project_clusters_documents_count=Count('document_clusters__documents', distinct=True))
        return qs


router = routers.DefaultRouter()
router.register(r'task-queues', TaskQueueViewSet, 'task-queue')
router.register(r'projects', ProjectViewSet, 'project')
router.register(r'project-clustering', ProjectClusteringViewSet, 'project-clustering')
router.register(r'upload-session', UploadSessionViewSet, 'upload-session')

urlpatterns = [
    path('', include(router.urls)),
    path('projects/<int:pk>/clustering-status/',
         ProjectViewSet.as_view({'get': 'clustering_status'}), name='clustering_status'),
    path('projects/<int:pk>/cluster/',
         ProjectViewSet.as_view({'post': 'cluster'}), name='cluster')
]
