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
import traceback
from collections import defaultdict, OrderedDict
from itertools import groupby
from typing import Dict, Set, Optional

# Third-party imports
import numpy as np
import pandas as pd
import rest_framework.views
from celery.states import SUCCESS, FAILURE, PENDING, REVOKED

# Django imports
from django.conf.urls import url
from django.contrib.postgres.aggregates.general import StringAgg
from django.db.models import Min, Max, Subquery, Prefetch, Q, OuterRef, TextField
from django.http import JsonResponse, HttpRequest
from elasticsearch import Elasticsearch
from rest_framework import routers, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, ValidationError as DRFValidationError
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework_nested import routers as nested_routers

# Project imports
import apps.common.mixins
from apps.analyze.models import *
from apps.common.api.permissions import ReviewerReadOnlyPermission
from apps.common.models import ReviewStatus
from apps.common.serializers import WritableSerializerMethodField
from apps.common.url_utils import as_bool, as_int
from apps.common.utils import get_api_module, GroupConcat
from apps.document import signals
from apps.document.admin import (
    DocumentFieldForm, UsersTasksValidationAdmin, PARAM_OVERRIDE_WARNINGS, DocumentTypeForm,
    DocumentFieldAdmin)
from apps.document.api.annotator_error import NoValueProvidedOrLocated
from apps.document.async_tasks.detect_field_values_task import DocDetectFieldValuesParams
from apps.document.constants import DocumentSystemField
from apps.document.field_detection import field_detection
from apps.document.field_detection.detector_field_matcher import DetectorFieldMatcher
from apps.document.field_detection.field_detection_celery_api import run_detect_field_values_for_document
from apps.document.field_types import TypedField, BooleanField, RelatedInfoField, MultiValueField
from apps.document.models import *
from apps.document.repository.document_field_repository import DocumentFieldRepository
from apps.document.repository.document_repository import DocumentRepository
from apps.document.repository.dto import FieldValueDTO, AnnotationDTO
from apps.document.tasks import plan_process_document_changed
from apps.document.views import show_document
from apps.extract.models import *
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


common_api_module = get_api_module('common')
project_api_module = get_api_module('project')
extract_api_module = get_api_module('extract')


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


class DocumentNoteDetailSerializer(apps.common.mixins.SimpleRelationSerializer):
    document_id = serializers.PrimaryKeyRelatedField(
        source='document', queryset=Document.objects.all())

    user = UserSerializer(source='history.last.history_user', many=False, read_only=True)
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
        read_only_fields = ('timestamp', 'user')


class DocumentNoteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentNote
        fields = ['note']


