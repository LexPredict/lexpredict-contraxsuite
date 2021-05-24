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

from typing import Union, Any, List

import numpy
import pandas as pd
import scipy.spatial.distance
import sklearn
from scipy.spatial.distance import _METRICS

# Project imports
from apps.analyze.models import DocumentSimilarity, TextUnitSimilarity, TextUnit
from apps.analyze.ml.features import DocumentFeatures, TextUnitFeatures, \
    Document2VecFeatures, TextUnit2VecFeatures

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DocumentSimilarityEngine:
    """
    Calculate similarity between Documents.
    :Example:
        >>> engine = DocumentSimilarityEngine(
        ...:        queryset=some_queryset,
        ...:        project_id=18,
        ...:        feature_source="term",
        ...:        threshold=0.8)
        >>> engine.get_similarity()
    """
    similarity_model = DocumentSimilarity
    similarity_model_field_a = 'document_a_id'
    similarity_model_field_b = 'document_b_id'
    block_step = 1000

    def __init__(self,
                 queryset=None,
                 project_id=None,
                 unit_type='sentence',
                 feature_source='term',
                 use_tfidf=False,
                 distance_type='cosine',
                 threshold=0.5,
                 create_reverse_relations=False,
                 run_id=None,
                 log_routine=None,
                 **extra_kwargs):
        """
        :param queryset: Document/TextUnit queryset
        :param project_id: int (optional)
        :param unit_type: str - one of "sentence", "paragraph"
        :param feature_source: str or list[str] - source name - e.g. "term", or ["term", "date"]
        :param use_tfidf: bool
        :param distance_type: str
        :param threshold: float
        :param create_reverse_relations: bool - create B-A relations
        :param run_id: str
        :param log_routine: logger fn
        """
        self.queryset = queryset
        self.project_id = project_id
        self.unit_type = unit_type or 'sentence'
        self.feature_source = feature_source
        self.use_tfidf = use_tfidf
        self.distance_type = distance_type or 'cosine'
        self.threshold = threshold
        self.create_reverse_relations = create_reverse_relations
        self.run_id = run_id
        self.log_routine = log_routine
        self.feature_extractor = self.get_feature_extractor(feature_source)
        self.extra_kwargs = extra_kwargs

    def check_arguments(self):
        if self.distance_type not in _METRICS:
            raise RuntimeError(f'Wrong distance type "{self.distance_type}", it should be in {list(_METRICS.keys())}')

    def get_feature_extractor(self, feature_source):
        return Document2VecFeatures if feature_source == 'vector' else DocumentFeatures

    def get_features(self):
        skip_unqualified_values = self.threshold > 0.0

        # get Feature object, see real signature in features.py module
        feature_engine = self.feature_extractor(
            queryset=self.queryset,
            project_id=self.project_id,
            feature_source=self.feature_source,
            unit_type=self.unit_type,
            drop_empty_rows=skip_unqualified_values,
            log_message=self.log_routine,
            **self.extra_kwargs
        )
        return feature_engine.get_features()

    def create_sim_obj(self, obj_a_id, obj_b_id, similarity):
        """
        Prepare similarity object to save in db
        """
        sim_obj = self.similarity_model()
        setattr(sim_obj, self.similarity_model_field_a, obj_a_id)
        setattr(sim_obj, self.similarity_model_field_b, obj_b_id)
        sim_obj.similarity = similarity
        sim_obj.similarity_type = self.distance_type  # is not used, no model field
        sim_obj.run_id = self.run_id
        return sim_obj

    def _get_similarity(self):
        """
        Central method to calculate and store similarity -
        Non optimized memory usage - may fail on large term frequency matrix
        """
        # get Feature object, see real signature in features.py module
        features = self.get_features()

        # Get distance matrix using pdist and squareform (mostly to visualize data in mind)
        term_frequency_matrix = features.term_frequency_matrix
        if self.use_tfidf:
            term_frequency_matrix = sklearn.feature_extraction.text.TfidfTransformer().fit_transform(
                features.term_frequency_matrix).toarray()
        distance_matrix = scipy.spatial.distance.squareform(
            scipy.spatial.distance.pdist(term_frequency_matrix, metric=self.distance_type))

        counter = 0
        # Create records based on threshold
        for i in range(distance_matrix.shape[0]):
            sim_obj_list = []

            for j in range(distance_matrix.shape[1]):

                # Skip B-A blocks, process A-B blocks only - i.e. skip similarity reverse relations
                if self.create_reverse_relations is False and j < i:
                    continue

                # Skip A-A, B-B records
                if i == j:
                    continue

                if distance_matrix[i, j] <= 1.0 - self.threshold:
                    sim_obj = self.create_sim_obj(features.item_index[i],
                                                  features.item_index[j],
                                                  100 * (1.0 - distance_matrix[i, j]))
                    sim_obj_list.append(sim_obj)

            # Bulk create
            self.similarity_model.objects.bulk_create(sim_obj_list, ignore_conflicts=True)
            counter += len(sim_obj_list)
        return counter

    def get_similarity(self, item_id=None):
        """
        Central method to calculate and store similarity
        Optimized memory usage by iterating over feature dataframe to get
        term frequency matrix of lower size
        """
        # get Feature object, see real signature in features.py module
        features = self.get_features()

        if item_id:
            sim_obj_list = self.calc_block_similarity(
                features.term_frequency_matrix, features.item_index, item_id=item_id)
            return len(sim_obj_list)

        counter = 0
        for block_start in range(0, features.term_frequency_matrix[0], self.block_step):
            block_end = block_start + self.block_step
            sim_obj_list = self.calc_block_similarity(
                features.term_frequency_matrix, features.item_index, block_start, block_end)
            counter += len(sim_obj_list)

        return counter

    def set_refs(self, obj_list):
        # suitable for text units only to set project_ids
        return obj_list

    def calc_block_similarity(self,
                              feature_df_data: Union[numpy.array, list],
                              feature_df_index: list,
                              block_start: int = None,
                              block_end: int = None,
                              item_id: Union[int, str] = None) -> List[Any]:
        result = []

        if item_id:
            item_index = feature_df_index.index(item_id)
            item_data = feature_df_data[item_index:item_index + 1]
            feature_df_index = feature_df_index[:item_index] + feature_df_index[item_index + 1:]
            feature_df_data = numpy.concatenate((feature_df_data[:item_index], feature_df_data[item_index + 1:]))
            dist_list = scipy.spatial.distance.cdist(
                item_data, feature_df_data, metric=self.distance_type)[0].astype(numpy.float32)
            result = [(item_id, b_id, (1 - score) * 100) for b_id, score in
                      zip(feature_df_index, dist_list) if 1 - score >= self.threshold]
            if self.create_reverse_relations:
                result += [(b_id, a_id, score) for a_id, b_id, score in result]

        else:
            dist_list = scipy.spatial.distance.cdist(
                feature_df_data[block_start:block_end], feature_df_data[block_start:],
                metric=self.distance_type).astype(numpy.float32)

            for n, data in enumerate(zip(feature_df_index[block_start:block_end], dist_list)):
                a_id, a_scores = data
                res = [(a_id, b_id, (1 - score) * 100) for b_id, score in
                       zip(feature_df_index[block_start + n + 1:], a_scores[n + 1:])
                       if 1 - score >= self.threshold and a_id != b_id]
                if self.create_reverse_relations:
                    res += [(b_id, a_id, score) for a_id, b_id, score in res]

                result += res

            # XXX: this is more safe for memory but takes more time - from 30 to 300 %
            # for n in range(block_start, min(block_end, len(feature_df_index))):
            #     a_id = feature_df_index[n]
            #     dist_list = scipy.spatial.distance.cdist(
            #         [feature_df_data[n]], feature_df_data[n + 1:], metric=self.distance_type)[0].astype(numpy.float32)
            #     _result = [(a_id, b_id, (1 - score) * 100) for b_id, score in
            #                zip(feature_df_index[n + 1:], dist_list) if 1 - score >= self.threshold]
            #     if self.create_reverse_relations:
            #         _result += [(b_id, a_id, score) for a_id, b_id, score in _result]
            #     result += _result

        sim_obj_list = [self.create_sim_obj(*i) for i in result]
        sim_obj_list = self.set_refs(sim_obj_list)
        return sim_obj_list


