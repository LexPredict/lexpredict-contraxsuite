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

from typing import List, Tuple

import numpy as np
from celery import shared_task
from lexnlp.nlp.en.segments.sentences import get_sentence_span_list
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.utils import check_random_state

from apps.celery import app
from apps.fields.document_fields_repository import DOCUMENT_FIELDS
from apps.fields.models import DocumentAnnotation, ClassifierModel, ClassifierDataSetEntry
from apps.fields.parsing.field_annotations_classifier import SkLearnClassifierModel
from apps.task.tasks import BaseTask, ExtendedTask

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


MODULE_NAME = __name__


class TrainFieldDetectorModel(BaseTask):
    name = 'Train Field Detector Model'

    def process(self, **kwargs):
        self.log_info('Going to train field detector model based on the datasets stored in DB...')

        document_class = kwargs.get('document_class')

        if document_class:
            TrainFieldDetectorModel.local_train_model_for_document_class(self, document_class)
        else:
            train_model_for_document_class_args = []
            for document_class, fields in DOCUMENT_FIELDS.items():
                train_model_for_document_class_args.append((document_class,))
            self.run_sub_tasks('Train Model For Each Document Class',
                               TrainFieldDetectorModel.train_model_for_document_class,
                               train_model_for_document_class_args)

    @staticmethod
    @shared_task(base=ExtendedTask, bind=True)
    def train_model_for_document_class(task: ExtendedTask, document_class_name: str):
        TrainFieldDetectorModel.local_train_model_for_document_class(task, document_class_name)

    @staticmethod
    def local_train_model_for_document_class(task: ExtendedTask, document_class_name: str):
        task.log_info('Building classifier model for document class: {0}'.format(
            document_class_name))

        classifier_model = ClassifierModel.objects.get(
            kind=ClassifierModel.KIND_SENTENCES_RELATED_TO_FIELDS,
            document_class=document_class_name,
            document_field=None)

        target_names = list(ClassifierDataSetEntry.objects.filter(
            field_detection_model=classifier_model).values_list('category', flat=True).distinct())

        target = []
        data = []
        for target_index, target_name in enumerate(target_names):
            entries = list(ClassifierDataSetEntry
                           .objects
                           .filter(field_detection_model=classifier_model, category=target_name)
                           .values_list('text', flat=True))
            target.extend(len(entries) * [target_index])
            data.extend(entries)
        target = np.array(target)
        data = np.array(data)

        random_state = check_random_state(seed=None)
        indices = np.arange(data.shape[0])
        random_state.shuffle(indices)
        data = data[indices]
        target = target[indices]

        text_clf = Pipeline([('vect', CountVectorizer()),
                             ('tfidf', TfidfTransformer()),
                             ('clf', SGDClassifier(loss='hinge', penalty='l2',
                                                   alpha=1e-3, random_state=42,
                                                   max_iter=5, tol=None)),
                             ])
        sklearn_model = text_clf.fit(data, target)

        model = SkLearnClassifierModel(sklearn_model=sklearn_model, target_names=target_names)

        classifier_model.set_trained_model_obj(model)
        classifier_model.save()

        task.log_info(
            'Trained model based on {0} dataset entries for document class: {1}'.format(
                len(target),
                document_class_name))