class FieldAnnotationValueSerializer(serializers.ModelSerializer):
    adapter = None

    value = serializers.SerializerMethodField()
    field_name = serializers.SerializerMethodField()

    class Meta:
        model = FieldAnnotation
        list_serializer_class = GeneratorListSerializer
        fields = ['pk',
                  'field',
                  'field_name',
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
            qs = qs.filter(project__reviewers=self.request.user)
        return qs


class DocumentNoteViewSet(apps.common.mixins.JqListAPIMixin, viewsets.ModelViewSet):
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

class BaseDocumentSerializer(apps.common.mixins.SimpleRelationSerializer):
    """
    Base serializer for all documents
    """
    status_data = common_api_module.ReviewStatusSerializer(source='status', many=False)
    available_statuses_data = serializers.SerializerMethodField()
    assignee_data = UserSerializer(source='assignee', many=False)
    available_assignees_data = serializers.SerializerMethodField()
    status_name = serializers.SerializerMethodField()
    assignee_name = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['pk', 'name', 'document_type', 'file_size', 'folder',
                  'status', 'status_data', 'status_name', 'available_statuses_data',
                  'assignee', 'assign_date', 'assignee_data', 'assignee_name', 'available_assignees_data',
                  'project', 'description', 'title']

    def get_available_assignees_data(self, obj):
        return UserSerializer(obj.available_assignees, many=True).data

    def get_available_statuses_data(self, obj):
        return common_api_module.ReviewStatusSerializer(
            ReviewStatus.objects.select_related('group'), many=True).data

    def get_status_name(self, obj):
        return obj.status.name if obj.status else None

    def get_assignee_name(self, obj):
        return obj.assignee.username if obj.assignee else None


class SimpleDocumentSerializer(BaseDocumentSerializer):
    """
    Serializer for user documents
    """

    class Meta:
        model = Document
        fields = ['pk', 'name', 'document_type', 'project', 'status_name']


class GenericDocumentSerializer(apps.common.mixins.SimpleRelationSerializer):
    """
    Serializer for documents with Generic Contract type
    """
    cluster_id = serializers.IntegerField()
    parties = serializers.CharField()
    min_date = serializers.DateField()
    max_date = serializers.DateField()
    max_currency_amount = serializers.FloatField()
    max_currency_name = serializers.CharField()

    class Meta:
        model = Document
        fields = ['pk', 'name', 'cluster_id', 'file_size', 'folder',
                  'parties', 'min_date', 'max_date',
                  'max_currency_amount', 'max_currency_name']


class DocumentWithFieldsDetailSerializer(BaseDocumentSerializer):
    """
    Serializer for document review page with detailed document field values
    """
    field_repo = DocumentFieldRepository()

    field_value_objects = serializers.SerializerMethodField()
    field_values = serializers.SerializerMethodField()
    notes = DocumentNoteDetailSerializer(source='documentnote_set', many=True)
    prev_id = serializers.SerializerMethodField()
    next_id = serializers.SerializerMethodField()
    sections = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['pk', 'name', 'document_type', 'file_size', 'folder',
                  'status', 'status_data', 'available_statuses_data',
                  'assignee', 'assign_date', 'assignee_data', 'available_assignees_data',
                  'description', 'title', 'full_text',
                  'notes', 'field_values', 'field_value_objects',
                  'prev_id', 'next_id', 'sections', 'cluster_id']

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
        return field_repo.get_field_uid_to_python_value(document_type_id=doc.document_type_id, doc_id=doc.pk)

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

    def update(self, updated_doc: Document, validated_data):
        with transaction.atomic():
            system_fields_changed = list()

            new_status = validated_data.get('status')
            if new_status is not None and new_status.pk != updated_doc.status_id:
                is_active = updated_doc.status and updated_doc.status.is_active
                if new_status.is_active != is_active:
                    field_repo = DocumentFieldRepository()
                    field_ids = field_repo.get_doc_field_ids_with_values(updated_doc.pk)
                    DocumentField.objects \
                        .filter(document_type_id=updated_doc.document_type_id, pk__in=Subquery(field_ids)) \
                        .update(dirty=True)
                system_fields_changed.append(DocumentSystemField.status.value)

            user = self.context['request'].user  # type: User
            new_assignee = validated_data.get('assignee')
            prev_assignee = updated_doc.assignee
            if new_assignee is None and prev_assignee is not None:
                validated_data['assign_date'] = None
                system_fields_changed.append(DocumentSystemField.assignee.value)
            elif new_assignee is not None and (prev_assignee is None or new_assignee.pk != prev_assignee.pk):
                validated_data['assign_date'] = datetime.datetime.now(tz=user.get_time_zone())
                system_fields_changed.append(DocumentSystemField.assignee.value)

            res = super().update(updated_doc, validated_data)

            plan_process_document_changed(doc_id=updated_doc.pk,
                                          system_fields_changed=system_fields_changed,
                                          generic_fields_changed=False,
                                          user_fields_changed=False,
                                          changed_by_user_id=user.pk)
            return res


class DocumentWithFieldsRestrictedDetailSerializer(DocumentWithFieldsDetailSerializer):
    """
    Serializer for document review page with detailed document field values
    but without some "expensive" data to speed up loading
    """
    class Meta:
        model = Document
        fields = ['pk', 'name', 'document_type', 'file_size', 'folder',
                  'status', 'status_data', 'available_statuses_data',
                  'assignee', 'assign_date', 'assignee_data', 'available_assignees_data',
                  'description', 'title',
                  # 'full_text',
                  'notes', 'field_values', 'field_value_objects',
                  'prev_id', 'next_id', 'sections', 'cluster_id']


class DocumentWithFieldsListSerializer(BaseDocumentSerializer):
    """
    Serializer for document list page with document field values
    """

    class Meta:
        model = Document
        fields = ['pk', 'name', 'document_type',
                  'description', 'title', 'file_size', 'folder',
                  'status', 'status_data', 'status_name',
                  'assignee', 'assign_date', 'assignee_data', 'assignee_name']


class ExtendedDocumentWithFieldsListSerializer(GenericDocumentSerializer,
                                               DocumentWithFieldsListSerializer):
    """
    Extended serializer for document list page with document field values
    + values for Generic Contract type document
    """

    class Meta:
        model = Document
        fields = ['pk', 'name', 'document_type', 'folder',
                  'description', 'title', 'file_size',
                  'status', 'status_data', 'status_name',
                  'assignee', 'assign_date', 'assignee_data', 'assignee_name',
                  'field_values', 'cluster_id', 'parties',
                  'min_date', 'max_date',
                  'max_currency_amount', 'max_currency_name']


class ExportDocumentWithFieldsListSerializer(DocumentWithFieldsListSerializer):
    """
    Extended serializer for export document list page with document field values
    """

    class Meta:
        model = Document
        fields = ['pk', 'name', 'description', 'title', 'file_size', 'folder',
                  'status_name', 'assignee_name']


class ExportExtendedDocumentWithFieldsListSerializer(ExtendedDocumentWithFieldsListSerializer):
    """
    Extended serializer for export document list page with document field values
    + values for Generic Contract type document
    """

    class Meta:
        model = Document
        fields = ['pk', 'name', 'description', 'title', 'file_size', 'folder',
                  'status_name', 'assignee_name',
                  'cluster_id', 'parties', 'min_date', 'max_date',
                  'max_currency_amount', 'max_currency_name']


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
        return qs


class DocumentViewSet(DocumentPermissionViewMixin, apps.common.mixins.APIActionMixin,
                      apps.common.mixins.JqListAPIMixin, viewsets.ModelViewSet):
    """
    list:
        Document List\n
        GET params to filter/sort/paginate response:
          - filterscount:1
          - filterdatafield0:name
          - filtercondition0:CONTAINS
          - filtervalue0:Employment
          - filteroperator0:0 (0-and, 1-or)
          - sortdatafield:title
          - sortorder:asc (asc, desc)
          - pagenum:0 (startswith 0)
          - pagesize:10
          - enable_pagination:true
          - total_records:true
    retrieve: Document Detail
    """
    queryset = Document.objects.all()

    def get_queryset(self):
        qs = Document.objects.filter(project__delete_pending=False)

        party_id = self.request.GET.get("party_id")
        if party_id:
            qs = qs.filter(textunit__partyusage__party__pk=party_id)

        if self.action == 'for_user':
            qs = qs.filter(assignee=self.request.user,
                           status__group__is_active=True)

        project_id = self.request.GET.get("project_id")

        # only for projects with GenericContract type and project detail view
        if project_id and DocumentType.generic().project_set.filter(pk=project_id).exists():
            qs = qs.filter(project_id=project_id).values('id', 'name') \
                .annotate(cluster_id=Max('documentcluster'),
                          assignee_name=F('assignee__username'),
                          status_name=F('status__name'),
                          parties=StringAgg('textunit__partyusage__party__name',
                                            delimiter=', ',
                                            distinct=True),
                          min_date=Min('textunit__dateusage__date'),
                          max_currency_amount=Max('textunit__currencyusage__amount'),
                          max_currency_name=Max('textunit__currencyusage__currency'),
                          max_date=Max('textunit__dateusage__date'))
            # filter by cluster_id
            cluster_id = self.request.GET.get("cluster_id")
            if cluster_id:
                qs = qs.filter(cluster_id=int(cluster_id))

        qs = qs.select_related('document_type', 'status', 'status__group', 'assignee', 'documenttext')

        return qs

    def get_serializer_class(self, *args, **kwargs):
        # if project and project is of Generic Contract type
        if self.action == 'for_user':
            return SimpleDocumentSerializer
        if self.request.GET.get('project_id') and \
                DocumentType.generic().project_set.filter(pk=self.request.GET['project_id']).exists():
            return GenericDocumentSerializer
        if self.action == 'list':
            return DocumentWithFieldsListSerializer
        return DocumentWithFieldsDetailSerializer

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
        if 'definitions' not in document.metadata:
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
            document.documentmetadata.metadata['definitions'] = res
            document.documentmetadata.save()
        return Response(document.metadata['definitions'])

    def destroy(self, request, *args, **kwargs):
        document = self.get_object()
        session = document.upload_session

        # delete document
        # remove document tasks in Document.full_delete post_delete signal task
        document.delete()

        # REMOVE redundant sessions
        remove_session = False
        # get status of documents in session
        progress = session.document_tasks_progress()
        if not progress:
            remove_session = True
        else:
            statuses = {i['tasks_overall_status'] for i in progress.values()}
            if statuses == {FAILURE}:
                remove_session = True
        if remove_session:
            # delete session documents' tasks
            session.session_tasks.delete()
            session.delete()
        return Response({'session_removed': remove_session}, status=200)

    @action(detail=True, methods=['get'])
    def show(self, request, **kwargs):
        document = self.get_object()
        return show_document(request, document.pk)

    @action(detail=False, methods=['get'], url_path='for-user')
    def for_user(self, request, *args, **kwrags):
        return super().list(request, *args, **kwrags)

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


class ProjectDocumentsWithFieldsViewSet(apps.common.mixins.APILoggingMixin,
                                        DocumentPermissionViewMixin, apps.common.mixins.APIActionMixin,
                                        apps.common.mixins.JqListAPIMixin, viewsets.ReadOnlyModelViewSet):
    """
    list: Document List with Fields
    retrieve: Document Detail with Fields
    """
    queryset = Document.objects.all()

    def get_object(self, *args, **kwargs):
        doc_pk = self.kwargs.get('pk')
        if not doc_pk:
            return super().get_object()

        query_set = self.get_project_queryset()
        doc = query_set.get(*args, **{'pk': doc_pk})  # type: Document
        return doc

    def get_project_queryset(self):
        project_pk = self.kwargs.get('project_pk')
        cluster_id = self.request.GET.get("cluster_id")

        document_qs = super().get_queryset().filter(project__pk=project_pk)
        if cluster_id:
            document_qs = document_qs.filter(cluster_id=int(cluster_id))

        if self.action == 'for_user':
            document_qs = document_qs.filter(assignee=self.request.user,
                                             status__group__is_active=True)
        elif self.action == 'retrieve':
            document_qs = document_qs.prefetch_related('documentnote_set')

        document_qs = document_qs \
            .select_related('status', 'status__group', 'document_type', 'assignee') \
            .defer('language', 'source', 'source_type', 'source_path',
                   'paragraphs', 'sentences', 'upload_session_id')

        document_qs = document_qs \
            .annotate(assignee_name=F('assignee__username'),
                      status_name=F('status__name'))
        return document_qs

    def get_extra_data(self, queryset):
        extra_data = super().get_extra_data(queryset)
        extra_data.update({'reviewed_total': queryset.filter(status__is_active=False).count()})
        extra_data.update({'query_string': self.request.META['QUERY_STRING']})
        return extra_data

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'for_user':
            return SimpleDocumentSerializer
        elif self.action == 'list':
            project_pk = self.kwargs.get('project_pk')
            is_generic = DocumentType.generic().project_set.filter(pk=project_pk).exists()
            if is_generic and project_pk:
                if self.request.GET.get('export_to'):
                    return ExportExtendedDocumentWithFieldsListSerializer
                return ExtendedDocumentWithFieldsListSerializer
            if self.request.GET.get('export_to'):
                return ExportDocumentWithFieldsListSerializer
            return DocumentWithFieldsListSerializer
        elif self.action == 'data':
            return DocumentWithFieldsRestrictedDetailSerializer
        return DocumentWithFieldsDetailSerializer

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

    @action(detail=False, methods=['get'], url_path='for-user')
    def for_user(self, request, *args, **kwrags):
        return super().list(request, *args, **kwrags)

    @action(methods=['get'], detail=True)
    def full_text(self, request, project_pk, pk):
        text = DocumentText.objects.filter(document_id=pk).values_list('full_text', flat=True).first()
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


# --------------------------------------------------------
# Document Property Views
# --------------------------------------------------------

class DocumentPropertyDetailSerializer(apps.common.mixins.SimpleRelationSerializer):
    class Meta:
        model = DocumentProperty
        fields = ['pk', 'key', 'value',
                  'created_date', 'created_by__username',
                  'modified_date', 'modified_by__username',
                  'document__pk', 'document__name',
                  'document__document_type', 'document__description']


class DocumentPropertyCreateSerializer(serializers.ModelSerializer):
    document_id = serializers.PrimaryKeyRelatedField(
        source='document', queryset=Document.objects.all())

    class Meta:
        model = DocumentProperty
        fields = ['pk', 'key', 'value', 'document_id']


class DocumentPropertyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentProperty
        fields = ['key', 'value']


class DocumentPropertyViewSet(apps.common.mixins.JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: Document Property List
    retrieve: Retrieve Document Property
    create: Create Document Property
    update: Update Document Property
    partial_update: Partial Update Document Property
    delete: Delete Document Property
    """
    queryset = DocumentProperty.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentPropertyCreateSerializer
        if self.action == 'update':
            return DocumentPropertyUpdateSerializer
        return DocumentPropertyDetailSerializer


# --------------------------------------------------------
# Document Tag Views
# --------------------------------------------------------

class DocumentTagDetailSerializer(apps.common.mixins.SimpleRelationSerializer):
    class Meta:
        model = DocumentTag
        fields = ['pk', 'tag', 'timestamp',
                  'user__username', 'document__pk',
                  'document__name', 'document__document_type',
                  'document__description']


class DocumentTagCreateSerializer(serializers.ModelSerializer):
    document_id = serializers.PrimaryKeyRelatedField(
        source='document', queryset=Document.objects.all())

    class Meta:
        model = DocumentTag
        fields = ['pk', 'tag', 'document_id']


class DocumentTagUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTag
        fields = ['tag']


class DocumentTagViewSet(apps.common.mixins.JqListAPIMixin, viewsets.ModelViewSet):
    """
    Document Tag List
    retrieve: Retrieve Document Tag
    create: Create Document Tag
    update: Update Document Tag
    partial_update: Partial Update Document Tag
    delete: Delete Document Tag
    """
    queryset = DocumentTag.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentTagCreateSerializer
        if self.action == 'update':
            return DocumentTagUpdateSerializer
        return DocumentTagDetailSerializer


# --------------------------------------------------------
# Text Unit Views
# --------------------------------------------------------

class TextUnitDetailSerializer(apps.common.mixins.SimpleRelationSerializer):
    class Meta:
        model = TextUnit
        fields = ['pk', 'unit_type', 'language', 'textunittext__text', 'text_hash',
                  'document__pk', 'document__name',
                  'document__document_type', 'document__description']


class TextUnitViewSet(apps.common.mixins.JqListAPIMixin, viewsets.ReadOnlyModelViewSet):
    """
    list: Text Unit List
    retrieve: Retrieve Text Unit
    """
    queryset = TextUnit.objects.all()
    serializer_class = TextUnitDetailSerializer
    es = Elasticsearch(hosts=settings.ELASTICSEARCH_CONFIG['hosts'])

    def get_queryset(self):
        qs = super().get_queryset()

        if "elastic_search" in self.request.GET:
            elastic_search = self.request.GET.get("elastic_search")
            es_query = {
                'query': {
                    'bool': {
                        'must': [
                            {'match': {'unit_type': 'paragraph'}},
                            {'match': {'text': elastic_search}},
                        ]
                    }
                }
            }
            es_res = self.es.search(size=1000, index=settings.ELASTICSEARCH_CONFIG['index'],
                                    body=es_query)
            # See UpdateElasticsearchIndex in tasks.py for the set of indexed fields
            pks = [hit['_source']['pk'] for hit in es_res['hits']['hits']]
            qs = TextUnit.objects.filter(pk__in=pks)
        elif "text_contains" in self.request.GET:
            text_search = self.request.GET.get("text_contains")
            qs = self.filter(text_search, qs, _or_lookup='textunittext__text__icontains')

        if "party_id" in self.request.GET:
            qs = qs.filter(partyusage__party_id=self.request.GET['party_id'])
        elif "text_unit_hash" in self.request.GET:
            # Text Unit Detail identical text units tab
            qs = qs.filter(text_hash=self.request.GET['text_unit_hash']) \
                .exclude(pk=self.request.GET['text_unit_id'])
        else:
            qs = qs.filter(unit_type='paragraph')
        return qs.order_by('pk')


# --------------------------------------------------------
# Text Unit Tag Views
# --------------------------------------------------------

class TextUnitTagDetailSerializer(apps.common.mixins.SimpleRelationSerializer):
    class Meta:
        model = TextUnitTag
        fields = ['pk', 'tag', 'timestamp', 'user__username',
                  'text_unit__document__pk',
                  'text_unit__document__name', 'text_unit__document__document_type',
                  'text_unit__document__description', 'text_unit__pk',
                  'text_unit__unit_type', 'text_unit__language']


class TextUnitTagCreateSerializer(serializers.ModelSerializer):
    text_unit_id = serializers.PrimaryKeyRelatedField(
        source='text_unit', queryset=TextUnit.objects.all())

    class Meta:
        model = TextUnitTag
        fields = ['pk', 'tag', 'text_unit_id']


class TextUnitTagUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextUnitTag
        fields = ['tag']


class TextUnitTagViewSet(apps.common.mixins.JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: Text Unit Tag List
    retrieve: Retrieve Text Unit Tag
    create: Create Text Unit Tag
    update: Update Text Unit Tag
    partial_update: Partial Update Text Unit Tag
    delete: Delete Text Unit Tag
    """
    queryset = TextUnitTag.objects.all()

    def get_serializer_class(self):
        if self.action in 'create':
            return TextUnitTagCreateSerializer
        if self.action == 'update':
            return TextUnitTagUpdateSerializer
        return TextUnitTagDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('text_unit', 'text_unit__document')
        return qs


# --------------------------------------------------------
# Text Unit Note Views
# --------------------------------------------------------

class TextUnitNoteDetailSerializer(apps.common.mixins.SimpleRelationSerializer):
    history = serializers.SerializerMethodField()
    username = serializers.CharField(
        source='history.last.history_user.username',
        read_only=True)

    class Meta:
        model = TextUnitNote
        fields = ['pk', 'note', 'timestamp', 'text_unit__document__pk',
                  'text_unit__document__name', 'text_unit__document__document_type',
                  'text_unit__document__description', 'text_unit__pk',
                  'text_unit__unit_type', 'text_unit__language',
                  'username', 'history']

    def get_history(self, obj):
        return obj.history.values(
            'id', 'text_unit_id', 'history_date',
            'history_user__username', 'note')


class TextUnitNoteCreateSerializer(serializers.ModelSerializer):
    text_unit_id = serializers.PrimaryKeyRelatedField(
        source='text_unit', queryset=TextUnit.objects.all())

    class Meta:
        model = TextUnitNote
        fields = ['pk', 'note', 'text_unit_id']


class TextUnitNoteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextUnitNote
        fields = ['note']


class TextUnitNoteViewSet(apps.common.mixins.JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: Text Unit Note List
    retrieve: Retrieve Text Unit Note
    create: Create Text Unit Note
    update: Update Text Unit Note
    partial_update: Partial Update Text Unit Note
    delete: Delete Text Unit Note
    """
    queryset = TextUnitNote.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return TextUnitNoteCreateSerializer
        if self.action == 'update':
            return TextUnitNoteUpdateSerializer
        return TextUnitNoteDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('text_unit', 'text_unit__document')
        return qs


# --------------------------------------------------------
# Text Unit Property Views
# --------------------------------------------------------

class TextUnitPropertyDetailSerializer(apps.common.mixins.SimpleRelationSerializer):
    class Meta:
        model = TextUnitProperty
        fields = ['pk', 'key', 'value',
                  'created_date', 'created_by__username',
                  'modified_date', 'modified_by__username',
                  'text_unit__document__pk', 'text_unit__document__name',
                  'text_unit__document__document_type', 'text_unit__document__description',
                  'text_unit__unit_type', 'text_unit__language', 'text_unit__pk']


class TextUnitPropertyCreateSerializer(serializers.ModelSerializer):
    text_unit_id = serializers.PrimaryKeyRelatedField(
        source='text_unit', queryset=TextUnit.objects.all())

    class Meta:
        model = TextUnitProperty
        fields = ['pk', 'key', 'value', 'text_unit_id']


class TextUnitPropertyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextUnitProperty
        fields = ['key', 'value']


class TextUnitPropertyViewSet(apps.common.mixins.JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: Text Unit Property List
    retrieve: Retrieve Text Unit Property
    create: Create Text Unit Property
    update: Update Text Unit Property
    partial_update: Partial Update Text Unit Property
    delete: Delete Text Unit Property
    """
    queryset = TextUnitProperty.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return TextUnitPropertyCreateSerializer
        if self.action == 'update':
            return TextUnitPropertyUpdateSerializer
        return TextUnitPropertyDetailSerializer


# --------------------------------------------------------
# Typeahead Views for Global Search bar
# --------------------------------------------------------

class TypeaheadDocument(apps.common.mixins.TypeaheadAPIView):
    """
    Typeahead Document\n
        Kwargs: field_name: [name, description]
        GET params:
          - q: str
    """
    model = Document
    limit_reviewers_qs_by_field = ''


class TypeaheadTextUnitTag(apps.common.mixins.TypeaheadAPIView):
    """
    Typeahead Text Unit Tag\n
        Kwargs: field_name: [tag]
        GET params:
          - q: str
    """
    model = TextUnitTag
    limit_reviewers_qs_by_field = 'text_unit__document'


class TypeaheadDocumentProperty(apps.common.mixins.TypeaheadAPIView):
    """
    Typeahead Text Unit Property\n
        Kwargs: field_name: [key]
        GET params:
          - q: str
    """
    model = DocumentProperty
    limit_reviewers_qs_by_field = 'document'


# --------------------------------------------------------
# Document Field Views
# --------------------------------------------------------

class DocumentFieldCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFieldCategory
        fields = ['id', 'name', 'order']


class DocumentFieldDetailSerializer(apps.common.mixins.SimpleRelationSerializer):
    value_aware = serializers.SerializerMethodField()
    choices = serializers.SerializerMethodField()
    depends_on_fields = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = DocumentField
        fields = ['uid', 'document_type', 'code', 'long_code', 'title', 'description', 'type',
                  'text_unit_type', 'value_detection_strategy', 'python_coded_field',
                  'classifier_init_script', 'formula', 'value_regexp', 'depends_on_fields',
                  'confidence', 'requires_text_annotations', 'read_only', 'category',
                  'default_value', 'choices', 'allow_values_not_specified_in_choices',
                  'stop_words', 'metadata', 'training_finished', 'dirty', 'order',
                  'trained_after_documents_number', 'hidden_always',
                  'hide_until_python', 'hide_until_js',
                  'detect_limit_unit', 'detect_limit_count',
                  'display_yes_no', 'value_aware', 'created_by', 'modified_by',
                  'created_date', 'modified_date']

    def get_category(self, obj):
        return obj.category.name if obj.category else None

    def get_value_aware(self, obj: DocumentField):
        return TypedField.by(obj).requires_value

    def get_choices(self, obj: DocumentField):
        return obj.get_choice_values()

    def get_depends_on_fields(self, obj: DocumentField):
        return [field.pk for field in obj.depends_on_fields.all()]


class DocumentFieldListSerializer(DocumentFieldDetailSerializer):
    category = DocumentFieldCategorySerializer(many=False, read_only=True)


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
            if field_name in serializer_fields and form_field.disabled:
                serializer_fields[field_name].read_only = True
            if field_name in serializer_fields and form_field.help_text:
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
                  'confidence', 'requires_text_annotations', 'read_only', 'category',
                  'default_value', 'choices', 'allow_values_not_specified_in_choices',
                  'stop_words', 'metadata', 'training_finished', 'dirty', 'order',
                  'trained_after_documents_number', 'hidden_always', 'hide_until_python',
                  'hide_until_js', 'display_yes_no', 'detect_limit_unit', 'detect_limit_count']

    def is_valid(self, raise_exception=False):
        super().is_valid()
        UsersTasksValidationAdmin.validate_running_tasks(self.context['request'], self.errors)
        return True

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        signals.document_field_changed.send(self.__class__, user=None, document_field=instance)
        return instance


class DocumentFieldViewSet(apps.common.mixins.JqListAPIMixin,
                           apps.common.mixins.APIResponseMixin,
                           apps.common.mixins.APIFormFieldsMixin,
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
    permission_classes = (ReviewerReadOnlyPermission,)
    options_serializer = DocumentFieldCreateSerializer
    response_unifier_serializer = DocumentFieldDetailSerializer

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

    @action(detail=True, methods=['post'])
    def check_formula(self, request, **kwargs):
        """
        Either "request.formula" or "request.hide_until_python" should be filled.
        """
        field_code = 'formula'
        formula = request.data.get(field_code)
        check_return_value = True

        if not formula:
            field_code = 'hide_until_python'
            formula = request.data.get(field_code)
            check_return_value = False
            if not formula:
                raise RuntimeError('DocumentFieldViewSet.check_formula: either "formula" or ' +
                                   '"hide_until_python" should be provided in request')

        rst_default = self.get_formula_errors(False, check_return_value, formula)
        if rst_default.calculated:
            rst_empty = self.get_formula_errors(True, check_return_value, formula)
            if rst_empty.errors:
                rst_default.warnings += ['There were errors with not initialized fields:']
                rst_default.warnings += rst_empty.errors

        return Response(rst_default.__dict__, content_type='application/json')

    def get_formula_errors(self,
                           check_on_empty_values: bool,
                           check_return_value: bool,
                           formula: str):

        document_field = self.get_object()  # type: DocumentField
        try:
            _ = TypedField.by(document_field)
        except KeyError:
            raise RuntimeError(
                f'DocumentFieldViewSet.check_formula: No TypedField obtained from {document_field.code}')

        dependent_fields = list(DocumentField.objects.filter(
            document_type__code=document_field.document_type.code))

        if check_on_empty_values:
            fields_to_values = {field.code: None
                                for field in dependent_fields}
        else:
            fields_to_values = {field.code: TypedField.by(field).example_python_value()
                                for field in dependent_fields}

        result = DocumentFieldAdmin.calculate_formula_result_on_values(
            check_return_value, document_field, fields_to_values, formula)
        return result


# --------------------------------------------------------
# Document Field Detector Views
# --------------------------------------------------------

class DocumentFieldDetectorDetailSerializer(apps.common.mixins.SimpleRelationSerializer):
    include_regexps = serializers.SerializerMethodField()
    field = serializers.CharField()

    class Meta:
        model = DocumentFieldDetector
        fields = ['uid', 'category', 'field',
                  'field__code', 'field__title', 'field__uid', 'field__document_type__title',
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
    def validate_exclude_regexps(self, value):
        if value:
            DocumentFieldDetector.compile_regexps_string(value)

    @check
    def validate_include_regexps(self, value):
        if value:
            DocumentFieldDetector.compile_regexps_string(value)

    @check
    def validate(self, data):
        if self.context['request'].method == 'PATCH' and 'field' not in data:
            return
        DetectorFieldMatcher.validate_detected_value(data['field'].type,
                                                     data.get('detected_value'))


class DocumentFieldDetectorViewSet(apps.common.mixins.JqListAPIMixin,
                                   apps.common.mixins.APIFormFieldsMixin,
                                   apps.common.mixins.APIResponseMixin,
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
    permission_classes = (ReviewerReadOnlyPermission,)
    options_serializer = DocumentFieldDetectorCreateSerializer
    response_unifier_serializer = DocumentFieldDetectorDetailSerializer

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return DocumentFieldDetectorCreateSerializer
        return DocumentFieldDetectorDetailSerializer


# --------------------------------------------------------
# Document Type Views
# --------------------------------------------------------

class FieldSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = DocumentField
        fields = ['id', 'category', 'order']

    def get_id(self, obj):
        return str(obj.pk)


class FieldDataSerializer(DocumentFieldDetailSerializer):
    category = DocumentFieldCategorySerializer(many=False, read_only=True)

    class Meta:
        fields = DocumentFieldDetailSerializer.Meta.fields + ['category']
        model = DocumentField


class DocumentTypeDetailSerializer(apps.common.mixins.SimpleRelationSerializer):
    fields_data = FieldDataSerializer(source='fields', many=True, read_only=True)
    created_by = UserSerializer(many=False)
    modified_by = UserSerializer(many=False)

    class Meta:
        model = DocumentType
        fields = ['uid', 'title', 'code', 'fields_data', 'search_fields', 'modified_by__username',
                  'editor_type', 'created_by', 'created_date', 'modified_by', 'modified_date',
                  'metadata']

    def to_representation(self, instance):
        ret = dict(super().to_representation(instance))
        for field in ret.get('fields_data'):
            # set search field flag
            field['default'] = field['uid'] in ret['search_fields']
        # del ret['search_fields']
        return ret


class DocumentTypeCreateSerializer(ModelFormBasedSerializer):
    model_form_class = DocumentTypeForm
    fields = FieldSerializer(many=True, read_only=True)

    class Meta:
        model = DocumentType
        fields = ['uid', 'title', 'code', 'fields', 'search_fields', 'editor_type',
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

    def create(self, validated_data):
        instance = super().create(validated_data)
        return self.set_fields(instance)

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if self.context['view'].action == 'partial_update' and 'fields' not in self.context['request'].data:
            return instance
        return self.set_fields(instance)

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
    fields = FieldSerializer(many=True, required=False)

    class Meta:
        model = DocumentType
        fields = ['uid', 'title', 'code', 'fields', 'search_fields', 'editor_type',
                  'field_categories',
                  'created_by', 'created_date', 'modified_by', 'modified_date']


class DocumentTypeViewSet(apps.common.mixins.JqListAPIMixin,
                          apps.common.mixins.APIResponseMixin,
                          apps.common.mixins.APIFormFieldsMixin,
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

    permission_classes = (ReviewerReadOnlyPermission,)
    options_serializer = DocumentTypeOptionsSerializer
    response_unifier_serializer = DocumentTypeDetailSerializer

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return DocumentTypeCreateSerializer
        return DocumentTypeDetailSerializer

    def destroy(self, request, *args, **kwargs):
        errors = dict()
        UsersTasksValidationAdmin.validate_running_tasks(request, errors)
        if errors:
            raise DRFValidationError(errors)

        return super().destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
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
            raise Exception(f'do_save_document_field_value: ' +
                            f'FieldAnnotation(pk={request_data["pk"]}) was not found')
    elif 'document' in request_data:
        document = DocumentRepository().get_document_by_id(request_data['document'])
    else:
        raise Exception('Request data should contain either field annotation\'s "pk" or '
                        '"document" parameter, but none was provided.')

    field = field_repo.get_document_field_by_id(request_data['field'])

    annotation_value = request_data.get('value')
    typed_field = TypedField.by(field)

    if (isinstance(typed_field, BooleanField) or isinstance(typed_field, RelatedInfoField)) \
            and annotation_value is not None and not isinstance(annotation_value, bool):
        annotation_value = True if str(annotation_value).lower() == 'yes' else \
            False if str(annotation_value).lower() == 'no' else None

    location_start = request_data.get('location_start')
    location_end = request_data.get('location_end')
    location_text = None
    if location_start is not None and location_end is not None:
        location_text = document.full_text[location_start:location_end]

    annotation_value, hint = typed_field.get_or_extract_value(document, annotation_value, None, location_text)
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
    dto = FieldValueDTO(field_value=field_value, annotations=[])

    if location_start is not None and location_end is not None:
        ant = AnnotationDTO(
            extraction_hint_name=hint,
            annotation_value=annotation_value,
            location_in_doc_start=location_start,
            location_in_doc_end=location_end)
        dto.annotations.append(ant)

    field_val, field_ants = field_repo.update_field_value_with_dto(
        document=document, field=field, field_value_dto=dto,
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
# Document Field Value History Views
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

    def validate(self, attrs):
        return super().validate(attrs)

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

    def get_serializer_class(self):
        return AnnotationInDocumentSerializer

    def perform_destroy(self, instance: FieldAnnotation):
        field_repo = DocumentFieldRepository()
        user = self.request.user
        field_repo.delete_field_annotation_and_update_field_value(instance, user)
        cache_and_detect_field_values(doc=instance.document, user=user, updated_fields={instance.field})


# --------------------------------------------------------
# Document Field Value Views
# --------------------------------------------------------

class DocumentFieldValueSerializer(serializers.ModelSerializer):
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
                  'modified_by',
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
            ret['annotations'] = FieldAnnotation.objects.filter(field=instance.field, document=instance.document)\
                .values('pk', 'location_start', 'location_end', 'location_text')
        return ret


class DocumentFieldValueViewSet(apps.common.mixins.JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: Document Field Value List
    retrieve: Document Field Value Details
    """
    queryset = FieldValue.objects.all()
    serializer_class = DocumentFieldValueSerializer
    http_method_names = ['get']

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(value__isnull=False, document__delete_pending=False)

        # via project router
        project_id = self.kwargs.get('project_pk')
        if project_id:
            qs = qs.filter(document__project_id=project_id)

        field_annotation_subquery = FieldAnnotation.objects\
            .filter(field=OuterRef("field"), document=OuterRef("document"))\
            .order_by('field', 'document')\
            .values('field', 'document')\
            .annotate(ann=GroupConcat('location_text', '\n-----\n'))

        qs = qs.annotate(
            project=F('document__project__name'),
            project_id=F('document__project_id'),
            document_name=F('document__name'),
            document_status=F('document__status__name'),
            field_name=Concat('field__document_type__title', Value(': '), 'field__title'))

        qs = qs.select_related('document', 'document__project', 'document__status',
                               'field', 'field__document_type')

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
            'modified_by', 'modified_date')

        return qs


# --------------------------------------------------------
#  Field Annotation Status Views
# --------------------------------------------------------

class FieldAnnotationStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = FieldAnnotationStatus
        fields = '__all__'


class FieldAnnotationStatusViewSet(apps.common.mixins.JqListAPIMixin, viewsets.ModelViewSet):
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
    assignee_name = serializers.SerializerMethodField()

    class Meta:
        model = FieldAnnotation
        list_serializer_class = GeneratorListSerializer
        fields = ['pk',
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
                  'status_id',
                  'status_name',
                  'assignee_id',
                  'assign_date',
                  'assignee_name',
                  'modified_by',
                  'modified_date']

    def get_assignee_name(self, obj):
        if obj.assignee:
            return obj.assignee.get_full_name()

    def get_field_names(self, declared_fields, info):
        columns = self.context['view'].request.GET.get('columns')
        if columns:
            columns = columns.split(',')
            self.Meta.fields = columns
            declared_fields = OrderedDict([(k, v) for k, v in self._declared_fields.items() if k in columns])
        return super().get_field_names(declared_fields, info)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        view = self.context['view']
        if view.action == 'retrieve':
            # get prev/next FieldAnnotation id using the same sort order and filters from list view
            qs = view.get_queryset()
            qs = view.filter_queryset(qs)
            ids = list(qs.filter(field=instance.field).values_list('pk', flat=True))
            pos = ids.index(instance.pk)
            prev_ids = ids[:pos]
            next_ids = ids[pos + 1:]
            ret['prev_id'] = prev_ids[-1] if prev_ids else None
            ret['next_id'] = next_ids[0] if next_ids else None
        return ret

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if 'assignee_id' in validated_data:
            instance.assign_date = now()
            instance.save()
        return instance


class DocumentFieldAnnotationViewSet(apps.common.mixins.JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: Field Annotation List
    retrieve: Annotation Details
    partial_update: Update Annotation
    """
    queryset = FieldAnnotation.objects.all()
    serializer_class = DocumentFieldAnnotationSerializer
    http_method_names = ['get', 'patch']

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(value__isnull=False, document__delete_pending=False)

        # via project router
        project_id = self.kwargs.get('project_pk')
        if project_id:
            qs = qs.filter(document__project_id=project_id)

        qs = qs.annotate(
            project_id=F('document__project_id'),
            project_name=F('document__project__name'),
            document_name=F('document__name'),
            document_status=F('document__status__name'),
            field_name=Concat('field__document_type__title', Value(': '), 'field__title'),
            status_name=F('status__name'),
        )

        qs = qs.select_related('document', 'document__status', 'document__project',
                               'field', 'field__document_type', 'assignee', 'status')

        qs = qs.only(
            'document__project_id', 'document__project__name',
            'document_id', 'document__name', 'document__status__name',
            'field_id', 'field__type', 'field__title',
            'field__document_type__title',
            'location_start', 'location_end', 'location_text',
            'value',
            'status_id', 'status__name',
            'assignee_id',
            'assignee__name', 'assignee__first_name', 'assignee__last_name', 'assignee__username',
            'assign_date',
            'modified_by', 'modified_date'
        )

        return qs.order_by('field_name', 'document_name')

    def get_extra_data(self, queryset):
        total_annotations_count = self.get_queryset().count()
        completed_annotations_count = self.get_queryset().filter(status__is_confirm=True).count()
        return dict(total_annotations_count=total_annotations_count,
                    completed_annotations_count=completed_annotations_count)

    def filter_queryset(self, queryset):

        project_id = self.kwargs.get('project_pk')
        request_data = self.request.GET
        columns = request_data.get('columns')
        save_filter = request_data.get('save_filter', False)

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

                    if not request_data._mutable:
                        request_data._mutable = True

                    if user_filter.column_filters:
                        request_data.update(user_filter.column_filters)
                    if user_filter.order_by:
                        request_data.update(user_filter.order_by)
                    if user_filter.columns:
                        request_data['columns'] = user_filter.columns

                    request_data._mutable = False

        return super().filter_queryset(queryset)


main_router = routers.DefaultRouter()
main_router.register(r'documents', DocumentViewSet, 'document')
main_router.register(r'document-fields', DocumentFieldViewSet, 'document-field')
main_router.register(r'document-field-detectors', DocumentFieldDetectorViewSet, 'document-field-detector')
main_router.register(r'document-field-values', DocumentFieldValueViewSet, 'document-field-values')
main_router.register(r'document-field-annotations', DocumentFieldAnnotationViewSet, 'document-field-annotations')
main_router.register(r'field-annotation-statuses', FieldAnnotationStatusViewSet, 'field-annotation-status')

main_router.register(r'annotations', AnnotationViewSet, 'annotation')

main_router.register(r'document-properties', DocumentPropertyViewSet, 'document-property')
main_router.register(r'document-notes', DocumentNoteViewSet, 'document-note')
main_router.register(r'document-tags', DocumentTagViewSet, 'document-tag')
main_router.register(r'text-units', TextUnitViewSet, 'text-unit')
main_router.register(r'text-unit-tags', TextUnitTagViewSet, 'text-unit-tag')
main_router.register(r'text-unit-notes', TextUnitNoteViewSet, 'text-unit-note')
main_router.register(r'text-unit-properties', TextUnitPropertyViewSet, 'text-unit-property')

# route documents via document type
document_type_router = routers.SimpleRouter()
document_type_router.register(r'document-types', DocumentTypeViewSet, 'document-types')
document_via_type_router = nested_routers.NestedSimpleRouter(
    document_type_router, r'document-types', lookup='document_type', trailing_slash=True)
document_via_type_router.register(r'documents', ProjectDocumentsWithFieldsViewSet, 'documents')

# route documents via project
project_router = routers.SimpleRouter()

project_router.register(r'project', project_api_module.ProjectViewSet, 'project')
document_via_project_router = nested_routers.NestedSimpleRouter(
    project_router, r'project', lookup='project', trailing_slash=True)
document_via_project_router.register(r'documents', ProjectDocumentsWithFieldsViewSet, 'documents')

# route field values via project
field_value_via_project_router = nested_routers.NestedSimpleRouter(
    project_router, r'project', lookup='project', trailing_slash=True)
field_value_via_project_router.register(
    r'document-field-values', DocumentFieldValueViewSet, 'project-document-field-values')

# route clauses (field annotations) via project
field_annotation_via_project_router = nested_routers.NestedSimpleRouter(
    project_router, r'project', lookup='project', trailing_slash=True)
field_annotation_via_project_router.register(
    r'document-field-annotations', DocumentFieldAnnotationViewSet, 'project-document-field-annotations')

annotation_via_document_router = nested_routers.NestedSimpleRouter(
    document_via_project_router, r'documents', lookup='document', trailing_slash=True)
annotation_via_document_router.register(r'annotations', AnnotationsInDocumentViewSet, 'annotations')

api_routers = [main_router, document_type_router,
               document_via_type_router, document_via_project_router,
               field_value_via_project_router, field_annotation_via_project_router,
               annotation_via_document_router]

urlpatterns = [

    url(r'^typeahead/document/(?P<field_name>[a-z_]+)/$', TypeaheadDocument.as_view(),
        name='typeahead-document'),
    url(r'^typeahead/document-property/(?P<field_name>[a-z_]+)/$',
        TypeaheadDocumentProperty.as_view(),
        name='typeahead-document-property'),
    url(r'^typeahead/text-unit-tag/(?P<field_name>[a-z_]+)/$', TypeaheadTextUnitTag.as_view(),
        name='typeahead-text-unit-tag'),

    url(r'stats/$', StatsAPIView.as_view(),
        name='stats'),
]
