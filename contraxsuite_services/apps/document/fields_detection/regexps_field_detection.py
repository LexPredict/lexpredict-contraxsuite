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

import io
from typing import Optional, List, Iterable, Dict, Any

import pandas as pd

from apps.document.field_types import FieldType
from apps.document.fields_detection.detector_field_matcher import DetectorFieldMatcher
from apps.document.fields_detection.fields_detection_abstractions import FieldDetectionStrategy, DetectedFieldValue, \
    ProcessLogger
from apps.document.fields_detection.stop_words import detect_with_stop_words_by_field_and_full_text
from apps.document.fields_processing.field_processing_utils import merge_document_field_values_to_python_value
from apps.document.models import ClassifierModel, TextUnit, DocumentFieldDetector, DocumentField, Document
from apps.document.repository.base_field_detector_repository import BaseFieldDetectorRepository
from apps.document.repository.base_text_unit_repository import BaseTextUnitRepository
from apps.document.repository.field_detector_repository import FieldDetectorRepository
from apps.document.repository.text_unit_repository import TextUnitRepository
from ..value_extraction_hints import ValueExtractionHint

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class RegexpsOnlyFieldDetectionStrategy(FieldDetectionStrategy):
    code = DocumentField.VD_USE_REGEXPS_ONLY

    text_unit_repo = TextUnitRepository()  # type:BaseTextUnitRepository
    field_detector_repo = FieldDetectorRepository()  # type: BaseFieldDetectorRepository

    @classmethod
    def train_document_field_detector_model(cls,
                                            log: ProcessLogger,
                                            field: DocumentField,
                                            train_data_project_ids: Optional[List],
                                            use_only_confirmed_field_values: bool = False,
                                            train_documents: Iterable[Document] = None) -> Optional[ClassifierModel]:

        return None

    @classmethod
    def detect_field_values(cls,
                            log: ProcessLogger,
                            doc: Document,
                            field: DocumentField,
                            cached_fields: Dict[str, Any]) -> List[DetectedFieldValue]:

        depends_on_full_text = doc.full_text
        detected_with_stop_words, detected_values = detect_with_stop_words_by_field_and_full_text(field,
                                                                                                  depends_on_full_text)
        if detected_with_stop_words:
            return detected_values or list()

        qs_text_units = RegexpsOnlyFieldDetectionStrategy.\
            text_unit_repo.get_doc_text_units(doc, field.text_unit_type)

        field_detectors = RegexpsOnlyFieldDetectionStrategy.\
            field_detector_repo.get_field_detectors(field)
        detectors = [DetectorFieldMatcher(d) for d in field_detectors]

        field_type_adapter = field.get_field_type()  # type: FieldType

        detected_values = list()  # type: List[DetectedFieldValue]


        for text_unit in qs_text_units:  # type: TextUnit

            for field_detector in detectors:
                matching_string = field_detector.matching_string(text_unit.text,
                                                                 text_is_sentence=text_unit.is_sentence())
                if matching_string is not None:
                    value = field_detector.get_validated_detected_value(field)
                    hint_name = None
                    if field_type_adapter.requires_value:
                        hint_name = field_detector.extraction_hint or ValueExtractionHint.TAKE_FIRST.name
                        value, hint_name = field_type_adapter \
                            .get_or_extract_value(doc,
                                                  field, value,
                                                  hint_name,
                                                  matching_string)
                        if value is None:
                            continue

                    detected_values.append(DetectedFieldValue(field, value, text_unit, hint_name))

                    if not (field_type_adapter.multi_value or field.is_choice_field()):
                        break

            if detected_values and not (field_type_adapter.multi_value or field.is_choice_field()):
                break

        return detected_values


