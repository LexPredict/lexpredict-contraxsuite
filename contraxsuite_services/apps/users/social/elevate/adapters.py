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
import requests
from urllib.parse import urlparse

from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.oauth2.client import OAuth2Error

from apps.users.models import User
from apps.users.social.adapters import email_follows_pattern, CustomOAuth2Adapter
from apps.users.social.elevate.provider import ElevateProvider

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


logger = logging.getLogger('django')


class ElevateOAuth2Adapter(CustomOAuth2Adapter):
    provider_id = ElevateProvider.id

    def __init__(self, request):
        super().__init__(request)
        app = SocialApp.objects.get(provider=self.provider_id)
        social_app_uri_map = dict(app.socialappuri_set.values_list('uri_type', 'uri'))
        self.authorize_url = social_app_uri_map.get('auth')
        self.access_token_url = social_app_uri_map.get('token')
        self.profile_url = social_app_uri_map.get('profile')

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url,
                            headers={'Authorization': f'Bearer {token.token}'})
        resp.raise_for_status()
        extra_data = resp.json()['data']
        try:
            login = self.get_provider() \
                .sociallogin_from_response(request,
                                           extra_data)
        except Exception as e:
            logger.error(f'ElevateOAuth2Adapter.complete_login: error in provider.sociallogin_from_response(): {e}')
            raise
        login.user.origin = User.USER_ORIGIN_SOCIAL
        if 'name' in extra_data:
            login.user.name = extra_data['name'] or login.user.name
        if not email_follows_pattern(login.user.email):
            msg = 'Email domain is not allowed'
            logger.error(f'ElevateOAuth2Adapter.complete_login: {msg}')
            raise OAuth2Error(msg)
        return login

    def get_redirect_uri(self):
        redirect_uri = super().get_redirect_uri()
        parsed_uri = urlparse(redirect_uri)
        return f'{parsed_uri.scheme}://{parsed_uri.netloc}/?provider={self.provider_id}'
