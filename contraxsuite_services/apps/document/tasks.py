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
import json
from typing import Any, List, Set, Dict

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from django.db import transaction
from django.utils.timezone import now
from psycopg2 import InterfaceError, OperationalError

from apps.celery import app
from apps.common.advancedcelery.db_cache import DbCache
from apps.document.field_types import FIELD_TYPES_REGISTRY, FieldType
from apps.document.fields_detection import field_detection, field_detection_utils
from apps.document.fields_detection.fields_detection_abstractions import DetectedFieldValue
from apps.document.fields_detection.regexps_field_detection import apply_simple_config
from apps.document.fields_processing import field_value_cache
from apps.document.fields_processing.field_processing_utils import merge_document_field_values_to_python_value
from apps.document.models import DocumentType, Document, ClassifierModel, DocumentFieldValue, TextUnit, DocumentField, \
    DocumentTypeField
from apps.project.models import Project
from apps.task.models import Task
from apps.task.tasks import BaseTask, ExtendedTask, CeleryTaskLogger, call_task, file_access_handler
from apps.task.utils.task_utils import TaskUtils

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.5a/LICENSE"
__version__ = "1.1.5a"
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
                               [(document_id, False)])
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

    def detect_field_values_for_document_type(self, document_type_pk,
                                              document_name: str,
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
            detect_field_values_for_document_args.append((doc_id, do_not_write))
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
                                         do_not_write):
        DetectFieldValues._detect_field_values_for_document(task,
                                                            document_id,
                                                            do_not_write)

    @staticmethod
    def _detect_field_values_for_document(task: ExtendedTask,
                                          document_id,
                                          do_not_write):
        doc = Document.objects.get(pk=document_id)

        if doc.status and not doc.status.is_active:
            task.log_info('Forbidden detecting field values for document with "completed"'
                          ' status, document #{} ({})'.format(document_id, doc.name))
            return

        log = CeleryTaskLogger(task)

        dfvs = field_detection \
            .detect_and_cache_field_values_for_document(log, doc, save=not do_not_write)

        task.log_info('Detected {0} field values for document #{1} ({2})'.format(
            len(dfvs), document_id, doc.name))


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
        document_type = DocumentType.objects.get(pk=document_type_uid)
        field = DocumentField.objects.get(pk=field_uid)
        new_model = field_detection \
            .train_document_field_detector_model(CeleryTaskLogger(task), document_type, field,
                                                 None)  # type: ClassifierModel
        if new_model:
            ClassifierModel.objects \
                .filter(document_type=document_type,
                        document_field=field).delete()
            new_model.save()


class TrainDirtyDocumentFieldDetectorModel(BaseTask):
    name = 'Train Dirty Document Field Detector Model'

    def process(self, **kwargs):
        self.log_info(
            'Going to train dirty field detector model based on the datasets stored in DB...')

        dirty_fields = DocumentTypeField.objects.get_dirty_fields()

        if dirty_fields:
            train_model_for_dirty_field_args = []

            for dirty_field in DocumentTypeField.objects.get_dirty_fields():  # type: DocumentTypeField
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
        dirty_field = DocumentTypeField.objects \
            .filter(pk=dirty_field_id) \
            .prefetch_related('document_type', 'document_field')[0]

        if dirty_field.can_retrain():
            dirty_field.dirty = False
            dirty_field.save()
            document_type = dirty_field.document_type
            field = dirty_field.document_field
            train_docs_count = field_detection_utils.get_approved_documents_number(document_type, field, None)
            if train_docs_count >= settings.ML_TRAIN_DATA_SET_GROUP_LEN:
                new_model = field_detection.train_document_field_detector_model(CeleryTaskLogger(task),
                                                                                document_type, field, None)
                if new_model:
                    ClassifierModel.objects.filter(document_type=document_type, document_field=field).delete()
                    new_model.save()


@app.task(name='advanced_celery.retrain_dirty_fields', bind=True)
def retrain_dirty_fields(self):
    TaskUtils.prepare_task_execution()
    if DocumentTypeField.objects.has_dirty_fields():
        task_name = TrainDirtyDocumentFieldDetectorModel.name
        execution_delay = now() - datetime.timedelta(
            seconds=settings.RETRAINING_TASK_EXECUTION_DELAY_IN_SEC)
        if not Task.objects.active_tasks_exist(task_name, execution_delay):
            call_task(task_name, module_name='apps.document.tasks')


