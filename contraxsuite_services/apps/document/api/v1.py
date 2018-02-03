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
from elasticsearch import Elasticsearch
from rest_framework import routers, serializers, viewsets, mixins
from rest_framework.generics import (
    ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView)

# Django imports
from django.conf import settings
from django.conf.urls import include, url
from django.core.urlresolvers import reverse
from django.http import JsonResponse

# Project imports
from apps.document.models import (
    Document, DocumentProperty, DocumentNote, DocumentTag,
    TextUnit, TextUnitProperty, TextUnitNote, TextUnitTag)
from apps.common.mixins import (
    SimpleRelationSerializer, JqListAPIView, TypeaheadAPIView)


# --------------------------------------------------------
# Document Views
# --------------------------------------------------------

class DocumentListSerializer(serializers.ModelSerializer):
    properties = serializers.IntegerField(
        source='documentproperty_set.distinct.count',
        read_only=True)
    relations = serializers.SerializerMethodField()
    text_units = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['pk', 'name', 'document_type', 'description', 'title',
                  'properties', 'relations', 'text_units']

    def get_relations(self, obj):
        return obj.document_a_set.distinct().count() + obj.document_b_set.distinct().count()

    def get_text_units(self, obj):
        return obj.paragraphs + obj.sentences


class DocumentListAPIView(JqListAPIView):
    """
    Document List\n
    GET params:
      - description_search: str
      - name_search: str
      - party_pk: int
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
    """
    queryset = Document.objects.all()
    serializer_class = DocumentListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        description_search = self.request.GET.get("description_search")
        if description_search:
            qs = qs.filter(description__icontains=description_search)
        name_search = self.request.GET.get("name_search")
        if name_search:
            qs = qs.filter(name__icontains=name_search)
        party_pk = self.request.GET.get("party_pk")
        if party_pk:
            qs = qs.filter(textunit__partyusage__party__pk=party_pk)
        return qs


class DocumentDetailSerializer(DocumentListSerializer):
    class Meta(DocumentListSerializer.Meta):
        fields = ['pk', 'name', 'document_type',
                  'description', 'relations']


class DocumentDetailAPIView(RetrieveAPIView):
    """
    Retrieve Document
    """
    queryset = Document.objects.all()
    serializer_class = DocumentDetailSerializer


class DocumentSentimentChartAPIView(ListAPIView):
    """
    Document Sentiment Chart
    """
    def list(self, request, *args, **kwargs):
        data = []
        documents = Document.objects\
            .filter(documentproperty__key='polarity')\
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
    document_url = serializers.SerializerMethodField()
    edit_url = serializers.SerializerMethodField()
    delete_url = serializers.SerializerMethodField()

    class Meta:
        model = DocumentProperty
        fields = ['pk', 'key', 'value',
                  'created_date', 'created_by__username',
                  'modified_date', 'modified_by__username',
                  'document__pk', 'document__name',
                  'document__document_type', 'document__description',
                  'document_url', 'edit_url', 'delete_url']

    def get_document_url(self, obj):
        return reverse('v1:document-detail', args=[obj.document.pk])

    def get_edit_url(self, obj):
        return reverse('v1:document-property-update', args=[obj.pk])

    def get_delete_url(self, obj):
        return reverse('v1:document-property-delete', args=[obj.pk])


class DocumentPropertyListAPIView(JqListAPIView):
    """
    Document Property List\n
    GET params:
      - see jqWidgets' grid GET params for sorting/filtering/paginating queryset
      - document_pk: int,
      - key_search: str,
    """
    queryset = DocumentProperty.objects.all()
    serializer_class = DocumentPropertyDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if "document_pk" in self.request.GET:
            qs = qs.filter(document__pk=self.request.GET['document_pk'])
        key_search = self.request.GET.get('key_search')
        if key_search:
            qs = qs.filter(key__icontains=key_search)
        qs = qs.select_related('document', 'created_by', 'modified_by')
        return qs


class DocumentPropertyCreateSerializer(serializers.ModelSerializer):
    document_id = serializers.PrimaryKeyRelatedField(
        source='document', queryset=Document.objects.all())

    class Meta:
        model = DocumentProperty
        fields = ['pk', 'key', 'value', 'document_id']


class DocumentPropertyCreateAPIView(CreateAPIView):
    """
    Create Document Property
    """
    queryset = DocumentProperty.objects.all()
    serializer_class = DocumentPropertyCreateSerializer


