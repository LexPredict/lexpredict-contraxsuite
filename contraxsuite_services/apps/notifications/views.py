import os
import random
from datetime import datetime

from django.http import HttpResponse, HttpResponseBadRequest, FileResponse, HttpResponseNotFound, \
    HttpResponseServerError
from django.views.generic.base import View
from tzlocal import get_localzone

from apps.common.log_utils import ErrorCollectingLogger
from apps.common.url_utils import as_bool, as_int
from apps.document.field_types import FIELD_TYPES_REGISTRY, FieldType
from apps.document.models import Document, DocumentField
from apps.rawdb.field_value_tables import build_field_handlers, get_document_field_values
from apps.task.views import BaseAjaxTaskView
from apps.users.models import User
from .forms import SendDigestForm
from .models import DocumentDigestConfig, DocumentNotificationSubscription, DocumentChangedEvent, DocumentAssignedEvent
from .notifications import render_digest, get_template_image_dir, get_digest_template_dir, ensure_no_dir_change, \
    get_notification_template_dir, render_notification
from .tasks import SendDigest


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

        digest = render_digest(config=config,
                               dst_user=dst_user,
                               run_date=run_date,
                               emulate_no_docs=emulate_no_docs)
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
        ensure_no_dir_change(image_fn)
        config = DocumentDigestConfig.objects.get(pk=config_id)
        template_dir = get_digest_template_dir(config)
        image_dir = get_template_image_dir(template_dir)
        image_fn = os.path.join(image_dir, image_fn)
        if not os.path.isfile(image_fn):
            return HttpResponseNotFound('Attachment not found: ' + image_fn)
        return FileResponse(open(image_fn, 'rb'))


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
        field_handlers = build_field_handlers(document_type, include_suggested_fields=False)
        field_values = get_document_field_values(document_type, document_id, handlers=field_handlers)

        example_changes = dict()
        if subscription.event in {DocumentAssignedEvent.code, DocumentChangedEvent.code} and field_values:
            for h in field_handlers:
                if random.random() > 0.3:
                    continue
                field_type = FIELD_TYPES_REGISTRY.get(h.field_type)  # type: FieldType
                field = DocumentField.objects.filter(code=h.field_code).first()
                if not field:
                    continue
                example_value = field_type.example_python_value(field=field)
                example_changes[h.field_code] = (example_value, field_values.get(h.field_code))

        notification = render_notification(already_sent_user_ids=set(),
                                           subscription=subscription,
                                           document=document,
                                           field_handlers=field_handlers,
                                           field_values=field_values,
                                           changes=example_changes,
                                           changed_by_user=request.user
                                           )
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
        ensure_no_dir_change(image_fn)
        config = DocumentNotificationSubscription.objects.get(pk=subscription_id)
        template_dir = get_notification_template_dir(config)
        image_dir = get_template_image_dir(template_dir)
        image_fn = os.path.join(image_dir, image_fn)
        if not os.path.isfile(image_fn):
            return HttpResponseNotFound('Attachment not found: ' + image_fn)
        return FileResponse(open(image_fn, 'rb'))


class SendDigestTaskView(BaseAjaxTaskView):
    form_class = SendDigestForm
    task_name = SendDigest.name
    html_form_class = 'popup-form send-digest'

    def disallow_start(self):
        return False
