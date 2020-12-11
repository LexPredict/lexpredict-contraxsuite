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
from typing import Optional, List, Iterable, Dict, Any, Set, Tuple

import chardet
import pandas as pd
import regex as re

from apps.common.log_utils import ProcessLogger
from apps.document.field_types import TypedField, MultiValueField
from apps.document.field_detection.detector_field_matcher import DetectorFieldMatcher
from apps.document.field_detection.fields_detection_abstractions import FieldDetectionStrategy
from apps.document.field_detection.stop_words import detect_with_stop_words_by_field_and_full_text
from apps.document.models import ClassifierModel, TextUnit, DocumentFieldDetector, DocumentField, Document, \
    DocumentFieldMultilineRegexDetector
from apps.document.repository.dto import FieldValueDTO, AnnotationDTO
from apps.document.repository.field_detector_repository import FieldDetectorRepository
from apps.document.repository.text_unit_repository import TextUnitRepository
from apps.document.value_extraction_hints import ValueExtractionHint

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class _CausedException(Exception):
    def __init__(self, message: str, cause: Optional[Exception] = None):
        self._explanation: str
        self.__cause__: Exception = cause
        super().__init__(f'{self._explanation}\n'
                         f'Cause: {self.__cause__.__class__.__name__}\n'
                         f'Reason: {self.__cause__}\n'
                         f'{message}\n')


class ValueExtractionFunctionThrownException(_CausedException):
    def __init__(self, message: str, cause: Optional[Exception] = None):
        self._explanation = f'Value extraction function has thrown an exception.'
        super().__init__(message, cause)


class CaughtErrorWhileApplyingFieldDetector(_CausedException):
    def __init__(self, message: str, cause: Optional[Exception] = None):
        self._explanation = f'Exception caught while trying to apply FieldDetector.'
        super().__init__(message, cause)