class DocumentPropertyRetrieveAPIView(RetrieveAPIView):
    """
    Retrieve Document Property
    """
    queryset = DocumentProperty.objects.all()
    serializer_class = DocumentPropertyDetailSerializer


class DocumentPropertyUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentProperty
        fields = ['key', 'value']


class DocumentPropertyUpdateAPIView(UpdateAPIView):
    """
    Update Document Property
    """
    queryset = DocumentProperty.objects.all()
    serializer_class = DocumentPropertyUpdateSerializer


class DocumentPropertyDeleteAPIView(DestroyAPIView):
    """
    Delete Document Property
    """
    queryset = DocumentProperty.objects.all()


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


class DocumentNoteListAPIView(JqListAPIView):
    """
    Document Note List\n
    GET params:
      - see jqWidgets' grid GET params for sorting/filtering/paginating queryset
      - document_pk: int,
      - note_search: str,
    """
    queryset = DocumentNote.objects.all()
    serializer_class = DocumentNoteDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        document_pk = self.request.GET.get('document_pk')
        if document_pk:
            qs = qs.filter(document__pk=document_pk)
        note_search = self.request.GET.get('note_search')
        if note_search:
            qs = qs.filter(note__icontains=note_search)
        return qs


class DocumentNoteCreateSerializer(serializers.ModelSerializer):
    document_id = serializers.PrimaryKeyRelatedField(
        source='document', queryset=Document.objects.all())

    class Meta:
        model = DocumentNote
        fields = ['pk', 'note', 'document_id']


class DocumentNoteCreateAPIView(CreateAPIView):
    """
    Create Document Note
    """
    queryset = DocumentNote.objects.all()
    serializer_class = DocumentNoteCreateSerializer


class DocumentNoteRetrieveAPIView(RetrieveAPIView):
    """
    Retrieve Document Note
    """
    queryset = DocumentNote.objects.all()
    serializer_class = DocumentNoteDetailSerializer


class DocumentNoteUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentNote
        fields = ['note']


class DocumentNoteUpdateAPIView(UpdateAPIView):
    """
    Update Document Note
    """
    queryset = DocumentNote.objects.all()
    serializer_class = DocumentNoteUpdateSerializer


class DocumentNoteDeleteAPIView(DestroyAPIView):
    """
    Delete Document Note
    """
    queryset = DocumentNote.objects.all()


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


class DocumentTagListAPIView(JqListAPIView):
    """
    Document Tag List\n
    GET params:
      - see jqWidgets' grid GET params for sorting/filtering/paginating queryset
      - document_pk: int
      - tag_search: str
    """
    queryset = DocumentTag.objects.all()
    serializer_class = DocumentTagDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        document_pk = self.request.GET.get('document_pk')
        if document_pk:
            qs = qs.filter(document__pk=document_pk)
        tag_search = self.request.GET.get('tag_search')
        if tag_search:
            qs = qs.filter(tag__icontains=tag_search)
        return qs


class DocumentTagCreateSerializer(serializers.ModelSerializer):
    document_id = serializers.PrimaryKeyRelatedField(
        source='document', queryset=Document.objects.all())

    class Meta:
        model = DocumentTag
        fields = ['pk', 'tag', 'document_id']


class DocumentTagCreateAPIView(CreateAPIView):
    """
    Create Document Tag
    """
    queryset = DocumentTag.objects.all()
    serializer_class = DocumentTagCreateSerializer


class DocumentTagRetrieveAPIView(RetrieveAPIView):
    """
    Retrieve Document Tag
    """
    queryset = DocumentTag.objects.all()
    serializer_class = DocumentTagDetailSerializer


class DocumentTagUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentTag
        fields = ['tag']


class DocumentTagUpdateAPIView(UpdateAPIView):
    """
    Update Document Tag
    """
    queryset = DocumentTag.objects.all()
    serializer_class = DocumentTagUpdateSerializer


class DocumentTagDeleteAPIView(DestroyAPIView):
    """
    Delete Document Tag
    """
    queryset = DocumentTag.objects.all()


# --------------------------------------------------------
# TextUnit Views
# --------------------------------------------------------

