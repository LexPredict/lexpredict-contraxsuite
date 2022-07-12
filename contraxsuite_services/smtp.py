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

import logging

# Django imports
from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


logger = logging.getLogger('django')


class CustomEmailBackend(EmailBackend):

    def __init__(self, **kwargs):
        """
        Use user-defined vars for email config instead of hardcoded in settings to be able to reconfigure on the fly
        """
        from apps.notifications.app_vars import APP_VAR_EMAIL_HOST, APP_VAR_EMAIL_PORT, APP_VAR_EMAIL_HOST_USER, \
            APP_VAR_EMAIL_HOST_PASSWORD, APP_VAR_EMAIL_USE_TLS
        config = dict(
            host=APP_VAR_EMAIL_HOST.val(),
            port=APP_VAR_EMAIL_PORT.val(),
            username=APP_VAR_EMAIL_HOST_USER.val(),
            password=APP_VAR_EMAIL_HOST_PASSWORD.val(),
            use_tls=APP_VAR_EMAIL_USE_TLS.val(),
        )
        kwargs.update(config)
        super().__init__(**kwargs)

    def send_messages(self, email_messages):
        for message in email_messages:
            if 'Reply-To' not in message.extra_headers:
                from apps.common.app_vars import SUPPORT_EMAIL
                message.extra_headers['Reply-To'] = SUPPORT_EMAIL.val() or settings.DEFAULT_REPLY_TO
        try:
            return super().send_messages(email_messages)
        except Exception as e:
            from apps.notifications.app_vars import APP_VAR_SKIP_MAIL_ERRORS
            if APP_VAR_SKIP_MAIL_ERRORS.val():
                logger.error(f'Error in CustomEmailBackend.send_messages(): {e}')
            else:
                raise
