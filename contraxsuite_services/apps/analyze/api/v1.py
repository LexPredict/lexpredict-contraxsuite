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
from typing import Set, OrderedDict, Dict, Tuple, List, Any, Optional

from guardian.shortcuts import get_objects_for_user
from rest_framework import serializers, routers, viewsets
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated

# Django imports
from django.conf.urls import url
from django.db.models import F, Count, Q
from django.db.models.functions import Left

# Project imports
from rest_framework.utils.serializer_helpers import ReturnList

import apps.common.mixins
from apps.analyze.models import *
from apps.common.schemas import JqFiltersListViewSchema

# TODO: this produces circular import
# from apps.analyze.views import ExistingClassifierClassifyView, CreateClassifierClassifyView, \
#     ClusterView

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# --------------------------------------------------------
# TextUnitClassification Views
# --------------------------------------------------------
from apps.document.models import DocumentPDFRepresentation
from apps.document.pdf_coordinates.text_coord_map import TextCoordMap


class TextUnitClassificationSerializer(apps.common.mixins.SimpleRelationSerializer):
    class Meta:
        model = TextUnitClassification
        fields = ['pk', 'text_unit__document__pk', 'text_unit__document__name',
                  'text_unit__document__document_type', 'text_unit__document__description',
                  'text_unit__pk', 'text_unit__unit_type', 'text_unit__language',
                  'class_name', 'class_value', 'user__username', 'timestamp']


class TextUnitClassificationCreateSerializer(serializers.ModelSerializer):
    text_unit_id = serializers.PrimaryKeyRelatedField(
        source='text_unit',
        queryset=TextUnit.objects.all())
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = TextUnitClassification
        fields = ['pk', 'class_name', 'class_value', 'text_unit_id', 'user_id']

    def get_user_id(self, obj):
        return self.context['request'].user.pk
    get_user_id.output_field = serializers.IntegerField(allow_null=True)


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
    get_suggestions.output_field = serializers.IntegerField(allow_null=True)


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
    get_documents_count.output_field = serializers.IntegerField(allow_null=True)


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
    get_text_unit_count.output_field = serializers.IntegerField(allow_null=True)

    def get_text_unit_data(self, obj):
        text_units = obj.text_units
        text_units = text_units.values(
            'pk', 'unit_type', 'text', 'language',
            'document__pk', 'document__name',
            'document__description', 'document__document_type')
        return list(text_units)
    get_text_unit_data.output_field = serializers.ListField(child=serializers.DictField())


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
# Similarity Run Views
# --------------------------------------------------------
# TODO: add permissions

class SimilarityRunSerializer(serializers.ModelSerializer):
    items_count = serializers.IntegerField()

    class Meta:
        model = SimilarityRun
        fields = ['id', 'project_id', 'feature_source',
                  'unit_source', 'unit_type', 'unit_id', 'items_count',
                  'created_by', 'created_date']


class SimilarityRunSchema(JqFiltersListViewSchema):
    parameters = [
        {'name': 'unit_source',
         'in': 'query',
         'required': False,
         'description': 'document / text_unit',
         'schema': {'type': 'string'}},
        {'name': 'project_id',
         'in': 'query',
         'required': False,
         'description': 'Project ID',
         'schema': {'type': 'integer'}},
    ]
    response_serializer = SimilarityRunSerializer()


class SimilarityRunPermissions(IsAuthenticated):
    def has_permission(self, request, view):
        # granularly forbid deletion; filter in SimilarityRunPermissionMixin
        if view.action == 'delete':
            if 'project_id' in request.GET:
                project = Project.objects.get(id=request.GET['project_id'])
                return request.user.has_perm('project.change_project', project)
            return request.user.has_perm('project.change_project')
        return True


class SimilarityRunPermissionMixin:
    permission_classes = [SimilarityRunPermissions]

    def get_queryset(self):
        projects = get_objects_for_user(self.request.user, 'project.view_project', Project) \
            .filter(delete_pending=False)
        return SimilarityRun.objects.filter(project__in=projects)


