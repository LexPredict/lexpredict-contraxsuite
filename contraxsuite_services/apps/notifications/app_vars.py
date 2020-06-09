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
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


APP_VAR_DISABLE_EVENT_NOTIFICATIONS = AppVar.set(
    'Notifications', 'disable_event_notifications', False,
    '''Disables sending any notifications bound to document events.''')

APP_VAR_EMAIL_BACKEND = AppVar.set('Mail server', 'email_backend', settings.EMAIL_BACKEND,
                                "Email backend class")
APP_VAR_EMAIL_HOST = AppVar.set('Mail server', 'email_host', settings.EMAIL_HOST,
                                "Email host")
APP_VAR_EMAIL_PORT = AppVar.set('Mail server', 'email_port', settings.EMAIL_PORT,
                                "Email port")
APP_VAR_EMAIL_USE_TLS = AppVar.set('Mail server', 'email_use_tls', settings.EMAIL_USE_TLS,
                                "Use TLS")
APP_VAR_EMAIL_HOST_USER = AppVar.set('Mail server', 'email_host_user', settings.EMAIL_HOST_USER,
                                "Email user")
APP_VAR_EMAIL_HOST_PASSWORD = AppVar.set('Mail server', 'email_host_password', settings.EMAIL_HOST_PASSWORD,
                                "Email password")
