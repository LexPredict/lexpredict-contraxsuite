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

from typing import Dict, Any

from billiard.exceptions import SoftTimeLimitExceeded
from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from psycopg2._psycopg import InterfaceError, OperationalError

from django.conf import settings

from apps.common.models import Action, get_default_status
from apps.document.constants import DOCUMENT_TYPE_CODE_GENERIC_DOCUMENT
from apps.document.field_detection import field_detection
from apps.document.field_detection.detect_field_values_params import DocDetectFieldValuesParams
from apps.document.models import DocumentType, Document
from apps.project.models import Project
from apps.task.tasks import ExtendedTask, call_task_func, CeleryTaskLogger

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
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

        reset_document_status = existing_data_action == 'delete'
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
                                                skip_modified_values=do_not_run_for_modified_documents,
                                                reset_document_status=reset_document_status)
            self.run_sub_tasks('Detect Field Values For Single Document',
                               DetectFieldValues.detect_field_values_for_document,
                               [(dcptrs.to_dict(),)])
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
        elif document_ids:
            qs = qs.filter(pk__in=document_ids)
        elif project_ids:
            qs = qs.filter(project_id__in=project_ids)
        elif document_type_pks:
            qs = qs.filter(document_type_id__in=document_type_pks)

        for doc_id, source, name in qs.values_list('id', 'source', 'name'):
            dcptrs = DocDetectFieldValuesParams(doc_id,
                                                do_not_write,
                                                kwargs.get('clear_old_values') or True,
                                                skip_modified_values=do_not_run_for_modified_documents,
                                                reset_document_status=reset_document_status)
            detect_field_values_for_document_args.append((dcptrs.to_dict(),))
            if source:
                source_data.append('{0}/{1}'.format(source, name))
            else:
                source_data.append(name)
            task_count += 1

        project_ids_list = list(set(qs.values_list('project_id', flat=True)))

        for project_id in project_ids_list:
            Action.objects.create(name='Detected Field Values',
                                  message=f'Detect Field Values task started for project '
                                          f'"{Project.objects.get(id=project_id).name}"',
                                  user_id=self.task.user_id,
                                  view_action='update',
                                  content_type=ContentType.objects.get_for_model(Project),
                                  model_name='Project',
                                  app_label='project',
                                  object_pk=project_id)

        self.run_sub_tasks('Detect Field Values For Each Document',
                           DetectFieldValues.detect_field_values_for_document,
                           detect_field_values_for_document_args, source_data)

        self.run_after_sub_tasks_finished(
            'Notify on Detect Field Values finished',
            DetectFieldValues.notify_on_completed_detect_action,
            [(project_ids_list, self.task.user_id)])

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
                                         detect_ptrs: Dict[str, Any]):
        detect_ptrs = DocDetectFieldValuesParams.wrap(detect_ptrs)
        doc = Document.all_objects.get(pk=detect_ptrs.document_id)
        log = CeleryTaskLogger(task)

        # If the document is in one of completed statuses then
        # the detected values wont be stored even if do_not_write = False.
        # But caching should go as usual.

        if detect_ptrs.reset_document_status:
            doc.status_id = get_default_status()
            doc.save()

        dfvs = field_detection \
            .detect_and_cache_field_values_for_document(
                log,
                doc,
                changed_by_user=task.task.user,
                save=not detect_ptrs.do_not_write,
                clear_old_values=detect_ptrs.clear_old_values,
                updated_field_codes=detect_ptrs.updated_field_codes,
                skip_modified_values=detect_ptrs.skip_modified_values,
                task=field_detection.detect_and_cache_field_values_for_document,
                reset_document_status=detect_ptrs.reset_document_status)

        task.log_info(f'Detected {len(dfvs)} field values for document ' +
                      f'#{detect_ptrs.document_id} ({doc.name})',
                      extra={Document.LOG_FIELD_DOC_ID: str(doc.pk),
                             Document.LOG_FIELD_DOC_NAME: doc.name})
        action_user_id = getattr(task.task.user, 'id', None) \
            or getattr(task.task.main_task.user, 'id', None)
        Action.objects.create(name='Detected Field Values',
                              message=f'Detect Field Values task is finished for project '
                                      f'"{doc.project.name}" with the result of {len(dfvs)} field '
                                      f'values',
                              user_id=action_user_id,
                              view_action='update',
                              content_type=ContentType.objects.get_for_model(Project),
                              model_name='Project',
                              app_label='project',
                              object_pk=doc.project_id)

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=3600,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3)
    def notify_on_completed_detect_action(_self,
                                          project_ids: list,
                                          user_id: int):
        from apps.notifications.models import WebNotificationMessage, WebNotificationTypes
        notifications = []
        for project_id in project_ids:
            project = Project.all_objects.get(id=project_id)
            message_data = {
                'project': project.name,
            }
            notification_type = WebNotificationTypes.FIELD_VALUE_DETECTION_COMPLETED
            message_data = notification_type.check_message_data(message_data)
            redirect_link = {
                'type': notification_type.redirect_link_type(),
                'params': {
                    'project_type': 'batch_analysis'
                        if project.type.code == DOCUMENT_TYPE_CODE_GENERIC_DOCUMENT
                        else 'contract_analysis',
                    'project_id': project.pk
                },
            }
            recipients = [user_id, ]
            notifications.append((message_data, redirect_link, notification_type,
                                  recipients))
        WebNotificationMessage.bulk_create_notification_messages(notifications)
