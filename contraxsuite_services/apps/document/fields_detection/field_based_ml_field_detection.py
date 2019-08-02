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

import math
import random
from typing import Optional, List, Tuple, Dict, Any, Callable, Iterable

from django.conf import settings
from django.db.models import Q, Subquery
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline, FeatureUnion

from apps.common.script_utils import eval_script
from apps.document.field_type_registry import FIELD_TYPE_REGISTRY
from apps.document.field_types import FieldType, ChoiceField
from apps.document.fields_detection import field_detection_utils
from apps.document.fields_detection.fields_detection_abstractions import FieldDetectionStrategy, DetectedFieldValue, \
    ProcessLogger
from apps.document.fields_detection.stop_words import detect_with_stop_words_by_field_and_full_text
from apps.document.fields_processing.document_vectorizers import FieldValueExtractor, \
    wrap_feature_names_with_field_code
from apps.document.models import ClassifierModel
from apps.document.models import DocumentField, Document

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def init_classifier_impl(field_code: str, init_script: str):
    if init_script is not None:
        init_script = init_script.strip()

    if not init_script:
        from sklearn import tree as sklearn_tree
        return sklearn_tree.DecisionTreeClassifier()

    from sklearn import tree as sklearn_tree
    from sklearn import neural_network as sklearn_neural_network
    from sklearn import neighbors as sklearn_neighbors
    from sklearn import svm as sklearn_svm
    from sklearn import gaussian_process as sklearn_gaussian_process
    from sklearn.gaussian_process import kernels as sklearn_gaussian_process_kernels
    from sklearn import ensemble as sklearn_ensemble
    from sklearn import naive_bayes as sklearn_naive_bayes
    from sklearn import discriminant_analysis as sklearn_discriminant_analysis
    from sklearn import linear_model as sklearn_linear_model

    eval_locals = {
        'sklearn_linear_model': sklearn_linear_model,
        'sklearn_tree': sklearn_tree,
        'sklearn_neural_network': sklearn_neural_network,
        'sklearn_neighbors': sklearn_neighbors,
        'sklearn_svm': sklearn_svm,
        'sklearn_gaussian_process': sklearn_gaussian_process,
        'sklearn_gaussian_process_kernels': sklearn_gaussian_process_kernels,
        'sklearn_ensemble': sklearn_ensemble,
        'sklearn_naive_bayes': sklearn_naive_bayes,
        'sklearn_discriminant_analysis': sklearn_discriminant_analysis
    }
    return eval_script('classifier init script of field {0}'.format(field_code), init_script, eval_locals)


