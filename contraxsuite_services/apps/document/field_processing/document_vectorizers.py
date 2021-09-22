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

from typing import List, Callable, Dict, Any

from sklearn.pipeline import Pipeline, FeatureUnion

from apps.document.field_processing.vectorizers import VectorizerStep
from apps.document.field_types import TypedField
from apps.document.models import DocumentField

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def wrap_feature_names_with_field_code(feature_names_func: Callable, field_code: str) -> Callable:
    return lambda: ['{0}__{1}'.format(field_code, feature_name) for feature_name in feature_names_func()]


class FieldValueExtractor(VectorizerStep):
    def __init__(self, field_code) -> None:
        super().__init__()
        self.field_code = field_code

    def transform(self, field_values_dicts: List[Dict[str, Any]], *args, **kwargs):
        return [fv.get(self.field_code) if fv else None for fv in field_values_dicts]

    def get_feature_names(self) -> List[str]:
        return ['']


def document_feature_vector_pipeline(feature_vector_fields: List[DocumentField], use_field_codes: bool = False) \
        -> FeatureUnion:
    transformer_list = []
    for field in sorted(feature_vector_fields, key=lambda f: f.pk):  # type: DocumentField
        typed_field = TypedField.by(field)  # type: TypedField

        field_vect_steps = [('sel', FieldValueExtractor(field.code if use_field_codes else field.pk))]

        field_vect_pipeline, _field_feature_names_func = typed_field.build_vectorization_pipeline()

        field_vect_steps.extend(field_vect_pipeline)

        transformer_list.append((field.code, Pipeline(field_vect_steps)))

    return FeatureUnion(transformer_list)
