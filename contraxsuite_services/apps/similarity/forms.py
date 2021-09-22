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

from scipy.spatial.distance import _METRICS

from django import forms
from django.utils.translation import ugettext_lazy as _

from apps.analyze.ml.features import DocumentFeatures
from apps.common.forms import checkbox_field
from apps.common.widgets import LTRRadioField, CustomLabelModelChoiceField
from apps.document.field_types import LinkedDocumentsField
from apps.document.models import DocumentField
from apps.project.models import Project

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class SimilarityForm(forms.Form):
    header = 'Identify similar Documents and/or Text Units.'
    run_name = forms.CharField(
        max_length=100,
        required=False)
    search_similar_documents = checkbox_field(
        "Identify similar Documents.",
        input_class='min-one-of',
        initial=True)
    search_similar_text_units = checkbox_field(
        "Identify similar Text Units.",
        input_class='min-one-of')
    similarity_threshold = forms.IntegerField(
        min_value=50,
        max_value=100,
        initial=75,
        required=True,
        help_text=_("Min. Similarity Value 50-100%")
    )
    project = CustomLabelModelChoiceField(
        queryset=Project.objects.order_by('-pk'),
        widget=forms.widgets.Select(attrs={'class': 'chosen'}),
        required=False,
        label='Restrict to project',
        custom_formatter=lambda p: f'#{p.pk} {p.name}, {p.document_set.count()} documents')
    use_idf = checkbox_field("Use TF-IDF to normalize data")
    delete = checkbox_field("Delete existing Similarity objects.", initial=True)


class DocumentSimilarityByFeaturesForm(forms.Form):
    header = 'Identify similar Documents by extracted features.'

    run_name = forms.CharField(
        max_length=100,
        required=False)
    similarity_threshold = forms.IntegerField(
        min_value=50,
        max_value=100,
        initial=75,
        required=True,
        help_text=_("Min. Similarity Value 50-100%")
    )
    # project field needed here to populate schema without hardcoded choices, redefined in _init_
    project = forms.IntegerField(required=True)

    feature_source = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'class': 'chosen'}),
        choices=[(i, i) for i in DocumentFeatures.source_fields],
        initial='term',
        required=True,
        help_text='Cluster by terms, parties or other fields.')
    distance_type = forms.ChoiceField(
        choices=[(i, i) for i in _METRICS],
        initial='cosine',
        required=False)
    item_id = forms.IntegerField(label='Document ID', required=False,
                                 help_text='Optional. Search similar for one concrete document')
    create_reverse_relations = checkbox_field('Create reverse relations, i.e. B-A similarities.')
    use_tfidf = checkbox_field('Use TF-IDF to normalize data.')
    delete = checkbox_field('Delete existing Similarity objects.', initial=True)

    class Meta:
        # BaseAjaxTaskView uses it to reorder fields in html form
        fields = ['run_name', 'project', 'feature_source', 'distance_type',
                  'similarity_threshold', 'item_id',
                  'create_reverse_relations', 'use_tfidf', 'delete']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        projects = Project.objects.order_by('-pk').values_list('pk', 'name')
        self.fields['project'] = forms.ChoiceField(
            choices=[(pk, f'#{pk} {name}') for pk, name in projects],
            widget=forms.widgets.Select(attrs={'class': 'chosen'}),
            required=True,
            help_text='Restrict to project')


class TextUnitSimilarityByFeaturesForm(DocumentSimilarityByFeaturesForm):
    header = 'Identify similar Text Units by extracted features.'
    unit_type = forms.ChoiceField(
        choices=[(None, '---'), ('sentence', 'sentence'), ('paragraph', 'paragraph')],
        initial='sentence',
        required=False)
    item_id = forms.IntegerField(label='Text Unit ID', required=False,
                                 help_text='Optional. Search similar for one concrete text unit.')

    class Meta:
        # BaseAjaxTaskView uses it to reorder fields in html form
        fields = ['run_name', 'project', 'feature_source', 'unit_type', 'distance_type',
                  'similarity_threshold', 'item_id',
                  'create_reverse_relations', 'use_tfidf', 'delete']


class ProjectDocumentsSimilarityByVectorsForm(DocumentSimilarityByFeaturesForm):
    header = 'Identify similar Documents in a Project by pre-calculated vectors.'
    feature_source = forms.CharField(initial='vector', widget=forms.HiddenInput(), required=False)
    # project field needed here to populate schema without hardcoded choices, redefined in _init_
    project = forms.IntegerField(
            label='Project / Transformer',
            required=False,
            help_text='Project with Document Transformer trained model')

    class Meta:
        # BaseAjaxTaskView uses it to reorder fields in html form
        fields = ['run_name', 'project', 'distance_type', 'similarity_threshold',
                  'feature_source', 'item_id',
                  'create_reverse_relations', 'use_tfidf', 'delete']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        projects = Project.objects \
            .filter(document_transformer__isnull=False) \
            .order_by('-pk') \
            .values_list('pk', 'name', 'document_transformer_id')
        self.fields['project'] = forms.ChoiceField(
            label='Project / Transformer',
            choices=[(project_id, f'#{project_id} {name}: transformer #{transformer_id}')
                     for project_id, name, transformer_id in projects],
            widget=forms.widgets.Select(attrs={'class': 'chosen'}),
            required=False,
            help_text='Project with Document Transformer trained model')
        self.fields = {n: f for n, f in self.fields.items() if n in self.Meta.fields}


