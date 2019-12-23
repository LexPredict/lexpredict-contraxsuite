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
from apps.document.field_detection.formula_based_field_detection import FormulaBasedFieldDetectionStrategy
from apps.document.models import ClassifierModel
from apps.document.repository.dto import FieldValueDTO
from apps.document.models import DocumentField, Document
from apps.document.field_detection.field_based_ml_field_detection import FieldBasedMLOnlyFieldDetectionStrategy

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class FormulaAndFieldBasedMLFieldDetectionStrategy(FieldBasedMLOnlyFieldDetectionStrategy):
    code = DocumentField.VD_FORMULA_AND_FIELD_BASED_ML

    @classmethod
    def train_document_field_detector_model(cls,
                                            log: ProcessLogger,
                                            field: DocumentField,
                                            train_data_project_ids: Optional[List],
                                            use_only_confirmed_field_values: bool = False) -> Optional[ClassifierModel]:
        try:
            return super().train_document_field_detector_model(log,
                                                               field,
                                                               train_data_project_ids,
                                                               use_only_confirmed_field_values)
        except RuntimeError:
            return None

    @classmethod
    def detect_field_value(cls,
                           log: ProcessLogger,
                           doc: Document,
                           field: DocumentField,
                           field_code_to_value: Dict[str, Any]) -> FieldValueDTO:
        try:
            return super().detect_field_value(log, doc, field, field_code_to_value)
        except ClassifierModel.DoesNotExist:
            return FormulaBasedFieldDetectionStrategy.detect_field_value(log, doc, field, field_code_to_value)
