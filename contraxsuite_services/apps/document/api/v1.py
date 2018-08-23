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
import io
import json
import traceback
from tempfile import NamedTemporaryFile

# Django imports
from django.conf import settings
from django.conf.urls import url
from django.contrib.postgres.aggregates.general import StringAgg
from django.core import serializers as core_serializers
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.db.models import F, Min, Max,\
    IntegerField, FloatField, DateField, TextField
from django.http import JsonResponse, HttpResponse

# Third-party imports
import numpy as np
import pandas as pd
from elasticsearch import Elasticsearch
from rest_framework import serializers, routers, viewsets, status
from rest_framework.decorators import detail_route
from rest_framework.generics import ListAPIView
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_nested import routers as nested_routers

# Project imports
from apps.analyze.models import *
from apps.common.api.permissions import ReviewerReadOnlyPermission
from apps.common.mixins import (
    SimpleRelationSerializer, JqListAPIMixin, TypeaheadAPIView,
    NestedKeyTextTransform)
from apps.common.models import ReviewStatus
from apps.common.utils import get_api_module
from apps.document.field_types import FIELD_TYPES_REGISTRY
from apps.document.models import (
    DocumentField, DocumentType, DocumentFieldValue, DocumentFieldDetector,
    DocumentProperty, DocumentNote, DocumentTag, DocumentRelation,
    TextUnitProperty, TextUnitNote, TextUnitTag, DocumentTypeField)
from apps.document.tasks import TrainDocumentFieldDetectorModel
from apps.extract.models import *
from apps.task.models import Task
from apps.task.tasks import call_task_func
from apps.users.models import User
from apps.document.views import show_document

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.3/LICENSE"
__version__ = "1.1.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

common_api_module = get_api_module('common')
project_api_module = get_api_module('project')
extract_api_module = get_api_module('extract')


# --------------------------------------------------------
# Document Views
# --------------------------------------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'first_name', 'last_name', 'username', 'role']


