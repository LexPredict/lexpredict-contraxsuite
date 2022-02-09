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

from typing import Optional, List, Dict, Tuple, Any

import pandas as pd
from django.conf import settings
from django.db import transaction
from django.db.models import F, Value, IntegerField, Q, Subquery
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.utils import shuffle

from apps.common.log_utils import ProcessLogger
from apps.document.field_detection.field_based_ml_field_detection import init_classifier_impl
from apps.document.field_detection.field_detection_repository import FieldDetectionRepository
from apps.document.field_detection.fields_detection_abstractions import FieldDetectionStrategy
from apps.document.field_detection.text_based_ml import SkLearnClassifierModel, encode_category, \
    parse_category, word_position_tokenizer
from apps.document.field_types import TypedField, MultiValueField
from apps.document.models import ClassifierModel, ExternalFieldValue, TextUnit, DocumentField, DocumentType, \
    Document, FieldAnnotation
from apps.document.repository.dto import FieldValueDTO, AnnotationDTO
from apps.document.repository.text_unit_repository import TextUnitRepository
from apps.document.value_extraction_hints import ValueExtractionHint

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TextBasedMLFieldDetectionStrategy(FieldDetectionStrategy):
    code = DocumentField.VD_TEXT_BASED_ML_ONLY
    text_unit_repo = TextUnitRepository()

    @classmethod
    def has_problems_with_field(cls, field: DocumentField) -> Optional[str]:
        return None

    @classmethod
    def get_user_data(cls, field: DocumentField,
                      project_ids: Optional[List[str]]) -> List[dict]:
        fd_repo = FieldDetectionRepository()
        qs_modified_document_ids = fd_repo.get_qs_active_modified_document_ids(field, project_ids)

        qs_finished_document_ids = fd_repo.get_qs_finished_document_ids(field.document_type, project_ids)
        return FieldAnnotation.objects.filter(Q(field=field),
                                              Q(text_unit__isnull=False),
                                              Q(document__in=Subquery(qs_modified_document_ids))
                                              | Q(document__in=Subquery(qs_finished_document_ids))) \
                   .values('modified_by', 'text_unit__text', 'value', 'extraction_hint') \
                   .order_by('modified_by')[:settings.ML_TRAIN_DATA_SET_GROUP_LEN]

    @classmethod
    def get_external_field_values(cls, field) -> List[dict]:
        return list(ExternalFieldValue.objects
                    .filter(field_id=field.pk)
                    .annotate(text_unit__text=F('text_unit_text'))
                    .values('text_unit__text', 'value', 'extraction_hint')
                    .annotate(created_by=Value(1, output_field=IntegerField()))[:settings.ML_TRAIN_DATA_SET_GROUP_LEN])

    @classmethod
    def get_no_field_text_units(cls, document_type: DocumentType, text_unit_type: str) -> List[str]:
        return list(
            TextUnit.objects.filter(document__document_type_id=document_type.pk, unit_type=text_unit_type,
                                    annotations_matches=None)
                .values_list('text', flat=True)[:settings.ML_TRAIN_DATA_SET_GROUP_LEN])

    @classmethod
    def init_classifier(cls, field: DocumentField):
        init_script = field.classifier_init_script  # type: str

        return init_classifier_impl(field.code, init_script)

    @classmethod
    def train_model(cls, log: ProcessLogger, field: DocumentField, train_data_sets: List[List[dict]],
                    split_and_log_out_of_sample_test_report: bool = False) -> ClassifierModel:
        typed_field = TypedField.by(field)
        df = pd.DataFrame.from_records(train_data_sets.pop(0))
        # add transferred external data
        for train_data in train_data_sets:
            df = df.append(pd.DataFrame.from_records(train_data))

        df['target_name'] = df.apply(lambda row: encode_category(
            field.code,
            row.value if typed_field.is_choice_field else None,
            row.extraction_hint), axis=1)

        df['target_index'] = df['target_name'].factorize(sort=True)[0] + 1

        df = df.append(
            [{'text_unit__text': i} for i in
             cls.get_no_field_text_units(field.document_type, field.text_unit_type)])

        df['target_index'] = df['target_index'].fillna(0).astype('int')
        df['target_name'] = df['target_name'].fillna(SkLearnClassifierModel.EMPTY_CAT_NAME).astype(
            'str')
        df['user_input'] = df['modified_by'].fillna(0).astype('bool')

        res_df = pd.DataFrame()

        for _, group_df in df.groupby('target_index'):
            if group_df.shape[0] > settings.ML_TRAIN_DATA_SET_GROUP_LEN:
                group_df = shuffle(
                    group_df.sort_values('user_input', ascending=False)[:settings.ML_TRAIN_DATA_SET_GROUP_LEN])
            res_df = res_df.append(group_df)
        res_df = shuffle(res_df)

        target_names = sorted(res_df['target_name'].unique())

        if field.classifier_init_script:
            try:
                clf = cls.init_classifier(field)
            except Exception as e:
                log.error(f'Unable to initialize classifier for field {field.code}. '
                          f'Classifier init script: {field.classifier_init_script}', exc_info=e)
            # TODO clf is not defined !!!
        else:
            clf = SGDClassifier(loss='hinge', penalty='l2',
                                alpha=1e-3, max_iter=5, tol=None, n_jobs=-1,
                                class_weight='balanced')

        log.info(f'Classifier initialized: {clf}')

        text_clf = Pipeline([('vect', CountVectorizer(strip_accents='unicode', analyzer='word',
                                                      stop_words='english',
                                                      tokenizer=word_position_tokenizer)),
                             ('tfidf', TfidfTransformer()),
                             ('clf', clf),
                             ])
        x = res_df['text_unit__text']
        y = res_df['target_index']

        if split_and_log_out_of_sample_test_report:
            x_train, x_test_os, y_train, y_test_os = train_test_split(x, y, test_size=0.2, random_state=42)
        else:
            x_train, x_test_os, y_train, y_test_os = x, None, y, None

        sklearn_model = text_clf.fit(x_train, y_train)

        model = SkLearnClassifierModel(sklearn_model=sklearn_model, target_names=target_names)

        classifier_model = ClassifierModel()
        classifier_model.set_trained_model_obj(model)
        classifier_model.document_field = field

        classifier_model.classifier_accuracy_report_in_sample = \
            classification_report(y,
                                  text_clf.predict(x),
                                  target_names=target_names)

        if y_test_os is not None and x_test_os is not None:
            classifier_model.classifier_accuracy_report_out_of_sample = \
                classification_report(y_test_os,
                                      text_clf.predict(x_test_os),
                                      target_names=target_names)

        return classifier_model

    @classmethod
    def get_train_data_sets(cls, field: DocumentField, project_ids: Optional[List[str]]) -> List[List[Dict]]:
        train_data_sets = []
        user_data = cls.get_user_data(field, project_ids)
        if user_data:
            train_data_sets.append(user_data)
        external_field_values = cls.get_external_field_values(field)
        if external_field_values:
            train_data_sets.append(external_field_values)
        return train_data_sets

    @classmethod
    def get_train_datasets_from_projects(cls,
                                         field_id,
                                         train_data_project_ids: Optional[List]) -> List[List[Dict]]:
        train_data = FieldAnnotation.objects \
            .filter(field_id=field_id,
                    document__project_id__in=train_data_project_ids) \
            .values('modified_by', 'text_unit__text', 'value', 'extraction_hint')
        return [list(train_data)]

    @classmethod
    def train_document_field_detector_model(cls,
                                            log: ProcessLogger,
                                            field: DocumentField,
                                            train_data_project_ids: Optional[List],
                                            use_only_confirmed_field_values: bool = False,
                                            split_and_log_out_of_sample_test_report: bool = False) \
            -> Optional[ClassifierModel]:
        log.info(f'Training model for field {field.code} (#{field.pk})...')

        if train_data_project_ids and not use_only_confirmed_field_values:
            train_data_sets = cls.get_train_datasets_from_projects(field.pk, train_data_project_ids)
        else:
            train_data_sets = cls.get_train_data_sets(field, train_data_project_ids)

        if not train_data_sets:
            log.info(
                f'Not enough data to train model for document_type {field.document_type.code}, field: {field.code}.')
            return None

        classifier_model = cls.train_model(log, field, train_data_sets, split_and_log_out_of_sample_test_report)
        log.info(
            f'Finished training model for document_type {field.document_type.code}, field: {field.code}.')

        return classifier_model

    @classmethod
    def predict_value(cls, sklearn_model: SkLearnClassifierModel, text: str) \
            -> Tuple[Optional[str], Optional[str], Optional[str]]:
        predicted = sklearn_model.sklearn_model.predict([text])
        target_index = predicted[0]
        target_name = sklearn_model.target_names[target_index]
        return parse_category(target_name)

    @classmethod
    def predict_and_extract_value(cls, sklearn_model: SkLearnClassifierModel,
                                  typed_field: TypedField,
                                  document: Document,
                                  field: DocumentField,
                                  text: str,
                                  location_start: int,
                                  location_end: int) -> Optional[AnnotationDTO]:
        field_code, value, hint_name = cls.predict_value(sklearn_model, text)
        if field_code == field.code:
            if typed_field.requires_value:
                hint_name = hint_name or ValueExtractionHint.TAKE_FIRST.name
                value, hint_name = typed_field \
                    .get_or_extract_value(document, value, hint_name, text)
                if not typed_field.is_python_annotation_value_ok(value):
                    raise ValueError(f'ML model of field {field.code} ({typed_field.type_code}) returned '
                                     f'annotation value not suitable for this field:\n'
                                     f'{value}')

                annotation_value = typed_field.annotation_value_python_to_json(value)
                return AnnotationDTO(annotation_value=annotation_value,
                                     location_in_doc_start=location_start,
                                     location_in_doc_end=location_end,
                                     extraction_hint_name=hint_name)
            return AnnotationDTO(annotation_value=None,
                                 location_in_doc_start=location_start,
                                 location_in_doc_end=location_end,
                                 extraction_hint_name=None)

    @classmethod
    @transaction.atomic
    def detect_field_value(cls,
                           log: ProcessLogger,
                           doc: Document,
                           field: DocumentField,
                           field_code_to_value: Dict[str, Any]) -> Optional[FieldValueDTO]:

        log.debug('detect_field_value: regexps_and_text_based_ml_field_value, ' +
                  f'field {field.code}({field.pk}), document #{doc.pk}')

        ants: List[AnnotationDTO] = []
        text_unit_repo = cls.text_unit_repo
        typed_field: TypedField = TypedField.by(field)
        qs_text_units = text_unit_repo.get_doc_text_units(doc, field.text_unit_type)

        try:
            classifier_model = ClassifierModel.objects.get(document_field=field)
            sklearn_model = classifier_model.get_trained_model_obj()

            for text_unit in qs_text_units.iterator():  # type: TextUnit
                ant = cls.predict_and_extract_value(sklearn_model=sklearn_model,
                                                    typed_field=typed_field,
                                                    document=doc,
                                                    field=field,
                                                    text=text_unit.text,
                                                    location_start=text_unit.location_start,
                                                    location_end=text_unit.location_end)
                if ant is None:
                    continue
                ants.append(ant)
                if not isinstance(typed_field, MultiValueField):
                    return FieldValueDTO(field_value=ant.annotation_value, annotations=ants)
            if not ants:
                return None

            return FieldValueDTO(field_value=typed_field.build_json_field_value_from_json_ant_values(
                [a.annotation_value for a in ants], doc.pk, field.pk), annotations=ants)

        except ClassifierModel.DoesNotExist as e:
            log.info(f'Classifier model does not exist for field: {field.code}')
            raise e
