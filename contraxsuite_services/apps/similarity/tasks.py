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

import math
from collections import defaultdict
from typing import Optional

import fuzzywuzzy.fuzz
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from apps.celery import app

from apps.analyze.ml.similarity import DocumentSimilarityEngine, TextUnitSimilarityEngine
from apps.analyze.models import (
    DocumentSimilarity, TextUnitSimilarity, PartySimilarity as PartySimilarityModel)
from apps.document import signals
from apps.document.field_processing.document_vectorizers import document_feature_vector_pipeline
from apps.document.models import DocumentField, TextUnit, Document
from apps.extract.models import Party
from apps.rawdb.constants import FIELD_CODE_DOC_ID
from apps.similarity.chunk_similarity_task import ChunkSimilarity
from apps.similarity.models import DocumentSimilarityConfig, DST_FIELD_SIMILARITY_CONFIG_ATTR
from apps.task.tasks import BaseTask, remove_punctuation_map, CeleryTaskLogger

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# TODO: Configuration-based and language-based stemmer.

# Create global stemmer
stemmer = nltk.stem.porter.PorterStemmer()


def normalize(text):
    """
    Simple text normalizer returning stemmed, lowercased tokens.
    :param text:
    :return:
    """
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))


def stem_tokens(tokens):
    """
    Simple token stemmer.
    :param tokens:
    :return:
    """
    res = []
    for item in tokens:
        try:
            res.append(stemmer.stem(item))
        except IndexError:
            pass
    return res


class PartySimilarity(BaseTask):
    """
    Task for the identification of similar party names.
    """
    name = 'Party Similarity'

    def process(self, **kwargs):
        """
        Task process method.
        :param kwargs: dict, form data
        """
        parties = Party.objects.values_list('pk', 'name')
        self.set_push_steps(len(parties) + 1)

        # 1. Delete if requested
        if kwargs['delete']:
            PartySimilarityModel.objects.all().delete()

        # 2. Select scorer
        scorer = getattr(fuzzywuzzy.fuzz, kwargs['similarity_type'])

        # 3. Iterate through all pairs
        similar_results = []
        for party_a_pk, party_a_name in parties:
            for party_b_pk, party_b_name in parties:
                if party_a_pk == party_b_pk:
                    continue

                # Calculate similarity
                if not kwargs['case_sensitive']:
                    party_a_name = party_a_name.upper()
                    party_b_name = party_b_name.upper()

                score = scorer(party_a_name, party_b_name)
                if score >= kwargs['similarity_threshold']:
                    similar_results.append(
                        PartySimilarityModel(
                            party_a_id=party_a_pk,
                            party_b_id=party_b_pk,
                            similarity=score))
            self.push()

        # 4. Bulk create similarity objects
        PartySimilarityModel.objects.bulk_create(similar_results)
        self.push()


