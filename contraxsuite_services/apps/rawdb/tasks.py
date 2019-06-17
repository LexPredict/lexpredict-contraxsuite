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

import traceback
from typing import Set, Generator, List, Any

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from django.db import connection
from django.db.models import Q
from psycopg2 import InterfaceError, OperationalError

from apps.common.log_utils import ProcessLogger
from apps.document.models import Document, DocumentType
from apps.rawdb.field_value_tables import (
    cache_document_fields, adapt_table_structure, doc_fields_table_name)
from apps.task.tasks import ExtendedTask, CeleryTaskLogger, Task, purge_task, call_task_func
from apps.rawdb.app_vars import APP_VAR_DISABLE_RAW_DB_CACHING

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.2/LICENSE"
__version__ = "1.2.2"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


this_module_name = __name__


def _get_reindex_task_name():
    return this_module_name + '.' + cache_document_fields_for_doc_ids_tracked.__name__


def there_are_non_indexed_docs_not_planned_to_index(
        document_type: DocumentType,
        log: ProcessLogger) -> bool:
    for doc_id in non_indexed_doc_ids_not_planned_to_index(document_type, 1):
        if doc_id:
            task_name = _get_reindex_task_name()
            fields_table = doc_fields_table_name(document_type.code)
            log.info(f'there_are_non_indexed_docs_not_planned_to_index: '
                     f'found document id={doc_id} of type {document_type.code}, '
                     f'task {task_name}. Fields table: {fields_table}')
            return True
    return False


def non_indexed_doc_ids_not_planned_to_index(
        document_type: DocumentType, pack_size: int = 100) -> Generator[List[int], None, None]:

    table_name = doc_fields_table_name(document_type.code)

    with connection.cursor() as cursor:
        # return documents of the specified type which
        # - do not exist in the corresponding fields cache
        # - have no planned but not-started reindex tasks on them
        cursor.execute('select dd.id \n'
                       'from document_document dd \n'
                       'left outer join "{table_name}" df on dd.id = df.document_id \n'
                       'left outer join lateral (select jsonb_array_elements(args->0) doc_id \n'
                       '                         from task_task \n'
                       '                         where name = %s \n'
                       '                         and own_status = %s\n'
                       '                         and date_work_start is null) tt on tt.doc_id = to_jsonb(dd.id) \n'
                       'where dd.document_type_id = %s and df.document_id is null and tt.doc_id is null'
                       .format(table_name=table_name), [_get_reindex_task_name(), 'PENDING', document_type.uid])

        rows = cursor.fetchmany(pack_size)
        while rows:
            yield [row[0] for row in rows]
            rows = cursor.fetchmany(pack_size)


def get_all_doc_ids(document_type_id, pack_size: int = 100) -> Generator[List[int], None, None]:
    with connection.cursor() as cursor:
        cursor.execute('select id from document_document where document_type_id = %s', [document_type_id])

        rows = cursor.fetchmany(pack_size)
        while rows:
            yield [row[0] for row in rows]
            rows = cursor.fetchmany(pack_size)


def _get_all_doc_ids_not_planned_to_index(query_filter: str, params: list, pack_size: int)\
        -> Generator[List[int], None, None]:
    with connection.cursor() as cursor:
        cursor.execute('select d.id from document_document d \n'
                       'left outer join lateral (select jsonb_array_elements(args->0) doc_id \n'
                       '                         from task_task \n'
                       '                         where name = %s \n'
                       '                         and own_status = %s\n'
                       '                         and date_work_start is null) tt on tt.doc_id = to_jsonb(d.id) \n'
                       'where {0} and tt.doc_id is null'.format(query_filter),
                       [_get_reindex_task_name(), 'PENDING'] + params)

        rows = cursor.fetchmany(pack_size)
        while rows:
            yield [row[0] for row in rows]
            rows = cursor.fetchmany(pack_size)


def get_all_doc_ids_not_planned_to_index_by_doc_type(document_type_id: Any, pack_size: int = 100) \
        -> Generator[List[int], None, None]:
    return _get_all_doc_ids_not_planned_to_index('d.document_type_id = %s', [document_type_id], pack_size)


def get_all_doc_ids_not_planned_to_index_by_project_pk(project_pk: Any, pack_size: int = 100) \
        -> Generator[List[int], None, None]:
    return _get_all_doc_ids_not_planned_to_index('d.project_id = %s', [project_pk], pack_size)


def get_all_doc_ids_not_planned_to_index_by_assignee_pk(assignee_pk: Any, pack_size: int = 100) \
        -> Generator[List[int], None, None]:
    return _get_all_doc_ids_not_planned_to_index('d.assignee_id = %s', [assignee_pk], pack_size)


