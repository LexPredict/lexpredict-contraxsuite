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

import datetime
from typing import Any, List, Optional, Set, Tuple, Generator, Union

import pandas as pd
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from django.db.models import F, Value, IntegerField, QuerySet
from django.db.models import Q, Subquery
from django.utils.timezone import now
from psycopg2 import InterfaceError, OperationalError
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.utils import shuffle

from apps.celery import app
from apps.document.field_types import FIELD_TYPES_REGISTRY, ValueExtractionHint, FieldType
from apps.document.models import DocumentType, Document, DocumentFieldDetector, \
    ClassifierModel, DocumentFieldValue, ExternalFieldValue, TextUnit, DocumentField, \
    DocumentTypeField
from apps.document.parsing.machine_learning import SkLearnClassifierModel, \
    encode_category, parse_category, word_position_tokenizer
from apps.document.python_coded_fields import PythonCodedField, PYTHON_CODED_FIELDS_REGISTRY
from apps.task.models import Task
from apps.task.tasks import BaseTask, ExtendedTask, call_task
from apps.task.utils.task_utils import TaskUtils
from apps.project.models import Project

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.4/LICENSE"
__version__ = "1.1.4"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

MODULE_NAME = __name__


class DetectedFieldValue:
    __slots__ = ['text_unit', 'value', 'hint_name', 'offset_start', 'offset_end']

    def __init__(self,
                 text_unit: TextUnit,
                 value: Any,
                 hint_name: Optional[str] = None,
                 offset_start: Optional[int] = None,
                 offset_end: Optional[int] = None) -> None:
        self.text_unit = text_unit
        self.value = value
        self.hint_name = hint_name
        self.offset_start = offset_start
        self.offset_end = offset_end
        super().__init__()

    def get_annotation_start(self):
        return self.text_unit.location_start + (self.offset_start or 0)

    def get_annotation_end(self):
        if self.offset_end:
            return self.text_unit.location_start + self.offset_end
        else:
            return self.text_unit.location_end

    def get_annotation_text(self):
        full_text = self.text_unit.text
        return full_text[self.offset_start or 0: self.offset_end or len(full_text)]


