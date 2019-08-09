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

from django import forms
from django.utils.translation import ugettext_lazy as _

from apps.common.forms import checkbox_field
from apps.document.field_types import LinkedDocumentsField
from apps.document.models import DocumentField

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
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
        queryset=DocumentField.objects.filter(type=LinkedDocumentsField.code),
        required=True)
