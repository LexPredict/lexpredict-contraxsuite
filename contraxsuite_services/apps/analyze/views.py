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

# Future imports
from __future__ import absolute_import, unicode_literals

# Python imports
import datetime

# Django imports
from django.core.urlresolvers import reverse
from django.db.models import Count

# Project imports
from apps.analyze.models import (
    DocumentCluster, DocumentSimilarity, PartySimilarity,
    TextUnitClassification, TextUnitClassifier, TextUnitClassifierSuggestion,
    TextUnitSimilarity, TextUnitCluster)
from apps.document.views import SubmitTextUnitTagView
from apps.common.mixins import (
    AdminRequiredMixin, CustomDeleteView,
    JqPaginatedListView, TypeaheadView)

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.5/LICENSE"
__version__ = "1.0.7"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TextUnitClassificationListView(JqPaginatedListView):
    """TextUnitClassificationListView

    CBV for list of TextUnitClassification records
    """
    model = TextUnitClassification
    json_fields = ['text_unit__document__pk', 'text_unit__document__name',
                   'text_unit__document__document_type', 'text_unit__document__description',
                   'text_unit__pk', 'text_unit__unit_type', 'text_unit__language',
                   'class_name', 'class_value', 'user__username', 'timestamp']
    limit_reviewers_qs_by_field = 'text_unit__document'

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = reverse('document:document-detail',
                                  args=[item['text_unit__document__pk']])
            item['detail_url'] = reverse('document:text-unit-detail', args=[item['text_unit__pk']])
            item['delete_url'] = reverse('analyze:text-unit-classification-delete',
                                         args=[item['pk']])
        return data

    def get_queryset(self):
        qs = super().get_queryset()

        class_name = self.request.GET.get("class_name")
        if class_name is not None and len(class_name.strip()) > 0:
            qs = qs.filter(class_name=class_name)

        class_value = self.request.GET.get("class_value")
        if class_value is not None and len(class_value.strip()) > 0:
            qs = qs.filter(class_value=class_value)

        text_unit_id = self.request.GET.get('text_unit_id')
        if text_unit_id:
            qs = qs.filter(text_unit__id=text_unit_id)

        qs = qs.select_related('text_unit', 'text_unit__document', 'user')
        return qs


class TextUnitClassificationDeleteView(CustomDeleteView):
    """TextUnitClassificationDeleteView

    CBV for deletion of TextUnitClassification records
    """
    model = TextUnitClassification

    def get_success_url(self):
        return reverse('analyze:text-unit-classification-list')

    # TODO: Mainline granular deletion permissions.
    def has_permission(self):
        document = self.get_object().text_unit.document
        return self.request.user.can_view_document(document)


class TextUnitClassifierListView(JqPaginatedListView):
    """TextUnitClassifierListView

    CBV for list of TextUnitClassifier records
    """
    model = TextUnitClassifier
    json_fields = ['name', 'version', 'class_name', 'is_active']
    annotate = {'suggestions': Count('textunitclassifiersuggestion')}

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['suggestions_url'] = reverse('analyze:text-unit-classifier-suggestion-list') + \
                                      '?class_name=' + item['class_name']
            item['retrain_url'] = '#'
            item['delete_url'] = reverse('analyze:text-unit-classifier-delete',
                                         args=[item['pk']])
        return data


class TextUnitClassifierDeleteView(AdminRequiredMixin, CustomDeleteView):
    """TextUnitClassifierListView

    CBV for deletion of TextUnitClassifier records
    """

    model = TextUnitClassifier

    #TODO: Mainline granular deletion permissions.
    #TODO: Mainline delete or de-activate for audit trail
    def get_success_url(self):
        return reverse('analyze:text-unit-classifier-list')


