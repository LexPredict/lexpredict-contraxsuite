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

# Third-party imports
from rest_framework import serializers, routers, viewsets
from rest_framework.views import APIView

# Django imports
from django.http import JsonResponse

# Project imports
from apps.common.mixins import JqMixin
from apps.project.models import Project, ProjectStatus, TaskQueue
from apps.document.models import Document
from apps.users.models import User
from apps.analyze.models import DocumentCluster

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.5/LICENSE"
__version__ = "1.0.7"
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


class TaskQueueViewSet(JqMixin, viewsets.ModelViewSet):
    """
    list: Task Queue List\n
        GET params:
          - only_completed: bool
          - only_assigned: bool
          - document_id: int
          - with_documents: bool
          - description_contains: str
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
# ProjectStatus Views
# --------------------------------------------------------

class ProjectStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectStatus
        fields = ['pk', 'name', 'code', 'order']


class ProjectStatusViewSet(JqMixin, viewsets.ModelViewSet):
    """
    list: ProjectStatus List\n
        GET params:
            - name: str
            - name_contains: str
            - code: str
            - code_contains: str
    retrieve: Retrieve ProjectStatus
    create: Create ProjectStatus
    update: Update ProjectStatus
    partial_update: Partial Update ProjectStatus
    delete: Delete ProjectStatus
    """
    queryset = ProjectStatus.objects.all()
    serializer_class = ProjectStatusSerializer


# --------------------------------------------------------
# Project Views
# --------------------------------------------------------

class ProjectSerializer(serializers.ModelSerializer):
    task_queues = serializers.PrimaryKeyRelatedField(
        queryset=TaskQueue.objects.all(), many=True, required=False)
    task_queue_data = TaskQueueSerializer(
        source='task_queues', many=True, read_only=True)
    status = serializers.PrimaryKeyRelatedField(
        queryset=ProjectStatus.objects.all(), many=True, required=False)
    status_data = ProjectStatusSerializer(
        source='status', many=True, read_only=True)
    owners = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False)
    owners_data = UserSerializer(
        source='owners', many=True, read_only=True)
    reviewers = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False)
    reviewers_data = UserSerializer(
        source='reviewers', many=True, read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['pk', 'name', 'description', 'status', 'status_data',
                  'owners', 'owners_data', 'reviewers', 'reviewers_data',
                  'task_queues', 'task_queue_data', 'progress']

    def get_progress(self, obj):
        return obj.progress(as_dict=True)


class ProjectViewSet(JqMixin, viewsets.ModelViewSet):
    """
    list: Project List\n
        GET params:
            - name: str
            - name_contains: str
            - description: str
            - description_contains: str
            - status__name: str
            - status__name_contains: str
            - status__code: str
            - status__code_contains: str
            - owners__username: str
            - reviewers__username: str
    retrieve: Retrieve Project
    create: Create Project
    update: Update Project
    partial_update: Partial Update Project
    delete: Delete Project
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_reviewer:
            qs = qs.filter(task_queues__reviewers=self.request.user)
        qs = qs.prefetch_related('task_queues')
        return qs


router = routers.DefaultRouter()
router.register(r'task-queues', TaskQueueViewSet, 'task-queue')
router.register(r'project-statuses', ProjectStatusViewSet, 'project-status')
router.register(r'projects', ProjectViewSet, 'project')
