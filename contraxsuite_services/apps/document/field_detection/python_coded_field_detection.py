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

from typing import Optional, List, Dict, Any

from apps.common.log_utils import ProcessLogger
from apps.document.field_detection.fields_detection_abstractions import FieldDetectionStrategy
from apps.document.field_types import TypedField
from apps.document.models import ClassifierModel
from apps.document.models import DocumentField, Document
from apps.document.python_coded_fields import PythonCodedField
from apps.document.python_coded_fields_registry import PYTHON_CODED_FIELDS_REGISTRY
from apps.document.repository.dto import FieldValueDTO

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class PythonCodedFieldDetectionStrategy(FieldDetectionStrategy):
    code = DocumentField.VD_PYTHON_CODED_FIELD

    @classmethod
    def has_problems_with_field(cls, field: DocumentField) -> Optional[str]:
        if not field.python_coded_field:
            return f'No python coded field class specified for field {field.code}'
        if field.python_coded_field not in PYTHON_CODED_FIELDS_REGISTRY:
            return f'Unknown python coded field {field.python_coded_field}'

    @classmethod
    def train_document_field_detector_model(cls,
                                            log: ProcessLogger,
                                            field: DocumentField,
                                            train_data_project_ids: Optional[List],
                                            use_only_confirmed_field_values: bool = False) -> Optional[ClassifierModel]:
        python_coded_field = PYTHON_CODED_FIELDS_REGISTRY.get(field.python_coded_field)  # type: PythonCodedField
        if not python_coded_field:
            raise RuntimeError('Unknown python-coded field: {0}'.format(field.python_coded_field))

        return python_coded_field.train_document_field_detector_model(field,
                                                                      train_data_project_ids,
                                                                      use_only_confirmed_field_values)

    @classmethod
    def detect_field_value(cls,
                           log: ProcessLogger,
                           doc: Document,
                           field: DocumentField,
                           field_code_to_value: Dict[str, Any]) -> Optional[FieldValueDTO]:
        python_coded_field = PYTHON_CODED_FIELDS_REGISTRY.get(field.python_coded_field)  # type: PythonCodedField
        if not python_coded_field:
            raise RuntimeError('Unknown python-coded field: {0}'.format(field.python_coded_field))
        typed_field = TypedField.by(field)  # type: TypedField

        if python_coded_field.type != typed_field.type_code:
            raise RuntimeError(f'Python-coded field {python_coded_field.__class__.__name__} is '
                               f'for fields of type {python_coded_field.type} and field {field.code} '
                               f'is of type {typed_field.type_code}')

        field_value_dto = python_coded_field.get_value(log=log, field=field, doc=doc,
                                                       cur_field_code_to_value=field_code_to_value)
        if not typed_field.is_json_field_value_ok(field_value_dto.field_value):
            raise ValueError(f'Python coded field class {field.python_coded_field} returned value not suitable for '
                             f'field {field.code} ({typed_field.type_code})')
        return field_value_dto
