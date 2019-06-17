from typing import List, Callable

from sklearn.pipeline import Pipeline, FeatureUnion

from .vectorizers import VectorizerStep
from ..field_types import FieldType
from ..models import DocumentField


def wrap_feature_names_with_field_code(feature_names_func: Callable, field_code: str) -> Callable:
    return lambda: ['{0}__{1}'.format(field_code, feature_name) for feature_name in feature_names_func()]


class FieldValueExtractor(VectorizerStep):
    def __init__(self, field_uid, field_type: 'FieldType') -> None:
        super().__init__()
        self.field_uid = field_uid
        self.field_type = field_type

    def transform(self, field_values_dicts: List, *args, **kwargs):
        return [self.field_type.merged_db_value_to_python(fv.get(self.field_uid) if fv else None) for fv in
                field_values_dicts]

    def get_feature_names(self) -> List[str]:
        return ['']


def document_feature_vector_pipeline(feature_vector_fields: List[DocumentField], use_field_codes:bool = False) \
        -> FeatureUnion:
    transformer_list = []
    for field in sorted(feature_vector_fields, key=lambda f: f.pk):  # type: DocumentField
        field_type = field.get_field_type()  # type: FieldType

        field_vect_steps = [('sel', FieldValueExtractor(field.code if use_field_codes else field.pk, field_type))]

        field_vect_pipeline, _field_feature_names_func = field_type.build_vectorization_pipeline()

        field_vect_steps.extend(field_vect_pipeline)

        transformer_list.append((field.code, Pipeline(field_vect_steps)))

    return FeatureUnion(transformer_list)