class DetectFieldValues(BaseTask):
    name = 'Detect Field Values'

    def process(self, document_type: DocumentType = None, document_name: str = None,
                do_not_write=False, drop_classifier_model=False, **kwargs):
        self.log_info("Going to detect document field values based on "
                      "the pre-coded regexps and field values entered by users...")

        document_id = kwargs.get('document_id')
        if document_id:
            self.set_push_steps(1)

            self.run_sub_tasks('Detect Field Values For Single Document',
                               DetectFieldValues.detect_field_values_for_document,
                               [(document_id, False, None)])
            self.push()
            return

        if document_type:
            document_type_pk = document_type['pk'] if isinstance(document_type, dict) else document_type.pk
            self.detect_field_values_for_document_type(
                document_type_pk, document_name, do_not_write, drop_classifier_model)
        else:
            document_type_pks = DocumentType.objects.all().values_list('uid', flat=True)
            for document_type_pk in document_type_pks:
                self.detect_field_values_for_document_type(
                    document_type_pk, document_name, do_not_write, drop_classifier_model)

    def detect_field_values_for_document_type(self, document_type_pk, document_name: str,
                                              do_not_write,
                                              drop_classifier_model):
        self.log_info(
            'Detecting field values for document type: {0}'.format(
                document_type_pk))
        document_type = DocumentType.objects.get(pk=document_type_pk)
        document_fields = document_type.fields
        if not document_fields:
            self.log_info('Can not find any fields assigned to document type: {0}'.format(
                document_type))
            return

        if drop_classifier_model:
            self.log_info(
                'Deleting field values and classifier models for document type: {0}'.format(
                    document_type))
            ClassifierModel.objects.filter(document_type=document_type).delete()

        task_count = 0

        detect_field_values_for_document_args = []
        source_data = []

        if document_name:
            documents_query = Document.objects.filter(document_type=document_type, name=document_name)
        else:
            documents_query = Document.objects.filter(document_type=document_type)

        for doc_id, source, name in documents_query.values_list('id', 'source', 'name'):
            detect_field_values_for_document_args.append((doc_id, do_not_write, None))
            if source:
                source_data.append('{0}/{1}'.format(source, name))
            else:
                source_data.append(name)
            task_count += 1
        else:
            if document_name:
                self.log_info(
                    'Document {0} of type {1} not found'.format(document_name, document_type))

        self.run_sub_tasks('Detect Field Values For Each Document',
                           DetectFieldValues.detect_field_values_for_document,
                           detect_field_values_for_document_args, source_data)
        if task_count == 0:
            self.log_info('No documents in DB for document type: {0}'.format(
                document_type))
        return task_count

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=6000,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3)
    def detect_field_values_for_document(task: ExtendedTask,
                                         document_id,
                                         do_not_write,
                                         field_uid):
        DetectFieldValues._detect_field_values_for_document(task,
                                                            document_id,
                                                            do_not_write,
                                                            field_uid)

    @staticmethod
    def _detect_field_values_for_document(task: ExtendedTask,
                                          document_id,
                                          do_not_write,
                                          field_uid):
        doc = Document.objects.get(pk=document_id)

        if doc.status and not doc.status.is_active:
            task.log_info('Forbidden detecting field values for document with "completed"'
                          ' status, document #{} ({})'.format(document_id, doc.name))
            return

        document_type = doc.document_type
        fields = [DocumentField.objects.get(
            pk=field_uid)] if field_uid \
            else document_type.fields.all()  # type: List[DocumentField]

        sentence_text_units = list(TextUnit.objects.filter(document=doc, unit_type="sentence"))

        detected_counter = 0
        for field in fields:
            # Delete previously detected values
            # to avoid accumulating garbage on each iteration.
            DocumentFieldValue.objects \
                .filter(document=doc,
                        field=field,
                        removed_by_user=False,
                        created_by__isnull=True,
                        modified_by__isnull=True) \
                .delete()

            if field.python_coded_field:
                detected_counter += DetectFieldValues \
                    .detect_field_values_for_python_coded_field(doc, field, sentence_text_units, do_not_write)
            else:
                classifier_model = None
                document_type_field = DocumentTypeField.objects.get(document_type=document_type,
                                                                    document_field=field)

                if not document_type_field.use_regexp_always:
                    try:
                        classifier_model = ClassifierModel.objects \
                            .get(document_type=document_type, document_field=field)
                    except ClassifierModel.DoesNotExist:
                        pass

                if classifier_model:
                    detected_counter += DetectFieldValues \
                        .detect_field_values_with_model(classifier_model, doc, field, sentence_text_units, do_not_write)
                else:
                    detected_counter += DetectFieldValues \
                        .detect_field_values_with_regexps(doc, field, sentence_text_units, do_not_write)

        task.log_info('Detected {0} field values for document #{1} ({2})'.format(
            detected_counter, document_id, doc.name))

    @classmethod
    def predict_value(cls, sklearn_model: SkLearnClassifierModel, text_unit: TextUnit) \
            -> Tuple[Union[str, None], Union[str, None], Union[str, None]]:
        predicted = sklearn_model.sklearn_model.predict([text_unit.text])
        target_index = predicted[0]
        target_name = sklearn_model.target_names[target_index]
        return parse_category(target_name)

    @classmethod
    def extract_value(cls, field_type_adapter: FieldType, document: Document, field: DocumentField, hint_name: str,
                      text_unit: TextUnit) -> Tuple[Any, Optional[str]]:
        if field_type_adapter.value_aware:
            hint_name = hint_name or ValueExtractionHint.TAKE_FIRST.name
            return field_type_adapter.get_or_extract_value(document, field, None, hint_name, text_unit.text)
        return None, None

    @classmethod
    def predict_and_extract_value(cls, sklearn_model: SkLearnClassifierModel,
                                  field_type_adapter: FieldType,
                                  document: Document,
                                  field: DocumentField,
                                  text_unit: TextUnit) -> Tuple[Any, Any]:
        field_uid, value, hint_name = cls.predict_value(sklearn_model, text_unit)
        if field_uid is not None:
            return cls.extract_value(field_type_adapter, document, field, hint_name, text_unit)
        return None, None

    @staticmethod
    def detect_field_values_with_model(classifier_model,
                                       document: Document,
                                       field: DocumentField,
                                       sentence_text_units: List[TextUnit],
                                       do_not_write: bool) -> int:
        sklearn_model = classifier_model.get_trained_model_obj()
        field_type_adapter = FIELD_TYPES_REGISTRY[field.type]

        detected_values = list()  # type: List[DetectedFieldValue]
        for text_unit in sentence_text_units:
            value, hint_name = DetectFieldValues.predict_and_extract_value(sklearn_model=sklearn_model,
                                                                           field_type_adapter=field_type_adapter,
                                                                           document=document,
                                                                           field=field,
                                                                           text_unit=text_unit)
            if value is None:
                continue
            detected_values.append(DetectedFieldValue(text_unit, value, hint_name))
            if not (field_type_adapter.multi_value or field.is_choice_field()):
                break

        return DetectFieldValues.save_detected_values(document, field, field_type_adapter,
                                                      detected_values, do_not_write)

    @staticmethod
    def detect_field_values_for_python_coded_field(document: Document,
                                                   field: DocumentField,
                                                   sentence_text_units: List[TextUnit],
                                                   do_not_write: bool) -> int:
        python_coded_field = PYTHON_CODED_FIELDS_REGISTRY.get(field.python_coded_field)  # type: PythonCodedField
        if not python_coded_field:
            raise RuntimeError('Unknown python-coded field: {0}'.format(field.python_coded_field))
        field_type_adapter = FIELD_TYPES_REGISTRY[field.type]  # type: FieldType

        detected_values = list()  # type: List[DetectedFieldValue]
        if python_coded_field.by_sentence:
            for text_unit in sentence_text_units:
                for value, location_start, location_end in python_coded_field.get_values(text_unit.text) or []:
                    detected_values.append(DetectedFieldValue(text_unit, value, None, location_start, location_end))
                    if not (field_type_adapter.multi_value or field.is_choice_field()):
                        return DetectFieldValues.save_detected_values(document, field, field_type_adapter,
                                                                      detected_values, do_not_write)
        else:
            for value, location_start, location_end in python_coded_field.get_values(document.full_text) or []:
                text_unit = TextUnit.objects.filter(document=document,
                                                    unit_type='sentence',
                                                    location_start__lte=location_start,
                                                    location_end__gte=location_start).first()  # type: TextUnit
                if not text_unit:
                    raise RuntimeError('Python coded field {0} detected a value in document {1} at '
                                       'location [{2};{3}] but the start of location does not belong to any '
                                       'text unit object in DB.\n'
                                       'It can not be. Something is broken.'
                                       .format(field.python_coded_field, document, location_start, location_end))
                location_length = location_end - location_start
                location_start = location_start - text_unit.location_start
                location_end = location_start + location_length
                detected_values.append(DetectedFieldValue(text_unit, value, None, location_start, location_end))
                if not (field_type_adapter.multi_value or field.is_choice_field()):
                    return DetectFieldValues.save_detected_values(document, field, field_type_adapter,
                                                                  detected_values, do_not_write)

        return DetectFieldValues.save_detected_values(document, field, field_type_adapter,
                                                      detected_values, do_not_write)

    @staticmethod
    def save_detected_values(document: Document, field: DocumentField, field_type_adapter: FieldType,
                             detected_values: List[DetectedFieldValue], do_not_write: bool):
        if len(detected_values) == 0:
            return 0

        try:
            if field.is_choice_field() and not field_type_adapter.multi_value:
                values_order = field.get_choice_values()
                for choice_value in values_order:
                    for dv in detected_values:
                        if choice_value == dv.value:
                            if not do_not_write:
                                field_type_adapter.save_value(document,
                                                              field,
                                                              dv.get_annotation_start(),
                                                              dv.get_annotation_end(),
                                                              dv.get_annotation_text(),
                                                              dv.text_unit,
                                                              dv.value,
                                                              user=None,
                                                              allow_overwriting_user_data=False,
                                                              extraction_hint=dv.hint_name)
                            return 1
            else:
                for dv in detected_values:
                    if not do_not_write:
                        field_type_adapter.save_value(document,
                                                      field,
                                                      dv.get_annotation_start(),
                                                      dv.get_annotation_end(),
                                                      dv.get_annotation_text(),
                                                      dv.text_unit,
                                                      dv.value,
                                                      user=None,
                                                      allow_overwriting_user_data=False,
                                                      extraction_hint=dv.hint_name)
                return len(detected_values)
        finally:
            document.cache_field_values()

    @staticmethod
    def detect_field_values_with_regexps(document: Document, field: DocumentField, sentence_text_units: List[TextUnit],
                                         do_not_write: bool) -> int:
        document_type = document.document_type
        field_detectors = DocumentFieldDetector.objects.filter(document_type=document_type,
                                                               field=field)
        field_type_adapter = FIELD_TYPES_REGISTRY.get(field.type)  # type: FieldType

        detected_values = list()  # type: List[DetectedFieldValue]

        for text_unit in sentence_text_units:

            for field_detector in field_detectors:
                if field_detector.matches(text_unit.text):
                    value = field_detector.detected_value
                    hint_name = None
                    if field_type_adapter.value_aware:
                        hint_name = field_detector.extraction_hint or ValueExtractionHint.TAKE_FIRST.name
                        value, hint_name = field_type_adapter \
                            .get_or_extract_value(document,
                                                  field, value,
                                                  hint_name,
                                                  text_unit.text)
                        if value is None:
                            continue

                    detected_values.append(DetectedFieldValue(text_unit, value, hint_name))

                    if not (field_type_adapter.multi_value or field.is_choice_field()):
                        break

        return DetectFieldValues.save_detected_values(document, field, field_type_adapter,
                                                      detected_values, do_not_write)