class TrainAndTest(BaseTask):
    name = 'Train And Test'
    soft_time_limit = 6000
    default_retry_delay = 10
    retry_backoff = True
    autoretry_for = (SoftTimeLimitExceeded, InterfaceError, OperationalError,)
    max_retries = 3

    def process(self, **kwargs):
        self.log_info(
            'Going to train document field based on the datasets stored in DB...')

        document_type_field_id = kwargs.get('document_type_field_id')
        skip_training = kwargs.get('skip_training')
        use_only_confirmed_field_values_for_training = kwargs.get('use_only_confirmed_field_values_for_training')
        train_data_project_ids = kwargs.get('train_data_project_ids')

        skip_testing = kwargs.get('skip_testing')
        use_only_confirmed_field_values_for_testing = kwargs.get('use_only_confirmed_field_values_for_testing')
        test_data_projects_ids = kwargs.get('test_data_projects_ids')

        document_type_field = DocumentTypeField.objects.get(pk=document_type_field_id)
        document_type = document_type_field.document_type
        field = document_type_field.document_field  # type: DocumentField

        if not field.is_detectable():
            self.log_info('Field {0} is not detectable. Nothing to train and/or test.'.format(field.code))

        new_model = None

        if not skip_training:
            if train_data_project_ids:
                self.log_info('Training model on the specified projects...')
            else:
                self.log_info('No training projects specified. '
                              'Training model on all user-confirmed field values in the system...')

            new_model = field_detection \
                .train_document_field_detector_model(CeleryTaskLogger(self),
                                                     document_type,
                                                     field,
                                                     train_data_project_ids,
                                                     use_only_confirmed_field_values_for_training)
            if new_model:
                ClassifierModel.objects.filter(document_type=document_type, document_field=field).delete()
                new_model.save()

                if new_model.classifier_accuracy_report_in_sample:
                    self.log_info('Sklearn test report for in-sample docs:\n{0}'
                                  .format(new_model.classifier_accuracy_report_in_sample))

                if new_model.classifier_accuracy_report_out_of_sample:
                    self.log_info('Sklearn test report for out-of-sample docs:\n{0}'
                                  .format(new_model.classifier_accuracy_report_out_of_sample))
            else:
                self.log_info('No model trained. '
                              'Probably the detection strategy of field {0} does not allow training'.format(field.code))

        if skip_testing:
            return

        if not test_data_projects_ids:
            self.log_info('No test projects specified. Skiping the testing step.')
            return
        else:
            if not use_only_confirmed_field_values_for_testing:
                test_document_ids = Document.objects \
                    .filter(project_id__in=test_data_projects_ids, document_type_id=document_type.pk) \
                    .values_list('pk', flat=True)
            else:
                test_document_ids = set(field_detection_utils
                                        .get_qs_active_modified_document_ids(document_type,
                                                                             field,
                                                                             test_data_projects_ids))
                test_document_ids.update(set(field_detection_utils
                                             .get_qs_finished_document_ids(document_type,
                                                                           test_data_projects_ids)))

            self.log_info('Testing field detection document-by-document...')
            test_tasks_args = []
            for test_document_id in test_document_ids:
                test_tasks_args.append((field.uid, test_document_id))

            if test_tasks_args:
                self.run_sub_tasks('Test Field Detector Model', TrainAndTest.test_field_detector_model,
                                   test_tasks_args)

                self.run_after_sub_tasks_finished('Join Field Detector Model Tests',
                                                  TrainAndTest.join_field_detector_model_tests,
                                                  [(field.uid, document_type.uid, new_model.pk if new_model else None)])

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=6000,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3)
    def test_field_detector_model(task: ExtendedTask, field_id, document_id) -> dict:
        document = Document.objects.get(pk=document_id)  # type: Document
        field = DocumentField.objects.get(pk=field_id)  # type: DocumentField

        expected_dfvs = field_detection.detect_and_cache_field_values(CeleryTaskLogger(task), document, field,
                                                                      save=False)  # type: List[DetectedFieldValue]
        actual_dfvs = list(DocumentFieldValue.objects
                           .filter(document=document, field=field, removed_by_user=False)
                           .all())  # type: List[DocumentFieldValue]

        if field.is_value_aware():
            # dates, numbers, e.t.c.
            expected_field_values = field_detection.merge_detected_field_values_to_python_value(expected_dfvs)
            expected_field_value = expected_field_values.get(field.code)

            actual_field_values = merge_document_field_values_to_python_value(actual_dfvs)
            actual_field_value = actual_field_values.get(field.code)

            matches = bool(expected_field_value == actual_field_value)
        else:
            # related-info e.t.c.
            expected_set = {'text_unit_' + str(dfv.text_unit.id) for dfv in expected_dfvs if dfv.text_unit}
            expected_field_value = '; '.join(sorted(expected_set))

            actual_set = {'text_unit_' + str(dfv.text_unit.id) for dfv in actual_dfvs if dfv.text_unit}
            actual_field_value = '; '.join(sorted(actual_set))
            matches = bool(expected_set == actual_set)

        if not matches:
            task.log_info('{3} Test doc: {0} (Project: {5}). '
                          'Detected: {1}. Real: {2}.\nDetected in text:-----\n{4}\n-----'
                          .format(document.name,
                                  expected_field_value,
                                  actual_field_value,
                                  '[  OK  ]' if matches else '[ ERR  ]',
                                  '\n---\n'.join([dfv.text_unit.text
                                                  for dfv in expected_dfvs]) if expected_dfvs else '',
                                  document.project.name if document.project else ''))

        text_units_number = TextUnit.objects.filter(document=document, unit_type=field.text_unit_type).count()

        return {
            'text_units_number': text_units_number,
            'value_matches_expected': matches
        }

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=600,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3)
    def join_field_detector_model_tests(task: ExtendedTask,
                                        field_uid,
                                        document_type_uid,
                                        classifier_model_id):
        results = list(Task.objects \
                       .filter(main_task_id=task.request.parent_id,
                               name=TrainAndTest.test_field_detector_model.name) \
                       .values_list('result', flat=True))

        test_text_units_number = 0
        match_number = 0
        test_doc_number = 0

        for res in results:
            test_doc_number += 1
            test_text_units_number += (res.get('text_units_number') or 0)
            if res.get('value_matches_expected'):
                match_number += 1

        accuracy = match_number / test_doc_number

        if classifier_model_id:
            classifier_model = ClassifierModel.objects.get(pk=classifier_model_id)
            classifier_model.field_detection_accuracy = accuracy
            classifier_model.save()

        field = DocumentField.objects.get(pk=field_uid)
        document_type = DocumentType.objects.get(pk=document_type_uid)

        task.log_info('Testing finished.\n'
                      'Document type: {0}.\n'
                      'Field: {1}.\n'
                      'Text unit type: {2}.\n'
                      'Test documents number: {3}.\n'
                      'Test text units number: {4}.\n'
                      'Accuracy: {5}.\n'
                      .format(document_type.code,
                              field.code,
                              field.text_unit_type,
                              test_doc_number,
                              test_text_units_number,
                              accuracy))


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
            log = CeleryTaskLogger(_task)
            field_value_cache.cache_generic_values(doc)
            suggested_values = field_detection.detect_and_cache_field_values_for_document(log, doc, False)
            field_value_cache.cache_field_values(doc, suggested_values, save=True)

    def process(self, project: Project = None, **_kwargs):
        document_qs = Document.objects

        if project:
            document_qs = document_qs.filter(project__pk=project['pk'])

        doc_id_pack = set()
        for doc_id in document_qs.values_list('pk', flat=True):
            doc_id_pack.add(doc_id)
            if len(doc_id_pack) >= 10:
                self.run_sub_tasks('Cache field values for a set of documents',
                                   self.cache_document_fields_for_doc_ids,
                                   [(doc_id_pack,)])
                doc_id_pack = set()
        if len(doc_id_pack) > 0:
            self.run_sub_tasks('Cache field values for a set of documents', self.cache_document_fields_for_doc_ids,
                               [(doc_id_pack,)])