class TextUnitClassifierSuggestionListView(JqPaginatedListView):
    """TextUnitClassifierSuggestionListView

    CBV for list of TextUnitClassifierSuggestion records
    """
    model = TextUnitClassifierSuggestion
    ordering = "-classifier_confidence"
    json_fields = ['text_unit__document__pk', 'text_unit__document__name',
                   'text_unit__document__document_type', 'text_unit__document__description',
                   'text_unit__pk',
                   'class_name', 'class_value', 'classifier_run', 'classifier_confidence']
    limit_reviewers_qs_by_field = 'text_unit__document'

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = reverse('document:document-detail',
                                  args=[item['text_unit__document__pk']])
            item['detail_url'] = reverse('document:text-unit-detail', args=[item['text_unit__pk']])
            item['delete_url'] = reverse('analyze:text-unit-classifier-suggestion-delete',
                                         args=[item['pk']])
        return data

    def get_queryset(self):
        qs = super().get_queryset()
        class_name = self.request.GET.get('class_name')
        if class_name is not None and len(class_name.strip()) > 0:
            qs = qs.filter(class_name=class_name)

        class_value = self.request.GET.get("class_value")
        if class_value is not None and len(class_value.strip()) > 0:
            qs = qs.objects.filter(class_value=class_value)

        return qs


class TextUnitClassifierSuggestionDeleteView(CustomDeleteView):
    """TextUnitClassifierSuggestionDeleteView

    CBV for deletion of TextUnitClassifierSuggestion records
    """
    model = TextUnitClassifierSuggestion

    def get_success_url(self):
        return reverse('analyze:text-unit-classifier-suggestion-list')

    def has_permission(self):
        document = self.get_object().text_unit.document
        return self.request.user.can_view_document(document)


class DocumentClusterListView(JqPaginatedListView):
    """DocumentClusterListView

    CBV for list of DocumentCluster records
    """
    model = DocumentCluster
    template_name = "analyze/document_cluster_list.html"
    limit_reviewers_qs_by_field = 'documents'

    def get_json_data(self, **kwargs):
        data = list(self.get_queryset())
        for item in data:
            cluster = DocumentCluster.objects.get(pk=item['pk'])
            documents = cluster.documents
            if self.request.user.is_reviewer:
                documents = documents.filter(taskqueue__reviewers=self.request.user)
            documents = documents.values('pk', 'name', 'description', 'document_type')
            for document in documents:
                document['url'] = reverse('document:document-detail', args=[document['pk']]),
            item['documents'] = list(documents)
        return {'data': data, 'total_records': len(data)}

    def get_queryset(self):
        qs = super().get_queryset()

        if "document_pk" in self.request.GET:
            qs = qs.filter(documents__pk=self.request.GET['document_pk'])

        qs = qs.values("pk", "cluster_id", "name", "self_name",
                       "description", "cluster_by", "using", "created_date") \
            .annotate(count=Count("documents")) \
            .order_by('cluster_by', 'using', 'cluster_id')
        return qs


class DocumentSimilarityListView(JqPaginatedListView):
    """DocumentSimilarityListView

    CBV for list of DocumentSimilarity records
    """
    model = DocumentSimilarity
    template_name = "analyze/document_similarity_list.html"
    limit_reviewers_qs_by_field = ['document_a', 'document_b']
    json_fields = ['document_a__name', 'document_a__description',
                   'document_a__pk', 'document_a__document_type',
                   'document_b__name', 'document_b__description',
                   'document_b__pk', 'document_b__document_type',
                   'similarity']

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['document_a__url'] = reverse('document:document-detail',
                                              args=[item['document_a__pk']]),
            item['document_b__url'] = reverse('document:document-detail',
                                              args=[item['document_b__pk']]),
        return data

    def get_queryset(self):
        qs = super().get_queryset()
        if "document_pk" in self.request.GET:
            qs = qs.filter(document_a__pk=self.request.GET['document_pk'])
        return qs


