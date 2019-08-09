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

from typing import Optional, List, Any, Iterable, Dict

from apps.common.log_utils import ProcessLogger
from apps.document.models import ClassifierModel, TextUnit
from apps.document.models import DocumentField, Document
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


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
        raise NotImplementedError()

    @classmethod
    def detect_field_values(cls,
                            log: ProcessLogger,
                            doc: Document,
                            field: DocumentField,
                            cached_fields: Dict[str, Any]) \
            -> Optional[List[DetectedFieldValue]]:
        raise NotImplementedError()


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
                            field: DocumentField,
                            cached_fields: Dict[str, Any]) -> \
            Optional[List[DetectedFieldValue]]:
        return None
