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
import json
import mimetypes
import os
import tarfile
import zipfile
from collections import OrderedDict
from io import BytesIO
from typing import BinaryIO, Union, Optional, List, Any, Dict

# Django imports
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.db import connection, transaction
from django.db.models import Count, Subquery, Q, F, Avg, Case, When, DecimalField, \
    Value, CharField, OuterRef, IntegerField
from django.http import JsonResponse, HttpRequest
from django.http.request import QueryDict
from django.urls import path, include
from django.utils.timezone import now

# Third-party imports
from celery.states import PENDING, SUCCESS
from guardian.shortcuts import get_objects_for_user
from rest_framework import routers, viewsets, views, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

# Project imports
import apps.common.mixins
from apps.analyze.models import DocumentCluster, SimilarityRun
from apps.analyze.tasks import Cluster
from apps.common.api.v1 import ActionViewSchema, ActionViewSet
from apps.common.archive_file import ArchiveFile
from apps.common.file_storage import get_file_storage
from apps.common.log_utils import render_error
from apps.common.logger import CsLogger
from apps.common.models import Action, ReviewStatus, AppVarStorage
from apps.common.schemas import object_list_content
from apps.common.url_utils import as_bool
from apps.common.utils import get_api_module, safe_to_int, cap_words
from apps.document.async_tasks.detect_field_values_task import DetectFieldValues
from apps.document.constants import DOCUMENT_TYPE_PK_GENERIC_DOCUMENT
from apps.document.models import Document, DocumentType, DocumentField, \
    FieldAnnotation, FieldAnnotationFalseMatch, FieldAnnotationStatus
from apps.document.repository.document_field_repository import DocumentFieldRepository
from apps.document.pdf_coordinates.coord_text_map import CoordTextMap
from apps.document.tasks import plan_process_documents_status_changed, plan_process_documents_assignee_changed
from apps.extract.models import TermTag, CompanyTypeTag
from apps.project.models import Project, TaskQueue, UploadSession, ProjectClustering, UserProjectsSavedFilter
from apps.project.schemas import *
from apps.project.signals import project_soft_deleted
from apps.project.tasks import ReassignProjectClusterDocuments, ClusterProjectDocuments, CleanProject, CancelUpload, \
    LoadArchive, track_session_completed, SetAnnotationsStatus, UpdateProjectDocumentsFields
from apps.rawdb.constants import FIELD_CODE_STATUS_ID, FIELD_CODE_ASSIGNEE_ID, FIELD_CODE_ASSIGN_DATE
from apps.task.models import Task
from apps.task.tasks import call_task, purge_task, LoadDocuments, call_task_func
from apps.task.schemas import ProjectTasksSchema, ProjectActiveTasksSchema, ProjectTaskLogSchema
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


common_api_module = get_api_module('common')
users_api_module = get_api_module('users')
ALREADY_EXISTS = 'Already exists'


class PatchedListView(views.APIView):
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
        fields = ['pk', 'username']


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


class TaskQueueViewSet(DjangoModelPermissions, apps.common.mixins.JqListAPIMixin, viewsets.ModelViewSet):
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


# --------------------------------------------------------
# Project Views
# --------------------------------------------------------

def project_progress(obj):
    if not hasattr(obj, 'project_total_documents_count'):
        obj.project_total_documents_count = obj.document_set.count()
    if not hasattr(obj, 'project_current_documents_count'):
        obj.project_current_documents_count = obj.document_set.filter(processed=True, delete_pending=False).count()
    if not hasattr(obj, 'project_reviewed_documents_count'):
        obj.project_reviewed_documents_count = obj.document_set.filter(processed=True, delete_pending=False).filter(
            status__group__is_active=False).count()

    stats = {
        'project_total_documents_count': obj.project_total_documents_count,
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
    junior_reviewers = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False)
    junior_reviewers_data = users_api_module.UserSerializer(
        source='junior_reviewers', many=True, read_only=True)
    type = serializers.PrimaryKeyRelatedField(
        queryset=DocumentType.objects.all(), many=False, required=False)
    type_data = DocumentTypeSerializer(source='type', many=False)

    progress = serializers.SerializerMethodField()
    progress.output_field = serializers.DictField(child=serializers.IntegerField())    # needed for schema

    user_permissions = serializers.SerializerMethodField()
    user_permissions.output_field = serializers.ListField(child=serializers.CharField())    # needed for schema

    app_vars = serializers.SerializerMethodField()
    app_vars.output_field = serializers.JSONField()

    created_by_name = serializers.CharField()
    modified_by_name = serializers.CharField()

    document_similarity_run_params = serializers.SerializerMethodField()
    document_similarity_run_params.output_field = serializers.DictField()

    text_unit_similarity_run_params = serializers.SerializerMethodField(allow_null=True)
    text_unit_similarity_run_params.output_field = serializers.DictField()

    document_similarity_process_allowed = serializers.SerializerMethodField()
    document_similarity_process_allowed.output_field = serializers.BooleanField()

    text_unit_similarity_process_allowed = serializers.SerializerMethodField()
    text_unit_similarity_process_allowed.output_field = serializers.BooleanField()

    class Meta:
        model = Project
        fields = ['pk', 'name', 'description',
                  'created_date', 'created_by_name', 'modified_date', 'modified_by_name',
                  'send_email_notification', 'hide_clause_review',
                  'status', 'status_data',
                  'owners', 'owners_data',
                  'reviewers', 'reviewers_data',
                  'super_reviewers', 'super_reviewers_data',
                  'junior_reviewers', 'junior_reviewers_data',
                  'type', 'type_data', 'progress', 'user_permissions',
                  'term_tags', 'document_transformer', 'text_unit_transformer',
                  'companytype_tags', 'app_vars',
                  'document_similarity_run_params', 'text_unit_similarity_run_params',
                  'document_similarity_process_allowed', 'text_unit_similarity_process_allowed']

    def get_progress(self, obj):
        return project_progress(obj)

    def get_user_permissions(self, obj):
        user = self.context['request'].user
        return sorted(user.get_all_permissions(obj))

    def get_app_vars(self, obj):
        from apps.common.api.v1 import ProjectAppVarSerializer
        app_vars = AppVarStorage.get_project_app_vars(obj.id, self.context['request'].user)
        app_vars_data = ProjectAppVarSerializer(app_vars, many=True).data
        return app_vars_data

    def get_document_similarity_run_params(self, obj):
        run = SimilarityRun.objects.filter(project=obj, unit_source='document').order_by('created_date').last()
        if run:
            return {'similarity_threshold': run.similarity_threshold,
                    'distance_type': run.distance_type,
                    'use_tfidf': run.use_tfidf,
                    'feature_source': run.feature_source}

    def get_text_unit_similarity_run_params(self, obj):
        run = SimilarityRun.objects.filter(project=obj, unit_source='text_unit').order_by('created_date').last()
        if run:
            return {'similarity_threshold': run.similarity_threshold,
                    'distance_type': run.distance_type,
                    'use_tfidf': run.use_tfidf,
                    'feature_source': run.feature_source,
                    'unit_type': run.unit_type}

    def get_document_similarity_process_allowed(self, obj):
        from apps.analyze.app_vars import SIMILARITY_MAX_BASE
        return 1 < obj.document_set.filter(delete_pending=False).count() < SIMILARITY_MAX_BASE.val()

    def get_text_unit_similarity_process_allowed(self, obj):
        from apps.analyze.app_vars import SIMILARITY_MAX_BASE
        sentence_count = obj.textunit_set.filter(unit_type='sentence', document__delete_pending=False).count()
        return 1 < sentence_count < SIMILARITY_MAX_BASE.val()


class CustomErrorMessageSerializer:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].error_messages['required'] = '"{}" field is required.'.format(cap_words(field))
            self.fields[field].error_messages['null'] = '"{}" field may not be null.'.format(cap_words(field))
            self.fields[field].error_messages['blank'] = '"{}" field may not be blank.'.format(cap_words(field))