class TextUnitListSerializer(SimpleRelationSerializer):
    document_url = serializers.SerializerMethodField()
    detail_url = serializers.SerializerMethodField()

    class Meta:
        model = TextUnit
        fields = ['pk', 'unit_type', 'language', 'text', 'text_hash',
                  'document__pk', 'document__name',
                  'document__document_type', 'document__description',
                  'document_url', 'detail_url']

    def get_document_url(self, obj):
        return reverse('v1:document-detail', args=[obj.document.pk])

    def get_detail_url(self, obj):
        return reverse('v1:text-unit-detail', args=[obj.pk])


class TextUnitListAPIView(JqListAPIView):
    """
    Text Unit List\n
    GET params:
      - see jqWidgets' grid GET params for sorting/filtering/paginating queryset
      - elastic_search: str
      - text_search: str
      - document_pk: int
      - party_pk: int
      - text_unit_hash: str
    """
    queryset = TextUnit.objects.all()
    serializer_class = TextUnitListSerializer
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
        elif "text_search" in self.request.GET:
            text_search = self.request.GET.get("text_search")
            qs = self.filter(text_search, qs, _or_lookup='text__icontains')

        if "document_pk" in self.request.GET:
            # Document Detail view
            qs = qs.filter(document__pk=self.request.GET['document_pk']).order_by('pk')
        elif "party_pk" in self.request.GET:
            qs = qs.filter(partyusage__party__pk=self.request.GET['party_pk'])
        elif "text_unit_hash" in self.request.GET:
            # Text Unit Detail identical text units tab
            qs = qs.filter(text_hash=self.request.GET['text_unit_hash'])\
                .exclude(pk=self.request.GET['text_unit_pk'])
        else:
            qs = qs.filter(unit_type='paragraph')
        return qs


class TextUnitDetailAPIView(RetrieveAPIView):
    """
    Retrieve Text Unit
    """
    queryset = TextUnit.objects.all()
    serializer_class = TextUnitListSerializer


# --------------------------------------------------------
# Text Unit Tag Views
# --------------------------------------------------------

class TextUnitTagDetailSerializer(SimpleRelationSerializer):
    document_url = serializers.SerializerMethodField()
    text_unit_url = serializers.SerializerMethodField()
    delete_url = serializers.SerializerMethodField()

    class Meta:
        model = TextUnitTag
        fields = ['pk', 'tag', 'timestamp', 'user__username',
                  'text_unit__document__pk',
                  'text_unit__document__name', 'text_unit__document__document_type',
                  'text_unit__document__description', 'text_unit__pk',
                  'text_unit__unit_type', 'text_unit__language',
                  'document_url', 'text_unit_url', 'delete_url']

    def get_document_url(self, obj):
        return reverse('v1:document-detail', args=[obj.text_unit.document.pk])

    def get_text_unit_url(self, obj):
        return reverse('v1:text-unit-detail', args=[obj.text_unit.pk])

    def get_delete_url(self, obj):
        return reverse('v1:text-unit-tag-delete', args=[obj.pk])


class TextUnitTagListAPIView(JqListAPIView):
    """
    Text Unit Tag List\n
    GET params:
      - see jqWidgets' grid GET params for sorting/filtering/paginating queryset
      - tag_search: str
      - text_unit_id: int
    """
    queryset = TextUnitTag.objects.all()
    serializer_class = TextUnitTagDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        tag_search = self.request.GET.get('tag_search')
        if tag_search:
            qs = qs.filter(tag=tag_search)
        text_unit_id = self.request.GET.get('text_unit_id')
        if text_unit_id:
            qs = qs.filter(text_unit__id=text_unit_id)
        qs = qs.select_related('text_unit', 'text_unit__document')
        return qs


class TextUnitTagCreateSerializer(serializers.ModelSerializer):
    text_unit_id = serializers.PrimaryKeyRelatedField(
        source='text_unit', queryset=TextUnit.objects.all())

    class Meta:
        model = TextUnitTag
        fields = ['pk', 'tag', 'text_unit_id']


class TextUnitTagCreateAPIView(CreateAPIView):
    """
    Create Text Unit Tag
    """
    queryset = TextUnitTag.objects.all()
    serializer_class = TextUnitTagCreateSerializer


class TextUnitTagRetrieveAPIView(RetrieveAPIView):
    """
    Retrieve Text Unit Tag
    """
    queryset = TextUnitTag.objects.all()
    serializer_class = TextUnitTagDetailSerializer


class TextUnitTagUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = TextUnitTag
        fields = ['tag']


class TextUnitTagUpdateAPIView(UpdateAPIView):
    """
    Update Text Unit Tag
    """
    queryset = TextUnitTag.objects.all()
    serializer_class = TextUnitTagUpdateSerializer


class TextUnitTagDeleteAPIView(DestroyAPIView):
    """
    Delete Text Unit Tag
    """
    queryset = TextUnitTag.objects.all()


# --------------------------------------------------------
# Text Unit Note Views
# --------------------------------------------------------

class TextUnitNoteDetailSerializer(SimpleRelationSerializer):
    document_url = serializers.SerializerMethodField()
    text_unit_url = serializers.SerializerMethodField()
    delete_url = serializers.SerializerMethodField()
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
                  'document_url', 'text_unit_url', 'delete_url',
                  'username', 'history']

    def get_document_url(self, obj):
        return reverse('v1:document-detail', args=[obj.text_unit.document.pk])

    def get_text_unit_url(self, obj):
        return reverse('v1:text-unit-detail', args=[obj.text_unit.pk])

    def get_delete_url(self, obj):
        return reverse('v1:text-unit-note-delete', args=[obj.pk])

    def get_history(self, obj):
        return obj.history.values(
            'id', 'text_unit_id', 'history_date',
            'history_user__username', 'note')


class TextUnitNoteListAPIView(JqListAPIView):
    """
    Text Unit Note List\n
    GET params:
      - see jqWidgets' grid GET params for sorting/filtering/paginating queryset
      - tag_search: str
      - text_unit_id: int
    """
    queryset = TextUnitNote.objects.all()
    serializer_class = TextUnitNoteDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        note_search = self.request.GET.get('note_search')
        if note_search:
            qs = qs.filter(note=note_search)
        text_unit_id = self.request.GET.get('text_unit_id')
        if text_unit_id:
            qs = qs.filter(text_unit__id=text_unit_id)
        qs = qs.select_related('text_unit', 'text_unit__document')
        return qs


class TextUnitNoteCreateSerializer(serializers.ModelSerializer):
    text_unit_id = serializers.PrimaryKeyRelatedField(
        source='text_unit', queryset=TextUnit.objects.all())

    class Meta:
        model = TextUnitNote
        fields = ['pk', 'note', 'text_unit_id']


class TextUnitNoteCreateAPIView(CreateAPIView):
    """
    Create Text Unit Note
    """
    queryset = TextUnitNote.objects.all()
    serializer_class = TextUnitNoteCreateSerializer


class TextUnitNoteRetrieveAPIView(RetrieveAPIView):
    """
    Retrieve Text Unit Note
    """
    queryset = TextUnitNote.objects.all()
    serializer_class = TextUnitNoteDetailSerializer


class TextUnitNoteUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = TextUnitNote
        fields = ['note']


class TextUnitNoteUpdateAPIView(UpdateAPIView):
    """
    Update Text Unit Note
    """
    queryset = TextUnitNote.objects.all()
    serializer_class = TextUnitNoteUpdateSerializer


class TextUnitNoteDeleteAPIView(DestroyAPIView):
    """
    Delete Text Unit Note
    """
    queryset = TextUnitNote.objects.all()


# --------------------------------------------------------
# Text Unit Property Views
# --------------------------------------------------------

class TextUnitPropertyDetailSerializer(SimpleRelationSerializer):
    document_url = serializers.SerializerMethodField()
    text_unit_url = serializers.SerializerMethodField()
    edit_url = serializers.SerializerMethodField()
    delete_url = serializers.SerializerMethodField()

    class Meta:
        model = TextUnitProperty
        fields = ['pk', 'key', 'value',
                  'created_date', 'created_by__username',
                  'modified_date', 'modified_by__username',
                  'text_unit__document__pk', 'text_unit__document__name',
                  'text_unit__document__document_type', 'text_unit__document__description',
                  'text_unit__unit_type', 'text_unit__language', 'text_unit__pk',
                  'document_url', 'text_unit_url', 'edit_url', 'delete_url']

    def get_document_url(self, obj):
        return reverse('v1:document-detail', args=[obj.text_unit.document.pk])

    def get_text_unit_url(self, obj):
        return reverse('v1:text-unit-detail', args=[obj.text_unit.pk])

    def get_edit_url(self, obj):
        return reverse('v1:text-unit-property-update', args=[obj.pk])

    def get_delete_url(self, obj):
        return reverse('v1:text-unit-property-delete', args=[obj.pk])