class TrainDocumentFieldDetectorModel(BaseTask):
    name = 'Train Document Field Detector Model'

    def process(self, **kwargs):
        self.log_info(
            'Going to train field detector model based on the datasets stored in DB...')

        document_type = kwargs.get('document_type')

        if document_type:
            self.train_model_for_document_type(document_type['pk'])
        else:
            document_type_pks = DocumentType.objects.values_list('uid', flat=True)
            for document_type_pk in document_type_pks:
                self.train_model_for_document_type(
                    document_type_pk)

    def train_model_for_document_type(self, document_type_pk: str) -> None:
        self.log_info('Building classifier model for document type: {0}'.format(
            document_type_pk))

        document_type = DocumentType.objects.get(pk=document_type_pk)

        train_model_for_field_args = []

        for field in document_type.fields.all():
            train_model_for_field_args.append((document_type.uid, field.uid))

        self.run_sub_tasks('Train Model For Each Field',
                           TrainDocumentFieldDetectorModel.train_model_for_field,
                           train_model_for_field_args)

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=6000,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3)
    def train_model_for_field(task: ExtendedTask, document_type_uid: str, field_uid: str) -> None:
        document_type_field = DocumentTypeField.objects.get_document_type_field(document_type_uid, field_uid)
        TrainDocumentFieldDetectorModel.train_document_field_detector_model(
            task=task,
            document_type_field=document_type_field,
            train_data_sets=TrainDocumentFieldDetectorModel.get_train_data_sets(document_type_field))

    @classmethod
    def get_user_data(cls,
                      document_type: DocumentType,
                      field: DocumentField,
                      trained_after_documents_number: int = None) -> List[dict]:
        modified_documents = set()
        train_data = list()

        modified_document_ids = DocumentFieldValue.objects \
            .filter(Q(field=field)
                    & Q(sentence__isnull=False)
                    & Q(document__document_type=document_type)
                    & (Q(created_by__isnull=False) | Q(removed_by_user=True))) \
            .values('document_id') \
            .order_by('document_id') \
            .distinct()

        document_values = DocumentFieldValue.objects \
                              .filter(Q(field=field),
                                      Q(document__document_type=document_type),
                                      Q(sentence__isnull=False),
                                      Q(document_id__in=Subquery(modified_document_ids)) | Q(
                                          document__status__is_active=False),
                                      Q(removed_by_user=False)) \
                              .values('document_id', 'created_by', 'sentence__text', 'value', 'extraction_hint') \
                              .order_by('created_by')[:settings.ML_TRAIN_DATA_SET_GROUP_LEN]

        for field_value in document_values:
            train_data.append({
                'created_by': field_value['created_by'],
                'sentence__text': field_value['sentence__text'],
                'value': field_value['value'],
                'extraction_hint': field_value['extraction_hint'],
            })

            modified_documents.add(field_value['document_id'])

        if trained_after_documents_number <= len(modified_documents):
            return train_data

    @classmethod
    def get_external_field_values(cls, field, document_type) -> QuerySet:
        return ExternalFieldValue.objects \
                   .filter(field_id=field.pk,
                           type_id=document_type.pk) \
                   .annotate(sentence__text=F('sentence_text')) \
                   .values('sentence__text', 'value', 'extraction_hint') \
                   .annotate(created_by=Value(1, output_field=IntegerField()))[:settings.ML_TRAIN_DATA_SET_GROUP_LEN]

    @classmethod
    def get_train_data_generator(cls, train_data: List[dict]) -> Generator[dict, None, None]:
        while train_data:
            yield train_data.pop(0)

    @classmethod
    def get_train_data_sets(cls, document_type_field: DocumentTypeField) \
            -> List[Generator[Any, None, None]]:
        document_type = document_type_field.document_type
        field = document_type_field.document_field
        train_data_sets = []
        user_data = cls.get_user_data(document_type, field, document_type_field.trained_after_documents_number)
        if user_data:
            train_data_sets.append(cls.get_train_data_generator(user_data))
        external_field_values = list(cls.get_external_field_values(field, document_type))
        if external_field_values:
            train_data_sets.append(cls.get_train_data_generator(external_field_values))
        return train_data_sets

    @classmethod
    def get_no_field_sentences(cls, document_type: DocumentType) -> List[str]:
        return list(
            TextUnit.objects
                .filter(document__document_type_id=document_type.pk, unit_type='sentence',
                        related_field_values=None)
                .values_list('text', flat=True)[:settings.ML_TRAIN_DATA_SET_GROUP_LEN])

    @classmethod
    def train_model(cls, document_type_field: DocumentTypeField, train_data_sets: List[dict]) -> ClassifierModel:
        document_type = document_type_field.document_type
        field = document_type_field.document_field
        df = pd.DataFrame.from_records(train_data_sets.pop(0))
        # add transferred external data
        for train_data in train_data_sets:
            df = df.append(pd.DataFrame.from_records(train_data))

        total_field_value_samples = df.shape[0]

        df['target_name'] = df.apply(lambda row: encode_category(
            field.pk,
            row.value if field.is_choice_field() else None,
            row.extraction_hint), axis=1)

        df['target_index'] = df.target_name.factorize(sort=True)[0] + 1

        df = df.append([{'sentence__text': i} for i in cls.get_no_field_sentences(document_type)])

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
        total_samples = res_df.shape[0]

        text_clf = Pipeline([('vect', CountVectorizer(strip_accents='unicode', analyzer='word',
                                                      stop_words='english',
                                                      tokenizer=word_position_tokenizer)),
                             ('tfidf', TfidfTransformer()),
                             ('clf', SGDClassifier(loss='hinge', penalty='l2',
                                                   alpha=1e-3, random_state=42,
                                                   max_iter=5, tol=None, n_jobs=-1,
                                                   class_weight='balanced')),
                             ])
        sklearn_model = text_clf.fit(res_df['sentence__text'], res_df['target_index'])

        model = SkLearnClassifierModel(sklearn_model=sklearn_model, target_names=target_names)

        classifier_model, created = ClassifierModel.objects.get_or_create(
            document_type_id=document_type.pk, document_field_id=field.pk)

        classifier_model.set_trained_model_obj(model)
        classifier_model.total_field_value_samples = total_field_value_samples
        classifier_model.total_samples = total_samples
        classifier_model.test_valid_fields_metric = None
        classifier_model.test_wrong_fields_metric = None
        classifier_model.test_sentences_number = None
        classifier_model.test_values_number = None
        classifier_model.predicted_valid_values_number = None
        classifier_model.predicted_wrong_values_number = None
        classifier_model.save()

        return classifier_model

    @classmethod
    def train_document_field_detector_model(cls,
                                            task: ExtendedTask,
                                            document_type_field: DocumentTypeField,
                                            train_data_sets: List[Any],
                                            force=False) -> ClassifierModel:
        document_type = document_type_field.document_type
        field = document_type_field.document_field

        task.log_info('Training model for field #{0} ({1})...'
                      .format(field.pk, field.code))

        if not force and document_type_field.use_regexp_always:
            task.log_info('Regexp will be used for document_type #{0} and field #{1}.'
                          .format(document_type.pk, field.pk))
        elif not train_data_sets:
            task.log_info('Not enough data to train model for document_type #{0} and field #{1}.'
                          .format(document_type.pk, field.pk))
        else:
            classifier_model = cls.train_model(document_type_field, train_data_sets)
            task.log_info(
                'Finished training model for document_type #{0} and field #{1}. '
                'Total number of samples: {2}'.format(document_type.pk, field.pk, classifier_model.total_samples))

            return classifier_model


