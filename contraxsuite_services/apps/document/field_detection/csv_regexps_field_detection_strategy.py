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


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import regex as re
from typing import Optional, List, Iterable, Any, Dict, Tuple, Callable

from apps.common.log_utils import ProcessLogger
from apps.document.field_detection.fields_detection_abstractions import FieldDetectionStrategy
from apps.document.field_types import MultiChoiceField
from apps.document.models import DocumentField, Document, ClassifierModel, DocumentFieldMultilineRegexDetector
from apps.document.repository.dto import FieldValueDTO, AnnotationDTO


class CsvRegexpsDetectionRow:
    def __init__(self,
                 reg_exp: Any = None,
                 value: str = None,
                 detector: DocumentFieldMultilineRegexDetector = None):
        self.reg_exp = reg_exp
        self.value = value
        self.detector = detector

    def find_value(self, text: str) -> Optional[Tuple[str, int, int]]:
        for match in self.reg_exp.finditer(text):
            return self.value, match.start(), match.end()
        return None

    def __repr__(self):
        return f'{self.reg_exp}: "{self.value}"'


class CsvRegexpsDetectionCache:
    PATTERNS_BY_FIELD = {}  # type: Dict[str, Tuple[str, List[CsvRegexpsDetectionRow]]]

    @classmethod
    def get_detectors(cls,
                      field_id: str,
                      log_function: Callable) -> List[CsvRegexpsDetectionRow]:
        detector_hash = cls.get_detector_hash(field_id)
        if not detector_hash:
            return []

        if field_id in cls.PATTERNS_BY_FIELD:
            hashsum, detectors = cls.PATTERNS_BY_FIELD[field_id]
            if hashsum == detector_hash:  # field in DB wasn't changes relatively to the cached record
                return detectors

        detector = cls.get_detector_object(field_id)
        detector_csv = detector.csv_content

        if not detector_csv:
            # data is corrupted: text is empty but hash is not
            # fix it in the DB
            cls.log_error(log_function,
                          field_id,
                          f'CSV checksum should be empty for field #{field_id}. Fixed.')
            detector.update_checksum()
            cls.save_detector_settings(detector)
            cls.PATTERNS_BY_FIELD[field_id] = ('', [],)
            return []

        detectors = cls.build_detectors(detector, log_function)
        cls.PATTERNS_BY_FIELD[field_id] = (detector.csv_checksum, detectors,)
        return detectors

    @classmethod
    def build_detectors(cls,
                        detector: DocumentFieldMultilineRegexDetector,
                        log_function: Callable) -> List[CsvRegexpsDetectionRow]:
        try:
            df = detector.get_as_pandas_df()
        except Exception as e:
            cls.log_error(log_function, f'CSV data is corrupted for field {detector.field_id}', e)
            return []
        if df.shape[0] == 0:
            return []
        if df.shape[1] != 2:
            cls.log_error(log_function, 'CSV data is has wrong number ' +
                          f'of columns ({df.shape[1]}) for field {detector.field_id}')
            return []

        detectors = []  # type: List[CsvRegexpsDetectionRow]
        for i, row in df.iterrows():
            try:
                detected_value = row[0]
                detector_reg_raw = row[1]
                if detector.regexps_pre_process_lower:
                    reg_pattern = re.compile(detector_reg_raw, re.IGNORECASE)
                else:
                    reg_pattern = re.compile(detector_reg_raw)
                detectors.append(CsvRegexpsDetectionRow(reg_pattern, detected_value, detector))
            except Exception as e:
                cls.log_error(log_function,
                              'CSV data is corrupted for field ' +
                              f'{detector.field_id} at line #{i}', e)
        return detectors

    @classmethod
    def log_error(cls,
                  log_function: Callable,
                  msg: str,
                  exception: Any = None) -> None:
        log_function(msg, exception)

    @classmethod
    def get_detector_hash(cls, field_id: str):
        detector_query = DocumentFieldMultilineRegexDetector.objects.filter(document_field__pk=field_id)
        detector_hash = list(detector_query.values_list('csv_checksum', flat=True))
        return (detector_hash[0] if detector_hash else '') or ''

    @classmethod
    def get_detector_object(cls, field_id: str) -> DocumentFieldMultilineRegexDetector:
        detector_query = DocumentFieldMultilineRegexDetector.objects.filter(document_field__pk=field_id)
        return detector_query[0]

    @classmethod
    def save_detector_settings(cls, detector: DocumentFieldMultilineRegexDetector):
        detector.save()


class CsvRegexpsFieldDetectionStrategy(FieldDetectionStrategy):
    code = DocumentField.VD_REGEXP_TABLE
    detecting_cache = CsvRegexpsDetectionCache

    @classmethod
    def has_problems_with_field(cls, field: DocumentField) -> Optional[str]:
        return None

    @classmethod
    def train_document_field_detector_model(cls,
                                            log: ProcessLogger,
                                            field: DocumentField,
                                            train_data_project_ids: Optional[List],
                                            use_only_confirmed_field_values: bool = False,
                                            split_and_log_out_of_sample_test_report: bool = False)\
            -> Optional[ClassifierModel]:

        return None

    @classmethod
    def detect_field_value(cls,
                           log: ProcessLogger,
                           doc: Document,
                           field: DocumentField,
                           field_code_to_value: Dict[str, Any]) -> Optional[FieldValueDTO]:
        log.debug('detect_field_value: csv_regexps_field_detection, ' +
                  f'field {field.code}({field.pk}), document #{doc.pk}')
        detectors = cls.detecting_cache.get_detectors(
            field.pk, lambda msg, er: log.error(msg,
                                                field_code=field.code,
                                                exc_info=er))
        if not detectors:
            return None

        is_multichoice = field.type == MultiChoiceField.type_code
        doc_text = cls.get_document_text(doc)

        annotations = []

        for detector in detectors:
            found_item = detector.find_value(doc_text)
            if not found_item:
                continue

            # TODO: implement reading values from full text (TextParts.FULL.value)
            # as it is done now, or from text units - paragraphs or sentences
            # based on field.text_unit_type - for other detector.text_part options
            """            
            if detector.text_part == TextParts.BEFORE_REGEXP.value:
                return matching_string[:begin], 0, begin
            elif detector.text_part == TextParts.AFTER_REGEXP.value:
                return matching_string[end:], end, len(text)
            elif detector.text_part == TextParts.INSIDE_REGEXP.value:
                return matching_string[begin:end], begin, end
            else:
                return text, 0, len(text)
            """

            # starting position has to be shifted backward by 1 symbol for FE
            ant = AnnotationDTO(annotation_value=found_item[0],
                                location_in_doc_start=max(found_item[1] - 1, 0),
                                location_in_doc_end=found_item[2],
                                extraction_hint_name='')
            if not is_multichoice:
                return FieldValueDTO(field_value=found_item[0], annotations=[ant])
            else:
                annotations.append(ant)

        if annotations:
            f_val = [a.annotation_value for a in annotations]
            return FieldValueDTO(field_value=f_val, annotations=annotations)
        return None

    @classmethod
    def get_document_text(cls, doc: Document) -> str:
        return doc.full_text