class TextUnitPropertyListAPIView(JqListAPIView):
    """
    Text Unit Property List\n
    GET params:
      - see jqWidgets' grid GET params for sorting/filtering/paginating queryset
      - text_unit_pk: int,
      - key_search: str,
    """
    queryset = TextUnitProperty.objects.all()
    serializer_class = TextUnitPropertyDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        text_unit_pk = self.request.GET.get('text_unit_pk')
        if text_unit_pk:
            qs = qs.filter(text_unit__pk=text_unit_pk)
        key_search = self.request.GET.get('key_search')
        if key_search:
            qs = qs.filter(key__icontains=key_search)
        return qs


class TextUnitPropertyCreateSerializer(serializers.ModelSerializer):
    text_unit_id = serializers.PrimaryKeyRelatedField(
        source='text_unit', queryset=TextUnit.objects.all())

    class Meta:
        model = TextUnitProperty
        fields = ['pk', 'key', 'value', 'text_unit_id']


class TextUnitPropertyCreateAPIView(CreateAPIView):
    """
    Create Text Unit Property
    """
    queryset = TextUnitProperty.objects.all()
    serializer_class = TextUnitPropertyCreateSerializer


class TextUnitPropertyRetrieveAPIView(RetrieveAPIView):
    """
    Retrieve Text Unit Property
    """
    queryset = TextUnitProperty.objects.all()
    serializer_class = TextUnitPropertyDetailSerializer


class TextUnitPropertyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextUnitProperty
        fields = ['key', 'value']


class TextUnitPropertyUpdateAPIView(UpdateAPIView):
    """
    Update Text Unit Property
    """
    queryset = TextUnitProperty.objects.all()
    serializer_class = TextUnitPropertyUpdateSerializer


class TextUnitPropertyDeleteAPIView(DestroyAPIView):
    """
    Delete Text Unit Property
    """
    queryset = TextUnitNote.objects.all()


# --------------------------------------------------------
# Typeahead Views for Global Search bar
# --------------------------------------------------------

class TypeaheadDocumentDescription(TypeaheadAPIView):
    """
    Typeahead Document description\n
    GET params:
      - q: str
    """
    model = Document
    search_field = 'description'
    limit_reviewers_qs_by_field = ''


class TypeaheadDocumentName(TypeaheadDocumentDescription):
    """
    Typeahead Document name\n
    GET params:
      - q: str
    """
    search_field = 'name'


class TypeaheadTextUnitTag(TypeaheadAPIView):
    """
    Typeahead Text Unit Tag\n
    GET params:
      - q: str
    """
    model = TextUnitTag
    search_field = 'tag'
    limit_reviewers_qs_by_field = 'text_unit__document'


class TypeaheadDocumentPropertyKey(TypeaheadAPIView):
    """
    Typeahead Text Unit Property key\n
    GET params:
      - q: str
    """
    model = DocumentProperty
    search_field = 'key'
    limit_reviewers_qs_by_field = 'document'


# router = routers.DefaultRouter()
# router.register(r'document/list', DocumentListViewSet, 'document')