class TextUnitSimilarityEngine(DocumentSimilarityEngine):
    """
    Calculate similarity between Documents.
    :Example:
        >>> engine = TextUnitSimilarityEngine(
        ...:        queryset=some_queryset,
        ...:        project_id=30,
        ...:        feature_source="term",
        ...:        threshold=0.8)
        >>> engine.get_similarity()
    """
    feature_extractor = TextUnitFeatures
    similarity_model = TextUnitSimilarity
    similarity_model_field_a = 'text_unit_a_id'
    similarity_model_field_b = 'text_unit_b_id'

    def get_feature_extractor(self, feature_source):
        return TextUnit2VecFeatures if feature_source == 'vector' else TextUnitFeatures

    def set_refs(self, obj_list):
        """
        Set project/document FKs for TextUnitSimilarity objects depending on text_unit_a_id/text_unit_b_id
        """
        unit_ids = {i for o in obj_list for i in (o.text_unit_a_id, o.text_unit_b_id)}
        values = TextUnit.objects.filter(id__in=unit_ids).values('id', 'document_id', 'project_id')
        values = {i['id']: i for i in values}
        ret = []
        for obj in obj_list:
            try:
                obj.document_a_id = values[obj.text_unit_a_id]['document_id']
                obj.document_b_id = values[obj.text_unit_b_id]['document_id']
                obj.project_a_id = values[obj.text_unit_a_id]['project_id']
                obj.project_b_id = values[obj.text_unit_b_id]['project_id']
                ret.append(obj)
            except KeyError:
                # rare case, seen one time, probably text unit was deleted whilst task execution
                pass
        return ret
