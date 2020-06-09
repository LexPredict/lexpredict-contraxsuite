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

from apps.document.models import Document
from apps.similarity.chunk_similarity_task import ChunkSimilarity
from apps.similarity.forms import (
    PreconfiguredDocumentSimilaritySearchForm, SimilarityForm,
    PartySimilarityForm, ChunkSimilarityForm, SimilarityByFeaturesForm)
from apps.similarity.similarity_metrics import make_text_units_query, SimilarityLimits
from apps.similarity.tasks import (
    PreconfiguredDocumentSimilaritySearch, Similarity, PartySimilarity, SimilarityByFeatures)
from apps.task.views import BaseAjaxTaskView

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
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

    def start_task_and_return(self, data):
        if data.get('skip_confirmation'):
            self.start_task(data)
            return self.json_response('The task is started. It can take a while.')

        project = data.get('project')
        proj_id = project.id if project else None
        search_target = data.get('search_target')
        if not search_target:
            search_target = 'document' if data.get('search_similar_documents') else 'unit'

        if search_target == 'document':
            count = Document.objects.all().count() if not proj_id \
                else Document.objects.filter(project_id=proj_id).count()
            count_limit = SimilarityLimits.WARN_MAX_DOCUMENTS
            unit_type = 'documents'
        else:
            # unit_text_regex = DocumentChunkSimilarityProcessor.unit_text_regex
            unit_query = make_text_units_query(proj_id)
            count = unit_query.count()
            count_limit = SimilarityLimits.WARN_MAX_TEXT_UNITS
            unit_type = 'paragraphs'

        if count < count_limit:
            self.start_task(data)
            return self.json_response('The task is started. It can take a while.')
        return self.json_response({'message': f'Processing {count} {unit_type} may take a long time.',
                                   'confirm': True})


class SimilarityByFeaturesView(BaseAjaxTaskView):
    task_class = SimilarityByFeatures
    form_class = SimilarityByFeaturesForm


class ChunkSimilarityView(SimilarityView):
    task_class = ChunkSimilarity
    form_class = ChunkSimilarityForm

    def get_metadata(self):
        similarity_items = []
        result_links = []
        tgt = self.request.POST.get('search_target') or 'document'
        if tgt == 'document':
            similarity_items.append('documents')
            result_links.append({'name': 'View Document Similarity List',
                                 'link': 'analyze:document-similarity-list'})
        else:
            similarity_items.append('text units')
            result_links.append({'name': 'View Text Unit Similarity List',
                                 'link': 'analyze:text-unit-similarity-list'})
        return dict(
            description='similarity for:{}; threshold:{}'.format(
                ', '.join(similarity_items),
                self.request.POST.get('similarity_threshold')),
            result_links=result_links)

    def start_task_and_return(self, data):
        if data.get('skip_confirmation'):
            self.start_task(data)
            return self.json_response('The task is started. It can take a while.')

        sm = ChunkSimilarity()
        estimation = sm.estimate_time(**data)
        # if estimated task duration is less than 1 hour:
        if estimation < SimilarityLimits.WARN_CHUNK_SIMILARITY_SECONDS:
            self.start_task(data)
            return self.json_response('The task is started. It can take a while.')
        _min, sec = divmod(estimation, 60)
        hour, _min = divmod(_min, 60)
        estim_str = "%d:%02d:%02d" % (hour, _min, sec)
        return self.json_response({'message': f'Processing may take about {estim_str}.',
                                   'confirm': True})


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
