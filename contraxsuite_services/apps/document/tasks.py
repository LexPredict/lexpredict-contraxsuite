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
from typing import List

import pandas as pd

from celery import shared_task
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.utils import shuffle

from apps.celery import app
from apps.document.field_types import FIELD_TYPES_REGISTRY, ValueExtractionHint
from apps.document.models import DocumentType, Document, DocumentFieldDetector, \
    ClassifierModel, DocumentFieldValue, TextUnit, DocumentField
from apps.document.parsing.machine_learning import SkLearnClassifierModel, \
    encode_category, parse_category, word_position_tokenizer
from apps.task.tasks import BaseTask, ExtendedTask

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.1b/LICENSE"
__version__ = "1.1.1b"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

MODULE_NAME = __name__


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

        document_ids = []
        if document_name:
            for pk in Document.objects.filter(document_type=document_type,
                                              name=document_name).values_list('pk', flat=True):
                document_ids.append(pk)
            else:
                self.log_info(
                    'Document {0} of type {1} not found'.format(document_name, document_type))

        if document_type:
            self.detect_field_values_for_document_type(
                document_type.pk, document_ids, do_not_write, drop_classifier_model)
        else:
            document_type_pks = DocumentType.objects.all().values_list('uid', flat=True)
            for document_type_pk in document_type_pks:
                DetectFieldValues \
                    .detect_field_values_for_document_type(
                    document_type_pk, document_ids, do_not_write, drop_classifier_model)

    def detect_field_values_for_document_type(self, document_type_pk, document_ids: List,
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
        for doc_id in document_ids or Document.objects.filter(
                document_type=document_type).values_list('id', flat=True):
            detect_field_values_for_document_args.append((doc_id, do_not_write, None))
            task_count += 1
        self.run_sub_tasks('Detect Field Values For Each Document',
                           DetectFieldValues.detect_field_values_for_document,
                           detect_field_values_for_document_args)
        if task_count == 0:
            self.log_info('No documents in DB for document type: {0}'.format(
                document_type))
        return task_count

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=600,
                 default_retry_delay=10,
                 retry_backoff=True)
    def detect_field_values_for_document(task: ExtendedTask,
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
            pk=field_uid)] if field_uid else document_type.fields.all()

        # TODO Prevent re-detecting values DELETED by a user
        # Currently it only prevents updating values created/updated by a user
        # but deleted values will not be taken into account and will be recreated.

        sentence_text_units = list(TextUnit.objects.filter(document=doc, unit_type="sentence"))

        detected_counter = 0
        for field in fields:
            # Delete previously detected values
            # to avoid accumulating garbage on each iteration.
            DocumentFieldValue.objects \
                .filter(document=doc,
                        field=field,
                        created_by__isnull=True,
                        modified_by__isnull=True) \
                .delete()

            try:
                classifier_model = ClassifierModel.objects \
                    .get(document_type=document_type, document_field=field)
                detected_counter += DetectFieldValues \
                    .detect_field_values_with_model(classifier_model,
                                                    doc, field, sentence_text_units,
                                                    do_not_write)
            except:
                detected_counter += DetectFieldValues \
                    .detect_initial_field_values_for_document_field(
                    doc, field, sentence_text_units, do_not_write)
        task.log_info('Detected {0} field values for document #{1} ({2})'.format(
            detected_counter, document_id, doc.name))

    @staticmethod
    def detect_field_values_with_model(classifier_model, document, field, sentence_text_units,
                                       do_not_write) -> int:
        sklearn_model = classifier_model.get_trained_model_obj()
        field_type_adapter = FIELD_TYPES_REGISTRY[field.type]

        detected_values = list()
        for text_unit in sentence_text_units:
            predicted = sklearn_model.sklearn_model.predict([text_unit.text])
            target_index = predicted[0]
            target_name = sklearn_model.target_names[target_index]
            field_uid, value, hint = parse_category(target_name)

            if field_uid is not None:
                if field_type_adapter.value_aware:
                    hint = hint or ValueExtractionHint.TAKE_FIRST.name
                    value, hint = field_type_adapter \
                        .get_or_extract_value(document,
                                              field, None,
                                              hint,
                                              text_unit.text)
                    if value is None:
                        continue

                detected_values.append((text_unit, value, hint))
                if not (field_type_adapter.multi_value or field.is_choice_field()):
                    break

        return DetectFieldValues.save_detected_values(document, field, field_type_adapter,
                                                      detected_values, do_not_write)

    @staticmethod
    def save_detected_values(document, field, field_type_adapter, detected_values, do_not_write):
        if len(detected_values) == 0:
            return 0
        if field.is_choice_field() and not field_type_adapter.multi_value:
            values_order = field.get_choice_values()
            for choice_value in values_order:
                for text_unit, value, hint in detected_values:
                    if choice_value == value:
                        if not do_not_write:
                            field_type_adapter.save_value(document,
                                                          field,
                                                          text_unit.location_start,
                                                          text_unit.location_end,
                                                          text_unit.text,
                                                          text_unit,
                                                          value,
                                                          user=None,
                                                          allow_overwriting_user_data=False,
                                                          extraction_hint=hint)
                        return 1
        else:
            for text_unit, value, hint in detected_values:
                if not do_not_write:
                    field_type_adapter.save_value(document,
                                                  field,
                                                  text_unit.location_start,
                                                  text_unit.location_end,
                                                  text_unit.text,
                                                  text_unit,
                                                  value,
                                                  user=None,
                                                  allow_overwriting_user_data=False,
                                                  extraction_hint=hint)
            return len(detected_values)

    @staticmethod
    def detect_initial_field_values_for_document_field(document, field, sentence_text_units,
                                                       do_not_write) -> int:
        document_type = document.document_type
        field_detectors = DocumentFieldDetector.objects.filter(document_type=document_type,
                                                               field=field)
        field_type_adapter = FIELD_TYPES_REGISTRY.get(field.type)

        detected_values = list()

        for text_unit in sentence_text_units:

            for field_detector in field_detectors:
                if field_detector.matches(text_unit.text):
                    value = field_detector.detected_value
                    hint = None
                    if field_type_adapter.value_aware:
                        hint = field_detector.extraction_hint or ValueExtractionHint.TAKE_FIRST.name
                        value, hint = field_type_adapter \
                            .get_or_extract_value(document,
                                                  field, value,
                                                  hint,
                                                  text_unit.text)
                        if value is None:
                            continue

                    detected_values.append((text_unit, value, hint))

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
            self.train_model_for_document_type(document_type.pk)
        else:
            document_type_pks = DocumentType.objects.values_list('uid', flat=True)
            for document_type_pk in document_type_pks:
                self.train_model_for_document_type(
                    document_type_pk)

    def train_model_for_document_type(self, document_type_pk) -> int:
        self.log_info('Building classifier model for document type: {0}'.format(
            document_type_pk))

        document_type = DocumentType.objects.get(pk=document_type_pk)

        no_field_sentences = list(
            TextUnit.objects
                .filter(unit_type='sentence', related_field_values=None)
                .values_list('text', flat=True)[:10000])

        train_model_for_field_args = []

        for field in document_type.fields.all():
            train_model_for_field_args.append((document_type.uid,
                                               field.uid,
                                               no_field_sentences,
                                               False))

        self.run_sub_tasks('Train Model For Each Field',
                           TrainDocumentFieldDetectorModel.train_model_for_field,
                           train_model_for_field_args)

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=1200,
                 default_retry_delay=10,
                 retry_backoff=True)
    def train_model_for_field(task: ExtendedTask,
                              document_type_uid,
                              field_uid,
                              no_field_sentences,
                              trigger_re_detecting_field_values):
        document_type = DocumentType.objects.get(pk=document_type_uid)
        field = DocumentField.objects.get(pk=field_uid)

        task.log_info('Training model for field #{0} ({1})...'
                      .format(field_uid, field.code))

        df = pd.DataFrame.from_records(DocumentFieldValue.objects
                                       .filter(field=field,
                                               document__document_type=document_type)
                                       .values('created_by', 'sentence__text', 'value',
                                               'extraction_hint'))

        df['target_name'] = df.apply(lambda row: encode_category(
            field_uid,
            row.value if field.is_choice_field() else None,
            row.extraction_hint), axis=1)

        df['target_index'] = df.target_name.factorize(sort=True)[0] + 1

        if no_field_sentences is None:
            no_field_sentences = list(
                TextUnit.objects
                    .filter(unit_type='sentence', related_field_values=None)
                    .extra(select={'sentence__text': 'text'})
                    .values('sentence__text'))
            df = df.append(no_field_sentences)
        else:
            df = df.append([{'sentence__text': i} for i in no_field_sentences])

        df['target_index'] = df['target_index'].fillna(0).astype('int')
        df['target_name'] = df['target_name'].fillna(SkLearnClassifierModel.EMPTY_CAT_NAME).astype(
            'str')
        df['user_input'] = df['created_by'].fillna(0).astype('bool')

        max_group_data_len = 10000
        res_df = pd.DataFrame()

        for group_index, group_df in df.groupby('target_index'):
            if group_df.shape[0] > max_group_data_len:
                group_df = shuffle(
                    group_df.sort_values('user_input', ascending=False)[:max_group_data_len])
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
            document_type_id=document_type_uid, document_field_id=field_uid)

        classifier_model.set_trained_model_obj(model)
        classifier_model.save()
        task.log_info(
            'Finished training model for document_type #{0} and field #{1}. '
            'Total number of samples: {2}'.format(document_type_uid, field_uid, total_samples))

        if trigger_re_detecting_field_values:

            detect_field_values_for_document_args = []

            document_ids = Document.objects.active().filter(
                document_type=document_type).values_list(
                'pk', flat=True)

            for document_id in document_ids:
                detect_field_values_for_document_args.append((document_id,
                                                              False,
                                                              field_uid))
            task.run_sub_tasks('Detect Values of Field {0} for Each Document'.format(
                field.code),
                DetectFieldValues.detect_field_values_for_document,
                detect_field_values_for_document_args)


app.register_task(DetectFieldValues())
app.register_task(TrainDocumentFieldDetectorModel())
