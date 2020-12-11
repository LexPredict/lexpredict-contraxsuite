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

from django.db.models import QuerySet
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union
from apps.common.log_utils import ProcessLogger
from apps.document.repository.dto import FieldValueDTO
from apps.document.models import ClassifierModel, Document, DocumentField, TextUnit

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class FieldDetectionStrategy:
    code = None

    @classmethod
    def has_problems_with_field(cls, field: DocumentField) -> Optional[str]:
        """
        Checks if this field detection strategy has any problems supporting the specified field.
        :param field:
        :return: None if everything is ok or error message if there are problems.
        """
        raise NotImplementedError()

    @classmethod
    def train_document_field_detector_model(cls,
                                            log: ProcessLogger,
                                            field: DocumentField,
                                            train_data_project_ids: Optional[List],
                                            use_only_confirmed_field_values: bool = False,
                                            split_and_log_out_of_sample_test_report: bool = False) \
            -> Optional[ClassifierModel]:
        raise NotImplementedError()

    @classmethod
    def detect_field_value(cls,
                           log: ProcessLogger,
                           doc: Document,
                           field: DocumentField,
                           field_code_to_value: Dict[str, Any]) -> Optional[FieldValueDTO]:
        raise NotImplementedError()

    @classmethod
    def reduce_textunits_by_detection_limit(cls,
                                            text_units: Union[QuerySet, Sequence[TextUnit]],
                                            field: DocumentField) -> Union[QuerySet, Sequence[TextUnit]]:
        """
        Checks if `text_units` are ordered ascendingly by `location_start`.
        If `detect_limit_count` is greater than 0, then `text_units` are sliced at that index and returned.

        Notes:
            1. This deprecates `update_units_counted(...)` and `is_unit_limit_exceeded(...)`.

        Args:
            text_units (Union[QuerySet, Sequence[TextUnit]]):
            field (DocumentField):

        Returns:
            QuerySet[TextUnit] or Sequence[TextUnit]:
                ordered ascendingly by `location_start` with detection limit applied.

        Raises:
            TypeError: if parameter `text_units` is not of type QuerySet[TextUnit] or Sequence[TextUnit].
            ValueError: if parameter `text_units` has not been filtered by `unit_type`.

        Example:

            qs_text_units = reduce_textunits_by_detection_limit(
                qs_text_units=text_unit_repo.get_doc_text_units(doc, field.text_unit_type),
                field=field
            )

        """
        # if field.detect_limit_unit == DocumentField.DETECT_LIMIT_CHAR:
        #     return text_units.filter(location_end__lt=field.detect_limit_count)
        if field.detect_limit_unit != 'NONE':
            if field.detect_limit_count > 0:
                if isinstance(text_units, QuerySet):
                    text_units = text_units.order_by('location_start', 'pk')
                    for child in text_units.query.where.children:
                        lhs = child.__dict__['lhs'].identity
                        if lhs[2][1] == ('document.TextUnit', 'unit_type'):
                            if child.__dict__['rhs'] == field.text_unit_type:
                                return text_units[:field.detect_limit_count]
                    raise ValueError('parameter `text_units`, a QuerySet, has not' +
                                     'been filtered by `unit_type')

                if isinstance(text_units, Sequence):
                    if all(map(lambda tu: tu.unit_type == field.text_unit_type, text_units)):
                        return sorted(
                            text_units,
                            key=lambda tu: (tu.location_start, tu.pk),
                            reverse=False
                        )[:field.detect_limit_count]

                raise TypeError('parameter `text_units` must be of type' +
                                'QuerySet[TextUnit] or Sequence[TextUnit]')
        return text_units


class DisabledFieldDetectionStrategy(FieldDetectionStrategy):
    code = DocumentField.VD_DISABLED

    @classmethod
    def has_problems_with_field(cls, field: DocumentField) -> Optional[str]:
        return None

    @classmethod
    def train_document_field_detector_model(cls,
                                            log: ProcessLogger,
                                            field: DocumentField,
                                            train_data_project_ids: Optional[List],
                                            use_only_confirmed_field_values: bool = False,
                                            split_and_log_out_of_sample_test_report: bool = False) -> Optional[ClassifierModel]:
        return None

    @classmethod
    def detect_field_value(cls,
                           log: ProcessLogger,
                           doc: Document,
                           field: DocumentField,
                           field_code_to_value: Dict[str, Any]) -> Optional[FieldValueDTO]:
        return None
