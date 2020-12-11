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

import mimetypes
import os
import random
import uuid
from datetime import datetime

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError
from django.views.generic.base import View
from tzlocal import get_localzone

from apps.common.log_utils import ErrorCollectingLogger
from apps.common.errors import render_error
from apps.common.url_utils import as_bool, as_int
from apps.document.field_types import TypedField
from apps.document.models import Document, DocumentField
from apps.notifications.notification_renderer import NotificationRenderer
from apps.rawdb.field_value_tables import build_field_handlers, get_document_field_values
from apps.task.views import BaseAjaxTaskView
from apps.users.models import User
from apps.notifications.forms import SendDigestForm
from apps.notifications.models import DocumentDigestConfig, DocumentNotificationSubscription, \
    DocumentChangedEvent, DocumentAssignedEvent
from apps.notifications.notifications import render_digest, get_notification_template_resource, \
    DocumentNotificationSource, get_predefined_mime_type
from apps.notifications.tasks import SendDigest

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class RenderDigestView(View):
    PARAM_DST_USER = 'dst_user'
    PARAM_EVENT = 'event'
    PARAM_EVENT_INITIATOR = 'event_initiator'
    PARAM_SEND = 'send_email'
    PARAM_EMULATE_NO_DOCS = 'emulate_no_docs'
    FORMAT_HTML = 'html'

    def get(self, request, config_id, content_format, **kwargs):
        dst_user_id_or_name = request.GET[self.PARAM_DST_USER]
        send_email = as_bool(request.GET, self.PARAM_SEND, False)
        emulate_no_docs = as_bool(request.GET, self.PARAM_EMULATE_NO_DOCS, False)

        config = DocumentDigestConfig.objects.get(pk=config_id)

        if dst_user_id_or_name:
            try:
                dst_user = User.objects.get(pk=int(dst_user_id_or_name))
            except ValueError:
                dst_user = User.objects.get(username=str(dst_user_id_or_name))
        else:
            dst_user = request.user

        run_date = datetime.now(tz=dst_user.timezone or get_localzone())

        try:
            digest = render_digest(config=config,
                                   dst_user=dst_user,
                                   run_date=run_date,
                                   emulate_no_docs=emulate_no_docs)
        except Exception as e:
            return HttpResponse(render_error('Exception caught while trying to render digest', e),
                                status=500, content_type='text/plain')

        if not digest:
            return HttpResponse('Notification contains no data.', status=200)

        if content_format == self.FORMAT_HTML:
            content = digest.html
            content_type = 'text/html'
        else:
            content = digest.txt
            content_type = 'text/plain'

        if send_email:
            log = ErrorCollectingLogger()
            digest.send(log)
            log.raise_if_error()

        return HttpResponse(content=content, content_type=content_type, status=200)


class DigestImageView(View):
    def get(self, request, config_id, image_fn, **kwargs):
        config = DocumentDigestConfig.objects.get(pk=config_id)
        image = get_notification_template_resource(os.path.join(config.template_name,
                                                                'images', image_fn))
        if not image:
            return HttpResponseNotFound('Attachment not found: ' + image_fn)

        content_type = get_predefined_mime_type(image_fn) or mimetypes.guess_type(image_fn)[0]
        return HttpResponse(content_type=content_type, content=image)


class RenderNotificationView(View):
    PARAM_DOCUMENT = 'document'
    PARAM_SEND = 'send_email'
    FORMAT_HTML = 'html'

    def get(self, request, subscription_id, content_format, **_kwargs):
        send_email = as_bool(request.GET, self.PARAM_SEND, False)

        subscription = DocumentNotificationSubscription.objects.get(pk=subscription_id)

        document_type = subscription.document_type

        document_id = as_int(request.GET, self.PARAM_DOCUMENT, None)
        if document_id:
            document = Document.objects.filter(document_type=document_type, pk=document_id).first()
            if not document:
                return HttpResponseBadRequest('Document with id = {0} not found or has wrong type.'.format(document_id))
        else:
            document = Document.objects.filter(document_type=document_type).first()
            if not document:
                return HttpResponseBadRequest('Document id not provided and '
                                              'there are no example documents of type {0}.'.format(document_type.code))

        document_id = document.pk
        field_handlers = build_field_handlers(document_type,
                                              include_annotation_fields=False)
        field_values = get_document_field_values(document_type, document_id, handlers=field_handlers)

        example_changes = dict()
        if subscription.event in {DocumentAssignedEvent.code, DocumentChangedEvent.code} and field_values:
            for h in field_handlers:
                if random.random() > 0.3:
                    continue
                field = DocumentField.objects.filter(code=h.field_code).first()
                if not field:
                    continue
                typed_field = TypedField.by(field)
                example_value = typed_field.example_python_value()
                example_changes[h.field_code] = (example_value, field_values.get(h.field_code))

        try:
            notification = NotificationRenderer.render_notification(
                uuid.uuid4().hex,
                subscription,
                DocumentNotificationSource(
                    document=document,
                    field_handlers=field_handlers,
                    field_values=field_values,
                    changes=example_changes,
                    changed_by_user=request.user))
        except Exception as e:
            return HttpResponse(render_error('Exception caught while trying to render notification', e),
                                status=500, content_type='text/plain')
        if not notification:
            return HttpResponse('Notification contains no data.', status=200)

        if content_format == self.FORMAT_HTML:
            content = notification.html
            content_type = 'text/html'
        else:
            content = notification.txt
            content_type = 'text/plain'

        if send_email:
            log = ErrorCollectingLogger()
            notification.send(log=log)
            error = log.get_error()
            if error:
                return HttpResponseServerError(content=error, content_type='application/json')

        return HttpResponse(content=content, content_type=content_type, status=200)


class NotificationImageView(View):
    def get(self, request, subscription_id, image_fn, **kwargs):
        config = DocumentNotificationSubscription.objects.get(pk=subscription_id)
        image = get_notification_template_resource(os.path.join(config.template_name, 'images', image_fn))
        if not image:
            return HttpResponseNotFound('Attachment not found: ' + image_fn)
        content_type = get_predefined_mime_type(image_fn) or mimetypes.guess_type(image_fn)[0]
        return HttpResponse(content_type=content_type, content=image)


class SendDigestTaskView(BaseAjaxTaskView):
    form_class = SendDigestForm
    task_name = SendDigest.name
    html_form_class = 'popup-form send-digest'

    def disallow_start(self):
        return False
