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

from billiard.exceptions import SoftTimeLimitExceeded
from celery import shared_task
from psycopg2._psycopg import InterfaceError, OperationalError

import settings
from apps.document.field_detection import field_detection
from apps.document.field_detection.detect_field_values_params import DocDetectFieldValuesParams
from apps.document.models import DocumentType, Document
from apps.task.tasks import ExtendedTask, call_task_func, CeleryTaskLogger

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DetectFieldValues(ExtendedTask):
    name = 'Detect Field Values'

    def process(self,
                document_type: DocumentType = None,
                project_ids=list,
                document_name: str = None,
                existing_data_action='maintain',
                do_not_write=False,
                **kwargs):
        self.log_info("Going to detect document field values based on "
                      "the pre-coded regexps and field values entered by users...")

        do_not_run_for_modified_documents = existing_data_action == 'maintain'
        if isinstance(document_type, dict):
            document_type = DocumentType.objects.get(pk=document_type['pk'])

        # reindex document grid fields cache after detecting fields
        from apps.rawdb.tasks import auto_reindex_not_tracked
        doc_type_code = document_type.code \
            if document_type and hasattr(document_type, 'code') else None
        call_task_func(auto_reindex_not_tracked,
                       (doc_type_code,),
                       None,
                       queue=settings.CELERY_QUEUE_SERIAL,
                       run_after_sub_tasks_finished=True,
                       main_task_id=self.request.id)

        document_id = kwargs.get('document_id')
        if document_id:
            self.set_push_steps(1)
            dcptrs = DocDetectFieldValuesParams(document_id,
                                                False,
                                                kwargs.get('clear_old_values') or True,
                                                skip_modified_values=do_not_run_for_modified_documents)
            self.run_sub_tasks('Detect Field Values For Single Document',
                               DetectFieldValues.detect_field_values_for_document,
                               [(dcptrs,)])
            self.push()
            return

        task_count = 0
        document_types = [document_type] if document_type else DocumentType.objects.all()
        document_type_pks = []
        for document_type in document_types:
            if document_type.pk and document_type.fields.exists():
                document_type_pks.append(document_type.pk)
            else:
                self.log_info('Can not find any fields assigned to document type: {0}'.format(document_type))

        detect_field_values_for_document_args = []
        source_data = []

        document_ids = kwargs.get('document_ids')
        qs = Document.objects.filter(status__is_active=True)
        if document_name:
            qs = qs.filter(name=document_name)
        elif document_id:
            qs = qs.filter(pk=document_id)
        elif project_ids:
            qs = qs.filter(project_id__in=project_ids)
        elif document_type_pks:
            qs = qs.filter(document_type_id__in=document_type_pks)
        elif document_ids:
            qs = qs.filter(pk__in=document_ids)

        for doc_id, source, name in qs.values_list('id', 'source', 'name'):
            dcptrs = DocDetectFieldValuesParams(doc_id,
                                                do_not_write,
                                                kwargs.get('clear_old_values') or True,
                                                skip_modified_values=do_not_run_for_modified_documents)
            detect_field_values_for_document_args.append((dcptrs,))
            if source:
                source_data.append('{0}/{1}'.format(source, name))
            else:
                source_data.append(name)
            task_count += 1

        self.run_sub_tasks('Detect Field Values For Each Document',
                           DetectFieldValues.detect_field_values_for_document,
                           detect_field_values_for_document_args, source_data)
        if task_count > 0:
            self.log_info('Found {0} documents'.format(task_count))
        else:
            self.log_info('No documents found')

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=6000,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3)
    def detect_field_values_for_document(task: ExtendedTask,
                                         detect_ptrs: DocDetectFieldValuesParams):
        doc = Document.all_objects.get(pk=detect_ptrs.document_id)
        log = CeleryTaskLogger(task)

        # If the document is in one of completed statuses then
        # the detected values wont be stored even if do_not_write = False.
        # But caching should go as usual.
        dfvs = field_detection \
            .detect_and_cache_field_values_for_document(log,
                                                        doc,
                                                        changed_by_user=task.task.user,
                                                        save=not detect_ptrs.do_not_write,
                                                        clear_old_values=detect_ptrs.clear_old_values,
                                                        updated_field_codes=detect_ptrs.updated_field_codes,
                                                        skip_modified_values=detect_ptrs.skip_modified_values)

        task.log_info(f'Detected {len(dfvs)} field values for document ' +
                      f'#{detect_ptrs.document_id} ({doc.name})',
                      extra={Document.LOG_FIELD_DOC_ID: str(doc.pk),
                             Document.LOG_FIELD_DOC_NAME: doc.name})