class LoadDocumentWithFields(BaseTask):
    name = 'Load Document With Fields'
    soft_time_limit = 6000
    default_retry_delay = 10
    retry_backoff = True
    autoretry_for = (SoftTimeLimitExceeded, InterfaceError, OperationalError,)
    max_retries = 3

    @staticmethod
    def load_field_values(task: ExtendedTask, document: Document, document_fields: dict, field_owners: dict) -> Dict:
        document_type = document.document_type
        fields_to_values = {}

        if not document_type:
            return fields_to_values

        field_code_aliases = document_type.field_code_aliases

        field_codes_to_fields = {f.code.lower(): f for f in document_type.fields.all()}

        if field_code_aliases:
            field_codes_to_fields.update({field_alias.lower(): field_codes_to_fields.get(field_code.lower())
                                          for field_alias, field_code in field_code_aliases.items() if
                                          field_alias and field_code})

        def _maybe_add_val(f, v, owner):
            if v is None:
                return
            v = DetectedFieldValue(f, v, user=owner)
            prev = fields_to_values.get(f)
            if not prev:
                fields_to_values[f] = [v]
            else:
                prev.append(v)

        for field_alias, field_value_text in document_fields.items():
            if field_value_text is None:
                continue

            field = field_codes_to_fields.get(field_alias.lower())
            if not field:
                task.log_warn(
                    'Field alias "{0}" not found for document type {1}'.format(field_alias, document_type.code))
                continue
            field_type_adapter = FIELD_TYPES_REGISTRY.get(field.type)  # type: FieldType
            field_owner = field_owners.get(field_alias)

            if type(field_value_text) is list:
                for possible_value_text in list(field_value_text):
                    maybe_value = field_type_adapter.extract_from_possible_value_text(field, possible_value_text)
                    _maybe_add_val(field, maybe_value, field_owner)
            else:
                maybe_value = field_type_adapter.extract_from_possible_value_text(field, field_value_text)
                _maybe_add_val(field, maybe_value, field_owner)

        return fields_to_values

    def process(self, **kwargs):
        self.log_info('Going to load document with fields...')

        document_name = kwargs.get('document_name')
        project = Project.objects.get(pk=kwargs.get('project_id'))  # type: Project
        run_detect_field_values = bool(kwargs.get('run_detect_field_values'))

        document_fields = kwargs.get('document_fields') or {}  # type: Dict
        if document_fields:
            document = Document(
                name=document_name,
                project=project,
                document_type=project.type,
                metadata={'parsed_by': None}
            )
            LoadDocumentWithFields.load_doc(self, document, document_fields, run_detect_field_values)

        path = kwargs['source_data']

        if path:
            self.log_info('Parse {0} at {1}'.format(path, file_access_handler))
            file_list = file_access_handler.list(path)

            self.log_info("Detected {0} files. Added {0} subtasks.".format(len(file_list)))

            if len(file_list) == 0:
                raise RuntimeError('Wrong file or directory name or directory is empty: {}'
                                   .format(path))
            load_docs_args = [(file_path, project.id, run_detect_field_values) for file_path in file_list]
            self.run_sub_tasks('Load Each Document',
                               LoadDocumentWithFields.create_document,
                               load_docs_args,
                               file_list)

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=3600,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError),
                 max_retries=3)
    def create_document(task: ExtendedTask, uri: str, project_id, run_detect_field_values):
        with file_access_handler.get_local_fn(uri) as (fn, file_name):
            task.task.title = 'Load Document: {0}'.format(uri)
            task.log_extra = {'log_document_name': uri}

            with open(fn, encoding='utf-8') as data_file:
                data = json.loads(data_file.read())
                project = Project.objects.get(pk=project_id)
                document_type = project.type
                document = Document(
                    name=file_name,
                    project=project,
                    document_type=document_type,
                    metadata={'parsed_by': None}
                )
                LoadDocumentWithFields.load_doc(task, document, data, run_detect_field_values)

    @staticmethod
    def load_doc(task: ExtendedTask, document: Document, document_fields: Dict, run_detect_field_values: bool,
                 filed_owners: dict = None):
        filed_owners = filed_owners if filed_owners else {}
        fields_to_values = LoadDocumentWithFields.load_field_values(task, document, document_fields, filed_owners)
        log = CeleryTaskLogger(task)

        with transaction.atomic():
            new_document = document.pk is None
            document.save(force_insert=new_document)
            if not new_document:
                DocumentFieldValue.objects \
                    .filter(document=document,
                            removed_by_user=False,
                            created_by__isnull=True,
                            modified_by__isnull=True) \
                    .delete()

            for field, values in fields_to_values.items():
                field_detection.save_detected_values(document, field, values)

            if run_detect_field_values:
                field_detection.detect_and_cache_field_values_for_document(log, document, True)
            else:
                dfvs = field_detection.detect_and_cache_field_values_for_document(log, document, False)
                field_value_cache.cache_field_values(document, dfvs, save=True)

        task.log_info('Loaded {0} field values for document #{1} ({2})'
                      .format(len(fields_to_values), document.pk, document.name))


