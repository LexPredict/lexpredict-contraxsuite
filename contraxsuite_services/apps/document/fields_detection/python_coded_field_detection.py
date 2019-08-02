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

from typing import Optional, List, Iterable, Dict, Any

from apps.document.field_types import FieldType
from apps.document.fields_detection.fields_detection_abstractions import FieldDetectionStrategy, DetectedFieldValue, \
    ProcessLogger
from apps.document.models import ClassifierModel, TextUnit
from apps.document.models import DocumentField, Document
from apps.document.python_coded_fields import PythonCodedField
from apps.document.python_coded_fields_registry import PYTHON_CODED_FIELDS_REGISTRY

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class PythonCodedFieldDetectionStrategy(FieldDetectionStrategy):
    code = DocumentField.VD_PYTHON_CODED_FIELD

    @classmethod
    def uses_cached_document_field_values(cls, field: DocumentField):
        python_coded_field = PYTHON_CODED_FIELDS_REGISTRY.get(field.python_coded_field)  # type: PythonCodedField
        if not python_coded_field:
            raise RuntimeError('Unknown python-coded field: {0}'.format(field.python_coded_field))

        return python_coded_field.uses_cached_document_field_values

    @classmethod
    def train_document_field_detector_model(cls,
                                            log: ProcessLogger,
                                            field: DocumentField,
                                            train_data_project_ids: Optional[List],
                                            use_only_confirmed_field_values: bool = False,
                                            train_documents: Iterable[Document] = None) -> Optional[ClassifierModel]:
        python_coded_field = PYTHON_CODED_FIELDS_REGISTRY.get(field.python_coded_field)  # type: PythonCodedField
        if not python_coded_field:
            raise RuntimeError('Unknown python-coded field: {0}'.format(field.python_coded_field))

        return python_coded_field.train_document_field_detector_model(field,
                                                                      train_data_project_ids,
                                                                      use_only_confirmed_field_values,
                                                                      train_documents)

    @classmethod
    def detect_field_values(cls,
                            log: ProcessLogger,
                            doc: Document,
                            field: DocumentField,
                            cached_fields: Dict[str, Any]) -> List[DetectedFieldValue]:
        python_coded_field = PYTHON_CODED_FIELDS_REGISTRY.get(field.python_coded_field)  # type: PythonCodedField
        if not python_coded_field:
            raise RuntimeError('Unknown python-coded field: {0}'.format(field.python_coded_field))
        field_type_adapter = field.get_field_type()  # type: FieldType

        detected_values = list()  # type: List[DetectedFieldValue]
        if python_coded_field.detect_per_text_unit:
            qs_text_units = TextUnit.objects \
                .filter(document=doc) \
                .filter(unit_type=field.text_unit_type) \
                .order_by('location_start', 'pk')

            for text_unit in qs_text_units.iterator():
                for value, location_start, location_end \
                        in python_coded_field.get_values(log, field, doc, text_unit.text) or []:
                    detected_values.append(
                        DetectedFieldValue(field, value, text_unit, None, location_start, location_end))
                    if not (field_type_adapter.multi_value or field.is_choice_field()):
                        return detected_values
        else:
            for value, location_start, location_end \
                    in python_coded_field.get_values(log, field, doc, doc.full_text) or []:
                if field.requires_text_annotations and (location_start is None or location_end is None):
                    raise RuntimeError('Python coded field {0} detected a value in document {1} at '
                                       'undefined location but the field requires text annotation (and location).\n'
                                       'This should not happen. Something is broken.'
                                       .format(field.python_coded_field, doc))
                if location_start is not None and location_end is not None:
                    text_unit = TextUnit.objects.filter(document=doc,
                                                        unit_type=field.text_unit_type,
                                                        location_start__lte=location_start,
                                                        location_end__gte=location_start).first()  # type: TextUnit
                    if not text_unit:
                        raise RuntimeError('Python coded field {0} detected a value in document {1} at '
                                           'location [{2};{3}] but the start of location does not belong to any '
                                           'text unit object in DB.\n'
                                           'This should not happen. Something is broken.'
                                           .format(field.python_coded_field, doc, location_start, location_end))
                    location_length = location_end - location_start
                    location_start = location_start - text_unit.location_start
                    location_end = location_start + location_length
                else:
                    text_unit = None
                    location_start = None
                    location_end = None
                detected_values.append(DetectedFieldValue(field, value, text_unit, None, location_start, location_end))
                if not (field_type_adapter.multi_value or field.is_choice_field()):
                    return detected_values

        return detected_values
