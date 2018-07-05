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
import os
import re
import sys

# Third-party imports
from rest_framework import serializers, routers, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.views import APIView
from rest_framework.response import Response

# Django imports
from django.conf import settings
from django.contrib.postgres.aggregates.general import StringAgg
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.db.models import Count, Min, Max

# Project imports
from apps.analyze.models import DocumentCluster
from apps.common.mixins import JqListAPIMixin
from apps.common.models import ReviewStatus
from apps.common.utils import get_api_module
from apps.document.models import Document, DocumentType
from apps.extract.models import CurrencyUsage
from apps.project.models import Project, TaskQueue, UploadSession, ProjectClustering
from apps.users.models import User
from apps.task.models import Task
from apps.task.tasks import call_task, purge_task
from urls import custom_apps
from apps.project.tasks import THIS_MODULE    # noqa


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.1/LICENSE"
__version__ = "1.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class PatchedListView(APIView):
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


class TaskQueueViewSet(JqListAPIMixin, viewsets.ModelViewSet):
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
    sessions_status_data = {str(i.pk): i.status for i in obj.uploadsession_set.all()}
    completed_sessions = {k: v for k, v in sessions_status_data.items() if v == 'Parsed'}
    uncompleted_sessions = {k: v for k, v in sessions_status_data.items() if v != 'Parsed'}
    project_uploaded_documents_count = Document.objects.filter(
        upload_session__project=obj).count()

    stats = {'project_current_documents_count': obj.document_set.count(),
             'project_uploaded_documents_count': project_uploaded_documents_count,
             'project_tasks_progress': obj.project_tasks_progress,
             'project_tasks_completed': obj.project_tasks_completed,
             'completed_sessions': completed_sessions or None,
             'uncompleted_sessions': uncompleted_sessions or None}

    if obj.type is None:
        project_clusters_documents_count = obj.projectclustering_set.last() \
            .document_clusters.aggregate(c=Count('documents'))['c'] \
            if obj.projectclustering_set.exists() else 0
        project_unclustered_documents_count = project_uploaded_documents_count - \
                                              project_clusters_documents_count
        reassigning_ots = {'task_name': 'reassigning',
                           'old_project_id': obj.pk}
        stats.update({
            'project_clusters_documents_count': project_clusters_documents_count,
            'project_unclustered_documents_count': project_unclustered_documents_count,
            'reassigning_progress': Task.special_tasks_progress_groups(reassigning_ots),
            'reassigning_completed': Task.special_tasks_completed(reassigning_ots),
            'cleanup_completed': Task.special_tasks_completed({'task_name': 'clean-project',
                                                               '_project_id': obj.pk}),
        })

    return stats


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ['uid', 'code', 'title']


common_api_module = get_api_module('common')


class ProjectDetailSerializer(serializers.ModelSerializer):
    status = serializers.PrimaryKeyRelatedField(
        queryset=ReviewStatus.objects.all(), many=False, required=False)
    status_data = common_api_module.ReviewStatusSerializer(
        source='status', many=False, read_only=True)
    owners = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False)
    owners_data = UserSerializer(
        source='owners', many=True, read_only=True)
    reviewers = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False)
    reviewers_data = UserSerializer(
        source='reviewers', many=True, read_only=True)
    type = serializers.PrimaryKeyRelatedField(
        queryset=DocumentType.objects.all(), many=False, required=False)
    type_data = DocumentTypeSerializer(source='type', many=False)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['pk', 'name', 'description', 'status', 'status_data',
                  'owners', 'owners_data', 'reviewers', 'reviewers_data',
                  'type', 'type_data', 'progress']

    def get_progress(self, obj):
        return project_progress(obj)


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['pk', 'name', 'description', 'type']


class ProjectUpdateSerializer(ProjectDetailSerializer):
    class Meta(ProjectDetailSerializer.Meta):
        model = Project
        fields = ['pk', 'name', 'description', 'status',
                  'owners', 'reviewers', 'type']


