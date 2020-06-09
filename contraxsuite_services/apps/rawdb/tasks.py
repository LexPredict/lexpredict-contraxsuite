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

from typing import Generator, List, Any, Iterable, Optional

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from celery.states import PENDING
from django.db import connection
from django.db.models import Q
from psycopg2 import InterfaceError, OperationalError

from apps.common.collection_utils import chunks
from apps.common.log_utils import ProcessLogger
from apps.document.models import Document, DocumentType
from apps.document.constants import FieldSpec
from apps.rawdb.constants import DOC_NUM_PER_SUB_TASK, DOC_NUM_PER_MAIN_TASK
from apps.rawdb.field_value_tables import (
    adapt_table_structure)
from apps.rawdb.repository.raw_db_repository import doc_fields_table_name
from apps.rawdb.field_value_tables import cache_document_fields
from apps.task.tasks import ExtendedTask, CeleryTaskLogger, Task, purge_task, call_task_func
from apps.users.models import User
import task_names

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


this_module_name = __name__


def _get_reindex_task_name():
    return this_module_name + '.' + cache_document_fields_for_doc_ids_tracked.__name__


def there_are_non_indexed_docs_not_planned_to_index(
        document_type: DocumentType,
        log: ProcessLogger) -> bool:
    for doc_id in non_indexed_doc_ids_not_planned_to_index_by_doc_type(document_type, 1):
        if doc_id:
            task_name = _get_reindex_task_name()
            fields_table = doc_fields_table_name(document_type.code)
            log.info(f'there_are_non_indexed_docs_not_planned_to_index: '
                     f'found document id={doc_id} of type {document_type.code}, '
                     f'task {task_name}. Fields table: {fields_table}')
            return True
    return False


def non_indexed_doc_ids_not_planned_to_index_by_doc_type(
        document_type: DocumentType, pack_size: int = 100) -> Generator[List[int], None, None]:
    yield from get_non_indexed_doc_ids_not_planned_to_index_by_predicate(
        document_type.code,
        f"dd.document_type_id = '{document_type.uid}'",
        pack_size)


def non_indexed_doc_ids_not_planned_to_index_by_project(
        document_type: DocumentType,
        project_id: int,
        pack_size: int = 100) -> Generator[List[int], None, None]:
    yield from get_non_indexed_doc_ids_not_planned_to_index_by_predicate(
        document_type.code,
        f"dd.project_id = '{project_id}'",
        pack_size)


def get_non_indexed_doc_ids_not_planned_to_index_by_predicate(
        doc_type_code: str,
        predicate: str,
        pack_size: int = 100) -> Generator[List[int], None, None]:
    table_name = doc_fields_table_name(doc_type_code)

    with connection.cursor() as cursor:
        # return documents of the specified type which
        # - do not exist in the corresponding fields cache
        # - have no planned but not-started reindex tasks on them
        cursor.execute('select dd.id \n'
                       'from document_document dd \n'
                       f'left outer join "{table_name}" df on dd.id = df.document_id \n'
                       'left outer join lateral (select jsonb_array_elements(args->0) doc_id \n'
                       '                         from task_task \n'
                       f"                         where name = '{_get_reindex_task_name()}' \n"
                       "                         and own_status = 'PENDING'\n"
                       '                         and date_work_start is null) tt on tt.doc_id = to_jsonb(dd.id) \n'
                       f'where {predicate} and df.document_id is null and tt.doc_id is null \n'
                       'and dd.processed is true')

        rows = cursor.fetchmany(pack_size)
        while rows:
            yield [row[0] for row in rows]
            rows = cursor.fetchmany(pack_size)


def _get_all_doc_ids_not_planned_to_index(query_filter: str, params: list, pack_size: int) \
        -> Generator[List[int], None, None]:
    with connection.cursor() as cursor:
        cursor.execute('select d.id from document_document d \n'
                       'left outer join lateral (select jsonb_array_elements(args->0) doc_id \n'
                       '                         from task_task \n'
                       '                         where name = %s \n'
                       '                         and own_status = %s\n'
                       '                         and date_work_start is null) tt on tt.doc_id = to_jsonb(d.id) \n'
                       'where {0} and tt.doc_id is null and d.processed is true'
                       .format(query_filter),
                       [_get_reindex_task_name(), PENDING] + params)

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
             name=task_names.TASK_NAME_MANUAL_REINDEX,
             bind=True,
             soft_time_limit=6000,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
             max_retries=3)
