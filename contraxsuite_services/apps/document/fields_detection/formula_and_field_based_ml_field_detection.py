import math
import random
from typing import Optional, List, Tuple, Dict, Any

from django.conf import settings
from django.db.models import Q, Subquery
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn import tree

from apps.document.field_types import FIELD_TYPES_REGISTRY, FieldType, ChoiceField
from apps.document.fields_detection import field_detection_utils
from apps.document.fields_detection.fields_detection_abstractions import FieldDetectionStrategy, DetectedFieldValue, \
    ProcessLogger
from apps.document.fields_detection.formula_based_field_detection import FormulaBasedFieldDetectionStrategy
from apps.document.fields_detection.vectorizers import VectorizerStep
from apps.document.models import ClassifierModel
from apps.document.models import DocumentField, Document, DocumentType


class FieldValueExtractor(VectorizerStep):
    def __init__(self, field_uid, field_type: FieldType) -> None:
        super().__init__()
        self.field_uid = field_uid
        self.field_type = field_type

    def transform(self, field_values_dicts: List, *args, **kwargs):
        return [self.field_type.merged_db_value_to_python(fv.get(self.field_uid) if fv else None) for fv in
                field_values_dicts]


class FieldBasedMLOnlyFieldDetectionStrategy(FieldDetectionStrategy):
    code = DocumentField.VD_FIELD_BASED_ML_ONLY

    @classmethod
    def uses_cached_document_field_values(cls, field):
        return True

    @classmethod
    def get_user_data(cls,
                      document_type: DocumentType,
                      field: DocumentField,
                      project_ids: Optional[List[str]]) -> Optional[List[dict]]:
        qs_modified_document_ids = field_detection_utils.get_qs_active_modified_document_ids(document_type,
                                                                                             field,
                                                                                             project_ids)
        qs_finished_document_ids = field_detection_utils.get_qs_finished_document_ids(document_type, project_ids)

        return list(Document.objects
                    .filter(pk__in=Q(Subquery(qs_modified_document_ids))
                                   | Q(Subquery(qs_finished_document_ids)))
                    .values_list('field_values', flat=True)[:settings.ML_TRAIN_DATA_SET_GROUP_LEN])

    @classmethod
    def build_pipeline(cls, depends_on_fields: List[Tuple[str, str, str]]):

        transformer_list = []

        for field_uid, field_code, field_type in sorted(depends_on_fields, key=lambda t: t[1]):
            field_type = FIELD_TYPES_REGISTRY[field_type]  # type: FieldType

            field_vect_steps = [('sel', FieldValueExtractor(field_uid, field_type))]
            field_vect_steps.extend(field_type.build_vectorization_pipeline())
            transformer_list.append((field_code, Pipeline(field_vect_steps)))

        # classifier = SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, max_iter=5, tol=None,
        #                            n_jobs=-1, class_weight='balanced')
        classifier = tree.DecisionTreeClassifier()

        return Pipeline([('vect', FeatureUnion(transformer_list)),
                         ('clf', classifier)])

    @classmethod
    def get_depends_on_uid_code_type(cls, field: DocumentField) -> List[Tuple[str, str, str]]:
        return list(field.depends_on_fields.all().values_list('uid', 'code', 'type'))

    @classmethod
    def remove_empty_fields(cls, depends_on_uid_code_type, train_data):
        uids = {r[0] for r in depends_on_uid_code_type}
        for d in train_data:
            non_zero_uids = set()
            for uid in uids:
                if d.get(uid):
                    non_zero_uids.add(uid)
            uids.difference_update(non_zero_uids)
            if len(uids) == 0:
                break

        return [(uid, code, field_type) for uid, code, field_type in depends_on_uid_code_type if uid not in uids]

    @classmethod
    def train_document_field_detector_model(cls,
                                            log: ProcessLogger,
                                            document_type: DocumentType,
                                            field: DocumentField,
                                            train_data_project_ids: Optional[List],
                                            use_only_confirmed_field_values: bool = False) -> Optional[ClassifierModel]:

        field_type_adapter = FIELD_TYPES_REGISTRY[field.type]  # type: FieldType

        log.set_progress_steps_number(7)
        log.info('Training model for field #{0} ({1})...'.format(field.pk, field.code))

        # Classifier: values of dependencies -> value of this field
        # Field types supported: only choice fields
        if not isinstance(field_type_adapter, ChoiceField):
            raise ValueError('Field-based ML supports only choice fields but field {0} (#{1}) is of type {2}'
                             .format(field.code, field.uid, field_type_adapter.code))
        # Lets find good values of depends-on fields suitable for using as train data.

        if train_data_project_ids and not use_only_confirmed_field_values:
            train_data = list(Document.objects \
                              .filter(project_id__in=train_data_project_ids) \
                              .values_list('field_values', flat=True)[:settings.ML_TRAIN_DATA_SET_GROUP_LEN])
        else:
            train_data = list(cls.get_user_data(document_type, field, train_data_project_ids))

        if not train_data:
            raise RuntimeError('Not enough train data for field {0} (#{1}). '
                               'Need at least {2} approved or changed documents of type {3}.'
                               .format(field.code, field.uid, settings.ML_TRAIN_DATA_SET_GROUP_LEN,
                                       document_type.code))

        depends_on_fields_types = cls.get_depends_on_uid_code_type(field)
        depends_on_fields_types = cls.remove_empty_fields(depends_on_fields_types, train_data)

        pipeline = cls.build_pipeline(depends_on_fields_types)  # type: Pipeline

        categories = sorted([c.strip() for c in field.choices.split('\n')])
        category_names_to_indexes = {c: i for i, c in enumerate(categories)}

        log.step_progress()
        log.info('Collecting feature rows from train and test documents in dict form...')

        #  When tried to use sklearn shuffling something went wrong, leaving manual methods for a while.
        random.shuffle(train_data)

        #  TODO: use sklearn methods for splitting train/test data and shuffling

        test_size = 0.2

        train_feature_data = list()
        train_target_data = list()

        for doc_field_values in train_data:
            field_value = doc_field_values.get(field.uid)
            del doc_field_values[field.uid]

            field_value_idx = category_names_to_indexes.get(field_value) if field_value else None
            if field_value_idx is None:
                field_value_idx = len(categories)

            train_feature_data.append(doc_field_values)
            train_target_data.append(field_value_idx)

        is_index = math.floor(test_size * len(train_data))

        test_oos_feature_data = train_feature_data[:is_index]
        test_oos_target_data = train_target_data[:is_index]

        train_feature_data = train_feature_data[is_index:]
        train_target_data = train_target_data[is_index:]

        test_is_feature_data = train_feature_data[:is_index]
        test_is_target_data = train_target_data[:is_index]

        log.step_progress()
        log.info('Training the model...')
        model = pipeline.fit(train_feature_data, train_target_data)
        log.step_progress()

        log.info('Testing the model...')
        cm = ClassifierModel()
        cm.document_type = document_type
        cm.document_field = field

        predicted_oos = pipeline.predict(test_oos_feature_data)
        cm.classifier_accuracy_report_out_of_sample = classification_report(test_oos_target_data,
                                                                            predicted_oos,
                                                                            target_names=categories)

        predicted_is = pipeline.predict(test_is_feature_data)
        cm.classifier_accuracy_report_in_sample = classification_report(test_is_target_data,
                                                                        predicted_is,
                                                                        target_names=categories)

        log.step_progress()
        log.info('Saving ClassifierModel instance...')

        cm.set_trained_model_obj({'model': model, 'categories': categories})
        log.step_progress()
        log.info('Finished.')
        return cm

    @classmethod
    def detect_field_values(cls,
                            log: ProcessLogger,
                            doc: Document,
                            field: DocumentField) -> List[DetectedFieldValue]:
        # This method assumes that field detection already goes in the required order and dependencies of this
        # field are already calculated / detected.

        document_type = doc.document_type  # type: DocumentType
        try:
            classifier_model = ClassifierModel.objects \
                .get(document_type=document_type, document_field=field)
            obj = classifier_model.get_trained_model_obj()  # type: Dict[str, Any]

            model = obj['model']
            categories = obj['categories']

            predicted = model.predict([doc.field_values])

            target_index = predicted[0]

            target_name = categories[target_index] if 0 <= target_index < len(categories) else None

            dfv = DetectedFieldValue(field, target_name)
            return [dfv]

        except ClassifierModel.DoesNotExist as e:
            raise e


class FormulaAndFieldBasedMLFieldDetectionStrategy(FieldBasedMLOnlyFieldDetectionStrategy):
    code = DocumentField.VD_FORMULA_AND_FIELD_BASED_ML

    @classmethod
    def uses_cached_document_field_values(cls, field):
        return True

    @classmethod
    def train_document_field_detector_model(cls, log: ProcessLogger, document_type: DocumentType, field: DocumentField,
                                            train_data_project_ids: Optional[List],
                                            use_only_confirmed_field_values: bool = False) -> Optional[ClassifierModel]:
        try:
            return super().train_document_field_detector_model(log,
                                                               document_type,
                                                               field,
                                                               train_data_project_ids,
                                                               use_only_confirmed_field_values)
        except RuntimeError as e:
            return None

    @classmethod
    def detect_field_values(cls,
                            log: ProcessLogger,
                            doc: Document,
                            field: DocumentField) -> List[DetectedFieldValue]:
        try:
            return super().detect_field_values(log, doc, field)
        except ClassifierModel.DoesNotExist:
            return FormulaBasedFieldDetectionStrategy.detect_field_values(log, doc, field)