class RegexpsOnlyFieldDetectionStrategy(FieldDetectionStrategy):
    code = DocumentField.VD_USE_REGEXPS_ONLY
    text_unit_repo = TextUnitRepository()
    field_detector_repo = FieldDetectorRepository()

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
        try:
            log.debug('detect_field_value: regexps_field_detection, ' +
                      f'field {field.code}({field.pk}), document #{doc.pk}')
        except AttributeError:
            pass

        ants: List[AnnotationDTO] = []
        depends_on_full_text: str = doc.full_text
        typed_field: TypedField = TypedField.by(field)
        text_unit_repo: TextUnitRepository = cls.text_unit_repo
        field_detector_repo: FieldDetectorRepository = cls.field_detector_repo

        detected_with_stop_words, detected_value = \
            detect_with_stop_words_by_field_and_full_text(field, doc, depends_on_full_text)
        if detected_with_stop_words:
            return FieldValueDTO(field_value=detected_value)

        qs_text_units = text_unit_repo.get_doc_text_units(doc, field.text_unit_type)
        qs_text_units = FieldDetectionStrategy.reduce_textunits_by_detection_limit(qs_text_units, field)

        field_detectors = field_detector_repo.get_field_detectors(field)
        detectors = [DetectorFieldMatcher(d) for d in field_detectors]

        for text_unit in qs_text_units:
            unit_ants = cls.extract_from_textunit(text_unit, field, detectors)
            if not unit_ants:
                continue
            if not isinstance(typed_field, MultiValueField):
                return FieldValueDTO(field_value=unit_ants[0].annotation_value, annotations=unit_ants)
            else:
                ants += unit_ants

        if not ants:
            return None

        if isinstance(typed_field, MultiValueField):
            field_value = typed_field.build_json_field_value_from_json_ant_values(
                [a.annotation_value for a in ants])
        else:
            field_value = typed_field.annotation_value_python_to_json(ants[0].annotation_value)
        return FieldValueDTO(field_value=field_value, annotations=ants)

    @classmethod
    def extract_from_textunit(cls,
                              text_unit: TextUnit,
                              field: DocumentField,
                              detectors: List[DetectorFieldMatcher]) -> List[AnnotationDTO]:
        """
        Searches TextUnit text for FieldDetector regex matches.
        Entity extraction, based on the Field type, is run and returned.

        Args:
            text_unit (TextUnit):
            field (DocumentField):
            detectors (List[DetectorFieldMatcher]):

        Returns:
            List[AnnotationDTO]:
        """

        ants = []
        src_text = text_unit.textunittext.text
        typed_field: TypedField = TypedField.by(field)
        for field_detector in detectors:
            try:
                matching_and_location = field_detector.matching_string(src_text, text_unit.is_sentence())
                if matching_and_location is not None:
                    hint_name = None
                    matching_string = matching_and_location[0]
                    value = field_detector.get_validated_detected_value(field)
                    if typed_field.requires_value:
                        hint_name = field_detector.extraction_hint or ValueExtractionHint.TAKE_FIRST.name
                        try:
                            value, hint_name = typed_field.get_or_extract_value(document=text_unit.document,
                                                                                possible_value=value,
                                                                                possible_hint=hint_name,
                                                                                text=matching_string)
                        except Exception as e:
                            raise ValueExtractionFunctionThrownException(
                                f'Document: {text_unit.document.name} (#{text_unit.document.pk})\n'
                                f'TextUnit: {text_unit.unit_type} (#{text_unit.pk})\n'
                                f'Value: {value}\n'
                                f'Extraction hint: {hint_name}\n'
                                f'Matching string:\n'
                                f'{matching_string}', e) from e
                        if value is None:
                            continue

                    annotation_value = typed_field.annotation_value_python_to_json(value)
                    ant = AnnotationDTO(annotation_value=annotation_value,
                                        location_in_doc_start=text_unit.location_start,
                                        location_in_doc_end=text_unit.location_end,
                                        extraction_hint_name=hint_name)

                    if not isinstance(typed_field, MultiValueField):
                        return [ant]
                    else:
                        ants.append(ant)
            except Exception as e:
                if isinstance(e, ValueExtractionFunctionThrownException):
                    raise e
                else:
                    raise CaughtErrorWhileApplyingFieldDetector(
                        f'Document: {text_unit.document.name} (#{text_unit.document.pk})\n'
                        f'TextUnit: {text_unit.unit_type} (#{text_unit.pk})\n'
                        f'Field detector: #{field_detector.detector.pk}\n'
                        f'{field_detector.detector.include_regexps}\n'
                        f'Text: {src_text[:300]}', e) from e
        return ants


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

        depends_on_fields = field.get_depends_on_codes()
        field_code_to_value = {c: v for c, v in field_code_to_value.items() if c in depends_on_fields}

        if field.stop_words:
            depends_on_full_text = '\n'.join([str(v) for v in field_code_to_value.values()])
            detected_with_stop_words, detected_value \
                = detect_with_stop_words_by_field_and_full_text(field, doc, depends_on_full_text)
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
            for detector_field_matcher in detectors:  # type: DetectorFieldMatcher
                matching_piece = detector_field_matcher.matching_string(depends_on_value, text_is_sentence=False)
                if matching_piece is not None:
                    matching_string = matching_piece[0]
                    value = detector_field_matcher.get_validated_detected_value(field)
                    if typed_field.requires_value:
                        hint_name = detector_field_matcher.extraction_hint or ValueExtractionHint.TAKE_FIRST.name
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


