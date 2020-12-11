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
from django.urls import reverse
from django.db.models import Count, Q
from django.contrib.auth.mixins import PermissionRequiredMixin

# Project imports
from apps.analyze.models import *
from apps.analyze.forms import *
from apps.analyze.tasks import TrainDoc2VecModel, TrainClassifier, RunClassifier, Cluster, BuildFeatureVectorsTask
from apps.common.contraxsuite_urls import doc_editor_url, project_documents_url
from apps.document.views import SubmitTextUnitTagView
from apps.task.views import BaseAjaxTaskView
import apps.common.mixins

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TextUnitClassificationListView(apps.common.mixins.JqPaginatedListView):
    """TextUnitClassificationListView

    CBV for list of TextUnitClassification records
    """
    model = TextUnitClassification
    json_fields = ['text_unit__document__pk',
                   'text_unit__document__project__name',
                   'text_unit__document__name',
                   'text_unit__document__document_type__title', 'text_unit__document__description',
                   'text_unit__pk', 'text_unit__unit_type', 'text_unit__language',
                   'class_name', 'class_value', 'user__name', 'timestamp']
    document_lookup = 'text_unit__document'
    template_name = 'analyze/text_unit_classification_list.html'

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = self.full_reverse('document:document-detail',
                                            args=[item['text_unit__document__pk']])
            item['detail_url'] = self.full_reverse('document:text-unit-detail', args=[item['text_unit__pk']])
            item['delete_url'] = self.full_reverse('analyze:text-unit-classification-delete',
                                                   args=[item['pk']])
        return data

    def get_queryset(self):
        qs = super().get_queryset()

        qs = qs.filter(
            text_unit__document__project_id__in=list(
                self.request.user.userprojectssavedfilter.projects.values_list('pk', flat=True)))

        class_name = self.request.GET.get("class_name")
        if class_name is not None and len(class_name.strip()) > 0:
            qs = qs.filter(class_name=class_name)

        class_value = self.request.GET.get("class_value")
        if class_value is not None and len(class_value.strip()) > 0:
            qs = qs.filter(class_value=class_value)

        text_unit_id = self.request.GET.get('text_unit_id')
        if text_unit_id:
            qs = qs.filter(text_unit_id=text_unit_id)

        qs = qs.select_related('text_unit', 'text_unit__document', 'user')
        return qs


class TextUnitClassificationDeleteView(apps.common.mixins.CustomDeleteView):
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


class DocumentClassificationListView(apps.common.mixins.JqPaginatedListView):
    """DocumentClassificationListView

    CBV for list of DocumentClassification records
    """
    model = DocumentClassification
    json_fields = ['document_id',
                   'document__project__name',
                   'document__name',
                   'document__document_type__title',
                   'class_name', 'class_value', 'user__name', 'timestamp']
    document_lookup = 'document'
    template_name = 'analyze/document_classification_list.html'

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = self.full_reverse('document:document-detail',
                                            args=[item['document_id']])
            item['detail_url'] = item['url']
            item['delete_url'] = self.full_reverse('analyze:document-classification-delete',
                                                   args=[item['pk']])
        return data

    def get_queryset(self):
        qs = super().get_queryset()

        qs = qs.filter(
            document__project_id__in=list(
                self.request.user.userprojectssavedfilter.projects.values_list('pk', flat=True)))

        class_name = self.request.GET.get("class_name")
        if class_name is not None and len(class_name.strip()) > 0:
            qs = qs.filter(class_name=class_name)

        class_value = self.request.GET.get("class_value")
        if class_value is not None and len(class_value.strip()) > 0:
            qs = qs.filter(class_value=class_value)

        document_id = self.request.GET.get('document_id')
        if document_id:
            qs = qs.filter(document_id=document_id)

        qs = qs.select_related('document', 'document__document_type', 'document__project', 'user') \
            .only(*self.json_fields)
        return qs


class DocumentClassificationDeleteView(apps.common.mixins.CustomDeleteView):
    """DocumentClassificationDeleteView

    CBV for deletion of DocumentClassification records
    """
    model = DocumentClassification

    def get_success_url(self):
        return reverse('analyze:document-classification-list')

    # TODO: Mainline granular deletion permissions.
    def has_permission(self):
        document = self.get_object().document
        return self.request.user.can_view_document(document)


