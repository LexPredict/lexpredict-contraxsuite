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

import csv
import datetime
import io
import json
import re
from typing import Any, List, Set, Dict, Iterable, Tuple

import jiphy
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.urls import reverse
from django.utils.timezone import now
from psycopg2 import InterfaceError, OperationalError

from apps.celery import app
from apps.common.db_cache.db_cache import DbCache
from apps.common.file_storage import get_file_storage
from apps.common.log_utils import render_error
from apps.common.sql_commons import escape_column_name
from apps.document.async_tasks.detect_field_values_task import DetectFieldValues
from apps.document.field_types import FieldType
from apps.document.fields_detection import field_detection, field_detection_utils
from apps.document.fields_detection.fields_detection_abstractions import DetectedFieldValue
from apps.document.fields_detection.regexps_field_detection import apply_simple_config
from apps.document.fields_processing import field_value_cache
from apps.document.fields_processing.field_processing_utils import merge_document_field_values_to_python_value
from apps.document.models import DocumentType, Document, ClassifierModel, DocumentFieldValue, TextUnit, DocumentField
from apps.document.repository.document_bulk_delete import get_document_bulk_delete
from apps.document.sync_tasks.document_files_cleaner import DocumentFilesCleaner
from apps.dump.document_type_import import import_document_type
from apps.project.models import Project
from apps.rawdb.field_value_tables import adapt_table_structure
from apps.task.models import Task
from apps.task.tasks import BaseTask, ExtendedTask, CeleryTaskLogger, call_task
from apps.task.utils.task_utils import TaskUtils
from .constants import DOCUMENT_FIELD_CODE_MAX_LEN

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


MODULE_NAME = __name__


class TrainDocumentFieldDetectorModel(BaseTask):
    name = 'Train Document Field Detector Model'
    priority = 9

    def process(self, **kwargs):
        self.log_info(
            'Going to train field detector model based on the datasets stored in DB...')

        document_type = kwargs.get('document_type')

        if document_type:
            self.train_model_for_document_type(document_type['pk'])
        else:
            document_type_pks = DocumentType.objects.values_list('uid', flat=True)
            for document_type_pk in document_type_pks:
                self.train_model_for_document_type(document_type_pk)

    def train_model_for_document_type(self, document_type_pk: str) -> None:
        self.log_info('Building classifier model for document type: {0}'.format(document_type_pk))

        document_type = DocumentType.objects.get(pk=document_type_pk)

        train_model_for_field_args = []

        for field in document_type.fields.all():
            train_model_for_field_args.append((field.uid,))

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
    def train_model_for_field(task: ExtendedTask, field_uid: str) -> None:
        field = DocumentField.objects.get(pk=field_uid)
        new_model = field_detection \
            .train_document_field_detector_model(CeleryTaskLogger(task), field, None)  # type: ClassifierModel
        if new_model:
            ClassifierModel.objects.filter(document_field=field).delete()
            new_model.save()


class TrainDirtyDocumentFieldDetectorModel(BaseTask):
    name = 'Train Dirty Document Field Detector Model'

    def process(self, **kwargs):
        self.log_info(
            'Going to train dirty field detector model based on the datasets stored in DB...')

        dirty_fields = DocumentField.objects.get_dirty_fields()

        if dirty_fields:
            train_model_for_dirty_field_args = []

            for dirty_field in DocumentField.objects.get_dirty_fields():
                train_model_for_dirty_field_args.append((dirty_field.pk,))

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
                 max_retries=3,
                 priority=9)
    def train_model_for_dirty_field(task: ExtendedTask, dirty_field_id: Any) -> None:
        dirty_field = DocumentField.objects.get(pk=dirty_field_id)
        if dirty_field.can_retrain():
            dirty_field.dirty = False
            dirty_field.save()
            train_docs_count = field_detection_utils.get_approved_documents_number(dirty_field, None)
            if train_docs_count >= dirty_field.trained_after_documents_number:
                new_model = field_detection.train_document_field_detector_model(CeleryTaskLogger(task),
                                                                                dirty_field,
                                                                                None)
                if new_model:
                    ClassifierModel.objects.filter(document_field=dirty_field).delete()
                    new_model.save()


