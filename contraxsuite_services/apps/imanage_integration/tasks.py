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

import json
import os
import uuid
from itertools import chain
from typing import List, Dict

from billiard.exceptions import SoftTimeLimitExceeded
from celery import shared_task
from celery.states import UNREADY_STATES
from django.db import connection
from django.utils import timezone
from django.utils.text import get_valid_filename
from django.utils.timezone import now
from psycopg2 import InterfaceError, OperationalError

from apps.celery import app
from apps.common.collection_utils import chunks
from apps.common.file_storage import get_file_storage
from apps.common.sql_commons import fetch_int, SQLClause
from apps.common.streaming_utils import buffer_contents_into_temp_file
from apps.document.tasks import plan_process_document_changed
from apps.imanage_integration.models import IManageConfig, IManageDocument
from apps.rawdb.signals import fire_document_fields_changed, DocumentEvent
from apps.task.models import Task
from apps.task.tasks import ExtendedTask, LoadDocuments, call_task
from apps.task.tasks import CeleryTaskLogger
from apps.users.user_utils import get_main_admin_user
from task_names import TASK_NAME_IMANAGE_TRIGGER_SYNC

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class IManageSynchronization(ExtendedTask):
    name = 'IManage Synchronization'
    soft_time_limit = 6000
    default_retry_delay = 10
    retry_backoff = True
    autoretry_for = (SoftTimeLimitExceeded, InterfaceError, OperationalError,)
    max_retries = 3

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=600,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError),
                 max_retries=0)
    def sync_imanage_document(task: ExtendedTask, imanage_config_id: int, imanage_doc_id: str):
        task.log_info('Synchronizing iManage document #{0} or config #{1}'.format(imanage_doc_id, imanage_config_id))
        imanage_doc = IManageDocument.objects \
            .filter(imanage_config_id=imanage_config_id, imanage_doc_id=imanage_doc_id) \
            .select_related('imanage_config').get()
        file_storage = get_file_storage()
        try:
            imanage_config = imanage_doc.imanage_config
            log = CeleryTaskLogger(task)
            project = imanage_config.resolve_dst_project(imanage_doc.imanage_doc_data, log)
            project_id = project.pk

            assignee = imanage_config.resolve_assignee(imanage_doc.imanage_doc_data, log)
            assignee_id = assignee.pk if assignee else None
            task.log_info('Assignee resolved to: {0}'.format(assignee.name if assignee else '<no assignee>'))

            task.log_info('Downloading iManage document contents into a temp file...')
            auth_token = imanage_config.login()
            filename, response = imanage_config.load_document(auth_token, imanage_doc_id)

            upload_session_id = str(uuid.uuid4())
            filename = get_valid_filename(filename)
            rel_filepath = os.path.join(upload_session_id, filename)

            _, ext = os.path.splitext(filename) if filename else None
            with buffer_contents_into_temp_file(response, ext) as temp_fn:

                # upload file to file storage
                with open(temp_fn, 'rb') as f:
                    file_storage.mk_doc_dir(upload_session_id)
                    file_storage.write_document(rel_filepath, f)

                kwargs = {
                    'document_type_id': imanage_config.document_type_id,
                    'project_id': project_id,
                    'assignee_id': assignee_id,
                    'user_id': get_main_admin_user().pk,
                    'propagate_exception': True,
                    'run_standard_locators': True,
                    'metadata': {},
                    'do_not_check_exists': True
                }
                if assignee_id:
                    kwargs['assign_date'] = now()

                pre_defined_fields = None
                if imanage_doc.imanage_doc_data and imanage_config.imanage_to_contraxsuite_field_binding:
                    pre_defined_fields = {}
                    for imanage_field_code, contraxsuite_field_code \
                            in dict(imanage_config.imanage_to_contraxsuite_field_binding).items():
                        imanage_field_value = imanage_doc.imanage_doc_data.get(imanage_field_code)
                        if imanage_field_value:
                            pre_defined_fields[contraxsuite_field_code] = imanage_field_value
                            task.log_info('Assigning iManage field {0} to Contraxsuite field {1}: {2}'
                                          .format(imanage_field_code, contraxsuite_field_code, imanage_field_value))
                        else:
                            task.log_info('iManage field {0} has no value assigned.'
                                          .format(imanage_field_code))
                else:
                    task.log_info('No binding of iManage fields to Contraxsuite fields.')

                document_id = LoadDocuments.create_document_local(
                    task=task,
                    file_path=temp_fn,
                    file_name=rel_filepath,
                    kwargs=kwargs,
                    pre_defined_doc_fields_code_to_val=pre_defined_fields)

                if document_id:
                    task.log_info('Created Contraxsuite document #{0}'.format(document_id))
                    imanage_doc.document_id = document_id
                    imanage_doc.last_sync_date = timezone.now()
                    imanage_doc.save(update_fields=['document_id', 'last_sync_date'])
                    # process document fields are changed event
                    if assignee_id:
                        old_field_values = {'assignee_id': None, 'assignee_name': None, 'assign_date': None}
                        new_field_values = {'assignee_id': assignee_id, 'assignee_name': assignee.name,
                                            'assign_date': kwargs.get('assign_date')}

                        fire_document_fields_changed(None,
                                                     log=log,
                                                     document_event=DocumentEvent.CHANGED.value,
                                                     document_pk=document_id,
                                                     field_handlers={},
                                                     fields_before=old_field_values,
                                                     fields_after=new_field_values,
                                                     changed_by_user=assignee)

                else:
                    task.log_error('Unable to create Contraxsuite document for '
                                   'iManage document #{0}'.format(imanage_doc_id))
                    raise RuntimeError('No document loaded.')
        except Exception as ex:
            task.log_error('Unable to synchronize iManage document #{0}'.format(imanage_doc_id), exc_info=ex)
            imanage_doc.import_problem = True
            imanage_doc.save(update_fields=['import_problem'])

    def sync_imanage_config(self, imanage_config: IManageConfig):
        auth_token = imanage_config.login()

        # Step 1: Find documents about which we don't know and store their ids in IManageDocument table
        imanage_docs = imanage_config.search_documents(auth_token)
        self.log_info('Found {0} documents at imanage server'.format(len(imanage_docs) if imanage_docs else None))

        with connection.cursor() as cursor:
            for docs_chunk in chunks(imanage_docs, 50):  # type: List[Dict]
                insert_clause = 'insert into "{table_name}" ' \
                                '(imanage_config_id, imanage_doc_id, imanage_doc_number, imanage_doc_data, ' \
                                ' import_problem) ' \
                                'values {values_place_holders} on conflict do nothing'.format(
                                    table_name=IManageDocument._meta.db_table,
                                    values_place_holders=', '.join(['(%s, %s, %s, %s, %s)'] * len(docs_chunk)))
                params = list(chain(*[(imanage_config.pk,
                                       str(doc['id']),
                                       str(doc.get('document_number')) if 'document_number' in doc else None,
                                       json.dumps(doc),
                                       False)
                                      for doc in docs_chunk]))
                cursor.execute(insert_clause, params)

        # Step 2. Get iManage doc ids for which we don't have Contraxsuite Documents created
        # Further we can add re-reading them from iManage by some logic
        args = [(imanage_config.id, imanage_doc_id) for imanage_doc_id in
                IManageDocument.objects.filter(imanage_config=imanage_config,
                                               import_problem=False,
                                               document__isnull=True).values_list('imanage_doc_id', flat=True)]
        imanage_config.last_sync_start = timezone.now()
        imanage_config.save(update_fields=['last_sync_start'])
        self.log_info('Found {0} new imanage documents for which we do not have Contraxsute documents'
                      .format(len(args) if args else 0))
        self.run_sub_tasks('Sync iManage documents for config: {0}'.format(imanage_config.code),
                           IManageSynchronization.sync_imanage_document, args)

    def process(self, **kwargs):
        if Task.objects \
                .exclude(id=self.request.id) \
                .filter(name=IManageSynchronization.name, status__in=UNREADY_STATES) \
                .exists():
            self.log_info('Previous IManage Synchronization task is still running. Exiting.')
            return

        imanage_config_dict = kwargs.get('imanage_config')
        auto = kwargs.get('auto')

        if auto:
            qr = IManageConfig.objects.raw('''select * from "{table_name}" where enabled = True 
            and (last_sync_start is null 
            or (last_sync_start + (sync_frequency_minutes::text||\' minute\')::INTERVAL) <= now())'''
                                           .format(table_name=IManageConfig._meta.db_table))
        else:
            if imanage_config_dict:
                qr = IManageConfig.objects.filter(pk=imanage_config_dict['pk'])
            else:
                qr = IManageConfig.objects.filter(enabled=True)

        found = False
        for imanage_config in list(qr):
            try:
                found = True
                self.sync_imanage_config(imanage_config)
            except Exception as ex:
                self.log_error('Unable to synchronize iManage config "{0}"'.format(imanage_config.code), exc_info=ex)
                return
        if not found:
            self.log_info('No enabled iManage configs matching the specified criteria found.')


UNREADY_STATE_TUPLE = tuple(UNREADY_STATES)


@shared_task(base=ExtendedTask,
             name=TASK_NAME_IMANAGE_TRIGGER_SYNC,
             bind=True,
             soft_time_limit=600,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError),
             max_retries=0)
def trigger_imanage_sync(_task: ExtendedTask):
    # SQL: Return 1 if there are enabled imanage configs last time processed too long ago
    # and there are no sync tasks pending.
    sql = SQLClause('''select case when ( 
    exists (select * from "{table_name}" where enabled = True 
    and (last_sync_start is null 
    or (last_sync_start + (sync_frequency_minutes::text||\' minute\')::INTERVAL) <= now()) 
    limit 1)
    and not exists (select * from "{task_table_name}" where name = %s and status in %s) 
    ) then 1 else 0 end   
    '''.format(table_name=IManageConfig._meta.db_table, task_table_name=Task._meta.db_table),
                    [IManageSynchronization.name, UNREADY_STATE_TUPLE])

    with connection.cursor() as cursor:
        if fetch_int(cursor, sql):
            call_task(IManageSynchronization.name, auto=True, module_name='apps.imanage_integration.tasks')


app.register_task(IManageSynchronization())
