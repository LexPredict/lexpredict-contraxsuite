import datetime
import os
import re
from concurrent.futures import ThreadPoolExecutor
from email.mime.image import MIMEImage
from typing import Dict, Optional, Any, List, Set, Tuple

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from jinja2 import Template

from apps.common.contraxsuite_urls import doc_editor_url, root_url
from apps.common.log_utils import ProcessLogger, render_error
from apps.document.models import Document
from apps.rawdb.field_value_tables import FIELD_CODE_DOC_ID, FIELD_CODE_DOC_NAME, FIELD_CODE_PROJECT_ID, \
    FIELD_CODES_SHOW_BY_DEFAULT_NON_GENERIC, FIELD_CODES_SHOW_BY_DEFAULT_GENERIC, FIELD_CODES_HIDE_BY_DEFAULT, \
    EmptyDocumentQueryResults
from apps.rawdb.rawdb.field_handlers import FieldHandler
from apps.task.tasks import file_access_handler
from apps.users.models import User
from .models import DocumentDigestConfig, DocumentDigestSendDate, DIGEST_PERIODS_BY_CODE, \
    DOC_FILTERS_BY_CODE, DocumentNotificationSubscription


def ensure_no_dir_change(fn: str):
    if '..' in fn or '/' in fn or '\\' in fn:
        raise RuntimeError('File name should be inside its parent dir: {0}'.format(fn))


def get_notification_template_resource(rfn: str) -> Optional[bytes]:
    fn = os.path.normpath(os.path.join(settings.NOTIFICATION_CUSTOM_TEMPLATES_PATH_IN_MEDIA, rfn))
    if not fn.startswith(settings.NOTIFICATION_CUSTOM_TEMPLATES_PATH_IN_MEDIA):
        raise RuntimeError('File name should be inside its parent dir: {0}'.format(rfn))

    res = file_access_handler.read(fn)
    if res:
        return res
    fn = os.path.normpath(os.path.join(settings.NOTIFICATION_EMBEDDED_TEMPLATES_PATH, rfn))
    if not fn.startswith(settings.NOTIFICATION_EMBEDDED_TEMPLATES_PATH):
        raise RuntimeError('File name should be inside its parent dir: {0}'.format(rfn))

    with open(fn, 'br') as f:
        return f.read()


RE_SRC_ATTACHMENT = re.compile(r'(<.{1,2000}")(images/)([^"]+)(".{1,2000})>')


def send_email(log: ProcessLogger, dst_user, subject: str, txt: str, html: str, image_dir: str, cc: Set[str] = None):
    if not dst_user.email:
        log.error('Destination user {0} has no email assigned'.format(dst_user.get_full_name()))
        return

    try:
        email = EmailMultiAlternatives(subject=subject,
                                       body=txt,
                                       cc=list(cc) if cc else None,
                                       from_email=settings.DEFAULT_FROM_EMAIL,
                                       to=['"{0}" <{1}>'.format(dst_user.get_full_name(), dst_user.email)])
        if html:
            images = [m.group(3) for m in RE_SRC_ATTACHMENT.finditer(html)]
            email_html = RE_SRC_ATTACHMENT.sub(r'\1cid:\3\4', html)
            email.attach_alternative(email_html, 'text/html')

            for image_fn in images:
                data = get_notification_template_resource(os.path.join(image_dir, image_fn))
                img = MIMEImage(data)
                img.add_header('Content-Id', '<' + image_fn + '>')
                img.add_header("Content-Disposition", "inline", filename=image_fn)
                email.attach(img)

        email.send(fail_silently=False)
    except Exception as caused_by:
        msg = render_error('Unable to send email to user "{0}" (#{1})'.format(dst_user.get_full_name(), dst_user.pk),
                           caused_by=caused_by)
        log.error(msg)


class RenderedNotification:
    __slots__ = ['dst_users', 'subject', 'txt', 'html', 'image_dir', 'cc']

    def __init__(self, dst_users: Set[User], subject: str, txt: str, html: str, image_dir: str, cc: Set[str]) -> None:
        super().__init__()
        self.dst_users = dst_users
        self.subject = subject
        self.txt = txt
        self.html = html
        self.image_dir = image_dir
        self.cc = cc

    def send(self, log: ProcessLogger):
        with ThreadPoolExecutor(max_workers=settings.EMAIL_PARALLEL_SEND) as executor:
            executor.map(lambda tpl: send_email(*tpl),
                         [(log, dst_user, self.subject, self.txt, self.html, self.image_dir, self.cc)
                          for dst_user in self.dst_users],
                         timeout=settings.EMAIL_TIMEOUT * len(self.dst_users))


class RenderedDigest:
    __slots__ = ['config', 'dst_user', 'date', 'subject', 'txt', 'html', 'image_dir']

    def __init__(self, config: DocumentDigestConfig, dst_user: User, date: datetime.datetime,
                 subject: str, txt: str, html: str, image_dir: str) -> None:
        super().__init__()
        self.config = config
        self.dst_user = dst_user
        self.date = date
        self.subject = subject
        self.txt = txt
        self.html = html
        self.image_dir = image_dir

    def send(self, log: ProcessLogger):
        send_email(log=log,
                   dst_user=self.dst_user,
                   subject=self.subject,
                   txt=self.txt,
                   html=self.html,
                   image_dir=self.image_dir)
        DocumentDigestSendDate.store_digest_sent(self.config, self.dst_user, self.date)


