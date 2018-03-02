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

from typing import List, Union

import numpy as np
from celery import shared_task
from lexnlp.nlp.en.segments.sentences import get_sentence_span_list
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.svm import LinearSVC
from skmultilearn.problem_transform import BinaryRelevance
from sklearn.pipeline import Pipeline
from sklearn.utils import check_random_state

from apps.celery import app
from apps.common.utils import fast_uuid
from apps.document.field_types import FIELD_TYPES_REGISTRY
from apps.document.models import DocumentType, Document, DocumentFieldDetector, DocumentField, \
    ClassifierModel, DocumentFieldValue
from apps.document.parsing.field_annotations_classifier import SkLearnClassifierModel
from apps.task.tasks import BaseTask, log

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.3/LICENSE"
__version__ = "1.0.6"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

MODULE_NAME = __name__


class ModelCategory:
    def __init__(self, document_field: Union[None, DocumentField], choice_value) -> None:
        self.document_field = document_field
        self.choice_value = choice_value

    def name(self):
        if not self.document_field:
            return SkLearnClassifierModel.EMPTY_CAT_NAME

        return str(self.document_field.uid) + (
            ':::' + str(self.choice_value) if self.choice_value is not None else '')

    @staticmethod
    def from_name(name: str):
        if SkLearnClassifierModel.EMPTY_CAT_NAME == name:
            return ModelCategory(None, None)
        ar = name.split(':::')
        if not ar:
            return None
        field_uid = ar[0]
        choice_value = ar[1] if len(ar) > 1 else None
        field = DocumentField.objects.get(uid=field_uid)
        return ModelCategory(field, choice_value)


class TrainDocumentFieldDetectorModel(BaseTask):
    name = 'Train Document Field Detector Model'

    def process(self, **kwargs):
        self.log('Going to train field detector model based on the datasets stored in DB...')

        document_type = kwargs.get('document_type')
        task_id = kwargs.get('task_id')

        if document_type:
            self.train_model_for_document_type(document_type.pk, task_id)
        else:
            document_type_pks = DocumentType.objects.values_list('uid', flat=True)
            for document_type_pk in document_type_pks:
                self.train_model_for_document_type(
                    document_type_pk, task_id)

    @staticmethod
    @shared_task
    def train_model_for_document_type(document_type_pk, task_id=None):
        log('Building classifier model for document type: {0}'.format(
            document_type_pk),
            task=task_id)

        document_type = DocumentType.objects.get(pk=document_type_pk)

        classifier_model = ClassifierModel.objects.get(
            document_type=document_type)

        document_fields = document_type.fields

        categories = [ModelCategory(None, None)]

        for f in document_fields.all():
            if f.is_choice_field() and f.choices:
                for choice in f.get_choice_values():
                    categories.append(ModelCategory(f, choice))
            else:
                categories.append(ModelCategory(f, None))

        target_names = sorted([cat.name() for cat in categories])
        target_index_by_name = {name: i for i, name in enumerate(target_names)}
        empty_target_index = target_index_by_name.get(SkLearnClassifierModel.EMPTY_CAT_NAME)
        sentences_to_target_arrays = {}

        for full_text, document_pk in Document.objects.filter(
                document_type=document_type).values_list('full_text', 'pk'):
            sentence_spans = get_sentence_span_list(full_text)
            values = set(DocumentFieldValue.objects.filter(document__pk=document_pk))
            counter = 0
            for span in sentence_spans:
                sentence = full_text[span[0]:span[1]]
                targets = sentences_to_target_arrays.get(sentence)
                if targets is None:
                    targets = np.zeros(len(target_names), dtype=int)
                    sentences_to_target_arrays[sentence] = targets

                to_del = set()
                for value in values:
                    if value.location_start <= span[1] and value.location_end >= span[0]:
                        category = ModelCategory(value.field,
                                                 value.value
                                                 if value.field.is_choice_field()
                                                 else None)
                        target_index = target_index_by_name.get(category.name())
                        if target_index is not None:
                            targets[target_index] = 1
                        to_del.add(value)
                if not to_del:
                    targets[empty_target_index] = 1
                    counter += 1
                else:
                    values = values - to_del
                    counter += len(to_del)

            log('Prepared {0} dataset entries for document #{1}'.format(
                counter,
                document_pk),
                task=task_id)

        data = []
        target = []

        for sentence, sentence_targets in sentences_to_target_arrays.items():
            data.append(sentence)
            target.append(sentence_targets)
            sentences_to_target_arrays[sentence] = None

        target = np.array(target)
        data = np.array(data)

        random_state = check_random_state(seed=None)
        indices = np.arange(data.shape[0])
        random_state.shuffle(indices)
        data = data[indices]
        target = target[indices]

        text_clf = Pipeline([('vect', CountVectorizer(strip_accents='unicode', analyzer='word',
                                                      stop_words='english')),
                             ('tfidf', TfidfTransformer()),
                             ('clf', BinaryRelevance(
                                 LinearSVC(class_weight='balanced', loss='epsilon_insensitive'))),
                             ])
        sklearn_model = text_clf.fit(data, target)

        model = SkLearnClassifierModel(sklearn_model=sklearn_model, target_names=target_names)

        classifier_model.set_trained_model_obj(model)
        classifier_model.save()

        log('Trained model based on {0} dataset entries for document type: {1}'.format(
            len(target),
            document_type),
            task=task_id)