class TextUnitClassifierListView(apps.common.mixins.JqPaginatedListView):
    """TextUnitClassifierListView

    CBV for list of TextUnitClassifier records
    """
    model = TextUnitClassifier
    json_fields = ['name', 'version', 'class_name', 'is_active']
    annotate = {'suggestions': Count('textunitclassifiersuggestion')}
    template_name = 'analyze/text_unit_classifier_list.html'

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['suggestions_url'] = '{}?class_name={}'.format(
                self.full_reverse('analyze:text-unit-classifier-suggestion-list'), item['class_name'])
            item['delete_url'] = self.full_reverse('analyze:text-unit-classifier-delete', args=[item['pk']])
        return data


class TextUnitClassifierDeleteView(apps.common.mixins.CustomDeleteView):
    """
    TextUnitClassifierListView
    CBV for deletion of TextUnitClassifier records
    """
    model = TextUnitClassifier

    # TODO: Mainline granular deletion permissions.
    # TODO: Mainline delete or de-activate for audit trail
    def has_permission(self):
        return self.request.user.has_perm('analyze.delete_textunitclassifier')

    def get_success_url(self):
        return reverse('analyze:text-unit-classifier-list')


class DocumentClassifierListView(apps.common.mixins.JqPaginatedListView):
    """DocumentClassifierListView

    CBV for list of DocumentClassifier records
    """
    model = DocumentClassifier
    json_fields = ['name', 'version', 'class_name', 'is_active']
    annotate = {'suggestions': Count('documentclassifiersuggestion')}
    template_name = 'analyze/document_classifier_list.html'

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['suggestions_url'] = '{}?class_name={}'.format(
                self.full_reverse('analyze:document-classifier-suggestion-list'), item['class_name'])
            item['delete_url'] = self.full_reverse('analyze:document-classifier-delete', args=[item['pk']])
        return data


class DocumentClassifierDeleteView(apps.common.mixins.CustomDeleteView):
    """
    DocumentClassifierListView
    CBV for deletion of DocumentClassifier records
    """
    model = DocumentClassifier

    def has_permission(self):
        return self.request.user.has_perm('analyze.delete_documentclassifier')

    # TODO: Mainline granular deletion permissions.
    # TODO: Mainline delete or de-activate for audit trail
    def get_success_url(self):
        return reverse('analyze:document-classifier-list')


class TextUnitClassifierSuggestionListView(apps.common.mixins.JqPaginatedListView):
    """TextUnitClassifierSuggestionListView

    CBV for list of TextUnitClassifierSuggestion records
    """
    model = TextUnitClassifierSuggestion
    ordering = "-classifier_confidence"
    json_fields = ['text_unit__document__pk',
                   'text_unit__document__project__name',
                   'text_unit__document__name',
                   'text_unit__document__document_type', 'text_unit__document__description',
                   'text_unit__pk',
                   'class_name', 'class_value', 'classifier_run', 'classifier_confidence']
    document_lookup = 'text_unit__document'
    template_name = 'analyze/text_unit_classifier_suggestion_list.html'

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = self.full_reverse('document:document-detail',
                                            args=[item['text_unit__document__pk']])
            item['detail_url'] = self.full_reverse('document:text-unit-detail', args=[item['text_unit__pk']])
            item['delete_url'] = self.full_reverse('analyze:text-unit-classifier-suggestion-delete',
                                                   args=[item['pk']])
        return data

    def get_queryset(self):
        qs = super().get_queryset()

        qs = qs.filter(
            text_unit__document__project_id__in=list(
                self.request.user.userprojectssavedfilter.projects.values_list('pk', flat=True)))

        class_name = self.request.GET.get('class_name')
        if class_name is not None and len(class_name.strip()) > 0:
            qs = qs.filter(class_name=class_name)

        class_value = self.request.GET.get("class_value")
        if class_value is not None and len(class_value.strip()) > 0:
            qs = qs.objects.filter(class_value=class_value)

        return qs


class TextUnitClassifierSuggestionDeleteView(apps.common.mixins.CustomDeleteView):
    """TextUnitClassifierSuggestionDeleteView

    CBV for deletion of TextUnitClassifierSuggestion records
    """
    model = TextUnitClassifierSuggestion

    def get_success_url(self):
        return reverse('analyze:text-unit-classifier-suggestion-list')

    def has_permission(self):
        document = self.get_object().text_unit.document
        return self.request.user.can_view_document(document)


