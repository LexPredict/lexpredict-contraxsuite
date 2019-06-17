import sys
import traceback
from typing import Optional, List, Dict, Any, Iterable

from django.conf import settings

from apps.document.fields_detection.fields_detection_abstractions import FieldDetectionStrategy, DetectedFieldValue, \
    ProcessLogger
from apps.document.fields_detection.stop_words import detect_with_stop_words_by_field_and_full_text
from apps.document.fields_processing.field_processing_utils import merge_document_field_values_to_python_value
from apps.document.models import ClassifierModel
from apps.document.models import DocumentField, Document


class DocumentFieldFormulaError(RuntimeError):
    def __init__(self, field_code, formula, field_values):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        self.base_error = exc_obj
        self.line_number = traceback.extract_tb(exc_tb)[-1].lineno
        self.field_values = field_values
        self.field_code = field_code
        msg = '{0} in formula of field \'{1}\'\n' \
              'Formula:' \
              '\n{2}\n' \
              'At line: {3}\n' \
              'Field values:\n' \
              '{4}'.format(exc_type.__name__, field_code, formula, self.line_number, field_values)
        super(RuntimeError, self).__init__(msg)


class FormulaBasedFieldDetectionStrategy(FieldDetectionStrategy):
    code = DocumentField.VD_USE_FORMULA_ONLY

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
    def calc_formula(cls,
                     field_code: str,
                     field_type_code: str,
                     formula: str,
                     depends_on_field_to_value: Dict[str, Any]) -> Any:
        if not formula or not formula.strip():
            return None

        if '__' in formula:
            raise SyntaxError('Formula contains "__" string. This may be unsafe for python eval.')
        eval_locals = dict()
        eval_locals.update(settings.CALCULATED_FIELDS_EVAL_LOCALS)
        eval_locals.update(depends_on_field_to_value)
        try:
            value = eval(formula, {}, eval_locals)
        except:
            raise DocumentFieldFormulaError(field_code, formula, depends_on_field_to_value)
        # value = eval(formula, {'__builtins__': {}}, eval_locals)
        return value

    @classmethod
    def detect_field_values(cls,
                            log: ProcessLogger,
                            doc: Document,
                            field: DocumentField,
                            cached_fields: Dict[str, Any]) -> List[DetectedFieldValue]:
        # This method assumes that field detection already goes in the required order and dependencies of this
        # field are already calculated / detected.

        formula = field.formula

        if not formula:
            raise ValueError('No formula specified for field {0} (#{1})'.format(field.code, field.uid))

        depends_on_fields = list(field.depends_on_fields.all())

        qs_document_field_values = doc.documentfieldvalue_set \
            .filter(removed_by_user=False) \
            .filter(field__in=depends_on_fields)

        field_code_to_value = merge_document_field_values_to_python_value(list(qs_document_field_values))

        field_code_to_value = {f.code: field_code_to_value.get(f.code) for f in depends_on_fields}

        if field.stop_words:
            depends_on_full_text = '\n'.join([str(v) for v in field_code_to_value.values()])
            detected_with_stop_words, detected_values \
                = detect_with_stop_words_by_field_and_full_text(field,
                                                                depends_on_full_text)
            if detected_with_stop_words:
                return detected_values or list()

        v = cls.calc_formula(field.code, field.type, formula, field_code_to_value)
        return [DetectedFieldValue(field, v)]
