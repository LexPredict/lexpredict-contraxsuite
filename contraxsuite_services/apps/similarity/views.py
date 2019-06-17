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
from apps.task.views import BaseAjaxTaskView
from apps.similarity.forms import (
    PreconfiguredDocumentSimilaritySearchForm, SimilarityForm, PartySimilarityForm)
from apps.similarity.tasks import PreconfiguredDocumentSimilaritySearch, Similarity, PartySimilarity

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.2/LICENSE"
__version__ = "1.2.2"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class SimilarityView(BaseAjaxTaskView):
    task_class = Similarity
    form_class = SimilarityForm

    def get_metadata(self):
        similarity_items = []
        result_links = []
        if self.request.POST.get('search_similar_documents'):
            similarity_items.append('documents')
            result_links.append({'name': 'View Document Similarity List',
                                 'link': 'analyze:document-similarity-list'})
        if self.request.POST.get('search_similar_text_units'):
            similarity_items.append('text units')
            result_links.append({'name': 'View Text Unit Similarity List',
                                 'link': 'analyze:text-unit-similarity-list'})
        return dict(
            description='similarity for:{}; threshold:{}'.format(
                ', '.join(similarity_items),
                self.request.POST.get('similarity_threshold')),
            result_links=result_links)


class PartySimilarityView(BaseAjaxTaskView):
    task_class = PartySimilarity
    form_class = PartySimilarityForm

    def get_metadata(self):
        return dict(
            description='similarity type:{}, threshold:{}'.format(
                self.request.POST.get('similarity_type'),
                self.request.POST.get('similarity_threshold')),
            result_links=[{'name': 'View Party Usage List',
                           'link': 'extract:party-usage-list'}])


class PreconfiguredDocumentSimilaritySearchView(BaseAjaxTaskView):
    task_class = PreconfiguredDocumentSimilaritySearch
    form_class = PreconfiguredDocumentSimilaritySearchForm

    def get_metadata(self):
        similarity_items = []
        result_links = []
        if self.request.POST.get('search_similar_documents'):
            similarity_items.append('documents')
            result_links.append({'name': 'View Document Similarity List',
                                 'link': 'analyze:document-similarity-list'})
        if self.request.POST.get('search_similar_text_units'):
            similarity_items.append('text units')
            result_links.append({'name': 'View Text Unit Similarity List',
                                 'link': 'analyze:text-unit-similarity-list'})
        return dict(
            description='similarity for:{}; threshold:{}'.format(
                ', '.join(similarity_items),
                self.request.POST.get('similarity_threshold')),
            result_links=result_links)