class ImportSimpleFieldDetectionConfig(BaseTask):
    name = 'Import Simple Field Detection Config'
    soft_time_limit = 6000
    default_retry_delay = 10
    retry_backoff = True
    autoretry_for = (SoftTimeLimitExceeded, InterfaceError, OperationalError,)
    max_retries = 3

    def process(self,
                document_type: Dict,
                document_field: Dict,
                config_csv_file: Dict,
                drop_previous_field_detectors: bool,
                update_field_choice_values: bool,
                **kwargs):
        try:
            self.log_info('Going to configure simple field detection config...')
            document_type = DocumentType.objects.get(pk=document_type['pk'])
            document_field = DocumentField.objects.get(pk=document_field['pk'])
            csv_bytes = DbCache.get(config_csv_file['cache_key'])
            apply_simple_config(CeleryTaskLogger(self),
                                document_field,
                                document_type,
                                csv_bytes,
                                drop_previous_field_detectors,
                                update_field_choice_values)
        finally:
            DbCache.clean_cache(config_csv_file['cache_key'])


app.register_task(DetectFieldValues())
app.register_task(TrainDocumentFieldDetectorModel())
app.register_task(TrainDirtyDocumentFieldDetectorModel())
app.register_task(CacheDocumentFields())
app.register_task(TrainAndTest())
app.register_task(LoadDocumentWithFields())
app.register_task(ImportSimpleFieldDetectionConfig())