class DetectFieldValues(BaseTask):
    name = 'Detect Field Values'

    def process(self, document_type: DocumentType = None, document_ids: List = None,
                do_not_write=False, drop_classifier_model=False, task_id=None, **kwargs):
        self.log("Going to detect document field values based on "
                 "the pre-coded regexps and field values entered by users...")

        task_count = 0

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
            log('Deleting classifier models for document type: {0}'.format(
                document_type),
                task=task_id)
            ClassifierModel.objects.filter(document_type=document_type).delete()

        classifier_model, created = ClassifierModel.objects.get_or_create(
            document_type=document_type)

        if created:
            log('New classifier data created for document type: {0}'.format(
                document_type),
                task=task_id)
        else:
            log('Classifier data set already exists for document type: {0}'.format(
                document_type),
                task=task_id)

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
                                         task_id=None):

        doc = Document.objects.get(pk=document_id)
        document_type = doc.document_type

        # TODO Prevent re-detecting values DELETED by a user
        # Currently it only prevents updating values created/updated by a user
        # but deleted values will not be taken into account and will be recreated.

        sklearn_model = None
        try:
            classifier_model = ClassifierModel.objects.get(document_type=document_type)
            sklearn_model = classifier_model.get_trained_model_obj()
        except:
            pass

        if sklearn_model:
            DetectFieldValues.detect_field_values_with_model(sklearn_model, doc, do_not_write,
                                                             task_id)
        else:
            DetectFieldValues.detect_initial_field_values_for_document(doc, do_not_write, task_id)

    @staticmethod
    def detect_field_values_with_model(sklearn_model, doc, do_not_write, task_id):
        categories_to_spans = sklearn_model.detect_category_names_to_spans(doc.full_text)
        counter = 0
        for category_name, spans in categories_to_spans.items():
            try:
                category = ModelCategory.from_name(category_name)
            except:
                log(
                    'Unable to build category from name: {0}. '
                    'Please try rebuilding the model.'.format(category_name), task=task_id)
                continue
            if not spans:
                continue

            field = category.document_field

            if field:
                field_type_adapter = FIELD_TYPES_REGISTRY.get(field.type)
                if not do_not_write:
                    DocumentFieldValue.objects \
                        .filter(document=doc) \
                        .filter(created_by__isnull=True) \
                        .filter(modified_by__isnull=True) \
                        .filter(field=field) \
                        .delete()

                for location_start, location_end, location_text in spans:
                    value = category.choice_value
                    if field_type_adapter.value_aware:
                        value = field_type_adapter.extraction_function(field, value, location_text)
                        if value is None:
                            continue

                    if not do_not_write:
                        field_type_adapter.save_value(doc, field, location_start, location_end,
                                                      location_text, value,
                                                      user=None,
                                                      allow_overwriting_user_data=False)
                    # log('Detected by model: {0}.{1} = {2}'.format(doc.name, field.code,
                    #                                              value or '[{0};{1}]'.format(
                    #                                                  location_start,
                    #                                                  location_end)), task=task_id)
                    counter += 1
        log('Model has detected {0} field values for document {1}'.format(counter, doc),
            task=task_id)

    @staticmethod
    def detect_initial_field_values_for_document(doc: Document, do_not_write, task_id):
        document_type = doc.document_type
        document_fields = document_type.fields.all()
        if not document_fields:
            log('Can not find any fields assigned to document type: {0}'.format(
                document_type),
                task=task_id)
            return

        field_detectors = DocumentFieldDetector.objects.filter(document_type=document_type)

        text = doc.full_text

        sentence_spans = get_sentence_span_list(text)

        for span in sentence_spans:
            sentence = text[span[0]:span[1]]

            for field_detector in field_detectors:
                if field_detector.matches(sentence):
                    field = field_detector.field
                    field_type_adapter = FIELD_TYPES_REGISTRY.get(field.type)

                    value = field_detector.detected_value
                    if field_type_adapter.value_aware:
                        value = field_type_adapter.extraction_function(field, value, sentence)
                        if value is None:
                            continue

                    # log('Detected by regexps: {0}.{1} = {2}'.format(doc.name, field.code,
                    #                                                value or '[{0};{1}]'.format(
                    #                                                    span[0],
                    #                                                    span[1])),
                    #    task=task_id)

                    if not do_not_write:
                        field_type_adapter.save_value(doc, field, span[0], span[1], sentence,
                                                      value,
                                                      user=None,
                                                      allow_overwriting_user_data=False)

        log('Processed {0} sentences of document {1}'.format(len(sentence_spans), doc.pk),
            task=task_id)


app.register_task(DetectFieldValues())
app.register_task(TrainDocumentFieldDetectorModel())
