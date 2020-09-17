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
import logging
import os
import traceback
from collections import defaultdict, OrderedDict
from itertools import groupby
from typing import Dict, Set
from zipfile import ZipFile, ZIP_DEFLATED

# Third-party imports
import numpy as np
import rest_framework.views
from celery.states import SUCCESS, FAILURE, PENDING, REVOKED
from djangoql.parser import DjangoQLParser

# Django imports
from django.conf.urls import url
from django.db.models import Subquery, Prefetch, OuterRef, TextField, CharField, IntegerField, DateField, Case, When
from django.db.models.functions import Cast
from django.db.utils import IntegrityError
from django.http import JsonResponse, HttpRequest, Http404, HttpResponse, HttpResponseNotFound
from rest_framework import routers, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, ValidationError as DRFValidationError, ParseError
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework_nested import routers as nested_routers

from apps.analyze.models import *
from apps.common.api.permissions import TopStaffPermission
# Project imports
from apps.common.log_utils import ProcessLogger
from apps.common.mixins import APIActionMixin, APIResponseMixin, SimpleRelationSerializer, \
    JqListAPIMixin, APIFormFieldsMixin, APILoggingMixin
from apps.common.models import ReviewStatus
from apps.common.serializers import WritableSerializerMethodField
from apps.common.url_utils import as_bool, as_int, as_int_list
from apps.common.utils import get_api_module, GroupConcat, topological_sort, Map
from apps.document import signals
from apps.document.admin import (
    DocumentFieldForm, UsersTasksValidationAdmin, PARAM_OVERRIDE_WARNINGS, DocumentTypeForm,
    DocumentFieldCategoryForm)
from apps.document.api.annotator_error import NoValueProvidedOrLocated
from apps.document.async_tasks.detect_field_values_task import DocDetectFieldValuesParams
from apps.document.constants import DocumentSystemField
from apps.document.field_detection import field_detection
from apps.document.field_detection.detector_field_matcher import DetectorFieldMatcher
from apps.document.field_detection.field_detection import FIELD_DETECTION_STRATEGY_REGISTRY
from apps.document.field_detection.field_detection_celery_api import run_detect_field_values_for_document
from apps.document.field_detection.fields_detection_abstractions import FieldDetectionStrategy
from apps.document.field_types import TypedField, BooleanField, RelatedInfoField, MultiValueField
from apps.document.forms import CloneDocumentFieldForm, CloneDocumentTypeForm
from apps.document.models import *
from apps.document.repository.document_field_repository import DocumentFieldRepository
from apps.document.repository.document_repository import DocumentRepository
from apps.document.repository.dto import FieldValueDTO, AnnotationDTO
from apps.document.scheme_migrations.scheme_migration import TAGGED_VERSION
from apps.document.tasks import plan_process_document_changed, ImportDocumentType
from apps.document.views import show_document
from apps.dump.app_dump import download, get_app_config_versioned_dump
from apps.extract.models import *
from apps.rawdb.signals import reindex_on_doc_type_change
from apps.task.tasks import call_task
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


common_api_module = get_api_module('common')
project_api_module = get_api_module('project')
extract_api_module = get_api_module('extract')

logger = logging.getLogger('django')
process_logger = ProcessLogger()


# --------------------------------------------------------
# Document Field Value Views
# --------------------------------------------------------

class GeneratorListSerializer(serializers.ListSerializer):
    """
    Return data as a generator instead of a list
    """

    def to_representation(self, data):
        """
        List of object instances -> List of dicts of primitive datatypes.
        """
        # Dealing with nested relationships, data can be a Manager,
        # so, get a queryset from the Manager if needed
        # Use an iterator on the queryset to allow large querysets to be
        # exported without excessive memory usage
        if isinstance(data, models.Manager):
            iterable = data.all().iterator()
        elif isinstance(data, models.QuerySet):
            iterable = data.iterator()
        else:
            iterable = data
        # Return a generator rather than a list so that streaming responses
        # can be used
        return (self.unify_representation(item) for item in iterable)

    def unify_representation(self, item):
        # if some nested field is not found i.e. document.project.name
        # but document has no associated project
        # this field will be missed in item data, so we need to override it
        # in case if we need strong fields mapping
        item_representation = self.child.to_representation(item)
        for field in self.child.Meta.fields:
            if field not in item_representation:
                item_representation[field] = None
        return item_representation

    @property
    def data(self):
        # Note we deliberately return the super of ListSerializer to avoid
        # instantiating a ReturnList, which would force evaluating the generator
        return super(serializers.ListSerializer, self).data


# --------------------------------------------------------
# Document Note Views
# --------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['pk', 'first_name', 'last_name', 'username', 'role',
                  'photo', 'full_name']

    def get_photo(self, obj):
        return obj.photo.url if obj.photo else None

    def get_full_name(self, obj):
        return obj.get_full_name()


class DocumentNoteDetailSerializer(SimpleRelationSerializer):
    document_id = serializers.PrimaryKeyRelatedField(
        source='document', queryset=Document.objects.all())

    user = UserSerializer(many=False, read_only=True)
    # history = serializers.SerializerMethodField()
    field_repo = DocumentFieldRepository()
    field_value_id = serializers.PrimaryKeyRelatedField(
        source='field_value',
        queryset=field_repo.get_all_docfieldvalues(),
        required=False)
    field_id = serializers.PrimaryKeyRelatedField(
        source='field', queryset=DocumentField.objects.all(), required=False)

    class Meta:
        model = DocumentNote
        fields = ['pk', 'note', 'timestamp', 'user',
                  'location_start', 'location_end',
                  'document_id', 'field_value_id', 'field_id']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return ret


class DocumentNoteExportSerializer(DocumentNoteDetailSerializer):

    user = serializers.CharField(source='history.last.history_user.username', read_only=True)
    annotation_text = serializers.SerializerMethodField()

    class Meta:
        model = DocumentNote
        fields = ['pk', 'note', 'timestamp', 'user', 'document_id', 'annotation_text']

    def get_annotation_text(self, obj):
        if obj.location_start is not None and obj.location_end is not None:
            return obj.document.full_text[obj.location_start:obj.location_end]


class DocumentNoteCreateSerializer(DocumentNoteDetailSerializer):
    class Meta(DocumentNoteDetailSerializer.Meta):
        fields = ['pk', 'note', 'timestamp',
                  'location_start', 'location_end',
                  'document_id', 'field_value_id', 'field_id',
                  'user_id', 'username', 'user']
        read_only_fields = ('timestamp', 'user')

    def save(self):
        user = self.context['request'].user
        self.validated_data['user_id'] = user.pk
        self.validated_data['user'] = user
        self.validated_data['username'] = user.username or user.name
        resp = super().save()
        return resp


class DocumentNoteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentNote
        fields = ['note']


class DocumentNotePermissions(BasePermission):
    # def has_permission(self, request, view):
    #     if request.user.is_reviewer and view.kwargs.get('project_pk'):
    #         return project_api_module.Project.objects.filter(pk=view.kwargs.get('project_pk'),
    #                                                          reviewers=request.user).exists()
    #     return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_reviewer:
            return obj.document.project.reviewers.filter(pk=request.user.pk).exists()
        return True


class DocumentNotePermissionViewMixin(object):
    permission_classes = (IsAuthenticated, DocumentNotePermissions)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_reviewer:
            qs = qs.filter(document__project__reviewers=self.request.user)
        elif self.request.user.is_manager:
            qs = qs.filter(Q(document__project__reviewers=self.request.user) |
                           Q(document__project__owners=self.request.user)).distinct()
        return qs