class TrainDirtyDocumentFieldDetectorModel(BaseTask):
    name = 'Train Dirty Document Field Detector Model'

    def process(self, **kwargs):
        self.log_info(
            'Going to train dirty field detector model based on the datasets stored in DB...')

        dirty_fields = DocumentTypeField.objects.get_dirty_fields()

        if dirty_fields:
            train_model_for_dirty_field_args = []

            for dirty_field in DocumentTypeField.objects.get_dirty_fields():
                train_model_for_dirty_field_args.append((dirty_field.id,))

            self.run_sub_tasks('Train Model For Dirty Fields',
                               TrainDirtyDocumentFieldDetectorModel.train_model_for_dirty_field,
                               train_model_for_dirty_field_args)

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=6000,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3)
    def train_model_for_dirty_field(task: ExtendedTask, dirty_field_id: Any) -> None:
        dirty_field = DocumentTypeField.objects.get(pk=dirty_field_id)
        if dirty_field.can_retrain():
            dirty_field.dirty = False
            dirty_field.save()
            document_type_field = DocumentTypeField.objects.get_document_type_field(dirty_field.document_type_id,
                                                                                    dirty_field.document_field_id)
            train_data_sets = TrainDocumentFieldDetectorModel.get_train_data_sets(document_type_field)
            TrainDocumentFieldDetectorModel \
                .train_document_field_detector_model(task=task,
                                                     document_type_field=document_type_field,
                                                     train_data_sets=train_data_sets)


