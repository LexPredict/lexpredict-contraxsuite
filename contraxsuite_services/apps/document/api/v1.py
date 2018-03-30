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

import io
import json
import traceback
from tempfile import NamedTemporaryFile
# Standard imports
from typing import Set

import numpy as np
import pandas as pd
# Django imports
from django.conf import settings
from django.conf.urls import url
from django.core import serializers as core_serializers
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponse
# Third-party imports
from elasticsearch import Elasticsearch
from rest_framework import serializers, routers, viewsets, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_nested import routers as nested_routers

# Project imports
from apps.analyze.models import *
from apps.common.mixins import (
    SimpleRelationSerializer, JqMixin, TypeaheadAPIView)
from apps.common.utils import get_api_module
from apps.document.field_types import FIELD_TYPES_REGISTRY
from apps.document.models import (
    DocumentField, DocumentType, DocumentFieldValue, DocumentFieldDetector,
    DocumentProperty, DocumentNote, DocumentTag, DocumentRelation,
    TextUnitProperty, TextUnitNote, TextUnitTag)
from apps.document.tasks import TrainDocumentFieldDetectorModel
from apps.extract.models import *
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.8/LICENSE"
__version__ = "1.0.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# --------------------------------------------------------
# Document Views
# --------------------------------------------------------

class DocumentSerializer(SimpleRelationSerializer):
    properties = serializers.IntegerField(
        source='documentproperty_set.distinct.count',
        read_only=True)
    relations = serializers.SerializerMethodField()
    text_units = serializers.SerializerMethodField()

    # field_values = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['pk', 'name', 'document_type',
                  'description', 'title',
                  'properties', 'relations', 'text_units']

    def get_relations(self, obj):
        return obj.document_a_set.distinct().count() + obj.document_b_set.distinct().count()

    def get_text_units(self, obj):
        return obj.paragraphs + obj.sentences


