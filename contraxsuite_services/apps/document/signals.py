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

from typing import Set, List, Optional, Dict, Any

from django.db import transaction
from django.db.models import QuerySet
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver, Signal
from guardian.shortcuts import assign_perm, get_content_type

from apps.common.log_utils import ProcessLogger
from apps.document.constants import FieldSpec
from apps.document.models import Document, DocumentField
from apps.document.models import FieldValue, FieldAnnotation
from apps.users.models import User, CustomUserObjectPermission

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


document_changed = Signal(providing_args=['changed_by_user', 'log', 'document', 'system_fields_changed',
                                          'generic_fields_changed', 'user_fields_changed',
                                          'document_initial_load', 'skip_caching', 'old_field_values'])
document_deleted = Signal(providing_args=['user', 'document'])

doc_full_delete = Signal(providing_args=['user', 'document_type_code', 'document_ids'])

document_field_changed = Signal(providing_args=['user', 'document_field'])
document_field_deleted = Signal(providing_args=['user', 'document_field'])
document_field_detection_failed = Signal(providing_args=['document', 'document_field', 'message'])

document_type_changed = Signal(providing_args=['user', 'document_type'])
document_type_deleted = Signal(providing_args=['user', 'document_type'])

doc_soft_delete = Signal(providing_args=['document_ids', 'delete_pending'])

documents_assignee_changed = Signal(providing_args=['documents', 'new_assignee_id', 'changed_by_user'])

documents_status_changed = Signal(providing_args=['documents', 'new_status_id', 'changed_by_user'])

hidden_fields_cleared = Signal(providing_args=['document', 'field_codes'])

documents_pre_update = Signal(providing_args=['queryset'])


def fire_document_changed(sender,
                          log: ProcessLogger,
                          document: Document,
                          changed_by_user: User = None,
                          document_initial_load: bool = False,
                          system_fields_changed: FieldSpec = True,
                          generic_fields_changed: FieldSpec = True,
                          user_fields_changed: bool = True,
                          skip_caching: bool = False,
                          old_field_values: Optional[Dict[str, Any]] = None):
    document_changed.send(sender,
                          log=log,
                          changed_by_user=changed_by_user,
                          document_initial_load=document_initial_load,
                          document=document,
                          system_fields_changed=system_fields_changed,
                          user_fields_changed=user_fields_changed,
                          generic_fields_changed=generic_fields_changed,
                          skip_caching=skip_caching,
                          old_field_values=old_field_values)


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


def fire_doc_full_delete(sender,
                         user: User,
                         document_type_code: str,
                         document_ids: List):
    doc_full_delete.send(sender,
                         user=user,
                         document_type_code=document_type_code,
                         document_ids=document_ids)


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


def fire_document_field_detection_failed(sender,
                                         document: Document,
                                         document_field: DocumentField,
                                         message: str,
                                         document_initial_load: bool):
    document_field_detection_failed.send(sender,
                                         document=document,
                                         document_field=document_field,
                                         message=message,
                                         document_initial_load=document_initial_load)


@receiver(post_save, sender=FieldValue)
def field_value_saved(sender, instance: FieldValue, created: bool = True, **kwargs):
    from apps.document.async_notifications import notify_field_value_saved
    transaction.on_commit(lambda: notify_field_value_saved(instance))


@receiver(post_delete, sender=FieldValue)
def field_value_deleted(sender, instance: FieldValue, **kwargs):
    from apps.document.async_notifications import notify_field_value_deleted
    transaction.on_commit(lambda: notify_field_value_deleted(instance))


@receiver(post_save, sender=FieldAnnotation)
def field_annotation_saved(sender, instance: FieldAnnotation, created: bool = True, **kwargs):
    from apps.document.async_notifications import notify_field_annotation_saved
    transaction.on_commit(lambda: notify_field_annotation_saved(instance))


@receiver(post_delete, sender=FieldAnnotation)
def field_annotation_deleted(sender, instance: FieldAnnotation, **kwargs):
    from apps.document.async_notifications import notify_field_annotation_deleted
    transaction.on_commit(lambda: notify_field_annotation_deleted(instance))


@receiver(documents_pre_update, sender=Document)
def reassign_permissions(sender, queryset, **kwargs):
    from apps.users.permissions import document_permissions, remove_perm

    if 'assignee' in kwargs or 'assignee_id' in kwargs:
        assignee = kwargs.get('assignee') or kwargs.get('assignee_id')
        new_assignee = User.objects.get(pk=assignee) if isinstance(assignee, int) else assignee
        # change perms
        for document in queryset:
            if document.assignee is not None:
                for perm_name in document_permissions:
                    remove_perm(perm_name, document.assignee, document)
        if new_assignee is not None:
            for perm_name in document_permissions:
                assign_perm(perm_name, new_assignee, queryset)

    # reassign document cluster
    if 'project' in kwargs or 'project_id' in kwargs:
        project = kwargs.get('project') or kwargs.get('project_id')
        new_project_id = project if isinstance(project, int) else project.pk
        # delete perms
        for document in queryset:
            if document.project_id != new_project_id:
                CustomUserObjectPermission.objects.filter(content_type=get_content_type(Document),
                                                          object_pk=document.pk).delete()