def render_digest(config: DocumentDigestConfig,
                  dst_user: User,
                  run_date: datetime.datetime,
                  emulate_no_docs: bool = False) -> Optional[RenderedDigest]:
    period_start = None
    period_end = None

    documents_filter = DOC_FILTERS_BY_CODE[config.documents_filter]

    period = DIGEST_PERIODS_BY_CODE[config.period] if config.period else None
    if period:
        period_start, period_end = period.prepare_period(config, dst_user, run_date)

    user_field_codes = list(config.user_fields.all().values_list('code', flat=True))
    generic_field_codes = config.generic_fields or []
    field_codes = [FIELD_CODE_DOC_ID, FIELD_CODE_PROJECT_ID, FIELD_CODE_DOC_NAME] \
                  + generic_field_codes + user_field_codes

    if emulate_no_docs:
        documents = EmptyDocumentQueryResults()
    else:
        documents = documents_filter.prepare_documents(document_type=config.document_type,
                                                       user=dst_user,
                                                       field_codes=field_codes,
                                                       period_start=period_start,
                                                       period_end=period_end)

    if not config.still_send_if_no_docs and (not documents or not documents.documents):
        return None

    template_context = {
        'to_user': dst_user,
        'period_aware': documents_filter.period_aware,
        'period_start': period_start,
        'period_end': period_end,
        'documents': documents,
        'document_type': config.document_type,
        'doc_url_resolver': doc_editor_url,
        'app_url': root_url()
    }  # type: Dict[str, Any]

    subject_template = config.subject or documents_filter.subject
    header_template = config.header or documents_filter.header

    subject = Template(subject_template).render(template_context)
    header = Template(header_template).render(template_context)

    no_docs_message = None

    if config.still_send_if_no_docs:
        no_docs_message_template = config.message_if_no_docs or documents_filter.message_if_no_docs
        no_docs_message = Template(no_docs_message_template).render(template_context)

    template_context.update({
        'subject': subject,
        'header': header,
        'no_docs_message': no_docs_message
    })

    html = None

    html_template = get_notification_template_resource(os.path.join(config.template_name, 'template.html'))
    if html_template:
        html = Template(html_template.decode('utf-8')).render(template_context)

    txt_template_name = os.path.join(config.template_name, 'template.txt')
    txt_template = get_notification_template_resource(txt_template_name)
    if not txt_template:
        raise RuntimeError('Txt template not found: {0}'.format(txt_template_name))
    txt = Template(txt_template.decode('utf-8')).render(template_context)

    image_dir = os.path.join(config.template_name, 'images')

    return RenderedDigest(config=config,
                          dst_user=dst_user,
                          date=run_date,
                          subject=subject,
                          txt=txt,
                          html=html,
                          image_dir=image_dir)


def render_notification(already_sent_user_ids: Set,
                        subscription: DocumentNotificationSubscription,
                        document: Document,
                        field_handlers: List[FieldHandler],
                        field_values: Dict[str, Any],
                        changes: Dict[str, Tuple[Any, Any]] = None,
                        changed_by_user: User = None) -> Optional[RenderedNotification]:
    document_type = document.document_type
    event_info = subscription.get_event_info()
    if not event_info:
        return None
    recipients = subscription.resolve_recipients(field_values)
    recipients = {r for r in recipients if r.id not in already_sent_user_ids} if recipients else None
    if not recipients:
        return None

    display_fields = set(subscription.generic_fields or {})
    display_fields.update(FIELD_CODES_SHOW_BY_DEFAULT_GENERIC if document_type.is_generic()
                          else FIELD_CODES_SHOW_BY_DEFAULT_NON_GENERIC)
    display_fields.update({f.code for f in subscription.user_fields.all() if f.document_type == document_type})

    changes_filtered = dict()

    if changes:
        for code, old_new in changes.items():
            if code in FIELD_CODES_HIDE_BY_DEFAULT:
                continue
            if old_new[0] == old_new[1] or field_values.get(code) == old_new[0]:
                continue
            changes_filtered[code] = old_new
    changes = changes_filtered

    display_fields.update(changes.keys())

    template_context = {
        'app_url': root_url(),
        'doc_url': doc_editor_url(document_type.code, document.project_id, document.pk),
        'event_code': event_info.code,
        'event_title': event_info.title,
        'event_initiator': changed_by_user,
        'document': field_values,
        'fields': [{
            'code': h.field_code,
            'title': h.field_title,
            'type': h.field_type,
            'value': field_values.get(h.field_code),
            'changed': h.field_code in changes,
            'changes': changes.get(h.field_code),
        } for h in field_handlers if h.field_code in display_fields],
        'changes': changes,
        'changed_by_user': changed_by_user
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