@app.task(name='advanced_celery.retrain_dirty_fields', bind=True)
def retrain_dirty_fields(self):
    TaskUtils.prepare_task_execution()
    if DocumentTypeField.objects.has_dirty_fields():
        task_name = TrainDirtyDocumentFieldDetectorModel.name
        execution_delay = now() - datetime.timedelta(
            seconds=settings.RETRAINING_TASK_EXECUTION_DELAY_IN_SEC)
        if not Task.objects.filter(name=task_name, own_status='PENDING',
                                   date_start__gt=execution_delay).exists():
            call_task(TrainDirtyDocumentFieldDetectorModel.name, module_name='apps.document.tasks')


class TrainDocumentField(BaseTask):
    name = 'Train Document Field'
    soft_time_limit = 6000
    default_retry_delay = 10
    retry_backoff = True
    autoretry_for = (SoftTimeLimitExceeded, InterfaceError, OperationalError,)
    max_retries = 3

    def process(self, **kwargs):
        self.log_info(
            'Going to train document field based on the datasets stored in DB...')

        document_type_field_id = kwargs.get('document_type_field_id')
        train_data_project_ids = kwargs.get('train_data_project_ids')
        test_data_projects_ids = kwargs.get('test_data_projects_ids')

        document_type_field = DocumentTypeField.objects.get(pk=document_type_field_id)
        document_type = document_type_field.document_type
        field = document_type_field.document_field
        train_data = DocumentFieldValue.objects \
            .filter(field_id=field.pk,
                    document__project_id__in=train_data_project_ids,
                    document__document_type_id=document_type.pk,
                    removed_by_user=False) \
            .values('created_by', 'sentence__text', 'value', 'extraction_hint')
        train_data = TrainDocumentFieldDetectorModel.get_train_data_generator(list(train_data))
        test_document_ids = Document.objects \
            .filter(project_id__in=test_data_projects_ids, document_type_id=document_type.pk) \
            .values_list('pk', flat=True)
        classifier_model = TrainDocumentFieldDetectorModel \
            .train_document_field_detector_model(task=self,
                                                 document_type_field=document_type_field,
                                                 train_data_sets=[train_data],
                                                 force=True)
        test_tasks_args = []
        for test_document_id in test_document_ids:
            test_tasks_args.append((classifier_model.pk, test_document_id))
        if test_tasks_args:
            self.run_sub_tasks('Test Field Detector Model', TrainDocumentField.test_field_detector_model,
                               test_tasks_args)
            self.run_after_sub_tasks_finished('Join Field Detector Model Tests',
                                              TrainDocumentField.join_field_detector_model_tests,
                                              [(classifier_model.pk,)])

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=6000,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3)
    def test_field_detector_model(task: ExtendedTask, classifier_model_id: Any, test_document_id: Any) -> dict:
        classifier_model = ClassifierModel.objects.get(pk=classifier_model_id)
        document = Document.objects.get(pk=test_document_id)
        field = classifier_model.document_field
        sklearn_model = classifier_model.get_trained_model_obj()
        field_type_adapter = FIELD_TYPES_REGISTRY[field.type]
        text_unit_with_value_ids = set()
        able_to_predict_text_units_ids = set()
        sentences_number = 0
        values_number = 0
        valid_values_number = 0
        able_to_predict = 0

        task.log_info(
            'Testing field detector model for document #{0}, field {1}...'.format(test_document_id, field.code))

        for text_unit in TextUnit.objects.filter(document_id=test_document_id, unit_type="sentence"):
            value_found = not (field_type_adapter.multi_value or field.is_choice_field()) \
                          and len(text_unit_with_value_ids) > 0
            if not value_found:
                sentences_number += 1

            field_uid, value, hint_name = DetectFieldValues.predict_value(sklearn_model=sklearn_model,
                                                                          text_unit=text_unit)
            if field_uid is not None:
                if field_type_adapter.value_extracting:
                    value, hint_name = DetectFieldValues.extract_value(field_type_adapter=field_type_adapter,
                                                                       document=document,
                                                                       field=field,
                                                                       hint_name=hint_name,
                                                                       text_unit=text_unit)
                else:
                    value = True
            if value is not None:
                able_to_predict_text_units_ids.add(text_unit.pk)
                if not value_found:
                    text_unit_with_value_ids.add(text_unit.pk)

        test_values = DocumentFieldValue.objects \
            .filter(document_id=test_document_id, field_id=field.pk) \
            .values_list('sentence_id', flat=True) \
            .distinct('sentence_id') \
            .order_by('sentence_id')
        for text_unit_id in test_values:
            values_number += 1
            if text_unit_id in text_unit_with_value_ids:
                text_unit_with_value_ids.remove(text_unit_id)
                valid_values_number += 1
                able_to_predict += 1
            elif text_unit_id in able_to_predict_text_units_ids:
                able_to_predict += 1

        task.log_info('Testing on document #{0}, field {1} finished'.format(test_document_id, field.code))
        return {
            'sentences_number': sentences_number,
            'values_number': values_number,
            'valid_values_number': valid_values_number,
            'wrong_values_number': len(text_unit_with_value_ids),
            'able_to_predict': able_to_predict
        }

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=600,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3)
    def join_field_detector_model_tests(task: ExtendedTask, classifier_model_id: Any) -> None:
        results = Task.objects \
            .filter(main_task_id=task.request.parent_id, name=TrainDocumentField.test_field_detector_model.name) \
            .values_list('result', flat=True)
        valid_fields_metric = None
        wrong_fields_metric = None
        sentences_number = 0
        values_number = 0
        valid_values_number = 0
        wrong_values_number = 0
        able_to_predict = 0

        for result in results:
            sentences_number += result['sentences_number']
            values_number += result['values_number']
            valid_values_number += result['valid_values_number']
            wrong_values_number += result['wrong_values_number']
            able_to_predict += result['able_to_predict']
        if values_number > 0:
            valid_fields_metric = valid_values_number * 100 / values_number
        if sentences_number - values_number > 0:
            wrong_fields_metric = wrong_values_number * 100 / (sentences_number - values_number)

        classifier_model = ClassifierModel.objects.get(pk=classifier_model_id)
        classifier_model.test_valid_fields_metric = valid_fields_metric
        classifier_model.test_wrong_fields_metric = wrong_fields_metric
        classifier_model.test_sentences_number = sentences_number
        classifier_model.test_values_number = values_number
        classifier_model.predicted_valid_values_number = valid_values_number
        classifier_model.predicted_wrong_values_number = wrong_values_number
        classifier_model.able_to_predict = able_to_predict
        classifier_model.save()

        task.log_info('Testing of field detector model finished. valid_fields_metric={0}, wrong_fields_metric={1}'
                      .format(str(valid_fields_metric), str(wrong_fields_metric)))


