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

from apps.document.field_types import FieldType
from apps.document.fields_detection import field_detection_utils
from apps.document.fields_detection.fields_detection_abstractions import FieldDetectionStrategy, DetectedFieldValue, \
    ProcessLogger
from apps.document.fields_detection.regexps_field_detection import RegexpsOnlyFieldDetectionStrategy
from apps.document.fields_detection.stop_words import detect_with_stop_words_by_field_and_full_text
from apps.document.fields_detection.text_based_ml import SkLearnClassifierModel, encode_category, \
    parse_category, word_position_tokenizer
from apps.document.models import ClassifierModel, DocumentFieldValue, ExternalFieldValue, TextUnit, \
    DocumentField, DocumentType
from apps.document.models import Document
from ..value_extraction_hints import ValueExtractionHint

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def get_user_data(field: DocumentField,
                  project_ids: Optional[List[str]]) -> List[dict]:
    qs_modified_document_ids = field_detection_utils.get_qs_active_modified_document_ids(field,
                                                                                         project_ids)

    qs_finished_document_ids = field_detection_utils.get_qs_finished_document_ids(field.document_type, project_ids)

    document_values = DocumentFieldValue.objects.filter(Q(field=field),
                                                        Q(text_unit__isnull=False),
                                                        Q(document__in=Subquery(qs_modified_document_ids))
                                                        | Q(document__in=Subquery(qs_finished_document_ids)),
                                                        Q(removed_by_user=False)) \
                          .values('created_by', 'text_unit__text', 'value', 'extraction_hint') \
                          .order_by('created_by')[:settings.ML_TRAIN_DATA_SET_GROUP_LEN]

    return list(document_values)


def get_external_field_values(field) -> List[dict]:
    return list(ExternalFieldValue.objects
                .filter(field_id=field.pk)
                .annotate(text_unit__text=F('text_unit_text'))
                .values('text_unit__text', 'value', 'extraction_hint')
                .annotate(created_by=Value(1, output_field=IntegerField()))[:settings.ML_TRAIN_DATA_SET_GROUP_LEN])


def get_train_data_sets(field: DocumentField, project_ids: Optional[List[str]]) \
        -> List[Dict]:
    train_data_sets = []
    user_data = get_user_data(field, project_ids)
    if user_data:
        train_data_sets.append(user_data)
    external_field_values = get_external_field_values(field)
    if external_field_values:
        train_data_sets.append(external_field_values)
    return train_data_sets


def get_no_field_text_units(document_type: DocumentType, text_unit_type: str) -> List[str]:
    return list(
        TextUnit.objects.filter(document__document_type_id=document_type.pk, unit_type=text_unit_type,
                                related_field_values=None)
            .values_list('text', flat=True)[:settings.ML_TRAIN_DATA_SET_GROUP_LEN])


def train_model(field: DocumentField, train_data_sets: List[dict]) -> ClassifierModel:
    df = pd.DataFrame.from_records(train_data_sets.pop(0))
    # add transferred external data
    for train_data in train_data_sets:
        df = df.append(pd.DataFrame.from_records(train_data))

    df['target_name'] = df.apply(lambda row: encode_category(
        field.pk,
        row.value if field.is_choice_field() else None,
        row.extraction_hint), axis=1)

    df['target_index'] = df['target_name'].factorize(sort=True)[0] + 1

    df = df.append([{'text_unit__text': i} for i in get_no_field_text_units(field.document_type, field.text_unit_type)])

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