@app.task(name='advanced_celery.retrain_dirty_fields', bind=True)
def retrain_dirty_fields(self):
    TaskUtils.prepare_task_execution()
    if DocumentField.objects.has_dirty_fields():
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

        document_field_id = kwargs.get('document_field_id')
        skip_training = kwargs.get('skip_training')
        use_only_confirmed_field_values_for_training = kwargs.get('use_only_confirmed_field_values_for_training')
        train_data_project_ids = kwargs.get('train_data_project_ids')

        skip_testing = kwargs.get('skip_testing')
        use_only_confirmed_field_values_for_testing = kwargs.get('use_only_confirmed_field_values_for_testing')
        test_data_projects_ids = kwargs.get('test_data_projects_ids')

        field = DocumentField.objects.get(pk=document_field_id)

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
                                                     field,
                                                     train_data_project_ids,
                                                     use_only_confirmed_field_values_for_training)
            if new_model:
                ClassifierModel.objects.filter(document_field=field).delete()
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
                    .filter(project_id__in=test_data_projects_ids, document_type_id=field.document_type.pk) \
                    .values_list('pk', flat=True)
            else:
                test_document_ids = set(field_detection_utils
                                        .get_qs_active_modified_document_ids(field,
                                                                             test_data_projects_ids))
                test_document_ids.update(set(field_detection_utils
                                             .get_qs_finished_document_ids(field.document_type,
                                                                           test_data_projects_ids)))

            self.log_info('Testing field detection document-by-document...')
            test_tasks_args = []
            for test_document_id in test_document_ids:
                test_tasks_args.append((field.uid, test_document_id))

            if test_tasks_args:
                self.run_sub_tasks('Test Field Detector Model', TrainAndTest.test_field_detector_model,
                                   test_tasks_args)
                args_list = [(field.uid, new_model.pk if new_model else None)]
                self.run_after_sub_tasks_finished('Join Field Detector Model Tests',
                                                  TrainAndTest.join_field_detector_model_tests,
                                                  args_list)

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
            found_in_text = [dfv.text_unit.text
                             for dfv in expected_dfvs
                             if dfv.text_unit and dfv.text_unit.text] if expected_dfvs else []
            found_in_text_msg = ''
            if found_in_text:
                found_in_text_msg = '\nDetected in text:\n-----\n{0}\n-----'.format('\n---\n'.join(found_in_text))
            task.log_info('{3} Test doc: {0} (Doc id: {6}, Project: {5}). '
                          'Detected: {1}. Real: {2}.{4}'
                          .format(document.name,
                                  expected_field_value,
                                  actual_field_value,
                                  '[  OK  ]' if matches else '[ ERR  ]',
                                  found_in_text_msg,
                                  document.project.name if document.project else '',
                                  document.id))

        text_units_number = TextUnit.objects.filter(document=document, unit_type=field.text_unit_type).count()

        return {
            'text_units_number': text_units_number,
            'value_matches_expected': matches,
            'actual_field_value': actual_field_value if field.is_choice_field() else None
        }

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=600,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3,
                 priority=9)
    def join_field_detector_model_tests(task: ExtendedTask,
                                        field_uid,
                                        classifier_model_id):
        results = list(Task.objects \
                       .filter(main_task_id=task.request.parent_id,
                               name=TrainAndTest.test_field_detector_model.name)
                       .values_list('result', flat=True))

        test_text_units_number = 0
        match_number = 0
        test_doc_number = 0

        matches_per_value = dict()
        total_per_value = dict()

        for res in results:
            actual_field_value = res.get('actual_field_value')

            if actual_field_value:
                if actual_field_value not in total_per_value:
                    total_per_value[actual_field_value] = 0
                total_per_value[actual_field_value] += 1

            test_doc_number += 1
            test_text_units_number += (res.get('text_units_number') or 0)
            if res.get('value_matches_expected'):
                match_number += 1
                if actual_field_value:
                    if actual_field_value not in matches_per_value:
                        matches_per_value[actual_field_value] = 0
                    matches_per_value[actual_field_value] += 1

        accuracy = match_number / test_doc_number

        if classifier_model_id:
            classifier_model = ClassifierModel.objects.get(pk=classifier_model_id)
            classifier_model.field_detection_accuracy = accuracy
            classifier_model.save()

        field = DocumentField.objects.get(pk=field_uid)

        task.log_info('Testing finished.\n'
                      'Document type: {0}.\n'
                      'Field: {1}.\n'
                      'Text unit type: {2}.\n'
                      'Test documents number: {3}.\n'
                      'Test text units number: {4}.\n'
                      'Accuracy: {5}.\n'
                      .format(field.document_type.code,
                              field.code,
                              field.text_unit_type,
                              test_doc_number,
                              test_text_units_number,
                              accuracy))

        if field.is_choice_field():
            accuracy_per_value = {actual_field_value: (matches_per_value.get(actual_field_value) or 0) / total
                                  for actual_field_value, total in total_per_value.items()}
            task.log_info('Accuracy per value:\n{0}'.format(json.dumps(accuracy_per_value, sort_keys=True, indent=2)))


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
        for doc in Document.all_objects.filter(pk__in=doc_ids):
            log = CeleryTaskLogger(_task)
            field_value_cache.cache_generic_values(doc, log=log)
            suggested_values = field_detection.detect_and_cache_field_values_for_document(log, doc, False,
                                                                                          clear_old_values=False)
            field_value_cache.cache_field_values(doc, suggested_values, save=True, log=log)

    @classmethod
    def start_cache_document_fields_for_doc_ids(cls, task: ExtendedTask, ids: Iterable[Any]) -> None:
        doc_id_pack = set()
        for doc_id in ids:
            doc_id_pack.add(doc_id)
            if len(doc_id_pack) >= 10:
                task.run_sub_tasks('Cache field values for a set of documents',
                                   cls.cache_document_fields_for_doc_ids,
                                   [(list(doc_id_pack),)])
                doc_id_pack = set()
        if len(doc_id_pack) > 0:
            task.run_sub_tasks('Cache field values for a set of documents', cls.cache_document_fields_for_doc_ids,
                               [(list(doc_id_pack),)])

    def process(self, project: Project = None, **_kwargs):
        document_qs = Document.objects

        if project:
            document_qs = document_qs.filter(project__pk=project['pk'])

        self.start_cache_document_fields_for_doc_ids(self, document_qs.values_list('pk', flat=True))