def get_all_doc_ids_not_planned_to_index_by_status_pk(status_pk: Any, pack_size: int = 100) \
        -> Generator[List[int], None, None]:
    return _get_all_doc_ids_not_planned_to_index('d.status_id = %s', [status_pk], pack_size)


@shared_task(base=ExtendedTask,
             name=settings.TASK_NAME_MANUAL_REINDEX,
             bind=True,
             soft_time_limit=6000,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
             max_retries=3)
def manual_reindex(task: ExtendedTask,
                   document_type_code: str = None,
                   force: bool = False):
    if APP_VAR_DISABLE_RAW_DB_CACHING.val:
        task.log_info('Document caching to raw tables is disabled in Commons / App Vars')
        return
    msg = f'manual_reindex called for {document_type_code}. ' \
          f'Task: {task.task_name}, main id: {task.main_task_id}'
    log = CeleryTaskLogger(task)
    log.info(msg)
    adapt_tables_and_reindex(task, document_type_code, force, True)


def _reindex_document_ids_packets(task: ExtendedTask, ids_packets: Generator[List[int], None, None]) -> None:
    reindex_task_name = 'Reindex set of documents'
    args = []
    for ids in ids_packets:
        args.append((ids,))
        if len(args) >= 100:
            task.run_sub_tasks(reindex_task_name, cache_document_fields_for_doc_ids_tracked, args)
            args = []
    task.run_sub_tasks(reindex_task_name, cache_document_fields_for_doc_ids_tracked, args)


@shared_task(base=ExtendedTask,
             name=settings.TASK_NAME_UPDATE_PROJECT_DOCUMENTS,
             bind=True,
             soft_time_limit=6000,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
             max_retries=3)
def update_project_documents(task: ExtendedTask, project_pk: Any) -> None:
    if APP_VAR_DISABLE_RAW_DB_CACHING.val:
        task.log_info('Document caching to raw tables is disabled in Commons / App Vars')
        return
    _reindex_document_ids_packets(task, get_all_doc_ids_not_planned_to_index_by_project_pk(project_pk, 20))


@shared_task(base=ExtendedTask,
             name=settings.TASK_NAME_UPDATE_ASSIGNEE_FOR_DOCUMENTS,
             bind=True,
             soft_time_limit=6000,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
             max_retries=3)
def update_assignee_for_documents(task: ExtendedTask, assignee_pk: Any) -> None:
    if APP_VAR_DISABLE_RAW_DB_CACHING.val:
        task.log_info('Document caching to raw tables is disabled in Commons / App Vars')
        return
    _reindex_document_ids_packets(task, get_all_doc_ids_not_planned_to_index_by_assignee_pk(assignee_pk, 20))


@shared_task(base=ExtendedTask,
             name=settings.TASK_NAME_UPDATE_STATUS_NAME_FOR_DOCUMENTS,
             bind=True,
             soft_time_limit=6000,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
             max_retries=3)
def update_status_name_for_documents(task: ExtendedTask, status_pk: Any) -> None:
    if APP_VAR_DISABLE_RAW_DB_CACHING.val:
        task.log_info('Document caching to raw tables is disabled in Commons / App Vars')
        return
    _reindex_document_ids_packets(task, get_all_doc_ids_not_planned_to_index_by_status_pk(status_pk, 20))


def any_other_reindex_task(self_task_id, document_type_code: str):
    return Task.objects.unready_main_tasks() \
        .filter(name__in={settings.TASK_NAME_AUTO_REINDEX, settings.TASK_NAME_MANUAL_REINDEX}) \
        .exclude(pk=self_task_id) \
        .filter(Q(kwargs__document_type_code=document_type_code)
                | Q(kwargs__document_type_code__isnull=True))


@shared_task(base=ExtendedTask,
             name=settings.TASK_NAME_AUTO_REINDEX,
             bind=True,
             soft_time_limit=6000,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
             max_retries=3)
def auto_reindex_not_tracked(task: ExtendedTask,
                             document_type_code: str = None,
                             force: bool = False):
    if APP_VAR_DISABLE_RAW_DB_CACHING.val:
        return
    document_types = [DocumentType.objects.get(code=document_type_code)] \
        if document_type_code is not None else DocumentType.objects.all()
    log = CeleryTaskLogger(task)

    task_model = task.task

    for document_type in document_types:
        reindex_needed = adapt_table_structure(log, document_type, force=force)
        if reindex_needed:
            force_fmt = ', forced' if force else ''
            task.log_info(f'Re-index from auto_reindex_not_tracked, {task.name}, '
                          f'for {document_type}{force_fmt}')
            call_task_func(manual_reindex, (document_type.code, False), task_model.user_id)
        else:
            if there_are_non_indexed_docs_not_planned_to_index(document_type, log) \
                    and not any_other_reindex_task(task.request.id, document_type.code).exists():
                task.log_info(f'auto_reindex_not_tracked({document_type.code}): '
                              f'there_are_non_indexed_docs_not_planned_to_index')
                call_task_func(manual_reindex,
                               (document_type.code, False),
                               task_model.user_id)