class DocumentClassifierSuggestionListView(apps.common.mixins.JqPaginatedListView):
    """DocumentClassifierSuggestionListView

    CBV for list of DocumentClassifierSuggestion records
    """
    model = DocumentClassifierSuggestion
    ordering = "-classifier_confidence"
    json_fields = ['document_id',
                   'document__project__name',
                   'document__name',
                   'document__document_type__title',
                   'class_name', 'class_value', 'classifier_run', 'classifier_confidence']
    document_lookup = 'document'
    template_name = 'analyze/document_classifier_suggestion_list.html'

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = self.full_reverse('document:document-detail', args=[item['document_id']])
            item['detail_url'] = item['url']
            item['delete_url'] = self.full_reverse('analyze:document-classifier-suggestion-delete',
                                                   args=[item['pk']])
        return data

    def get_queryset(self):
        qs = super().get_queryset()

        qs = qs.filter(
            document__project_id__in=list(
                self.request.user.userprojectssavedfilter.projects.values_list('pk', flat=True)))

        class_name = self.request.GET.get('class_name')
        if class_name is not None and len(class_name.strip()) > 0:
            qs = qs.filter(class_name=class_name)

        class_value = self.request.GET.get("class_value")
        if class_value is not None and len(class_value.strip()) > 0:
            qs = qs.objects.filter(class_value=class_value)

        return qs.select_related('document', 'document__project', 'document__document_type').only(*self.json_fields)


class DocumentClassifierSuggestionDeleteView(apps.common.mixins.CustomDeleteView):
    """DocumentClassifierSuggestionDeleteView

    CBV for deletion of DocumentClassifierSuggestion records
    """
    model = DocumentClassifierSuggestion

    def get_success_url(self):
        return reverse('analyze:document-classifier-suggestion-list')

    def has_permission(self):
        document = self.get_object().document
        return self.request.user.can_view_document(document)


class DocumentClusterListView(PermissionRequiredMixin, apps.common.mixins.JqPaginatedListView):
    """DocumentClusterListView

    CBV for list of DocumentCluster records
    """
    model = DocumentCluster
    template_name = "analyze/document_cluster_list.html"
    document_lookup = 'documents'
    extra_json_fields = ['count']
    permission_required = None

    def has_permission(self):
        if 'document_pk' in self.request.GET:
            document = Document.objects.get(pk=self.request.GET['document_pk'])
            return self.request.user.can_view_document(document)
        return True

    def get_json_data(self, **kwargs):
        data = super().get_json_data(**kwargs)
        for item in data['data']:
            cluster = DocumentCluster.objects.get(pk=item['pk'])
            documents = cluster.documents

            # permission filter
            user_document_ids = self.request.user.user_document_ids
            documents = documents.filter(id__in=user_document_ids)

            documents = documents.values('pk', 'name', 'description', 'project__name', 'document_type__title')
            for document in documents:
                document['url'] = self.full_reverse('document:document-detail', args=[document['pk']]),
            item['documents'] = list(documents)
        return data

    def get_queryset(self):
        qs = super().get_queryset()

        # permission filter
        user_document_ids = self.request.user.user_document_ids
        qs = qs.filter(documents__pk__in=user_document_ids)

        # qs = qs.filter(documents__project_id__in=self.request.user.userprojectssavedfilter.projects.all())

        if 'document_pk' in self.request.GET:
            qs = qs.filter(documents__pk=self.request.GET['document_pk'])

        qs = qs.values("pk", "cluster_id", "name", "self_name",
                       "description", "cluster_by", "using", "created_date") \
            .annotate(count=Count("documents")) \
            .order_by('cluster_by', 'using', 'cluster_id').distinct()
        return qs


class DocumentSimilarityListView(apps.common.mixins.JqPaginatedListView):
    """DocumentSimilarityListView

    CBV for list of DocumentSimilarity records
    """
    model = DocumentSimilarity
    template_name = "analyze/document_similarity_list.html"
    document_lookup = ['document_a', 'document_b']
    json_fields = ['document_a__name', 'document_a__project__name',
                   'document_a__pk', 'document_a__document_type__title',
                   'document_b__name', 'document_b__project__name',
                   'document_b__pk', 'document_b__document_type__title',
                   'similarity',
                   'document_a__project_id',
                   'document_b__project_id',
                   'document_a__document_type__code',
                   'document_b__document_type__code']

    def get_json_data(self, **kwargs):
        data = super().get_json_data()

        for item in data['data']:
            item['document_a__url'] = \
                doc_editor_url(item['document_a__document_type__code'],
                               item['document_a__project_id'], item['document_a__pk'])
            item['document_b__url'] = \
                doc_editor_url(item['document_b__document_type__code'],
                               item['document_b__project_id'], item['document_b__pk'])
            item['project_a__url'] = \
                project_documents_url(item['document_a__document_type__code'],
                                      item['document_a__project_id'])
            item['project_b__url'] = \
                project_documents_url(item['document_b__document_type__code'],
                                      item['document_b__project_id'])
        return data

    def get_queryset(self):
        qs = super().get_queryset()
        # TODO: remove the filter
        project_ids = list(self.request.user.userprojectssavedfilter.projects.values_list('pk', flat=True))
        qs = qs.filter(Q(document_a__project_id__in=project_ids) |
                       Q(document_b__project_id__in=project_ids))

        if "document_pk" in self.request.GET:
            qs = qs.filter(document_a__pk=self.request.GET['document_pk'])
        return qs


