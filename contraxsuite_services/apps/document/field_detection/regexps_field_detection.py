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

from apps.common.log_utils import ProcessLogger
from apps.document.field_types import TypedField, MultiValueField
from apps.document.field_detection.detector_field_matcher import DetectorFieldMatcher
from apps.document.field_detection.fields_detection_abstractions import FieldDetectionStrategy
from apps.document.field_detection.stop_words import detect_with_stop_words_by_field_and_full_text
from apps.document.models import ClassifierModel, TextUnit, DocumentFieldDetector, DocumentField, Document
from apps.document.repository.dto import FieldValueDTO, AnnotationDTO
from apps.document.repository.field_detector_repository import FieldDetectorRepository
from apps.document.repository.text_unit_repository import TextUnitRepository
from apps.document.value_extraction_hints import ValueExtractionHint

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class ValueExtractionFunctionThrownException(Exception):
    pass


class CaughtErrorWhileApplyingFieldDetector(Exception):
    pass


class RegexpsOnlyFieldDetectionStrategy(FieldDetectionStrategy):
    code = DocumentField.VD_USE_REGEXPS_ONLY

    @classmethod
    def has_problems_with_field(cls, field: DocumentField) -> Optional[str]:
        return None

    @classmethod
    def train_document_field_detector_model(cls,
                                            log: ProcessLogger,
                                            field: DocumentField,
                                            train_data_project_ids: Optional[List],
                                            use_only_confirmed_field_values: bool = False,
                                            train_documents: Iterable[Document] = None) -> Optional[ClassifierModel]:

        return None

    @classmethod
    def detect_field_value(cls,
                           log: ProcessLogger,
                           doc: Document,
                           field: DocumentField,
                           field_code_to_value: Dict[str, Any]) -> Optional[FieldValueDTO]:
        text_unit_repo = TextUnitRepository()
        field_detector_repo = FieldDetectorRepository()

        depends_on_full_text = doc.full_text
        detected_with_stop_words, detected_value = detect_with_stop_words_by_field_and_full_text(field,
                                                                                                 depends_on_full_text)
        if detected_with_stop_words:
            return FieldValueDTO(field_value=detected_value)

        qs_text_units = text_unit_repo.get_doc_text_units(doc, field.text_unit_type)

        field_detectors = field_detector_repo.get_field_detectors(field)
        detectors = [DetectorFieldMatcher(d) for d in field_detectors]

        typed_field = TypedField.by(field)  # type: TypedField
        ants = list()  # type: List[AnnotationDTO]
        units_counted = 0

        for text_unit in qs_text_units:  # type: TextUnit
            if field.detect_limit_count:
                units_counted = FieldDetectionStrategy.update_units_counted(
                    field, units_counted, text_unit)
                if units_counted > field.detect_limit_count:
                    break

            for field_detector in detectors:
                try:
                    matching_piece = field_detector.matching_string(
                        text_unit.textunittext.text, text_is_sentence=text_unit.is_sentence())
                    if matching_piece is not None:
                        if field.detect_limit_unit == DocumentField.DETECT_LIMIT_CHAR:
                            if field.detect_limit_count < units_counted + matching_piece[1]:
                                continue
                        matching_string = matching_piece[0]
                        value = field_detector.get_validated_detected_value(field)
                        hint_name = None
                        if typed_field.requires_value:
                            hint_name = field_detector.extraction_hint or ValueExtractionHint.TAKE_FIRST.name
                            try:
                                value, hint_name = typed_field \
                                    .get_or_extract_value(doc,
                                                          value,
                                                          hint_name,
                                                          matching_string)
                            except Exception as e:
                                raise ValueExtractionFunctionThrownException(
                                    f'Value extraction function has thrown an exception.\n'
                                    f'Document: {doc.name} (#{doc.pk})\n'
                                    f'Value: {value}\n'
                                    f'Extraction hint: {hint_name}\n'
                                    f'Matching string:\n'
                                    f'{matching_string}') from e
                            if value is None:
                                continue

                        annotation_value = typed_field.annotation_value_python_to_json(value)
                        ant = AnnotationDTO(annotation_value=annotation_value,
                                            location_in_doc_start=text_unit.location_start,
                                            location_in_doc_end=text_unit.location_end,
                                            extraction_hint_name=hint_name)

                        if not isinstance(typed_field, MultiValueField):
                            return FieldValueDTO(field_value=ant.annotation_value, annotations=[ant])
                        else:
                            ants.append(ant)
                except Exception as e:
                    raise CaughtErrorWhileApplyingFieldDetector(
                        f'Exception caught while trying to apply field detector.\n'
                        f'Document: {doc.name} (#{doc.pk})\n'
                        f'Field detector: #{field_detector.detector.pk}\n'
                        f'{field_detector.detector.include_regexps}\n'
                        f'Text unit: #{text_unit.pk}\n'
                        f'{text_unit.text[:300]}') from e

            if field.detect_limit_count and field.detect_limit_unit == DocumentField.DETECT_LIMIT_CHAR:
                units_counted += len(text_unit.text)

        if not ants:
            return None

        return FieldValueDTO(
            field_value=typed_field.build_json_field_value_from_json_ant_values([a.annotation_value for a in ants]),
            annotations=ants)


