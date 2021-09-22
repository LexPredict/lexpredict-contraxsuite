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

from enum import Enum
from typing import Dict, Optional, List, Any

import django.dispatch
from django.conf import settings
from django.db.models import QuerySet
from django.dispatch import receiver

from apps.common import signals as common_signals
from apps.common.log_utils import ProcessLogger
from apps.document import signals
from apps.document.constants import DocumentSystemField, FieldSpec
from apps.document.models import Document, DocumentType, DocumentField
from apps.document.repository.document_field_repository import DocumentFieldRepository
from apps.project import signals as project_signals
from apps.rawdb.rawdb.rawdb_field_handlers import RawdbFieldHandler
from apps.users import signals as user_signals
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def reindex_on_doc_type_change(document_type: DocumentType):
    from apps.rawdb.app_vars import APP_VAR_DISABLE_RAW_DB_CACHING
    if APP_VAR_DISABLE_RAW_DB_CACHING.val():
        return

    from apps.rawdb.tasks import auto_reindex_not_tracked
    from apps.task.tasks import call_task_func
    call_task_func(auto_reindex_not_tracked, (document_type.code,), None, queue=settings.CELERY_QUEUE_SERIAL)


def reindex_on_field_change(document_field: DocumentField):
    from apps.rawdb.app_vars import APP_VAR_DISABLE_RAW_DB_CACHING
    if APP_VAR_DISABLE_RAW_DB_CACHING.val():
        return

    from apps.rawdb.tasks import auto_reindex_not_tracked
    from apps.task.tasks import call_task_func

    try:
        if document_field.document_type:
            call_task_func(auto_reindex_not_tracked, (document_field.document_type.code,),
                           None, queue=settings.CELERY_QUEUE_SERIAL)
    except DocumentField.DoesNotExist:
        pass


@receiver(signals.document_deleted)
def document_delete_listener(sender, **kwargs):
    user = kwargs.get('user')
    document = kwargs.get('document')
    from apps.rawdb.app_vars import APP_VAR_DISABLE_RAW_DB_CACHING
    if APP_VAR_DISABLE_RAW_DB_CACHING.val():
        return
    from apps.rawdb.field_value_tables import delete_document_from_cache
    delete_document_from_cache(user, document)


@receiver(signals.doc_full_delete)
def multiple_documents_delete_listener(sender, user, document_type_code, document_ids, **kwargs):
    from apps.rawdb.app_vars import APP_VAR_DISABLE_RAW_DB_CACHING
    if APP_VAR_DISABLE_RAW_DB_CACHING.val():
        return
    from apps.rawdb.field_value_tables import delete_documents_from_cache_by_ids
    delete_documents_from_cache_by_ids(user, document_type_code, document_ids)


@receiver(signals.document_field_changed)
def document_field_change_listener(sender, **kwargs):
    document_field = kwargs.get('document_field')
    reindex_on_field_change(document_field)


@receiver(signals.document_field_deleted)
def document_field_delete_listener(sender, **kwargs):
    document_field = kwargs.get('document_field')
    reindex_on_field_change(document_field)


@receiver(signals.document_type_changed)
def document_type_change_listener(sender, **kwargs):
    document_type = kwargs.get('document_type')
    reindex_on_doc_type_change(document_type)


@receiver(signals.document_type_deleted)
def document_type_delete_listener(sender, **kwargs):
    document_type = kwargs.get('document_type')
    from apps.rawdb.field_value_tables import _delete_document_fields_table
    _delete_document_fields_table(ProcessLogger(), document_type.code)


@receiver(project_signals.project_saved)
def project_name_change_listener(sender, **kwargs):
    project = kwargs.get('instance')
    old_project = kwargs.get('old_instance')
    if old_project is not None and project.name != old_project.name:
        from apps.task.tasks import call_task_func
        from apps.rawdb.tasks import reindex_all_project_documents
        call_task_func(reindex_all_project_documents, (project.pk,), None)


@receiver(user_signals.user_saved)
def user_full_name_change_listener(sender, **kwargs):
    user = kwargs.get('instance')
    old_user = kwargs.get('old_instance')
    if old_user is not None and old_user.name != user.name:
        from apps.task.tasks import call_task_func
        from apps.rawdb.tasks import reindex_assignee_for_all_documents_in_system
        call_task_func(reindex_assignee_for_all_documents_in_system, (user.pk,), None)


@receiver(common_signals.review_status_saved)
def review_status_save_listener(sender, **kwargs):
    review_status = kwargs.get('instance')
    old_review_status = kwargs.get('old_instance')
    if old_review_status is not None and review_status.name != old_review_status.name:
        from apps.task.tasks import call_task_func
        from apps.rawdb.tasks import reindex_status_name_for_all_documents_in_system
        call_task_func(reindex_status_name_for_all_documents_in_system, (review_status.pk,), None)


