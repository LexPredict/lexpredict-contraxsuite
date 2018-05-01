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

import numpy as np
from celery import shared_task
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.utils import check_random_state

from apps.celery import app
from apps.common.utils import fast_uuid
from apps.document.field_types import FIELD_TYPES_REGISTRY, ValueExtractionHint
from apps.document.models import DocumentType, Document, DocumentFieldDetector, \
    ClassifierModel, DocumentFieldValue, TextUnit, DocumentField
from apps.document.parsing.machine_learning import SkLearnClassifierModel, \
    encode_category, parse_category, word_position_tokenizer
from apps.task.tasks import BaseTask, log

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.9/LICENSE"
__version__ = "1.0.9"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

MODULE_NAME = __name__


class DetectFieldValues(BaseTask):
    name = 'Detect Field Values'

    def process(self, document_type: DocumentType = None, document_name: str = None,
                do_not_write=False, drop_classifier_model=False, task_id=None, **kwargs):
        self.log("Going to detect document field values based on "
                 "the pre-coded regexps and field values entered by users...")

        document_id = kwargs.get('document_id')
        if document_id:
            self.task.subtasks_total = 1
            self.task.save()
            self.detect_field_values_for_document(document_id=document_id, do_not_write=False)
            self.task.push()
            return

        task_count = 0

        document_ids = []
        if document_name:
            for pk in Document.objects.filter(document_type=document_type,
                                              name=document_name).values_list('pk', flat=True):
                document_ids.append(pk)
            else:
                self.log('Document {0} of type {1} not found'.format(document_name, document_type))

        if document_type:
            task_count += self \
                .detect_field_values_for_document_type(
                document_type.pk, document_ids, do_not_write, drop_classifier_model, task_id)
        else:
            document_type_pks = DocumentType.objects.all().values_list('uid', flat=True)
            for document_type_pk in document_type_pks:
                task_count += DetectFieldValues \
                    .detect_field_values_for_document_type(
                    document_type_pk, document_ids, do_not_write, drop_classifier_model, task_id)

        self.task.subtasks_total = task_count
        self.task.save()

    @staticmethod
    def detect_field_values_for_document_type(document_type_pk, document_ids: List,
                                              do_not_write,
                                              drop_classifier_model,
                                              task_id):
        log(
            'Detecting field values for document type: {0}'.format(
                document_type_pk),
            task=task_id)
        document_type = DocumentType.objects.get(pk=document_type_pk)
        document_fields = document_type.fields
        if not document_fields:
            log('Can not find any fields assigned to document type: {0}'.format(
                document_type),
                task=task_id)
            return

        if drop_classifier_model:
            log('Deleting field values and classifier models for document type: {0}'.format(
                document_type),
                task=task_id)
            ClassifierModel.objects.filter(document_type=document_type).delete()

        task_count = 0

        for doc_id in document_ids or Document.objects.filter(
                document_type=document_type).values_list('id', flat=True):
            DetectFieldValues.detect_field_values_for_document.apply_async(
                args=(doc_id, do_not_write, task_id),
                task_id='%d_%s' % (
                    task_id, fast_uuid()))
            task_count += 1
        if task_count == 0:
            log('No documents in DB for document type: {0}'.format(
                document_type),
                task=task_id)
        return task_count

    @staticmethod
    @shared_task
    def detect_field_values_for_document(document_id,
                                         do_not_write,
                                         task_id=None,
                                         field_uid=None):

        doc = Document.objects.get(pk=document_id)
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
                                                    do_not_write, task_id)
            except:
                detected_counter += DetectFieldValues \
                    .detect_initial_field_values_for_document_field(
                    doc, field, sentence_text_units, do_not_write, task_id)
        log('Detected {0} field values for document #{1} ({2})'.format(detected_counter,
                                                                       document_id, doc.name),
            task=task_id)

    @staticmethod
    def detect_field_values_with_model(classifier_model, document, field, sentence_text_units,
                                       do_not_write, task_id) -> int:
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
                                                       do_not_write, task_id) -> int:
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
        self.log('Going to train field detector model based on the datasets stored in DB...')

        document_type = kwargs.get('document_type')
        task_id = kwargs.get('task_id')

        task_count = 0

        if document_type:
            task_count += self.train_model_for_document_type(document_type.pk, task_id)
        else:
            document_type_pks = DocumentType.objects.values_list('uid', flat=True)
            for document_type_pk in document_type_pks:
                task_count += self.train_model_for_document_type(
                    document_type_pk, task_id)

        self.task.subtasks_total = task_count
        self.task.save()

    def train_model_for_document_type(self, document_type_pk, task_id=None) -> int:
        self.log('Building classifier model for document type: {0}'.format(
            document_type_pk))

        document_type = DocumentType.objects.get(pk=document_type_pk)

        no_field_sentences = list(
            TextUnit.objects
                .filter(unit_type='sentence', related_field_values=None)
                .values_list('text', flat=True)[:10000])

        task_count = 0
        for field in document_type.fields.all():
            self.train_model_for_field.apply_async(
                args=(document_type.uid, field.uid, task_id, no_field_sentences),
                task_id='%d_%s' % (
                    task_id, fast_uuid()))
            task_count += 1

        return task_count

    @staticmethod
    @shared_task
    def train_model_for_field(document_type_uid, field_uid, task_id=None, no_field_sentences=None,
                              trigger_re_detecting_field_values=False):
        document_type = DocumentType.objects.get(pk=document_type_uid)
        field = DocumentField.objects.get(pk=field_uid)

        log('Training model for field #{0} ({1})...'
            .format(field_uid, field.code), task=task_id)

        field_values = list(DocumentFieldValue.objects
                            .filter(field=field, document__document_type_id=document_type_uid)
                            .values_list('sentence__text', 'value', 'extraction_hint'))
        if len(field_values) == 0:
            log('No document field values found for field #{0} ({1}). Nothing to train on.'
                .format(field_uid, field.code), task=task_id)
            return

        target_names = {SkLearnClassifierModel.EMPTY_CAT_NAME}
        field_targets_to_sentences = dict()
        for sentence, value, hint in field_values:
            target_name = encode_category(field_uid,
                                          value if field.is_choice_field() else None,
                                          hint)
            target_names.add(target_name)
            sentences = field_targets_to_sentences.get(target_name)
            if sentences is None:
                sentences = list()
                field_targets_to_sentences[target_name] = sentences
            sentences.append(sentence)

        target_names = sorted(list(target_names))
        target_name_to_index = {name: index for index, name in enumerate(target_names)}

        data = []
        target = []

        for target_name, sentences in field_targets_to_sentences.items():
            target_index = target_name_to_index[target_name]
            data.extend(sentences)
            target.extend([target_index] * len(sentences))

        if no_field_sentences is None:
            no_field_sentences = list(
                TextUnit.objects
                    .filter(unit_type='sentence', related_field_values=None)
                    .values_list('text', flat=True))

        if no_field_sentences is not None:
            data.extend(no_field_sentences)
            no_field_target_index = target_name_to_index[SkLearnClassifierModel.EMPTY_CAT_NAME]
            target.extend([no_field_target_index] * len(no_field_sentences))

        total_samples = len(data)
        target = np.array(target)
        data = np.array(data)

        random_state = check_random_state(seed=None)
        indices = np.arange(data.shape[0])
        random_state.shuffle(indices)
        data = data[indices]
        target = target[indices]

        text_clf = Pipeline([('vect', CountVectorizer(strip_accents='unicode', analyzer='word',
                                                      stop_words='english',
                                                      tokenizer=word_position_tokenizer)),
                             ('tfidf', TfidfTransformer()),
                             ('clf', SGDClassifier(loss='hinge', penalty='l2',
                                                   alpha=1e-3, random_state=42,
                                                   max_iter=5, tol=None, n_jobs=-1,
                                                   class_weight='balanced')),
                             ])
        sklearn_model = text_clf.fit(data, target)

        model = SkLearnClassifierModel(sklearn_model=sklearn_model, target_names=target_names)

        classifier_model, created = ClassifierModel.objects.get_or_create(
            document_type_id=document_type_uid, document_field_id=field_uid)

        classifier_model.set_trained_model_obj(model)
        classifier_model.save()
        log(
            'Finished training model for document_type #{0} and field #{1}. '
            'Total number of samples: {2}'.format(document_type_uid, field_uid, total_samples),
            task=task_id)
        if trigger_re_detecting_field_values:
            for document_id in Document.objects.filter(document_type=document_type).values_list(
                    'pk', flat=True):
                DetectFieldValues.detect_field_values_for_document.apply_async(
                    args=(document_id, False, task_id, field_uid))


app.register_task(DetectFieldValues())
app.register_task(TrainDocumentFieldDetectorModel())