class TextUnitSimilarityListView(apps.common.mixins.JqPaginatedListView):
    """TextUnitSimilarityListView

    CBV for list of TextUnitSimilarity records
    """
    model = TextUnitSimilarity
    template_name = "analyze/text_unit_similarity_list.html"
    document_lookup = ['text_unit_a__document', 'text_unit_b__document']
    json_fields = ['similarity', 'text_unit_a_id', 'text_unit_b_id']
    LIMIT_QUERY = 100000

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            unit_a = TextUnit.objects.get(pk=item['text_unit_a_id'])  # type: TextUnit
            unit_b = TextUnit.objects.get(pk=item['text_unit_b_id'])  # type: TextUnit

            item['text_unit_a__pk'] = unit_a.pk
            item['text_unit_b__pk'] = unit_b.pk
            item['text_unit_a__unit_type'] = unit_a.unit_type
            item['text_unit_b__unit_type'] = unit_b.unit_type
            item['text_unit_a__language'] = unit_a.language
            item['text_unit_b__language'] = unit_b.language
            item['text_unit_a__textunittext__text'] = unit_a.text
            item['text_unit_b__textunittext__text'] = unit_b.text

            item['text_unit_a__document__pk'] = unit_a.document_id
            item['text_unit_b__document__pk'] = unit_b.document_id
            item['text_unit_a__document__name'] = unit_a.document.name
            item['text_unit_b__document__name'] = unit_b.document.name

            item['text_unit_a__url'] = self.full_reverse('document:text-unit-detail',
                                                         args=[item['text_unit_a__pk']]),
            item['text_unit_b__url'] = self.full_reverse('document:text-unit-detail',
                                                         args=[item['text_unit_b__pk']]),
            item['text_unit_a_document_url'] = self.full_reverse('document:document-detail',
                                                                 args=[item['text_unit_a__document__pk']]),
            item['text_unit_b_document_url'] = self.full_reverse('document:document-detail',
                                                                 args=[item['text_unit_b__document__pk']]),
        return data

    def get_queryset(self):
        qs = super().get_queryset()
        # TODO: remove the filter
        project_ids = list(self.request.user.userprojectssavedfilter.projects.values_list('pk', flat=True))
        qs = qs.filter(Q(project_a_id__in=project_ids) |
                       Q(project_b_id__in=project_ids))

        if "text_unit_pk" in self.request.GET:
            qs = qs.filter(text_unit_a__pk=self.request.GET['text_unit_pk'])
        qs = qs.select_related('text_unit_a', 'text_unit_a__textunittext',
                               'text_unit_b', 'text_unit_b__textunittext')
        return qs


class PartySimilarityListView(apps.common.mixins.JqPaginatedListView):
    """PartySimilarityListView

    CBV for list of PartySimilarity records
    """
    model = PartySimilarity
    # document_lookup = ['document_a', 'document_b']
    json_fields = ['party_a__name', 'party_a__description',
                   'party_a__pk', 'party_a__type_abbr',
                   'party_b__name', 'party_a__description',
                   'party_b__pk', 'party_b__type_abbr',
                   'similarity']

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['party_a__url'] = self.full_reverse('extract:party-summary',
                                                     args=[item['party_a__pk']]),
            item['party_b__url'] = self.full_reverse('extract:party-summary',
                                                     args=[item['party_b__pk']]),
        return data

    def get_queryset(self):
        qs = super().get_queryset()
        if "party_pk" in self.request.GET:
            qs = qs.filter(party_a__pk=self.request.GET['party_pk'])
        return qs


