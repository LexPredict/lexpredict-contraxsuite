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
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import logging

from allauth.utils import build_absolute_uri
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter, OAuth2LoginView, OAuth2CallbackView

from django.conf import settings
from django.urls import reverse
from django.utils.http import urlencode

from apps.users.models import SocialAppUri


logger = logging.getLogger('django')


class AdvancedRedirectOAuth2Client(OAuth2Client):
    def get_redirect_url(self, authorization_url, extra_params):
        params = {
            'client_id': self.consumer_key,
            'redirect_uri': self.callback_url,
            'scope': self.scope,
            'response_type': 'code'
        }
        if self.state:
            params['state'] = self.state
        params.update(extra_params)
        url = authorization_url
        if '?' in url:
            url += '&'
        else:
            url += '?'
        return url + urlencode(params)

    @staticmethod
    def wrap(qs: OAuth2Client):
        qs.__class__ = AdvancedRedirectOAuth2Client
        return qs


class AppAwareLoginView(OAuth2LoginView):
    def get_client(self, request, app):
        setattr(self.adapter, 'app_id', app.id)
        client = super().get_client(request, app)
        return AdvancedRedirectOAuth2Client.wrap(client)


class AppAwareCallbackView(OAuth2CallbackView):
    def get_client(self, request, app):
        setattr(self.adapter, 'app_id', app.id)
        return super().get_client(request, app)


def get_uri_by_app(app_id: int, uri_type: str) -> str:
    uris = list(SocialAppUri.objects.filter(social_app_id=app_id,
                                            uri_type=uri_type))
    if not uris:
        msg = f'URI: {uri_type} was not found for app #{app_id}'
        logger.error(msg)
        raise Exception(msg)
    return uris[0].uri


def get_callback_url(provider: OAuth2Adapter, request, app):
    callback_url = reverse(provider.provider_id + "_callback")
    protocol = getattr(settings, 'OAUTH_CALLBACK_PROTOCOL') or provider.redirect_uri_protocol
    try:
        return build_absolute_uri(request, callback_url, protocol)
    except Exception as e:
        logger.error(f'Error in get_callback_url("{callback_url}"): {e}')
        raise