def manual_reindex(task: ExtendedTask,
                   document_type_code: str = None,
                   force: bool = False,
                   project_id: Optional[int] = None):
    from apps.rawdb.app_vars import APP_VAR_DISABLE_RAW_DB_CACHING
    if APP_VAR_DISABLE_RAW_DB_CACHING.val:
        task.log_info('Document caching to raw tables is disabled in Commons / App Vars')
        return
    run_parameters = {'document type': document_type_code}
    if project_id:
        run_parameters['project'] = project_id
    if force:
        run_parameters['force'] = True
    ptrs_str = ', '.join([f'{p}={run_parameters[p]}' for p in run_parameters])

    msg = f'manual_reindex called for {ptrs_str}. ' \
          f'Task: {task.task_name}, main id: {task.main_task_id}'
    log = CeleryTaskLogger(task)
    log.info(msg)
    adapt_tables_and_reindex(task, document_type_code, force, True, project_id)


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
             name=task_names.TASK_NAME_UPDATE_PROJECT_DOCUMENTS,
             bind=True,
             soft_time_limit=6000,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
             max_retries=3)
def reindex_all_project_documents(task: ExtendedTask, project_pk: Any) -> None:
    from apps.rawdb.app_vars import APP_VAR_DISABLE_RAW_DB_CACHING
    if APP_VAR_DISABLE_RAW_DB_CACHING.val:
        task.log_info('Document caching to raw tables is disabled in Commons / App Vars')
        return
    _reindex_document_ids_packets(task,
                                  get_all_doc_ids_not_planned_to_index_by_project_pk(project_pk, DOC_NUM_PER_SUB_TASK))


@shared_task(base=ExtendedTask,
             name=task_names.TASK_NAME_UPDATE_ASSIGNEE_FOR_DOCUMENTS,
             bind=True,
             soft_time_limit=6000,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
             max_retries=3)
def reindex_assignee_for_all_documents_in_system(task: ExtendedTask, assignee_pk: Any) -> None:
    from apps.rawdb.app_vars import APP_VAR_DISABLE_RAW_DB_CACHING
    if APP_VAR_DISABLE_RAW_DB_CACHING.val:
        task.log_info('Document caching to raw tables is disabled in Commons / App Vars')
        return
    _reindex_document_ids_packets(task,
                                  get_all_doc_ids_not_planned_to_index_by_assignee_pk(assignee_pk,
                                                                                      DOC_NUM_PER_SUB_TASK))


@shared_task(base=ExtendedTask,
             name=task_names.TASK_NAME_UPDATE_STATUS_NAME_FOR_DOCUMENTS,
             bind=True,
             soft_time_limit=6000,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
             max_retries=3)
def reindex_status_name_for_all_documents_in_system(task: ExtendedTask, status_pk: Any) -> None:
    from apps.rawdb.app_vars import APP_VAR_DISABLE_RAW_DB_CACHING
    if APP_VAR_DISABLE_RAW_DB_CACHING.val:
        task.log_info('Document caching to raw tables is disabled in Commons / App Vars')
        return
    _reindex_document_ids_packets(task,
                                  get_all_doc_ids_not_planned_to_index_by_status_pk(status_pk, DOC_NUM_PER_SUB_TASK))


def any_other_reindex_task(self_task_id, document_type_code: str, project_id: Optional[int]):
    tasks = Task.objects.unready_main_tasks() \
        .filter(name__in={task_names.TASK_NAME_AUTO_REINDEX, task_names.TASK_NAME_MANUAL_REINDEX}) \
        .exclude(pk=self_task_id) \
        .filter(Q(kwargs__document_type_code=document_type_code) |
                Q(kwargs__document_type_code__isnull=True))
    if project_id:
        tasks = tasks.filter(Q(kwargs__project_id=project_id))
    return tasks