class TextBasedMLFieldDetectionStrategy(FieldDetectionStrategy):
    code = DocumentField.VD_TEXT_BASED_ML_ONLY

    @classmethod
    def train_document_field_detector_model(cls,
                                            log: ProcessLogger,
                                            field: DocumentField,
                                            train_data_project_ids: Optional[List],
                                            use_only_confirmed_field_values: bool = False,
                                            train_documents: Iterable[Document] = None) -> Optional[ClassifierModel]:
        log.info('Training model for field #{0} ({1})...'
                 .format(field.pk, field.code))

        if train_documents:
            doc_ids = list(train_documents.values_list('id', flat=True)) if hasattr(train_documents, 'values_list') \
                else [doc.id for doc in train_documents]
            train_data = DocumentFieldValue.objects.filter(document_id__in=doc_ids, removed_by_user=False)\
                .values('created_by', 'text_unit__text', 'value', 'extraction_hint')
            train_data_sets = [list(train_data)]
        elif train_data_project_ids and not use_only_confirmed_field_values:
            train_data = DocumentFieldValue.objects \
                .filter(field_id=field.pk,
                        document__project_id__in=train_data_project_ids,
                        removed_by_user=False) \
                .values('created_by', 'text_unit__text', 'value', 'extraction_hint')
            train_data_sets = [list(train_data)]
        else:
            train_data_sets = get_train_data_sets(field, train_data_project_ids)

        if not train_data_sets:
            log.info('Not enough data to train model for document_type #{0} and field #{1}.'
                     .format(field.document_type.pk, field.pk))
            return None

        classifier_model = train_model(field, train_data_sets)
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
                                  field_type_adapter: FieldType,
                                  document: Document,
                                  field: DocumentField,
                                  text_unit: TextUnit) -> Optional[DetectedFieldValue]:
        field_uid, value, hint_name = cls.predict_value(sklearn_model, text_unit)
        if field_uid == field.uid:
            if field_type_adapter.requires_value:
                hint_name = hint_name or ValueExtractionHint.TAKE_FIRST.name
                value, hint_name = field_type_adapter \
                    .get_or_extract_value(document, field, value, hint_name, text_unit.text)
                return DetectedFieldValue(field, value, text_unit, hint_name)
            else:
                return DetectedFieldValue(field, None, text_unit)

        return None

    @classmethod
    def detect_field_values(cls,
                            log: ProcessLogger,
                            doc: Document,
                            field: DocumentField,
                            cached_fields: Dict[str, Any]) -> List[DetectedFieldValue]:

        depends_on_full_text = doc.full_text
        detected_with_stop_words, detected_values = detect_with_stop_words_by_field_and_full_text(field,
                                                                                                  depends_on_full_text)
        if detected_with_stop_words:
            return detected_values or list()

        try:
            classifier_model = ClassifierModel.objects.get(document_field=field)
            sklearn_model = classifier_model.get_trained_model_obj()
            field_type_adapter = field.get_field_type()

            detected_values = list()  # type: List[DetectedFieldValue]

            qs_text_units = TextUnit.objects \
                .filter(document=doc) \
                .filter(unit_type=field.text_unit_type) \
                .order_by('location_start', 'pk')

            for text_unit in qs_text_units.iterator():
                detected_value = cls.predict_and_extract_value(sklearn_model=sklearn_model,
                                                               field_type_adapter=field_type_adapter,
                                                               document=doc,
                                                               field=field,
                                                               text_unit=text_unit)
                if detected_value is None:
                    continue
                detected_values.append(detected_value)
                if not (field_type_adapter.multi_value or field.is_choice_field()):
                    break
            return detected_values

        except ClassifierModel.DoesNotExist as e:
            log.info('Classifier model does not exist for field: {0}'.format(field.code))
            raise e


class RegexpsAndTextBasedMLFieldDetectionStrategy(TextBasedMLFieldDetectionStrategy):
    code = DocumentField.VD_REGEXPS_AND_TEXT_BASED_ML

    @classmethod
    def uses_cached_document_field_values(cls, field):
        return True

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
                                                               use_only_confirmed_field_values,
                                                               train_documents)
        except RuntimeError as e:
            return None

    @classmethod
    def detect_field_values(cls,
                            log: ProcessLogger,
                            doc: Document,
                            field: DocumentField,
                            cached_fields: Dict[str, Any]) -> List[DetectedFieldValue]:
        try:
            return super().detect_field_values(log, doc, field, cached_fields)
        except ClassifierModel.DoesNotExist:
            return RegexpsOnlyFieldDetectionStrategy.detect_field_values(log, doc, field, cached_fields)
