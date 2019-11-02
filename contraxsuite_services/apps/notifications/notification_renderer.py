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

import os
from typing import Dict, Set, Optional, List, Any

from jinja2 import Template

from apps.common.contraxsuite_urls import root_url, doc_editor_url
from apps.notifications.models import DocumentNotificationSubscription
from apps.notifications.notifications import RenderedNotification, DocumentNotificationSource, \
    get_notification_template_resource
from apps.rawdb.constants import FIELD_CODES_SHOW_BY_DEFAULT_GENERIC, FIELD_CODES_HIDE_BY_DEFAULT, \
    FIELD_CODES_SHOW_BY_DEFAULT_NON_GENERIC
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.3.0/LICENSE"
__version__ = "1.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class NotificationRenderer:
    package_already_sent_user_ids = {}  # type:Dict[str, Set[str]]

    @staticmethod
    def render_notification(package_id: str,
                            subscription: DocumentNotificationSubscription,
                            data: DocumentNotificationSource) -> Optional[RenderedNotification]:
        if package_id in NotificationRenderer.package_already_sent_user_ids:
            already_sent_user_ids = NotificationRenderer.package_already_sent_user_ids[package_id]
        else:
            already_sent_user_ids = set()
            NotificationRenderer.package_already_sent_user_ids[package_id] = already_sent_user_ids

        document_type = data.document.document_type
        event_info = subscription.get_event_info()
        if not event_info:
            return None
        recipients = subscription.resolve_recipients(data.field_values)
        recipients = {r for r in recipients if r.id not in already_sent_user_ids} if recipients else None
        if not recipients:
            return None

        display_fields = set(subscription.generic_fields or {})
        display_fields.update(FIELD_CODES_SHOW_BY_DEFAULT_GENERIC if document_type.is_generic()
                              else FIELD_CODES_SHOW_BY_DEFAULT_NON_GENERIC)
        display_fields.update({f.code for f in subscription.user_fields.all() if f.document_type == document_type})

        changes_filtered = dict()

        if data.changes:
            for code, old_new in data.changes.items():
                if code in FIELD_CODES_HIDE_BY_DEFAULT:
                    continue
                if old_new[0] == old_new[1] or data.field_values.get(code) == old_new[0]:
                    continue
                changes_filtered[code] = old_new
        changes = changes_filtered

        display_fields.update(changes.keys())

        template_context = {
            'app_url': root_url(),
            'doc_url': doc_editor_url(document_type.code,
                                      data.document.project_id,
                                      data.document.pk),
            'event_code': event_info.code,
            'event_title': event_info.title,
            'event_initiator': data.changed_by_user,
            'document': data.field_values,
            'fields': [{
                'code': h.field_code,
                'title': h.field_title,
                'type': h.field_type,
                'value': data.field_values.get(h.field_code),
                'changed': h.field_code in changes,
                'changes': changes.get(h.field_code),
            } for h in data.field_handlers if h.field_code in display_fields],
            'changes': changes,
            'changed_by_user': data.changed_by_user
        }  # type: Dict[str, Any]

        subject_template = subscription.subject or event_info.default_subject
        header_template = subscription.header or event_info.default_subject

        subject = Template(subject_template).render(template_context)
        header = Template(header_template).render(template_context)

        template_context.update({
            'subject': subject,
            'header': header
        })

        html = None

        html_template = get_notification_template_resource(os.path.join(subscription.template_name, 'template.html'))
        if html_template:
            html = Template(html_template.decode('utf-8')).render(template_context)

        txt_template_name = os.path.join(subscription.template_name, 'template.txt')
        txt_template = get_notification_template_resource(txt_template_name)
        if not txt_template:
            raise RuntimeError('Txt template not found: {0}'.format(txt_template_name))
        txt = Template(txt_template.decode('utf-8')).render(template_context)

        image_dir = os.path.join(subscription.template_name, 'images')

        return RenderedNotification(dst_users=recipients,
                                    subject=subject,
                                    txt=txt,
                                    html=html,
                                    image_dir=image_dir,
                                    cc=subscription.get_cc_addrs())

    @staticmethod
    def render_notification_pack(
            package_id: str,
            subscription: DocumentNotificationSubscription,
            data: List[DocumentNotificationSource]) -> List[RenderedNotification]:
        notifications_pack = []  # type: List[RenderedNotification]
        if not data:
            return notifications_pack
        event_info = subscription.get_event_info()
        if not event_info:
            return notifications_pack

        if package_id in NotificationRenderer.package_already_sent_user_ids:
            already_sent_user_ids = NotificationRenderer.package_already_sent_user_ids[package_id]
        else:
            already_sent_user_ids = set()
            NotificationRenderer.package_already_sent_user_ids[package_id] = already_sent_user_ids

        # merge message bodies
        # all the documents have the same type
        document_type = data[0].document.document_type

        template_context = {
            'app_url': root_url(),
            'event_code': event_info.code,
            'event_title': event_info.title,
            'documents': []
        }

        # get recipients per message, split message packs by recipients
        msgs_by_recipients = {}  # type:[str, List[DocumentNotificationSource]]
        recipients_by_key = {}  # type:[str, List[User]]
        for msg_data in data:
            recipients = subscription.resolve_recipients(msg_data.field_values)  # type:Set[User]
            recipients = {r for r in recipients if r.id not in already_sent_user_ids} if recipients else None
            if not recipients:
                continue
            recp_ids = [str(r.pk) for r in recipients]
            recp_ids.sort()
            recp_key = ','.join(recp_ids)
            if recp_key in msgs_by_recipients:
                msgs_by_recipients[recp_key].append(msg_data)
            else:
                msgs_by_recipients[recp_key] = [msg_data]
                recipients_by_key[recp_key] = recipients

        subject = ''
        for recp_key in msgs_by_recipients:
            recipients = recipients_by_key[recp_key]
            for msg_data in msgs_by_recipients[recp_key]:
                display_fields = set(subscription.generic_fields or {})
                display_fields.update(FIELD_CODES_SHOW_BY_DEFAULT_GENERIC if document_type.is_generic()
                                      else FIELD_CODES_SHOW_BY_DEFAULT_NON_GENERIC)
                display_fields.update({f.code for f in subscription.user_fields.all() if f.document_type == document_type})

                changes_filtered = dict()

                if msg_data.changes:
                    for code, old_new in msg_data.changes.items():
                        if code in FIELD_CODES_HIDE_BY_DEFAULT:
                            continue
                        if old_new[0] == old_new[1] or msg_data.field_values.get(code) == old_new[0]:
                            continue
                        changes_filtered[code] = old_new
                changes = changes_filtered

                display_fields.update(changes.keys())

                document_context = {
                    'doc_url': doc_editor_url(document_type.code,
                                              msg_data.document.project_id,
                                              msg_data.document.pk),
                    'event_initiator': msg_data.changed_by_user,
                    'document': msg_data.field_values,
                    'fields': [{
                        'code': h.field_code,
                        'title': h.field_title,
                        'type': h.field_type,
                        'value': msg_data.field_values.get(h.field_code),
                        'changed': h.field_code in changes,
                        'changes': changes.get(h.field_code),
                    } for h in msg_data.field_handlers if h.field_code in display_fields],
                    'changes': changes,
                    'changed_by_user': msg_data.changed_by_user
                }  # type: Dict[str, Any]

                subject_template = subscription.subject or event_info.default_subject
                header_template = subscription.header or event_info.default_subject

                subject = Template(subject_template).render(template_context)
                header = Template(header_template).render(template_context)

                template_context.update({
                    'subject': subject,
                    'header': header
                })  # ??

                template_context['documents'].append(document_context)

            html = None

            html_template = get_notification_template_resource(
                os.path.join(subscription.template_name, 'template_pack.html'))
            if html_template:
                html = Template(html_template.decode('utf-8')).render(template_context)

            txt_template_name = os.path.join(subscription.template_name, 'template_pack.txt')
            txt_template = get_notification_template_resource(txt_template_name)
            if not txt_template:
                raise RuntimeError('Txt template not found: {0}'.format(txt_template_name))
            txt = Template(txt_template.decode('utf-8')).render(template_context)

            image_dir = os.path.join(subscription.template_name, 'images')

            notification = RenderedNotification(dst_users=recipients,
                                                subject=subject,
                                                txt=txt,
                                                html=html,
                                                image_dir=image_dir,
                                                cc=subscription.get_cc_addrs())
            notifications_pack.append(notification)
        return notifications_pack