class SimilarityRunViewSet(SimilarityRunPermissionMixin,
                           apps.common.mixins.JqListAPIView,
                           viewsets.ModelViewSet):
    """
    list: list Similarity Run objects
    retrieve: get Similarity Run object
    delete: delete Similarity Run object
    """
    http_method_names = ['get', 'delete']
    queryset = SimilarityRun.objects.all()
    serializer_class = SimilarityRunSerializer
    schema = SimilarityRunSchema()

    def get_queryset(self):
        qs = super().get_queryset()
        if 'unit_source' in self.request.GET:
            qs = qs.filter(unit_source=self.request.GET['unit_source'])
        if 'project_id' in self.request.GET:
            qs = qs.filter(project_id=self.request.GET['project_id'])
        qs = qs.annotate(items_count=Count('documentsimilarity') +
                                     Count('textunitsimilarity') +
                                     Count('partysimilarity'))
        return qs


# --------------------------------------------------------
# DocumentSimilarity Views
# --------------------------------------------------------
# TODO: add permissions

class DocumentSimilaritySerializer(apps.common.mixins.SimpleRelationSerializer):
    run = SimilarityRunSerializer(many=False, read_only=True)

    class Meta:
        model = DocumentSimilarity
        fields = ['document_a__name', 'document_a__pk',
                  'document_b__name', 'document_b__pk',
                  'similarity', 'run']


class DocumentSimilarityListAPIView(apps.common.mixins.JqListAPIView):
    """
    Base Document Similarity List
    """
    queryset = DocumentSimilarity.objects.all()
    serializer_class = DocumentSimilaritySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        run_id = self.request.GET.get('run_id')
        if run_id:
            qs = qs.filter(run_id=run_id)
        document_id = self.request.GET.get('document_id')
        if document_id:
            qs = qs.filter(document_a_id=document_id)
        return qs.select_related('document_a', 'document_b', 'run')


# --------------------------------------------------------
# Project DocumentSimilarity Views
# --------------------------------------------------------

class ProjectDocumentSimilaritySerializer(apps.common.mixins.SimpleRelationSerializer):
    # run = SimilarityRunSerializer(many=False, read_only=True)
    document_a_name = serializers.CharField()
    document_b_name = serializers.CharField()
    document_b_text = serializers.CharField()

    class Meta:
        model = DocumentSimilarity
        fields = ['document_a_name', 'document_a_id',
                  'document_b_name', 'document_b_id', 'document_b_text',
                  'similarity', 'run_id']


class ProjectDocumentSimilarityResponseSerializer(serializers.Serializer):
    data = serializers.ListSerializer(child=ProjectDocumentSimilaritySerializer())
    document_a_id = serializers.IntegerField(required=False, allow_null=True)
    document_a_name = serializers.CharField(required=False, allow_null=True)
    total_records = serializers.IntegerField(required=False)


class SimilarProjectDocumentsSchema(JqFiltersListViewSchema):
    parameters = [
        {'name': 'text_max_length',
         'in': 'query',
         'required': False,
         'description': 'document b text max length, 0 to get all text',
         'schema': {'type': 'integer'}},
        {'name': 'run_id',
         'in': 'query',
         'required': False,
         'description': 'run id or document id required',
         'schema': {'type': 'integer'}},
        {'name': 'document_id',
         'in': 'query',
         'required': False,
         'description': 'run id or document id required',
         'schema': {'type': 'integer'}}
    ]
    response_serializer = ProjectDocumentSimilarityResponseSerializer()


class ProjectDocumentSimilarityListPermissionViewMixin:
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DocumentSimilarity.objects.filter(document_a__in=Document.get_allowed_document_ids(self.request.user.id))


