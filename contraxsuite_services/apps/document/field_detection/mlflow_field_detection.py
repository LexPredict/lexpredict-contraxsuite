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

import pandas as pd

from apps.common.log_utils import ProcessLogger
from apps.document.field_detection.fields_detection_abstractions import FieldDetectionStrategy
from apps.document.field_types import TypedField, MultiValueField
from apps.document.models import ClassifierModel, DocumentField, Document
from apps.document.repository.dto import FieldValueDTO, AnnotationDTO
from apps.document.repository.text_unit_repository import TextUnitRepository
from apps.document.value_extraction_hints import ValueExtractionHint
from apps.mlflow.mlflow_model_manager import MLFlowModelManager

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class MLFlowModelBasedFieldDetectionStrategy(FieldDetectionStrategy):
    code = DocumentField.VD_MLFLOW_MODEL
    text_unit_repo = TextUnitRepository()

    @classmethod
    def test_model(cls, model_uri: str):
        model_input = {}
        model_input['text'] = 'Hello world!'
        model_input_df = pd.DataFrame([model_input])
        return MLFlowModelManager().predict(model_uri, model_input_df)

    @classmethod
    def has_problems_with_field(cls, field: DocumentField) -> Optional[str]:
        if not field.mlflow_model_uri:
            return f'MLFlow model uri is not set for field {field.code}'
        try:
            output = cls.test_model(field.mlflow_model_uri)
            output = output[0] if output is not None else None
            tf = TypedField.by(field)
            if not tf.is_python_field_value_ok(output):
                return f'MLFlow model returned value which does not match the field type.\n' \
                    f'Returned value (shortened up to 100 chars): {str(output)[:100]}.\n ' \
                    f'Example value: {tf.example_python_value()}.'
            return None
        except Exception as e:
            from apps.common.errors import render_error
            render_error('MLFlow model has thrown exception when testing '
                         '(input = 1-row DataFrame with text = "Hello World")', e)

    @classmethod
    def train_document_field_detector_model(cls,
                                            log: ProcessLogger,
                                            field: DocumentField,
                                            train_data_project_ids: Optional[List],
                                            use_only_confirmed_field_values: bool = False,
                                            split_and_log_out_of_sample_test_report: bool = False)\
            -> Optional[ClassifierModel]:
        return None

    @classmethod
    def detect_field_value(cls,
                           log: ProcessLogger,
                           doc: Document,
                           field: DocumentField,
                           field_code_to_value: Dict[str, Any]) -> Optional[FieldValueDTO]:

        ants: List[AnnotationDTO] = []
        typed_field: TypedField = TypedField.by(field)
        text_unit_repo = cls.text_unit_repo

        if field.mlflow_detect_on_document_level:
            log.debug('detect_field_value: mlflow_field_detection on doc level, ' +
                      f'field {field.code}({field.pk}), document #{doc.pk}')
            text = doc.text
            model_input = dict(field_code_to_value)
            model_input['text'] = text
            model_input_df = pd.DataFrame([model_input])
            model_output = MLFlowModelManager().predict(field.mlflow_model_uri, model_input_df)
            value = model_output[0]
            if not value:
                return None

            hint_name = ValueExtractionHint.TAKE_FIRST.name
            value, hint_name = typed_field \
                .get_or_extract_value(doc, value, hint_name, text)

            if not value:
                return None
            return FieldValueDTO(field_value=value)

        qs_text_units = text_unit_repo.get_doc_text_units(doc, field.text_unit_type)
        log.debug('detect_field_value: mlflow_field_detection on text unit level, ' +
                  f'field {field.code}({field.pk}), document #{doc.pk}')

        for text_unit in qs_text_units.iterator():
            model_input = dict(field_code_to_value)
            model_input['text'] = text_unit.text
            model_input_df = pd.DataFrame([model_input])
            model_output = MLFlowModelManager().predict(field.mlflow_model_uri, model_input_df)
            value = model_output[0]
            if value is None:
                continue
            ant = None

            if typed_field.requires_value:
                # For the field types expecting a value the mlflow model must return either a value or None.
                hint_name = ValueExtractionHint.TAKE_FIRST.name
                value, hint_name = typed_field.get_or_extract_value(doc, value, hint_name, text_unit.text)
                if not typed_field.is_python_annotation_value_ok(value):
                    raise ValueError(f'ML model of field {field.code} ({typed_field.type_code}) returned '
                                     f'annotation value not suitable for this field:\n'
                                     f'{value}')

                annotation_value = typed_field.annotation_value_python_to_json(value)
                ant = AnnotationDTO(annotation_value=annotation_value,
                                    location_in_doc_start=text_unit.location_start,
                                    location_in_doc_end=text_unit.location_end,
                                    extraction_hint_name=hint_name)
            elif value:
                # For the related-info fields the mlflow model must return 0 or 1
                # where 1 means the text unit matches the field.
                ant = AnnotationDTO(annotation_value=None,
                                    location_in_doc_start=text_unit.location_start,
                                    location_in_doc_end=text_unit.location_end,
                                    extraction_hint_name=None)

            if ant is None:
                continue
            ants.append(ant)
            if not isinstance(typed_field, MultiValueField):
                return FieldValueDTO(field_value=ant.annotation_value, annotations=ants)

        if not ants:
            return None

        return FieldValueDTO(field_value=typed_field.build_json_field_value_from_json_ant_values(
            [a.annotation_value for a in ants]), annotations=ants)
