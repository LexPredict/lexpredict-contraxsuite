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

# Django imports
from django.conf.urls import url

# Project imports
import apps.common.mixins
from apps.analyze.models import *

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.1/LICENSE"
__version__ = "1.2.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# --------------------------------------------------------
# TextUnitClassification Views
# --------------------------------------------------------

class TextUnitClassificationSerializer(apps.common.mixins.SimpleRelationSerializer):
    class Meta:
        model = TextUnitClassification
        fields = ['pk', 'text_unit__document__pk', 'text_unit__document__name',
                  'text_unit__document__document_type', 'text_unit__document__description',
                  'text_unit__pk', 'text_unit__unit_type', 'text_unit__language',
                  'class_name', 'class_value', 'user__username', 'timestamp']


class TextUnitClassificationCreateSerializer(serializers.ModelSerializer):
    text_unit_id = serializers.PrimaryKeyRelatedField(
        source='text_unit', queryset=TextUnit.objects.all())
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = TextUnitClassification
        fields = ['pk', 'class_name', 'class_value', 'text_unit_id', 'user_id']

    def get_user_id(self, obj):
        return self.context['request'].user.pk


class TextUnitClassificationViewSet(apps.common.mixins.JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: Text Unit Classification List
    retrieve: Retrieve Text Unit Classification
    create: Create Text Unit Classification
    update: Update Text Unit Classification
    delete: Delete Text Unit Classification
    """
    queryset = TextUnitClassification.objects.all()
    http_method_names = ['get', 'post', 'delete']

    def get_serializer_class(self):
        if self.action == 'create':
            return TextUnitClassificationCreateSerializer
        return TextUnitClassificationSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('text_unit', 'text_unit__document', 'user')
        return qs


# --------------------------------------------------------
# TextUnitClassifier Views
# --------------------------------------------------------

class TextUnitClassifierSerializer(apps.common.mixins.SimpleRelationSerializer):
    suggestions = serializers.SerializerMethodField()

    class Meta:
        model = TextUnitClassifier
        fields = ['pk', 'name', 'version', 'class_name', 'is_active', 'suggestions']

    def get_suggestions(self, obj):
        return obj.textunitclassifiersuggestion_set.count()


class TextUnitClassifierViewSet(apps.common.mixins.JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: Text Unit Classifier List
    delete: Delete Text Unit Classifier
    """
    queryset = TextUnitClassifier.objects.all()
    serializer_class = TextUnitClassifierSerializer
    http_method_names = ['get', 'delete']


# --------------------------------------------------------
# TextUnitClassifierSuggestion Views
# --------------------------------------------------------

class TextUnitClassifierSuggestionSerializer(TextUnitClassificationSerializer):
    class Meta:
        model = TextUnitClassifierSuggestion
        fields = ['pk', 'text_unit__document__pk', 'text_unit__document__name',
                  'text_unit__document__document_type',
                  'text_unit__document__description',
                  'text_unit__pk', 'class_name', 'class_value',
                  'classifier_run', 'classifier_confidence']


class TextUnitClassifierSuggestionViewSet(apps.common.mixins.JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: Text Unit Classifier Suggestion List
    delete: Delete Text Unit Classifier Suggestion
    """
    queryset = TextUnitClassifierSuggestion.objects.all()
    serializer_class = TextUnitClassifierSuggestionSerializer
    http_method_names = ['get', 'delete']


# --------------------------------------------------------
# DocumentCluster Views
# --------------------------------------------------------


class DocumentSerializer(apps.common.mixins.SimpleRelationSerializer):
    class Meta:
        model = Document
        fields = ['pk', 'name', 'document_type']


class DocumentClusterSerializer(apps.common.mixins.SimpleRelationSerializer):
    documents_count = serializers.SerializerMethodField()
    document_data = DocumentSerializer(
        source='documents', many=True, read_only=True)

    class Meta:
        model = DocumentCluster
        fields = ['pk', 'cluster_id', 'name', 'self_name',
                  'description', 'cluster_by', 'using', 'created_date',
                  'documents_count', 'document_data']

    def get_documents_count(self, obj):
        return obj.documents.count()


class DocumentClusterUpdateSerializer(apps.common.mixins.SimpleRelationSerializer):

    class Meta:
        model = DocumentCluster
        fields = ['pk', 'name']


class DocumentClusterAPIView(apps.common.mixins.JqListAPIView, viewsets.ModelViewSet):
    """
    list: Document Cluster List
    retrieve: Retrieve Document Cluster
    update: Update Document Cluster (name)
    partial_update: Partial Update Document Cluster (name)
    """
    queryset = DocumentCluster.objects.all()
    http_method_names = ['get', 'patch', 'put']

    def get_queryset(self):
        qs = super().get_queryset()
        document_id = self.request.GET.get('document_id')
        if document_id:
            qs = qs.filter(documents_id=document_id)
        return qs.order_by('cluster_by', 'using', 'cluster_id')

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return DocumentClusterUpdateSerializer
        return DocumentClusterSerializer


# --------------------------------------------------------
# TextUnitCluster Views
# --------------------------------------------------------

class TextUnitClusterSerializer(apps.common.mixins.SimpleRelationSerializer):
    text_unit_count = serializers.SerializerMethodField()
    text_unit_data = serializers.SerializerMethodField()

    class Meta:
        model = TextUnitCluster
        fields = ['pk', 'cluster_id', 'name', 'self_name',
                  'description', 'cluster_by', 'using', 'created_date',
                  'text_unit_count', 'text_unit_data']

    def get_text_unit_count(self, obj):
        return obj.text_units.count()

    def get_text_unit_data(self, obj):
        text_units = obj.text_units
        text_units = text_units.values(
            'pk', 'unit_type', 'text', 'language',
            'document__pk', 'document__name',
            'document__description', 'document__document_type')
        return list(text_units)


class TextUnitClusterListAPIView(apps.common.mixins.JqListAPIView):
    """
    Text Unit Cluster List
    """
    queryset = TextUnitCluster.objects.all()
    serializer_class = TextUnitClusterSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        text_unit_id = self.request.GET.get('text_unit_id')
        if text_unit_id:
            qs = qs.filter(text_units_id=text_unit_id)

        return qs.order_by('cluster_by', 'using', 'cluster_id')


# --------------------------------------------------------
# DocumentSimilarity Views
# --------------------------------------------------------

class DocumentSimilaritySerializer(apps.common.mixins.SimpleRelationSerializer):
    class Meta:
        model = DocumentSimilarity
        fields = ['pk', 'document_a__name', 'document_a__description',
                  'document_a__pk', 'document_a__document_type',
                  'document_b__name', 'document_b__description',
                  'document_b__pk', 'document_b__document_type',
                  'similarity']


class DocumentSimilarityListAPIView(apps.common.mixins.JqListAPIView):
    """
    Document Similarity List
    """
    queryset = DocumentSimilarity.objects.all()
    serializer_class = DocumentSimilaritySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        document_id = self.request.GET.get('document_id')
        if document_id:
            qs = qs.filter(document_a_id=document_id)
        return qs


# --------------------------------------------------------
# TextUnitSimilarity Views
# --------------------------------------------------------

class TextUnitSimilaritySerializer(apps.common.mixins.SimpleRelationSerializer):
    class Meta:
        model = TextUnitSimilarity
        fields = ['pk', 'text_unit_a__pk', 'text_unit_a__unit_type',
                  'text_unit_a__language', 'text_unit_a__text',
                  'text_unit_a__document__pk', 'text_unit_a__document__name',
                  'text_unit_b__pk', 'text_unit_b__unit_type',
                  'text_unit_b__language', 'text_unit_b__text',
                  'text_unit_b__document__pk', 'text_unit_b__document__name',
                  'similarity']


class TextUnitSimilarityListAPIView(apps.common.mixins.JqListAPIView):
    """
    Text Unit Similarity List
    """
    queryset = TextUnitSimilarity.objects.all()
    serializer_class = TextUnitSimilaritySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        text_unit_id = self.request.GET.get('text_unit_id')
        if text_unit_id:
            qs = qs.filter(text_units_a_id=text_unit_id)
        return qs


# --------------------------------------------------------
# PartySimilarity Views
# --------------------------------------------------------

class PartySimilaritySerializer(apps.common.mixins.SimpleRelationSerializer):
    class Meta:
        model = PartySimilarity
        fields = ['pk', 'party_a__name', 'party_a__description',
                  'party_a__pk', 'party_a__type_abbr',
                  'party_b__name', 'party_a__description',
                  'party_b__pk', 'party_b__type_abbr',
                  'similarity']


class PartySimilarityListAPIView(apps.common.mixins.JqListAPIView):
    """
    Party Similarity List
    """
    queryset = PartySimilarity.objects.all()
    serializer_class = PartySimilaritySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        party_id = self.request.GET.get('party_id')
        if party_id:
            qs = qs.filter(party_a_id=party_id)
        return qs


# --------------------------------------------------------
# Typeahead Views
# --------------------------------------------------------

class TypeaheadTextUnitClassification(apps.common.mixins.TypeaheadAPIView):
    """
    Typeahead TextUnitClassification\n
        Kwargs: field_name: [class_name, class_value]
        GET params:
          - q: str
    """
    model = TextUnitClassification
    limit_reviewers_qs_by_field = 'text_unit__document'


router = routers.DefaultRouter()
router.register(r'text-unit-classifications', TextUnitClassificationViewSet,
                'text-unit-classification')
router.register(r'text-unit-classifiers', TextUnitClassifierViewSet,
                'text-unit-classifier')
router.register(r'text-unit-classifier-suggestions', TextUnitClassifierSuggestionViewSet,
                'text-unit-classifier-suggestion')
router.register(r'document-cluster', DocumentClusterAPIView, 'document-cluster')

urlpatterns = [
    url(r'^text-unit-cluster/list/$', TextUnitClusterListAPIView.as_view(),
        name='text-unit-cluster-list'),

    url(r'^document-similarity/list/$', DocumentSimilarityListAPIView.as_view(),
        name='document-similarity-list'),
    url(r'^text-unit-similarity/list/$', TextUnitSimilarityListAPIView.as_view(),
        name='text-unit-similarity-list'),
    url(r'^party-similarity/list/$', PartySimilarityListAPIView.as_view(),
        name='party-similarity-list'),

    url(r'^typeahead/text-unit-classification/(?P<field_name>[a-z_]+)/$',
        TypeaheadTextUnitClassification.as_view(),
        name='typeahead-text-unit-classification'),
]