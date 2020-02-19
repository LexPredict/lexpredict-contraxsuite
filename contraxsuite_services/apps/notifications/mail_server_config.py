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

from importlib import import_module
from typing import Dict, Any

from django.core.mail.backends.base import BaseEmailBackend
from apps.notifications.app_vars import APP_VAR_EMAIL_BACKEND

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class MailServerConfig:
    backend_by_type = {}  # type: Dict[str, Any]

    @staticmethod
    def make_connection_config() -> BaseEmailBackend:
        from apps.notifications.app_vars import APP_VAR_EMAIL_HOST, APP_VAR_EMAIL_USE_TLS, \
            APP_VAR_EMAIL_PORT, APP_VAR_EMAIL_HOST_USER, APP_VAR_EMAIL_HOST_PASSWORD
        from apps.common.models import AppVar

        cache_vars = AppVar.get_values_by_category(AppVar.MAIL_CATEGORY)
        backend_class = APP_VAR_EMAIL_BACKEND.get_cached_value(cache_vars)
        ctor = MailServerConfig.import_class(backend_class)

        return ctor(host=APP_VAR_EMAIL_HOST.get_cached_value(cache_vars),
                    port=APP_VAR_EMAIL_PORT.get_cached_value(cache_vars),
                    username=APP_VAR_EMAIL_HOST_USER.get_cached_value(cache_vars),
                    password=APP_VAR_EMAIL_HOST_PASSWORD.get_cached_value(cache_vars),
                    use_tls=APP_VAR_EMAIL_USE_TLS.get_cached_value(cache_vars),
                    fail_silently=False)

    @staticmethod
    def import_class(class_name: str):
        if class_name in MailServerConfig.backend_by_type:
            return MailServerConfig.backend_by_type[class_name]

        dotpos = class_name.rfind('.')
        mod_path = class_name[:dotpos]
        cls_path = class_name[dotpos + 1:]

        cls = getattr(import_module(mod_path), cls_path)
        MailServerConfig.backend_by_type[class_name] = cls
        return cls
