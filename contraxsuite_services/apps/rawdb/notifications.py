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

from typing import Dict, Any, List

from apps.document.async_notifications import notify_on_document_changes
from apps.document.models import Document
from apps.rawdb.constants import FIELD_CODE_ANNOTATION_SUFFIX
from apps.rawdb.rawdb.rawdb_field_handlers import RawdbFieldHandler
from apps.users.models import User
from apps.websocket.channel_message import ChannelMessage
from apps.websocket.channel_message_types import CHANNEL_MSG_TYPE_FIELDS_UPDATED

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class UserNotifications:
    @staticmethod
    def notify_user_on_document_values_changed(
            document: Document,
            document_fields_before: Dict[str, Any],
            document_fields_after: Dict[str, Any],
            field_handlers: List[RawdbFieldHandler],
            changed_by_user: User) -> None:
        if not document_fields_after or not document.processed:
            return
        allowed_fields = {h.field_code for h in field_handlers
                          if not h.is_annotation}

        field_changed = {}
        for field in document_fields_after:
            if field not in allowed_fields:
                continue
            if field.endswith(FIELD_CODE_ANNOTATION_SUFFIX):
                continue
            old_val = document_fields_before.get(field) \
                if document_fields_before else None
            new_val = document_fields_after[field]
            if old_val == new_val:
                continue
            field_changed[field] = {'new_val': new_val, 'old_val': old_val}

        if not field_changed:
            return

        # notify clients through WS
        payload = {
            'fields': field_changed,
            'document_id': document.pk,
            'project_id': document.project.pk,
            'project_name': document.project.name,
        }
        if changed_by_user:
            payload['user'] = {
                'id': changed_by_user.pk,
                'first_name': changed_by_user.first_name,
                'last_name': changed_by_user.last_name,
                'login': changed_by_user.username
            }
        message = ChannelMessage(CHANNEL_MSG_TYPE_FIELDS_UPDATED,
                                 payload)
        notify_on_document_changes(document.pk, message)