class ProjectCreateSerializer(CustomErrorMessageSerializer, serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['pk', 'name', 'description', 'type',
                  'send_email_notification', 'term_tags',
                  'companytype_tags']


class ProjectUpdateSerializer(CustomErrorMessageSerializer, ProjectDetailSerializer):
    class Meta(ProjectDetailSerializer.Meta):
        model = Project
        fields = ['pk', 'name', 'description', 'status', 'send_email_notification',
                  'owners', 'reviewers', 'super_reviewers', 'junior_reviewers',
                  'type', 'hide_clause_review', 'term_tags', 'companytype_tags',
                  'document_transformer', 'text_unit_transformer']

    def update(self, instance, validated_data):
        prev_team_ids = set(instance.get_team().values_list('id', flat=True))

        res = super().update(instance, validated_data)

        curr_team_qs = instance.get_team()
        curr_team_ids = set(curr_team_qs.values_list('id', flat=True))

        removed_user_ids = prev_team_ids - curr_team_ids

        with transaction.atomic():
            transaction.on_commit(lambda: instance.clean_up_assignees(removed_user_ids))

        instance.reset_project_team_perms()

        return res


class ProjectListSerializer(ProjectDetailSerializer):
    count_of_documents = serializers.IntegerField()

    # CS-6593, see ProjectViewSet.get_queryset below
    # count_of_documents.output_field = serializers.IntegerField()

    class Meta(ProjectDetailSerializer.Meta):
        model = Project
        fields = ['pk', 'name', 'status', 'status_data',
                  'type', 'type_data', 'count_of_documents']

    # CS-6593, see ProjectViewSet.get_queryset below
    # def get_count_of_documents(self, obj):
    #     user = self.context['request'].user
    #     if user.has_perm('project.view_documents', obj):
    #         return obj.document_set.filter(processed=True).count()
    #     return obj.document_set.filter(assignee=user, processed=True).count()
    # get_count_of_documents.output_field = serializers.IntegerField()


class ProjectStatsSerializer(serializers.Serializer):
    # serializer for openapi schema, see apps.project.schemas.ProjectStatsSchema - it uses this
    project_id = serializers.IntegerField()
    name = serializers.CharField()
    type_title = serializers.CharField()
    documents_total = serializers.IntegerField()
    clauses_total = serializers.IntegerField()
    avg_ocr_grade = serializers.IntegerField(allow_null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for document_status_name in ReviewStatus.objects.values_list('name', flat=True):
            status_count_col_name = 'document_status_' + document_status_name.lower().replace(' ', '_')
            status_pcnt_col_name = f"document_status_{document_status_name.lower().replace(' ', '_')}_pcnt"
            self.fields[status_count_col_name] = serializers.IntegerField()
            self.fields[status_pcnt_col_name] = serializers.FloatField()
        for clause_status_name in FieldAnnotationStatus.objects.values_list('name', flat=True):
            status_count_col_name = 'clause_status_' + clause_status_name.lower().replace(' ', '_')
            status_pcnt_col_name = f"clause_status_{clause_status_name.lower().replace(' ', '_')}_pcnt"
            self.fields[status_count_col_name] = serializers.IntegerField()
            self.fields[status_pcnt_col_name] = serializers.FloatField()


class ProjectStatserializer(ProjectDetailSerializer):
    total_documents_count = serializers.SerializerMethodField()
    reviewed_documents_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['pk', 'name', 'status', 'total_documents_count', 'reviewed_documents_count']

    def get_total_documents_count(self, obj):
        return obj.document_set.filter(delete_pending=False, processed=True).count()
    get_total_documents_count.output_field = serializers.IntegerField()

    def get_reviewed_documents_count(self, obj):
        return obj.document_set.filter(delete_pending=False, processed=True, status__group__is_active=False).count()
    get_reviewed_documents_count.output_field = serializers.IntegerField()


def require_generic_contract_type(func):
    def decorator(cls, *args, **kwargs):
        project = cls.get_object()
        cls.object = project
        if project.type and not project.type.is_generic():
            raise APIException('Allowed for projects with "Generic Contract Type" only')
        return func(cls, *args, **kwargs)

    decorator.__doc__ = func.__doc__
    return decorator


class ProjectPermissions(IsAuthenticated):
    def has_permission(self, request, view):
        if view.action == 'create':
            return request.user.has_perm('project.add_project')
        if view.action == 'project_stats':
            return request.user.has_perm('project.view_project_stats')

        # select_projects - via get_queryset

        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        # Warn! self.get_object() initializes this check! so include it in custom view func!
        user = request.user
        if view.action in ['detect_field_values']:
            return user.has_perm('project.detect_field_values', obj)
        # annotations itself should be filtered by permissions, so no need for additional check
        if view.action in ['retrieve', 'progress', 'tasks', 'active_tasks', 'task_log']:
            return user.has_perm('project.view_project', obj)
        # TODO: make a separate permission on project to view "actions"?
        if view.action in ['update', 'partial_update', 'actions']:
            return user.has_perm('project.change_project', obj)
        # TODO: make a separate permission on project?
        if view.action in ['search_similar_documents', 'search_similar_text_units']:
            return user.has_perm('project.view_project', obj)
        if view.action in ['delete', 'mark_delete', 'unmark_delete', 'cleanup']:
            return user.has_perm('project.delete_project', obj)
        if view.action in ['cluster', 'clustering-status', 'send_clusters_to_project']:
            return user.has_perm('project.recluster_project', obj)
        if view.action in ['set_status']:
            return user.has_perm('project.bulk_update_status', obj)
        if view.action in ['assign_documents', 'assign_annotations',
                           'assignees', 'annotations_assignees']:
            return user.has_perm('project.bulk_assign', obj)
        if view.action in ['assign_document']:
            return user.has_perm('project.individual_assign', obj) or \
                   user.has_perm('project.bulk_assign', obj)
        if view.action == 'set_annotation_status':
            if 'individual' in request.data:
                return user.has_perm('project.view_project', obj)
            return user.has_perm('project.bulk_update_status', obj)

        # TODO: check these:
        # recent - rework SQL - use guardian.shortcuts.get_objects_foe_user

        return super().has_object_permission(request, view, obj)


class ProjectPermissionViewMixin:
    permission_classes = (ProjectPermissions,)

    def get_queryset(self):
        return get_objects_for_user(self.request.user, 'project.view_project', Project) \
            .filter(delete_pending=False)


class ProjectViewSet(apps.common.mixins.APILoggingMixin,
                     ProjectPermissionViewMixin,
                     apps.common.mixins.APIActionMixin,
                     apps.common.mixins.JqListAPIMixin,
                     apps.common.mixins.APIFormFieldsMixin,
                     viewsets.ModelViewSet):
    """
    list: Project List
    retrieve: Retrieve Project
    create: Create Project
    update: Update Project
    partial_update: Partial Update Project
    delete: Delete Project
    """
    options_serializer = ProjectDetailSerializer
    queryset = Project.objects.all()
    track_view_actions = ['create', 'update', 'partial_update', 'cluster', 'retrieve']

    # The actions below should be tracked manually to save non-standard action message/name
    # 'assign_document', 'assign_documents', 'set_status', 'update_document_fields',
    # 'set_annotation_status', 'assign_annotations'

    def perform_create(self, serializer):
        project = super().perform_create(serializer)
        project.owners.add(self.request.user)
        project.reset_project_team_perms()
        return project

    def create(self, request, *args, **kwargs):
        """
        Create Document/TextUnit Vectors if needed
        """
        app_vars = request.data.get('app_vars')
        if app_vars is not None:
            del request.data['app_vars']
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance: Project = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data

        if app_vars is not None:
            self.apply_project_appvars(app_vars, instance, request)

        if app_vars is not None:
            from apps.common.api.v1 import ProjectAppVarSerializer
            app_vars = AppVarStorage.get_project_app_vars(instance.pk, request.user)
            app_var_json = ProjectAppVarSerializer(app_vars, many=True).data
            data['app_vars'] = app_var_json

        # check the term tags and company types are provided
        if not instance.term_tags.exists():
            default_tag = TermTag.objects.get(name=TermTag.DEFAULT_TAG)
            instance.term_tags.add(default_tag)
            instance.save()
        if not instance.companytype_tags.exists():
            default_tag = CompanyTypeTag.objects.get(name=CompanyTypeTag.DEFAULT_TAG)
            instance.companytype_tags.add(default_tag)
            instance.save()

        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """
        Create Document/TextUnit Vectors if needed
        Update ocr_enable project app var if needed
        """
        if 'ocr_enable' in request.data:
            del request.data['ocr_enable']

        _instance = self.get_object()

        app_vars = request.data.get('app_vars')
        if app_vars is not None:
            del request.data['app_vars']

        response = super().update(request, *args, **kwargs)
        instance = Project.objects.get(pk=_instance.pk)

        if app_vars is not None:
            self.apply_project_appvars(app_vars, instance, request)

        if app_vars is not None:
            from apps.common.api.v1 import ProjectAppVarSerializer
            app_vars = AppVarStorage.get_project_app_vars(instance.pk, request.user)
            app_var_json = ProjectAppVarSerializer(app_vars, many=True).data
            response.data['app_vars'] = app_var_json

        return response

    def get_serializer_class(self):
        if self.action == 'create':
            return ProjectCreateSerializer
        if self.action in ['update', 'partial_update']:
            return ProjectUpdateSerializer
        if self.action == 'list':
            return ProjectListSerializer
        if self.action == 'stats':
            return ProjectStatserializer
        if self.action == 'project_stats':
            return ProjectStatsSerializer
        return ProjectDetailSerializer

    def get_project_stats_qs(self, qs):
        annotations = OrderedDict(
            project_id=F('id'),
            type_title=Case(When(type_id=DocumentType.generic_pk(), then=Value('Batch Analysis')),
                            default=F('type__title'), output_field=CharField()),
            documents_total=Count('document', distinct=True),
            avg_ocr_grade=Avg('document__ocr_rating'),
            clauses_total=Count('document__annotations_matches', distinct=True) +
                          Count('document__annotation_false_matches',
                                distinct=True),
            clause_status_rejected=Count('document__annotation_false_matches',
                                         distinct=True))

        def get_ann_name(title, prefix=None, suffix=None):
            res = title.lower().replace(' ', '_')
            if prefix:
                res = f'{prefix}_{res}'
            if suffix:
                res = f'{res}_{suffix}'
            return res

        document_statuses = ReviewStatus.objects.values_list('name', flat=True)
        clause_statuses = FieldAnnotationStatus.objects.values_list('name', 'is_rejected')
        decimal_field = DecimalField(max_digits=5, decimal_places=2)

        for document_status_name in document_statuses:
            # add {status_name_pcnt: decimal} column
            status_col_name = get_ann_name(document_status_name, prefix='document_status')
            annotations[status_col_name] = Count(
                'document',
                filter=Q(document__status__name=document_status_name),
                distinct=True)
            # add {status_name_pcnt: decimal} column
            status_pcnt_col_name = get_ann_name(status_col_name, suffix='pcnt')
            annotations[status_pcnt_col_name] = Case(
                    When(Q(documents_total=0), then=0),
                    default=100.0 * F(status_col_name) / F('documents_total'),
                    output_field=decimal_field)

        for clause_status_name, is_rejected in clause_statuses:
            # add {status_name: int} column
            status_col_name = get_ann_name(clause_status_name, prefix='clause_status')
            relation_name = 'annotation_false_matches' if is_rejected else 'annotations_matches'
            _filter = None if is_rejected else Q(document__annotations_matches__status__name=clause_status_name)
            annotations[status_col_name] = Count(
                f'document__{relation_name}', filter=_filter, distinct=True)
            # add {status_name_pcnt: decimal} column
            status_pcnt_col_name = get_ann_name(status_col_name, suffix='pcnt')
            annotations[status_pcnt_col_name] = Case(
                    When(Q(clauses_total=0), then=0),
                    default=100.0 * F(status_col_name) / F('clauses_total'),
                    output_field=decimal_field)

        qs = qs.annotate(**annotations)
        columns = ['name', 'type'] + list(annotations.keys())

        return qs.values(*columns)

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('type').prefetch_related('status')

        if self.action == 'project_stats':
            qs = self.get_project_stats_qs(qs.order_by('name'))

        elif self.action == 'retrieve':
            qs = qs \
                .select_related('created_by', 'modified_by') \
                .annotate(created_by_name=F('created_by__name'),
                          modified_by_name=F('modified_by__name'))

        elif self.action == 'list':
            # try to fetch document counts in ORM query rather than in serializer method to avoid lots of DB requests
            # CS-6593, see serializer above
            owner_project_ids = get_objects_for_user(
                self.request.user, 'project.view_documents', Project).values_list('id', flat=True)
            owner_documents_subq = Document.objects \
                .filter(project_id=OuterRef('id'), project_id__in=owner_project_ids, processed=True) \
                .order_by('project_id').values('project_id').annotate(c=Count('project_id')).values('c')
            assigned_documents_subq = Document.objects \
                .filter(project_id=OuterRef('id'), assignee=self.request.user, processed=True) \
                .order_by('project_id').values('project_id').annotate(c=Count('project_id')).values('c')
            qs = qs.annotate(
                count_of_documents=Case(
                    When(id__in=owner_project_ids, then=Subquery(owner_documents_subq, output_field=IntegerField())),
                    default=Subquery(assigned_documents_subq, output_field=IntegerField())))

        elif self.action not in ['list', 'project_stats']:
            qs = qs.prefetch_related('owners',
                                     'super_reviewers',
                                     'junior_reviewers',
                                     'reviewers')
        else:
            pass
            # qs = qs.annotate(count_of_documents=Count('document'))
        return qs

    def get_extra_data(self, queryset, initial_queryset):
        return {'available_statuses': common_api_module.ReviewStatusSerializer(
            ReviewStatus.objects.select_related('group'), many=True).data}

    def apply_project_appvars(self,
                              app_vars: List[Dict[str, Any]],
                              instance: Project,
                              request):
        user_id = request.user.pk if request.user else None
        from apps.common.api.v1 import ProjectAppVarSerializer
        app_var_list = ProjectAppVarSerializer.deserialize(app_vars)
        AppVarStorage.apply_project_app_vars(instance.pk, app_var_list, user_id)

    @action(detail=True, methods=['get'], schema=ProjectProgressSchema())
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

    @staticmethod
    def _cluster(project, user_id=None, n_clusters=3, method='kmeans', cluster_by='term'):

        project.drop_clusters()
        project_clustering = ProjectClustering.objects.create(project=project)

        task_id = call_task(
            ClusterProjectDocuments,
            user_id=user_id,
            project_id=project.id,
            project_clustering_id=project_clustering.id,
            method=method,
            metadata={'project_id': project.id},
            cluster_by=cluster_by,
            n_clusters=n_clusters)

        return {'task_id': task_id, 'project_clustering_id': project_clustering.id}

    @require_generic_contract_type
    def cluster(self, request, **kwargs):
        """
        Cluster Project Documents\n
            Params:
                - method: str[KMeans, MiniBatchKMeans, Birch, DBSCAN]
                - cluster_by: str[term, date, text, definition, duration, party,
                                  geoentity, currency_name, currency_value]
                - n_clusters: int
                - force: bool (optional) - force clustering if uncompleted tasks exist
        """
        project = getattr(self, 'object', None) or self.get_object()
        force = request.data.get('force') == 'true'

        task = Task.objects.filter(name=ClusterProjectDocuments.name,
                                   status=PENDING,
                                   kwargs__project_id=project.id).last()
        if task is not None:
            if force:
                purge_task(task.pk)
            else:
                data = {'task_id': task.pk,
                        'project_clustering_id': task.kwargs.get('project_clustering_id')}
                return Response(data)

        if not force:
            if project.uploadsession_set.filter(completed=False).exists():
                raise APIException('Project has uncompleted upload sessions.')
            if not project.uploadsession_set.filter(completed=True).exists():
                raise APIException("Project hasn't completed upload sessions.")

        if request.data.get('require_confirmation'):
            cluster_params = {
                'do_cluster_documents': True,
                'project': project
            }
            count, count_limit = Cluster.estimate_reaching_limit(cluster_params)
            if count > count_limit:
                return Response({'message': 'Processing large amounts of documents may take a long time.',
                                 'confirm': True})

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

        res = self._cluster(project,
                            user_id=request.user.id,
                            n_clusters=n_clusters,
                            method=request.data.get('method', 'kmeans'),
                            cluster_by=cluster_by)
        return Response(res)

    def search_similar(self, request, task, transformer_id_field):
        project = self.get_object()
        data = self.schema.request_serializer.__class__(data=request.data)
        if not data.is_valid():
            return Response(data.errors, status=400)
        data = data.data
        data['project'] = project.id
        data['user_id'] = request.user.id
        if 'selection' in data:
            # we got location of the annotation as coordinates
            selection = data['selection']
            location = CoordTextMap.get_text_location_by_coords(
                data['document_id'], selection)
            data['location_start'] = location[0]
            data['location_end'] = location[1]

        # get feature_source and optional transformer_id
        transformer_id = getattr(project, transformer_id_field)
        if transformer_id:
            data['feature_source'] = 'vector'
            data['transformer_id'] = transformer_id
        else:
            data['feature_source'] = 'term'
        task_id = call_task(task, **data)
        return Response({'task_id': task_id})

    @action(detail=True, methods=['post'], schema=ProjectSearchSimilarDocumentsSchema())
    def search_similar_documents(self, request, **kwargs):
        from apps.similarity.tasks import DocumentSimilarityByFeatures
        return self.search_similar(request,
                                   task=DocumentSimilarityByFeatures,
                                   transformer_id_field='document_transformer_id')

    @action(detail=True, methods=['post'], schema=ProjectSearchSimilarTextUnitsSchema())
    def search_similar_text_units(self, request, **kwargs):
        from apps.similarity.tasks import TextUnitSimilarityByFeatures
        return self.search_similar(request,
                                   task=TextUnitSimilarityByFeatures,
                                   transformer_id_field='text_unit_transformer_id')

    def delete_similarity_task_results(self, request, task):
        project = self.get_object()
        task_id = call_task(task, project_id=project.id, user_id=request.user.id)
        return Response({'task_id': task_id})

    @action(detail=True, methods=['delete'])
    def delete_document_similarity_results(self, request, **kwargs):
        from apps.similarity.tasks import DeleteDocumentSimilarityResults
        return self.delete_similarity_task_results(request, task=DeleteDocumentSimilarityResults)

    @action(detail=True, methods=['delete'])
    def delete_text_unit_similarity_results(self, request, **kwargs):
        from apps.similarity.tasks import DeleteTextUnitSimilarityResults
        return self.delete_similarity_task_results(request, task=DeleteTextUnitSimilarityResults)

    @action(detail=True, methods=['get'], schema=ProjectTasksSchema())
    def tasks(self, request, **kwargs):
        from apps.task.api.v1 import TaskViewSet
        view = TaskViewSet(request=self.request, kwargs={'project_id': kwargs['pk']},
                           format_kwarg='project_id', action='project_tasks')
        view.permission_classes = []
        return view.project_tasks(self.request, project_id=kwargs['pk'])

    @action(detail=True, methods=['get'], schema=ProjectActiveTasksSchema())
    def active_tasks(self, request, **kwargs):
        from apps.task.api.v1 import TaskViewSet
        view = TaskViewSet(request=self.request, kwargs={'project_id': kwargs['pk']},
                           format_kwarg='project_id', action='project_active_tasks')
        view.permission_classes = []
        return view.project_active_tasks(self.request, project_id=kwargs['pk'])

    @action(detail=True, methods=['get'], schema=ProjectTaskLogSchema(), url_path=r'task/(?P<task_id>[\w-]+)/task-logs')
    def task_log(self, request, **kwargs):
        from apps.task.api.v1 import TaskLogAPIView
        self.request.GET._mutable = True
        self.request.GET['task_id'] = kwargs['task_id']
        self.request.GET._mutable = False
        view = TaskLogAPIView(request=self.request, action='project_task_logs')
        view.permission_classes = []
        return view.get(self.request)

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

        # update project clustering status based on task status
        clustering.set_status_by_task()

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

    @action(detail=True, methods=['post'], url_path='send-clusters-to-project', schema=SendClusterToProjectSchema())
    # @require_generic_contract_type
    def send_clusters_to_project(self, request, **kwargs):
        """
        Send clusters to another Project\n
            Params:
                - cluster_ids: list[int]
                - project_id: int
        """
        project = self.get_object()

        # via API
        if isinstance(request.data, QueryDict):
            cluster_ids = [int(i) for i in request.data.getlist('cluster_ids')]
        # via swagger or SDK
        else:
            cluster_ids = request.data['cluster_ids']

        project_clustering = project.projectclustering_set.last()
        if not project_clustering:
            raise APIException('Project Clustering object not found')
        reassigned_cluster_ids = project_clustering.metadata.get('reassigned_cluster_ids', [])
        already_reassigned_clusters = set(cluster_ids) & set(reassigned_cluster_ids)
        if already_reassigned_clusters:
            raise APIException('Cluster(s) id=({}) is/are already reassigned to another project'
                               .format(', '.join(str(i) for i in already_reassigned_clusters)))

        new_project_id = int(request.data['project_id'])
        call_task(
            ReassignProjectClusterDocuments,
            project_clustering_id=project_clustering.id,
            cluster_ids=cluster_ids,
            project_id=project.id,
            new_project_id=new_project_id,
            user_id=request.user.id)

        return Response('OK')

    @action(detail=True, methods=['post'], schema=CleanupProjectSchema())
    # @require_generic_contract_type
    def cleanup(self, request, **kwargs):
        """
        Clean project (Generic Contract Type project)
        """
        _ = self.get_object()    # init obj perms

        delete = request.data.get('delete', True)
        # for swagger or SDK
        if isinstance(delete, str):
            delete = json.loads(delete)

        call_task(
            CleanProject,
            _project_id=int(kwargs['pk']),
            delete=delete,
            user_id=request.user.id)

        return Response('OK')

    @action(detail=False, methods=['get'], schema=ProjectStatsSchema())
    def project_stats(self, request, **kwargs):
        """
        Get project stats across all projects
        see related code in get_queryset() and serializer
        """
        return super().list(request, **kwargs)

    @action(detail=False, methods=['post'], schema=SelectProjectsSchema())
    def select_projects(self, request, **kwargs):
        """
        Select projects for review in Explorer UI
        """
        qs = self.get_queryset()
        received_project_ids = request.data.get('project_ids')
        allowed_project_ids = qs.filter(pk__in=received_project_ids).values_list('pk', flat=True)
        obj, _ = UserProjectsSavedFilter.objects.get_or_create(user=request.user)
        obj.projects.set(allowed_project_ids)

        ret = dict(
            saved_filter_id=obj.id,
            user_id=request.user.id,
            project_ids=obj.projects.values_list('id', flat=True),
            show_warning=not obj.projects.exists()
        )
        return Response(ret)

    @action(detail=True, methods=['post'], schema=MarkUnmarkForDeleteProjectsSchema())
    def mark_delete(self, request, **kwargs):
        """
        Method marks the whole project (remove_all=True) / the project's documents (remove_all=False)
        for deleting. These marked documents (and the project) will become hidden in API.
        Documents, listed in excluded_ids list, will not be marked for deleting.\n
            Params:
                - all: bool - mark all filtered by a user documents
                - remove_all: bool - mark project+documents
                - exclude_document_ids: list[int]
        """
        return self.mark_unmark_for_delete(True, request, **kwargs)

    @action(detail=True, methods=['post'], schema=MarkUnmarkForDeleteProjectsSchema())
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
            if delete_pending:
                project_soft_deleted.send(sender='Project marked Soft Deleted', instance=proj, user=request.user)
        return Response({"count_deleted": count_deleted}, status=200)

    @action(detail=True, methods=['get'], schema=ProjectDocumentsAssigneesSchema())
    def assignees(self, request, **kwargs):
        """
        Get assignees data
        """
        # permissions check
        project = self.get_object()

        result = []
        # TODO: optimize
        for user in project.available_assignees:
            docs = project.document_set.filter(assignee=user)
            result.append({
                'assignee_id': user.id,
                'assignee_name': user.name,
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

    def get_document_ids(self, request):
        """
        Method to apply "document_ids", "no_document_ids" and "all" filters
        using SavedFilter from rawdb.DocumentsAPIView
        """
        if request.data.get('all'):
            documents = self.get_document_queryset()
            if request.data.get('no_document_ids'):
                documents = documents.exclude(pk__in=request.data.get('no_document_ids'))
            return documents.values_list('pk', flat=True)
        return request.data.get('document_ids')

    def save_mass_action(self, action_name, action_message, document_ids, request_data=None, cache_documents=False):
        date = now()
        actions = [Action(name=action_name,
                          message=action_message,
                          view_action=self.action,
                          user=self.request.user,
                          date=date,
                          content_type=ContentType.objects.get_for_model(Document),
                          object_pk=doc_id,
                          model_name='Document',
                          app_label='document',
                          request_data=request_data or self.request.data)
                   for doc_id in document_ids]
        Action.objects.bulk_create(actions)
        Document.objects.filter(pk__in=document_ids).update(modified_by=self.request.user, modified_date=date)

        # cache document modified_date/modified_by only
        if cache_documents:
            from apps.document.tasks import plan_process_document_changed
            for doc_id in document_ids:
                plan_process_document_changed(doc_id,
                                              system_fields_changed=['modified_date', 'modified_by'],
                                              generic_fields_changed=False,
                                              user_fields_changed=False,
                                              changed_by_user_id=self.request.user.id)

    @action(detail=True, methods=['post'], schema=UpdateProjectDocumentsFieldsSchema())
    def update_document_fields(self, request, *args, **kwargs):
        """
        Bulk update project documents field, similar to /fields/ API in document app\n
            Params:
                document_ids: list[int]
                all: any value - update all documents if any value
                no_document_ids: list[int] - exclude those docs from action (if "all" is set)
                fields_data: - dict {field_code: [values]}
                on_existing_value: "replace_all" | "add_new" (for multi-choice fields)
            Returns:
                task_id
        """
        document_ids = self.get_document_ids(request)
        if not document_ids:
            raise APIException('document_ids not found')
        fields_data = request.data.get('fields_data')
        if not fields_data:
            raise APIException('fields_data not found')

        task_id = call_task(
            UpdateProjectDocumentsFields,
            document_ids=document_ids,
            project_id=kwargs['pk'],
            fields_data=request.data['fields_data'],
            on_existing_value=request.data.get('on_existing_value'),
            user_id=request.user.pk)

        # TODO: move into task? OR just count an attempt?
        msg_tip = ', '.join([f'"{field_code}" to "{value}"' for field_code, value in fields_data.items()])
        self.save_mass_action(action_name='Field Value Changed',
                              action_message=f'Document fields bulk changed: {msg_tip}',
                              document_ids=document_ids,
                              request_data=request.data['fields_data'])

        return Response({'task_id': task_id})

    @action(detail=True, methods=['post'], schema=AssignProjectDocumentsSchema())
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
        project = self.get_object()    # noqa: permissions check
        assignee_id = request.data.get('assignee_id')
        document_ids = self.get_document_ids(request)
        return self.assign_multiple_documents(assignee_id, project, request.user.pk, document_ids)

    @action(detail=True, methods=['post'], schema=AssignProjectDocumentSchema())
    def assign_document(self, request, **kwargs):
        """
        Bulk assign batch of documents to a review team member\n
            Params:
                document_id: int
                assignee_id: int
            Returns:
                bool (number of reassigned documents)
        """
        project = self.get_object()  # noqa: permissions check
        assignee_id = request.data.get('assignee_id')
        document_ids = [request.data.get('document_id')]
        return self.assign_multiple_documents(assignee_id, project, request.user.pk, document_ids)

    def assign_multiple_documents(self,
                                  assignee_id: int,
                                  project: Project,
                                  changed_by_id: int,
                                  document_ids: List[int]):
        assignee = User.objects.get(pk=assignee_id) if assignee_id is not None else None
        if assignee is not None:
            if not assignee.has_perm('view_project', project):
                return Response(
                    {'detail': f'This assignee #{assignee.pk} has no permission to view this project'},
                    status=404)
        # FIXME: moved into Document model's pre_update
        # change perms for documents
        plan_process_documents_assignee_changed(doc_ids=document_ids,
                                                new_assignee_id=assignee_id,
                                                changed_by_user_id=changed_by_id)

        # TODO: move into task? OR just count an attempt?
        self.save_mass_action(action_name='Assignee Changed',
                              action_message=f'Document assignee bulk changed to "{assignee.name if assignee else None}"',
                              document_ids=document_ids)
        return Response({'success': len(document_ids)})

    @action(detail=True, methods=['post'], schema=SetProjectDocumentsStatusSchema())
    def set_status(self, request, **kwargs):
        """
        Bulk set status for batch of documents\n
            Params:
                document_ids: list[int]
                no_document_ids: list[int] - exclude those docs from action (if "all" is set)
                all: any value - update all documents if any value
                status_id: int
            Returns:
                int (number of reassigned documents)
        """
        # permissions check
        project = self.get_object()
        status_id = request.data.get('status_id')

        document_ids = self.get_document_ids(request)
        documents = Document.objects.filter(project=project, pk__in=document_ids)

        import apps.document.repository.document_field_repository as dfr
        field_repo = dfr.DocumentFieldRepository()

        with transaction.atomic():
            review_status = ReviewStatus.objects.get(pk=status_id)
            modified_fields = field_repo.get_modified_field_ids(documents, review_status.is_active)
            DocumentField.objects.filter(pk__in=Subquery(modified_fields)).update(dirty=True)
            ret = documents.update(status=status_id)

            # set Unreviewed annotations to Accepted
            if review_status.is_final:
                ann_final_status = FieldAnnotationStatus.accepted_status()
                field_repo.update_field_annotations_by_doc_ids(
                    document_ids, [(f'{FIELD_CODE_STATUS_ID}', ann_final_status.pk)])

        plan_process_documents_status_changed(document_ids, status_id, request.user.pk)

        # TODO: move into task? OR just count an attempt?
        self.save_mass_action(action_name='Status Changed',
                              action_message=f'Document status bulk changed to "{review_status.name}"',
                              document_ids=document_ids)
        return Response({'success': ret})

    def get_annotations_queryset(self, only_true_annotations=False):
        """
        Get project annotations using SavedFilter logic to filter out FieldAnnotations*
        """
        project = self.get_object()

        request = HttpRequest()
        request.user = self.request.user
        request.GET = self.request.data

        from apps.document.api.v1 import DocumentFieldAnnotationViewSet as api_view
        view = api_view(request=request, kwargs={'project_pk': project.pk})
        view.action = 'list'

        qs = view.get_queryset(only_true_annotations=only_true_annotations)

        return qs

    @action(detail=True, methods=['get'], schema=ProjectAnnotationsAssigneesSchema())
    def annotations_assignees(self, request, **kwargs):
        """
        Get assignees data for FieldAnnotations
        """
        # permissions check
        _ = self.get_object()

        # get only "true" annotations as "false" annotations don't have assignee field
        annotation_qs = self.get_annotations_queryset(only_true_annotations=True).values('assignee_id', 'uid')

        assignee_ids = {i['assignee_id'] for i in annotation_qs if i['assignee_id']}

        result = []
        for user in User.objects.filter(pk__in=assignee_ids):
            user_annotation_uids = [i['uid'] for i in annotation_qs if i['assignee_id'] == user.id]
            result.append({
                'assignee_id': user.id,
                'assignee_name': user.name,
                'annotations_count': len(user_annotation_uids),
                'annotation_uids': sorted(user_annotation_uids)})
        return Response(result)

    @action(detail=True, methods=['post'], schema=AssignProjectAnnotationsSchema())
    def assign_annotations(self, request, **kwargs):
        """
        Bulk assign batch of annotations to a review team member\n
            Params:
                annotation_ids: list[int]
                all: any value - update all annotations if any value
                no_annotation_ids: list[int] - exclude those annotations from action (if "all" is set)
                assignee_id: int
            Returns:
                int (number of reassigned annotations)
        """
        project = self.get_object()    # noqa: permissions check
        assignee_id = request.data.get('assignee_id')

        if assignee_id is not None and \
                assignee_id not in project.get_team().values_list('id', flat=True):
            return Response({'detail': f'This assignee (id={assignee_id}) is not in project owners or reviewers'},
                            status=404)

        annotations = self.get_annotations_queryset()

        # re-fetch annotations as initial values-qs doesn't allow update
        ant_uids = [i['uid'] for i in annotations]
        print(f'Updating {len(ant_uids)} annotations')
        field_repo = DocumentFieldRepository()
        field_repo.update_field_annotations_by_ant_ids(
            ant_uids, [(FIELD_CODE_ASSIGNEE_ID, assignee_id or 'null'),
                       (FIELD_CODE_ASSIGN_DATE, f"'{now().isoformat()}'")],
            update_false_matches=True)

        document_ids = {i['document_id'] for i in annotations}
        assignee_name = User.objects.get(id=assignee_id).name if assignee_id else None
        self.save_mass_action(action_name='Field Annotation Changed',
                              action_message=f'Document Annotation assignee bulk changed to "{assignee_name}"',
                              document_ids=document_ids,
                              cache_documents=True)
        return Response({'success': annotations.count()})

    @action(detail=True, methods=['post'], schema=SetProjectAnnotationsStatusSchema())
    def set_annotation_status(self, request, **kwargs):
        """
        Bulk set status for batch of annotations\n
            Params:
                document_ids: list[int]
                all: any value - update all annotations if any value
                no_annotation_ids: list[int] - exclude those annotations from action (if "all" is set)
                status_id: int - field annotation status id
                run_mode: str - 'sync', 'background', 'smart'
            Returns:
                int (number of reassigned annotations)
        """
        MAX_ANTS_TO_RUN_SYNC = 20
        self.get_object()    # noqa: permissions check
        # "sync" - process request in foreground
        # "background" - process request in background as a separate Celery task
        # "smart" - process request in foreground if there are less than N annotations found
        run_mode = request.data.get('run_mode') or 'sync'
        status_id = request.data.get('status_id')
        annotations = self.get_annotations_queryset()
        # re-fetch annotations as initial values-qs doesn't allow update
        ant_uids = [i['uid'] for i in annotations]

        except_true_ann = FieldAnnotation.objects \
            .filter(uid__in=ant_uids, document__status__code='completed') \
            .values_list('uid', flat=True)
        except_false_ann = FieldAnnotationFalseMatch.objects \
            .filter(uid__in=ant_uids, document__status__code='completed') \
            .values_list('uid', flat=True)
        ant_uids = [i for i in ant_uids if i not in except_true_ann and i not in except_false_ann]

        run_sync = run_mode == 'sync'
        if not run_sync:
            run_sync = run_mode == 'smart' and len(ant_uids) < MAX_ANTS_TO_RUN_SYNC

        # TODO: move into task? OR just count an attempt?
        document_ids = {i['document_id'] for i in annotations}
        status_name = FieldAnnotationStatus.objects.get(id=status_id).name
        self.save_mass_action(action_name='Field Annotation Changed',
                              action_message=f'Document Annotation status bulk changed to "{status_name}"',
                              document_ids=document_ids,
                              cache_documents=True)

        if run_sync:
            sync_task = SetAnnotationsStatus()
            sync_task.process(ids=ant_uids,
                              status_id=status_id,
                              user_id=request.user.pk)
            return Response({'success': len(ant_uids)})

        task_id = call_task(
            SetAnnotationsStatus,
            ids=ant_uids,
            status_id=status_id,
            user_id=request.user.pk)

        return Response({'task_id': task_id, 'annotations': len(ant_uids)})

    @action(detail=False, methods=['get'], schema=RecentProjectsSchema())
    def recent(self, request, **kwargs):
        """
        Get recent N projects\n
            Params:
                n: int - default is 5
        """
        last_n = int(request.GET.get('n', 5))
        content_type_id = ContentType.objects.get_for_model(Project).id
        user = request.user

        user_projects = user.user_projects
        if not user_projects.exists():
            return Response([])

        sql = '''
            SELECT
              p1.id project_id,
              p1.name project_name,
              CASE WHEN p1.type_id = %s THEN TRUE ELSE FALSE END AS is_generic,
              (SELECT count(d1.id)
               FROM document_document d1
               WHERE d1.id in ({document_ids}) 
                   AND d1.delete_pending = FALSE
                   AND d1.processed = TRUE 
                   AND d1.project_id = p1.id) extracted_doc_count,
              (SELECT count(d2.id)
               FROM document_document d2
               WHERE d2.id in ({document_ids}) 
                   AND d2.delete_pending = FALSE
                   AND d2.processed = TRUE 
                   AND d2.project_id = p1.id 
                   AND d2.status_id IN (SELECT rs.id
                                        FROM common_reviewstatus rs INNER JOIN common_reviewstatusgroup rsg
                                            ON rs.group_id = rsg.id
                                        WHERE rsg.is_active = FALSE)) reviewed_doc_count
            FROM project_project p1
            INNER JOIN common_action ca
                ON NOT p1.delete_pending AND ca.content_type_id = %s AND ca.user_id = %s AND ca.object_pk = p1.id :: VARCHAR
            WHERE p1.delete_pending = FALSE AND p1.id in ({project_ids})
            GROUP BY p1.id
            ORDER BY max(ca.date) DESC
            LIMIT %s
        '''.format(document_ids=','.join([str(i) for i in user.user_document_ids]) or 0,
                   project_ids=','.join([str(i) for i in user_projects.values_list('pk', flat=True)]))

        result = []
        with connection.cursor() as cursor:
            cursor.execute(sql, [DOCUMENT_TYPE_PK_GENERIC_DOCUMENT, content_type_id, user.id, last_n])
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

    @action(detail=True, methods=['post'], schema=DetectProjectFieldValuesSchema())
    def detect_field_values(self, request, **kwargs):
        project = getattr(self, 'object', None) or self.get_object()  # type: Project
        do_not_update_modified = request.data.get('do_not_update_modified')
        if do_not_update_modified is None:
            do_not_update_modified = True
        do_not_write = request.data.get('do_not_write') or False
        document_ids = request.data.get('document_ids')

        task_id = call_task(
            DetectFieldValues,
            user_id=request.user.id,
            document_type=project.type,
            project_ids=[project.pk],
            do_not_write=do_not_write,
            existing_data_action='maintain' if do_not_update_modified else 'delete',
            document_ids=document_ids)

        return Response({'task_id': task_id})

    @action(detail=True, methods=['post'])
    def locate_items(self, request, **kwargs):
        items_to_locate = request.data.get('items_to_locate', [])  # i.e. ['term']
        if not items_to_locate:
            raise ValueError('"items_to_locate" argument missed', 'items_to_locate')
        project_id = request.data.get('project_id')
        if not project_id:
            raise ValueError('"project_id" argument missed', 'project_id')
        delete_existing = request.data.get('delete_existing', True)
        search_in = request.data.get('search_in', ['sentence'])

        task_id = call_task(
            'Locate',
            tasks={t: {'locate': True, 'delete': delete_existing} for t in items_to_locate},
            parse=search_in,
            user_id=request.user.pk,
            project_id=int(project_id),
            selected_tags=request.data.get('selected_tags'))
        return Response({'task_id': task_id}, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset):
        # do not apply passed JQ filters for parent object (Project) - pass them into child view only
        if self.action in ['settings_actions', 'cluster_actions', 'tasks']:
            self.skip_jq_filters = True
        return super().filter_queryset(queryset)

    # actions

    def save_action_parent(self):
        # sync created/modified fields with action object
        if self.action in ['retrieve', 'cluster']:
            return
        obj = self.user_action.object
        if not obj:
            return
        if self.action == 'create':
            obj.created_by = self.user_action.user
            obj.created_date = self.user_action.date
        obj.modified_by = self.user_action.user
        obj.modified_date = self.user_action.date
        obj.save()

    @staticmethod
    def get_object_state(obj):
        obj_state = dict()
        for field in obj._meta.fields:
            field_name = field.name
            # avoid loading whole transformer.model_object - it takes much time
            if field_name in ['document_transformer', 'text_unit_transformer']:
                field_name += '_id'
            obj_state[field.name] = getattr(obj, field_name)
        for field in obj._meta.many_to_many:
            obj_state[field.name] = list(getattr(obj, field.name).order_by('pk'))
        return obj_state

    def get_action_name(self):
        if self.action == 'cluster':
            return 'Cluster Project'
        return super().get_action_name()

    def get_action_message(self):
        if self.action == 'cluster':
            return f'Cluster Project with parameters: {dict(self.request.data)}'
        return super().get_action_message()

    def get_updated_fields_message(self, old_instance_state, new_instance_state):
        """
        Create description for updated fields
        :param old_instance_state: dict
        :param new_instance_state: dict
        """
        changes = []
        for field in old_instance_state:
            old_field_value = old_instance_state[field]
            new_field_value = new_instance_state[field]
            if old_field_value != new_field_value:
                if field in ['owners', 'reviewers', 'super_reviewers', 'junior_reviewers']:
                    added = set(new_field_value).difference(old_field_value)
                    for user in added:
                        changes.append(f'User "{user.name}" added to Project\'s "{cap_words(field)}"')
                    removed = set(old_field_value).difference(new_field_value)
                    for user in removed:
                        changes.append(f'User "{user.name}" removed from Project\'s "{cap_words(field)}"')
                    continue
                if field in ['document_transformer', 'text_unit_transformer']:
                    old_field_value = f'#{old_field_value}' if old_field_value else None
                    new_field_value = f'#{new_field_value}' if new_field_value else None
                    field = cap_words(field)
                else:
                    field = f'field "{field}"'
                changes.append(
                    f'{self.model_name} {field} changed '
                    f'from "{old_field_value}" '
                    f'to "{new_field_value}"')
        if changes:
            return ', '.join(changes)

    def actions(self, view_action_names):
        project = self.get_object()    # project permissions check goes in get_object
        # re-use ActionViewSet to handle jq-widgets-like filter/sort/pagination
        view = ActionViewSet(request=self.request,
                             kwargs={'project_id': project.pk,
                                     'view_actions': view_action_names,
                                     # 'init_action': 'create'
                                     })
        view.action = 'list'
        view.permission_classes = []
        view.format_kwarg = {}
        data = view.list(self.request)
        return data

    @action(detail=True, methods=['get'], schema=ActionViewSchema())
    def settings_actions(self, request, **kwargs):
        return self.actions(view_action_names=['create', 'update', 'partial_update'])

    @action(detail=True, methods=['get'], schema=ActionViewSchema())
    def cluster_actions(self, request, **kwargs):
        return self.actions(view_action_names=['cluster'])


class LocaleAPIViewSchema(AutoSchema):
    def get_responses(self, path, method):
        response = {'200': object_list_content,
                    '500': string_content}
        return response


class LocaleListView(APIView):
    permission_classes = (IsAuthenticated, )
    schema = LocaleAPIViewSchema()

    def get(self, request, *args, **kwargs):
        return Response(self.represent_data(settings.LOCALES))

    def represent_data(self, data: dict):
        representation = {"data": []}
        for locale, title in data.items():
            try:
                lng, loc = locale.split("_")
                lng_title, loc_title = title.split(" / ")
            except ValueError:
                continue

            representation["data"].append({
                "language_code": lng,
                "locale_code": loc,
                "full_code": locale,
                "language": lng_title,
                "locale": loc_title,
            })
        return representation


# --------------------------------------------------------
# UploadSession Views
# --------------------------------------------------------

class UploadSessionCreateSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), many=False, required=False)
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=False, required=False)
    upload_files = serializers.DictField(required=False, read_only=True)
    review_files = serializers.BooleanField(required=False, read_only=True)
    force = serializers.BooleanField(required=False, read_only=True)

    class Meta:
        model = UploadSession
        fields = ['uid', 'project', 'created_by', 'upload_files', 'review_files', 'force']


class UploadSessionUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = UploadSession
        fields = ['pk', 'project', 'created_by', 'created_date', 'completed']


class UploadSessionDetailSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(many=False)
    # project = ProjectDetailSerializer(many=False, required=False)
    document_type = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    is_canceling = serializers.SerializerMethodField()

    class Meta:
        model = UploadSession
        fields = ['uid', 'project', 'created_by', 'created_date',
                  'document_type', 'progress', 'completed', 'is_canceling']

    def get_progress(self, obj):
        return obj.document_tasks_progress(details=True)

    def get_document_type(self, obj):
        return DocumentTypeSerializer(obj.project.type, many=False).data if obj.project else None

    def get_is_canceling(self, obj: UploadSession):
        return Task.objects.filter(upload_session_id=obj.pk, name='Cancel Upload', status=PENDING).exists()


class UploadSessionPermissions(IsAuthenticated):

    def has_permission(self, request, view):
        if view.action in ['create']:

            # otherwise schema generations fails
            if 'project' in request.data:
                project = Project.objects.get(pk=request.data['project'])
                return request.user.has_perm('project.add_project_document', project)
            return request.user.has_perm('project.add_uploadsession')

        # status - filter via get_queryset

        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        action = view.action
        user = request.user
        if action in ['update']:
            return user.has_perm('project.change_project', obj.project)
        if action in ['destroy']:
            return user.has_perm('project.delete_project', obj.project)
        if action in ['upload', 'batch_upload', '_batch_upload', 'files', 'progress',
                      'cancel_upload', 'delete_file', 'partial_update']:
            return user.has_perm('project.add_project_document', obj.project)
        return super().has_object_permission(request, view, obj)


class UploadSessionPermissionViewMixin:
    permission_classes = (UploadSessionPermissions,)

    def get_queryset(self):
        qs = super().get_queryset()
        projects = get_objects_for_user(self.request.user, 'project.add_project_document', Project)
        qs = qs.filter(project_id__in=projects.values_list('pk', flat=True))
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
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'create':
            return UploadSessionCreateSerializer
        if self.action in ['update', 'partial_update']:
            return UploadSessionUpdateSerializer
        return UploadSessionDetailSerializer

    @staticmethod
    @transaction.atomic
    def can_upload_file(project: Project,
                        file_name: str,
                        file_size: Optional[int],
                        upload_session_id: str = None):
        """
        Check whether a file is new and should be uploaded
        :param project: Project
        :param file_name: file name
        :param file_size: file size in bytes
        :param upload_session_id: uid, None in case if reassign_cluster task
        :return: bool
        """
        # o. empty document
        if not file_size:
            return 'empty'

        # 1.1 if a document is duplicated in current session (except check in ReassignProjectClusterDocuments task)
        if upload_session_id:
            similar_documents_task_query = Task.objects.main_tasks().filter(
                name=LoadDocuments.name,
                upload_session_id=upload_session_id,
                metadata__file_name=file_name)
            if file_size is not None:
                similar_documents_task_query = similar_documents_task_query.filter(metadata__file_size=file_size)
            if similar_documents_task_query.exists():
                return 'duplicate_in_this_session'

        # 1.2 if a Document of file name and size already uploaded and parsed
        doc_query = Document.objects.filter(
            project=project,
            name=file_name,
            processed=True)
        if file_size is not None:
            doc_query = doc_query.filter(file_size=file_size)
        if doc_query.exists():
            return 'exists'

        # 2. if a Document of file name and size already uploaded and parsed BUT soft-deleted
        doc_query = Document.all_objects.filter(
            delete_pending=True,
            project=project,
            name=file_name,
            processed=True)
        if file_size is not None:
            doc_query = doc_query.filter(file_size=file_size)
        if doc_query.exists():
            return 'delete_pending'

        # 3. if a Document is not created yet or processed=True is not set yet
        # so parsing is in progress
        # and Task for file name and size exists with appropriate status
        task_query = Task.objects.main_tasks().filter(
            name=LoadDocuments.name,
            upload_session__project=project,
            metadata__file_name=file_name,
            status__in=(PENDING,))
        if file_size is not None:
            task_query = task_query.filter(metadata__file_size=file_size)
        if task_query.exists():
            return 'processing'

        # 4.1. if task has completed at this moment and that's why step#1 was missed
        # 4.2. if Task exists but document was reassigned to another project
        task_query = Task.objects.main_tasks().filter(
            name=LoadDocuments.name,
            upload_session__project=project,
            metadata__file_name=file_name,
            status__in=(SUCCESS,))
        if file_size is not None:
            task_query = task_query.filter(metadata__file_size=file_size)

        if task_query.exists():
            doc_query = Document.objects.filter(
                project=project,
                name=file_name,
                documentmetadata__metadata__upload_status='DONE')
            if file_size is not None:
                doc_query = doc_query.filter(file_size=file_size)
            if doc_query.exists():
                return 'exists'

        # 5. VERY RARE: if a file of name and size already exists but LD Task is not created yet
        # but LD Task object itself is created immediately after storing a file
        # So - skipping this check, load: True

        # 6. Other RARE cases:
        #     a) size doesn't match:
        #         - if a Document exists: it's another document, load: True
        #         - elif a Task exists: it's another document, load: True
        #         - else:
        #             = it's another document - load: True
        #             = it's the same document, in storing on disk process - load: False (TODO)
        #             = it's the same document but uploading was interrupted - load: True

        # 7. LD Task has FAILURE status, document has processed=False, but DeleteDocument task failed FSR as well
        # just allow to upload the same document - TODO: check possible issues

        # since we does double check in /upload method, - skip RARE cases for now
        return True

    def create(self, request, *args, **kwargs):
        project = Project.objects.get(pk=request.data.get('project'))
        response = super().create(request, *args, **kwargs)

        # TODO: leave "upload_files" only / talk with FE
        upload_files = request.data.pop('upload_files', None)
        review_files = request.data.pop('review_files', False)

        upload_session_id = response.data['uid']

        if upload_files and review_files:

            force_rename = request.data.get('force') or request.META.get('HTTP_FORCE', False) == 'true'

            if force_rename is None:
                from apps.document.app_vars import ALLOW_DUPLICATE_DOCS
                force_rename = not ALLOW_DUPLICATE_DOCS.val(project_id=project.id)

            do_upload_files = {}
            upload_unique_files = []
            exists = []
            delete_pending = []
            processing = []
            empty = []
            duplicate_in_this_session = []

            for file_path, file_size in upload_files.items():
                file_name = os.path.basename(file_path)
                status = self.can_upload_file(project, os.path.basename(file_path), file_size, upload_session_id)

                if (force_rename and status not in {'delete_pending', 'empty'}) or \
                        (status is True and (file_name, file_size) not in upload_unique_files):
                    do_upload_files[file_path] = True
                    upload_unique_files.append((file_name, file_size))
                else:
                    do_upload_files[file_path] = False
                    if status == 'duplicate_in_this_session':
                        duplicate_in_this_session.append(file_path)
                    elif status == 'exists':
                        exists.append(file_path)
                    elif status == 'delete_pending':
                        delete_pending.append(file_path)
                    elif status == 'processing':
                        processing.append(file_path)
                    elif status == 'empty':
                        empty.append(file_path)

            data = dict(
                upload_files=do_upload_files,
                exists=exists,
                delete_pending=delete_pending,
                processing=processing,
                empty=empty
            )
            response.data.update(data)

        call_task_func(track_session_completed, (), request.user.pk)
        return response

    @action(detail=True, methods=['get'], schema=ProjectUploadSessionProgressSchema())
    def progress(self, request, pk):
        """
        Get Progress for a session per files (short form)
        """
        session = self.get_object()
        session.check_and_set_completed()
        document_tasks_progress = session.document_tasks_progress()
        document_tasks_progress_total = 100 if session.completed else session.document_tasks_progress_total
        result = {'project_id': session.project.pk if session.project else None,
                  'document_tasks_progress': document_tasks_progress or None,
                  'document_tasks_progress_total': document_tasks_progress_total,
                  'documents_total_size': session.documents_total_size,
                  'session_status': session.status}
        return Response(result)

    @action(detail=False, methods=['get'], schema=UploadSessionStatusSchema())
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
            CsLogger.get_django_logger().exception(exc)

    def upload_file(self,
                    file_name: str,
                    file_size: int,
                    contents: Union[BinaryIO, HttpRequest],
                    force: bool,
                    user_id: int,
                    directory_path: str,
                    review_file: bool = True) -> Response:

        """
        Upload file method
        :param file_name:
        :param file_size:
        :param contents:
        :param force: force rewrite doc
        :param user_id:
        :param directory_path:
        :param review_file: whether check or not for empty/exists/delete_pending/processing status
        :return:
        """
        logger = CsLogger.get_django_logger()
        from apps.document.app_vars import MAX_DOCUMENT_SIZE
        if file_size > MAX_DOCUMENT_SIZE.val() * 1024 * 1024:
            logger.error(f'uploading: file {file_name} is too large ({file_size})')
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=f'File size is greater than allowed max {MAX_DOCUMENT_SIZE.val()} Mb')

        try:
            session = self.get_object()
        except (UploadSession.DoesNotExist, ValidationError):
            logger.error('Uploading: session was not found')
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data='Wrong upload session uid.')

        project = session.project
        from apps.document.app_vars import ALLOW_DUPLICATE_DOCS
        force_rename = force or not ALLOW_DUPLICATE_DOCS.val(project_id=project.id)

        if review_file or force_rename:
            can_upload_status = self.can_upload_file(project, file_name, file_size, session.pk)
        else:
            can_upload_status = True

        if not force_rename and can_upload_status is not True:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'status': can_upload_status})

        try:
            if can_upload_status is not True:
                file_base_name, file_ext = os.path.splitext(file_name)
                file_copy_name_ptn = '{0} copy {1:02d}{2}'
                for n in range(1, 999):
                    file_copy_name = file_copy_name_ptn.format(file_base_name, n, file_ext)
                    can_upload_copy_status = self.can_upload_file(project, file_copy_name, file_size, session.pk)
                    if can_upload_copy_status is True:
                        file_name = file_copy_name
                        break

            stor = get_file_storage()
            source_path = stor.sub_path_join(session.pk, file_name)

            # # check file name is unique
            # from apps.document.sync_tasks.ensure_new_paths_unique_task import EnsureNewPathsUnique
            # en_task = EnsureNewPathsUnique(
            #     lambda msg: get_django_logger().error(msg))
            #
            # try:
            #     unique = en_task.ensure_new_file_unique(project=project,
            #                                             source_path=source_path,
            #                                             doc_name=file_name,
            #                                             rename_old_document=force_rename)
            #     if not unique:
            #         return Response(status=status.HTTP_409_CONFLICT, data=ALREADY_EXISTS)
            # except Exception as e:
            #     return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            #                     data='Failed to remove files with the same name, original exception is: {}'.format(str(e)))

            # TODO: move this check into "stor" itself | we do that check in can_upoad_file() ?
            if not file_size:
                return Response(status=status.HTTP_204_NO_CONTENT,
                                data={'status': 'Empty file'})
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
                project_id=project.id,
                run_standard_locators=True,
                metadata={'file_name': file_name, 'file_size': file_size},
                linked_tasks=None,
                directory_path=directory_path)

            if project.send_email_notification \
                    and not session.notified_upload_started:
                self._notify_upload_started(session)

        except Exception as e:
            logger.error(f'uploading: general error ({e})')
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            data=render_error('Unable to load file', caused_by=e))

        return Response(status=status.HTTP_201_CREATED, data={'status': 'OK'})

    @action(detail=True, methods=['post'], schema=UploadSessionFilesSchema())
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
                                force=as_bool(request.GET, 'force', False) or
                                      request.META.get('HTTP_FORCE', False) == 'true',
                                directory_path=request.headers.get('Directory-Path'))

    def upload_archive(self, request, file_, archive_type, directory_path=None):
        from apps.document.app_vars import MAX_ARCHIVE_SIZE
        if file_.size > MAX_ARCHIVE_SIZE.val() * 1024 * 1024:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=f'Archive size is greater than allowed max {MAX_ARCHIVE_SIZE.val()} Mb')

        try:
            session = self.get_object()
        except (UploadSession.DoesNotExist, ValidationError):
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data='Wrong upload session uid.')

        if not file_.size:
            raise Exception(f'File "{file_.name}" has zero length')

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
            directory_path=directory_path,
            user_id=request.user.id,
            session_id=session.pk,
            force=as_bool(request.POST, 'force', False) or request.META.get('HTTP_FORCE', False) == 'true'
        )

        return Response(status=status.HTTP_200_OK, data='Loaded')

    def is_zip(self, file_):
        if zipfile.is_zipfile(file_):
            mime_type = mimetypes.guess_type(file_.name)
            if not mime_type or not mime_type[0]:
                mime_type = (ArchiveFile.guess_file_mime_type(file_), None,)
            if mime_type[0] in settings.ARCHIVES['zip']['allowed_mime_types']:
                # I believe further checks are unnecessary even for XLS, DOCX and other archives
                # ext = os.path.basename(file_.name).split('.', 1)
                # if len(ext) == 2 and ext[1] in settings.ARCHIVES['zip']['allowed_extensions']:
                return True
        return False

    def is_tar(self, file_):
        mime_type = mimetypes.guess_type(file_.name)
        if not mime_type or not mime_type[0]:
            mime_type = (ArchiveFile.guess_file_mime_type(file_), None,)
        if (hasattr(file_, 'temporary_file_path') and tarfile.is_tarfile(file_.temporary_file_path())) or \
                mime_type[0] in settings.ARCHIVES['tar']['allowed_mime_types']:
            # ext = os.path.basename(file_.name).split('.', 1)
            # if len(ext) == 2 and ext[1] in settings.ARCHIVES['tar']['allowed_extensions']:
            return True
        return False

    @action(detail=True, methods=['post'], schema=UploadSessionUploadSchema())
    def upload(self, request, pk: str, review_file=True, directory_path=None):
        """
        Upload a File\n
            Params:
                - file: file object
                - force: bool (optional) - whether rewrite existing file and Document
                - review_file: bool - whether skip file check (exists or not)
                - directory_path: str - may be passed from TUS plugin
        """
        file_ = request.FILES.dict().get('file')

        if not file_ and isinstance(request.data, (str, bytes)):
            file_encoding = request.META.get('HTTP_FILE_ENCODING', 'utf-8')
            file_ = BytesIO(request.data.encode(file_encoding)
                            if isinstance(request.data, str) else request.data)
            file_name = request.META.get('HTTP_FILE_NAME')
            file_ = File(file_, name=file_name)

        if not file_:
            raise APIException('File not found.')

        if self.is_zip(file_):
            return self.upload_archive(request, file_, directory_path=directory_path, archive_type='zip')
        if self.is_tar(file_):
            return self.upload_archive(request, file_, directory_path=directory_path, archive_type='tar')
        file_.seek(0)

        resp = self.upload_file(file_name=file_.name,
                                file_size=file_.size,
                                contents=file_.file,
                                user_id=request.user.id,
                                force=request.POST.get('force') == 'true' or
                                      request.META.get('HTTP_FORCE') == 'true',
                                directory_path=directory_path or request.POST.get('directory_path'),
                                review_file=review_file)

        # workaround for old frontend usage which checks status based on string constants in response data
        # and not on the status codes
        if resp.status_code == status.HTTP_201_CREATED:
            resp.status_code = status.HTTP_200_OK
        return resp

    @action(detail=True, methods=['post'], schema=UploadSessionBatchUploadSchema())
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
                project_id=project.id,
                metadata={'file_name': file_name},
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

    @action(detail=True, methods=['delete'], url_path='cancel')
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

    @action(detail=True, methods=['delete'], url_path='delete-file', schema=UploadSessionDeleteFileSchema())
    def delete_file(self, request, **kwargs):
        """
        Delete a file from session\n
            Params:
                - filename: str
        """
        session_id = self.get_object().pk
        file_name = request.POST.get('filename') or request.data.get('filename')

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