class CsvDetectorImporter:
    FD_CATEGORY_IMPORTED_SIMPLE_CONFIG = 'imported_simple_config'
    RE_SPLIT_SEARCH_STR = re.compile(r';|d/b/a')
    SYMBOLS_TO_ESCAPE = ['.', '(', ')', '{', '}', '[', ']', '?']

    def __init__(self,
                 log: ProcessLogger,
                 document_field: DocumentField,
                 drop_previous_field_detectors: bool,
                 update_field_choice_values: bool,
                 csv_contains_regexps: bool = False,
                 selected_columns: Optional[str] = None,
                 wrap_in_wordbreaks: bool = True,
                 save_in_csv_format: bool = True):
        """
        Import CSV records as a number of field detectors
        :param log: logging provider
        :param document_field: field to create detector for, usually a Choice field
        :param csv_contains_regexps: if CSV columns are Regex we don't change their values (e.g. " " for r"\s{1,5}")
        :param drop_previous_field_detectors: delete existing detectors for field "document_field"
        :param update_field_choice_values: make new options for "document_field"
        :param selected_columns: column numbers (starting from 1) or letters to get detected value and search string
        :param wrap_in_wordbreaks: wrap search patterns in \b ... \b special symbols (word break)
        :param save_in_csv_format: save entire CSV as a DocumentFieldMultilineRegexDetector record
        """
        from apps.document.app_vars import CSV_DETECTOR_COMPANIES, CSV_DETECTOR_CONJUNCTIONS
        self.company_abbreviations = CSV_DETECTOR_COMPANIES.val.split(',,')
        self.company_abbreviations = {c.lower() for c in self.company_abbreviations}
        self.conjunctions = CSV_DETECTOR_CONJUNCTIONS.val.split(',,')

        self.log = log
        self.document_field = document_field
        self.drop_previous_field_detectors = drop_previous_field_detectors
        self.update_field_choice_values = update_field_choice_values
        self.csv_contains_regexps = csv_contains_regexps
        self.selected_columns_str = selected_columns
        self.wrap_in_wordbreaks = wrap_in_wordbreaks
        self.save_in_csv_format = save_in_csv_format
        self.value_column = 0
        self.value_suffix_column = None  # type: Optional[int]
        self.columns_to_search = []  # type: List[int]
        self.df = None

    def process_csv(self, csv: bytes) -> None:
        """
        :param csv: comma or semicolon separated text file
        """
        encoding_guess = chardet.detect(csv)
        encoding = encoding_guess.get('encoding') if encoding_guess else None
        encoding = encoding or 'utf-8'

        try:
            self.df = pd.read_csv(io.BytesIO(csv),
                                  index_col=False,
                                  header=None,
                                  skiprows=1,
                                  names=['value', 'pattern'],
                                  dtype={'value': str, 'pattern': str},
                                  encoding=encoding)
        except:
            self.df = pd.read_csv(io.BytesIO(csv),
                                  dtype=str,
                                  encoding=encoding)
        self.get_search_columns()

        if self.df.shape[0] < 1 or self.df.shape[1] < 1:
            raise ValueError('Config csv contains no data')
        if not self.columns_to_search:
            raise ValueError('No columns to search provided')

        row_num = self.df.shape[0]

        self.log.info(f'Creating {row_num} naive field detectors for document field ' +
                      f'{self.document_field} and document type {self.document_field.document_type}...')
        self.log.set_progress_steps_number(int(row_num / 10) + 1)

        # values_by_search_col = {search_value: [value_suffix_strings], [search_strings_formatted]}
        items_by_value = {}  # type: Dict[str, Tuple[Set[str], Set[str]]]
        for index, row in self.df.iterrows():
            if len(row) == 0:
                continue
            field_val = row[self.value_column]
            if not field_val or type(field_val) is not str:
                continue

            value_suffix = row[self.value_suffix_column] if self.value_suffix_column is not None else None
            value_suffix = value_suffix if type(value_suffix) is str else None
            include_reg_cells = list(row[self.columns_to_search])  # type: List[str]
            if not include_reg_cells or not include_reg_cells[0] or type(include_reg_cells[0]) is not str:
                continue
            if not self.csv_contains_regexps:
                include_reg_cells = self.pre_process_regexp_option(include_reg_cells)
            include_reg_cells = [c for c in include_reg_cells if c]
            if not include_reg_cells:
                continue

            if field_val in items_by_value:
                if value_suffix:
                    items_by_value[field_val][0].add(value_suffix or '')
                items_by_value[field_val][1].update(include_reg_cells)
            else:
                items_by_value[field_val] = ({value_suffix or ''}, set(include_reg_cells))
            if index % 10 == 0:
                self.log.step_progress()

        # compose { value: [search strings] } dictionary
        detectors_by_value = {}  # type: Dict[str, List[str]]
        for value_cell in items_by_value:
            value_suffixes, search_values = items_by_value[value_cell]
            if not value_suffixes or None in value_suffixes:
                continue
            value_suffixes_list = list(value_suffixes)
            value_suffixes_list.sort()
            search_values_list = list(search_values)
            search_values_list.sort()

            field_val = self.join_value_with_search_cells(value_cell, value_suffixes_list)
            detectors_by_value[field_val] = search_values_list

        self.save_detector_settings(detectors_by_value)

        if self.update_field_choice_values:
            choices = list(detectors_by_value)
            choices.sort()
            self.document_field.choices = '\n'.join(choices)
            self.document_field.save()

        self.log.info('Done.')

    def save_detector_settings(self, detectors_by_value: Dict[str, List[str]]) -> None:
        # save [all pattern: value] records into DocumentFieldMultilineRegexDetector
        if self.save_in_csv_format:
            self.save_detector_settings_csv(detectors_by_value)
            return

        # save patterns as one or more DocumentFieldDetector records
        # but before (optionally) delete old settings
        if self.drop_previous_field_detectors:
            DocumentFieldDetector.objects.filter(field=self.document_field,
                                                 category=self.FD_CATEGORY_IMPORTED_SIMPLE_CONFIG).delete()
        for field_val in detectors_by_value:
            include_reg_values = detectors_by_value[field_val]

            detector = DocumentFieldDetector()
            detector.category = self.FD_CATEGORY_IMPORTED_SIMPLE_CONFIG
            detector.field = self.document_field
            detector.regexps_pre_process_lower = True
            detector.detected_value = field_val
            detector.include_regexps = '\n'.join(include_reg_values)
            detector.save()

    def save_detector_settings_csv(self, detectors_by_value: Dict[str, List[str]]) -> None:
        detector = DocumentFieldMultilineRegexDetector()
        detector.document_field = self.document_field
        df = pd.DataFrame(columns=['value', 'pattern'])
        df.set_index("pattern", inplace=True)
        for field_val in detectors_by_value:
            for include_reg_value in detectors_by_value[field_val]:
                df = df.append({
                    'value': field_val,
                    'pattern': include_reg_value
                }, ignore_index=True)
        df.drop_duplicates(subset='pattern', inplace=True)

        try:
            existing = DocumentFieldMultilineRegexDetector.objects.get(
                document_field_id=self.document_field.uid)  # type: DocumentFieldMultilineRegexDetector
        except DocumentFieldMultilineRegexDetector.DoesNotExist:
            detector.csv_content = df.to_csv()
            detector.update_checksum()
            detector.save()
            return

        # just update CSV content and hashsum
        if self.drop_previous_field_detectors:
            existing.csv_content = df.to_csv()
            existing.update_checksum()
            existing.save()
            return

        # join these options with existing one
        # overwriting duplicates by detected_value or regexp pattern
        existing.combine_with_dataframe(df)
        existing.save()

    @classmethod
    def join_value_with_search_cells(cls, fval: str, include_reg_cells: Any) -> str:
        suffix_values = []
        for cell in include_reg_cells:  # type: str
            cell_values = cell.split(';')
            for val in cell_values:
                suffix_values.append(val.strip(' \t;'))
        suffix_str = '; '.join([v.strip() for v in suffix_values if v])
        return fval if not suffix_str else f'{fval} ({suffix_str})'

    def get_search_columns(self) -> None:
        if not self.selected_columns_str:
            self.columns_to_search = [i for i in range(self.df.shape[1]) if i != self.value_column]
            return

        value_columns, search_columns = self.get_numbers_from_str()
        self.value_column = value_columns[0]
        if len(value_columns) > 1:
            self.value_suffix_column = value_columns[1]

        self.columns_to_search = search_columns

    def get_numbers_from_str(self) -> Tuple[List[int], List[int]]:
        str_parts = self.selected_columns_str.split(':')
        if len(str_parts) != 2:
            raise RuntimeError('Selected columns field should contain at least two parts ' +
                               'separated by ":" ("A: B" or "2, 1: 1" or "B, C: D, E" ...)')
        col_indices = ([], [],)  # type: Tuple[List[int], List[int]]
        for i in range(2):
            for col_str in re.findall(r'\d+', str_parts[i]):
                col_index = int(col_str) - 1
                col_indices[i].append(col_index)
            if not col_indices[i]:
                search_str = str_parts[i].lower()
                start_order = ord('a')
                for col_str in re.findall(r'[a-z]{1,1}', search_str):
                    col_index = ord(col_str) - start_order
                    col_indices[i].append(col_index)

        errors = []
        if not col_indices[0]:
            errors.append('Selected columns field: left part of ":" (value columns) should ' +
                          'contain at least one number or letter')
        if len(col_indices[0]) > 2:
            errors.append('Selected columns field: left part of ":" (value columns) should ' +
                          'contain one or two values')
        if not col_indices[1]:
            errors.append('Selected columns field: right part of ":" (search columns) should ' +
                          'contain at least one number or letter')
        if errors:
            raise RuntimeError('\n'.join(errors))

        return col_indices

    def pre_process_regexp_option(self, source_choices: List[str]) -> List[str]:
        """
        Split choice option and / or replace
        "the", "and", "&" with ".{1,5}",
        also remove company type (like LLC ...)
        :param source_choices: ["Joe Smith Archives, LLC d/b/a Foxtrot (085292)", ... ]
        :return: one ore more choices
        """
        search_items = []
        # Change "the", "and", "&" for ".{1,5}"
        # remove company type (like LLC ...)
        reg_token = re.compile(r'''[a-zA-Z\.0-9_\-"']+|[()0-9]+|&''')
        for source_choice in source_choices:
            if not source_choice:
                continue
            for choice_opt in self.RE_SPLIT_SEARCH_STR.split(source_choice):
                choice_opt = choice_opt.strip(' \t,')
                tokens = [m.group().strip('.') for m in reg_token.finditer(choice_opt)]
                # remove company abbreviations
                # tokens = [t for t in tokens if t not in self.company_abbreviations]
                # to lower case
                tokens = [t.lower() for t in tokens]
                # escape spec symbols
                escaped_tokens = []
                for token in tokens:
                    for esc_smb in self.SYMBOLS_TO_ESCAPE:
                        token = token.replace(esc_smb, '\\' + esc_smb)
                    escaped_tokens.append(token)
                tokens = escaped_tokens

                # replace conjunctions and merge
                space_token = r'\s{1,5}'
                tokens_separated = []  # type: List[str]
                for i in range(len(tokens)):
                    t = tokens[i]
                    is_conj = t in self.conjunctions
                    is_abbr = t in self.company_abbreviations
                    if is_conj or is_abbr:
                        # remove previous separator
                        if tokens_separated and tokens_separated[-1] == space_token:
                            tokens_separated = tokens_separated[:-1]
                        # "Wholsale, Inc. " -> gives len(Inc) + 4 extra symbols (, . )
                        # while a conjunction produces len(<conjunction>) + 3 extra symbols
                        len_extra = 2 if is_conj else 4
                        word_break = r'(\b|,)' if is_abbr else r'\b'
                        tokens_separated.append(f'{word_break}.{{1,{len(t) + len_extra}}}')
                        continue
                    tokens_separated.append(t)
                    if i < len(tokens) - 1:
                        tokens_separated.append(space_token)
                choice_opt = ''.join(tokens_separated)

                if self.wrap_in_wordbreaks:
                    choice_opt = rf'(^|\b|\s){choice_opt}(\b|\s|$)'
                search_items.append(choice_opt)
        return search_items
