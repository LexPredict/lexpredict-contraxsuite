from typing import Optional, List, Iterable, Dict, Any

from apps.document.fields_detection.fields_detection_abstractions import DetectedFieldValue, \
    ProcessLogger
from apps.document.fields_detection.formula_based_field_detection import FormulaBasedFieldDetectionStrategy
from apps.document.models import ClassifierModel
from apps.document.models import DocumentField, Document
from .field_based_ml_field_detection import FieldBasedMLOnlyFieldDetectionStrategy


class FormulaAndFieldBasedMLFieldDetectionStrategy(FieldBasedMLOnlyFieldDetectionStrategy):
    code = DocumentField.VD_FORMULA_AND_FIELD_BASED_ML

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
        try:
            return super().train_document_field_detector_model(log,
                                                               field,
                                                               train_data_project_ids,
                                                               use_only_confirmed_field_values,
                                                               train_documents)
        except RuntimeError as e:
            return None

    @classmethod
    def detect_field_values(cls,
                            log: ProcessLogger,
                            doc: Document,
                            field: DocumentField,
                            cached_fields: Dict[str, Any]) -> List[DetectedFieldValue]:
        try:
            return super().detect_field_values(log, doc, field)
        except ClassifierModel.DoesNotExist:
            return FormulaBasedFieldDetectionStrategy.detect_field_values(log, doc, field)