class FieldBasedRegexpsDetectionStrategy(FieldDetectionStrategy):
    code = DocumentField.VD_FIELD_BASED_REGEXPS

    @classmethod
    def has_problems_with_field(cls, field: DocumentField) -> Optional[str]:
        return None

    @classmethod
    def train_document_field_detector_model(cls,
                                            log: ProcessLogger,
                                            field: DocumentField,
                                            train_data_project_ids: Optional[List],
                                            use_only_confirmed_field_values: bool = False) -> Optional[ClassifierModel]:

        return None

    @classmethod
    def detect_field_value(cls,
                           log: ProcessLogger,
                           doc: Document,
                           field: DocumentField,
                           field_code_to_value: Dict[str, Any]) -> Optional[FieldValueDTO]:

        depends_on_fields = field.get_depends_on_codes()
        field_code_to_value = {c: v for c, v in field_code_to_value.items() if c in depends_on_fields}

        if field.stop_words:
            depends_on_full_text = '\n'.join([str(v) for v in field_code_to_value.values()])
            detected_with_stop_words, detected_value \
                = detect_with_stop_words_by_field_and_full_text(field, depends_on_full_text)
            if detected_with_stop_words:
                return FieldValueDTO(field_value=detected_value)

        field_detectors = DocumentFieldDetector.objects.filter(field=field)
        detectors = [DetectorFieldMatcher(d) for d in field_detectors]
        typed_field = TypedField.by(field)  # type: TypedField

        values = list()  # type: List

        for depends_on_value in field_code_to_value.values():
            if not depends_on_value:
                continue
            depends_on_value = str(depends_on_value)
            for field_detector in detectors:  # type: DetectorFieldMatcher
                matching_piece = field_detector.matching_string(depends_on_value, text_is_sentence=False)
                if matching_piece is not None:
                    matching_string = matching_piece[0]
                    value = field_detector.get_validated_detected_value(field)
                    if typed_field.requires_value:
                        hint_name = field_detector.extraction_hint or ValueExtractionHint.TAKE_FIRST.name
                        value, hint_name = typed_field \
                            .get_or_extract_value(doc,
                                                  value,
                                                  hint_name,
                                                  matching_string)
                        if value is None:
                            continue

                    value = typed_field.annotation_value_python_to_json(value)
                    if not isinstance(typed_field, MultiValueField):
                        return FieldValueDTO(field_value=value)
                    else:
                        values.append(value)

        if isinstance(typed_field, MultiValueField):
            return FieldValueDTO(field_value=typed_field.build_json_field_value_from_json_ant_values(values))
        else:
            return None


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
            includes = [i.strip().replace(' ', r'\s{1,100}') for i in includes]
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