class LoadDocumentWithFields(BaseTask):
    name = 'Load Document With Fields'
    soft_time_limit = 6000
    default_retry_delay = 10
    retry_backoff = True
    autoretry_for = (SoftTimeLimitExceeded, InterfaceError, OperationalError,)
    max_retries = 3
    priority = 9

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

            field = field_codes_to_fields.get(field_alias.lower())  # type: DocumentField
            if not field:
                task.log_warn(
                    'Field alias "{0}" not found for document type {1}'.format(field_alias, document_type.code))
                continue
            field_type_adapter = field.get_field_type()  # type: FieldType
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

        file_storage = get_file_storage()

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
            self.log_info('Parse {0} at {1}'.format(path, file_storage))
            file_list = file_storage.list_documents(path)

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
        file_storage = get_file_storage()
        with file_storage.get_document_as_local_fn(uri) as (fn, file_name):
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
                 field_owners: dict = None):
        field_owners = field_owners if field_owners else {}
        fields_to_values = LoadDocumentWithFields.load_field_values(task, document, document_fields, field_owners)
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
                field_detection.detect_and_cache_field_values_for_document(log, document, True, clear_old_values=False)
            else:
                dfvs = field_detection.detect_and_cache_field_values_for_document(log, document, False,
                                                                                  clear_old_values=False)
                field_value_cache.cache_field_values(document, dfvs, save=True, log=log)

        task.log_info('Loaded {0} field values for document #{1} ({2}): {3}'
                      .format(len(fields_to_values),
                              document.pk,
                              document.name,
                              ';\n'.join('{0}: {1}'.format(f.code, ', '.join([str(v.value) for v in l]) if l else '')
                                         for f, l in fields_to_values.items())))


class ImportCSVFieldDetectionConfig(BaseTask):
    name = 'Import CSV Field Detection Config'
    soft_time_limit = 6000
    default_retry_delay = 10
    retry_backoff = True
    autoretry_for = (SoftTimeLimitExceeded, InterfaceError, OperationalError,)
    max_retries = 3

    def process(self,
                document_field: Dict,
                config_csv_file: Dict,
                drop_previous_field_detectors: bool,
                update_field_choice_values: bool,
                csv_contains_regexps: bool,
                **kwargs):
        try:
            self.log_info('Going to configure simple field detection config...')
            document_field = DocumentField.objects.get(pk=document_field['pk'])
            csv_bytes = DbCache.get(config_csv_file['cache_key'])
            apply_simple_config(CeleryTaskLogger(self),
                                document_field,
                                csv_bytes,
                                drop_previous_field_detectors,
                                update_field_choice_values,
                                csv_contains_regexps=csv_contains_regexps)
        finally:
            DbCache.clean_cache(config_csv_file['cache_key'])