def require_generic_contract_type(func):
    def decorator(cls, *args, **kwargs):
        project = cls.get_object()
        if project.type and not project.type.is_generic():
            raise APIException('Allowed for projects with "Generic Contract Type" only')
        return func(cls, *args, **kwargs)
    decorator.__doc__ = func.__doc__
    return decorator


class ProjectViewSet(JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: Project List
    retrieve: Retrieve Project
    create: Create Project
    update: Update Project
    partial_update: Partial Update Project
    delete: Delete Project
    """
    queryset = Project.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return ProjectCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProjectUpdateSerializer
        return ProjectDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # if self.request.user.is_reviewer:
        #     qs = qs.filter(task_queues__reviewers=self.request.user)
        qs = qs.prefetch_related('status', 'owners', 'reviewers', 'uploadsession_set')
        return qs

    @detail_route(methods=['get'])
    def progress(self, request, **kwargs):
        """
        Project Progress - completed/uncompleted session, status of project tasks\n
        """
        return Response(project_progress(self.get_object()))

    @detail_route(methods=['post'])
    @require_generic_contract_type
    def cluster(self, request, **kwargs):
        """
        Cluster Project Documents\n
            Params:
                - method: str[KMeans, MiniBatchKMeans, Birch, DBSCAN]
                - n_clusters: int
                - force: bool (optional) - force clustering if uncompleted tasks exist
        """
        if not request.POST.get('force') == 'true':
            obj = self.get_object()
            progress = project_progress(obj)
            if progress['uncompleted_sessions'] is not None:
                raise APIException('Project has uncompleted upload sessions.')
            elif progress['completed_sessions'] is None:
                raise APIException("Project hasn't completed upload sessions.")

        project_id = kwargs.get('pk')

        project_clustering = ProjectClustering.objects.create(project_id=project_id)

        try:
            n_clusters = int(request.POST.get('n_clusters', 3))
        except ValueError:
            n_clusters = 3

        task_id = call_task(
            task_name='ClusterProjectDocuments',
            module_name='apps.project.tasks',
            user_id=request.user.id,
            project_id=project_id,
            project_clustering_id=project_clustering.id,
            method=request.POST.get('method', 'KMeans'),
            metadata={'project_id': project_id},
            n_clusters=n_clusters)

        return Response({'task_id': task_id,
                         'project_clustering_id': project_clustering.id})

    @detail_route(methods=['get'], url_path='clustering-status')
    @require_generic_contract_type
    def clustering_status(self, request, **kwargs):
        """
        Last Clustering task status/data\n
            Params:
                - project_clustering_id: int (optional) - return last if not provided
        """
        project_clustering_id = request.GET.get('project_clustering_id')
        project = self.get_object()

        if project_clustering_id:
            clustering = project.projectclustering_set.get(pk=project_clustering_id)
        else:
            clustering = project.projectclustering_set.last()

        if not clustering:
            return Response({'details': 'Cluster session not found'}, status=200)

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
                    if len(cluster_reassigning_data) != 1:
                        raise APIException('Found more than one reassigning of cluster id={}'
                                           .format(cluster['pk']))
                    cluster['reassigned_to_project_id'] = cluster_reassigning_data[0]['new_project_id']

                cluster['cluster_terms'] = data['metadata']['clusters_data'][str(cluster['cluster_id'])]['cluster_terms']

            except KeyError:
                pass

        return Response(data)

    @detail_route(methods=['post'], url_path='send-clusters-to-project')
    @require_generic_contract_type
    def send_clusters_to_project(self, request, **kwargs):
        """
        Send clusters to another Project\n
            Params:
                - cluster_ids: list[int]
                - project_id: int
        """
        cluster_ids = [int(i) for i in request.POST.getlist('cluster_ids')]
        project = self.get_object()
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
            task_name='ReassignProjectClusterDocuments',
            module_name='apps.project.tasks',
            cluster_ids=cluster_ids,
            project_id=project.id,
            new_project_id=new_project_id,
            user_id=request.user.id)

        return Response('OK')

    @detail_route(methods=['post'])
    # @require_generic_contract_type
    def cleanup(self, request, **kwargs):
        """
        Clean project (Generic Contract Type project)
        """
        call_task(
            task_name='CleanProject',
            module_name='apps.project.tasks',
            project_id=int(kwargs['pk']),
            user_id=request.user.id)

        return Response('OK')

    @detail_route(methods=['post'])
    def assign_documents(self, request, **kwargs):
        """
        Bulk assign batch of documents to a review team member\n
            Params:
                document_ids: list[int]
                assignee_id: int
            Returns:
                int (number of reassigned documents)
        """
        document_ids = [int(i) for i in request.POST.getlist('document_ids')]
        assignee_id = request.POST.get('assignee_id')
        ret = Document.objects\
            .filter(pk__in=document_ids)\
            .update(assignee=assignee_id)
        return Response(ret)

    @detail_route(methods=['get'])
    def documents(self, request, **kwargs):
        """
        Get list of project documents
        """
        project = self.get_object()

        # if project.type.is_generic() and (project.projectclustering_set.exists()
        #         and not project.projectclustering_set.last().completed):
        #     return Response('Project documents clustering is not completed.', status=500)

        qs = list(
            Document.objects
                .filter(project=project)
                .values('id', 'name')
                .annotate(cluster_id=Max('documentcluster'),
                          parties=StringAgg('textunit__partyusage__party__name',
                                            delimiter=', ',
                                            distinct=True),
                          min_date=Min('textunit__dateusage__date'),
                          # max_currency=Max('textunit__currencyusage__amount'),
                          max_date=Max('textunit__dateusage__date'))
                .order_by('cluster_id', 'name'))

        # get max currency amount and currency itself
        # as it's hard to get currency itself like USD
        # along with amount in previous query
        currencies_qs = CurrencyUsage.objects \
            .filter(text_unit__document__project=project) \
            .values('text_unit__document__name', 'currency') \
            .annotate(max_currency=Max('amount')).order_by('max_currency')
        max_currencies = {i['text_unit__document__name']:
                              {'max_currency': i['max_currency'],
                               'max_currency_str': '{} {}'.format(
                                   i['currency'],
                                   int(i['max_currency'])
                                   if int(i['max_currency']) == i['max_currency']
                                   else i['max_currency'])}
                          for i in currencies_qs}

        # join two queries results
        for item in qs:
            if item['name'] in max_currencies:
                item.update(max_currencies[item['name']])
            else:
                item.update({'max_currency': None, 'max_currency_str': None})

        return Response(qs)


# --------------------------------------------------------
# UploadSession Views
# --------------------------------------------------------

class UploadSessionSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), many=False, required=True)
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=False, required=False)

    class Meta:
        model = UploadSession
        fields = ['uid', 'project', 'created_by']


class UploadSessionDetailSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(many=False)
    project = ProjectDetailSerializer(many=False)
    document_type = DocumentTypeSerializer(source='project.type', many=False)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = UploadSession
        fields = ['uid', 'project', 'created_by', 'created_date',
                  'document_type', 'progress']

    def get_progress(self, obj):
        return obj.document_tasks_progress(details=True)


class UploadSessionViewSet(JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: Session Upload List
    retrieve: Retrieve Session Upload
    create: Create Session Upload
    update: Update Session Upload
    partial_update: Partial Update Session Upload
    delete: Delete Session Upload
    """
    queryset = UploadSession.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UploadSessionSerializer
        return UploadSessionDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('project')
        return qs

    def create(self, request, *args, **kwargs):
        project = Project.objects.get(pk=request.data.get('project'))
        # if project.type.is_generic() and project.uploadsession_set.exists():
        #     return Response("This Project already has upload session", status=500)
        project.drop_clusters()
        return super().create(request, *args, **kwargs)

    @detail_route(methods=['get'])
    def progress(self, request, **kwargs):
        """
        Get Progress for a session per files (short form)
        """
        session = self.get_object()
        document_tasks_progress = session.document_tasks_progress()
        result = {'project_id': session.project.pk,
                  'document_tasks_progress': document_tasks_progress or None,
                  'document_tasks_progress_total': session.document_tasks_progress_total,
                  'session_status': session.status}
        return Response(result)

    @list_route(methods=['get'])
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
        result = {str(i.pk): i.status for i in qs}
        return Response(result)

    @detail_route(methods=['post'])
    def upload(self, request, **kwargs):
        """
        Upload a File\n
            Params:
                - file: file object
                - force: bool (optional) - whether rewrite existing file and Document
                - send_email_notifications: bool (optional) - sent notification email that batch uploading started
        """
        session = self.get_object()
        session_id = kwargs.get('pk')
        project = session.project
        file_ = request.FILES.dict().get('file')

        if session_id and file_:
            try:
                project_storages = {
                    str(_session_id): FileSystemStorage(
                        location=os.path.join(
                            settings.MEDIA_ROOT,
                            settings.FILEBROWSER_DIRECTORY,
                            str(_session_id)))
                    for _session_id in project.uploadsession_set.values_list('pk', flat=True)}

                # check existing documents with the same name
                this_file_documents = project.document_set.filter(name=file_.name)

                # check existing files with the same name but not stored yet as Document
                this_file_storages = {
                    _session_id: _storage
                    for _session_id, _storage in project_storages.items()
                    if _storage.exists(file_.name) and not Document.objects.filter(
                        source_path=os.path.join(
                            _session_id, file_.name)).exists()}

                if this_file_documents.exists() or this_file_storages:
                    if request.POST.get('force') == 'true':
                        for _session_id, _storage in this_file_storages.items():
                            _storage.delete(file_.name)
                            file_tasks = Task.objects\
                                .filter(metadata__session_id=_session_id)\
                                .filter(metadata__file_name=file_.name)
                            for file_task in file_tasks:
                                if file_task.metadata.get('file_name') == file_.name:
                                    purge_task(file_task.id)
                            # TODO: redundant?
                            Document.objects\
                                .filter(upload_session_id=_session_id, name=file_.name)\
                                .delete()
                        for doc in this_file_documents:
                            doc.delete()
                    else:
                        raise APIException('Already exists')

                storage = FileSystemStorage(
                    location=os.path.join(
                        settings.MEDIA_ROOT,
                        settings.FILEBROWSER_DIRECTORY,
                        session_id))

                stored_file_name = storage.save(file_.name, file_.file)

                required_locators = ['date',
                                     'party',
                                     'term',
                                     'geoentity',
                                     'currency',
                                     'citation',
                                     'definition',
                                     'duration']

                linked_tasks = [
                    {'task_name': 'Locate',
                     'locate': required_locators,
                     'parse': 'sentences',
                     'do_delete': False,
                     'metadata': {'session_id': session_id, 'file_name': file_.name},
                     'user_id': request.user.id}
                ]

                document_type = UploadSession.objects.get(pk=session_id).project.type

                # if Document type specified
                if document_type:

                    for app_name in custom_apps:
                        module_str = 'apps.%s.tasks' % app_name
                        module = sys.modules.get(module_str)
                        if hasattr(module, 'DetectFieldValues'):
                            linked_tasks.append(
                                {'task_name': 'DetectFieldValues',
                                 'module_name': module_str,
                                 'do_not_write': False,
                                 'metadata': {'session_id': session_id, 'file_name': file_.name},
                                 'user_id': request.user.id})

                call_task(
                    task_name='LoadDocuments',
                    source_path=os.path.join(session_id, stored_file_name),
                    user_id=request.user.id,
                    metadata={'session_id': session_id, 'file_name': file_.name},
                    linked_tasks=linked_tasks)

                if request.POST.get('send_email_notifications') == 'true' and \
                        not session.notified_upload_started:
                    session.notify_upload_started()

            except Exception as e:
                raise APIException(str(e))
        else:
            raise ValidationError('Provide session_id and file in request data.')
        return Response('Loaded')

    @detail_route(methods=['delete'], url_path='delete-file')
    def delete_file(self, request, **kwargs):
        """
        Delete a file from session\n
            Params:
                - filename: str
        """
        session_id = kwargs.get('pk')
        file_name = request.POST.get('filename')

        if not file_name:
            raise APIException('Provide a file name.')

        try:
            storage = FileSystemStorage(
                location=os.path.join(
                    settings.MEDIA_ROOT,
                    settings.FILEBROWSER_DIRECTORY,
                    session_id))

            if storage.exists(file_name):
                storage.delete(file_name)
                file_tasks = Task.objects\
                    .filter(metadata__session_id=session_id)\
                    .filter(metadata__file_name=file_name)
                for file_task in file_tasks:
                    if file_task.metadata.get('file_name') == file_name:
                        purge_task(file_task.id)
                Document.objects\
                    .filter(upload_session_id=session_id, name=file_name)\
                    .delete()
                return Response('Deleted')
            else:
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


class TaskSerializer(serializers.ModelSerializer):
    reason = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['pk', 'name', 'progress', 'status', 'reason']

    def get_reason(self, obj):
        if obj.has_error:
            message_head = 'Clustering failed. '
            message_body = 'Unexpected error while clustering. Try again later.'
            if obj.result:
                task_result = obj.result
                if isinstance(task_result, dict):
                    exc_message = task_result.get('exc_message')
                    exc_type = task_result.get('exc_type')
                    if exc_message and exc_type:
                        # trace = obj.traceback
                        if ('max_df corresponds to < documents than min_df' in exc_message) or\
                           ('Number of samples smaller than number of clusters' in exc_message) or\
                           (re.search(r'n_samples=\d+ should be >= n_clusters=\d+', exc_message)):
                            message_body = 'Try to increase number of documents ' \
                                           'or set lower number of clusters.'
                        elif re.search(r'n_components=\d+ must be between \d+ and n_features=\d+',
                                exc_message):
                            message_body = 'Chosen documents seems are very similar,' \
                                           ' clustering algorithm is not able to form clusters.'
            reason = message_head + message_body
            return reason


class DocumentClusterSerializer(analyze_api_module.DocumentClusterSerializer):
    class Meta(analyze_api_module.DocumentClusterSerializer.Meta):
        model = DocumentCluster
        fields = ['pk', 'cluster_id', 'self_name', 'using',
                  'documents_count', 'document_data']


class ProjectClusteringSerializer(serializers.ModelSerializer):
    document_clusters = DocumentClusterSerializer(many=True, read_only=True)
    project = ProjectSerializer(many=False, read_only=True)
    task = TaskSerializer(many=False, read_only=True)
    project_uploaded_documents_count = serializers.SerializerMethodField()
    project_current_documents_count = serializers.SerializerMethodField()
    project_clusters_documents_count = serializers.SerializerMethodField()
    project_unclustered_documents_count = serializers.SerializerMethodField()

    class Meta:
        model = ProjectClustering
        fields = ['pk', 'project', 'document_clusters', 'task',
                  'metadata', 'created_date',
                  'project_uploaded_documents_count',
                  'project_current_documents_count',
                  'project_clusters_documents_count',
                  'project_unclustered_documents_count']

    def get_project_uploaded_documents_count(self, obj):
        return Document.objects.filter(upload_session__project=obj.project).count()

    def get_project_current_documents_count(self, obj):
        return obj.project.document_set.count()

    def get_project_clusters_documents_count(self, obj):
        return obj.document_clusters.aggregate(c=Count('documents'))['c']

    def get_project_unclustered_documents_count(self, obj):
        return self.get_project_uploaded_documents_count(obj) - \
               self.get_project_clusters_documents_count(obj)


class ProjectClusteringViewSet(JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: ProjectCluster List
    retrieve: ProjectCluster Details
    """
    queryset = ProjectClustering.objects.all()
    serializer_class = ProjectClusteringSerializer
    http_method_names = ['get']

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related('document_clusters').select_related('project', 'task')
        return qs


router = routers.DefaultRouter()
router.register(r'task-queues', TaskQueueViewSet, 'task-queue')
router.register(r'projects', ProjectViewSet, 'project')
router.register(r'project-clustering', ProjectClusteringViewSet, 'project-clustering')
router.register(r'upload-session', UploadSessionViewSet, 'upload-session')
