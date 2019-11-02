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

from typing import Set, List

import django.dispatch
from django.db.models import QuerySet
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.common.log_utils import ProcessLogger
from apps.document.constants import FieldSpec
from apps.document.models import Document
from apps.document.models import FieldValue, FieldAnnotation
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.3.0/LICENSE"
__version__ = "1.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


document_changed = django.dispatch.Signal(providing_args=['changed_by_user', 'log', 'document', 'system_fields_changed',
                                                          'generic_fields_changed', 'user_fields_changed',
                                                          'document_initial_load'])
document_deleted = django.dispatch.Signal(providing_args=['user', 'document'])

document_field_changed = django.dispatch.Signal(providing_args=['user', 'document_field'])
document_field_deleted = django.dispatch.Signal(providing_args=['user', 'document_field'])

document_type_changed = django.dispatch.Signal(providing_args=['user', 'document_type'])
document_type_deleted = django.dispatch.Signal(providing_args=['user', 'document_type'])

doc_soft_delete = django.dispatch.Signal(providing_args=['document_ids', 'delete_pending'])

documents_assignee_changed = django.dispatch.Signal(providing_args=['documents', 'new_assignee_id', 'changed_by_user'])

documents_status_changed = django.dispatch.Signal(providing_args=['documents', 'new_status_id', 'changed_by_user'])

hidden_fields_cleared = django.dispatch.Signal(providing_args=['document', 'field_codes'])


def fire_document_changed(sender,
                          log: ProcessLogger,
                          document: Document,
                          changed_by_user: User = None,
                          document_initial_load: bool = False,
                          system_fields_changed: FieldSpec = True,
                          generic_fields_changed: FieldSpec = True,
                          user_fields_changed: bool = True):
    document_changed.send(sender,
                          log=log,
                          changed_by_user=changed_by_user,
                          document_initial_load=document_initial_load,
                          document=document,
                          system_fields_changed=system_fields_changed,
                          user_fields_changed=user_fields_changed,
                          generic_fields_changed=generic_fields_changed)


def fire_document_deleted(sender,
                          document: Document,
                          user: User):
    document_deleted.send(sender,
                          user=user,
                          document=document)


def fire_doc_soft_delete(sender,
                         document_ids,
                         delete_pending: bool):
    doc_soft_delete.send(sender,
                         document_ids=document_ids,
                         delete_pending=delete_pending)


def fire_documents_assignee_changed(sender,
                                    doc_ids: List[int],
                                    new_assignee_id: int,
                                    changed_by_user: User):
    documents_assignee_changed.send(sender,
                                    doc_ids=doc_ids,
                                    new_assignee_id=new_assignee_id,
                                    changed_by_user=changed_by_user)


def fire_documents_status_changed(sender,
                                  documents: QuerySet,
                                  new_status_id: int,
                                  changed_by_user: User):
    documents_status_changed.send(sender,
                                  documents=documents,
                                  new_status_id=new_status_id,
                                  changed_by_user=changed_by_user)


def fire_hidden_fields_cleared(sender, document: Document, field_codes: Set[str]):
    hidden_fields_cleared.send(sender, document=document, field_codes=field_codes)


@receiver(post_save, sender=FieldValue)
def field_value_saved(sender, instance: FieldValue, created: bool = True, **kwargs):
    from apps.document.async_notifications import notify_field_value_saved
    from django.db import transaction
    transaction.on_commit(lambda: notify_field_value_saved(instance))


@receiver(post_delete, sender=FieldValue)
def field_value_deleted(sender, instance: FieldValue, **kwargs):
    from apps.document.async_notifications import notify_field_value_deleted
    from django.db import transaction
    transaction.on_commit(lambda: notify_field_value_deleted(instance))


@receiver(post_save, sender=FieldAnnotation)
def field_annotation_saved(sender, instance: FieldAnnotation, created: bool = True, **kwargs):
    from apps.document.async_notifications import notify_field_annotation_saved
    from django.db import transaction
    transaction.on_commit(lambda: notify_field_annotation_saved(instance))


@receiver(post_delete, sender=FieldAnnotation)
def field_annotation_deleted(sender, instance: FieldAnnotation, **kwargs):
    from apps.document.async_notifications import notify_field_annotation_deleted
    from django.db import transaction
    transaction.on_commit(lambda: notify_field_annotation_deleted(instance))