class ProjectDocumentSimilarityListAPIView(ProjectDocumentSimilarityListPermissionViewMixin,
                                           apps.common.mixins.JqListAPIView):
    """
    Project Document Similarity List for ONE document
    Params:
        - run_id: int - run id (either document_id required)
        - document_id: int - document id (either run_id required)
        - text_max_length: int - document b text max length, '0' to get all text
    """
    queryset = DocumentSimilarity.objects.all()
    serializer_class = ProjectDocumentSimilaritySerializer
    schema = SimilarProjectDocumentsSchema()
    complex_value_for_fields = ['similarity']
    text_max_length = 300
    action = '_list'

    def get_queryset(self):
        qs = super().get_queryset().order_by('-similarity', 'document_a_id')
        run_id = self.request.GET.get('run_id')
        document_id = self.request.GET.get('document_id')
        if run_id:
            # choose similar documents inside one run
            qs = qs.filter(run_id=run_id)
        elif document_id:
            # choose similar documents for ONE document inside ONE project
            qs = qs.filter(document_a_id=document_id,
                           document_b__project_id=F('document_a__project_id'))
        else:
            raise APIException('run_id or document_id query parameter required', code=404)

        left = self.request.GET.get('text_max_length')
        document_b_text_ann = F('document_b__documenttext__full_text')
        if left not in ['0']:
            try:
                left = int(left) or self.text_max_length
            except:
                left = self.text_max_length
            document_b_text_ann = Left(document_b_text_ann, left)

        qs = qs.annotate(
            document_a_name=F('document_a__name'),
            document_b_name=F('document_b__name'),
            document_b_text=document_b_text_ann)
        return qs.select_related('document_a', 'document_b', 'document_b__documenttext', 'run')

    def get_extra_data(self, queryset, initial_queryset):
        extra_data = super().get_extra_data(queryset, initial_queryset)
        document_id = self.request.GET.get('document_id')
        extra_data['document_a_id'] = int(document_id) or None
        extra_data['document_a_name'] = Document.objects.get(id=document_id).name if document_id else None
        return extra_data


# --------------------------------------------------------
# TextUnitSimilarity Views
# --------------------------------------------------------
# TODO: add permissions

class TextUnitSimilaritySerializer(apps.common.mixins.SimpleRelationSerializer):
    run = SimilarityRunSerializer(many=False, read_only=True)

    class Meta:
        model = TextUnitSimilarity
        fields = ['text_unit_a_id', 'text_unit_a__unit_type',
                  'text_unit_a__language', 'text_unit_a__text',
                  'document_a_id', 'document_a__name',
                  'text_unit_b_id', 'text_unit_b__unit_type',
                  'text_unit_b__language', 'text_unit_b__text',
                  'document_b_id', 'document_b__name',
                  'similarity', 'run']


class TextUnitSimilarityListAPIView(apps.common.mixins.JqListAPIView):
    """
    Base Text Unit Similarity List
    """
    queryset = TextUnitSimilarity.objects.all()
    serializer_class = TextUnitSimilaritySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        run_id = self.request.GET.get('run_id')
        if run_id:
            qs = qs.filter(run_id=run_id)
        text_unit_id = self.request.GET.get('text_unit_id')
        if text_unit_id:
            qs = qs.filter(text_units_a_id=text_unit_id)
        return qs.select_related('text_unit_a',
                                 'text_unit_b',
                                 'document_a', 'document_b', 'run')


# --------------------------------------------------------
# Project TextUnitSimilarity Views
# --------------------------------------------------------

class ProjectTextUnitSimilaritySerializer(apps.common.mixins.SimpleRelationSerializer):
    # run = SimilarityRunSerializer(many=False, read_only=True)
    document_a_name = serializers.CharField()
    document_b_name = serializers.CharField()
    text_unit_a_text = serializers.CharField()
    text_unit_b_text = serializers.CharField()

    class Meta:
        model = TextUnitSimilarity
        fields = ['document_a_name', 'document_a_id',
                  'text_unit_a_id', 'text_unit_a_text', 'text_unit_a__unit_type',
                  'text_unit_a__location_start', 'text_unit_a__location_end',
                  'document_b_name', 'document_b_id',
                  'text_unit_b_id', 'text_unit_b_text',
                  'text_unit_b__location_start', 'text_unit_b__location_end',
                  'similarity', 'run_id']

    def to_representation(self, instance):
        res = super().to_representation(instance)
        return res


