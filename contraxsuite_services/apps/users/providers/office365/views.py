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

from __future__ import unicode_literals

import requests
from allauth.socialaccount.providers.oauth2.client import OAuth2Error

from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter

from apps.common.logger import CsLogger
from .provider import Office365Provider
from ..custom_auxilary import log_error, format_data_message
from ..custom_uris import get_callback_url, AppAwareLoginView, AppAwareCallbackView
from ...adapters import email_follows_pattern
from ...models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


logger = CsLogger.get_django_logger()


class Office365OAuth2Adapter(OAuth2Adapter):
    provider_id = Office365Provider.id
    _authorize_url_template = 'https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/authorize'
    _access_token_url_template = 'https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/token'
    profile_url = 'https://graph.microsoft.com/v1.0/me'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': f'Bearer {token.token}'}
        resp = requests.get(self.profile_url, headers=headers)
        extra_data = resp.json()
        try:
            login = self.get_provider().sociallogin_from_response(
                request, extra_data)
        except Exception as e:
            logger.error(f'Error in Office365OAuth2Adapter.sociallogin_from_response(): {e}')
            raise
        login.user.origin = User.USER_ORIGIN_SOCIAL
        if 'name' in extra_data:
            login.user.name = extra_data['name'] or login.user.name
        user_email = login.user.email or extra_data.get('email') or extra_data.get('mail', '')
        if not email_follows_pattern(user_email):
            msg = format_data_message('Email domain is not allowed',
                                      {
                                          'user': login.user,
                                          'extra': extra_data
                                      })
            logger.error(msg)
            log_error(msg)
            raise OAuth2Error(f'Email domain is not allowed for "{user_email}"')
        return login

    def _get_o365_tenant(self):
        # https://docs.microsoft.com/en-us/azure/active-directory/develop/active-directory-v2-protocols#endpoints
        """
        Available tenant values: common, organizations, consumers, contoso.onmicrosoft.com.
        """
        from allauth.socialaccount import app_settings
        _settings = app_settings.PROVIDERS.get(self.get_provider().id, {})
        return _settings.get('TENANT', 'common')

    @property
    def authorize_url(self):
        """Define the tenant's available for SocialLogin authorize (common, organizations, consumers, contoso.onmicrosoft.com)"""
        url = self._authorize_url_template.format(TENANT=self._get_o365_tenant())
        from ...app_vars import AZURE_AD_ALLOW_SWITCH_TENANT
        if AZURE_AD_ALLOW_SWITCH_TENANT.val():
            url += '?prompt=select_account'
        return url

    @property
    def access_token_url(self):
        """Define the tenant's available for SocialLogin token (common, organizations, consumers, contoso.onmicrosoft.com)"""
        return self._access_token_url_template.format(TENANT=self._get_o365_tenant())

    def get_callback_url(self, request, app):
        if request.GET and 'next' in request.GET:
            request.session['next'] = request.GET['next']
        return get_callback_url(self, request, app)


oauth2_login = AppAwareLoginView.adapter_view(Office365OAuth2Adapter)
oauth2_callback = AppAwareCallbackView.adapter_view(Office365OAuth2Adapter)