class CacheDocumentFields(BaseTask):
    name = 'Cache Document Fields'

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=6000,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3
                 )
    def cache_document_fields_for_doc_ids(_task: ExtendedTask, doc_ids: Set):
        for doc in Document.objects.filter(pk__in=doc_ids):
            doc.cache_generic_values()
            doc.cache_field_values()

    def process(self, project: Project = None, **_kwargs):
        document_qs = Document.objects

        if project:
            document_qs = document_qs.filter(project__pk=project['pk'])

        doc_id_pack = set()
        for doc_id in document_qs.values_list('pk', flat=True):
            doc_id_pack.add(doc_id)
            if len(doc_id_pack) >= 10:
                self.run_sub_tasks('Cache field values for a set of documents', self.cache_document_fields_for_doc_ids,
                                   [(doc_id_pack,)])
                doc_id_pack = set()
        if len(doc_id_pack) > 0:
            self.run_sub_tasks('Cache field values for a set of documents', self.cache_document_fields_for_doc_ids,
                               [(doc_id_pack,)])


app.register_task(DetectFieldValues())
app.register_task(TrainDocumentFieldDetectorModel())
app.register_task(TrainDirtyDocumentFieldDetectorModel())
app.register_task(CacheDocumentFields())
app.register_task(TrainDocumentField())