class BaseDocumentSerializer(SimpleRelationSerializer):
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
        fields = ['pk', 'name', 'document_type', 'file_size',
                  'status', 'status_data', 'status_name', 'available_statuses_data',
                  'assignee', 'assignee_data', 'assignee_name', 'available_assignees_data',
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


class GenericDocumentSerializer(SimpleRelationSerializer):
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
        fields = ['pk', 'name', 'cluster_id', 'file_size',
                  'parties', 'min_date', 'max_date',
                  'max_currency_amount', 'max_currency_name']


class DocumentWithFieldsDetailSerializer(BaseDocumentSerializer):
    """
    Serializer for document review page with detailed document field values
    """
    field_value_objects = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['pk', 'name', 'document_type', 'file_size',
                  'status', 'status_data', 'available_statuses_data',
                  'assignee', 'assignee_data', 'available_assignees_data',
                  'description', 'title', 'full_text',
                  'field_value_objects', 'field_values']

    def get_field_value_objects(self, doc):
        field_uids_to_field_value_objects = {}
        for fv in doc.documentfieldvalue_set.all():
            serialized_fv = DocumentFieldValueSerializer(fv).data
            field = fv.field
            field_uid = field.uid
            field_type = FIELD_TYPES_REGISTRY[fv.field.type]
            if field_type.multi_value:
                if field_uids_to_field_value_objects.get(field_uid) is None:
                    field_uids_to_field_value_objects[field_uid] = [serialized_fv]
                else:
                    field_uids_to_field_value_objects[field_uid].append(serialized_fv)
            else:
                field_uids_to_field_value_objects[field_uid] = serialized_fv
        return field_uids_to_field_value_objects


class DocumentWithFieldsListSerializer(BaseDocumentSerializer):
    """
    Serializer for document list page with document field values
    """
    search_field_values = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['pk', 'name', 'document_type',
                  'description', 'title', 'file_size',
                  'status', 'status_data', 'status_name',
                  'assignee', 'assignee_data', 'assignee_name',
                  'field_values', 'search_field_values']

    def get_search_field_values(self, doc):
        if not doc.field_values:
            return {}
        return {k: v for k, v in doc.field_values.items() if hasattr(doc, k.replace('-', '_'))}


class ExtendedDocumentWithFieldsListSerializer(GenericDocumentSerializer,
                                               DocumentWithFieldsListSerializer):
    """
    Extended serializer for document list page with document field values
    + values for Generic Contract type document
    """
    class Meta:
        model = Document
        fields = ['pk', 'name', 'document_type', 'cluster_id',
                  'description', 'title', 'file_size',
                  'status', 'status_data', 'status_name',
                  'assignee', 'assignee_data', 'assignee_name',
                  'field_values', 'search_field_values',
                  'cluster_id', 'parties',
                  'min_date', 'max_date',
                  'max_currency_amount', 'max_currency_name']


class ExportDocumentWithFieldsListSerializer(ExtendedDocumentWithFieldsListSerializer):
    """
    Extended serializer for export document list page with document field values
    + values for Generic Contract type document
    """
    status_name = serializers.SerializerMethodField()
    assignee_name = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['pk', 'name', 'cluster_id',
                  'description', 'title', 'file_size',
                  'status_name', 'assignee_name',
                  'field_values',
                  'cluster_id', 'parties',
                  'min_date', 'max_date',
                  'max_currency_amount', 'max_currency_name']

    def get_status_name(self, obj):
        return obj.status.name if obj.status else None

    def get_assignee_name(self, obj):
        return obj.assignee.get_full_name() if obj.assignee else None


class DocumentPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_reviewer and view.kwargs.get('project_pk'):
            return project_api_module.Project.objects.filter(pk=view.kwargs.get('project_pk'),
                                                             reviewers=request.user).exists()
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_reviewer:
            return obj.project.reviewers.filter(pk=request.user.pk).exists()
        return True


class DocumentPermissionViewMixin(object):
    permission_classes = (IsAuthenticated, DocumentPermissions)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_reviewer:
            qs = qs.filter(project__reviewers=self.request.user)
        return qs


class DocumentViewSet(DocumentPermissionViewMixin, JqListAPIMixin, viewsets.ModelViewSet):
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
        qs = super().get_queryset()

        party_id = self.request.GET.get("party_id")
        if party_id:
            qs = qs.filter(textunit__partyusage__party__pk=party_id)

        project_id = self.request.GET.get("project_id")

        is_generic = DocumentType.generic().project_set.filter(pk=project_id).exists()

        # only for projects with GenericContract type and project detail view
        if is_generic and project_id:
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

        qs = qs.select_related('document_type', 'status', 'status__group', 'assignee')

        return qs

    def get_serializer_class(self, *args, **kwargs):
        # if project and project is of Generic Contract type
        if self.request.GET.get('project_id') and \
                 DocumentType.generic().project_set.filter(pk=self.request.GET['project_id']).exists():
            return GenericDocumentSerializer
        if self.action == 'list':
            return DocumentWithFieldsListSerializer
        return DocumentWithFieldsDetailSerializer

    @detail_route(methods=['get'])
    def extraction(self, request, **kwargs):
        """
        Standard extracted info - Top level + details\n
            Params:
                - skip_details: bool - show top-level data only (skip per text-unit data)
                - values: str - list of str separated by comma like dates,parties,courts
        """
        document = self.get_object()
        class_kwargs = dict(request=request, format_kwarg=None, document_id=document.id)
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
            geo_entities=extract_api_module.TopGeoEntityUsageListAPIView,
            geo_aliases=extract_api_module.TopGeoAliasUsageListAPIView,
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
            if statuses == {'FAILURE'}:
                remove_session = True
        if remove_session:
            # delete session documents' tasks
            session.session_tasks.delete()
            session.delete()
        return Response({'session_removed': remove_session}, status=200)

    @detail_route(methods=['get'])
    def show(self, request, **kwargs):
        document = self.get_object()
        return show_document(request, document.pk)


transform_map = {
    'float': FloatField,
    'int': IntegerField,
    'date': DateField,
    'duration': FloatField,
    'amount': FloatField,
    'money': (FloatField, 'amount'),
    'address': (TextField, 'address'),
    'geography': (TextField, 'entity__name'),
}


def create_field_annotation(field_uid, field_type):
    """
    Create annotation for "metadata__field_values__uid__maybe" json field
    """
    _field_uid = field_uid.replace('-', '_')
    output_field = transform_map.get(field_type, TextField)
    if isinstance(output_field, tuple):
        output_field = output_field[0]
    transform = NestedKeyTextTransform([field_uid], 'field_values', output_field=output_field())
    transform.key_name = field_uid
    return {_field_uid: transform}


def create_full_field_annotation(field_uid, field_type):
    """
    Create annotation for "metadata__field_values__uid__maybe" json field
    """
    nested_fields = []
    _field_uid = field_uid.replace('-', '_')
    output_field = transform_map.get(field_type, TextField)
    if isinstance(output_field, (tuple, list)):
        output_field, nested_fields = output_field[:2]
    if isinstance(nested_fields, str):
        nested_fields = [nested_fields]
    nested_fields = ['field_values', field_uid] + nested_fields
    return {
        _field_uid: NestedKeyTextTransform(nested_fields, 'metadata', output_field=output_field())}


class DocumentWithFieldsViewSet(DocumentPermissionViewMixin, JqListAPIMixin, viewsets.ReadOnlyModelViewSet):
    """
    list: Document List with Fields
    retrieve: Document Detail with Fields
    """
    queryset = Document.objects.all()

    def get_queryset(self):

        qs = super().get_queryset()

        document_type_pk = self.kwargs.get('document_type_pk')
        if document_type_pk:
            qs = qs.filter(document_type__pk=document_type_pk)

        project_pk = self.kwargs.get('project_pk')
        if project_pk:
            qs = qs.filter(project__pk=project_pk)

        cluster_id = self.request.GET.get("cluster_id")
        if cluster_id:
            qs = qs.filter(cluster_id=int(cluster_id))

        qs = qs.select_related('document_type', 'status', 'status__group')

        # annotate documents with fields data document.a_field_uid = value
        # to filter and sort by field values
        if qs.exists():
            field_data = DocumentField.objects.filter(
                search_field_document_type__pk__in=qs.values_list('document_type__pk', flat=True))\
                .values_list('pk', 'type')
            for uid, _type in field_data:
                qs = qs.annotate(**create_field_annotation(uid, _type))

        # add extra annotates based on extracted data
        qs = qs \
            .annotate(cluster_id=Max('documentcluster'),
                      assignee_name=F('assignee__username'),
                      status_name=F('status__name'),
                      parties=StringAgg('textunit__partyusage__party__name',
                                        delimiter=', ',
                                        distinct=True),
                      max_currency_amount=Max('textunit__currencyusage__amount'),
                      max_currency_name=Max('textunit__currencyusage__currency'),
                      min_date=Min('textunit__dateusage__date'),
                      max_date=Max('textunit__dateusage__date'))

        # !!! this can be ineffective - throws additional queries in Document.get_field_values !!!
        qs = qs.defer('language', 'source', 'source_type', 'source_path', 'full_text',
                      'paragraphs', 'sentences', 'upload_session_id')

        return qs

    def get_extra_data(self, queryset):
        reviewed = queryset.filter(status__is_active=False).count()
        return {'reviewed_total': reviewed}

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'list':
            if self.request.GET.get('export_to'):
                return ExportDocumentWithFieldsListSerializer
            project_pk = self.kwargs.get('project_pk')
            is_generic = DocumentType.generic().project_set.filter(pk=project_pk).exists()
            if is_generic and project_pk:
                return ExtendedDocumentWithFieldsListSerializer
            return DocumentWithFieldsListSerializer
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
            data[field['title']] = data['field_values'].apply(lambda x: x.get(field['pk']))
        return data

    @detail_route(methods=['get'])
    def show(self, request, **kwargs):
        document = self.get_object()
        return show_document(request, document.pk)


class DocumentSentimentChartAPIView(ListAPIView):
    """
    Document Sentiment Chart
    """

    def list(self, request, *args, **kwargs):
        data = []
        documents = Document.objects \
            .filter(documentproperty__key='polarity') \
            .filter(documentproperty__key='subjectivity')
        for doc in documents:
            try:
                data.append(dict(
                    pk=doc.pk,
                    url=reverse('v1:document-detail', args=[doc.pk]),
                    name=doc.name,
                    polarity=float(doc.documentproperty_set.filter(
                        key='polarity').first().value),
                    subjectivity=float(doc.documentproperty_set.filter(
                        key='subjectivity').first().value)))
            except (AttributeError, ValueError):
                pass
        return JsonResponse(data, safe=False)


# --------------------------------------------------------
# Document Property Views
# --------------------------------------------------------

class DocumentPropertyDetailSerializer(SimpleRelationSerializer):
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


class DocumentPropertyViewSet(JqListAPIMixin, viewsets.ModelViewSet):
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
# Document Note Views
# --------------------------------------------------------

class DocumentNoteDetailSerializer(SimpleRelationSerializer):
    username = serializers.CharField(
        source='history.last.history_user.username',
        read_only=True)
    history = serializers.SerializerMethodField()

    class Meta:
        model = DocumentNote
        fields = ['pk', 'note', 'timestamp',
                  'document__pk', 'document__name',
                  'document__document_type', 'document__description',
                  'username', 'history']

    def get_history(self, obj):
        return obj.history.values(
            'id', 'document_id', 'history_date',
            'history_user__username', 'note')


class DocumentNoteCreateSerializer(serializers.ModelSerializer):
    document_id = serializers.PrimaryKeyRelatedField(
        source='document', queryset=Document.objects.all())

    class Meta:
        model = DocumentNote
        fields = ['pk', 'note', 'document_id']


class DocumentNoteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentNote
        fields = ['note']


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

    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentNoteCreateSerializer
        if self.action == 'update':
            return DocumentNoteUpdateSerializer
        return DocumentNoteDetailSerializer


# --------------------------------------------------------
# Document Tag Views
# --------------------------------------------------------

class DocumentTagDetailSerializer(SimpleRelationSerializer):
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


class DocumentTagViewSet(JqListAPIMixin, viewsets.ModelViewSet):
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

class TextUnitDetailSerializer(SimpleRelationSerializer):
    class Meta:
        model = TextUnit
        fields = ['pk', 'unit_type', 'language', 'text', 'text_hash',
                  'document__pk', 'document__name',
                  'document__document_type', 'document__description']


class TextUnitViewSet(JqListAPIMixin, viewsets.ReadOnlyModelViewSet):
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
            qs = self.filter(text_search, qs, _or_lookup='text__icontains')

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

class TextUnitTagDetailSerializer(SimpleRelationSerializer):
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


class TextUnitTagViewSet(JqListAPIMixin, viewsets.ModelViewSet):
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

class TextUnitNoteDetailSerializer(SimpleRelationSerializer):
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


class TextUnitNoteViewSet(JqListAPIMixin, viewsets.ModelViewSet):
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

class TextUnitPropertyDetailSerializer(SimpleRelationSerializer):
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


class TextUnitPropertyViewSet(JqListAPIMixin, viewsets.ModelViewSet):
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

class TypeaheadDocument(TypeaheadAPIView):
    """
    Typeahead Document\n
        Kwargs: field_name: [name, description]
        GET params:
          - q: str
    """
    model = Document
    limit_reviewers_qs_by_field = ''


class TypeaheadTextUnitTag(TypeaheadAPIView):
    """
    Typeahead Text Unit Tag\n
        Kwargs: field_name: [tag]
        GET params:
          - q: str
    """
    model = TextUnitTag
    limit_reviewers_qs_by_field = 'text_unit__document'


class TypeaheadDocumentProperty(TypeaheadAPIView):
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

class DocumentFieldDetailSerializer(SimpleRelationSerializer):
    calculated = serializers.SerializerMethodField()

    class Meta:
        model = DocumentField
        fields = ['uid', 'code', 'title', 'description', 'type', 'choices', 'calculated',
                  'formula', 'modified_by__username', 'modified_date']

    def get_calculated(self, obj):
        return bool(obj.is_calculated())


class DocumentFieldCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentField
        fields = ['uid', 'code', 'title', 'description', 'type', 'choices']


class DocumentFieldViewSet(JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: Document Field List
    retrieve: Retrieve Document Field
    create: Create Document Field
    update: Update Document Field
    partial_update: Partial Update Document Field
    delete: Delete Document Field
    """
    queryset = DocumentField.objects.all()
    permission_classes = (ReviewerReadOnlyPermission,)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return DocumentFieldCreateSerializer
        return DocumentFieldDetailSerializer


# --------------------------------------------------------
# Document Type Views
# --------------------------------------------------------

class DocumentTypeDetailSerializer(SimpleRelationSerializer):
    fields_data = DocumentFieldDetailSerializer(
        source='fields', many=True, read_only=True)
    search_fields_data = DocumentFieldDetailSerializer(
        source='search_fields', many=True, read_only=True)

    class Meta:
        model = DocumentType
        fields = ['uid', 'code', 'title',
                  'fields_data', 'search_fields_data',
                  'modified_by__username', 'modified_date']


class DocumentTypeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ['uid', 'code', 'title', 'fields', 'search_fields']


class DocumentTypeViewSet(JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: Document Type List\n
    retrieve: Retrieve Document Type
    create: Create Document Type
    update: Update Document Type
    partial_update: Partial Update Document Type
    delete: Delete Document Type
    """
    queryset = DocumentType.objects.select_related('modified_by')\
        .prefetch_related('fields', 'search_fields')
    permission_classes = (ReviewerReadOnlyPermission,)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return DocumentTypeCreateSerializer
        return DocumentTypeDetailSerializer


# --------------------------------------------------------
# Document Field Value Views
# --------------------------------------------------------

def _trigger_retraining(document_type_uid, field_uid, user_id):
    if settings.FIELDS_RETRAIN_MODEL_ON_ANNOTATIONS_CHANGE:
        call_task_func(TrainDocumentFieldDetectorModel.train_model_for_field,
                       (document_type_uid, field_uid, None, True), user_id=user_id)


class DocumentFieldValueSerializer(serializers.ModelSerializer):
    adapter = None

    class Meta:
        model = DocumentFieldValue
        fields = ['pk',
                  'document',
                  'field',
                  'location_start', 'location_end', 'location_text',
                  'value',
                  'created_by', 'created_date', 'modified_by', 'modified_date']

    def save(self, **kwargs):
        field = self.validated_data['field']
        self.adapter = FIELD_TYPES_REGISTRY.get(field.type)
        return super().save(**kwargs)

    def create(self, validated_data):
        document = validated_data['document']
        location_start = validated_data['location_start']
        location_end = validated_data['location_end']
        field = validated_data['field']
        sentence_text_unit = TextUnit.objects.filter(document=document,
                                                     unit_type='sentence',
                                                     location_start__lte=location_end,
                                                     location_end__gte=location_start).first()
        res = self.adapter.save_value(document,
                                      field,
                                      location_start,
                                      location_end,
                                      validated_data['location_text'],
                                      sentence_text_unit,
                                      validated_data['value'],
                                      self.context['request'].user,
                                      True)

        _trigger_retraining(document.document_type_id, field.uid)

        return res

    def delete(self, instance: DocumentFieldValue, validated_data):
        res = self.adapter.delete(instance)
        _trigger_retraining(instance.document.document_type_id, instance.field_id)
        return res


class DocumentFieldValueViewSet(JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: Document Field Value List
    retrieve: Retrieve Document Field Value
    create: Create Document Field Value
    update: Update Document Field Value
    partial_update: Partial Update Document Field Value
    delete: Delete Document Field Value
    """
    queryset = DocumentFieldValue.objects.all()
    serializer_class = DocumentFieldValueSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(value__isnull=False)

        document_type_code = self.request.GET.get('document_type_code')
        if document_type_code:
            qs = qs.filter(document__type__code=document_type_code)

        document_id = self.request.GET.get('document_id')
        if document_id:
            qs = qs.filter(document_id=document_id)

        field_code = self.request.GET.get('field_code')
        if field_code:
            qs = qs.filter(field__code=field_code)

        value = self.request.GET.get('value')
        if value:
            qs = qs.filter(value__val=value)

        return qs

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        adapter = FIELD_TYPES_REGISTRY.get(instance.field.type)
        adapter.delete(instance)
        _trigger_retraining(instance.document.document_type_id, instance.field_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


# --------------------------------------------------------
# Document Field Value History Views
# --------------------------------------------------------

class DocumentFieldValueHistorySerializer(SimpleRelationSerializer):
    object_id = serializers.SerializerMethodField()
    history_id = serializers.SerializerMethodField()
    history_user = serializers.SerializerMethodField()
    history_date = serializers.SerializerMethodField()
    history_type = serializers.SerializerMethodField()
    latest_history_type = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    class Meta:
        model = DocumentFieldValue
        fields = ['history_id', 'object_id', 'document_id', 'document__name',
                  'document__type__code', 'document__type__title',
                  'field_id', 'field__code', 'field__type', 'field__title',
                  'value', 'history_user', 'history_date', 'history_type',
                  'latest_history_type']

    def get_value(self, obj):
        return obj.history_object.val

    def get_object_id(self, obj):
        return obj.history_object.pk

    def get_history_id(self, obj):
        return obj.pk

    def get_history_user(self, obj):
        user = obj.history_user
        return user.username if user else None

    def get_history_date(self, obj):
        return obj.history_date

    def get_history_type(self, obj):
        return obj.get_history_type_display()

    def get_latest_history_type(self, obj):
        return obj.instance.history.latest().get_history_type_display()


class DocumentFieldValueHistoryViewSet(JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: Document Field Value History List
    retrieve: Retrieve Document Field Value History
    update: Update Document Field Value History\n
        Apply specific history state
    """
    queryset = DocumentFieldValue.history.all()
    serializer_class = DocumentFieldValueHistorySerializer
    http_method_names = ['get', 'put']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by('document_id', 'field__code', 'history_date')

    def update(self, request, *args, **kwargs):
        hist_object = self.get_object()
        source_object = hist_object.instance
        source_object.save()
        serializer = self.get_serializer(source_object.history.latest())
        return Response(serializer.data)


class StatsAPIView(APIView):
    def get(self, request, *args, **kwargs):

        # get admin tasks data
        task_api_module = get_api_module('task')
        task_api_view = task_api_module.TaskViewSet(request=request)
        task_api_view.format_kwarg = {}
        admin_task_df = pd.DataFrame(task_api_view.list(request=request).data)
        admin_task_total_count = admin_task_df.shape[0]
        admin_task_by_status_count = dict(admin_task_df.groupby(['status']).size()) \
            if not admin_task_df.empty else 0

        # get projects data
        project_api_view = project_api_module.ProjectViewSet(request=request)
        project_api_view.format_kwarg = {}
        project_data = project_api_view.list(request=request).data
        if not project_data:
            project_total_count = project_completed_count = project_completed_weight = \
                project_progress_avg = project_documents_total_count = \
                project_documents_unique_count = 0
        else:
            for i in project_data:
                progress_data = i.pop('progress')
                i.update(progress_data)
            project_df = pd.DataFrame(project_data)
            project_df['completed'] = np.where(project_df['progress'] == 100, 1, 0)
            project_total_count = project_df.shape[0]
            project_df_sum = project_df.sum()
            project_completed_count = project_df_sum.completed
            project_completed_weight = round(project_completed_count / project_total_count * 100, 1)
            project_progress_avg = round(project_df.mean().progress, 1)
            project_documents_total_count = project_df_sum.total_documents_count
            project_documents_unique_count = Document.objects.filter(
                taskqueue__project__isnull=False) \
                .distinct().count()

        # get task queues data
        task_queue_api_view = project_api_module.TaskQueueViewSet(request=request)
        task_queue_api_view.format_kwarg = {}
        task_queue_data = task_queue_api_view.list(request=request).data
        if not task_queue_data:
            task_queue_total_count = task_queue_completed_count = task_queue_completed_weight = \
                task_queue_progress_avg = task_queue_documents_total_count = \
                task_queue_documents_unique_count = task_queue_reviewers_unique_count = 0
        else:
            for i in task_queue_data:
                progress_data = i.pop('progress')
                i.update(progress_data)
            task_queue_df = pd.DataFrame(task_queue_data)
            task_queue_df['completed'] = np.where(task_queue_df['progress'] == 100, 1, 0)
            task_queue_total_count = task_queue_df.shape[0]
            task_queue_df_sum = task_queue_df.sum()
            task_queue_completed_count = task_queue_df_sum.completed
            task_queue_completed_weight = round(
                task_queue_completed_count / task_queue_total_count * 100, 1)
            task_queue_progress_avg = round(task_queue_df.mean().progress, 1)
            task_queue_documents_total_count = task_queue_df_sum.total_documents_count
            task_queue_documents_unique_count = Document.objects.filter(taskqueue__isnull=False) \
                .distinct().count()
            task_queue_reviewers_unique_count = User.objects.filter(taskqueue__isnull=False) \
                .distinct().count()

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
            "project_progress_avg": project_progress_avg,
            "project_documents_total_count": project_documents_total_count,
            "project_documents_unique_count": project_documents_unique_count,
            "task_queue_total_count": task_queue_total_count,
            "task_queue_completed_count": task_queue_completed_count,
            "task_queue_completed_weight": task_queue_completed_weight,
            "task_queue_progress_avg": task_queue_progress_avg,
            "task_queue_documents_total_count": task_queue_documents_total_count,
            "task_queue_documents_unique_count": task_queue_documents_unique_count,
            "task_queue_reviewers_unique_count": task_queue_reviewers_unique_count,
            "admin_task_total_count": admin_task_total_count,
            "admin_task_by_status_count": admin_task_by_status_count,
        }
        return Response(data)


class DumpDocumentTypeConfigView(APIView):
    def get_full_dump(self):
        return list(DocumentField.objects.all()) \
               + list(DocumentType.objects.all()) \
               + list(DocumentFieldDetector.objects.all()) \
               + list(DocumentTypeField.objects.all())

    def get(self, request, *args, **kwargs):
        """
        Dump all document types, fields and field detectors to json.

        """
        data = self.get_full_dump()
        return HttpResponse(core_serializers.serialize("json", data),
                            content_type='Application/json')

    def put(self, request, *args, **kwargs):
        data = request.data
        buf = io.StringIO()

        try:

            with NamedTemporaryFile(mode='w+', suffix='.json') as f:
                json.dump(data, f)
                f.seek(0)
                call_command('loaddata', f.name, app_label='document', stdout=buf,
                             interactive=False)
                buf.seek(0)
            return HttpResponse(content=core_serializers.serialize("json", self.get_full_dump()),
                                content_type='Application/json',
                                status=200)
        except:
            log = buf.read()
            tb = traceback.format_exc()
            data = {
                'log': log,
                'exception': tb
            }
            return HttpResponse(content=json.dumps(data),
                                content_type='Application/json',
                                status=400)


main_router = routers.DefaultRouter()
main_router.register(r'documents', DocumentViewSet, 'document')
main_router.register(r'document-fields', DocumentFieldViewSet, 'document-field')

main_router.register(r'document-field-values', DocumentFieldValueViewSet, 'document-field-value')
main_router.register(r'document-field-values-history', DocumentFieldValueHistoryViewSet,
                     'document-field-values-history')

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
document_via_type_router.register(r'documents', DocumentWithFieldsViewSet, 'documents')

# route documents via project
project_router = routers.SimpleRouter()
project_router.register(r'project', project_api_module.ProjectViewSet, 'project')
document_via_project_router = nested_routers.NestedSimpleRouter(
    project_router, r'project', lookup='project', trailing_slash=True)
document_via_project_router.register(r'documents', DocumentWithFieldsViewSet, 'documents')

api_routers = [main_router, document_type_router,
               document_via_type_router, document_via_project_router]

urlpatterns = [
    url(r'document-sentiment-chart/$', DocumentSentimentChartAPIView.as_view(),
        name='document-sentiment-chart'),

    url(r'^typeahead/document/(?P<field_name>[a-z_]+)/$', TypeaheadDocument.as_view(),
        name='typeahead-document'),
    url(r'^typeahead/document-property/(?P<field_name>[a-z_]+)/$',
        TypeaheadDocumentProperty.as_view(),
        name='typeahead-document-property'),
    url(r'^typeahead/text-unit-tag/(?P<field_name>[a-z_]+)/$', TypeaheadTextUnitTag.as_view(),
        name='typeahead-text-unit-tag'),

    url(r'stats/$', StatsAPIView.as_view(),
        name='stats'),
    url(r'config-dump', DumpDocumentTypeConfigView.as_view(), name='dump-config'),
]