class FieldBasedMLOnlyFieldDetectionStrategy(FieldDetectionStrategy):
    from apps.rawdb.repository.raw_db_repository import RawDbRepository
    code = DocumentField.VD_FIELD_BASED_ML_ONLY
    FIELD_REPOSITORY = RawDbRepository()

    @classmethod
    def uses_cached_document_field_values(cls, field):
        return True

    @classmethod
    def get_user_data(cls,
                      field: DocumentField,
                      project_ids: Optional[List[str]]) -> Optional[List[dict]]:
        qs_modified_document_ids = field_detection_utils.get_qs_active_modified_document_ids(field,
                                                                                             project_ids)
        qs_finished_document_ids = field_detection_utils.get_qs_finished_document_ids(field.document_type, project_ids)

        return list(Document.objects
                    .filter(pk__in=Q(Subquery(qs_modified_document_ids)) | Q(Subquery(qs_finished_document_ids)))
                    .values_list('field_values', flat=True)[:settings.ML_TRAIN_DATA_SET_GROUP_LEN])

    @classmethod
    def init_classifier(cls, field: DocumentField):
        init_script = field.classifier_init_script  # type: str

        return init_classifier_impl(field.code, init_script)

    @classmethod
    def build_pipeline(cls, field: DocumentField, depends_on_fields: List[Tuple[str, str, str]]) -> Tuple[
        Pipeline, List[str]]:

        transformer_list = []
        feature_names_funcs = []
        for field_uid, field_code, field_type in sorted(depends_on_fields, key=lambda t: t[1]):
            field_type = FIELD_TYPE_REGISTRY[field_type]  # type: FieldType

            field_vect_steps = [('sel', FieldValueExtractor(field_uid, field_type))]

            field_vect_pipeline, field_feature_names_func = field_type.build_vectorization_pipeline()

            field_vect_steps.extend(field_vect_pipeline)

            transformer_list.append((field_code, Pipeline(field_vect_steps)))

            feature_names_funcs.append(wrap_feature_names_with_field_code(field_feature_names_func, field_code))

        classifier = cls.init_classifier(field)

        return Pipeline([('vect', FeatureUnion(transformer_list)),
                         ('clf', classifier)]), feature_names_funcs

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
    def get_categories(cls, field: DocumentField) -> List[str]:
        return sorted(field.get_choice_values())

    @classmethod
    def train_document_field_detector_model(cls,
                                            log: ProcessLogger,
                                            field: DocumentField,
                                            train_data_project_ids: Optional[List],
                                            use_only_confirmed_field_values: bool = False,
                                            train_documents: Iterable[Document] = None) \
            -> Optional[ClassifierModel]:

        field_type_adapter = field.get_field_type()  # type: FieldType

        log.set_progress_steps_number(7)
        log.info('Training model for field #{0} ({1})...'.format(field.pk, field.code))

        # Classifier: values of dependencies -> value of this field
        # Field types supported: only choice fields
        if not isinstance(field_type_adapter, ChoiceField):
            raise ValueError('Field-based ML supports only choice fields but field {0} (#{1}) is of type {2}'
                             .format(field.code, field.uid, field_type_adapter.code))
        # Lets find good values of depends-on fields suitable for using as train data.

        train_data = cls.get_train_values(field, train_data_project_ids, train_documents,
                                          use_only_confirmed_field_values)

        if not train_data:
            raise RuntimeError('Not enough train data for field {0} (#{1}). '
                               'Need at least {2} approved or changed documents of type {3}.'
                               .format(field.code, field.uid, settings.ML_TRAIN_DATA_SET_GROUP_LEN,
                                       field.document_type.code))

        depends_on_fields_types = cls.get_depends_on_uid_code_type(field)
        depends_on_fields_types = cls.remove_empty_fields(depends_on_fields_types, train_data)

        pipeline, feature_names_funcs = cls.build_pipeline(field,
                                                           depends_on_fields_types)  # type: Pipeline, List[Callable]

        categories = cls.get_categories(field)
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

        test_is_feature_data = train_feature_data  # [:is_index]
        test_is_target_data = train_target_data  # [:is_index]

        log.step_progress()
        log.info('Training the model...')
        model = pipeline.fit(train_feature_data, train_target_data)

        log.step_progress()

        log.info('Testing the model...')
        cm = ClassifierModel()
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

        feature_names = []
        for f in feature_names_funcs:
            feature_names.extend(f())

        cm.set_trained_model_obj({'model': model, 'categories': categories, 'feature_names': feature_names})
        log.step_progress()
        log.info('Finished.')
        return cm

    @classmethod
    def get_train_values(cls,
                         field: DocumentField,
                         train_data_project_ids: Optional[List],
                         train_documents: Iterable[Document],
                         use_only_confirmed_field_values: bool) -> List[Dict[str, Any]]:
        repo = FieldBasedMLOnlyFieldDetectionStrategy.FIELD_REPOSITORY
        if train_documents:
            return list(repo.get_documents_field_values_by_uid(train_documents))

        if train_data_project_ids and not use_only_confirmed_field_values:
            return list(repo.get_project_documents_field_values_by_uid(train_data_project_ids,
                                                                settings.ML_TRAIN_DATA_SET_GROUP_LEN,
                                                                field.document_type))
        return list(cls.get_user_data(field, train_data_project_ids))

    @classmethod
    def maybe_detect_with_stop_words(cls,
                                     field: DocumentField,
                                     cached_fields: Dict[str, Any]) -> Optional[List[DetectedFieldValue]]:
        if field.stop_words:
            depends_on_fields = list(field.depends_on_fields.all())
            depends_on_full_text = []

            if not any(cached_fields):
                return None

            for df in depends_on_fields:  # type: DocumentField
                field_type_adapter = FIELD_TYPE_REGISTRY[df.type]  # type: FieldType
                v = field_type_adapter.merged_db_value_to_python(cached_fields.get(df.uid))
                if v:
                    depends_on_full_text.append(str(v))

            detected_with_stop_words, detected_values = \
                detect_with_stop_words_by_field_and_full_text(field, '\n'.join(depends_on_full_text))
            if detected_with_stop_words:
                return detected_values or list()
        return None

    @classmethod
    def detect_field_values(cls,
                            log: ProcessLogger,
                            doc: Document,
                            field: DocumentField,
                            cached_fields: Dict[str, Any]) -> List[DetectedFieldValue]:
        detected_values = cls.maybe_detect_with_stop_words(field, cached_fields)
        if detected_values is not None:
            return detected_values

        try:
            classifier_model = ClassifierModel.objects.get(document_field=field)
            obj = classifier_model.get_trained_model_obj()  # type: Dict[str, Any]

            model = obj['model']
            categories = obj['categories']

            doc_field_vals = cached_fields
            predicted = model.predict([doc_field_vals])

            target_index = predicted[0]

            target_name = categories[target_index] if 0 <= target_index < len(categories) else None

            dfv = DetectedFieldValue(field, target_name)
            return [dfv]

        except ClassifierModel.DoesNotExist as e:
            raise e


class FieldBasedMLWithUnsureCatFieldDetectionStrategy(FieldBasedMLOnlyFieldDetectionStrategy):
    code = DocumentField.VD_FIELD_BASED_WITH_UNSURE_ML_ONLY

    @classmethod
    def get_categories(cls, field: DocumentField) -> List[str]:
        categories = set(field.get_choice_values())
        if field.unsure_choice_value:
            categories.remove(field.unsure_choice_value)
        return sorted(categories)

    @classmethod
    def detect_field_values(cls,
                            log: ProcessLogger,
                            doc: Document,
                            field: DocumentField,
                            cached_fields: Dict[str, Any]) -> List[DetectedFieldValue]:

        # If changing this code make sure you update similar code in notebooks/demo/Train and Debug Decision Tree...

        detected_values = cls.maybe_detect_with_stop_words(field, cached_fields)
        if detected_values is not None:
            return detected_values

        try:
            classifier_model = ClassifierModel.objects.get(document_field=field)
            obj = classifier_model.get_trained_model_obj()  # type: Dict[str, Any]

            model = obj['model']
            categories = obj['categories']

            category_probabilities = model.predict_proba([cached_fields])[0]

            target_index = max(range(len(category_probabilities)), key=category_probabilities.__getitem__)
            target_probability = category_probabilities[target_index]

            predicted_value = categories[target_index] if 0 <= target_index < len(categories) else None

            if predicted_value is None:
                target_name = field.unsure_choice_value
            else:
                threshold = (field.unsure_thresholds_by_value or {}) \
                                .get(predicted_value) or DocumentField.DEFAULT_UNSURE_THRESHOLD

                target_name = predicted_value if target_probability >= threshold else field.unsure_choice_value

            dfv = DetectedFieldValue(field, target_name)
            return [dfv]

        except ClassifierModel.DoesNotExist as e:
            raise e
