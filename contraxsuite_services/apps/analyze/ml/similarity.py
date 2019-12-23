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

import numpy
import scipy.spatial.distance
import sklearn

# Project imports
from apps.analyze.models import DocumentSimilarity, TextUnitSimilarity
from apps.document.models import Document, DocumentText
from apps.analyze.ml.features import DocumentFeatures, TextUnitFeatures
from lexnlp.nlp.en.tokens import get_token_list, get_stem_list

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
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
    feature_extractor = DocumentFeatures
    similarity_model = DocumentSimilarity
    similarity_model_field_a = 'document_a_id'
    similarity_model_field_b = 'document_b_id'

    def __init__(self,
                 queryset=None,
                 project_id=None,
                 unit_type='sentence',
                 feature_source='term',
                 use_tfidf=False,
                 distance_type='cosine',
                 threshold=0.5):
        """
        :param queryset: Document/TextUnit queryset
        :param project_id: int (optional)
        :param unit_type: str - one of "sentence", "paragraph"
        :param feature_source: str or list[str] - source name - e.g. "term", or ["term", "date"]
        :param use_tfidf: bool
        :param distance_type: str
        :param threshold: float
        """
        self.queryset = queryset
        self.project_id = project_id
        self.unit_type = unit_type
        self.feature_source = feature_source
        self.use_tfidf = use_tfidf
        self.distance_type = distance_type
        self.threshold = threshold

    def get_similarity_matrix(self, observation_matrix: numpy.array):
        """
        Calculate the pairwise similarity of a set of records in an MxN `observation_matrix` with M records and N features.
        :param observation_matrix: numpy.array - feature matrix
        :return: numpy.array - distance_matrix
        # TODO: Implement boolean conversion for relevant distance metrics, e.g., Jaccard.
        """
        # Toggle TF-IDF
        if self.use_tfidf:
            observation_matrix = sklearn.feature_extraction.text.TfidfTransformer().fit_transform(
                observation_matrix).toarray()
            distance_matrix = scipy.spatial.distance.squareform(
                scipy.spatial.distance.pdist(observation_matrix, metric=self.distance_type))
        else:
            distance_matrix = scipy.spatial.distance.squareform(
                scipy.spatial.distance.pdist(observation_matrix, self.distance_type))

        return distance_matrix

    def get_similarity(self):
        """
        Central method to calculate and store similarity
        """
        skip_unqualified_values = self.threshold > 0

        # get Feature object, see real signature in features.py module
        features = self.feature_extractor(
            queryset=self.queryset,
            project_id=self.project_id,
            feature_source=self.feature_source,
            unit_type=self.unit_type,
            skip_unqualified_values=skip_unqualified_values).get_features()

        # Get distance matrix
        distance_matrix = self.get_similarity_matrix(features.term_frequency_matrix)

        # Create records based on threshold
        sim_obj_list = []

        for i in range(distance_matrix.shape[0]):
            for j in range(i):
                if distance_matrix[i, j] <= (1.0 - self.threshold):
                    sim_obj = self.similarity_model()
                    setattr(sim_obj, self.similarity_model_field_a, features.item_index[i])
                    setattr(sim_obj, self.similarity_model_field_b, features.item_index[j])
                    sim_obj.similarity = 100 * (1.0 - distance_matrix[i, j])
                    sim_obj.similarity_type = self.distance_type
                    sim_obj_list.append(sim_obj)

        # Bulk create
        self.similarity_model.objects.bulk_create(sim_obj_list)


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


# TODO: this is uncompleted feature in 1.3.0-lexnlp-review branch, keep it as is for now
def find_similar_doc_text(document_query_set=None, threshold: float = 0.5, distance_type: str = "cosine",
                          lowercase: bool = True, stopword: bool = True, stem: bool = True):
    """
    Find similar documents using the actual text of documents, optionally lowercasing, stopwording,
    and stemming text.  Only records with greater than `threshold` similarity under distance type `distance_type`
    are populated in database.
    NOTE: This method is designed to "just work" by iterating efficiently from a memory perspective.  More efficient
    methods are possible if we assume large RAM environments, but such methods should not be default for reliability
    perspective.
    :param document_query_set:
    :param threshold:
    :param distance_type:
    :param lowercase:
    :param stopword:
    :param stem:
    :return:
    """

    # We are going to first obtain only the primary keys to allow for efficient lower-triangular access.
    if document_query_set is None:
        document_id_set = Document.objects.only("id").order_by("id").values_list("id", flat=True)
    else:
        document_id_set = document_query_set.order_by("-id").values_list("id", flat=True)

    # Processor switch
    processor_method = get_stem_list if stem else get_token_list

    # N.B.: This method duplicates data requests in exchange for minimal memory usage.  It is designed to
    # scale to any size document set, even if its performance is lower than in-memory options.  It should be the
    # default approach unless we can confirm that a document set and RAM meet needs for other approaches.

    # We are going to fix text for outer document.
    # TODO: Finish implementing once lexnlp.nlp.en.transforms.tokens is improved
    for i in enumerate(document_id_set):
        doc_a = DocumentText.objects.get(document__id=document_id_set[i])
        doc_a_tokens = processor_method(doc_a.full_text, stopword=stem, lowercase=lowercase)
        # TODO: get_token_distribution/get_stem_distribution

        # The inner loop stops at i to ensure lower-triangular access pattern.
        for j in range(i):
            doc_b = DocumentText.objects.get(document__id=document_id_set[j])
            doc_b_tokens = processor_method(doc_b.full_text, stopword=stem, lowercase=lowercase)
            # TODO: get_token_distribution/get_stem_distribution