class SimilarProjectTextUnitsRequestSerializer(serializers.Serializer):
    text_max_length = serializers.IntegerField(required=False, help_text='text unit b text max length, 0 to get all text')
    run_id = serializers.IntegerField(required=False, help_text='run id or text unit id required')
    last_run = serializers.BooleanField(required=False, help_text='run id or last_run or text unit id required')
    text_unit_id = serializers.IntegerField(required=False, help_text='run id or text unit id required')
    document_id = serializers.IntegerField(required=False, help_text='document ID')
    location_start = serializers.IntegerField(required=False, help_text='start of chosen text block in a Document')
    location_end = serializers.IntegerField(required=False, help_text='end of chosen text block in a Document')
    selection = serializers.ListField(child=serializers.DictField(), required=False,
                                      help_text='selection coordinates')


class ProjectTextUnitSimilarityResponseSerializer(serializers.Serializer):
    data = serializers.ListSerializer(child=ProjectTextUnitSimilaritySerializer())
    document_a_id = serializers.IntegerField(required=False, allow_null=True)
    selected_text = serializers.CharField(required=False, allow_null=True)
    total_records = serializers.IntegerField(required=False)


class SimilarProjectTextUnitsSchema(JqFiltersListViewSchema):
    response_serializer = ProjectTextUnitSimilaritySerializer()
    request_serializer = SimilarProjectTextUnitsRequestSerializer()

    def get_operation(self, path, method):
        op = super().get_operation(path, method)
        # transform request serializer data in GET query parameters
        if method == 'GET':
            post_body = super().map_serializer(self.request_serializer)
            get_parameters = []
            for name, values in post_body['properties'].items():
                required_fields = post_body.get('required', [])
                query_param = {'name': name,
                               'in': 'query',
                               'required': name in required_fields,
                               'description': values.pop('description', None),
                               'schema': values}
                get_parameters.append(query_param)
            op['parameters'].extend(get_parameters)
        return op


class ProjectTextUnitSimilarityListPermissionViewMixin:
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TextUnitSimilarity.objects.filter(document_a__in=Document.get_allowed_document_ids(self.request.user.id))


