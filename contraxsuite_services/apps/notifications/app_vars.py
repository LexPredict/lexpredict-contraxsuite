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

from apps.common.models import AppVar
from django.conf import settings

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


APP_VAR_EMAIL_HOST = AppVar.set(
    'Mail server', 'email_host', settings.EMAIL_HOST, 'Email host',
    access_type='admin')
APP_VAR_EMAIL_PORT = AppVar.set(
    'Mail server', 'email_port', settings.EMAIL_PORT, 'Email port',
    access_type='admin')
APP_VAR_EMAIL_USE_TLS = AppVar.set(
    'Mail server', 'email_use_tls', settings.EMAIL_USE_TLS, 'Use TLS',
    access_type='admin')
APP_VAR_EMAIL_HOST_USER = AppVar.set(
    'Mail server', 'email_host_user', settings.EMAIL_HOST_USER, 'Email user',
    access_type='admin')
APP_VAR_EMAIL_HOST_PASSWORD = AppVar.set(
    'Mail server', 'email_host_password', settings.EMAIL_HOST_PASSWORD, 'Email password',
    access_type='admin')

APP_VAR_DISABLE_EVENT_NOTIFICATIONS = AppVar.set(
    'Notifications', 'disable_event_notifications', False,
    '''Disables sending any notifications bound to document events.''')
APP_VAR_EMAIL_BACKEND = AppVar.set(
    'Mail server',
    'email_backend',
    settings.EMAIL_BACKEND,
    '''Email backend class:
    <ul>
        <li><code>"default":</code>: use default ContraxSuite Mail sender class</li>
        <li><code>"log"</code>: don't send emails, log the messages instead</li>
        <li><code>"&lt;fully.qualified.class.name&gt;"</code>: use specific Mail sender 
            class, specify the class by fully qualified name</li>
    </ul>''')

APP_VAR_SKIP_MAIL_ERRORS = AppVar.set('Mail server', 'skip_mail_errors', False,
                                      "Don't stop execution on mail sending errors")


def get_email_backend_class() -> str:
    known_values = {
        'default': 'smtp.CustomEmailBackend',
        'log': 'django.core.mail.backends.console.EmailBackend'
    }
    mail_back = APP_VAR_EMAIL_BACKEND.val()
    return known_values.get(mail_back, mail_back)