class BuildFieldDetectorDataset(BaseTask):
    name = 'Build Field Detector Dataset'

    def process(self, **kwargs):
        self.log_info(
            "Going to prepare datasets based on the pre-coded regexps and annotations"
            "entered by users...")

        document_class = kwargs.get('document_class')
        document_ids = kwargs.get('document_ids')

        if document_class:
            self.build_sentences_to_fields_relations_dataset(
                document_class, document_ids)
        else:
            for document_class, fields in DOCUMENT_FIELDS.items():
                self.build_sentences_to_fields_relations_dataset(
                    document_class, document_ids)

    @staticmethod
    def _sentence_matches_annotations(sentence_span: Tuple[int, int],
                                      annotations: List[Tuple[int, int]]):
        #
        # a:  25        30
        # s:       28       33
        #
        #
        if annotations:
            for a in annotations:
                if a[0] <= sentence_span[1] and sentence_span[0] <= a[1]:
                    return True
        return False

    @staticmethod
    def _get_doc_class(doc_class_name: str):
        field_configs = DOCUMENT_FIELDS.get(doc_class_name)
        if not field_configs:
            return None
        for field_config in field_configs.values():
            return field_config.document_class

    def build_sentences_to_fields_relations_dataset(self, document_class_name: str,
                                                    document_ids: List):
        self.log_info(
            'Building classifier for detecting sentences related to fields '
            'for document class: {0}'.format(
                document_class_name))
        field_configs = DOCUMENT_FIELDS[document_class_name]
        if not field_configs:
            self.log_warn('Can not find any field configs for document class: {0}'.format(
                document_class_name))
            return

        document_class = BuildFieldDetectorDataset._get_doc_class(document_class_name)

        classifier_model, created = ClassifierModel.objects.get_or_create(
            kind=ClassifierModel.KIND_SENTENCES_RELATED_TO_FIELDS,
            document_class=document_class_name,
            document_field=None)

        if created:
            self.log_info('Classifier data set already exists for document class: {0}'.format(
                document_class_name))
        else:
            self.log_info('New classifier data created for document class: {0}'.format(
                document_class_name))

        task_count = 0

        build_dataset_on_document_args = []
        for doc_id in document_ids or document_class.objects.all().values_list('id', flat=True):
            build_dataset_on_document_args.append((document_class_name, doc_id, False))
            task_count += 1
        self.run_sub_tasks('Build Dataset on Each Document',
                           BuildFieldDetectorDataset.build_dataset_on_document,
                           build_dataset_on_document_args)
        if task_count == 0:
            self.log_info('No documents in DB for document class: {0}'.format(
                document_class_name))
        return task_count

    @staticmethod
    @shared_task(base=ExtendedTask, bind=True)
    def build_dataset_on_document(task: ExtendedTask,
                                  document_class_name: str,
                                  document_id,
                                  retrain_model: bool):
        field_configs = DOCUMENT_FIELDS[document_class_name]
        if not field_configs:
            return

        document_class = BuildFieldDetectorDataset._get_doc_class(document_class_name)

        doc = document_class.objects.get(pk=document_id)

        classifier_model, created = ClassifierModel.objects.get_or_create(
            kind=ClassifierModel.KIND_SENTENCES_RELATED_TO_FIELDS,
            document_class=document_class_name,
            document_field=None)

        deleted, rows_count = ClassifierDataSetEntry.objects.filter(
            field_detection_model=classifier_model,
            document=doc).delete()
        if deleted > 0:
            task.log_info(
                'Deleted {0} data set entries of document {1}'.format(deleted, doc.pk))

        def add(code, sentence):
            ClassifierDataSetEntry.objects.create(field_detection_model=classifier_model,
                                                  document=doc,
                                                  category=code,
                                                  text=sentence)

            task.log_info('Extracting training data from document: {0}'.format(doc.pk))

        text = doc.full_text
        annotations = list(DocumentAnnotation.objects.filter(document__pk=doc.pk))
        sentence_spans = get_sentence_span_list(text)
        for span in sentence_spans:
            sentence = text[span[0]:span[1]]
            annotated_fields = set()
            added = False
            if annotations:
                for a in annotations:
                    if a.document_field \
                            and a.start_offset <= span[1] and span[0] <= a.end_offset:
                        field_code = a.document_field.pk
                        add(field_code, sentence)
                        annotated_fields.add(field_code)
                        added = True

            for field_config in field_configs.values():
                if field_config.field_code not in annotated_fields \
                        and field_config.sentence_matches_field_detectors(sentence):
                    add(field_config.field_code, sentence)
                    added = True
            if not added:
                add('', sentence)
            task.log_info('Processed {0} sentences of document {1}'
                          .format(len(sentence_spans), doc.pk))

        if retrain_model:
            TrainFieldDetectorModel.train_model_for_document_class.apply_async(
                args=(document_class_name,))


app.register_task(BuildFieldDetectorDataset())
app.register_task(TrainFieldDetectorModel())