class ProjectTextUnitSimilarityListAPIView(ProjectTextUnitSimilarityListPermissionViewMixin,
                                           apps.common.mixins.JqListAPIView):
    """
    Project Text Unit Similarity List for ONE text unit
    Params:
        - run_id: int - run id (either text_unit_id required)
        - text_unit_id: int - text unit id (either run_id required)
        - text_max_length: int - text unit b text max length, '0' to get all text
    """
    queryset = TextUnitSimilarity.objects.all()
    serializer_class = ProjectTextUnitSimilaritySerializer
    schema = SimilarProjectTextUnitsSchema()
    complex_value_for_fields = ['similarity']
    text_max_length = 200
    selected_text = None

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        request_data = self.request.data
        qs = super().get_queryset().order_by('-similarity', 'text_unit_a_id')
        run_id = request_data.get('run_id')
        text_unit_id = request_data.get('text_unit_id')
        last_run = 'last_run' in request_data    # any value
        document_id = request_data.get('document_id')
        location_start = request_data.get('location_start')
        location_end = request_data.get('location_end')
        if 'selection' in request_data:
            # we got location of the annotation as coordinates
            selection = request_data['selection']
            location = DocumentPDFRepresentation.get_text_location_by_coords_for_doc(document_id, selection)
            location_start, location_end = location
            request_data['location_start'] = location_start
            request_data['location_end'] = location_end

        try:
            self.selected_text = Document.objects.get(pk=document_id).text[
                                 location_start:location_end]
        except Document.DoesNotExist:
            self.selected_text = ""

        if run_id:
            # choose ALL similar text units inside ONE run
            qs = qs.filter(run_id=run_id)
        elif text_unit_id:
            # choose similar text units for ONE text unit inside ONE project
            qs = qs.filter(text_unit_a_id=text_unit_id, project_b=F('project_a'))
        elif document_id and location_start is not None and location_end is not None:
            # choose similar text units for {SOME chosen text units by location} inside ONE project
            text_unit_ids = self.get_text_unit_a_ids(request_data)
            qs = qs.filter(text_unit_a_id__in=text_unit_ids, project_b=F('project_a'))
        else:
            raise APIException('"run_id" or "text_unit_id" or'
                               ' ("document_id" and "location_start" and "location_end") or' 
                               ' ("document_id" and "selection")' 
                               ' query parameters required', code=404)

        if last_run and qs.exists():
            last_run_id = qs.order_by('run_id').last().run_id
            qs = qs.filter(run_id=last_run_id)

        # limit text size if needed to speed up api
        left = self.request.GET.get('text_max_length')
        text_unit_a_text_ann = F('text_unit_a__text')
        text_unit_b_text_ann = F('text_unit_b__text')
        if left not in ['0']:
            try:
                left = int(left) or self.text_max_length
            except:
                left = self.text_max_length
            text_unit_b_text_ann = Left(text_unit_b_text_ann, left)

        qs = qs.annotate(
            document_a_name=F('document_a__name'),
            document_b_name=F('document_b__name'),
            text_unit_a_text=text_unit_a_text_ann,
            text_unit_b_text=text_unit_b_text_ann)

        return qs.select_related('document_a', 'text_unit_a',
                                 'document_b', 'text_unit_b',
                                 'run')

    def get_text_unit_a_ids(self, kwargs):
        document_id = kwargs.get('document_id')
        location_start = kwargs.get('location_start')
        location_end = kwargs.get('location_end')
        unit_type = kwargs.get('unit_type', 'sentence')

        # get text unit IDs having document coordinates
        text_unit_qs = TextUnit.objects \
            .filter(document_id=document_id, unit_type=unit_type) \
            .filter(Q(location_start__lte=location_start, location_end__gte=location_start) |
                    Q(location_start__gte=location_start, location_end__lte=location_end) |
                    Q(location_start__lte=location_end, location_end__gte=location_end)) \
            .distinct()
        return list(text_unit_qs.values_list('pk', flat=True))

    def get_extra_data(self, queryset, initial_queryset):
        extra_data = super().get_extra_data(queryset, initial_queryset)
        document_id = self.request.data.get('document_id')
        extra_data['document_id'] = int(document_id) if document_id else None
        extra_data['selected_text'] = self.selected_text
        return extra_data

    def add_extra_list_data(self, request, data: ReturnList):
        document_ids: Set[int] = set()
        item: OrderedDict
        if not request.data.get('need_coordinates'):
            return
        for item in data:
            document_ids.add(item['document_a_id'])
            document_ids.add(item['document_b_id'])
        # get PDF data for all documents
        if not document_ids:
            return
        document_data: Dict[int, Tuple[List[List[float]], List[Dict[str, Any]]]] = {}
        for doc_id in document_ids:
            pdf_data = DocumentPDFRepresentation.objects.filter(document_id=doc_id).first()
            if pdf_data:
                document_data[doc_id] = pdf_data.char_bboxes_list, pdf_data.pages_list
        # add coordinates to each text unit
        for item in data:
            item['selection_a'] = self.get_unit_location_coordinates(
                item['document_a_id'], int(item['text_unit_a__location_start']),
                int(item['text_unit_a__location_end']), document_data)
            item['selection_b'] = self.get_unit_location_coordinates(
                item['document_b_id'], int(item['text_unit_b__location_start']),
                int(item['text_unit_b__location_end']), document_data)

    @classmethod
    def get_unit_location_coordinates(
            cls,
            document_id: int,
            loc_start: int,
            loc_end: int,
            document_data: Dict[int, Tuple[List[List[float]], List[Dict[str, Any]]]]) -> Optional[List[Dict[str, Any]]]:
        if loc_start == loc_end:
            return None
        doc_data = document_data.get(document_id)
        if not doc_data:
            return None
        selections = TextCoordMap.get_line_areas(doc_data[0], doc_data[1], loc_start, loc_end)
        if not selections:
            return None
        return [{'page': s.page, 'area': [
            s.area[0], s.area[1], s.area[2], s.area[3]
        ]} for s in selections]