urlpatterns = [
    url(r'document/list/$', DocumentListAPIView.as_view(),
        name='document-list'),
    url(r'document/(?P<pk>\d+)/detail/$', DocumentDetailAPIView.as_view(),
        name='document-detail'),
    url(r'document-sentiment-chart/$', DocumentSentimentChartAPIView.as_view(),
        name='document-sentiment-chart'),

    url(r'document-tag/list/$', DocumentTagListAPIView.as_view(),
        name='document-tag-list'),
    url(r'document-tag/create/$', DocumentTagCreateAPIView.as_view(),
        name='document-tag-create'),
    url(r'document-tag/(?P<pk>\d+)/detail/$', DocumentTagRetrieveAPIView.as_view(),
        name='document-tag-detail'),
    url(r'document-tag/(?P<pk>\d+)/update/$', DocumentTagUpdateAPIView.as_view(),
        name='document-tag-update'),
    url(r'document-tag/(?P<pk>\d+)/delete/$', DocumentTagDeleteAPIView.as_view(),
        name='document-tag-delete'),

    url(r'document-property/list/$', DocumentPropertyListAPIView.as_view(),
        name='document-property-list'),
    url(r'document-property/create/$', DocumentPropertyCreateAPIView.as_view(),
        name='document-property-create'),
    url(r'document-property/(?P<pk>\d+)/detail/$', DocumentPropertyRetrieveAPIView.as_view(),
        name='document-property-detail'),
    url(r'document-property/(?P<pk>\d+)/update/$', DocumentPropertyUpdateAPIView.as_view(),
        name='document-property-update'),
    url(r'document-property/(?P<pk>\d+)/delete/$', DocumentPropertyDeleteAPIView.as_view(),
        name='document-property-delete'),

    url(r'document-note/list/$', DocumentNoteListAPIView.as_view(),
        name='document-note-list'),
    url(r'document-note/create/$', DocumentNoteCreateAPIView.as_view(),
        name='document-note-create'),
    url(r'document-note/(?P<pk>\d+)/detail/$', DocumentNoteRetrieveAPIView.as_view(),
        name='document-note-detail'),
    url(r'document-note/(?P<pk>\d+)/update/$', DocumentNoteUpdateAPIView.as_view(),
        name='document-note-update'),
    url(r'document-note/(?P<pk>\d+)/delete/$', DocumentNoteDeleteAPIView.as_view(),
        name='document-note-delete'),

    url(r'text-unit/list/$', TextUnitListAPIView.as_view(),
        name='text-unit-list'),
    url(r'text-unit/(?P<pk>\d+)/detail/$', TextUnitDetailAPIView.as_view(),
        name='text-unit-detail'),

    url(r'text-unit-tag/list/$', TextUnitTagListAPIView.as_view(),
        name='text-unit-tag-list'),
    url(r'text-unit-tag/create/$', TextUnitTagCreateAPIView.as_view(),
        name='text-unit-tag-create'),
    url(r'text-unit-tag/(?P<pk>\d+)/detail/$', TextUnitTagRetrieveAPIView.as_view(),
        name='text-unit-tag-detail'),
    url(r'text-unit-tag/(?P<pk>\d+)/update/$', TextUnitTagUpdateAPIView.as_view(),
        name='text-unit-tag-update'),
    url(r'text-unit-tag/(?P<pk>\d+)/delete/$', TextUnitTagDeleteAPIView.as_view(),
        name='text-unit-tag-delete'),

    url(r'text-unit-note/list/$', TextUnitNoteListAPIView.as_view(),
        name='text-unit-note-list'),
    url(r'text-unit-note/create/$', TextUnitNoteCreateAPIView.as_view(),
        name='text-unit-note-create'),
    url(r'text-unit-note/(?P<pk>\d+)/detail/$', TextUnitNoteRetrieveAPIView.as_view(),
        name='text-unit-note-detail'),
    url(r'text-unit-note/(?P<pk>\d+)/update/$', TextUnitNoteUpdateAPIView.as_view(),
        name='text-unit-note-update'),
    url(r'text-unit-note/(?P<pk>\d+)/delete/$', TextUnitNoteDeleteAPIView.as_view(),
        name='text-unit-note-delete'),

    url(r'text-unit-property/list/$', TextUnitPropertyListAPIView.as_view(),
        name='text-unit-property-list'),
    url(r'text-unit-property/create/$', TextUnitPropertyCreateAPIView.as_view(),
        name='text-unit-property-create'),
    url(r'text-unit-property/(?P<pk>\d+)/detail/$', TextUnitPropertyRetrieveAPIView.as_view(),
        name='text-unit-property-detail'),
    url(r'text-unit-property/(?P<pk>\d+)/update/$', TextUnitPropertyUpdateAPIView.as_view(),
        name='text-unit-property-update'),
    url(r'text-unit-property/(?P<pk>\d+)/delete/$', TextUnitPropertyDeleteAPIView.as_view(),
        name='text-unit-property-delete'),

    url(r'^complete/document/description/$', TypeaheadDocumentDescription.as_view(),
        name='document-description-complete'),
    url(r'^complete/document/name/$', TypeaheadDocumentName.as_view(),
        name='document-name-complete'),
    url(r'^complete/document-property/key/$', TypeaheadDocumentPropertyKey.as_view(),
        name='document-property-key-complete'),
    url(r'^complete/text-unit-tag/tag/$', TypeaheadTextUnitTag.as_view(),
        name='text-unit-tag-complete'),
]