class DocumentViewSet(JqMixin, viewsets.ReadOnlyModelViewSet):
    """
    list:
        Document List\n
        GET params:
          - description: str
          - description_contains: str
          - name: str
          - name_contains: str
          - title: str
          - document_type: str
          - source_type: str
          - type_id: int
          - party_id: int\n
        GET params for jqwidgets grid query (sample, see jqWidgets documentation):
          - languageoperator:and
          - filtervalue0:en
          - filtercondition0:CONTAINS
          - filteroperator0:0
          - filterdatafield0:language
          - filterGroups[0][field]:language
          - filterGroups[0][filters][0][label]:en
          - filterGroups[0][filters][0][value]:en
          - filterGroups[0][filters][0][condition]:CONTAINS
          - filterGroups[0][filters][0][operator]:and
          - filterGroups[0][filters][0][field]:language
          - filterGroups[0][filters][0][type]:stringfilter
          - filterscount:1
          - groupscount:0
          - sortdatafield:text
          - sortorder:asc
          - pagenum:0
          - pagesize:10
          - recordstartindex:0
          - recordendindex:10
          - enable_pagination:true
    retrieve: Document Detail
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        party_id = self.request.GET.get("party_id")
        if party_id:
            qs = qs.filter(textunit__partyusage__party__pk=party_id)

        return qs


class DocumentWithFieldsListAPI(viewsets.ViewSet):
    def list(self, request, document_type_pk):
        document_type = DocumentType.objects.get(pk=document_type_pk)

        search_fields_by_uid = dict()

        calculated_search_fields = set()
        non_calculated_search_field_ids = set()
        depends_on_field_ids = set()
        depends_on_fields = set()

        for f in document_type.search_fields.all():
            search_fields_by_uid[str(f.uid)] = f
            if f.is_calculated():
                calculated_search_fields.add(f)
                for df in f.depends_on_fields.all():
                    depends_on_field_ids.add(df.uid)
                    depends_on_fields.add(df)
            else:
                non_calculated_search_field_ids.add(f.uid)

        documents_by_id = {}

        document_query = Document.objects \
            .filter(document_type_id=document_type_pk)

        for pk, name, description, title in document_query \
                .values_list('id', 'name', 'description', 'title'):
            doc_dict = {
                'pk': pk,
                'document_type': document_type_pk,
                'name': name,
                'description': description,
                'title': title,
                'field_values': {}
            }
            documents_by_id[pk] = doc_dict

        field_values_query = DocumentFieldValue.objects \
            .filter(document__document_type_id=document_type_pk) \
            .filter(field_id__in=non_calculated_search_field_ids.union(depends_on_field_ids)) \
            .filter(value__isnull=False)

        for document_id, field_id, value in field_values_query \
                .values_list('document__id', 'field_id', 'value'):
            field_id = str(field_id)
            field = search_fields_by_uid.get(field_id)

            if not field:
                continue

            field_type = FIELD_TYPES_REGISTRY[field.type]

            doc = documents_by_id.get(document_id)
            if not doc:
                continue

            fields = doc['field_values']

            if field_type.multi_value:
                values = fields.get(field_id)
                if values is None:
                    fields[field_id] = [value]
                elif value not in values:
                    values.append(value)
            else:
                fields[field_id] = value

        for doc_dict in documents_by_id.values():
            field_values = doc_dict['field_values']
            depends_on_field_to_value = {f: field_values.get(str(f.uid)) for f in depends_on_fields}

            for field in calculated_search_fields:
                field_values[str(field.uid)] = field.calculate(depends_on_field_to_value)

            doc_dict['field_values'] = {str(uid): value for uid, value in field_values.items() if
                                        str(uid) in search_fields_by_uid}

        return JsonResponse(list(documents_by_id.values()), safe=False)

    def retrieve(self, request, pk, document_type_pk):
        doc = Document.objects.get(pk=pk)
        field_value_objects = dict()
        field_values = dict()
        doc_dict = {
            'pk': doc.id,
            'document_type': document_type_pk,
            'name': doc.name,
            'description': doc.description,
            'title': doc.title,
            'field_values': field_values,
            'field_value_objects': field_value_objects,
            'full_text': doc.full_text
        }

        fields_to_values = {}

        for fv in DocumentFieldValue.objects.filter(document=doc):
            serialized_fv = DocumentFieldValueSerializer(fv).data
            field = fv.field
            field_uid = str(field.uid)
            field_type = FIELD_TYPES_REGISTRY[fv.field.type]
            if field_type.multi_value:
                if field_value_objects.get(field_uid) is None:
                    field_value_objects[field_uid] = [serialized_fv]
                    fields_to_values[field] = [serialized_fv.get('value')]
                else:
                    field_value_objects[field_uid].append(serialized_fv)
                    if fv.value not in fields_to_values[field]:
                        fields_to_values[field].append(serialized_fv.get('value'))
            else:
                field_value_objects[field_uid] = serialized_fv
                fields_to_values[field] = serialized_fv.get('value')

        all_fields = list(doc.document_type.fields.all())
        for f in all_fields:
            if f not in fields_to_values:
                fields_to_values[f] = None

        for f in all_fields:
            if f.is_calculated():
                value = f.calculate(fields_to_values)
            else:
                value = fields_to_values.get(f)
            field_values[str(f.uid)] = value

        return JsonResponse(doc_dict)


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


class DocumentPropertyViewSet(JqMixin, viewsets.ModelViewSet):
    """
    list: Document Property List\n
        GET params:
          - document_id: int
          - key: str
          - key_contains: str
          - value: str
          - value_contains: str
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


class DocumentNoteViewSet(JqMixin, viewsets.ModelViewSet):
    """
    list: Document Note List\n
        GET params:
          - document_id: int
          - note: str
          - note_contains: str
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


class DocumentTagViewSet(JqMixin, viewsets.ModelViewSet):
    """
    Document Tag List\n
        GET params:
          - document_id: int
          - tag: str
          - tag_contains: str
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


class TextUnitViewSet(JqMixin, viewsets.ReadOnlyModelViewSet):
    """
    list: Text Unit List\n
        GET params:
          - elastic_search: str
          - text_search: str
          - document_id: int
          - party_id: int
          - text_unit_hash: str
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


class TextUnitTagViewSet(JqMixin, viewsets.ModelViewSet):
    """
    list: Text Unit Tag List\n
        GET params:
          - tag: str
          - tag_contains: str
          - text_unit_id: int
          - user__username: str
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


class TextUnitNoteViewSet(JqMixin, viewsets.ModelViewSet):
    """
    list: Text Unit Note List\n
        GET params:
          - note: str
          - note_contains: str
          - text_unit_id: int
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


class TextUnitPropertyViewSet(JqMixin, viewsets.ModelViewSet):
    """
    list: Text Unit Property List\n
        GET params:
          - text_unit_id: int
          - key: str
          - key_contains: str
          - value: str
          - value_contains: str
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
    class Meta:
        model = DocumentField
        fields = ['uid', 'code', 'title', 'type', 'choices',
                  'modified_by__username', 'modified_date']


class DocumentFieldCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentField
        fields = ['uid', 'code', 'title', 'type', 'choices']


class DocumentFieldViewSet(JqMixin, viewsets.ModelViewSet):
    """
    list: Document Field List\n
        GET params:
          - uid: int
          - code: str
          - title: str
          - type: str
          - choices: str
    retrieve: Retrieve Document Field
    create: Create Document Field
    update: Update Document Field
    partial_update: Partial Update Document Field
    delete: Delete Document Field
    """
    queryset = DocumentField.objects.all()

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


class DocumentTypeViewSet(JqMixin, viewsets.ModelViewSet):
    """
    list: Document Type List\n
        GET params:
          - uid: str
          - code: str
          - title: str
    retrieve: Retrieve Document Type
    create: Create Document Type
    update: Update Document Type
    partial_update: Partial Update Document Type
    delete: Delete Document Type
    """
    queryset = DocumentType.objects.all()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return DocumentTypeCreateSerializer
        return DocumentTypeDetailSerializer


# --------------------------------------------------------
# Document Field Value Views
# --------------------------------------------------------

def _trigger_retraining(document_type_uid, field_uid):
    if settings.FIELDS_RETRAIN_MODEL_ON_ANNOTATIONS_CHANGE:
        TrainDocumentFieldDetectorModel.train_model_for_field.apply_async(
            args=(document_type_uid, field_uid, None, None, True))


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


class DocumentFieldValueViewSet(JqMixin, viewsets.ModelViewSet):
    """
    list: Document Field Value List\n
        GET params:
          - document_type_code: str
          - field_code: str
          - value: str
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


class DocumentFieldValueHistoryViewSet(JqMixin, viewsets.ModelViewSet):
    """
    list: Document Field Value History List
        GET params:
            - document_id: int
            - id: int (DocumentFieldValue.id)
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
        project_api_module = get_api_module('project')
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
               + list(DocumentFieldDetector.objects.all())

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


class DocumentWithFieldsSerializer(SimpleRelationSerializer):
    field_values = serializers.SerializerMethodField()
    document_type = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['pk', 'name', 'description', 'title', 'full_text', 'document_type',
                  'field_values']

    def get_document_type(self, obj):
        uuid = obj.get('document_type')
        return str(uuid) if uuid else None

    def _build_field_value_dict(self, field_values: Set[DocumentFieldValue]):
        if not field_values:
            return None
        res = dict()

        for field_value in field_values:
            value = field_value.value
            field_id = field_value.field_id
            existing = res.get(field_id)
            if not existing:
                res[field_id] = value
            elif type(existing) is list:
                if value not in existing:
                    existing.append(value)
            elif existing != value:
                res[field_id] = [existing, value]
        return res

    def get_field_values(self, obj):
        field_value_objects = obj.get('documentfieldvalue_set')
        return self._build_field_value_dict(field_value_objects)


class DocumentWithFieldsViewSet(JqMixin, viewsets.ReadOnlyModelViewSet):
    """
    list: Document With FieldVales List\n
    retrieve: Document With FieldVales Detail
    """
    queryset = Document.objects.all()
    serializer_class = DocumentWithFieldsSerializer

    def get_queryset(self):
        document_type = DocumentType.objects.get(pk=self.kwargs.get('document_type_pk'))
        search_fields = document_type.search_fields.all()
        search_field_ids = [f.uid for f in search_fields]
        columns = ('pk', 'name', 'document_type', 'description', 'title', 'documentfieldvalue') \
            if self.action == 'list' \
            else (
            'pk', 'name', 'document_type', 'description', 'title', 'full_text',
            'documentfieldvalue')

        qs = super().get_queryset() \
            .prefetch_related('documentfieldvalue_set') \
            .filter(document_type=document_type) \
            .filter(documentfieldvalue__field_id__in=search_field_ids) \
            .values(*columns)
        return qs


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

document_type_router = routers.SimpleRouter()
document_type_router.register(r'document-types', DocumentTypeViewSet, 'document-types')

document_router = nested_routers.NestedSimpleRouter(document_type_router, r'document-types',
                                                    lookup='document_type', trailing_slash=True)
document_router.register(r'documents', DocumentWithFieldsListAPI, 'documents')
document_router.register(r'documents2', DocumentWithFieldsViewSet, 'documents')

api_routers = [main_router, document_type_router, document_router]

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
