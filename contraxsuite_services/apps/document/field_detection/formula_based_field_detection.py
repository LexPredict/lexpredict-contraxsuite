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

import sys
import traceback
from typing import Optional, List, Dict, Any, Iterable

from apps.common.log_utils import ProcessLogger
from apps.common.script_utils import eval_script, ScriptError
from apps.document.field_detection.fields_detection_abstractions import FieldDetectionStrategy
from apps.document.field_detection.stop_words import detect_with_stop_words_by_field_and_full_text
from apps.document.field_types import TypedField
from apps.document.models import ClassifierModel
from apps.document.models import DocumentField, Document
from apps.document.repository.dto import FieldValueDTO

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DocumentFieldFormulaError(RuntimeError):
    def __init__(self, field_code, formula, field_values):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        self.base_error = exc_obj
        self.line_number = traceback.extract_tb(exc_tb)[-1].lineno
        self.field_values = field_values
        self.field_code = field_code
        msg = f'{exc_type.__name__} in formula of Document Field \'{field_code}\'\n' \
              f'{self.base_error}' \
              f'Formula:\n{formula}\n' \
              f'At line: {self.line_number}\n' \
              f'Field values:\n{field_values}'
        super(RuntimeError, self).__init__(msg)


class FormulaBasedFieldDetectionStrategy(FieldDetectionStrategy):
    code = DocumentField.VD_USE_FORMULA_ONLY

    @classmethod
    def has_problems_with_field(cls, field: DocumentField) -> Optional[str]:
        return None if field.formula else 'Formula-based field detection strategy requires field to have the formula.'

    @classmethod
    def train_document_field_detector_model(cls,
                                            log: ProcessLogger,
                                            field: DocumentField,
                                            train_data_project_ids: Optional[List],
                                            use_only_confirmed_field_values: bool = False,
                                            split_and_log_out_of_sample_test_report: bool = False) -> Optional[ClassifierModel]:
        return None

    @classmethod
    def calc_formula(cls,
                     field_code: str,
                     formula: str,
                     depends_on_field_to_value: Dict[str, Any]) -> Any:
        if not formula or not formula.strip():
            return None

        try:
            return eval_script(script_title=f'{field_code} formula',
                               script_code=formula,
                               eval_locals=depends_on_field_to_value)
        except ScriptError as se:
            raise DocumentFieldFormulaError(field_code, formula, depends_on_field_to_value) from se

    @classmethod
    def detect_field_value(cls,
                           log: ProcessLogger,
                           doc: Document,
                           field: DocumentField,
                           field_code_to_value: Dict[str, Any]) -> FieldValueDTO:
        formula = field.formula

        if not formula:
            raise ValueError(f'No formula specified for field {field.code} (#{field.uid})')

        depends_on_field_codes = field.get_depends_on_codes() or set()

        field_code_to_value = {c: v for c, v in field_code_to_value.items() if c in depends_on_field_codes}

        if field.stop_words:
            depends_on_full_text = '\n'.join([str(v) for v in field_code_to_value.values()])
            log.debug('detect_field_value: formula_based_field_detection, checking stop words, ' +
                      f'field {field.code}({field.pk}), document #{doc.pk}')
            detected_with_stop_words, detected_values \
                = detect_with_stop_words_by_field_and_full_text(field,
                                                                depends_on_full_text)
            if detected_with_stop_words:
                return detected_values or list()
        else:
            log.debug('detect_field_value: formula_based_field_detection, ' +
                      f'field {field.code}({field.pk}), document #{doc.pk}')

        v = cls.calc_formula(field_code=field.code, formula=formula, depends_on_field_to_value=field_code_to_value)
        typed_field = TypedField.by(field)

        # We don't accept formulas returning values of wrong type to avoid further confusion and
        # creating wrong formulas in future.
        # For example for multi-choice fields the formula should return a list and not a string
        # to ensure the admin understands that this value will replace the whole set/list of strings and not
        # just add one more string to the value.
        if typed_field.is_choice_field and typed_field.multi_value:
            if v and isinstance(v, str):
                # "outdated" formula is incorrect and returns string instead of
                # set / list, but we don't warn user: when he updates this formula
                # (or other detection method) he'll be forced to write code, returning
                # list or set.
                v = [v]

        if not typed_field.is_python_field_value_ok(v):
            raise ValueError(f'Formula of field {field.code} returned value not suitable for this field:\n{v}')
        v = typed_field.field_value_python_to_json(v)
        return FieldValueDTO(field_value=v)