# --------------------------------------------------------
# PartySimilarity Views
# --------------------------------------------------------

class PartySimilaritySerializer(apps.common.mixins.SimpleRelationSerializer):
    run = SimilarityRunSerializer(many=False, read_only=True)

    class Meta:
        model = PartySimilarity
        fields = ['pk', 'party_a__name', 'party_a__description',
                  'party_a__pk', 'party_a__type_abbr',
                  'party_b__name', 'party_a__description',
                  'party_b__pk', 'party_b__type_abbr',
                  'similarity', 'run']


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
        return qs.select_related('party_a', 'party_b', 'run')


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
    document_lookup = 'text_unit__document'


# --------------------------------------------------------
# MLModel Views
# --------------------------------------------------------

class MLModelSerializer(apps.common.mixins.SimpleRelationSerializer):
    class Meta:
        model = MLModel
        # ['id', 'name', 'version', 'vector_name', 'default', 'is_active']
        fields = '__all__'


class MLModelListAPIView(apps.common.mixins.JqListAPIView):
    """
    MLModel List
    """
    queryset = MLModel.objects.all()
    serializer_class = MLModelSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if 'target_entity' in self.request.GET:
            qs = qs.filter(target_entity=self.request.GET['target_entity'])
        if 'apply_to' in self.request.GET:
            qs = qs.filter(target_entity=self.request.GET['apply_to'])
        return qs


class TransformerSerializer(apps.common.mixins.SimpleRelationSerializer):
    class Meta:
        model = MLModel
        fields = ['id', 'name']


class DocumentTransformerListAPIView(apps.common.mixins.JqListAPIView):
    """
    MLModel List - document transformers only
    """
    queryset = MLModel.document_transformers.all()
    serializer_class = TransformerSerializer


class TextUnitTransformerListAPIView(apps.common.mixins.JqListAPIView):
    """
    MLModel List - text unit transformers only
    """
    queryset = MLModel.textunit_transformers.all()
    serializer_class = TransformerSerializer


router = routers.DefaultRouter()
router.register('text-unit-classifications', TextUnitClassificationViewSet,
                'text-unit-classification')
router.register('text-unit-classifiers', TextUnitClassifierViewSet,
                'text-unit-classifier')
router.register('text-unit-classifier-suggestions', TextUnitClassifierSuggestionViewSet,
                'text-unit-classifier-suggestion')

router.register('document-cluster', DocumentClusterAPIView, 'document-cluster')

router.register('similarity-runs', SimilarityRunViewSet, 'similarity-runs')

urlpatterns = [
    url(r'^text-unit-cluster/list/$', TextUnitClusterListAPIView.as_view(),
        name='text-unit-cluster-list'),

    url(r'^document-similarity/list/$', DocumentSimilarityListAPIView.as_view(),
        name='document-similarity-list'),
    url(r'^project-document-similarity/list/$', ProjectDocumentSimilarityListAPIView.as_view(),
        name='project-document-similarity-list'),

    url(r'^text-unit-similarity/list/$', TextUnitSimilarityListAPIView.as_view(),
        name='text-unit-similarity-list'),
    url(r'^project-text-unit-similarity/list/$', ProjectTextUnitSimilarityListAPIView.as_view(),
        name='project-text-unit-similarity-list'),

    url(r'^party-similarity/list/$', PartySimilarityListAPIView.as_view(),
        name='party-similarity-list'),

    url(r'^ml-model/list/$', MLModelListAPIView.as_view(), name='ml-model-list'),
    url(r'^document-transformer/list/$', DocumentTransformerListAPIView.as_view(), name='document-transformer-list'),
    url(r'^text-unit-transformer/list/$', TextUnitTransformerListAPIView.as_view(), name='text-unit-transformer-list'),

    url(r'^typeahead/text-unit-classification/(?P<field_name>[a-z_]+)/$',
        TypeaheadTextUnitClassification.as_view(),
        name='typeahead-text-unit-classification'),
]