def document_change_listener_impl(sender,
                                  signal,
                                  log: ProcessLogger,
                                  document: Document,
                                  system_fields_changed: FieldSpec = True,
                                  generic_fields_changed: FieldSpec = True,
                                  user_fields_changed: bool = True,
                                  changed_by_user: User = None,
                                  document_initial_load: bool = False,
                                  skip_caching: bool = False,
                                  old_field_values: Optional[Dict[str, Any]] = None):
    # this listener only cares of caching
    if skip_caching:
        return

    from apps.rawdb.app_vars import APP_VAR_DISABLE_RAW_DB_CACHING
    if APP_VAR_DISABLE_RAW_DB_CACHING.val():
        return
    from apps.rawdb.field_value_tables import cache_document_fields
    log = log or ProcessLogger()
    cache_document_fields(log=log,
                          document=document,
                          cache_system_fields=system_fields_changed,
                          cache_generic_fields=generic_fields_changed,
                          cache_user_fields=user_fields_changed,
                          changed_by_user=changed_by_user,
                          document_initial_load=document_initial_load,
                          old_field_values=old_field_values)


@receiver(signals.document_changed)
def document_change_listener(sender, **kwargs):
    document_change_listener_impl(sender, **kwargs)


document_fields_changed = django.dispatch.Signal(
    providing_args=['document_event', 'changed_by_user', 'log', 'document', 'field_handlers', 'fields_before',
                    'fields_after'])


class DocumentEvent(Enum):
    CREATED = 'loaded'
    CHANGED = 'changed'
    DELETED = 'deleted'


def fire_document_fields_changed(sender,
                                 log: ProcessLogger,
                                 document_event: str,
                                 document_pk: int,
                                 field_handlers: Dict[str, RawdbFieldHandler],
                                 fields_before: Optional[Dict],
                                 fields_after: Optional[Dict],
                                 changed_by_user: User = None):
    document_fields_changed.send(sender,
                                 log=log, document_event=document_event,
                                 document_pk=document_pk, field_handlers=field_handlers,
                                 fields_before=fields_before,
                                 fields_after=fields_after, changed_by_user=changed_by_user)


# noinspection PyUnusedLocal
def doc_soft_delete_listener_impl(sender,
                                  signal,
                                  document_ids: List[int],
                                  delete_pending: bool):
    from apps.rawdb.field_value_tables import set_documents_delete_status
    set_documents_delete_status(document_ids, delete_pending)


@receiver(signals.doc_soft_delete)
def doc_soft_delete_listener(sender, **kwargs):
    doc_soft_delete_listener_impl(sender, **kwargs)


# noinspection PyUnusedLocal
def update_documents_assignee_impl(sender,
                                   signal,
                                   doc_ids: List[int],
                                   new_assignee_id: int,
                                   changed_by_user: User):
    from apps.rawdb.tasks import plan_reindex_tasks_in_chunks

    field_repo = DocumentFieldRepository()
    field_repo.update_docs_assignee(doc_ids, new_assignee_id)

    plan_reindex_tasks_in_chunks(doc_ids, changed_by_user.pk if changed_by_user else None,
                                 cache_system_fields=[DocumentSystemField.assignee.value],
                                 cache_generic_fields=False,
                                 cache_user_fields=False,
                                 priority=7)


@receiver(signals.documents_assignee_changed)
def documents_assignee_changed_listener(sender, **kwargs):
    update_documents_assignee_impl(sender, **kwargs)


# noinspection PyUnusedLocal
def update_documents_status_impl(sender,
                                 signal,
                                 documents: QuerySet,
                                 new_status_id: int,
                                 changed_by_user: User):
    from apps.rawdb.repository.raw_db_repository import RawDbRepository
    from apps.rawdb.tasks import plan_reindex_tasks_in_chunks
    repo = RawDbRepository()
    doc_ids = set(documents.values_list('pk', flat=True))
    repo.update_documents_status(doc_ids, new_status_id, changed_by_user)
    plan_reindex_tasks_in_chunks(doc_ids, changed_by_user.pk,
                                 cache_system_fields=[DocumentSystemField.status.value],
                                 cache_generic_fields=False,
                                 cache_user_fields=False)


@receiver(signals.documents_status_changed)
def documents_status_changed_listener(sender, **kwargs):
    update_documents_status_impl(sender, **kwargs)


# noinspection PyUnusedLocal
def clear_hidden_fields_impl(sender, signal, document: Document, field_codes: List[str]):
    from apps.rawdb.field_value_tables import clear_user_fields_no_events
    clear_user_fields_no_events(document=document, user_fields=field_codes)


@receiver(signals.hidden_fields_cleared)
def hidden_fields_cleared_listener(sender, **kwargs):
    clear_hidden_fields_impl(sender, **kwargs)
