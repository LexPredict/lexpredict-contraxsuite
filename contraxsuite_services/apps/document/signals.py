from typing import Dict, Any, Optional

import django.dispatch

from apps.common.log_utils import ProcessLogger
from apps.document.models import Document
from apps.users.models import User

document_changed = django.dispatch.Signal(providing_args=['changed_by_user', 'log', 'document', 'system_fields_changed',
                                                          'generic_fields_changed', 'user_fields_changed',
                                                          'pre_detected_field_values', 'document_initial_load'])
document_deleted = django.dispatch.Signal(providing_args=['user', 'document'])

document_field_changed = django.dispatch.Signal(providing_args=['user', 'document_field'])
document_field_deleted = django.dispatch.Signal(providing_args=['user', 'document_field'])

document_type_changed = django.dispatch.Signal(providing_args=['user', 'document_type'])
document_type_deleted = django.dispatch.Signal(providing_args=['user', 'document_type'])


def fire_document_changed(sender,
                          log: ProcessLogger,
                          document: Document,
                          changed_by_user: User = None,
                          document_initial_load: bool = False,
                          system_fields_changed: bool = True,
                          generic_fields_changed: bool = True,
                          user_fields_changed: bool = True,
                          pre_detected_field_values: Optional[Dict[str, Any]] = None):
    document_changed.send(sender,
                          log=log,
                          changed_by_user=changed_by_user,
                          document_initial_load=document_initial_load,
                          document=document,
                          system_fields_changed=system_fields_changed,
                          user_fields_changed=user_fields_changed,
                          generic_fields_changed=generic_fields_changed,
                          pre_detected_field_values=pre_detected_field_values)


def fire_documents_changed(sender,
                           log: ProcessLogger,
                           doc_qr,
                           changed_by_user: User = None,
                           document_initial_load: bool = False,
                           system_fields_changed: bool = True,
                           generic_fields_changed: bool = True,
                           user_fields_changed: bool = True):
    for doc in doc_qr.select_related('document_type', 'project', 'status'):  # type: Document
        fire_document_changed(sender=sender,
                              log=log,
                              changed_by_user=changed_by_user,
                              document_initial_load=document_initial_load,
                              document=doc,
                              system_fields_changed=system_fields_changed,
                              generic_fields_changed=generic_fields_changed,
                              user_fields_changed=user_fields_changed)
