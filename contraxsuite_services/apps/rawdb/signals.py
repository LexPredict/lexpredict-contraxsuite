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
from typing import Dict, Any, Optional, List

import django.dispatch
from django.conf import settings
from django.dispatch import receiver

from apps.common.log_utils import ProcessLogger
from apps.document import signals
from apps.project import signals as project_signals
from apps.users import signals as user_signals
from apps.common import signals as common_signals
from apps.document.models import Document, DocumentType, DocumentField
from apps.rawdb.rawdb.field_handlers import FieldHandler
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.2/LICENSE"
__version__ = "1.2.2"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def reindex_on_doc_type_change(document_type: DocumentType):
    from apps.rawdb.app_vars import APP_VAR_DISABLE_RAW_DB_CACHING
    if APP_VAR_DISABLE_RAW_DB_CACHING.val:
        return

    from apps.rawdb.tasks import auto_reindex_not_tracked
    from apps.task.tasks import call_task_func
    call_task_func(auto_reindex_not_tracked, (document_type.code,), None, queue=settings.CELERY_QUEUE_SERIAL)


def reindex_on_field_change(document_field: DocumentField):
    from apps.rawdb.app_vars import APP_VAR_DISABLE_RAW_DB_CACHING
    if APP_VAR_DISABLE_RAW_DB_CACHING.val:
        return

    from apps.rawdb.tasks import auto_reindex_not_tracked
    from apps.task.tasks import call_task_func
    from apps.document.models import DocumentField

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
    if APP_VAR_DISABLE_RAW_DB_CACHING.val:
        return
    from apps.rawdb.field_value_tables import delete_document_from_cache
    delete_document_from_cache(user, document)


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


@receiver(project_signals.project_saved)
def project_name_change_listener(sender, **kwargs):
    project = kwargs.get('instance')
    old_project = kwargs.get('old_instance')
    if old_project is not None and project.name != old_project.name:
        from apps.task.tasks import call_task_func
        from apps.rawdb.tasks import update_project_documents
        call_task_func(update_project_documents, (project.pk,), None)


@receiver(user_signals.user_saved)
def user_full_name_change_listener(sender, **kwargs):
    user = kwargs.get('instance')
    old_user = kwargs.get('old_instance')
    if old_user is not None and old_user.get_full_name() != user.get_full_name():
        from apps.task.tasks import call_task_func
        from apps.rawdb.tasks import update_assignee_for_documents
        call_task_func(update_assignee_for_documents, (user.pk,), None)


@receiver(common_signals.review_status_saved)
def review_status_save_listener(sender, **kwargs):
    review_status = kwargs.get('instance')
    old_review_status = kwargs.get('old_instance')
    if old_review_status is not None and review_status.name != old_review_status.name:
        from apps.task.tasks import call_task_func
        from apps.rawdb.tasks import update_status_name_for_documents
        call_task_func(update_status_name_for_documents, (review_status.pk,), None)


# noinspection PyUnusedLocal
def document_change_listener_impl(_sender,
                                  signal,
                                  log: ProcessLogger,
                                  document: Document,
                                  system_fields_changed: bool = True,
                                  generic_fields_changed: bool = True,
                                  user_fields_changed: bool = True,
                                  pre_detected_field_values: Optional[Dict[str, Any]] = None,
                                  changed_by_user: User = None,
                                  document_initial_load: bool = False):
    from apps.rawdb.app_vars import APP_VAR_DISABLE_RAW_DB_CACHING
    if APP_VAR_DISABLE_RAW_DB_CACHING.val:
        return
    from .field_value_tables import cache_document_fields
    log = log or ProcessLogger()
    cache_document_fields(log=log,
                          document=document,
                          cache_generic_fields=generic_fields_changed,
                          cache_user_fields=user_fields_changed,
                          pre_detected_field_codes_to_suggested_values=pre_detected_field_values,
                          changed_by_user=changed_by_user,
                          document_initial_load=document_initial_load)


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
                                 document: Document,
                                 field_handlers: Dict[str, FieldHandler],
                                 fields_before: Optional[Dict],
                                 fields_after: Optional[Dict],
                                 changed_by_user: User = None):
    document_fields_changed.send(sender,
                                 log=log, document_event=document_event,
                                 document=document, field_handlers=field_handlers,
                                 fields_before=fields_before,
                                 fields_after=fields_after, changed_by_user=changed_by_user)


# noinspection PyUnusedLocal
def doc_soft_delete_listener_impl(_sender,
                                  signal,
                                  document_ids: List[int],
                                  delete_pending: bool):
    from apps.rawdb.field_value_tables import set_documents_delete_status
    set_documents_delete_status(document_ids, delete_pending)


@receiver(signals.doc_soft_delete)
def doc_soft_delete_listener(sender, **kwargs):
    doc_soft_delete_listener_impl(sender, **kwargs)
