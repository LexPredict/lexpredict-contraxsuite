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

from typing import List, Optional, Dict, Any, Tuple

from django.contrib.postgres.aggregates.general import StringAgg

from apps.common.log_utils import ProcessLogger
from apps.document import field_types
from apps.document.field_types import TypedField
from apps.document.models import DocumentField, ClassifierModel, Document, TextUnit
from apps.document.repository.dto import FieldValueDTO, AnnotationDTO
from apps.extract.models import CurrencyUsage, DateUsage, PartyUsage

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class PythonCodedField:
    code = ''
    title = ''
    type = ''

    def train_document_field_detector_model(self,
                                            document_field: DocumentField,
                                            train_data_project_ids: List,
                                            use_only_confirmed_field_values: bool = False) -> Optional[ClassifierModel]:
        return None

    def get_value(self, log: ProcessLogger, field: DocumentField, doc: Document,
                  cur_field_code_to_value: Dict[str, Any]) \
            -> Optional[FieldValueDTO]:
        """
        Locates field values in text - either in a sentence or in a whole document text
        (depending on 'by_sentence' flag).
        :param log
        :param field Configured document field
        :param doc: Document in which the location is done
        :param cur_field_code_to_value: Current field values of this document. May contain only the depends-on fields.
        :return: List of tuples: (value, location_start, location_end)
        """
        raise NotImplementedError()


class TextUnitBasedSingleValuePythonCodedField(PythonCodedField):

    def find_value_in_text_unit(self,
                                log: ProcessLogger,
                                field: DocumentField,
                                doc: Document,
                                text_unit: TextUnit) -> Tuple[bool, Any]:
        raise NotImplementedError()

    def get_value(self, log: ProcessLogger, field: DocumentField, doc: Document,
                  cur_field_code_to_value: Dict[str, Any]) \
            -> Optional[FieldValueDTO]:
        typed_field = TypedField.by(field)  # type: TypedField
        if typed_field.multi_value:
            raise Exception(f'Python coded field {self.__class__.__name__} supports only single-value field types and '
                            f'{typed_field.type_code} is multi-value')

        qs_text_units = TextUnit.objects \
            .filter(document=doc) \
            .filter(unit_type=field.text_unit_type) \
            .order_by('location_start', 'pk')

        for text_unit in qs_text_units.iterator():  # type: TextUnit
            found, value = self.find_value_in_text_unit(log, field, doc, text_unit)
            if found:
                value = typed_field.field_value_python_to_json(value)
                ant = AnnotationDTO(annotation_value=value,
                                    location_in_doc_start=text_unit.location_start,
                                    location_in_doc_end=text_unit.location_end)
                return FieldValueDTO(field_value=value, annotations={ant})


class PartiesField(PythonCodedField):
    code = 'generic.Parties'
    title = 'Parties'
    type = field_types.StringField.type_code

    def get_value(self, log, field: DocumentField, doc: Document,
                  cur_field_code_to_value: Dict[str, Any]) -> Optional[FieldValueDTO]:
        v = PartyUsage.objects.filter(text_unit__document_id=doc.id) \
            .aggregate(value=StringAgg('party__name', delimiter=', ', distinct=True))
        value = TypedField.by(field).field_value_python_to_json(v['value'])
        return FieldValueDTO(field_value=value) if v else None


class MaxCurrencyField(PythonCodedField):
    code = 'generic.MaxCurrency'
    title = 'Max Currency'
    type = field_types.MoneyField.type_code
    detect_per_text_unit = False

    def get_value(self, log, field: DocumentField, doc: Document,
                  cur_field_code_to_value: Dict[str, Any]) -> Optional[FieldValueDTO]:
        for v in CurrencyUsage.objects.filter(text_unit__document_id=doc.id) \
                .order_by('-amount') \
                .values('currency', 'amount'):
            v = TypedField.by(field).field_value_python_to_json(v)
            return FieldValueDTO(field_value=v)
        return None


class MinDateField(PythonCodedField):
    code = 'generic.EarliestDate'
    title = 'Earliest Date'
    type = field_types.DateField.type_code
    detect_per_text_unit = False

    def get_value(self, log, field: DocumentField, doc: Document,
                  cur_field_code_to_value: Dict[str, Any]) -> Optional[FieldValueDTO]:
        for v in DateUsage.objects.filter(text_unit__document_id=doc.id) \
                .order_by('date') \
                .values_list('date', flat=True):
            v = TypedField.by(field).field_value_python_to_json(v)
            return FieldValueDTO(field_value=v)
        return None


class MaxDateField(PythonCodedField):
    code = 'generic.LatestDate'
    title = 'Latest Date'
    type = field_types.DateField.type_code
    detect_per_text_unit = False

    def get_value(self, log, field: DocumentField, doc: Document,
                  cur_field_code_to_value: Dict[str, Any]) -> Optional[FieldValueDTO]:
        for v in DateUsage.objects.filter(text_unit__document_id=doc.id) \
                .order_by('-date') \
                .values_list('date', flat=True):
            v = TypedField.by(field).field_value_python_to_json(v)
            return FieldValueDTO(field_value=v)
        return None


PYTHON_CODED_FIELDS = [PartiesField(), MinDateField(), MaxDateField(), MaxCurrencyField()]