class ProjectTextUnitsSimilarityByVectorsForm(TextUnitSimilarityByFeaturesForm):
    header = 'Identify similar Text Units in a Project by pre-calculated vectors.'
    # project field needed here to populate schema without hardcoded choices, redefined in _init_
    project = forms.IntegerField(
            label='Project / Transformer',
            required=False,
            help_text='Project with Text Unit Transformer trained model')
    feature_source = forms.CharField(initial='vector', widget=forms.HiddenInput(), required=False)
    document_id = forms.IntegerField(required=False)
    location_start = forms.IntegerField(required=False)
    location_end = forms.IntegerField(required=False)

    class Meta:
        # BaseAjaxTaskView uses it to reorder fields in html form
        fields = ['run_name', 'project', 'unit_type', 'distance_type', 'similarity_threshold',
                  'feature_source', 'item_id', 'document_id', 'location_start', 'location_end',
                  'create_reverse_relations', 'use_tfidf', 'delete']

    field_order = Meta.fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        projects = Project.objects \
            .filter(text_unit_transformer__isnull=False) \
            .order_by('-pk') \
            .values_list('pk', 'name', 'text_unit_transformer_id')
        self.fields['project'] = forms.ChoiceField(
            label='Project / Transformer',
            choices=[(project_id, f'#{project_id} {name}: transformer #{transformer_id}')
                     for project_id, name, transformer_id in projects],
            widget=forms.widgets.Select(attrs={'class': 'chosen'}),
            required=False,
            help_text='Project with Text Unit Transformer trained model')
        self.fields = {n: f for n, f in self.fields.items() if n in self.Meta.fields}


class ChunkSimilarityForm(forms.Form):
    header = 'Identify similar Documents and/or Text Units.'
    run_name = forms.CharField(
        max_length=100,
        required=False)
    search_target = LTRRadioField(
        choices=(('document', 'Identify similar Documents'),
                 ('textunit', 'Identify similar Text Units')),
        initial='document',
        required=True)
    similarity_threshold = forms.IntegerField(
        min_value=50,
        max_value=100,
        initial=75,
        required=True,
        help_text=_("Min. Similarity Value 50-100%"))
    use_idf = checkbox_field("Use TF-IDF to normalize data", initial=True)
    ignore_case = checkbox_field("Ignore case", initial=True)
    delete = checkbox_field("Delete existing Similarity objects.", initial=True)
    project = CustomLabelModelChoiceField(
        queryset=Project.objects.order_by('-pk'),
        widget=forms.widgets.Select(attrs={'class': 'chosen'}),
        required=False,
        label='Restrict to project',
        custom_formatter=lambda p: f'#{p.pk} {p.name}, {p.document_set.count()} documents')
    term_type = LTRRadioField(
        choices=(('CHAR_NGRAMS', 'Compare text by char ngrams'),
                 ('WORDS', 'Compare text by words'),
                 ('WORD_3GRAMS', 'Compare texts by word 3-grams')),
        initial='WORDS',
        required=True)
    ngram_len = forms.IntegerField(
        min_value=3,
        max_value=20,
        initial=6,
        required=True,
        help_text='ngram length when using char ngrams')


class PartySimilarityForm(forms.Form):
    header = 'Identify similar Parties.'
    run_name = forms.CharField(
        max_length=100,
        required=False)
    case_sensitive = checkbox_field('Case Sensitive', initial=True)
    similarity_type = forms.ChoiceField(
        choices=[('token_set_ratio', 'token_set_ratio'),
                 ('token_sort_ratio', 'token_sort_ratio')],
        required=True,
        initial='token_set_ratio')
    similarity_threshold = forms.IntegerField(
        min_value=0,
        max_value=100,
        initial=90,
        required=True,
        help_text=_("Min. Similarity Value 0-100%."))
    delete = checkbox_field("Delete existing PartySimilarity objects.", initial=True)


class PreconfiguredDocumentSimilaritySearchForm(forms.Form):
    header = 'Identify similar Documents'

    field = forms.ModelChoiceField(
        queryset=DocumentField.objects.filter(type=LinkedDocumentsField.type_code),
        widget=forms.widgets.Select(attrs={'class': 'chosen'}),
        required=True)
    project = forms.ModelChoiceField(
        queryset=Project.objects.order_by('-pk'),
        widget=forms.widgets.Select(attrs={'class': 'chosen'}),
        required=False,
        label='Restrict to project')