class TextUnitClusterListView(apps.common.mixins.JqPaginatedListView):
    """PartySimilarityListView

    CBV for list of TextUnitCluster records
    """
    model = TextUnitCluster
    template_name = "analyze/text_unit_cluster_list.html"
    document_lookup = 'text_units__document'
    extra_json_fields = ['count']

    def get_queryset(self):
        qs = super().get_queryset()

        # qs = qs.filter(text_units__document__project_id__in=self.request.user.userprojectssavedfilter.projects.all())

        if "text_unit_pk" in self.request.GET:
            qs = qs.filter(text_units__pk=self.request.GET['text_unit_pk'])

        qs = qs.values("pk", "cluster_id", "name", "self_name",
                       "description", "cluster_by", "using", "created_date") \
            .annotate(count=Count("text_units")) \
            .order_by('cluster_by', 'using', 'cluster_id').distinct()
        return qs


class TypeaheadTextUnitClassName(apps.common.mixins.TypeaheadView):
    model = TextUnitClassification
    search_field = 'class_name'
    document_lookup = 'text_unit__document'


class TypeaheadTextUnitClassValue(TypeaheadTextUnitClassName):
    search_field = 'class_value'


class SubmitTextUnitClassificationView(SubmitTextUnitTagView):

    def get_success_message(self):
        return "Successfully added class name /%s/ with class value /%s/ for %s" % (
            self.request.POST['class_name'],
            self.request.POST['class_value'],
            str(self.tag_owner))

    # TODO: Allow granular update permissions.
    def process(self, request):
        if self.tag_owner is None:
            return self.failure()
        TextUnitClassification.objects.create(
            text_unit=self.tag_owner,
            class_name=request.POST["class_name"],
            class_value=request.POST["class_value"],
            user=request.user,
            timestamp=datetime.datetime.now()
        )
        return self.success()


class TrainDocumentDoc2VecModelView(BaseAjaxTaskView):
    task_class = TrainDoc2VecModel
    module_name = 'apps.analyze.tasks'
    form_class = TrainDocumentDoc2VecTaskForm


class TrainTextUnitDoc2VecModelView(TrainDocumentDoc2VecModelView):
    form_class = TrainTextUnitDoc2VecTaskForm


class BuildFeatureVectorsTaskView(BaseAjaxTaskView):
    task_class = BuildFeatureVectorsTask
    module_name = 'apps.analyze.tasks'
    form_class = BuildFeatureVectorsTaskForm
    html_form_class = 'popup-form build-features-form'


class RunDocumentClassifierView(BaseAjaxTaskView):
    task_class = RunClassifier
    module_name = 'apps.analyze.tasks'
    form_class = RunDocumentClassifierForm


class RunTextUnitClassifierView(BaseAjaxTaskView):
    task_class = RunClassifier
    module_name = 'apps.analyze.tasks'
    form_class = RunTextUnitClassifierForm


class TrainTextUnitClassifierView(BaseAjaxTaskView):
    task_class = TrainClassifier
    module_name = 'apps.analyze.tasks'
    form_class = TrainTextUnitClassifierForm
    html_form_class = 'popup-form classify-form'


class TrainDocumentClassifierView(BaseAjaxTaskView):
    task_class = TrainClassifier
    module_name = 'apps.analyze.tasks'
    form_class = TrainDocumentClassifierForm
    html_form_class = 'popup-form classify-form'


class ClusterView(BaseAjaxTaskView):
    task_class = Cluster
    module_name = 'apps.analyze.tasks'
    form_class = ClusterForm
    html_form_class = 'popup-form cluster-form'

    def get_metadata(self):
        cluster_items = []
        result_links = []
        do_cluster_documents = self.request.POST.get('do_cluster_documents')
        if do_cluster_documents:
            cluster_items.append('documents')
            result_links.append({'name': 'View Document Cluster List',
                                 'link': 'analyze:document-cluster-list'})
        do_cluster_text_units = self.request.POST.get('do_cluster_text_units')
        if do_cluster_text_units:
            cluster_items.append('text units')
            result_links.append({'name': 'View Text Unit Cluster List',
                                 'link': 'analyze:text-unit-cluster-list'})
        return dict(
            description='cluster:{}; by:{}; algorithm:{}; name:{}'.format(
                ', '.join(cluster_items),
                self.request.POST.get('cluster_by'),
                self.request.POST.get('using'),
                self.request.POST.get('name')),
            result_links=result_links)

    def start_task_and_return(self, data):
        if data.get('skip_confirmation'):
            self.start_task(data)
            return self.json_response(self.task_started_message)

        count, count_limit = Cluster.estimate_reaching_limit(data)
        # if we don't have to cluster too many units ...
        if count < count_limit:
            self.start_task(data)
            return self.json_response(self.task_started_message)
        message = 'Processing large amounts of documents may take a long time.'
        return self.json_response({'message': message,
                                   'confirm': True})
