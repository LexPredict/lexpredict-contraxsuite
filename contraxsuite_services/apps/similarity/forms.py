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
from apps.common.widgets import LTRRadioField
from apps.document.field_types import LinkedDocumentsField
from apps.document.models import DocumentField
from apps.project.models import Project

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class SimilarityForm(forms.Form):
    header = 'Identify similar Documents and/or Text Units.'
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
    use_idf = checkbox_field("Use TF-IDF to normalize data")
    delete = checkbox_field("Delete existing Similarity objects.", initial=True)
    project = forms.ModelChoiceField(
        queryset=Project.objects.order_by('-pk'),
        widget=forms.widgets.Select(attrs={'class': 'chosen'}),
        required=False,
        label='Restrict to project')


class SimilarityByFeaturesForm(forms.Form):
    header = 'Identify similar Documents or Text Units by extracted features.'
    search_similar_documents = checkbox_field(
        "Identify similar Documents.",
        input_class='max-one-of',
        initial=True)
    search_similar_text_units = checkbox_field(
        "Identify similar Text Units.",
        input_class='max-one-of')
    similarity_threshold = forms.IntegerField(
        min_value=50,
        max_value=100,
        initial=75,
        required=True,
        help_text=_("Min. Similarity Value 50-100%")
    )
    use_tfidf = checkbox_field("Use TF-IDF to normalize data")
    delete = checkbox_field("Delete existing Similarity objects.", initial=True)
    project = forms.ModelChoiceField(
        queryset=Project.objects.order_by('-pk'),
        widget=forms.widgets.Select(attrs={'class': 'chosen'}),
        required=False,
        label='Restrict to project')
    feature_source = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'class': 'chosen'}),
        choices=[(i, i) for i in DocumentFeatures.source_fields],
        initial='term',
        required=True,
        help_text='Cluster by terms, parties or other fields.')
    unit_type = forms.ChoiceField(
        choices=[('sentence', 'sentence'), ('paragraph', 'paragraph')],
        initial='sentence',
        required=True)
    distance_type = forms.ChoiceField(
        choices=[(i, i) for i in _METRICS],
        initial='cosine',
        required=True)


class ChunkSimilarityForm(forms.Form):
    header = 'Identify similar Documents and/or Text Units.'
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
        help_text=_("Min. Similarity Value 50-100%")
    )
    use_idf = checkbox_field("Use TF-IDF to normalize data", initial=True)
    ignore_case = checkbox_field("Ignore case", initial=True)
    delete = checkbox_field("Delete existing Similarity objects.", initial=True)
    project = forms.ModelChoiceField(
        queryset=Project.objects.order_by('-pk'),
        widget=forms.widgets.Select(attrs={'class': 'chosen'}),
        required=False,
        label='Restrict to project')
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
        required=True)
    project = forms.ModelChoiceField(queryset=Project.objects.all(),
                                     required=False, label='Restrict to project')