class DocumentNoteViewSet(JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: Document Note List
    retrieve: Retrieve Document Note
    create: Create Document Note
    update: Update Document Note
    partial_update: Partial Update Document Note
    delete: Delete Document Note
    """
    queryset = DocumentNote.objects.all()

    def get_queryset(self):

        qs = super().get_queryset()

        project_id = self.request.GET.get('project_id')
        if project_id:
            qs = qs.filter(document__project_id=project_id)

        document_id = self.request.GET.get('document_id')
        if document_id:
            force = bool(self.request.GET.get('force'))
            qs = qs.filter(document_id=document_id)
            if not force:
                qs = qs.filter(document__delete_pending=False)

        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentNoteCreateSerializer
        if self.action == 'update':
            return DocumentNoteUpdateSerializer
        if self.request.GET.get('export_to'):
            return DocumentNoteExportSerializer
        return DocumentNoteDetailSerializer


# --------------------------------------------------------
# Document Views
# --------------------------------------------------------

class FieldAnnotationValueSerializer(serializers.ModelSerializer):
    adapter = None

    value = serializers.SerializerMethodField()
    field_name = serializers.SerializerMethodField()

    class Meta:
        model = FieldAnnotation
        list_serializer_class = GeneratorListSerializer
        fields = ['pk',
                  'field', 'field_name',
                  'location_start', 'location_end', 'location_text',
                  'value',
                  'modified_by', 'modified_date']

    def get_field_name(self, obj: FieldAnnotation):
        return '{type}: {field}'.format(
            type=obj.field.document_type.title if obj.field.document_type else 'NA',
            field=obj.field.title)

    def get_project(self, obj: FieldAnnotation):
        return obj.document.project.name if obj.document.project else 'NA'

    def get_value(self, obj: FieldAnnotation):
        return obj.value


class DocumentsForUserSerializer(SimpleRelationSerializer):
    """
    Serializer for user documents
    """
    status_name = serializers.CharField()

    class Meta:
        model = Document
        fields = ['pk', 'name', 'document_type', 'project', 'status_name']


class DocumentDetailDjangoQLSerializer(SimpleRelationSerializer):
    """
    Serializer for djangoql queries
    """
    project_name = serializers.CharField(source='project.name')

    class Meta:
        model = Document
        fields = ['id', 'name', 'project_id', 'project_name']


class DocumentDetailSerializer(DocumentsForUserSerializer):
    """
    Serializer for document review page with detailed document field values
    """
    field_repo = DocumentFieldRepository()

    status_data = common_api_module.ReviewStatusSerializer(source='status', many=False)
    available_statuses_data = serializers.SerializerMethodField()
    assignee_data = UserSerializer(source='assignee', many=False)
    available_assignees_data = serializers.SerializerMethodField()
    field_value_objects = serializers.SerializerMethodField()
    field_values = serializers.SerializerMethodField()
    notes = DocumentNoteDetailSerializer(source='documentnote_set', many=True)
    prev_id = serializers.SerializerMethodField()
    next_id = serializers.SerializerMethodField()
    sections = serializers.SerializerMethodField()
    initial_annotation_id = serializers.SerializerMethodField()
    page_locations = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['pk', 'name', 'document_type', 'file_size', 'folder',
                  'status', 'status_data', 'available_statuses_data',
                  'assignee', 'assign_date', 'assignee_data', 'available_assignees_data',
                  'description', 'title',
                  'initial_annotation_id',
                  'page_locations',
                  'notes', 'field_values', 'field_value_objects',
                  'prev_id', 'next_id', 'sections', 'cluster_id']

    def get_available_assignees_data(self, obj):
        return UserSerializer(obj.available_assignees, many=True).data

    def get_available_statuses_data(self, obj):
        return common_api_module.ReviewStatusSerializer(
            ReviewStatus.objects.select_related('group'), many=True).data

    def get_neighbours(self, document, use_saved_filter=True):
        prev_id = next_id = None
        user = self.context['request'].user
        project = document.project
        from apps.rawdb.api.v1 import DocumentsAPIView

        ids = DocumentsAPIView.simulate_get(user, project, use_saved_filter=use_saved_filter)

        if document.pk in ids:
            pos = ids.index(document.pk)
        else:
            return self.get_neighbours(document, use_saved_filter=False)

        prev_ids = ids[:pos]
        if prev_ids:
            prev_id = prev_ids[-1]
        next_ids = ids[pos + 1:]
        if next_ids:
            next_id = next_ids[0]
        return prev_id, next_id

    def get_prev_id(self, obj):
        return self.get_neighbours(obj)[0]

    def get_next_id(self, obj):
        return self.get_neighbours(obj)[1]

    def get_sections(self, obj):
        if isinstance(obj.metadata, dict) and 'sections' in obj.metadata:
            return obj.metadata['sections'] or []
        return []

    def get_field_values(self, doc: Document):
        """
        Get field values in format: field uid -> python/json value.
        :param doc:
        :return:
        """
        field_repo = DocumentFieldRepository()
        return field_repo.get_field_uid_to_python_value(
            document_type_id=doc.document_type_id,
            doc_id=doc.pk,
            ignore_errors=True,
            log_func=lambda m: logger.error(m))

    def get_field_value_objects(self, doc: Document):
        """
        Get annotations.
        :param doc:
        :return:
        """
        field_uids_to_field_value_objects = {}
        for fv in doc.annotations_matches.all():  # type: FieldAnnotation
            serialized_fv = FieldAnnotationValueSerializer(fv).data
            field = fv.field
            field_uid = field.uid
            typed_field = TypedField.by(fv.field)
            if typed_field.multi_value:
                if field_uids_to_field_value_objects.get(field_uid) is None:
                    field_uids_to_field_value_objects[field_uid] = [serialized_fv]
                else:
                    field_uids_to_field_value_objects[field_uid].append(serialized_fv)
            else:
                field_uids_to_field_value_objects[field_uid] = serialized_fv
        return field_uids_to_field_value_objects

    def get_initial_annotation_id(self, obj):
        """
        Get either first clause with "Unreviewed" status or just first one in any status
        """
        document_annotations = obj.annotations_matches.order_by('location_start')
        unreviewed = document_annotations.filter(
            document__delete_pending=False,
            status_id=FieldAnnotationStatus.initial_status_pk())
        if unreviewed.exists():
            document_annotations = unreviewed
        return document_annotations.first().uid if document_annotations.exists() else None

    def get_page_locations(self, doc: Document):
        return list(DocumentPage.objects.filter(document_id=doc.pk).order_by(
            'number').values_list('location_start', 'location_end'))


class DocumentPermissions(BasePermission):

    def has_permission(self, request, view):
        reviewer_permission = self.has_reviewer_permisson(request, view)
        if reviewer_permission is not None:
            return reviewer_permission

        # TODO: find better way to validate user permission for those endpoints,
        # because we check multiple projects at once, but need only one containing its documents
        is_reviewer_action = request.method == 'POST' and view.action in [
            'mark_delete', 'unmark_delete']
        if is_reviewer_action and request.user.is_reviewer:
            document_ids = request.data.get('document_ids', [])
            project_id = request.data.get('project_id')

            if request.data.get('all') and project_id:
                from apps.rawdb.api.v1 import DocumentsAPIView
                document_ids = DocumentsAPIView.simulate_get(request.user, project_id)

            projects = project_api_module.Project.objects.filter(
                document__in=document_ids,
                super_reviewers=request.user)
            if not projects.exists():
                return False
        elif request.user.is_reviewer:
            if request.method in ['POST', 'PUT', 'DELETE']:
                return False
            elif request.method == 'PATCH' and \
                    list(request.data.keys()) not in (['status'], ['assignee']):
                return False
            if view.kwargs.get('project_pk'):
                return project_api_module.Project.objects.filter(pk=view.kwargs.get('project_pk'),
                                                                 reviewers=request.user).exists()
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_reviewer:
            return obj.project.reviewers.filter(pk=request.user.pk).exists()
        return True

    @staticmethod
    def has_reviewer_permisson(request, view) -> Optional[bool]:
        if not request.user.is_reviewer:
            return None
        reviewer_actions = ['fields']
        if view.action not in reviewer_actions:
            return None
        # check project requested
        project_id = view.kwargs.get('project_pk')
        if not project_id:
            return None

        projects = project_api_module.Project.objects.filter(
            (Q(reviewers=request.user) | Q(super_reviewers=request.user)) &
            Q(pk=int(project_id)))
        return projects.exists()


class DocumentPermissionViewMixin(object):
    permission_classes = (IsAuthenticated, DocumentPermissions)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_reviewer:
            qs = qs.filter(project__reviewers=self.request.user)
        elif self.request.user.is_manager:
            qs = qs.filter(Q(project__reviewers=self.request.user) |
                           Q(project__owners=self.request.user)).distinct()
        return qs


class DocumentViewSet(APILoggingMixin,
                      DocumentPermissionViewMixin, APIActionMixin,
                      JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: Document List with Fields
    retrieve: Document Detail with Fields
    """
    queryset = Document.objects.filter(processed=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_documents = None

    def get_object(self, *args, **kwargs):
        doc_pk = self.kwargs.get('pk')
        if not doc_pk:
            return super().get_object()

        query_set = self.get_queryset()
        try:
            doc = query_set.get(*args, **{'pk': doc_pk})  # type: Document
        except Document.DoesNotExist:
            raise Http404()
        return doc

    def get_queryset(self):
        qs = super().get_queryset()

        ql = self.request.GET.get('q')
        if ql:
            if not self.is_valid_ql(ql):
                raise APIException('Provide project data for djangoql query.')
            try:
                qs = Document.ql_objects.djangoql(ql).distinct()
            except Exception as e:
                raise APIException(str(e))

        project_id = self.kwargs.get('project_pk')
        if project_id:
            qs = qs.filter(project_id=project_id)

        cluster_id = self.request.GET.get("cluster_id")
        if cluster_id:
            qs = qs.filter(cluster_id=int(cluster_id))

        if self.action == 'for_user':
            qs = qs.filter(assignee=self.request.user, status__group__is_active=True)
            self.total_documents = qs.count()

        elif self.action == 'retrieve':
            qs = qs.prefetch_related('documentnote_set')

        qs = qs \
            .select_related('status', 'status__group', 'document_type', 'assignee') \
            .defer('language', 'source', 'source_type', 'source_path',
                   'paragraphs', 'sentences', 'upload_session_id')

        qs = qs.annotate(assignee_name=F('assignee__username'),
                         status_name=F('status__name'))

        return qs

    @staticmethod
    def is_valid_ql(ql):
        """
        Check that query string has "project" to have limited set of documents
        otherwise it may crash a server with 502/504 error
        :param ql: query string
        :return: bool
        """
        expression = DjangoQLParser().parse(ql)

        def validate(e):
            if hasattr(e, 'parts'):
                yield 'project' in e.parts
            else:
                if hasattr(e, 'left'):
                    yield from validate(e.left)
                if hasattr(e, 'right'):
                    yield from validate(e.right)

        return any(validate(expression))

    def get_extra_data(self, queryset):
        extra_data = super().get_extra_data(queryset)
        extra_data.update({'reviewed_total': queryset.filter(status__is_active=False).count()})
        extra_data.update({'query_string': self.request.META['QUERY_STRING']})
        return extra_data

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'data' or self.request.method == 'PATCH':
            return DocumentDetailSerializer
        elif 'q' in self.request.GET:
            return DocumentDetailDjangoQLSerializer
        return DocumentsForUserSerializer

    def get_export_file_name(self):
        project_pk = self.kwargs.get('project_pk')
        if project_pk:
            return project_api_module.Project.objects.get(pk=project_pk).name

    def process_export_data(self, data):
        # data['max_date'] = data['max_date'].astype('datetime64[ns]')
        # data['min_date'] = data['min_date'].astype('datetime64[ns]')
        fields = DocumentField.objects.filter(
            field_document_type__project__pk=self.kwargs['project_pk']).values('pk', 'title')
        for field in fields:
            data[field['title']] = data['field_values'].apply(lambda x: x.get(field['pk']) if x else '')
        return data

    @action(detail=True, methods=['get'])
    def show(self, request, **kwargs):
        document = self.get_object()
        return show_document(request, document.pk)

    @action(detail=False, methods=['get'])
    def download_zip(self, request, **kwargs):
        from apps.common.file_storage import get_file_storage
        file_storage = get_file_storage()

        project_id = self.kwargs.get('project_pk')
        document_ids = as_int_list(request.GET, 'document_ids')
        except_document_ids = as_int_list(request.GET, 'exclude_document_ids')
        all_ids = as_bool(request.GET, 'all')
        # need to have either "document_ids" param OR "all" + optional "except_document_ids" params
        if not (document_ids or all_ids):
            return Response(
                {'detail': 'Provide either "?document_ids=1,2,3" or "'
                           '?all=true" parameter plus optional "&except_document_ids=1,2,3" param.'},
                status=404)

        from apps.rawdb.api.v1 import DocumentsAPIView
        ids = DocumentsAPIView.simulate_get(request.user, project_id, use_saved_filter=True)
        documents = Document.objects.filter(id__in=ids)

        if document_ids:
            documents = documents.filter(id__in=document_ids)
        if except_document_ids:
            documents = documents.exclude(id__in=except_document_ids)

        if not documents.exists():
            return HttpResponseNotFound('Not Found')

        from apps.document.app_vars import MAX_DOCUMENTS_TO_EXPORT_SIZE_HTTP
        total_files_fize = sum(documents.values_list('file_size', flat=True))

        if total_files_fize <= MAX_DOCUMENTS_TO_EXPORT_SIZE_HTTP.val * 1024 * 1024:
            resp = HttpResponse(content_type='application/zip')
            resp['Content-Disposition'] = f'attachment; filename="export.zip"'

            with ZipFile(resp, 'w', ZIP_DEFLATED) as zip_archive:
                for doc in documents:
                    with file_storage.get_document_as_local_fn(doc.source_path) as (fn, _):
                        try:
                            dst = os.path.join(doc.documentcluster_set.last().name, doc.name)\
                                if doc.document_type.is_generic() else doc.name
                            zip_archive.writestr(dst, open(fn, 'rb').read())
                        except FileNotFoundError:
                            pass
                return resp

        document_ids = list(documents.values_list('id', flat=True))
        from apps.document.tasks import ExportDocumentFiles
        task_id = call_task(ExportDocumentFiles,
                            document_ids=document_ids,
                            project_id=project_id,
                            user_id=request.user.id)
        msg = 'Selected documents will be archived. You will receive an email with a link ' \
              'to download the documents when they are ready.'
        return Response(status=200, data={'task_id': task_id, 'detail': msg})

    @action(detail=False, methods=['get'], url_path='for-user')
    def for_user(self, request, *args, **kwrags):
        response = super().list(request, *args, **kwrags)
        data = dict(
            total_documents=self.total_documents,
            data=response.data
        )
        return Response(data)

    @action(methods=['get'], detail=True)
    def full_text(self, request, project_pk, pk):
        document = self.get_object()
        text = document.text
        return JsonResponse(data=text, safe=False)

    @action(detail=True, methods=['get'], url_path='data')
    def data(self, request, *args, **kwrags):
        """
        Restricted set of fields in response (except full_text), see get_serializer_class()
        """
        return super().retrieve(request, *args, **kwrags)

    @action(methods=['get', 'put', 'post', 'patch'], detail=True)
    def fields(self, request: HttpRequest, project_pk: int, pk: int):
        field_repo = DocumentFieldRepository()

        if request.method == 'GET':
            field_code_to_value = field_repo.get_field_code_to_json_value(doc_id=pk)
            field_code_to_ant_stats = field_repo.get_annotation_stats_by_doc(document_id=pk)
            res = {
                field_code: {'value': value, 'annotation_stats': field_code_to_ant_stats.get(field_code)}
                for field_code, value in field_code_to_value.items()
            }
            return JsonResponse(res)
        elif request.method in {'POST', 'PUT', 'PATCH'}:
            doc = self.get_object()
            updated_fields = {f for f, fv in field_repo.update_field_values(doc, request.user, request.data)}
            cache_and_detect_field_values(doc=doc, user=request.user, updated_fields=updated_fields)
            return Response(status=200)

    @action(detail=True, methods=['get'])
    def extraction(self, request, **kwargs):
        """
        Standard extracted info - Top level + details\n
            Params:
                - skip_details: bool - show top-level data only (skip per text-unit data)
                - values: str - list of str separated by comma like dates,parties,courts
        """
        document = self.get_object()
        text_unit_type = self.request.GET.get('text_unit_type')

        class_kwargs = dict(request=request, format_kwarg=None,
                            document_id=document.id, text_unit_type=text_unit_type)

        extraction_map = dict(
            amounts=extract_api_module.TopAmountUsageListAPIView,
            citations=extract_api_module.TopCitationUsageListAPIView,
            copyrights=extract_api_module.TopCopyrightUsageListAPIView,
            courts=extract_api_module.TopCourtUsageListAPIView,
            currencies=extract_api_module.TopCurrencyUsageListAPIView,
            dates=extract_api_module.TopDateUsageListAPIView,
            date_durations=extract_api_module.TopDateDurationUsageListAPIView,
            definitions=extract_api_module.TopDefinitionUsageListAPIView,
            distances=extract_api_module.TopDistanceUsageListAPIView,
            geographies=extract_api_module.TopGeoEntityUsageListAPIView,
            parties=extract_api_module.TopPartyUsageListAPIView,
            percents=extract_api_module.TopPercentUsageListAPIView,
            ratios=extract_api_module.TopRatioUsageListAPIView,
            # terms=extract_api_module.TopTermUsageListAPIView,
            trademarks=extract_api_module.TopTrademarkUsageListAPIView,
            url=extract_api_module.TopUrlUsageListAPIView,
        )
        if request.GET.get('values'):
            requested_keys = request.GET.get('values').split(',')
            extraction_map = {k: v for k, v in extraction_map.items() if k in requested_keys}

        result = {key_name: view_class(**class_kwargs).data
                  for key_name, view_class in extraction_map.items()}

        # reformat output
        try:
            for item_name, item_data in result.items():
                for value_data in item_data:
                    value_data['title'] = item_name.upper().replace('_', ' ')
                    for row in value_data['data']:
                        row['ranges'] = [{'startOffset': row['text_unit__location_start'],
                                          'endOffset': row['text_unit__location_end']}]
        except:
            pass
        return Response(result)

    @action(detail=True, methods=['get'])
    def definitions(self, request, **kwargs):
        document = self.get_object()
        if document.metadata is None or 'definitions' not in document.metadata:
            definitions = DefinitionUsage.objects.filter(text_unit__document=document) \
                .annotate(startOffset=F('text_unit__location_start'),
                          endOffset=F('text_unit__location_end'),
                          text=F('text_unit__textunittext__text')).values(
                'definition', 'startOffset', 'endOffset', 'text')

            res = list()
            grouped = {k: [{vik: viv for vik, viv in vi.items() if vik != 'definition'} for vi in v] for
                       k, v in groupby(definitions, lambda i: i['definition'])}
            for definition, data in grouped.items():
                definition_re = re.compile(r'\b{}(?!\-)\b(?!s\b)'.format(re.escape(definition)), re.I | re.M)

                item = {'definition': definition,
                        'matches': [{'startOffset': m.start(), 'endOffset': m.end()} for m in
                                    definition_re.finditer(document.text.replace('\n', ' '))],
                        'descriptions': list(data)}
                res.append(item)
            if document.metadata is None:
                DocumentMetadata.objects.create(document=document, metadata=dict())
            document.documentmetadata.metadata['definitions'] = res
            document.documentmetadata.save()
        return Response(document.metadata['definitions'])

    @action(detail=False, methods=['post'])
    def mark_delete(self, request, **kwargs):
        """
        Method marks a number of documents for deleting. These marked documents will become hidden in API.
        :param request: provide a list of document ids here: document_ids: [...]
        :param kwargs:
        :return: OK or 404
        """
        return self.mark_unmark_for_delete(True, request)

    @action(detail=False, methods=['post'])
    def unmark_delete(self, request, **kwargs):
        """
        Method recovers documents, marked for deleting. These documents will become visible in API.
        :param request: provide a list of document ids here: document_ids: [...]
        :param kwargs:
        :return: OK or 404
        """
        return self.mark_unmark_for_delete(False, request)

    @staticmethod
    def mark_unmark_for_delete(delete_not_undelete: bool, request) -> Response:
        ids = request.data.get('document_ids', [])
        project_id = request.data.get('project_id')

        if request.data.get('all') and project_id:
            from apps.rawdb.api.v1 import DocumentsAPIView
            ids = DocumentsAPIView.simulate_get(request.user, project_id)

        from apps.document.sync_tasks.soft_delete_document_task import SoftDeleteDocumentsSyncTask
        count_deleted = SoftDeleteDocumentsSyncTask().process(
            document_ids=ids,
            delete_not_undelete=delete_not_undelete)
        return Response({"count_deleted": count_deleted}, status=200)

    def update(self, request, *args, **kwargs):
        """
        Set new assignee OR document status
        """
        document = self.get_object()
        with transaction.atomic():
            system_fields_changed = list()

            if 'status' in request.data:
                new_status = ReviewStatus.objects.get(pk=request.data.get('status'))
                if new_status is not None and new_status != document.status_id:
                    is_active = document.status and document.status.is_active
                    if new_status.is_active != is_active:
                        field_repo = DocumentFieldRepository()
                        field_ids = field_repo.get_doc_field_ids_with_values(document.pk)
                        DocumentField.objects \
                            .filter(document_type_id=document.document_type_id, pk__in=Subquery(field_ids)) \
                            .update(dirty=True)
                    system_fields_changed.append(DocumentSystemField.status.value)

            if 'assignee' in request.data:
                new_assignee = User.objects.get(pk=request.data.get('assignee'))
                prev_assignee = document.assignee
                if new_assignee is None and prev_assignee is not None:
                    request.data['assign_date'] = None
                    system_fields_changed.append(DocumentSystemField.assignee.value)
                elif new_assignee is not None and (prev_assignee is None or new_assignee.pk != prev_assignee.pk):
                    request.data['assign_date'] = datetime.datetime.now(tz=request.user.get_time_zone())
                    system_fields_changed.append(DocumentSystemField.assignee.value)

            # allow update ONLY for status and assignee fields via API
            if system_fields_changed:
                super().update(request, *args, **kwargs)

                plan_process_document_changed(doc_id=document.pk,
                                              system_fields_changed=system_fields_changed,
                                              generic_fields_changed=False,
                                              user_fields_changed=False,
                                              changed_by_user_id=request.user.pk)
            return Response('OK')


# --------------------------------------------------------
# TextUnit Views
# --------------------------------------------------------

class TextUnitDjangoQLSerializer(SimpleRelationSerializer):

    document_name = serializers.CharField(source='document.name')
    project_name = serializers.CharField(source='project.name')

    class Meta:
        model = TextUnit
        fields = ['id', 'unit_type', 'text',
                  'project_id', 'project_name',
                  'document_id', 'document_name']


class TextUnitViewSet(APILoggingMixin,
                      DocumentPermissionViewMixin, APIActionMixin,
                      JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: TextUnit List
    retrieve: Retrieve TextUnit
    """
    queryset = TextUnit.objects
    http_method_names = ['get']
    serializer_class = TextUnitDjangoQLSerializer

    def get_queryset(self):

        qs = super().get_queryset()

        ql = self.request.GET.get('q')
        if ql:
            if not self.is_valid_ql(ql):
                raise APIException('Provide document or/and project data for djangoql query.')
            try:
                qs = TextUnit.ql_objects.djangoql(ql).distinct()
            except Exception as e:
                raise APIException(str(e))
        elif self.action == 'list':
            raise APIException('Provide djangoql query.')

        qs = qs.select_related('textunittext', 'project', 'document')

        return qs

    @staticmethod
    def is_valid_ql(ql):
        """
        Check that query string has "project" or "document" to have limited set of text units
        otherwise it may crash a server with 502/504 error
        :param ql: query string
        :return: bool
        """
        expression = DjangoQLParser().parse(ql)

        def validate(e):
            if hasattr(e, 'parts'):
                yield 'project' in e.parts or 'document' in e.parts
            else:
                if hasattr(e, 'left'):
                    yield from validate(e.left)
                if hasattr(e, 'right'):
                    yield from validate(e.right)

        return any(validate(expression))


# --------------------------------------------------------
# Document Field Views
# --------------------------------------------------------

class DocumentFieldCategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFieldCategory
        fields = ['id', 'name', 'order']


class DocumentFieldFamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFieldFamily
        fields = ['id', 'code', 'title']


class DocumentFieldDetailSerializer(SimpleRelationSerializer):
    value_aware = serializers.SerializerMethodField()
    choices = serializers.SerializerMethodField()
    depends_on_fields = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = DocumentField
        fields = ['uid', 'document_type', 'code', 'long_code', 'title', 'description', 'type',
                  'text_unit_type', 'value_detection_strategy', 'python_coded_field',
                  'classifier_init_script', 'formula', 'value_regexp', 'depends_on_fields',
                  'confidence', 'requires_text_annotations', 'read_only', 'category', 'family',
                  'default_value', 'choices', 'allow_values_not_specified_in_choices',
                  'stop_words', 'metadata', 'training_finished', 'dirty', 'order',
                  'trained_after_documents_number', 'hidden_always',
                  'hide_until_python', 'hide_until_js',
                  'detect_limit_unit', 'detect_limit_count',
                  'display_yes_no', 'value_aware', 'created_by', 'modified_by',
                  'created_date', 'modified_date',
                  'vectorizer_stop_words', 'unsure_choice_value', 'unsure_thresholds_by_value',
                  'mlflow_model_uri', 'mlflow_detect_on_document_level']

    def get_category(self, obj):
        return obj.category.name if obj.category else None

    def get_value_aware(self, obj: DocumentField):
        return TypedField.by(obj).requires_value

    def get_choices(self, obj: DocumentField):
        return obj.get_choice_values()

    def get_depends_on_fields(self, obj: DocumentField):
        return [field.pk for field in obj.depends_on_fields.all()]


class DocumentFieldListSerializer(DocumentFieldDetailSerializer):
    category = DocumentFieldCategorySimpleSerializer(many=False, read_only=True)
    family = DocumentFieldFamilySerializer(many=False, read_only=True)


class ModelFormBasedSerializer(serializers.ModelSerializer):
    """
    Model Serializer based on Model Form to validate input data using form fields
    """
    model_form_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.model_form_class is None:
            raise APIException('ModelForm class is not defined')

    def get_fields(self):
        """
        Set field readonly if form field is disabled
        """
        serializer_fields = super().get_fields()
        try:
            model_form = self.model_form_class(instance=self.instance)
        except Exception as e:
            raise APIException(str(e))
        for field_name, form_field in model_form.fields.items():
            if field_name in serializer_fields:
                if form_field.disabled:
                    serializer_fields[field_name].read_only = True
                if form_field.required:
                    serializer_fields[field_name].required = True
                if form_field.help_text:
                    serializer_fields[field_name].help_text = form_field.help_text
        return serializer_fields

    def is_valid(self, raise_exception=False):
        form_errors = {}
        request = self.context['request']
        form_data = request.data

        # pass full data to model form
        if request.method == 'PATCH':
            _form_data = self.to_representation(self.instance)
            _form_data.update(form_data)
            form_data = _form_data

        model_form = self.model_form_class(form_data, instance=self.instance)
        if not model_form.is_valid():
            form_errors = model_form.errors
        super().is_valid(raise_exception=False)

        all_errors = dict(self.errors)
        all_errors.update(form_errors)
        if all_errors:
            raise DRFValidationError(all_errors)

        # update validated data using form data in case if some values were changed in form clean()
        self._validated_data = {k: model_form.cleaned_data[k]
                                for k, _ in self._validated_data.items()}
        return True


class DocumentFieldCreateSerializer(ModelFormBasedSerializer):
    model_form_class = DocumentFieldForm

    class Meta:
        model = DocumentField
        fields = ['document_type', 'code', 'long_code', 'title', 'description', 'type',
                  'text_unit_type', 'value_detection_strategy', 'python_coded_field',
                  'classifier_init_script', 'formula', 'value_regexp', 'depends_on_fields',
                  'confidence', 'requires_text_annotations', 'read_only', 'category', 'family',
                  'default_value', 'choices', 'allow_values_not_specified_in_choices',
                  'stop_words', 'metadata', 'training_finished', 'dirty', 'order',
                  'trained_after_documents_number', 'hidden_always', 'hide_until_python',
                  'hide_until_js', 'display_yes_no', 'detect_limit_unit', 'detect_limit_count',
                  'vectorizer_stop_words', 'unsure_choice_value', 'unsure_thresholds_by_value',
                  'mlflow_model_uri', 'mlflow_detect_on_document_level']

    def is_valid(self, raise_exception=False):
        super().is_valid()
        UsersTasksValidationAdmin.validate_running_tasks(self.context['request'], self.errors)
        return True

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        signals.document_field_changed.send(self.__class__, user=None, document_field=instance)
        return instance


class DocumentFieldViewSet(JqListAPIMixin,
                           APIResponseMixin,
                           APIFormFieldsMixin,
                           viewsets.ModelViewSet):
    """
    list: Document Field List
    retrieve: Retrieve Document Field
    create: Create Document Field
        Params:
            - document_type: uid of Document Type
            - code: str - Unique Short name for field, max 50 symbols, should contain only latin letters, digits, and underscores
            - long_code: str - Unique Calculated field, max 150 symbols
            - title: str - Verbose name for field, max 100 symbols
            - description: str - optional
            - type: str - max 30 symbols (from pre-defined choices)
            - text_unit_type: str - (from pre-defined choices) default = sentences
            - value_detection_strategy: str - max 50 chars (from pre-defined choices)
            - unsure_choice_value: str - max 256 chars, default=null
            - unsure_thresholds_by_value: json
            - python_coded_field: str - max 100 chars
            - classifier_init_script: str
            - formula: str
            - depends_on_fields: array of uids, optional
            - confidence: str - max 100 chars (from pre-defined choices)
            - requires_text_annotations: bool, default=True
            - read_only: bool, default=False
            - category: int - id of DocumentFieldCategory instance
            - default_value: json
            - choices: str - \\n-separated list of choices
            - allow_values_not_specified_in_choices: bool - default=False
            - stop_words: json, optional
            - metadata: json, optional
            - training_finished: bool, default=False
            - dirty: bool, default=False
            - order: integer - default=0
            - trained_after_documents_number: integer, default=null
            - hidden_always: bool - default=False
            - hide_until_python: str, optional
            - hide_until_js: str, optional
            - display_yes_no: bool - default=False
    update: Update Document Field
    partial_update: Partial Update Document Field
    delete: Delete Document Field
    """
    queryset = DocumentField.objects \
        .select_related('document_type', 'modified_by') \
        .prefetch_related(Prefetch('depends_on_fields', queryset=DocumentField.objects.all().only('pk')))
    permission_classes = (TopStaffPermission,)
    options_serializer = DocumentFieldCreateSerializer
    response_unifier_serializer = DocumentFieldDetailSerializer

    def get_extra_data(self, qs):
        data = super().get_extra_data(qs)
        data['count_of_filtered_items'] = qs.count()
        data['count_of_items'] = DocumentField.objects.count()
        return data

    def destroy(self, request, *args, **kwargs):
        errors = dict()
        UsersTasksValidationAdmin.validate_running_tasks(request, errors)
        if errors:
            raise DRFValidationError(errors)

        return super().destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.delete()
        signals.document_field_deleted.send(self.__class__, user=None, document_field=instance)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return DocumentFieldCreateSerializer
        elif self.action == 'list':
            return DocumentFieldListSerializer
        return DocumentFieldDetailSerializer

    @action(detail=False, methods=['post'])
    def check_field_formula(self, request, **kwargs):
        """
        Check formula for new NOT SAVED Document Field
        Either "request.data.formula" or "request.data.hide_until_python" should be filled.
        Expects request data arguments:
        - formula: str OR
        - hide_until_python: str
        - field_type: str
        - document_type: str - document type uid
        - depends_on_fields: List[str] - list of field uids
        """
        from apps.document.admin import DocumentFieldFormulaCheck
        return DocumentFieldFormulaCheck(request.data).check()

    @action(detail=True, methods=['post'])
    def check_formula(self, request, **kwargs):
        """
        Check formula for EXISTING Document Field
        Expects request data arguments:
        - formula: str OR
        - hide_until_python: str
        - field_type: str
        - document_type: str - document type uid
        - depends_on_fields: List[str] - list of field uids
        Either "request.data.formula" or "request.data.hide_until_python" should be filled.
        """
        document_field = self.get_object()
        from apps.document.admin import DocumentFieldFormulaCheck
        return DocumentFieldFormulaCheck(request.data, document_field).check()

    @classmethod
    def clone_field(cls, source_field, target_document_type,
                    new_field_code=None, new_field_category=None,
                    clone_depends_on_fields=True, reindex=True):
        """
        Clone given Document Field
        :param source_field: source DocumentField object
        :param target_document_type: clone to DocumentType object
        :param new_field_code: str - code for new-created DocumentField
        :param new_field_category: DocumentFieldCategory object
        :param clone_depends_on_fields: bool - whether clone or not depends_on_fields as well
        :return: new DocumentField
        """
        source_document_type = source_field.document_type

        def _clone_field(source_field_pk, new_field_code=None, new_field_category=None):

            source_field = DocumentField.objects.get(pk=source_field_pk)
            field_detectors = source_field.field_detectors.all()
            depends_on_fields = source_field.depends_on_fields.all()

            new_field = source_field
            new_field.pk = None
            new_field.document_type = target_document_type

            if not new_field_code:
                new_field_code = new_field.make_unique_code()
            new_field.code = new_field_code

            if not new_field_category and source_document_type != target_document_type and source_field.category:
                new_field_category, category_created = DocumentFieldCategory.objects.get_or_create(
                    document_type=target_document_type,
                    name=source_field.category.name)
                if category_created:
                    new_field_category.order = source_field.order
                    new_field_category.save()
            new_field.category = new_field_category

            try:
                new_field.save()
            except IntegrityError:
                new_field.code = new_field.make_unique_code(new_field.code)

            for detector in field_detectors:
                detector.pk = None
                detector.field = new_field
                detector.save()

            if clone_depends_on_fields and depends_on_fields.exists():
                if source_document_type == target_document_type:
                    new_field.depends_on_fields.set(depends_on_fields)
                else:
                    for dep_field in depends_on_fields:
                        new_dep_field = _clone_field(dep_field.pk)
                        new_field.depends_on_fields.add(new_dep_field)

            return new_field

        new_field = _clone_field(source_field.pk,
                                 new_field_code=new_field_code,
                                 new_field_category=new_field_category)

        if source_field.family is None:
            new_family = DocumentFieldFamily.objects.create(
                code=source_field.code, title=source_field.title)
            source_field.family = new_family
            source_field.save()
            new_field.family = new_family
            new_field.save()

        if reindex:
            reindex_on_doc_type_change(target_document_type)

        return new_field

    @action(detail=True, methods=['post'])
    def clone(self, request, **kwargs):
        """
        Clone existing DocumentField and its depends_on_fields and detectors
        Params:
            - document_type: uid of target Document Type (required)
            - code: str - optional - code for new document field
        """
        form_data = request.data
        form = CloneDocumentFieldForm(form_data)

        if not form.is_valid():
            raise DRFValidationError(form.errors)

        source_field = self.get_object()
        target_document_type = form.cleaned_data['document_type']

        new_field = self.clone_field(source_field,
                                     target_document_type,
                                     new_field_code=form.cleaned_data['code'])

        data = DocumentFieldDetailSerializer(new_field).data
        return Response(data)

    @action(detail=True, methods=['post'])
    def pre_delete(self, request, **kwargs):
        """
        Get info about related objects for ready-to-delete document type.
        """
        obj = self.get_object()
        data = dict()

        # WARN! this collector takes too much time as it collects ALL objects includind
        # TextUnit, all ThingUsages, etc, so replaced with simplified version
        # using = db_router.db_for_write(obj._meta.model)
        # collector = NestedObjects(using=using)
        # collector.collect([obj])
        # full_data = collector.nested()
        # data['model_count'] = OrderedDict(sorted(
        #     [(cap_words(model._meta.verbose_name_plural), len(objs))
        #      for model, objs in collector.model_objs.items()
        #      if 'relationship' not in model._meta.verbose_name_plural]))

        data['delete_related_objects'] = dict(
            document_field_detectors=obj.field_detectors.count(),
        )
        data['affect_related_objects'] = dict(
            documents=Document.objects.filter(document_type=obj.document_type).count(),
            projects=Project.objects.filter(type=obj.document_type).count(),
        )
        return Response(data)


# --------------------------------------------------------
# Document Field Category Views
# --------------------------------------------------------

class FieldSimpleSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = DocumentField
        fields = ['id', 'category', 'code', 'title', 'order']

    def get_id(self, obj):
        return str(obj.pk)


class DocumentFieldCategoryListSerializer(serializers.ModelSerializer):
    fields_number = serializers.IntegerField()
    fields = FieldSimpleSerializer(source='documentfield_set', many=True)
    document_type_title = serializers.CharField()

    class Meta:
        model = DocumentFieldCategory
        fields = ['id', 'document_type', 'document_type_title', 'name', 'order',
                  'fields', 'fields_number', 'export_key']


class DocumentFieldCategoryCreateSerializer(ModelFormBasedSerializer):
    model_form_class = DocumentFieldCategoryForm
    fields = serializers.ListField(read_only=True)
    fields_number = serializers.IntegerField(read_only=True)

    class Meta:
        model = DocumentFieldCategory
        fields = ['id', 'document_type', 'name', 'order', 'fields', 'fields_number']

    def set_fields(self, instance: DocumentFieldCategory):
        field_uids = self.context['request'].data.get('fields')
        DocumentField.objects.filter(category=instance).update(category=None)
        DocumentField.objects.filter(uid__in=field_uids).update(category=instance)
        return instance

    def create(self, validated_data):
        instance = super().create(validated_data)
        return self.set_fields(instance)

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if self.context['view'].action == 'partial_update' and 'fields' not in self.context['request'].data:
            return instance
        return self.set_fields(instance)


class DocumentFieldCategoryOptionsSerializer(DocumentFieldCategoryCreateSerializer):
    fields = FieldSimpleSerializer(source='documentfield_set', many=True)

    class Meta:
        model = DocumentFieldCategory
        fields = ['id', 'document_type', 'name', 'order', 'fields']


class DocumentFieldCategoryViewSet(JqListAPIMixin,
                                   APIResponseMixin,
                                   APIFormFieldsMixin,
                                   viewsets.ModelViewSet):
    """
    list: DocumentFieldCategory List\n
    retrieve: Retrieve DocumentFieldCategory\n
    create: Create DocumentFieldCategory\n
        Params:
            - document_type: uid
            - name: str - Verbose name for field category, max 100 symbols
            - order: int
            - fields: array of field uids
    update: Update Document Type
        Params:
            - document_type: uid
            - name: str - Verbose name for field category, max 100 symbols
            - order: int
            - fields: array of field uids
    partial_update: Partial Update DocumentFieldCategory
    delete: Delete DocumentFieldCategory
    """
    queryset = DocumentFieldCategory.objects.all()

    permission_classes = (TopStaffPermission,)
    options_serializer = DocumentFieldCategoryOptionsSerializer

    def get_queryset(self):
        qs = super().get_queryset().select_related('document_type').prefetch_related('documentfield_set')
        return qs.annotate(fields_number=Count('documentfield'),
                           document_type_title=F('document_type__title'))

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return DocumentFieldCategoryCreateSerializer
        return DocumentFieldCategoryListSerializer

    def get_fields_data(self):
        # substitute data for /form-fields/ API
        fields = super().get_fields_data()
        fields['document_type']['allow_null'] = False
        fields['fields'].update({
            "ui_element": {
                "type": "select",
                "multichoice": True,
                "data_type": "array"
            },
            "allow_null": True,
            "required": False,
            "choices": {i['pk']: f'{i["document_type__code"]}: {i["title"]}'
                        for i in DocumentField.objects.filter(document_type__isnull=False).select_related('document_type').values('pk', 'title', 'document_type__code')},
        })
        return fields

    def patched_object_response(self, response):
        obj_id = response.data.get('id')
        if obj_id:
            return Response(DocumentFieldCategoryListSerializer(self.get_queryset().get(pk=obj_id)).data)
        return response

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return self.patched_object_response(response)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return self.patched_object_response(response)


# --------------------------------------------------------
# Document Field Detector Views
# --------------------------------------------------------

class DocumentFieldDetectorDetailSerializer(SimpleRelationSerializer):
    include_regexps = serializers.SerializerMethodField()
    field = serializers.CharField()

    class Meta:
        model = DocumentFieldDetector
        fields = ['uid', 'category', 'field',
                  'field__code', 'field__title', 'field__uid', 'field__type',
                  'field__document_type__title',
                  'exclude_regexps', 'definition_words', 'include_regexps',
                  'regexps_pre_process_lower', 'detected_value', 'extraction_hint', 'text_part']

    def get_field(self, obj):
        return obj.field.title

    def get_include_regexps(self, obj):
        return obj.include_regexps.split('\n') if obj.include_regexps and obj.field else None


def check(func):
    def wrapper(self, value):
        try:
            func(self, value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))
        return value

    return wrapper


class DocumentFieldDetectorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFieldDetector
        fields = '__all__'

    @check
    def validate(self, data):
        if self.context['request'].method == 'PATCH' and 'field' not in data:
            return
        DetectorFieldMatcher.validate_detected_value(data['field'].type,
                                                     data.get('detected_value'))


class DocumentFieldDetectorViewSet(JqListAPIMixin,
                                   APIFormFieldsMixin,
                                   APIResponseMixin,
                                   viewsets.ModelViewSet):
    """
    list: Document Field List
    retrieve: Retrieve Document Field
    create: Create Document Field
        Params:
            - fields: uid
            - category: str - max 64 symbols (from pre-defined choices)
            - exclude_regexps: str - optional
            - definition_words: str - optional
            - include_regexps: str - optional
            - regexps_pre_process_lower: bool, default=False
            - detected_value: str - max 256 chars
            - extraction_hint: str - max 30 chars (from pre-defined choices)
            - text_part: str - max 30 chars (from pre-defined choices)
    update: Update Document Field
        Params:
            - fields: uid
            - category: str - max 64 symbols (from pre-defined choices)
            - exclude_regexps: str - optional
            - definition_words: str - optional
            - include_regexps: str - optional
            - regexps_pre_process_lower: bool, default=False
            - detected_value: str - max 256 chars
            - extraction_hint: str - max 30 chars (from pre-defined choices)
            - text_part: str - max 30 chars (from pre-defined choices)
    partial_update: Partial Update Document Field
    delete: Delete Document Field
    """
    queryset = DocumentFieldDetector.objects.select_related('field')
    permission_classes = (TopStaffPermission,)
    options_serializer = DocumentFieldDetectorCreateSerializer
    response_unifier_serializer = DocumentFieldDetectorDetailSerializer

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return DocumentFieldDetectorCreateSerializer
        return DocumentFieldDetectorDetailSerializer

    def get_extra_data(self, qs):
        data = super().get_extra_data(qs)
        data['count_of_filtered_items'] = qs.count()
        data['count_of_items'] = DocumentFieldDetector.objects.count()
        return data


# --------------------------------------------------------
# Document Type Views
# --------------------------------------------------------

class FieldDataSerializer(DocumentFieldDetailSerializer):
    category = DocumentFieldCategorySimpleSerializer(many=False, read_only=True)

    class Meta:
        fields = DocumentFieldDetailSerializer.Meta.fields + ['category']
        model = DocumentField


class DocumentTypeDetailSerializer(SimpleRelationSerializer):
    fields_data = FieldDataSerializer(source='fields', many=True, read_only=True)
    fields_number = serializers.IntegerField()
    created_by = UserSerializer(many=False)
    modified_by = UserSerializer(many=False)
    categories = DocumentFieldCategorySimpleSerializer(many=True, read_only=True)

    class Meta:
        model = DocumentType
        fields = ['uid', 'title', 'code', 'fields_data', 'search_fields', 'modified_by__username',
                  'editor_type', 'created_by', 'created_date', 'modified_by', 'modified_date',
                  'metadata', 'fields_number', 'categories']

    def to_representation(self, instance):
        ret = dict(super().to_representation(instance))
        for field in ret.get('fields_data'):
            # set search field flag
            field['default'] = field['uid'] in ret['search_fields']
        # del ret['search_fields']
        return ret


class DocumentTypeCreateSerializer(ModelFormBasedSerializer):
    model_form_class = DocumentTypeForm
    fields = FieldSimpleSerializer(many=True, read_only=True)
    categories = DocumentFieldCategorySimpleSerializer(many=True, read_only=True)

    class Meta:
        model = DocumentType
        fields = ['uid', 'title', 'code',
                  'categories',
                  'fields', 'search_fields', 'editor_type',
                  'field_code_aliases', 'metadata']

    def set_fields(self, instance: DocumentType):
        fields_data = self.context['request'].data.get('fields')
        if fields_data is not None and instance is not None and instance.pk:
            fields_data = {f['id']: f for f in fields_data}
            for field in list(instance.fields.all()):  # type: DocumentField
                field_patch = fields_data.get(field.uid)
                if not field_patch:
                    field.delete()
                else:
                    field.category_id = field_patch.get('category')
                    field.order = field_patch.get('order', 0)
                    field.save(update_fields=['category', 'order'])

        return instance

    def set_categories(self, instance: DocumentType):
        categories_data = self.context['request'].data.get('categories')
        if categories_data is not None and instance is not None and instance.pk:
            new_categories_data = [c for c in categories_data if not c.get('id')]

            categories_data = {c['id']: c for c in categories_data if c.get('id')}
            for category in list(instance.categories.all()):  # type: DocumentFieldCategory
                category_patch = categories_data.get(category.pk)
                if not category_patch:
                    category.delete()
                else:
                    category.name = category_patch.get('name')
                    category.order = category_patch.get('order', 0)
                    category.save(update_fields=['name', 'order'])

            if new_categories_data:
                for c in new_categories_data:
                    c.update({'document_type': instance})
                DocumentFieldCategory.objects.bulk_create(
                    [DocumentFieldCategory(**i) for i in new_categories_data])

        return instance

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance = self.set_fields(instance)
        instance = self.set_categories(instance)
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if self.context['view'].action == 'partial_update':
            if 'fields' in self.context['request'].data:
                instance = self.set_fields(instance)
            if 'categories' in self.context['request'].data:
                instance = self.set_categories(instance)
            return instance
        instance = self.set_fields(instance)
        instance = self.set_categories(instance)
        return instance

    def validate_may_delete_data(self, errors_dst: dict):
        field_repo = DocumentFieldRepository()
        request = self.context['request']
        if as_bool(request.GET, PARAM_OVERRIDE_WARNINGS):
            return

        fields_data = request.data.get('fields')
        if fields_data is not None and self.instance is not None and self.instance.pk:
            field_values_to_delete = dict()
            fields_data = {f['id']: f for f in fields_data}
            for field in list(self.instance.fields.all()):  # type: DocumentField
                field_patch = fields_data.get(field.uid)
                if not field_patch:
                    field_values_to_delete[field.code] = field_repo.get_count_by_field(field.pk)
            if field_values_to_delete:
                field_values_to_delete = ';<br />\n'.join([f'{field}: {n} values'
                                                           for field, n in field_values_to_delete.items()])
                errors_dst['warning:will_delete_values'] = f'You are going to delete document fields. ' \
                                                           f'This will cause deleting all their stored field values:<br/>\n{field_values_to_delete}.'

    def is_valid(self, raise_exception=False):
        super().is_valid()
        UsersTasksValidationAdmin.validate_running_tasks(self.context['request'], self.errors)
        self.validate_may_delete_data(self.errors)
        return True

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        signals.document_type_changed.send(self.__class__, user=None, document_type=instance)
        return instance


class DocumentTypeOptionsSerializer(DocumentTypeCreateSerializer):
    field_categories = serializers.PrimaryKeyRelatedField(
        source='fields__category',
        queryset=DocumentFieldCategory.objects.all(), allow_empty=True, allow_null=True)
    fields = FieldSimpleSerializer(many=True, required=False)

    class Meta:
        model = DocumentType
        fields = ['uid', 'title', 'code', 'fields', 'search_fields', 'editor_type',
                  'field_categories',
                  'created_by', 'created_date', 'modified_by', 'modified_date']


class DocumentTypeViewSet(JqListAPIMixin,
                          APIResponseMixin,
                          APIFormFieldsMixin,
                          viewsets.ModelViewSet):
    """
    list: Document Type List\n
    retrieve: Retrieve Document Type
    create: Create Document Type\n
        Params:
            - code: str - Short name for field, max 50 symbols
            - title: str - Verbose name for field, max 100 symbols
            - field_code_aliases: json - Aliases of field codes for document import purposes
            - fields: array of objects like [{id: uid, category: id, order: int}, ...]
            - search_fields: array of uids - set of fields to filter/sort on Document list page
            - editor_type: str - max 100 symbols (from pre-defined choices)
            - metadata: json - optional
    update: Update Document Type
        Params:
            - code: str - Short name for field, max 50 symbols
            - title: str - Verbose name for field, max 100 symbols
            - field_code_aliases: json - Aliases of field codes for document import purposes
            - fields: array of objects like [{id: uid, category: id, order: int}, ...]
            - search_fields: array of uids - set of fields to filter/sort on Document list page
            - editor_type: str - max 100 symbols (from pre-defined choices)
            - metadata: json - optional
    partial_update: Partial Update Document Type
    delete: Delete Document Type
    """
    queryset = DocumentType.objects.select_related('modified_by') \
        .prefetch_related('search_fields', 'fields', 'fields__category',
                          Prefetch('fields__depends_on_fields',
                                   queryset=DocumentField.objects.all().only('pk')))

    permission_classes = (TopStaffPermission,)
    options_serializer = DocumentTypeOptionsSerializer
    response_unifier_serializer = DocumentTypeDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(fields_number=Count('fields'))

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return DocumentTypeCreateSerializer
        return DocumentTypeDetailSerializer

    def get_extra_data(self, qs):
        data = super().get_extra_data(qs)
        data['count_of_filtered_items'] = qs.count()
        data['count_of_items'] = DocumentType.objects.count()
        return data

    def destroy(self, request, *args, **kwargs):
        errors = dict()
        UsersTasksValidationAdmin.validate_running_tasks(request, errors)
        if errors:
            raise DRFValidationError(errors)

        instance = self.get_object()

        if instance.project_set.exists():
            from apps.document.app_vars import ALLOW_REMOVE_DOC_TYPE_WITH_PROJECT
            if ALLOW_REMOVE_DOC_TYPE_WITH_PROJECT.val:
                _ = super().destroy(request, *args, **kwargs)
                return Response({
                    'detail': f'Task "Delete Document Types" is started for document types: {instance.title}.'},
                    status=200)
            else:
                return Response(
                    {'detail': f'Selected Document Type has {instance.project_set.count()} related project(s), '
                     'please delete related project(s) first.'},
                    status=403)

        return super().destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        from apps.document.app_vars import ALLOW_REMOVE_DOC_TYPE_WITH_PROJECT
        if ALLOW_REMOVE_DOC_TYPE_WITH_PROJECT.val and instance.project_set.exists():
            from apps.task.tasks import _call_task
            from apps.document.tasks import DeleteDocumentTypes
            _call_task(DeleteDocumentTypes,
                       document_type_ids=[instance.pk],
                       user_id=self.request.user.id)
        else:
            instance.delete()
        signals.document_type_deleted.send(self.__class__, user=None, document_type=instance)

    def get_fields_data(self):
        """
        Patch for /form-field endpoint
        """
        fields = super().get_fields_data()
        fields['fields']['field_categories'] = fields.pop('field_categories', None)
        fields['fields']['ui_element'] = fields['search_fields']['ui_element']
        fields['fields']['field_type'] = fields['search_fields']['field_type']
        fields['fields']['choices'] = fields['search_fields']['choices']
        fields['modified_by']['required'] = False
        return fields

    @action(detail=False, methods=['put'])
    def import_doc_type(self, request, *_args, **_kwargs):
        if 'file' not in request.data:
            raise ParseError("Empty content")
        f = request.data['file']
        update_cache = request.data.get('update_cache', True)
        action = request.data.get('action', 'validate')
        source_version = request.data.get('source_version', None)

        task_id = call_task(ImportDocumentType,
                            **{'document_type_config_json_file': f,
                               'update_cache': update_cache,
                               'action': action,
                               'source_version': source_version})
        return Response(status=200, data={'task_id': task_id})

    @action(detail=True, methods=['get'])
    def export_doc_type(self, request, *_args, **_kwargs):
        document_type = self.get_object()
        version = request.data.get('target_version', None)
        json_data, version = get_app_config_versioned_dump([document_type.code], version)
        if version >= TAGGED_VERSION:
            json_data = f'{{"version": "{version}", "data": {json_data} }}'
        return download(json_data, f'{document_type.code}_{datetime.date.today()}')

    @classmethod
    def clone_type(cls, source_document_type: DocumentType, code: str, title: str):
        """
        Clone given Document Type
        :param source_document_type: source DocumentType object
        :param code: str - code for new-created DocumentType
        :param title: str - title for new-created DocumentType
        :return: new DocumentType
        """
        new_document_type = DocumentType.objects.get(pk=source_document_type.pk)
        new_document_type.pk = None
        new_document_type.code = code
        new_document_type.title = title
        new_document_type.save()

        # clone fields
        new_document_type.fields.clear()
        # sort field before cloning as they may have dependencies
        field_deps = [(f.pk, set(f.depends_on_fields.values_list('pk', flat=True)))
                      for f in source_document_type.fields.all()]
        sorted_field_ids = list(topological_sort(field_deps))
        field_objects_map = dict([(obj.pk, obj) for obj in source_document_type.fields.all()])
        sorted_fields = [field_objects_map[pk] for pk in sorted_field_ids]

        for source_field in sorted_fields:
            new_field = DocumentFieldViewSet.clone_field(
                source_field, new_document_type, source_field.code,
                clone_depends_on_fields=False,
                reindex=False
            )
            depends_on_fields_codes = source_field.depends_on_fields.values_list('code', flat=True)
            depends_on_fields = new_document_type.fields.filter(code__in=depends_on_fields_codes)
            new_field.depends_on_fields.set(depends_on_fields)

        # set search_fields
        search_field_codes = source_document_type.search_fields.values_list('code', flat=True)
        new_search_fields = new_document_type.fields.filter(code__in=search_field_codes)
        new_document_type.search_fields.set(new_search_fields)

        reindex_on_doc_type_change(new_document_type)

        return new_document_type

    @action(detail=True, methods=['post'])
    def clone(self, request, **kwargs):
        """
        Clone existing Document Type and its fields
        Params:
            - title: str - title for new document type (required)
            - code: str - code for new document type (required)
        """
        form_data = request.data
        form = CloneDocumentTypeForm(form_data)

        if not form.is_valid():
            raise DRFValidationError(form.errors)

        source_document_type = self.get_object()

        # create new DT object
        new_document_type = self.clone_type(source_document_type,
                                            code=form.cleaned_data['code'],
                                            title=form.cleaned_data['title'])

        data = DocumentTypeDetailSerializer(new_document_type).data
        return Response(data)

    @action(detail=True, methods=['post'])
    def pre_delete(self, request, **kwargs):
        """
        Get info about related objects for ready-to-delete document type.
        """
        obj = self.get_object()
        data = dict()

        # WARN! this collector takes too much time as it collects ALL objects includind
        # TextUnit, all ThingUsages, etc, so replaced with simplified version
        # using = db_router.db_for_write(obj._meta.model)
        # collector = NestedObjects(using=using)
        # collector.collect([obj])
        # # full_data = collector.nested()
        # data['model_count'] = OrderedDict(sorted(
        #     [(cap_words(model._meta.verbose_name_plural), len(objs))
        #      for model, objs in collector.model_objs.items()
        #      if 'relationship' not in model._meta.verbose_name_plural]))

        data['delete_related_objects'] = dict(
            document_fields=obj.fields.count(),
            document_field_detectors_count=DocumentFieldDetector.objects.filter(field__document_type=obj).count(),
            documents=Document.all_objects.filter(document_type=obj).count(),
            documents_delete_pending=Document.all_objects.filter(document_type=obj, delete_pending=True).count(),
            projects=obj.project_set.count(),
            projects_delete_pending=obj.project_set.filter(delete_pending=True).count()
        )

        # Get detailed data
        # data['document_fields'] = obj.fields.order_by('title') \
        #     .annotate(documents=Count('document')) \
        #     .values('pk', 'code', 'title')
        # data['projects'] = obj.project_set.order_by('name') \
        #     .annotate(documents=Count('document')) \
        #     .values('pk', 'name', 'documents')
        return Response(data)


# --------------------------------------------------------
# Annotator Views
# --------------------------------------------------------

class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldAnnotation
        fields = ['pk', 'document', 'field', 'value',
                  'location_start', 'location_end', 'location_text',
                  'modified_by', 'modified_date']


def do_save_document_field_value(request_data: Dict, user) -> \
        Tuple[Document, DocumentField, Dict]:
    """
    Creates or updates document's field value with or w/o annotations.
    """
    field_repo = DocumentFieldRepository()

    if 'pk' in request_data and request_data['pk']:
        ant_model = FieldAnnotation.objects.filter(pk=request_data['pk']).first()  # type: FieldAnnotation
        if ant_model:
            document = ant_model.document
        else:
            raise Exception('do_save_document_field_value: ' +
                            f'FieldAnnotation(pk={request_data["pk"]}) was not found')
    elif 'document' in request_data:
        document = DocumentRepository().get_document_by_id(request_data['document'])
    else:
        raise Exception('Request data should contain either field annotation\'s "pk" or '
                        '"document" parameter, but none was provided.')

    field = field_repo.get_document_field_by_id(request_data['field'])

    annotation_value = request_data.get('value')
    typed_field = TypedField.by(field)

    if isinstance(typed_field, RelatedInfoField):
        annotation_value = None

    if isinstance(typed_field, BooleanField) and annotation_value is not None and \
            not isinstance(annotation_value, bool):
        annotation_value = True if str(annotation_value).lower() == 'yes' else \
            False if str(annotation_value).lower() == 'no' else None

    location_start = request_data.get('location_start')
    location_end = request_data.get('location_end')
    location_text = None
    if location_start is not None and location_end is not None:
        location_text = document.full_text[location_start:location_end]
    if annotation_value and isinstance(annotation_value, str):
        location_text = annotation_value

    all_fields = document.document_type.fields \
        .all() \
        .prefetch_related(Prefetch('depends_on_fields', queryset=DocumentField.objects.only('uid').all()))
    all_fields = list(all_fields)
    current_field_values = {f.code: None for f in all_fields}
    actual_field_values = field_repo.get_field_code_to_python_value(
        document_type_id=document.document_type.pk,
        doc_id=document.pk,
        field_codes_only=None)
    current_field_values.update(actual_field_values)

    # try to detect field value
    field_detection_strategy = FIELD_DETECTION_STRATEGY_REGISTRY[
        field.value_detection_strategy]  # type: FieldDetectionStrategy

    new_field_value_dto = None  # type: Optional[FieldValueDTO]
    if not new_field_value_dto:
        # try to detect field value by the field itself
        annotation_value, hint = typed_field.get_or_extract_value(
            document, annotation_value, None, location_text)
        annotation_value = typed_field.annotation_value_python_to_json(annotation_value)

        if location_start is not None \
                and location_end is not None \
                and annotation_value is None \
                and typed_field.requires_value:
            raise NoValueProvidedOrLocated(f'Field {field.code} is value-aware. '
                                           'There was no value provided and no suitable '
                                           'value located in the provided text. '
                                           'Storing empty value makes no sense.')
            # And saving None to a field without providing annotation means - clearing the field.

        field_value = typed_field.build_json_field_value_from_json_ant_values([annotation_value]) \
            if isinstance(typed_field, MultiValueField) and \
               not isinstance(typed_field, RelatedInfoField) else annotation_value
        new_field_value_dto = FieldValueDTO(field_value=field_value, annotations=[])

        if location_start is not None and location_end is not None:
            ant = AnnotationDTO(
                extraction_hint_name=hint,
                annotation_value=annotation_value,
                location_in_doc_start=location_start,
                location_in_doc_end=location_end)
            new_field_value_dto.annotations.append(ant)

    field_val, field_ants = field_repo.update_field_value_with_dto(
        document=document, field=field, field_value_dto=new_field_value_dto,
        user=user)

    field_value = {
        'document': document.pk,
        'document_name': document.name,
        'field': field.uid,
        'field_name': field.code,
        'value': field_val.value,
        'project': document.project.name,
        'modified_by': user.pk,
        'modified_date': datetime.datetime.now(),
        'pk': None,
        'location_start': location_start,
        'location_end': location_end,
        'location_text': location_text
    }

    annotation = field_ants[0] if field_ants else None
    if annotation:
        field_value['value'] = annotation.value
        field_value['pk'] = annotation.pk
        field_value['location_start'] = annotation.location_start
        field_value['location_end'] = annotation.location_end
        field_value['location_text'] = annotation.location_text

    return document, field, field_value


def cache_and_detect_field_values(doc: Document,
                                  user: User,
                                  updated_fields: Set[DocumentField]):
    # Next start field re-detection and re-caching in Celery because there can be other fields
    # depending on the changed fields.
    dcptrs = DocDetectFieldValuesParams(doc.pk,
                                        updated_field_codes=[field.code for field in updated_fields])
    run_detect_field_values_for_document(dcptrs, user=user)


def do_delete_document_field_value(ant_id: int, user) -> Tuple[Document, DocumentField, Dict]:
    """
    Delete an annotation / DocumentFieldValue / mark it as removed
    """
    field_repo = DocumentFieldRepository()
    ant_model = FieldAnnotation.objects.get(pk=ant_id)
    doc, field, ant_model = field_repo.delete_field_annotation_and_update_field_value(ant_model, user)
    ant_dict = AnnotationSerializer(ant_model).data
    return doc, field, ant_dict


def render_error_json(operation_uid, e: Exception) -> Dict:
    return {'operation_uid': operation_uid,
            'status': 'error',
            'exception_type': type(e).__name__,
            'message': str(e),
            'exception': traceback.format_exc()}


class AnnotationViewSet(viewsets.ModelViewSet):
    """
    list: Annotation (Document Field Value) List
    retrieve: Retrieve Annotation (Document Field Value)
    create: Create Annotation (Document Field Value)
    update: Update Annotation (Document Field Value)
    delete: Delete Annotation (Document Field Value)
    """
    field_repo = DocumentFieldRepository()
    queryset = field_repo.get_all_docfieldvalues()
    serializer_class = AnnotationSerializer
    http_method_names = ['get', 'put', 'post', 'delete']
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = super().get_queryset()
        document_id = self.request.GET.get('document_id')
        if document_id:
            qs = qs.filter(document_id=document_id)
        return qs

    def update(self, request, *args, **kwargs):
        try:
            doc, field, res = do_save_document_field_value(request.data, request.user)
            cache_and_detect_field_values(doc,
                                          user=request.user,
                                          updated_fields={field})
        except Exception as e:
            res = render_error_json(None, e)

        return Response(res)

    def create(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @action(detail=False, methods=['put'])
    def annotate(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            doc, field, res = do_delete_document_field_value(kwargs['pk'], request.user)
            cache_and_detect_field_values(doc, user=request.user, updated_fields={field})
        except Exception as e:
            res = render_error_json(None, e)
        return Response(res)

    @action(detail=False, methods=['post'])
    def suggest(self, request, *args, **kwargs):
        """
        Suggest field value before creating an annotation.
        """
        annotator_data = request.data
        doc = Document.objects.get(pk=annotator_data['document'])
        document_field = DocumentField.objects.get(pk=annotator_data['field'])
        location_text = annotator_data['quote']

        typed_field = TypedField.by(document_field)

        if document_field.is_detectable():
            field_value = field_detection.suggest_field_value(doc=doc, field=document_field)
        else:
            field_value = typed_field.suggest_value(doc, location_text)

        return Response({'suggested_value': field_value})

    @action(detail=False, methods=['put'])
    def batch(self, request, *args, **kwargs):
        """
        Create batch of annotations\n
            PUT Params:
                 - operation_uid: uid
                 - action: str ["save", "delete"]
                 - id: int - PK of DocumentFieldValue
                 - data: {"document": id, "field": uid, "location_start": int, "location_end": int, "value": val}
        """
        batch_commands = request.data

        res = []
        documents_to_cache = defaultdict(set)
        for cmd_num, cmd in enumerate(batch_commands):
            operation_uid = cmd.get('operation_uid')
            try:
                action = cmd['action']

                if action == 'delete':
                    pk = cmd['id']
                    doc, field, deleted_field_value = do_delete_document_field_value(pk, request.user)
                    documents_to_cache[doc].add(field)
                    res.append({'operation_uid': operation_uid, 'status': 'success', 'data': deleted_field_value})
                elif action == 'save':
                    data = cmd['data']
                    doc, field, saved_field_value = do_save_document_field_value(data, request.user)
                    documents_to_cache[doc].add(field)
                    res.append({'operation_uid': operation_uid, 'status': 'success', 'data': saved_field_value})
            except Exception as e:
                res.append(render_error_json(operation_uid, e))

        for doc, fields in documents_to_cache.items():
            if doc:
                cache_and_detect_field_values(doc, user=request.user, updated_fields=fields)

        return Response(res)


# --------------------------------------------------------
# Stats View
# --------------------------------------------------------

class StatsAPIView(rest_framework.views.APIView):

    def get(self, request, *args, **kwargs):

        # get admin tasks data
        task_api_module = get_api_module('task')
        task_api_view = task_api_module.TaskViewSet(request=request, action='stats')
        task_api_view.format_kwarg = {}
        admin_task_df = pd.DataFrame(task_api_view.list(request=request).data)
        admin_task_total_count = admin_task_df.shape[0]
        admin_task_statuses = (SUCCESS, FAILURE, PENDING, REVOKED)
        admin_task_by_status_count = {i: 0 for i in admin_task_statuses}
        current_admin_task_by_status_count = dict(admin_task_df.groupby(['status']).size()) \
            if not admin_task_df.empty else 0
        admin_task_by_status_count.update(current_admin_task_by_status_count)

        # get projects data
        project_api_view = project_api_module.ProjectViewSet(request=request, action='stats')
        project_api_view.format_kwarg = {}
        project_data = project_api_view.list(request=request).data
        if not project_data:
            project_total_count = project_completed_count = project_completed_weight = \
                project_documents_total_count = \
                project_documents_completed_count = project_documents_completed_weight = 0
        else:
            project_df = pd.DataFrame(project_data)
            project_df['progress'] = project_df.apply(
                lambda row: (row['reviewed_documents_count'] / row['total_documents_count'] * 100)
                if row['total_documents_count'] else 0, axis=1)
            project_df['completed'] = np.where(project_df['progress'] == 100, 1, 0)
            project_total_count = project_df.shape[0]
            project_df_sum = project_df.sum()
            project_completed_count = project_df_sum.completed
            project_completed_weight = round(project_completed_count / project_total_count * 100, 1)
            project_documents_total_count = project_df_sum.total_documents_count
            project_documents_completed_count = project_df_sum.reviewed_documents_count
            project_documents_completed_weight = round(
                project_documents_completed_count / project_documents_total_count * 100, 1)

        # set counts depending on user role
        documents = Document.objects
        document_properties = DocumentProperty.objects
        document_tags = DocumentTag.objects
        document_notes = DocumentNote.objects
        document_relations = DocumentRelation.objects
        document_clusters = DocumentCluster.objects
        text_units = TextUnit.objects
        tu_tags = TextUnitTag.objects
        tu_properties = TextUnitProperty.objects
        tu_classifications = TextUnitClassification.objects
        tu_classification_suggestions = TextUnitClassifierSuggestion.objects
        tuc_suggestion_types = TextUnitClassifierSuggestion.objects.distinct('class_name')
        tu_notes = TextUnitNote.objects
        tu_clusters = TextUnitCluster.objects

        terms = Term.objects
        term_usages = TermUsage.objects

        amount_usages = AmountUsage.objects
        citation_usages = CitationUsage.objects
        copyright_usages = CopyrightUsage.objects
        court_usages = CourtUsage.objects
        currency_usages = CurrencyUsage.objects
        date_duration_usages = DateDurationUsage.objects
        date_usages = DateUsage.objects
        definition_usages = DefinitionUsage.objects
        distance_usages = DistanceUsage.objects
        geo_entities = GeoEntity.objects
        geo_entity_usages = GeoEntityUsage.objects
        geo_aliases = GeoAlias.objects
        geo_alias_usages = GeoAliasUsage.objects
        geo_relations = GeoRelation.objects
        parties = Party.objects
        party_usages = PartyUsage.objects
        percent_usages = PercentUsage.objects
        ratio_usages = RatioUsage.objects
        regulation_usages = RegulationUsage.objects
        trademark_usages = TrademarkUsage.objects
        url_usages = UrlUsage.objects

        if request.user.is_reviewer:
            document_filter_opts = dict(document__taskqueue__reviewers=request.user)
            tu_filter_opts = dict(text_unit__document__taskqueue__reviewers=request.user)

            documents = documents.filter(taskqueue__reviewers=request.user).distinct()
            document_properties = document_properties.filter(**document_filter_opts).distinct()
            document_tags = document_tags.filter(**document_filter_opts).distinct()
            document_notes = document_notes.filter(**document_filter_opts).distinct()
            document_relations = document_relations.filter(
                document_a__taskqueue__reviewers=request.user,
                document_b__taskqueue__reviewers=request.user).distinct()
            document_clusters = document_clusters.filter(
                documents__taskqueue__reviewers=request.user).distinct()
            text_units = text_units.filter(**document_filter_opts).distinct()
            tu_tags = tu_tags.filter(**tu_filter_opts).distinct()
            tu_properties = tu_properties.filter(**tu_filter_opts).distinct()
            tu_classifications = tu_classifications.filter(**tu_filter_opts).distinct()
            tu_classification_suggestions = tu_classification_suggestions.filter(
                **tu_filter_opts).distinct()
            tuc_suggestion_types = tuc_suggestion_types.filter(**tu_filter_opts).distinct(
                'class_name')
            tu_notes = tu_notes.filter(**tu_filter_opts).distinct()
            tu_clusters = tu_clusters.filter(
                text_units__document__taskqueue__reviewers=request.user).distinct()
            terms = terms.filter(
                termusage__text_unit__document__taskqueue__reviewers=request.user).distinct()
            term_usages = term_usages.filter(**tu_filter_opts).distinct()

            amount_usages = amount_usages.filter(**tu_filter_opts).distinct()
            citation_usages = citation_usages.filter(**tu_filter_opts).distinct()
            copyright_usages = copyright_usages.filter(**tu_filter_opts).distinct()
            court_usages = court_usages.filter(**tu_filter_opts).distinct()
            currency_usages = currency_usages.filter(**tu_filter_opts).distinct()
            date_duration_usages = date_duration_usages.filter(**tu_filter_opts).distinct()
            date_usages = date_usages.filter(**tu_filter_opts).distinct()
            definition_usages = definition_usages.filter(**tu_filter_opts).distinct()
            distance_usages = distance_usages.filter(**tu_filter_opts).distinct()

            geo_aliases = geo_aliases.filter(
                geoaliasusage__text_unit__document__taskqueue__reviewers=request.user).distinct()
            geo_alias_usages = geo_alias_usages.filter(**tu_filter_opts).distinct()
            geo_entities = geo_entities.filter(
                geoentityusage__text_unit__document__taskqueue__reviewers=request.user).distinct()
            geo_entity_usages = geo_entity_usages.filter(**tu_filter_opts).distinct()
            geo_relations = geo_relations.filter(
                entity_a__geoentityusage__text_unit__document__taskqueue__reviewers=request.user,
                entity_b__geoentityusage__text_unit__document__taskqueue__reviewers=request.user) \
                .distinct()

            parties = parties.filter(
                partyusage__text_unit__document__taskqueue__reviewers=request.user).distinct()
            party_usages = party_usages.filter(**tu_filter_opts).distinct()
            percent_usages = percent_usages.filter(**tu_filter_opts).distinct()
            ratio_usages = ratio_usages.filter(**tu_filter_opts).distinct()
            regulation_usages = regulation_usages.filter(**tu_filter_opts).distinct()
            trademark_usages = trademark_usages.filter(**tu_filter_opts).distinct()
            url_usages = url_usages.filter(**tu_filter_opts).distinct()

        data = {
            "document_count": documents.count(),
            "document_property_count": document_properties.count(),
            "document_tag_count": document_tags.count(),
            "document_note_count": document_notes.count(),
            "document_relation_count": document_relations.count(),
            "document_cluster_count": document_clusters.count(),
            "text_unit_count": text_units.count(),
            "text_unit_tag_count": tu_tags.count(),
            "text_unit_property_count": tu_properties.count(),
            "text_unit_classification_count": tu_classifications.count(),
            "text_unit_classification_suggestion_count": tu_classification_suggestions.count(),
            "text_unit_classification_suggestion_type_count": tuc_suggestion_types.count(),
            "text_unit_note_count": tu_notes.count(),
            "text_unit_cluster_count": tu_clusters.count(),
            "amount_usage_count": amount_usages.count(),
            "citation_usage_count": citation_usages.count(),
            "copyright_usage_count": copyright_usages.count(),
            "court_count": Court.objects.count(),
            "court_usage_count": court_usages.count(),
            "currency_usage_count": currency_usages.count(),
            "date_duration_usage_count": date_duration_usages.count(),
            "date_usage_count": date_usages.count(),
            "definition_usage_count": definition_usages.count(),
            "distance_usage_count": distance_usages.count(),

            "geo_alias_count": geo_aliases.count(),
            "geo_alias_usage_count": geo_alias_usages.count(),
            "geo_entity_count": geo_entities.count(),
            "geo_entity_usage_count": geo_entity_usages.count(),
            "geo_relation_count": geo_relations.count(),
            "party_count": parties.count(),
            "party_usage_count": party_usages.count(),
            "percent_usage_count": percent_usages.count(),
            "ratio_usage_count": ratio_usages.count(),
            "regulation_usage_count": regulation_usages.count(),
            "trademark_usage_count": trademark_usages.count(),
            "url_usage_count": url_usages.count(),
            "term_count": terms.count(),
            "term_usage_count": term_usages.count(),

            "project_total_count": project_total_count,
            "project_completed_count": project_completed_count,
            "project_completed_weight": project_completed_weight,
            "project_documents_total_count": project_documents_total_count,
            "project_documents_completed_count": project_documents_completed_count,
            "project_documents_completed_weight": project_documents_completed_weight,

            "admin_task_total_count": admin_task_total_count,
            "admin_task_by_status_count": admin_task_by_status_count,

            "backend_version_number": settings.VERSION_NUMBER
        }
        return Response(data)


# --------------------------------------------------------
# Document Field Value Views
# --------------------------------------------------------

class DocumentFieldValueSerializer(serializers.ModelSerializer):
    modified_by_username = serializers.CharField(read_only=True)
    field_name = serializers.CharField(read_only=True)
    project = serializers.SerializerMethodField()
    project_id = serializers.IntegerField(read_only=True)
    document_name = serializers.CharField(read_only=True)
    document_status = serializers.CharField(read_only=True)
    location_text = serializers.CharField(read_only=True)

    class Meta:
        model = FieldValue
        list_serializer_class = GeneratorListSerializer
        fields = ['pk',
                  'project_id',
                  'project',
                  'document_id',
                  'document_name',
                  'document_status',
                  'field_id',
                  'field_name',
                  'value',
                  'python_value',
                  'location_text',
                  'modified_by_username',
                  'modified_by_id',
                  'modified_date']

    def get_project(self, obj: FieldValue):
        return obj.document.project.name if obj.document.project else 'NA'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        view = self.context['view']
        if view.action == 'retrieve':
            # get prev/next FieldValue id using the same sort order and filters from list view
            qs = view.get_queryset()
            qs = view.filter_queryset(qs)
            ids = list(qs.filter(field=instance.field).values_list('pk', flat=True))
            pos = ids.index(instance.pk)
            prev_ids = ids[:pos]
            next_ids = ids[pos + 1:]
            ret['prev_id'] = prev_ids[-1] if prev_ids else None
            ret['next_id'] = next_ids[0] if next_ids else None
            ret['annotations'] = FieldAnnotation.objects.filter(field=instance.field, document=instance.document) \
                .values('pk', 'location_start', 'location_end', 'location_text')
        return ret


class DocumentFieldValueViewSet(JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: Document Field Value List
    retrieve: Document Field Value Details
    """
    queryset = FieldValue.objects.all()
    serializer_class = DocumentFieldValueSerializer
    http_method_names = ['get']
    unfiltered_queryset = None

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(value__isnull=False, document__delete_pending=False)

        if self.request.user.is_reviewer:
            qs = qs.filter(document__project__reviewers=self.request.user)
        elif self.request.user.is_manager:
            qs = qs.filter(Q(document__project__reviewers=self.request.user) |
                           Q(document__project__owners=self.request.user)).distinct()

        self.unfiltered_queryset = qs

        # via project router
        project_id = self.kwargs.get('project_pk')
        if project_id:
            qs = qs.filter(document__project_id=project_id)

        field_annotation_subquery = FieldAnnotation.objects \
            .filter(field=OuterRef("field"), document=OuterRef("document")) \
            .order_by('field', 'document') \
            .values('field', 'document') \
            .annotate(ann=GroupConcat('location_text', '\n-----\n'))

        qs = qs.annotate(
            modified_by_username=F('modified_by__username'),
            project=F('document__project__name'),
            project_id=F('document__project_id'),
            document_name=F('document__name'),
            document_status=F('document__status__name'),
            field_name=Concat('field__document_type__title', Value(': '), 'field__title'))

        qs = qs.select_related('document', 'document__project', 'document__status',
                               'field', 'field__document_type', 'modified_by')

        if self.action == 'list':
            qs = qs.annotate(
                location_text=Subquery(field_annotation_subquery.values('ann')[:1],
                                       output_field=TextField()))

        qs = qs.only(
            'document_id', 'document__name', 'document__status__name',
            'document__project_id', 'document__project__name',
            'field_id', 'field__title', 'field__type',
            'field__document_type__title',
            'value',
            'modified_by_id', 'modified_by__username', 'modified_date')

        return qs

    def get_extra_data(self, qs):
        data = super().get_extra_data(qs)
        data['count_of_filtered_items'] = qs.count()
        data['count_of_items'] = (self.unfiltered_queryset or FieldValue.objects).count()
        return data


# --------------------------------------------------------
#  Field Annotation Status Views
# --------------------------------------------------------

class FieldAnnotationStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = FieldAnnotationStatus
        fields = '__all__'


class FieldAnnotationStatusViewSet(JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: FieldAnnotationStatus List
    retrieve: Retrieve FieldAnnotationStatus
    create: Create FieldAnnotationStatus
    update: Update FieldAnnotationStatus
    delete: Delete FieldAnnotationStatus
    """
    queryset = FieldAnnotationStatus.objects.all()
    serializer_class = FieldAnnotationStatusSerializer


# --------------------------------------------------------
# Annotator View
# --------------------------------------------------------

class AnnotationInDocumentSerializer(serializers.ModelSerializer):
    field = WritableSerializerMethodField(read_only=False)

    def get_field(self, instance: FieldAnnotation):
        return instance.field.code

    def deserialize_field(self, field_code: str):
        document_id = self.initial_data['document']
        return DocumentField.objects.get(code=field_code,
                                         document_type_id__in=Document.objects
                                         .filter(pk=document_id)
                                         .values('document_type_id'))

    class Meta:
        model = FieldAnnotation
        fields = ['pk', 'document', 'value', 'field',
                  'location_start', 'location_end', 'location_text',  # TODO: Remove location_text when frontend ready
                  'modified_by', 'modified_date']

    def create(self, validated_data):
        instance = FieldAnnotation()
        self.update(instance, validated_data)
        cache_and_detect_field_values(doc=instance.document,
                                      user=self.context['request'].user,
                                      updated_fields={instance.field})
        return instance

    def update(self, instance: FieldAnnotation, validated_data):
        instance.document = validated_data['document']
        instance.field = validated_data['field']
        typed_field = TypedField.by(instance.field)
        instance.location_start = validated_data['location_start']
        instance.location_end = validated_data['location_end']
        instance.location_text = instance.document.full_text[instance.location_start:instance.location_end]
        old_ant_value = instance.value
        instance.value = validated_data['value']
        instance.extraction_hint = typed_field.pick_hint_by_searching_for_value_among_extracted(instance.location_text,
                                                                                                instance.value)
        user = self.context['request'].user
        instance.modified_by = user

        field_repo = DocumentFieldRepository()
        field_repo.store_field_annotation_and_update_field_value(instance, old_ant_value=old_ant_value)
        cache_and_detect_field_values(doc=instance.document, user=user, updated_fields={instance.field})
        return instance


# TODO: Ensure security
class AnnotationsInDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = AnnotationInDocumentSerializer

    def get_queryset(self):
        qs = FieldAnnotation.objects.filter(document_id=self.kwargs['document_pk'])

        location_offset = as_int(self.request.GET, 'location_offset')
        if location_offset is not None:
            qs = qs.filter(location_start__gte=location_offset)

        location_limit = as_int(self.request.GET, 'location_limit')
        if location_limit is not None:
            qs = qs.filter(location_start__lte=(location_offset or 0) + location_limit)

        field_code = self.request.GET.get('field')
        if field_code:
            qs = qs.filter(field__code=field_code)

        offset = as_int(self.request.GET, 'offset', None)
        limit = as_int(self.request.GET, 'limit', None)
        end = (offset or 0) + limit if limit else None

        return qs.select_related('field').order_by('location_start')[offset:end]

    def perform_destroy(self, instance: FieldAnnotation):
        field_repo = DocumentFieldRepository()
        user = self.request.user
        field_repo.delete_field_annotation_and_update_field_value(instance, user)
        cache_and_detect_field_values(doc=instance.document, user=user, updated_fields={instance.field})


# --------------------------------------------------------
# Clause (Document Field Annotation) Views
# --------------------------------------------------------

class DocumentFieldAnnotationSerializer(serializers.ModelSerializer):
    project_id = serializers.IntegerField(read_only=True)
    project_name = serializers.CharField(read_only=True)
    document_name = serializers.CharField(read_only=True)
    document_status = serializers.CharField(read_only=True)
    field_name = serializers.CharField(read_only=True)
    status_id = serializers.IntegerField(read_only=False)
    assignee_id = serializers.IntegerField(read_only=False)
    status_name = serializers.CharField(read_only=True)
    assignee_name = serializers.CharField(read_only=True)

    class Meta:
        model = FieldAnnotation
        list_serializer_class = GeneratorListSerializer
        # WARN: fields order makes sense here for list view
        fields = ['pk',
                  'uid',
                  'project_id',
                  'project_name',
                  'document_id',
                  'document_name',
                  'document_status',
                  'field_id',
                  'field_name',
                  'value',
                  'location_start',
                  'location_end',
                  'location_text',
                  'assignee_id',
                  'assign_date',
                  'status_id',
                  'status_name',
                  'assignee_name',
                  'modified_by_id',
                  'modified_date']

    def get_field_names(self, declared_fields, info):
        columns = self.context['view'].request.GET.get('columns')
        if columns:
            initial_fields = list(self.Meta.fields)
            columns = columns.split(',')
            self.Meta.fields = columns
            declared_fields = OrderedDict([(k, v) for k, v in self._declared_fields.items() if k in columns])
            res = super().get_field_names(declared_fields, info)
            self.Meta.fields = initial_fields
            return res
        return super().get_field_names(declared_fields, info)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        view = self.context['view']

        # inject next/prev annotation id into data
        if view.action == 'retrieve':
            # in case if queryset is ValuesQueryset instance
            if isinstance(instance, dict):
                instance = Map(instance)

            # get prev/next FieldAnnotation id using the same sort order and filters from list view
            # INFO: DISABLED filter by field
            # view.kwargs['field_id'] = instance.field_id
            qs = view.get_queryset()

            id_set = [(i['uid'], i['document_id']) for i in qs]
            uids = [i[0] for i in id_set]

            pos = uids.index(instance.uid)
            prev_uids = uids[:pos]
            next_uids = uids[pos + 1:]
            ret['prev_id'] = prev_uids[-1] if prev_uids else None
            ret['next_id'] = next_uids[0] if next_uids else None
            ret['prev_document_id'] = id_set[:pos][-1][1] if prev_uids else None
            ret['next_document_id'] = id_set[pos + 1:][0][1] if next_uids else None

        return ret

    def update(self, instance, validated_data):
        initial_status = instance.status
        instance = super().update(instance, validated_data)
        if 'assignee_id' in validated_data:
            instance.assign_date = now()
            instance.save()
        if initial_status != instance.status:
            Document.reset_status_from_annotations(ann_status=instance.status, document_ids=[instance.document.id])

        return instance


class DocumentFieldAnnotationViewSet(JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: Field Annotation List + Field Annotation False Match List
    retrieve: Field Annotation Details (not Field Annotation False Match)
    partial_update: Update Annotation (not Field Annotation False Match)
    """
    serializer_class = DocumentFieldAnnotationSerializer
    http_method_names = ['get', 'patch']

    # custom lookup field to retrieve single object using unique object attr
    lookup_field = 'uid'

    # stats for resulter json data
    total_annotations_count = None
    unfiltered_annotations_count = None
    completed_annotations_count = None
    assignee_data = []

    # common fields for FieldAnnotation and FieldAnnotationFalseMatch
    # WARN: fields order makes sense here for list view
    common_fields = [
        'pk',
        'uid',
        'field_id',
        'value',
        'location_start',
        'location_end',
        'location_text',
        'assignee_id',
        'assign_date',
    ]

    @action(detail=False, methods=['get'], url_path='for-user')
    def for_user(self, request, *args, **kwrags):
        response = super().list(request, *args, **kwrags)
        data = self.get_extra_data(None)
        data['data'] = response.data
        return Response(data)

    def get_object(self):
        """
        Custom method to get single object as
        UNION queryset doesn't support filtering and GET method.
        """
        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

        # get object either from FieldAnnotation OR FieldAnnotationsFalseMatch queryset
        true_ann_queryset = self.get_true_annotations_queryset()
        true_ann_obj = true_ann_queryset.filter(**filter_kwargs)
        if true_ann_obj.exists():
            obj = true_ann_obj.last()
            # if isinstance(obj, dict):
            #     obj = FieldAnnotation.objects.get(uid=obj['uid'])
        else:
            false_ann_queryset = self.get_false_annotations_queryset()
            false_ann_obj = false_ann_queryset.filter(**filter_kwargs)
            if false_ann_obj.exists():
                obj = false_ann_obj.last()
                # if isinstance(obj, dict):
                #     obj = FieldAnnotationFalseMatch.objects.get(uid=obj['uid'])
            else:
                raise Http404(f'No FieldAnnotation or FieldAnnotationFalseMatch found with '
                              f'"{self.kwargs[lookup_url_kwarg]}" {self.lookup_field}.')

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get_initial_queryset(self, model):
        """
        Get initial queryset for a given model, apply  filters
        :param model:
        :return:
        """
        # filter out deleted documents
        qs = model.objects.filter(document__delete_pending=False)

        if self.request.user.is_reviewer:
            qs = qs.filter(document__project__reviewers=self.request.user)
        elif self.request.user.is_manager:
            qs = qs.filter(Q(document__project__reviewers=self.request.user) |
                           Q(document__project__owners=self.request.user)).distinct()

        # stats page for a user
        if self.action == 'for_user':
            qs = qs.filter(assignee=self.request.user)

        # via project router
        project_id = self.kwargs.get('project_pk')
        if project_id:
            qs = qs.filter(document__project_id=project_id)

        # filter by field
        field_id = self.kwargs.get('field_id')
        if field_id:
            qs = qs.filter(field_id=field_id)

        # filters from "assign", "set_status" actions
        if self.request.GET.get('all') and self.request.GET.get('no_annotation_ids'):
            qs = qs.exclude(uid__in=self.request.GET.get('no_annotation_ids'))
        elif self.request.GET.get('annotation_ids'):
            qs = qs.filter(uid__in=self.request.GET.get('annotation_ids'))

        return qs

    def get_true_annotations_queryset(self):
        """
        Get FieldAnnotation queryset
        """
        true_ann_qs = self.get_initial_queryset(FieldAnnotation)

        if self.action == 'for_user':
            true_ann_qs = true_ann_qs.filter(status__is_accepted=False)

        # WARN: fields order makes sense here for list view
        true_ann_only_fields = [
            'status_id',
            'modified_by_id',
            'modified_date']

        # TODO: move common annotations into get_initial_queryset()
        # WARN: fields order makes sense here for list view
        true_ann_qs_annotate = OrderedDict(
            document_id=Cast('document_id', output_field=CharField()),
            project_id=F('document__project_id'),
            project_name=F('document__project__name'),
            document_name=F('document__name'),
            document_status=F('document__status__name'),
            field_name=F('field__title'),
            status_name=F('status__name'),
            assignee_name=Case(When(Q(assignee__name__isnull=False) & ~Q(assignee__name=''), then=F('assignee__name')),
                               When(Q(assignee__first_name__in=['', None]) |
                                    Q(assignee__last_name__in=['', None]), then=F('assignee__username')),
                               default=Concat(F('assignee__first_name'), Value(' '), F('assignee__last_name')),
                               output_field=CharField())
        )
        # WARN: MUST HAVE the same
        # 1. fields number
        # 2. fields order
        # for FieldAnnotation and FieldAnnotationFalseMatch querysets to perform UNION !!!
        # so .values() and .annotate() applies THE SAME fields number and order
        true_ann_fields = self.common_fields + true_ann_only_fields
        true_ann_qs = true_ann_qs.values(*true_ann_fields).annotate(**true_ann_qs_annotate)

        return true_ann_qs

    def get_false_annotations_queryset(self):
        """
        Get FieldAnnotationFalseMatch queryset
        """
        false_ann_qs = self.get_initial_queryset(FieldAnnotationFalseMatch)

        # TODO: move common annotations into get_initial_queryset()
        # WARN: fields order makes sense here for list view
        false_ann_qs = false_ann_qs.values(*self.common_fields).annotate(
            status_id=Value(FieldAnnotationStatus.rejected_status_pk(), output_field=IntegerField()),
            modified_by_id=Cast(None, output_field=IntegerField()),
            modified_date=Cast(None, output_field=DateField()),

            document_id=Cast('document_id', output_field=CharField()),
            project_id=F('document__project_id'),
            project_name=F('document__project__name'),
            document_name=F('document__name'),
            document_status=F('document__status__name'),
            field_name=F('field__title'),
            status_name=Value('Rejected', output_field=CharField()),
            assignee_name=Case(When(Q(assignee__name__isnull=False) & ~Q(assignee__name=''), then=F('assignee__name')),
                               When(Q(assignee__first_name__in=['', None]) |
                                    Q(assignee__last_name__in=['', None]), then=F('assignee__username')),
                               default=Concat(F('assignee__first_name'), Value(' '), F('assignee__last_name')),
                               output_field=CharField())
        )
        return false_ann_qs

    def get_assignee_data(self, qs: QuerySet):

        df = pd.DataFrame(qs)
        if not df.empty:
            df = df.groupby(['assignee_id', 'assignee_name']).agg(
                {'uid': {'annotation_uids': lambda x: list(x), 'annotations_count': 'count'}})
            if not df.empty:
                df.columns = df.columns.droplevel()
                df = df.reset_index()
                df['assignee_id'] = df['assignee_id'].astype(int)
                self.assignee_data = df.to_dict('records')

    def get_queryset(self, **kwargs):
        """
        Get UNION of FieldAnnotations + FieldAnnotationFalseMatches,
        filter and sort it
        return: ValuesQuerySet
        """
        if self.action == 'list':
            # save or inject saved filter
            self.apply_saved_filters()

        # WARN: true/false annotation querysets MUST HAVE the same
        # 1. fields number
        # 2. fields order
        # to perform UNION !!!
        # so .values() and .annotate() applies THE SAME fields number and order
        true_ann_qs = self.get_true_annotations_queryset()

        # collect stats - see self.get_extra_data()
        # count unfiltered rows (need to concat with false ones below)
        self.unfiltered_annotations_count = true_ann_qs.count()

        # do not union with FalseMatches if single object,
        # as querysets with UNION doesn't support filter/get methods

        # WARN: need to filter BEFORE UNION as querysets with UNION doesn't support filtering
        # see https://docs.djangoproject.com/en/2.2/ref/models/querysets/#union
        true_ann_qs = super().filter(true_ann_qs)

        # collect stats - see self.get_extra_data()
        # completed annotations (filtered) (need to concat with false ones below)
        self.completed_annotations_count = true_ann_qs.filter(status__is_accepted=True).count()

        # case when API "available_assignees" or "assign_annotations"
        if kwargs.get('only_true_annotations') is True or self.action == 'for_user':
            # get columns from the serializer to unify querysets before UNION
            self.total_annotations_count = true_ann_qs.count()
            self.get_assignee_data(true_ann_qs)
            return true_ann_qs

        false_ann_qs = self.get_false_annotations_queryset()

        # collect stats - see self.get_extra_data()
        # count unfiltered rows (need to concat with true ones above)
        self.unfiltered_annotations_count += false_ann_qs.count()

        # WARN: need to filter BEFORE UNION as querysets with UNION doesn't support filtering
        # see https://docs.djangoproject.com/en/2.2/ref/models/querysets/#union
        false_ann_qs = super().filter(false_ann_qs)

        # collect stats - see self.get_extra_data()
        # completed annotations (filtered) (need to concat with true ones above)
        self.completed_annotations_count += false_ann_qs.count()

        # WARN: fields order makes sense here for list view
        # get columns from the serializer to unify querysets before UNION
        columns = DocumentFieldAnnotationSerializer.Meta.fields
        union_qs = true_ann_qs.values(*columns).union(false_ann_qs.values(*columns))

        # collect stats - see self.get_extra_data()
        self.total_annotations_count = union_qs.count()

        # finally sort UNION queryset
        union_qs = self.sort_queryset(union_qs)
        self.get_assignee_data(union_qs)

        return union_qs

    def sort_queryset(self, queryset):
        """
        Sort UNION queryset using "sortdatafield" from request and default sort order
        """
        sort_fields = ['field_name', 'document_name', 'location_start']
        request_sort_field = self.request.GET.get('sortdatafield')
        if request_sort_field:
            request_sort_order = self.request.GET.get('sortorder', 'asc')
            if request_sort_order == 'desc':
                request_sort_field = f'-{request_sort_field}'
            sort_fields.insert(0, request_sort_field)
        columns = self.request.GET.get('columns')
        if columns:
            columns = columns.split(',')
            sort_fields = [i for i in sort_fields if i.lstrip('-') in columns]
        return queryset.order_by(*sort_fields)

    def filter_queryset(self, queryset):
        """
        Disable native filter_queryset() method as we need to filter querysets separately and
        it's already done in get_queryset() method
        """
        if self.action == 'for_user':
            queryset = queryset.filter(status_id=FieldAnnotationStatus.initial_status_pk())
        return queryset

    def get_extra_data(self, queryset):
        """
        Pass extra data into json response, such as total_annotations_count
        """
        data = dict(total_annotations_count=self.total_annotations_count,
                    count_of_filtered_items=self.total_annotations_count,
                    count_of_items=self.unfiltered_annotations_count,
                    completed_annotations_count=self.completed_annotations_count,
                    assignee_data=self.assignee_data)
        return data

    def apply_saved_filters(self):
        """
        Save filters OR inject existing FieldAnnotationSavedFilter data
        into request for further processing
        """
        project_id = self.kwargs.get('project_pk')
        request_data = self.request.GET
        columns = request_data.get('columns')
        save_filter = request_data.get('save_filter') == 'true'

        # if user changes filter/sort - it should be saved anyway
        # create/update SavedFilter if filter/sort/columns params provided in request
        if 'sortdatafield' in request_data or 'filterscount' in request_data or 'columns' in request_data:
            user_filter, _ = FieldAnnotationSavedFilter.objects.update_or_create(
                user=self.request.user,
                project_id=project_id,
                document_type=project_api_module.Project.objects.get(pk=project_id).type,
                filter_type=constants.FA_USER_FILTER,
                defaults=dict(
                    columns=columns,
                    column_filters={k: v for k, v in request_data.items() if k[:6] == 'filter'} or None,
                    order_by={k: v for k, v in request_data.items() if k[:4] == 'sort'} or None,
                )
            )
        # otherwise try to apply SavedFilter if it exists by patching request data
        # or delete filter
        else:
            user_filter = FieldAnnotationSavedFilter.objects.filter(
                user=self.request.user,
                project_id=project_id,
                filter_type=constants.FA_USER_FILTER)
            if user_filter.exists():

                # if a user dropped filters
                if save_filter:
                    user_filter.delete()
                # case for grid initiating
                else:
                    user_filter = user_filter.last()

                    if not getattr(request_data, '_mutable', True):
                        request_data._mutable = True

                    if user_filter.column_filters:
                        request_data.update(user_filter.column_filters)
                    if user_filter.order_by:
                        request_data.update(user_filter.order_by)
                    if user_filter.columns:
                        request_data['columns'] = user_filter.columns

                    if hasattr(request_data, '_mutable'):
                        request_data._mutable = False


main_router = routers.DefaultRouter()
main_router.register(r'documents', DocumentViewSet, 'document')
main_router.register(r'document-notes', DocumentNoteViewSet, 'document-note')
main_router.register(r'document-fields', DocumentFieldViewSet, 'document-field')
main_router.register(r'document-types', DocumentTypeViewSet, 'document-types')
main_router.register(r'document-field-categories', DocumentFieldCategoryViewSet, 'document-field-category')
main_router.register(r'document-field-detectors', DocumentFieldDetectorViewSet, 'document-field-detector')
main_router.register(r'document-field-values', DocumentFieldValueViewSet, 'document-field-values')
main_router.register(r'document-field-annotations', DocumentFieldAnnotationViewSet, 'document-field-annotations')
main_router.register(r'field-annotation-statuses', FieldAnnotationStatusViewSet, 'field-annotation-status')
main_router.register(r'textunits', TextUnitViewSet, 'textunit')

# Annotator - create new annotation/change/delete
main_router.register(r'annotations', AnnotationViewSet, 'annotation')

# route documents via project
project_router = routers.SimpleRouter()

project_router.register(r'project', project_api_module.ProjectViewSet, 'project')
document_via_project_router = nested_routers.NestedSimpleRouter(
    project_router, r'project', lookup='project', trailing_slash=True)
document_via_project_router.register(r'documents', DocumentViewSet, 'documents')

# route field values via project
field_value_via_project_router = nested_routers.NestedSimpleRouter(
    project_router, r'project', lookup='project', trailing_slash=True)
field_value_via_project_router.register(
    r'document-field-values', DocumentFieldValueViewSet, 'project-document-field-values')

# route Clauses (field annotations) via project
field_annotation_via_project_router = nested_routers.NestedSimpleRouter(
    project_router, r'project', lookup='project', trailing_slash=True)
field_annotation_via_project_router.register(
    r'document-field-annotations', DocumentFieldAnnotationViewSet, 'project-document-field-annotations')

# Annotator urls
annotation_via_document_router = nested_routers.NestedSimpleRouter(
    document_via_project_router, r'documents', lookup='document', trailing_slash=True)
annotation_via_document_router.register(r'annotations', AnnotationsInDocumentViewSet, 'annotations')

api_routers = [main_router,
               document_via_project_router,
               field_value_via_project_router, field_annotation_via_project_router,
               annotation_via_document_router]

urlpatterns = [
    url(r'stats/$', StatsAPIView.as_view(),
        name='stats'),
]
