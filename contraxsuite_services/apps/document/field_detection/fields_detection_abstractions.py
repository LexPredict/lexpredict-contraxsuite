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

from typing import Optional, List, Any, Dict

from apps.document.repository.dto import FieldValueDTO

from apps.common.log_utils import ProcessLogger
from apps.document.models import ClassifierModel, TextUnit
from apps.document.models import DocumentField, Document

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
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
                                            use_only_confirmed_field_values: bool = False) -> Optional[ClassifierModel]:
        raise NotImplementedError()

    @classmethod
    def detect_field_value(cls,
                           log: ProcessLogger,
                           doc: Document,
                           field: DocumentField,
                           field_code_to_value: Dict[str, Any]) -> Optional[FieldValueDTO]:
        raise NotImplementedError()

    @classmethod
    def update_units_counted(cls,
                             field: DocumentField,
                             units_counted: int,
                             text_unit: TextUnit) -> int:
        if field.detect_limit_count:
            if field.detect_limit_unit == DocumentField.DETECT_LIMIT_UNIT:
                units_counted += 1
            elif field.detect_limit_unit == DocumentField.DETECT_LIMIT_PARAGRAPH \
                    and text_unit.unit_type == TextUnit.UNIT_TYPE_PARAGRAPH:
                units_counted += 1
            elif field.detect_limit_unit == DocumentField.DETECT_LIMIT_SENTENCE \
                    and text_unit.unit_type == TextUnit.UNIT_TYPE_SENTENCE:
                units_counted += 1

        return units_counted


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
                                            use_only_confirmed_field_values: bool = False) -> Optional[ClassifierModel]:
        return None

    @classmethod
    def detect_field_value(cls,
                           log: ProcessLogger,
                           doc: Document,
                           field: DocumentField,
                           field_code_to_value: Dict[str, Any]) -> Optional[FieldValueDTO]:
        return None
