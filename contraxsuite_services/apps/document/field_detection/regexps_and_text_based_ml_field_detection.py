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

from typing import Optional, List, Dict, Tuple, Iterable, Any

import pandas as pd
from django.conf import settings
from django.db.models import F, Value, IntegerField, Q, Subquery
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.utils import shuffle

from apps.common.log_utils import ProcessLogger
from apps.document.field_detection.field_detection_repository import FieldDetectionRepository
from apps.document.field_detection.fields_detection_abstractions import FieldDetectionStrategy
from apps.document.field_detection.regexps_field_detection import RegexpsOnlyFieldDetectionStrategy
from apps.document.field_detection.stop_words import detect_with_stop_words_by_field_and_full_text
from apps.document.field_detection.text_based_ml import SkLearnClassifierModel, encode_category, \
    parse_category, word_position_tokenizer
from apps.document.field_types import TypedField, MultiValueField
from apps.document.models import ClassifierModel, ExternalFieldValue, TextUnit, \
    DocumentField, DocumentType
from apps.document.models import Document, FieldAnnotation
from apps.document.repository.dto import FieldValueDTO, AnnotationDTO
from apps.document.value_extraction_hints import ValueExtractionHint

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.3.0/LICENSE"
__version__ = "1.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TextBasedMLFieldDetectionStrategy(FieldDetectionStrategy):
    code = DocumentField.VD_TEXT_BASED_ML_ONLY

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
                                    related_field_values=None)
                .values_list('text', flat=True)[:settings.ML_TRAIN_DATA_SET_GROUP_LEN])

    @classmethod
    def train_model(cls, field: DocumentField, train_data_sets: List[List[dict]]) -> ClassifierModel:
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
            [{'text_unit__text': i} for i in cls.get_no_field_text_units(field.document_type, field.text_unit_type)])

        df['target_index'] = df['target_index'].fillna(0).astype('int')
        df['target_name'] = df['target_name'].fillna(SkLearnClassifierModel.EMPTY_CAT_NAME).astype(
            'str')
        df['user_input'] = df['created_by'].fillna(0).astype('bool')

        res_df = pd.DataFrame()

        for group_index, group_df in df.groupby('target_index'):
            if group_df.shape[0] > settings.ML_TRAIN_DATA_SET_GROUP_LEN:
                group_df = shuffle(
                    group_df.sort_values('user_input', ascending=False)[:settings.ML_TRAIN_DATA_SET_GROUP_LEN])
            res_df = res_df.append(group_df)
        res_df = shuffle(res_df)

        target_names = sorted(res_df['target_name'].unique())

        text_clf = Pipeline([('vect', CountVectorizer(strip_accents='unicode', analyzer='word',
                                                      stop_words='english',
                                                      tokenizer=word_position_tokenizer)),
                             ('tfidf', TfidfTransformer()),
                             ('clf', SGDClassifier(loss='hinge', penalty='l2',
                                                   alpha=1e-3, max_iter=5, tol=None, n_jobs=-1,
                                                   class_weight='balanced')),
                             ])
        x = res_df['text_unit__text']
        y = res_df['target_index']

        x_train, x_test_os, y_train, y_test_os = train_test_split(x, y, test_size=0.2, random_state=42)
        _x_train, x_test_is, _y_train, y_test_is = train_test_split(x_train, y_train, test_size=0.2, random_state=42)

        sklearn_model = text_clf.fit(x_train, y_train)

        model = SkLearnClassifierModel(sklearn_model=sklearn_model, target_names=target_names)

        classifier_model = ClassifierModel()

        classifier_model.set_trained_model_obj(model)
        classifier_model.document_field = field

        predicted_os = text_clf.predict(x_test_os)
        predicted_is = text_clf.predict(x_test_is)

        classifier_model.classifier_accuracy_report_out_of_sample = classification_report(y_test_os,
                                                                                          predicted_os,
                                                                                          target_names=target_names)
        classifier_model.classifier_accuracy_report_in_sample = classification_report(y_test_is,
                                                                                      predicted_is,
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
                                            use_only_confirmed_field_values: bool = False) -> Optional[ClassifierModel]:
        log.info(f'Training model for field {field.code} (#{field.pk})...')

        if train_data_project_ids and not use_only_confirmed_field_values:
            train_data_sets = cls.get_train_datasets_from_projects(field.pk, train_data_project_ids)
        else:
            train_data_sets = cls.get_train_data_sets(field, train_data_project_ids)

        if not train_data_sets:
            log.info('Not enough data to train model for document_type #{0} and field #{1}.'
                     .format(field.document_type.pk, field.pk))
            return None

        classifier_model = cls.train_model(field, train_data_sets)
        log.info(
            'Finished training model for document_type #{0} and field #{1}.'.format(field.document_type.pk, field.pk))

        return classifier_model

    @classmethod
    def predict_value(cls, sklearn_model: SkLearnClassifierModel, text_unit: TextUnit) \
            -> Tuple[Optional[str], Optional[str], Optional[str]]:
        predicted = sklearn_model.sklearn_model.predict([text_unit.text])
        target_index = predicted[0]
        target_name = sklearn_model.target_names[target_index]
        return parse_category(target_name)

    @classmethod
    def predict_and_extract_value(cls, sklearn_model: SkLearnClassifierModel,
                                  typed_field: TypedField,
                                  document: Document,
                                  field: DocumentField,
                                  text_unit: TextUnit) -> Optional[AnnotationDTO]:
        field_code, value, hint_name = cls.predict_value(sklearn_model, text_unit)
        if field_code == field.code:
            if typed_field.requires_value:
                hint_name = hint_name or ValueExtractionHint.TAKE_FIRST.name
                value, hint_name = typed_field \
                    .get_or_extract_value(document, value, hint_name, text_unit.text)
                if not typed_field.is_python_annotation_value_ok(value):
                    raise ValueError(f'ML model of field {field.code} ({typed_field.type_code}) returned '
                                     f'annotation value not suitable for this field:\n'
                                     f'{value}')

                annotation_value = typed_field.annotation_value_python_to_json(value)
                return AnnotationDTO(annotation_value=annotation_value,
                                     location_in_doc_start=text_unit.location_start,
                                     location_in_doc_end=text_unit.location_end,
                                     extraction_hint_name=hint_name)
            else:
                return AnnotationDTO(annotation_value=None,
                                     location_in_doc_start=text_unit.location_start,
                                     location_in_doc_end=text_unit.location_end,
                                     extraction_hint_name=None)

        return None

    @classmethod
    def detect_field_value(cls,
                           log: ProcessLogger,
                           doc: Document,
                           field: DocumentField,
                           field_code_to_value: Dict[str, Any]) -> Optional[FieldValueDTO]:

        depends_on_full_text = doc.full_text
        detected_with_stop_words, detected_value = detect_with_stop_words_by_field_and_full_text(field,
                                                                                                 depends_on_full_text)
        if detected_with_stop_words:
            return FieldValueDTO(field_value=detected_value)

        try:
            classifier_model = ClassifierModel.objects.get(document_field=field)
            sklearn_model = classifier_model.get_trained_model_obj()
            typed_field = TypedField.by(field)  # type: TypedField

            ants = list()  # type: List[AnnotationDTO]

            qs_text_units = TextUnit.objects \
                .filter(document=doc) \
                .filter(unit_type=field.text_unit_type) \
                .order_by('location_start', 'pk')

            units_counted = 0
            for text_unit in qs_text_units.iterator():
                if field.detect_limit_count:
                    units_counted = FieldDetectionStrategy.update_units_counted(
                        field, units_counted, text_unit)
                    if units_counted > field.detect_limit_count:
                        break

                ant = cls.predict_and_extract_value(sklearn_model=sklearn_model,
                                                    typed_field=typed_field,
                                                    document=doc,
                                                    field=field,
                                                    text_unit=text_unit)
                if ant is None:
                    continue
                if field.detect_limit_count and field.detect_limit_unit == DocumentField.DETECT_LIMIT_CHAR:
                    if ant.location_in_doc_start > field.detect_limit_count:
                        break

                ants.append(ant)
                if not isinstance(typed_field, MultiValueField):
                    return FieldValueDTO(field_value=ant.annotation_value, annotations=ants)

                if field.detect_limit_count and field.detect_limit_unit == DocumentField.DETECT_LIMIT_CHAR:
                    units_counted += len(text_unit.text)

            if not ants:
                return None

            return FieldValueDTO(field_value=typed_field.build_json_field_value_from_json_ant_values([a.annotation_value
                                                                                                      for a in ants]),
                                 annotations=ants)

        except ClassifierModel.DoesNotExist as e:
            log.info(f'Classifier model does not exist for field: {field.code}')
            raise e


class RegexpsAndTextBasedMLFieldDetectionStrategy(TextBasedMLFieldDetectionStrategy):
    code = DocumentField.VD_REGEXPS_AND_TEXT_BASED_ML

    @classmethod
    def train_document_field_detector_model(cls,
                                            log: ProcessLogger,
                                            field: DocumentField,
                                            train_data_project_ids: Optional[List],
                                            use_only_confirmed_field_values: bool = False,
                                            train_documents: Iterable[Document] = None) -> Optional[ClassifierModel]:
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
                           field_code_to_value: Dict[str, Any]) -> Optional[FieldValueDTO]:
        try:
            return super().detect_field_value(log, doc, field, field_code_to_value)
        except ClassifierModel.DoesNotExist:
            return RegexpsOnlyFieldDetectionStrategy.detect_field_value(log, doc, field, field_code_to_value)