class FieldBasedRegexpsDetectionStrategy(FieldDetectionStrategy):
    code = DocumentField.VD_FIELD_BASED_REGEXPS

    @classmethod
    def uses_cached_document_field_values(cls, field):
        return True

    @classmethod
    def train_document_field_detector_model(cls,
                                            log: ProcessLogger,
                                            field: DocumentField,
                                            train_data_project_ids: Optional[List],
                                            use_only_confirmed_field_values: bool = False,
                                            train_documents: Iterable[Document] = None) -> Optional[ClassifierModel]:

        return None

    @classmethod
    def detect_field_values(cls,
                            log: ProcessLogger,
                            doc: Document,
                            field: DocumentField,
                            cached_fields: Dict[str, Any]) -> List[DetectedFieldValue]:

        depends_on_fields = list(field.depends_on_fields.all())

        qs_document_field_values = doc.documentfieldvalue_set \
            .filter(removed_by_user=False) \
            .filter(field__in=depends_on_fields)

        field_code_to_value = merge_document_field_values_to_python_value(list(qs_document_field_values))

        field_code_to_value = {f.code: field_code_to_value.get(f.code) for f in depends_on_fields}

        if field.stop_words:
            depends_on_full_text = '\n'.join([str(v) for v in field_code_to_value.values()])
            detected_with_stop_words, detected_values \
                = detect_with_stop_words_by_field_and_full_text(field, depends_on_full_text)
            if detected_with_stop_words:
                return detected_values or list()

        field_detectors = DocumentFieldDetector.objects.filter(field=field)
        detectors = [DetectorFieldMatcher(d) for d in field_detectors]
        field_type_adapter = field.get_field_type()  # type: FieldType

        detected_values = list()  # type: List[DetectedFieldValue]

        for depends_on_value in field_code_to_value.values():
            if not depends_on_value:
                continue
            depends_on_value = str(depends_on_value)
            for field_detector in detectors:  # type: DetectorFieldMatcher
                matching_string = field_detector.matching_string(depends_on_value, text_is_sentence=False)
                if matching_string is not None:
                    value = field_detector.get_validated_detected_value(field)
                    hint_name = None
                    if field_type_adapter.requires_value:
                        hint_name = field_detector.extraction_hint or ValueExtractionHint.TAKE_FIRST.name
                        value, hint_name = field_type_adapter \
                            .get_or_extract_value(doc,
                                                  field, value,
                                                  hint_name,
                                                  matching_string)
                        if value is None:
                            continue

                    detected_values.append(DetectedFieldValue(field, value, None, hint_name))

                    if not (field_type_adapter.multi_value or field.is_choice_field()):
                        break

            if detected_values and not (field_type_adapter.multi_value or field.is_choice_field()):
                break

        return detected_values


FD_CATEGORY_IMPORTED_SIMPLE_CONFIG = 'imported_simple_config'


def apply_simple_config(log: ProcessLogger,
                        document_field: DocumentField,
                        csv: bytes,
                        drop_previous_field_detectors: bool,
                        update_field_choice_values: bool,
                        csv_contains_regexps: bool = False):
    df = pd.read_csv(io.BytesIO(csv), dtype=str)
    if df.shape[0] < 1 or df.shape[1] < 1:
        raise ValueError('Config csv contains no data')
    row_num = df.shape[0]

    if update_field_choice_values:
        choices = df[df.columns[0]].dropna().drop_duplicates().sort_values().tolist()
        document_field.choices = '\n'.join(choices)
        document_field.save()

    log.info('Creating {2} naive field detectors for document field {0} and document type {1}...'
             .format(document_field, document_field.document_type, df.shape[0]))
    log.set_progress_steps_number(int(row_num / 10) + 1)
    if drop_previous_field_detectors:
        DocumentFieldDetector.objects.filter(field=document_field, category=FD_CATEGORY_IMPORTED_SIMPLE_CONFIG).delete()
    for index, row in df.iterrows():
        if len(row) == 0:
            continue

        includes = row.dropna()

        if not csv_contains_regexps:
            includes = [i.strip().replace(' ', '\s{1,100}') for i in includes]
        includes = [i for i in includes if i]

        if len(includes) == 1:
            log.info('There are no search strings specified for detected value {0}'.format(row[0]))
            continue

        detector = DocumentFieldDetector()
        detector.category = FD_CATEGORY_IMPORTED_SIMPLE_CONFIG
        detector.field = document_field
        detector.regexps_pre_process_lower = True
        detector.detected_value = row[0]
        detector.include_regexps = '\n'.join(includes[1:])
        detector.save()
        if index % 10 == 0:
            log.step_progress()
    log.info('Done.')
