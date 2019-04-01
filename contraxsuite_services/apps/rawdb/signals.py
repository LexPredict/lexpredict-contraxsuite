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
from enum import Enum
from typing import Dict, Any, Optional

import django.dispatch
from django.conf import settings
from django.dispatch import receiver

from apps.common.log_utils import ProcessLogger
from apps.document import signals
from apps.document.models import Document, DocumentType, DocumentField
from apps.rawdb.rawdb.field_handlers import FieldHandler
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.0/LICENSE"
__version__ = "1.2.0"
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
