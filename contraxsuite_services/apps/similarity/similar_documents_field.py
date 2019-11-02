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

from datetime import timedelta
from typing import List, Optional, Iterable, Any, Set, Dict

from sklearn.metrics.pairwise import cosine_similarity

from apps.common.log_utils import ProcessLogger
from apps.document.field_processing.document_vectorizers import document_feature_vector_pipeline
from apps.document.models import DocumentField, Document, ClassifierModel, FieldValue
from apps.document.python_coded_fields import PythonCodedField
from apps.document.repository.document_field_repository import DocumentFieldRepository
from apps.document.repository.dto import FieldValueDTO
from apps.rawdb.constants import FIELD_CODE_DOC_ID
from apps.rawdb.field_value_tables import cache_document_fields
from apps.similarity.models import (
    DocumentSimilarityConfig, DST_FIELD_SIMILARITY_CONFIG_ATTR, DEFAULT_SIMILARITY_TRESHOLD,
    DEFAULT_DATE_CONSTRAINT_DAYS)

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.3.0/LICENSE"
__version__ = "1.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class SimilarDocumentsField(PythonCodedField):
    code = 'similarity.SimilarDocuments'
    title = 'Similar Documents'
    type = 'linked_documents'

    def train_document_field_detector_model(self, document_field: DocumentField, train_data_project_ids: List,
                                            use_only_confirmed_field_values: bool = False,
                                            train_documents: Iterable[Document] = None) -> Optional[ClassifierModel]:
        return None

    def _maybe_save_reverse_similarity_value(self,
                                             log: ProcessLogger,
                                             field: DocumentField,
                                             document: Document,
                                             other_doc_id) -> bool:
        field_repo = DocumentFieldRepository()
        if not field_repo.field_value_exists(other_doc_id, field.pk, [document.pk]):
            other_document = Document.all_objects.get(pk=other_doc_id)
            field_repo.update_field_value_with_dto(document=other_document,
                                                   field=field,
                                                   field_value_dto=FieldValueDTO(field_value=[document.pk]),
                                                   merge=True)
            cache_document_fields(log=log,
                                  document=other_document,
                                  cache_system_fields=False,
                                  cache_generic_fields=False,
                                  cache_user_fields=[field.code])

    def get_value(self, log: ProcessLogger, field: DocumentField, doc: Document, text: str,
                  cur_field_code_to_value: Dict[str, Any]) -> Optional[FieldValueDTO]:

        try:
            conf = getattr(field, DST_FIELD_SIMILARITY_CONFIG_ATTR)  # type: Optional[DocumentSimilarityConfig]
        except DocumentSimilarityConfig.DoesNotExist:
            conf = None

        if conf:
            conf.self_validate()

        similarity_threshold = conf.similarity_threshold if conf else DEFAULT_SIMILARITY_TRESHOLD
        feature_vector_fields = field.depends_on_fields.all()
        date_constraint_field_code = conf.date_constraint_field.code if conf and conf.date_constraint_field else None
        date_constraint_days = conf.date_constraint_days if conf else DEFAULT_DATE_CONSTRAINT_DAYS
        document_type = doc.document_type

        feature_vector_field_codes = {f.code for f in feature_vector_fields}

        doc_field_values = dict(cur_field_code_to_value)
        doc_field_values[FIELD_CODE_DOC_ID] = doc.pk

        if date_constraint_field_code:
            doc_date = doc_field_values.get(date_constraint_field_code)
            date_start = doc_date - timedelta(days=date_constraint_days)
            date_end = doc_date + timedelta(days=date_constraint_days)

            doc_ids_query = FieldValue.objects \
                .filter(field__code=date_constraint_field_code) \
                .filter(value__gte=date_start) \
                .filter(value__lte=date_end) \
                .filter(document__document_type_id=document_type.pk) \
                .exclude(document_id=doc.pk) \
                .values_list('document_id', flat=True)
        else:
            doc_date = doc.history.last().history_date
            date_start = doc_date - timedelta(days=date_constraint_days)
            date_end = doc_date + timedelta(days=date_constraint_days)

            doc_ids_query = Document.history \
                .filter(history_type='+',
                        history_date__gte=date_start,
                        history_date__lte=date_end,
                        document_type_id=document_type.pk) \
                .exclude(id=doc.pk) \
                .values_list('pk', flat=True)

        try:
            vectorizer = document_feature_vector_pipeline(feature_vector_fields, use_field_codes=True)

            field_repo = DocumentFieldRepository()

            field_values_list = list()

            for doc_id, field_values in field_repo \
                    .get_field_code_to_python_value_multiple_docs(document_type_id=document_type.pk,
                                                                  doc_ids=doc_ids_query,
                                                                  field_codes_only=feature_vector_field_codes):
                d = dict(field_values)
                d[FIELD_CODE_DOC_ID] = doc_id
                field_values_list.append(d)

            if not field_values_list:
                return None

            field_values_list = [doc_field_values] + field_values_list
            feature_vectors = vectorizer.fit_transform(field_values_list)
            doc_feature_vectors = feature_vectors[0]
        except ValueError as ve:
            if 'empty vocabulary' in str(ve):
                log.info(f'Similarity: {field.code}: Vectorization got "empty vocabulary" probably no one of the docs '
                         f'contains any value in the feature vector fields.')
                return None
            raise ve

        similarities = cosine_similarity(doc_feature_vectors, feature_vectors)

        # TODO: Think about removing usage of other_field_values_list here and switching it to generator
        # to avoid storing the list of all field values. We only need feature vectors but they have no doc id.
        res = set()  # type: Set[int]
        for y, field_values in enumerate(field_values_list):
            other_doc_pk = field_values[FIELD_CODE_DOC_ID]
            if doc.pk == other_doc_pk:
                continue
            similarity = similarities[0, y]
            if similarity < similarity_threshold:
                continue
            res.add(other_doc_pk)
            self._maybe_save_reverse_similarity_value(log=log, field=field, document=doc, other_doc_id=other_doc_pk)

        return FieldValueDTO(field_values=sorted(res))
