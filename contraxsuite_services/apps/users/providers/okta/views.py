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


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import requests
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter

from apps.users.adapters import email_follows_pattern
from apps.users.models import SocialAppUri, User
from apps.users.providers.okta.provider import OktaProvider
from apps.users.providers.custom_uris import AppAwareLoginView, AppAwareCallbackView, get_uri_by_app, get_callback_url


class OktaOAuth2Adapter(OAuth2Adapter):
    provider_id = OktaProvider.id

    def complete_login(self, request, app, token, **kwargs):
        resp = self.get_response(token)
        resp.raise_for_status()
        extra_data = resp.json()
        login = self.get_provider() \
            .sociallogin_from_response(request,
                                       extra_data)
        login.user.origin = User.USER_ORIGIN_SOCIAL
        if 'name' in extra_data:
            login.user.name = extra_data['name'] or login.user.name
        if not email_follows_pattern(login.user.email):
            raise OAuth2Error('Email domain is not allowed')
        return login

    def get_response(self, token):
        return requests.post(self.profile_url,
                             json={},
                             headers={'Authorization': f'Bearer {token.token}'})

    @property
    def access_token_url(self) -> str:
        return get_uri_by_app(self.app_id, SocialAppUri.URI_TYPE_TOKEN)

    @property
    def authorize_url(self) -> str:
        return get_uri_by_app(self.app_id, SocialAppUri.URI_TYPE_AUTH)

    @property
    def profile_url(self) -> str:
        return get_uri_by_app(self.app_id, SocialAppUri.URI_TYPE_PROFILE)

    def get_callback_url(self, request, app):
        if request.GET and 'next' in request.GET:
            request.session['next'] = request.GET['next']
        return get_callback_url(self, request, app)


oauth2_login = AppAwareLoginView.adapter_view(OktaOAuth2Adapter)
oauth2_callback = AppAwareCallbackView.adapter_view(OktaOAuth2Adapter)