class FindBrokenDocumentFieldValues(BaseTask):
    name = 'Find Broken Document Field Values'

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=3600,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError),
                 max_retries=3)
    def check_document_field_values(task: ExtendedTask, dfv_ids: Set, delete_broken: bool = False):

        for dfv in DocumentFieldValue.objects \
                .filter(pk__in=dfv_ids) \
                .select_related('field'):  # type: DocumentFieldValue
            try:
                temp_value = dfv.python_value
                if temp_value is not None:
                    field = dfv.field
                    if field.is_choice_field() and not field.is_choice_value(temp_value):
                        raise ValueError('Field value {0} is not in list of its choice values:\n{1}'
                                         .format(temp_value, field.choices))
            except:
                if delete_broken:
                    dfv.delete()
                    msg = render_error('Found broken document field value.\n'
                                       'Document field value id: {0}\n'
                                       'DB value: {1}\n'
                                       'The document field value has been deleted.\n'
                                       .format(dfv.pk, dfv.value))
                else:
                    content_type = ContentType.objects.get_for_model(DocumentFieldValue)
                    dfv_admin_url = reverse("admin:%s_%s_change" %
                                            (content_type.app_label, content_type.model), args=(dfv.pk,))
                    msg = render_error('Found broken document field value.\n'
                                       'Document field value id: {0}\n'
                                       'DB value: {1}\n'
                                       'Admin URL: {2}\n'.format(dfv.pk, dfv.value, dfv_admin_url))
                task.log_info(msg)

    def process(self, **kwargs):
        document_field_arg = kwargs.get('document_field')
        document_field_id = document_field_arg['pk'] if document_field_arg else None

        delete_broken = kwargs.get('delete_broken')

        dfv_qs = DocumentFieldValue.objects

        if document_field_id:
            dfv_qs = dfv_qs.filter(field_id=document_field_id)
        else:
            dfv_qs = dfv_qs.all()

        dfv_ids = set()
        total_num = dfv_qs.count()
        count = 0
        for dfv_id in dfv_qs.values_list('pk', flat=True):
            count += 1
            if len(dfv_ids) >= 100:
                self.log_info('Sub-tasks started for {0} document field values of {1}'.format(count, total_num))
                self.run_sub_tasks('Check document field values', self.check_document_field_values,
                                   [(list(dfv_ids), delete_broken)])
                dfv_ids = set()
            else:
                dfv_ids.add(dfv_id)

        if len(dfv_ids) > 0:
            self.run_sub_tasks('Check document field values', self.check_document_field_values,
                               [(list(dfv_ids), delete_broken)])
            self.log_info('Sub-tasks started for {0} document field values of {1}'.format(count, total_num))


class ImportDocumentType(BaseTask):
    name = 'Import Document Type'
    soft_time_limit = 3600
    default_retry_delay = 10
    retry_backoff = True
    autoretry_for = (SoftTimeLimitExceeded, InterfaceError, OperationalError,)
    max_retries = 3

    def process(self,
                document_type_config_csv_file: Dict,
                action: str,
                update_cache: bool,
                **kwargs):

        if action == 'validate':
            save = False
            auto_fix_validation_errors = False
            remove_missed_objects = False
        elif action == 'validate|import':
            save = True
            auto_fix_validation_errors = False
            remove_missed_objects = False
        elif action == 'import|auto_fix|retain_missing_objects':
            save = True
            auto_fix_validation_errors = True
            remove_missed_objects = False
        elif action == 'import|auto_fix|remove_missing_objects':
            save = True
            auto_fix_validation_errors = True
            remove_missed_objects = True
        else:
            raise RuntimeError('Unknown action')

        try:
            json_bytes = DbCache.get(document_type_config_csv_file['cache_key'])
            document_type = import_document_type(json_bytes=json_bytes,
                                                 save=save,
                                                 auto_fix_validation_errors=auto_fix_validation_errors,
                                                 remove_missed_in_dump_objects=remove_missed_objects,
                                                 task=self)
        finally:
            DbCache.clean_cache(document_type_config_csv_file['cache_key'])

        if save and update_cache:
            from apps.rawdb.app_vars import APP_VAR_DISABLE_RAW_DB_CACHING
            if not APP_VAR_DISABLE_RAW_DB_CACHING.val:
                self.log_info('Adapting RawDB table structure after import ...')
                adapt_table_structure(CeleryTaskLogger(self), document_type, force=False)
            ids = Document.all_objects.filter(document_type=document_type).values_list('pk', flat=True)
            self.log_info('Caching document field values ...')
            CacheDocumentFields.start_cache_document_fields_for_doc_ids(self, ids)