class TextUnitSimilarityListView(JqPaginatedListView):
    """TextUnitSimilarityListView

    CBV for list of TextUnitSimilarity records
    """
    model = TextUnitSimilarity
    template_name = "analyze/text_unit_similarity_list.html"
    limit_reviewers_qs_by_field = ['text_unit_a__document', 'text_unit_b__document']
    json_fields = ['text_unit_a__pk', 'text_unit_a__unit_type',
                   'text_unit_a__language', 'text_unit_a__text',
                   'text_unit_a__document__pk', 'text_unit_a__document__name',
                   'text_unit_b__pk', 'text_unit_b__unit_type',
                   'text_unit_b__language', 'text_unit_b__text',
                   'text_unit_b__document__pk', 'text_unit_b__document__name',
                   'similarity']

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['text_unit_a__url'] = reverse('document:text-unit-detail',
                                               args=[item['text_unit_a__pk']]),
            item['text_unit_b__url'] = reverse('document:text-unit-detail',
                                               args=[item['text_unit_b__pk']]),
            item['text_unit_a_document_url'] = reverse('document:document-detail',
                                                       args=[item['text_unit_a__document__pk']]),
            item['text_unit_b_document_url'] = reverse('document:document-detail',
                                                       args=[item['text_unit_b__document__pk']]),
        return data

    def get_queryset(self):
        qs = super().get_queryset()
        if "text_unit_pk" in self.request.GET:
            qs = qs.filter(text_unit_a__pk=self.request.GET['text_unit_pk'])
        return qs


class PartySimilarityListView(JqPaginatedListView):
    """PartySimilarityListView

    CBV for list of PartySimilarity records
    """
    model = PartySimilarity
    # limit_reviewers_qs_by_field = ['document_a', 'document_b']
    json_fields = ['party_a__name', 'party_a__description',
                   'party_a__pk', 'party_a__type_abbr',
                   'party_b__name', 'party_a__description',
                   'party_b__pk', 'party_b__type_abbr',
                   'similarity']

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['party_a__url'] = reverse('extract:party-summary',
                                           args=[item['party_a__pk']]),
            item['party_b__url'] = reverse('extract:party-summary',
                                           args=[item['party_b__pk']]),
        return data

    def get_queryset(self):
        qs = super().get_queryset()
        if "party_pk" in self.request.GET:
            qs = qs.filter(party_a__pk=self.request.GET['party_pk'])
        return qs


class TextUnitClusterListView(JqPaginatedListView):
    """PartySimilarityListView

    CBV for list of TextUnitCluster records
    """
    model = TextUnitCluster
    template_name = "analyze/text_unit_cluster_list.html"
    limit_reviewers_qs_by_field = 'text_units__document'

    def get_json_data(self, **kwargs):
        data = list(self.get_queryset())
        for item in data:
            cluster = TextUnitCluster.objects.get(pk=item['pk'])
            text_units = cluster.text_units.values(
                'pk', 'unit_type', 'text', 'language',
                'document__pk', 'document__name',
                'document__description', 'document__document_type')
            for text_unit in text_units:
                text_unit['document_url'] = reverse('document:document-detail',
                                                    args=[text_unit['document__pk']]),
                text_unit['text_unit_url'] = reverse('document:text-unit-detail',
                                                     args=[text_unit['pk']])
            item['text_units'] = list(text_units)
        return {'data': data, 'total_records': len(data)}

    def get_queryset(self):
        qs = super().get_queryset()

        if "text_unit_pk" in self.request.GET:
            qs = qs.filter(text_units__pk=self.request.GET['text_unit_pk'])

        qs = qs.values("pk", "cluster_id", "name", "self_name",
                       "description", "cluster_by", "using", "created_date") \
            .annotate(count=Count("text_units")) \
            .order_by('cluster_by', 'using', 'cluster_id')
        return qs


class TypeaheadTextUnitClassName(TypeaheadView):
    model = TextUnitClassification
    search_field = 'class_name'
    limit_reviewers_qs_by_field = 'text_unit__document'


class TypeaheadTextUnitClassValue(TypeaheadTextUnitClassName):
    search_field = 'class_value'


class SubmitTextUnitClassificationView(SubmitTextUnitTagView):

    def get_success_message(self):
        return "Successfully added class name /%s/ with class value /%s/ for %s" % (
            self.request.POST['class_name'],
            self.request.POST['class_value'],
            str(self.owner))

    #TODO: Allow granular update permissions.
    def process(self, request):
        if self.owner is None:
            return self.failure()
        TextUnitClassification.objects.create(
            text_unit=self.owner,
            class_name=request.POST["class_name"],
            class_value=request.POST["class_value"],
            user=request.user,
            timestamp=datetime.datetime.now()
        )
        return self.success()
