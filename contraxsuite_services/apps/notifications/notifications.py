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
from apps.common.file_storage import get_file_storage
from apps.common.log_utils import ProcessLogger
from apps.document.models import Document
from apps.rawdb.field_value_tables import EmptyDocumentQueryResults
from apps.rawdb.constants import FIELD_CODE_DOC_NAME, FIELD_CODE_DOC_ID, FIELD_CODE_PROJECT_ID
from apps.rawdb.rawdb.rawdb_field_handlers import RawdbFieldHandler
from apps.users.models import User
from apps.notifications.models import DocumentDigestConfig, DocumentDigestSendDate, \
    DIGEST_PERIODS_BY_CODE, DOC_FILTERS_BY_CODE

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def ensure_no_dir_change(fn: str):
    if '..' in fn or '/' in fn or '\\' in fn:
        raise RuntimeError('File name should be inside its parent dir: {0}'.format(fn))


def get_predefined_mime_type(rfn: str) -> Optional[str]:
    fn = os.path.normpath(os.path.join(settings.NOTIFICATION_CUSTOM_TEMPLATES_PATH_IN_MEDIA, rfn))
    _, file_extension = os.path.splitext(fn)
    if file_extension.lower() == '.svg':
        return 'svg+xml'
    return None


def get_notification_template_resource(rfn: str) -> Optional[bytes]:
    fn = os.path.normpath(os.path.join(settings.NOTIFICATION_CUSTOM_TEMPLATES_PATH_IN_MEDIA, rfn))
    if not fn.startswith(settings.NOTIFICATION_CUSTOM_TEMPLATES_PATH_IN_MEDIA):
        raise RuntimeError('File name should be inside its parent dir: {0}'.format(rfn))

    res = get_file_storage().read(fn)
    if res:
        return res
    fn = os.path.normpath(os.path.join(settings.NOTIFICATION_EMBEDDED_TEMPLATES_PATH, rfn))
    if not fn.startswith(settings.NOTIFICATION_EMBEDDED_TEMPLATES_PATH):
        raise RuntimeError('File name should be inside its parent dir: {0}'.format(rfn))

    with open(fn, 'br') as f:
        return f.read()


RE_SRC_ATTACHMENT = re.compile(r'(<.{1,2000}")(images/)([^"]+)(".{1,2000})>')


def send_email(log: ProcessLogger, dst_user, subject: str, txt: str, html: str,
               image_dir: str = None, cc: Set[str] = None):

    if not dst_user.email:
        log.error('Destination user {0} has no email assigned'.format(dst_user.get_full_name()))
        return

    try:
        from apps.notifications.mail_server_config import MailServerConfig
        from apps.common.app_vars import SUPPORT_EMAIL
        backend = MailServerConfig.make_connection_config()
        email = EmailMultiAlternatives(subject=subject,
                                       body=txt,
                                       cc=list(cc) if cc else None,
                                       from_email=SUPPORT_EMAIL.val or settings.DEFAULT_FROM_EMAIL,
                                       to=['"{0}" <{1}>'.format(dst_user.get_full_name(), dst_user.email)],
                                       connection=backend)
        if html:
            images = [m.group(3) for m in RE_SRC_ATTACHMENT.finditer(html)]
            email_html = RE_SRC_ATTACHMENT.sub(r'\1cid:\3\4', html)
            email.attach_alternative(email_html, 'text/html')

            if images and image_dir:
                for image_fn in images:
                    data = get_notification_template_resource(os.path.join(image_dir, image_fn))
                    mime_type = get_predefined_mime_type(image_fn)
                    try:
                        img = MIMEImage(data, _subtype=mime_type) if mime_type else MIMEImage(data)
                    except TypeError as e:
                        raise RuntimeError(f"Couldn't guess MIME type for tile {image_fn}") from e
                    img.add_header('Content-Id', '<' + image_fn + '>')
                    img.add_header("Content-Disposition", "inline", filename=image_fn)
                    email.attach(img)

        email.send(fail_silently=False)
    except Exception as caused_by:
        log.error(f'Unable to send email to user "{dst_user.get_full_name()}" (#{dst_user.pk})',
                  exc_info=caused_by)


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


class DocumentNotificationSource:
    def __init__(self,
                 document: Document,
                 field_handlers: List[RawdbFieldHandler],
                 field_values: Dict[str, Any],
                 changes: Dict[str, Tuple[Any, Any]] = None,
                 changed_by_user: User = None):
        self.document = document
        self.field_handlers = field_handlers
        self.field_values = field_values
        self.changes = changes
        self.changed_by_user = changed_by_user