class Similarity(BaseTask):
    """
    Find Similar Documents, Text Units
    """
    name = 'Similarity'
    verbose = True
    n_features = 100
    self_name_len = 3
    step = 2000

    def process(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

        search_similar_documents = kwargs['search_similar_documents']
        search_similar_text_units = kwargs['search_similar_text_units']
        similarity_threshold = kwargs['similarity_threshold']
        project = kwargs.get('project')
        project_id = project['pk'] if project else 0
        self.log_info('Min similarity: %d' % similarity_threshold)

        # get text units with min length 100 signs
        filters = dict(unit_type='paragraph', textunittext__text__regex=r'.{100}.*')
        if project_id:
            filters['document__project_id'] = project_id
        text_units = TextUnit.objects.filter(**filters)
        len_tu_set = text_units.count()

        push_steps = 0
        if search_similar_documents:
            push_steps += 4
        if search_similar_text_units:
            push_steps += math.ceil(len_tu_set / self.step) ** 2 + 3
        self.set_push_steps(push_steps)

        documents = Document.objects.filter(project_id=project_id) if project_id \
            else Document.objects.all()

        # similar Documents
        if search_similar_documents:

            # step #1 - delete
            if kwargs['delete']:
                DocumentSimilarity.objects.all().delete()
            self.push()

            # step #2 - prepare data
            texts_set = ['\n'.join(d.textunit_set.values_list('textunittext__text', flat=True))
                         for d in documents]
            self.push()

            # step #3
            vectorizer = TfidfVectorizer(max_df=0.5, max_features=self.n_features,
                                         min_df=2, stop_words='english',
                                         use_idf=kwargs['use_idf'])
            X = vectorizer.fit_transform(texts_set)
            self.push()

            # step #4
            similarity_matrix = cosine_similarity(X) * 100
            pks = documents.values_list('pk', flat=True)
            for x in range(len(pks) - 1):
                document_a = pks[x]
                # use it to search for unique a<>b relations
                # for y, document_b in enumerate(Document.objects.all()[x + 1:], start=x + 1):
                for y in range(x + 1, len(pks)):
                    document_b = pks[y]
                    similarity = similarity_matrix[x, y]
                    if similarity < similarity_threshold:
                        continue
                    DocumentSimilarity.objects.create(
                        document_a_id=document_a,
                        document_b_id=document_b,
                        similarity=similarity)
            self.push()

        # similar Text Units
        if search_similar_text_units:

            # step #1 - delete
            if kwargs['delete']:
                TextUnitSimilarity.objects.all().delete()
            self.push()

            # step #2 - prepare data
            texts_set, pks = zip(*text_units.values_list('textunittext__text', 'pk'))
            self.push()

            # step #3
            vectorizer = TfidfVectorizer(tokenizer=normalize,
                                         max_df=0.5, max_features=self.n_features,
                                         min_df=2, stop_words='english',
                                         use_idf=kwargs['use_idf'])
            X = vectorizer.fit_transform(texts_set)
            self.push()

            # step #4
            for i in range(0, len_tu_set, self.step):
                for j in range(i + 1, len_tu_set, self.step):
                    similarity_matrix = cosine_similarity(
                        X[i:min([i + self.step, len_tu_set])],
                        X[j:min([j + self.step, len_tu_set])]) * 100
                    for g in range(similarity_matrix.shape[0]):
                        tu_sim = [
                            TextUnitSimilarity(
                                text_unit_a_id=pks[i + g],
                                text_unit_b_id=pks[j + h],
                                similarity=similarity_matrix[g, h])
                            for h in range(similarity_matrix.shape[1])
                            if i + g != j + h and similarity_matrix[g, h] >= similarity_threshold]
                        TextUnitSimilarity.objects.bulk_create(tu_sim)
                    self.push()


class SimilarityByFeatures(BaseTask):
    """
    Find Similar Documents, Text Units by extracted features
    """
    name = 'Similarity By Features'

    def process(self, **kwargs):
        search_similar_documents = kwargs['search_similar_documents']
        search_similar_text_units = kwargs['search_similar_text_units']

        project = kwargs['project']
        project_id = project['pk'] if project else None
        unit_type = kwargs['unit_type']
        feature_source = kwargs['feature_source']
        use_tfidf = kwargs['use_tfidf']
        distance_type = kwargs['distance_type']
        similarity_threshold = kwargs['similarity_threshold'] / 100

        self.log_info('Min similarity: {}'.format(similarity_threshold))
        self.set_push_steps(2)

        if search_similar_documents:
            db_model = DocumentSimilarity
            engine_class = DocumentSimilarityEngine
        elif search_similar_text_units:
            db_model = TextUnitSimilarity
            engine_class = TextUnitSimilarityEngine
        else:
            self.log_error("Classify task target (documents or text units) is not specified.")
            return

        if kwargs['delete']:
            # TODO: delete all Similarity db objects OR filter by unit_type/project_id
            deleted = db_model.objects.filter().delete()
            self.log_info('Deleted "{}"'.format(deleted[1]))

        self.push()

        engine = engine_class(
            project_id=project_id,
            unit_type=unit_type,
            feature_source=feature_source,
            use_tfidf=use_tfidf,
            distance_type=distance_type,
            threshold=similarity_threshold
        )
        count = engine.get_similarity()
        self.log_info('Created: %d similarity objects.' % count)
        self.push()


class PreconfiguredDocumentSimilaritySearch(BaseTask):
    name = 'PreconfiguredDocumentSimilaritySearch'
    verbose = True
    n_features = 100
    self_name_len = 3
    step = 2000

    def process(self, **kwargs):
        dst_field = kwargs['field']
        dst_field = DocumentField.objects.filter(pk=dst_field['pk']) \
            .prefetch_related('depends_on_fields') \
            .select_related(DST_FIELD_SIMILARITY_CONFIG_ATTR) \
            .first()  # type: DocumentField

        if not dst_field:
            raise RuntimeError('Document field not found: {0}'.format(kwargs['field']))

        proj = kwargs['project']
        proj_id = proj['pk'] if proj else None  # type:Optional[int]
        doc_query = Document.objects.filter(document_type=dst_field.document_type,
                                            project_id=proj_id) if proj_id \
            else Document.objects.filter(document_type=dst_field.document_type)

        config = getattr(dst_field, DST_FIELD_SIMILARITY_CONFIG_ATTR)  # type: DocumentSimilarityConfig

        config.self_validate()

        similarity_threshold = config.similarity_threshold
        feature_vector_fields = list(dst_field.depends_on_fields.all())
        feature_vector_field_codes = [f.code for f in feature_vector_fields]

        self.log_info('{field}: Min similarity: {threshold}'
                      .format(field=dst_field.code, threshold=similarity_threshold))

        import apps.document.repository.document_field_repository as dfr
        field_repo = dfr.DocumentFieldRepository()
        qr_doc_ids = doc_query.values_list('pk', flat=True)
        doc_ids_to_code_to_value = field_repo \
            .get_field_code_to_python_value_multiple_docs(document_type_id=dst_field.document_type_id,
                                                          doc_ids=qr_doc_ids,
                                                          field_codes_only=feature_vector_field_codes)

        field_values_list = list()
        for doc_id, values in doc_ids_to_code_to_value:
            values[FIELD_CODE_DOC_ID] = doc_id
            field_values_list.append(values)

        total_docs = len(field_values_list)

        self.set_push_steps(int(5 + total_docs / 100))

        self.push()
        self.log_info(
            '{field}: Building feature vectors for {n} documents'.format(field=dst_field.code, n=total_docs))

        vectorizer = document_feature_vector_pipeline(feature_vector_fields, use_field_codes=True)
        feature_vectors = vectorizer.fit_transform(field_values_list)

        self.push()
        self.log_info('{field}: Finding similar documents (similarity >= {threshold})'
                      .format(field=dst_field.code, threshold=similarity_threshold))

        doc_ids_to_values = defaultdict(set)
        for x, doc_a_field_values in enumerate(field_values_list):
            doc_a_pk = doc_a_field_values[FIELD_CODE_DOC_ID]
            similarities = cosine_similarity(feature_vectors[x], feature_vectors)
            for y, doc_b_field_values in enumerate(field_values_list):
                doc_b_pk = doc_b_field_values[FIELD_CODE_DOC_ID]
                if doc_a_pk == doc_b_pk:
                    continue
                similarity = similarities[0, y]
                if similarity < similarity_threshold:
                    continue
                doc_ids_to_values[doc_a_pk].add(doc_b_pk)
                doc_ids_to_values[doc_b_pk].add(doc_a_pk)
            if x % 100 == 0:
                self.log_info('{field}: Checked for similarity {x} documents of {n}'
                              .format(field=dst_field.code, x=x + 1, n=total_docs))
                self.push()

        self.push()
        self.log_info('{field}: Found {n} similar documents. Storing links into the document fields.'
                      .format(field=dst_field.code, n=len(doc_ids_to_values)))

        doc_ids_to_values = {doc_id: list(v) if v else None for doc_id, v in doc_ids_to_values}
        field_repo.store_values_one_field_many_docs_no_ants(field=dst_field, doc_ids_to_values=doc_ids_to_values)

        log = CeleryTaskLogger(self)
        for doc_id in doc_ids_to_values.keys():
            try:
                doc = Document.objects.get(pk=doc_id)
                signals.fire_document_changed(log=log, document=doc, changed_by_user=None, system_fields_changed=False,
                                              generic_fields_changed=False, user_fields_changed=[dst_field.code])
            except Exception as ex:
                self.log_error(f'Unable to fire doc id change event for doc #{doc_id}', exc_info=ex)


app.register_task(PreconfiguredDocumentSimilaritySearch())
app.register_task(Similarity())
app.register_task(SimilarityByFeatures())
app.register_task(ChunkSimilarity())
app.register_task(PartySimilarity())
