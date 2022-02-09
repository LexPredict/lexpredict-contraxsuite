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

from apps.document.models import DocumentFieldCategory, DocumentType
from apps.users.models import User
from apps.websocket import channel_message_types as message_types
from apps.websocket.channel_message import ChannelMessage
from apps.websocket.websockets import Websockets

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def notify_document_field_category_event(category: DocumentFieldCategory, event_name: str, changes: dict = None):
    """
    Notify any change in categories
    """
    data = dict(
        id=category.pk,
        document_type_id=category.document_type.pk,
        order=category.order,
        name=category.name,
        event=event_name,
        changes=changes
    )
    message = ChannelMessage(
        message_types.CHANNEL_MSG_TYPE_FIELD_CATEGORY_EVENT, data)

    users = User.get_users_for_object(
        object_pk=category.document_type.pk,
        object_model=DocumentType,
        perm_name='view_documenttype').values_list('pk', flat=True)

    Websockets().send_to_users(qs_users=users, message_obj=message)


def notify_document_type_event(document_type: DocumentType, event_name: str, changes: dict = None):
    """
    Notify any change in doc type
    """
    data = dict(
        id=str(document_type.pk),
        code=document_type.code,
        title=document_type.title,
        event=event_name,
        changes=changes
    )
    message = ChannelMessage(
        message_types.CHANNEL_MSG_TYPE_DOCUMENT_TYPE_EVENT, data)

    users = User.get_users_for_object(
        object_pk=document_type.pk,
        object_model=DocumentType,
        perm_name='view_documenttype').values_list('pk', flat=True)

    Websockets().send_to_users(qs_users=users, message_obj=message)