def adapt_tables_and_reindex(task: ExtendedTask,
                             document_type_code: str = None,
                             force_recreate_tables: bool = False,
                             force_reindex: bool = False):
    """
    "RawDB: Reindex" task
    Checks if raw table with field values of doc type needs to be altered according to the changed
    field structure and triggers document reindexing if needed.

    This task should be always executed in the "serial" queue (used for Celery Beat) to avoid parallel modifications
    on the same table.
    See settings.py/CELERY_BEAT_SCHEDULE
    :param task:
    :param document_type_code: Document type code or None to check all doc types.
    :param force_recreate_tables: Force re-creating tables and re-indexing from scratch.
    :param force_reindex: Force re-indexing of all docs even if the table was not altered.
    :return:
    """
    document_types = [DocumentType.objects.get(code=document_type_code)] \
        if document_type_code is not None else DocumentType.objects.all()
    log = CeleryTaskLogger(task)

    for document_type in document_types:
        reindex_needed = adapt_table_structure(log,
                                               document_type,
                                               force=force_recreate_tables)

        if force_recreate_tables:
            # If "force" is requested - we cancel all currently planned re-index tasks
            # and plan (re-plan) reindexing for all documents of this task.
            for prev_task in any_other_reindex_task(task.request.id, document_type.code):
                purge_task(prev_task)
            args = [(ids,) for ids in get_all_doc_ids(document_type.uid, 20)]
            task.log_info(f'Initiating re-index for all documents of {document_type.code} ' +
                          f' - forced tables recreating.')
            task.run_sub_tasks('Reindex set of documents',
                               cache_document_fields_for_doc_ids_tracked,
                               args)
        elif reindex_needed or force_reindex:
            comment = 'forced' if force_reindex else 'reindex needed'
            task.log_info(f'Raw DB table for document type {document_type.code} ' +
                          f'has been altered ({comment}), task "{task.task_name}".\n' +
                          f'Initiating re-index for all documents of this document type.')
            # If we altered the field structure then we need to re-index all docs of this type.
            # If no need to force - we plan re-index tasks only
            # for those documents for which they are not planned yet
            args = [(ids,) for ids in get_all_doc_ids_not_planned_to_index_by_doc_type(document_type.uid, 20)]
            task.run_sub_tasks('Reindex set of documents',
                               cache_document_fields_for_doc_ids_tracked, args)
        else:
            # If we did not alter the table but there are non-indexed docs fo this type
            # then we trigger the re-index task making it index non-indexed docs only.
            # In this case we don't stop other re-index tasks. But we can be stopped further in case of
            # full reindex.

            # It makes sense to only plan re-indexing for those docs which are:
            # - not indexed
            # - have no re-index planned for them
            task.log_info(f'Initiating re-index for all documents of {document_type.code} ' +
                          f' - index not planned.')
            args = [(ids,) for ids in non_indexed_doc_ids_not_planned_to_index(document_type, 20)]
            task.run_sub_tasks('Reindex set of documents', cache_document_fields_for_doc_ids_tracked, args)


def cache_document_fields_for_doc_ids(task: ExtendedTask, doc_ids: Set):
    # This task is added to exclude-from-tracking list and is not seen in task list at /advanced
    # Also if running it as a aub-task it will not participate in the parent task's progress.
    log = CeleryTaskLogger(task)
    for doc in Document.all_objects.filter(pk__in=doc_ids) \
            .select_related('document_type', 'assignee', 'status'):  # type: Document
        cache_document_fields(log, doc)


@shared_task(base=ExtendedTask,
             bind=True,
             soft_time_limit=6000,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
             max_retries=3)
def cache_document_fields_for_doc_ids_not_tracked(task: ExtendedTask, doc_ids: Set):
    cache_document_fields_for_doc_ids(task, doc_ids)


@shared_task(base=ExtendedTask,
             bind=True,
             soft_time_limit=6000,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
             max_retries=3)
def cache_document_fields_for_doc_ids_tracked(task: ExtendedTask, doc_ids: Set):
    cache_document_fields_for_doc_ids(task, doc_ids)


def get_brief_call_stack() -> str:
    lines = []  # type: List[str]
    for line in traceback.format_stack():
        if 'site-packages' not in line:
            lines.append(line.strip())
    return '\n'.join(lines)