class ProjectSerializer(ProjectDetailSerializer):
    class Meta(ProjectDetailSerializer.Meta):
        model = Project
        fields = ['pk', 'name', 'progress']


class DocumentClusterSerializer(serializers.ModelSerializer):
    documents_count = serializers.SerializerMethodField()

    class Meta:
        model = DocumentCluster
        fields = ['pk', 'cluster_id', 'name', 'documents_count']

    def get_documents_count(self, obj):
        return obj.documents.filter(processed=True).count()
    get_documents_count.output_field = serializers.IntegerField()


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
    get_status.output_field = serializers.CharField()


class ProjectClusteringViewSet(apps.common.mixins.JqListAPIMixin, viewsets.ReadOnlyModelViewSet):
    """
    list: ProjectCluster List
    retrieve: ProjectCluster Details
    """
    queryset = ProjectClustering.objects.all()
    serializer_class = ProjectClusteringSerializer

    def get_queryset(self):
        projects = get_objects_for_user(self.request.user, 'project.recluster_project', Project)
        qs = super().get_queryset() \
            .filter(project_id__in=projects.values_list('pk', flat=True)) \
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
         ProjectViewSet.as_view({'get': 'clustering_status'}, schema=ProjectClusteringStatusSchema()),
         name='clustering_status'),
    path('projects/<int:pk>/cluster/',
         ProjectViewSet.as_view({'post': 'cluster'}, schema=ClusterProjectSchema()), name='cluster'),
    path('locales/', LocaleListView.as_view(), name='locales')
]
