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
from typing import List, Optional, Iterable, Any, Tuple

from sklearn.metrics.pairwise import cosine_similarity

from apps.common.log_utils import ProcessLogger
from apps.common.sql_commons import SQLClause
from apps.document.field_types import FieldType
from apps.document.fields_processing.document_vectorizers import document_feature_vector_pipeline
from apps.document.models import DocumentField, Document, ClassifierModel, DocumentFieldValue
from apps.document.python_coded_fields import PythonCodedField
from apps.rawdb.field_value_tables import FIELD_CODE_DOC_ID, FIELD_CODE_CREATE_DATE
from apps.rawdb.field_value_tables import cache_document_fields
from apps.rawdb.repository.raw_db_repository import RawDbRepository
from apps.similarity.models import (
    DocumentSimilarityConfig, DST_FIELD_SIMILARITY_CONFIG_ATTR, DEFAULT_SIMILARITY_TRESHOLD,
    DEFAULT_DATE_CONSTRAINT_DAYS)

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.2/LICENSE"
__version__ = "1.2.2"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class SimilarDocumentsField(PythonCodedField):
    code = 'similarity.SimilarDocuments'
    title = 'Similar Documents'
    type = 'linked_documents'
    detect_per_text_unit = False

    def train_document_field_detector_model(self, document_field: DocumentField, train_data_project_ids: List,
                                            use_only_confirmed_field_values: bool = False,
                                            train_documents: Iterable[Document] = None) -> Optional[ClassifierModel]:
        return None

    def _maybe_save_reverse_similarity_value(self,
                                             log: ProcessLogger,
                                             field: DocumentField,
                                             document: Document,
                                             other_doc_id) -> bool:
        if not DocumentFieldValue.objects.filter(document_id=other_doc_id, field=field, value=document.pk).exists():
            other_document = Document.all_objects.get(pk=other_doc_id)
            DocumentFieldValue(document=other_document, field=field, value=document.pk).save()
            cache_document_fields(log=log, document=other_document, cache_generic_fields=False, cache_user_fields=True)

    def get_values(self, log: ProcessLogger, field: DocumentField, doc: Document, text: str) \
            -> List[Tuple[Any, Optional[int], Optional[int]]]:

        try:
            conf = getattr(field, DST_FIELD_SIMILARITY_CONFIG_ATTR)  # type: DocumentSimilarityConfig
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

        # TODO: replace with the corresponding method call when ready
        doc_field_values = dict()
        for fv in doc.documentfieldvalue_set \
                .filter(field__code__in=feature_vector_field_codes.union({date_constraint_field_code})):
            if fv.removed_by_user:
                continue

            field = fv.field
            field_type = fv.field.get_field_type()  # type: FieldType
            doc_field_values[field.code] = field_type \
                .merge_multi_python_values(doc_field_values.get(field.code), fv.python_value)
        doc_field_values[FIELD_CODE_DOC_ID] = doc.pk

        doc_date = doc_field_values.get(date_constraint_field_code) if date_constraint_field_code else None
        if not doc_date:
            doc_date = doc.history.last().history_date
            date_constraint_field_code = FIELD_CODE_CREATE_DATE

        date_start = doc_date - timedelta(days=date_constraint_days)
        date_end = doc_date + timedelta(days=date_constraint_days)

        try:
            vectorizer = document_feature_vector_pipeline(feature_vector_fields, use_field_codes=True)

            rawdb = RawDbRepository()
            where = SQLClause(f'"{FIELD_CODE_DOC_ID}" != %s '
                              f'and "{date_constraint_field_code}" >= %s '
                              f'and "{date_constraint_field_code}" <= %s',
                              [doc.pk, date_start, date_end])

            field_values_list = list(rawdb.get_field_values(document_type=document_type,
                                                            where_sql=where,
                                                            field_codes=feature_vector_field_codes.union(
                                                                {FIELD_CODE_DOC_ID, date_constraint_field_code})))

            if not field_values_list:
                return []

            field_values_list = [doc_field_values] + field_values_list
            feature_vectors = vectorizer.fit_transform(field_values_list)
            doc_feature_vectors = feature_vectors[0]
        except ValueError as ve:
            if 'empty vocabulary' in str(ve):
                log.info(f'Similarity: {field.code}: Vectorization got "empty vocabulary" probably no one of the docs '
                         f'contains any value in the feature vector fields.')
                return []
            raise ve

        similarities = cosine_similarity(doc_feature_vectors, feature_vectors)

        # TODO: Think about removing usage of other_field_values_list here and switching it to generator
        # to avoid storing the list of all field values. We only need feature vectors but they have no doc id.
        res = list()  # type: List[Tuple[Any, Optional[int], Optional[int]]]:
        for y, field_values in enumerate(field_values_list):
            other_doc_pk = field_values[FIELD_CODE_DOC_ID]
            if doc.pk == other_doc_pk:
                continue
            similarity = similarities[0, y]
            if similarity < similarity_threshold:
                continue
            res.append((other_doc_pk, None, None))
            self._maybe_save_reverse_similarity_value(log=log, field=field, document=doc, other_doc_id=other_doc_pk)

        return res