class FixDocumentFieldCodes(BaseTask):
    name = 'Fix Document Field Codes'
    priority = 9

    RE_FIELD_CODE_NUM = re.compile(r'(.*)_(\d+)')

    def process(self, **kwargs):

        with transaction.atomic():

            csv_log = list()  # type: List[Tuple[str, str, str]]
            for document_type in DocumentType.objects.all():  # type: DocumentType
                changed_field_codes = dict()  # type: Dict[str, str]
                field_code_use_counts = dict()  # type: Dict[str, int]

                for code in DocumentField.objects \
                        .filter(document_type=document_type) \
                        .order_by('order', 'code') \
                        .values_list('code', flat=True):
                    field_code_use_counts[code] = 1
                    m = self.RE_FIELD_CODE_NUM.fullmatch(code)
                    if m:
                        base = m.group(1)
                        num = int(m.group(2))
                        old_num = field_code_use_counts.get(base) or 0
                        field_code_use_counts[base] = max(old_num, num)

                for field in DocumentField.objects \
                        .filter(document_type=document_type) \
                        .order_by('order', 'code'):  # type: DocumentField
                    field_code_escaped = escape_column_name(field.code)[:DOCUMENT_FIELD_CODE_MAX_LEN]

                    if field.code == field_code_escaped:
                        field_code_use_counts[field.code] = (field_code_use_counts.get(field.code) or 0) + 1
                        long_code = DocumentField.get_long_code(field, document_type)
                        if field.long_code != long_code:
                            self.log_info('Updating field long code {0} to {1}'
                                          .format(field.long_code, long_code))
                            field.long_code = long_code
                            field.save(update_fields={'long_code'})
                    else:
                        field_code_use_count = field_code_use_counts.get(field_code_escaped)
                        if field_code_use_count is not None:
                            field_code_use_counts[field_code_escaped] = field_code_use_count + 1
                            counter_str = str(field_code_use_count)

                            # make next repeated column name to be column1, column2, ...
                            # make it fitting into N chars by cutting the field code on the required
                            # number of chars to fit the num
                            field_code_escaped = field_code_escaped[:DOCUMENT_FIELD_CODE_MAX_LEN - len(counter_str) - 1] \
                                                 + '_' + counter_str
                        else:
                            field_code_use_counts[field_code_escaped] \
                                = (field_code_use_counts.get(field_code_escaped) or 0) + 1

                        self.log_info('Updating field {0}.{1} to {2}'
                                      .format(document_type.code, field.code, field_code_escaped))
                        changed_field_codes[field.code] = field_code_escaped
                        csv_log.append((document_type.code, field.code, field_code_escaped))
                        field.code = field_code_escaped

                        field.long_code = DocumentField.get_long_code(field, document_type)

                        field.save(update_fields={'code', 'long_code'})

                    hide_until_js = jiphy.to.javascript(field.hide_until_python) if field.hide_until_python else ''
                    if hide_until_js != field.hide_until_js:
                        field.hide_until_js = hide_until_js
                        self.log_info('Updating hide_until_js for field {0}.{1}'
                                      .format(document_type.code, field.code))
                        field.save(update_fields={'hide_until_js'})

                if len(changed_field_codes) > 0 and document_type.field_code_aliases:
                    updated_aliases = {k: changed_field_codes.get(v) or v
                                       for k, v in document_type.field_code_aliases.items()}
                    self.log_info('Updating field code aliases of document type {0}"\n{1}'
                                  .format(document_type.code, updated_aliases))
                    document_type.field_code_aliases = updated_aliases
                    document_type.save(update_fields={'field_code_aliases'})

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(('Document Type', 'Old Field Code', 'New Field Code'))
        for r in csv_log:
            writer.writerow(r)
        self.log_info('\n\n\n------------------\n'
                      'Changed fields csv:\n' + output.getvalue() + '\n------------------')


class DeleteDocuments(BaseTask):
    name = 'Delete Documents'
    priority = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.document.repository.document_repository import default_document_repository
        self.document_repository = default_document_repository

    def process(self, **kwargs):
        doc_ids = kwargs.get('_document_ids')
        file_paths = self.document_repository.get_all_document_source_paths(doc_ids)
        get_document_bulk_delete().delete_documents(doc_ids)
        try:
            DocumentFilesCleaner.delete_document_files(file_paths)
        except Exception as e:
            self.log_error(e)


app.register_task(DetectFieldValues())
app.register_task(TrainDocumentFieldDetectorModel())
app.register_task(TrainDirtyDocumentFieldDetectorModel())
app.register_task(CacheDocumentFields())
app.register_task(TrainAndTest())
app.register_task(LoadDocumentWithFields())
app.register_task(ImportCSVFieldDetectionConfig())
app.register_task(FindBrokenDocumentFieldValues())
app.register_task(ImportDocumentType())
app.register_task(FixDocumentFieldCodes())
app.register_task(DeleteDocuments())
