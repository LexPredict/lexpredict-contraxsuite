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

from allauth.account.models import EmailAddress
from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.providers.base import AuthAction, ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

from apps.users.providers.custom_auxilary import route_next_param_to_query, derive_user_name, log_info, \
    format_data_message

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


logger = logging.getLogger('django')


class Scope(object):
    EMAIL = 'email'
    PROFILE = 'profile'


class GoogleAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('link')

    def get_avatar_url(self):
        return self.account.extra_data.get('picture')

    def to_str(self):
        dflt = super().to_str()
        return self.account.extra_data.get('name', dflt)


class GoogleProvider(OAuth2Provider):
    id = 'google'
    name = 'Google'
    account_class = GoogleAccount

    def get_default_scope(self):
        scope = [Scope.PROFILE]
        if QUERY_EMAIL:
            scope.append(Scope.EMAIL)
        return scope

    def get_auth_params(self, request, action):
        ret = super(GoogleProvider, self).get_auth_params(request,
                                                          action)
        if action == AuthAction.REAUTHENTICATE:
            ret['prompt'] = 'select_account consent'
        return ret

    def extract_uid(self, data):
        if not data or 'id' not in data:
            raise RuntimeError(f'Google provider: there is no "id" field in extract_uid() arg or arg is empty')
        return str(data['id'])

    def extract_common_fields(self, data):
        user_data = {'email': data.get('email'),
                     'username': data.get('email'),
                     'last_name': data.get('family_name'),
                     'first_name': data.get('given_name')}
        derive_user_name(user_data)
        log_info(format_data_message('Google IDP user data', data))
        return user_data

    def extract_email_addresses(self, data):
        ret = []
        email = data.get('email')
        if email and data.get('verified_email'):
            ret.append(EmailAddress(email=email,
                       verified=True,
                       primary=True))
        return ret


route_next_param_to_query()


provider_classes = [GoogleProvider]
