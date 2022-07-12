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

from typing import Dict, Optional

from django.core.exceptions import ObjectDoesNotExist
from django.dispatch import receiver

from apps.common.logger import CsLogger
from apps.document.models import FieldValue, FieldAnnotation, Document, DocumentField
from apps.document.repository.document_field_repository import DocumentFieldRepository
from apps.document.signals import document_field_detection_failed
from apps.project.models import Project
from apps.users.models import User
from apps.websocket import channel_message_types as message_types
from apps.websocket.channel_message import ChannelMessage
from apps.websocket.websockets import Websockets

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def _user_to_dto(user: User) -> Optional[Dict]:
    if not user:
        return None
    return {
        'id': user.pk,
        'login': user.name,
        'full_name': user.name
    }


def _annotation_to_dto(instance: FieldAnnotation) -> Optional[Dict]:
    if not instance:
        return None
    from apps.document.api.v1 import AnnotationInDocumentSerializer
    return AnnotationInDocumentSerializer(instance).data


def _get_user_dto(instance):
    return _user_to_dto(getattr(instance, 'request_user', None))


def safe_failure(func):
    """
    Fail silently in case if related object doesn't exist - just log function and return None
    """
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ObjectDoesNotExist as e:
            logger = CsLogger.get_django_logger()
            logger.warning(f'{func.__name__} failed because related object was probably deleted, '
                           f'original exception is "{e}"')
    return decorator


@safe_failure
def _notify_field_value_saved(instance: FieldValue, deleted=False):
    if not instance.document.processed:
        return
    field_value = {'document': instance.document_id,
                   'project_id': instance.document.project_id,
                   'field__code': instance.field.code,
                   'value': instance.value if not deleted else None}

    annotation_stats = DocumentFieldRepository().get_annotation_stats_by_field_value(instance)

    message = ChannelMessage(message_types.CHANNEL_MSG_TYPE_FIELD_VALUE_SAVED,
                             {'field_value': field_value,
                              'annotation_stats': annotation_stats,
                              'user': _get_user_dto(instance)})
    notify_on_document_changes(instance.document.pk, message)


def notify_field_value_saved(instance: FieldValue):
    _notify_field_value_saved(instance, deleted=False)


def notify_field_value_deleted(instance: FieldValue):
    _notify_field_value_saved(instance, deleted=True)


@safe_failure
def notify_field_annotation_saved(instance: FieldAnnotation):
    if not instance.document.processed:
        return
    message = ChannelMessage(message_types.CHANNEL_MSG_TYPE_FIELD_ANNOTATION_SAVED,
                             {'annotation': _annotation_to_dto(instance),
                              'user': _get_user_dto(instance)})
    notify_on_document_changes(instance.document.pk, message)


@safe_failure
def notify_field_annotation_deleted(instance: FieldAnnotation):
    if not instance.document.processed:
        return
    message = ChannelMessage(message_types.CHANNEL_MSG_TYPE_FIELD_ANNOTATION_DELETED,
                             {'annotation': _annotation_to_dto(instance),
                              'user': _get_user_dto(instance)})
    notify_on_document_changes(instance.document.pk, message)


def document_field_detection_failed_impl(sender,
                                         signal,
                                         document: Document,
                                         document_field: DocumentField,
                                         message: str,
                                         document_initial_load: bool):
    if document_initial_load:
        # WS notifications for failed detection are disabled when
        # document is being processed for the first time
        return
    project_id = document.project_id
    data = {
        'document': {
            'id': document.pk,
            'name': document.name,
            'project_id': project_id,
            'project_name': document.project.name,
        },
        'field': {
            'id': document_field.uid,
            'code': document_field.code,
            'title': document_field.title
        },
        'message': message
    }
    chan_msg = ChannelMessage(message_types.CHANNEL_MSG_TYPE_DETECTION_FAILED, data)

    users = User.get_users_for_object(
        object_pk=project_id,
        object_model=Project,
        perm_name='add_project_document')

    Websockets().send_to_users(qs_users=users, message_obj=chan_msg)


@receiver(document_field_detection_failed)
def document_field_detection_failed_listener(sender, **kwargs):
    document_field_detection_failed_impl(sender, **kwargs)


def notify_on_document_changes(doc_id: int, message: ChannelMessage):
    """
    Send the websocket message to the users allowed to read the specified document.
    :param doc_id: ID of the document.
    :param message: Message to send.
    :return:
    """
    project_id = Document.objects.get(pk=doc_id).project_id
    users_with_project_perm = User.get_users_for_object(
        object_pk=project_id,
        object_model=Project,
        perm_name='change_document_field_values')
    users_with_document_perm = User.get_users_for_object(
        object_pk=doc_id,
        object_model=Document,
        perm_name='change_document_field_values')

    Websockets().send_to_users(
        qs_users=users_with_project_perm.union(users_with_document_perm).distinct(),
        message_obj=message)
