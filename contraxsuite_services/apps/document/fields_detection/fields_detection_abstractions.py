from typing import Optional, List, Any, Iterable

from apps.common.log_utils import ProcessLogger
from apps.document.models import ClassifierModel, TextUnit
from apps.document.models import DocumentField, Document
from apps.users.models import User


class DetectedFieldValue:
    __slots__ = ['text_unit', 'value', 'hint_name', 'offset_start', 'offset_end', 'field', 'user']

    def __init__(self,
                 field: DocumentField,
                 value: Any,
                 text_unit: Optional[TextUnit] = None,
                 hint_name: Optional[str] = None,
                 offset_start: Optional[int] = None,
                 offset_end: Optional[int] = None,
                 user: User = None) -> None:
        self.text_unit = text_unit
        self.value = value
        self.hint_name = hint_name
        self.offset_start = offset_start
        self.offset_end = offset_end
        self.field = field
        self.user = user
        super().__init__()

    @property
    def python_value(self):
        # Let's duplicate DocumentFieldValue logic here, to get cache_field_values working correctly
        return self.text_unit.text if self.field.is_related_info_field() and self.text_unit else self.value

    @python_value.setter
    def python_value(self, pv):
        self.value = pv

    def get_annotation_start(self):
        return self.text_unit.location_start + (self.offset_start or 0) \
            if self.text_unit and self.text_unit.location_start is not None else None

    def get_annotation_end(self):
        if not self.text_unit or self.text_unit.location_end is None:
            return None
        if self.offset_end:
            return self.text_unit.location_start + self.offset_end
        else:
            return self.text_unit.location_end

    def get_annotation_text(self):
        if not self.text_unit:
            return None
        full_text = self.text_unit.text
        return full_text[self.offset_start or 0: self.offset_end or len(full_text)]


class FieldDetectionStrategy:
    code = 'Unknown'

    @classmethod
    def uses_cached_document_field_values(cls, field):
        return False

    @classmethod
    def train_document_field_detector_model(cls,
                                            log: ProcessLogger,
                                            field: DocumentField,
                                            train_data_project_ids: Optional[List],
                                            use_only_confirmed_field_values: bool = False) -> Optional[ClassifierModel]:
        raise NotImplemented()

    @classmethod
    def detect_field_values(cls,
                            log: ProcessLogger,
                            doc: Document,
                            field: DocumentField) \
            -> Optional[List[DetectedFieldValue]]:
        raise NotImplemented()


class DisabledFieldDetectionStrategy(FieldDetectionStrategy):
    code = DocumentField.VD_DISABLED

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
                            field: DocumentField) -> \
            Optional[List[DetectedFieldValue]]:
        return None