@shared_task(base=ExtendedTask,
             name=task_names.TASK_NAME_AUTO_REINDEX,
             bind=True,
             soft_time_limit=6000,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
             max_retries=3)
def auto_reindex_not_tracked(task: ExtendedTask,
                             document_type_code: str = None,
                             force: bool = False):
    from apps.rawdb.app_vars import APP_VAR_DISABLE_RAW_DB_CACHING
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
            call_task_func(manual_reindex,
                           (document_type.code, False),
                           task_model.user_id,
                           caller_task=task)
        else:
            if there_are_non_indexed_docs_not_planned_to_index(document_type, log) \
                    and not any_other_reindex_task(task.request.id, document_type.code, None).exists():
                task.log_info(f'auto_reindex_not_tracked({document_type.code}): '
                              f'there_are_non_indexed_docs_not_planned_to_index')
                call_task_func(manual_reindex,
                               (document_type.code, False),
                               task_model.user_id)


def adapt_tables_and_reindex(task: ExtendedTask,
                             document_type_code: str = None,
                             force_recreate_tables: bool = False,
                             force_reindex: bool = False,
                             project_id: Optional[int] = None):
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
    :param project_id: project's filter
    :return:
    """
    from apps.project.models import Project
    if project_id:
        project = Project.objects.get(pk=project_id)
        document_types = [project.type]
    else:
        document_types = [DocumentType.objects.get(code=document_type_code)] \
            if document_type_code is not None else DocumentType.objects.all()
    log = CeleryTaskLogger(task)
    from apps.document.repository.document_repository import DocumentRepository
    doc_repo = DocumentRepository()

    for document_type in document_types:
        reindex_needed = adapt_table_structure(log,
                                               document_type,
                                               force=force_recreate_tables)

        if force_recreate_tables:
            # If "force" is requested - we cancel all currently planned re-index tasks
            # and plan (re-plan) reindexing for all documents of this task.
            for prev_task in any_other_reindex_task(task.request.id, document_type.code, project_id):
                purge_task(prev_task)
            doc_ids = doc_repo.get_doc_ids_by_project(project_id, DOC_NUM_PER_SUB_TASK) if project_id \
                else doc_repo.get_doc_ids_by_type(document_type.uid, DOC_NUM_PER_SUB_TASK)

            args = [(ids,) for ids in doc_ids]
            task.log_info(f'Initiating re-index for all documents of {document_type.code} '
                          f' - forced tables recreating.')
            task.run_sub_tasks('Reindex set of documents',
                               cache_document_fields_for_doc_ids_tracked,
                               args)
        elif reindex_needed or force_reindex:
            comment = 'forced' if force_reindex else 'reindex needed'
            task.log_info(f'Raw DB table for document type {document_type.code} '
                          f'has been altered ({comment}), task "{task.task_name}".\n'
                          f'Initiating re-index for all documents of this document type.')
            # If we altered the field structure then we need to re-index all docs of this type.
            # If no need to force - we plan re-index tasks only
            # for those documents for which they are not planned yet
            doc_ids = get_all_doc_ids_not_planned_to_index_by_project_pk(
                project_id, DOC_NUM_PER_SUB_TASK) if project_id else \
                get_all_doc_ids_not_planned_to_index_by_doc_type(
                    document_type.uid, DOC_NUM_PER_SUB_TASK)
            args = [(ids,) for ids in doc_ids]
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
            task.log_info(f'Initiating re-index for all documents of {document_type.code} '
                          f' - index not planned.')
            doc_ids = non_indexed_doc_ids_not_planned_to_index_by_project(
                document_type, project_id, DOC_NUM_PER_SUB_TASK) if project_id \
                else non_indexed_doc_ids_not_planned_to_index_by_doc_type(
                    document_type, DOC_NUM_PER_SUB_TASK)
            args = [(ids,) for ids in doc_ids]
            task.run_sub_tasks('Reindex set of documents', cache_document_fields_for_doc_ids_tracked, args)


def cache_document_fields_for_doc_ids(task: ExtendedTask,
                                      doc_ids: Iterable,
                                      changed_by_user_id: int = None,
                                      cache_system_fields: FieldSpec = True,
                                      cache_generic_fields: FieldSpec = True,
                                      cache_user_fields: bool = True):
    log = CeleryTaskLogger(task)
    changed_by_user = User.objects.get(pk=changed_by_user_id) if changed_by_user_id is not None else None
    for doc in Document.all_objects.filter(pk__in=doc_ids) \
            .select_related('document_type', 'assignee', 'status'):  # type: Document
        try:
            cache_document_fields(log, doc, changed_by_user=changed_by_user,
                                  cache_system_fields=cache_system_fields,
                                  cache_generic_fields=cache_generic_fields,
                                  cache_user_fields=cache_user_fields)
        except Document.DoesNotExist:
            pass


@shared_task(name=task_names.TASK_NAME_CACHE_DOC_NOT_TRACKED,
             base=ExtendedTask,
             bind=True,
             soft_time_limit=6000,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
             max_retries=3)
def cache_document_fields_for_doc_ids_not_tracked(task: ExtendedTask,
                                                  doc_ids: List,
                                                  changed_by_user_id: int = None,
                                                  cache_system_fields: FieldSpec = True,
                                                  cache_generic_fields: FieldSpec = True,
                                                  cache_user_fields: bool = True):
    """
    Cache document fields in a loop, not parallel.
    "Not tracked" - means it is in a list of tasks not shown in the admin task lists if started as the main task.
    """
    cache_document_fields_for_doc_ids(task, doc_ids, changed_by_user_id,
                                      cache_system_fields=cache_system_fields,
                                      cache_generic_fields=cache_generic_fields,
                                      cache_user_fields=cache_user_fields)


@shared_task(base=ExtendedTask,
             bind=True,
             soft_time_limit=6000,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
             max_retries=3)
def cache_document_fields_for_doc_ids_tracked(task: ExtendedTask,
                                              doc_ids: List,
                                              changed_by_user_id: int = None,
                                              cache_system_fields: FieldSpec = True,
                                              cache_generic_fields: FieldSpec = True,
                                              cache_user_fields: bool = True):
    """
    Cache document fields in a loop, not parallel.
    "Tracked" - means if it is started from apps.rawdb.field_value_tables import cache_document_fields
    """
    cache_document_fields_for_doc_ids(task, doc_ids, changed_by_user_id,
                                      cache_system_fields=cache_system_fields,
                                      cache_generic_fields=cache_generic_fields,
                                      cache_user_fields=cache_user_fields)


@shared_task(base=ExtendedTask,
             name='Index Documents',
             bind=True,
             soft_time_limit=6000,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
             max_retries=3)
def index_documents(task: ExtendedTask,
                    doc_ids: List,
                    changed_by_user_id: int = None,
                    cache_system_fields: FieldSpec = True,
                    cache_generic_fields: FieldSpec = True,
                    cache_user_fields: bool = True):
    """
    Index documents (cache document fields) in parallel. Document ids set is split to chunks and a
    sub-task is started for each sub-list.
    """
    args = [(sub_list, changed_by_user_id, cache_system_fields, cache_generic_fields, cache_user_fields)
            for sub_list in chunks(doc_ids, DOC_NUM_PER_SUB_TASK)]
    task.run_sub_tasks('Reindex documents', cache_document_fields_for_doc_ids_tracked, args)


def plan_reindex_tasks_in_chunks(all_doc_ids: Iterable,
                                 changed_by_user_id: int = None,
                                 cache_system_fields: FieldSpec = True,
                                 cache_generic_fields: FieldSpec = True,
                                 cache_user_fields: bool = True):
    """
    Plans document reindexing. Splits the provided set of doc ids to chunks and runs N main tasks which will be
    displayed in the admin task list. Splitting is done to avoid overloading rabbitmq with possible too large
    argument list. Started tasks may split their processing to any number of sub-tasks to parallelize the work.
    """
    for doc_ids_chunk in chunks(all_doc_ids, DOC_NUM_PER_MAIN_TASK):
        call_task_func(index_documents,
                       (doc_ids_chunk, changed_by_user_id,
                        cache_system_fields, cache_generic_fields, cache_user_fields),
                       changed_by_user_id)
