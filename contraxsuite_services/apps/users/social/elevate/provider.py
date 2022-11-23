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
from allauth.socialaccount.providers.base import ProviderAccount

from apps.users.social.custom_auxilary import derive_user_name, log_info, format_data_message
from apps.users.social.provider import CustomOAuth2Provider

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


logger = logging.getLogger('django')


class ElevateAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('link')

    def get_avatar_url(self):
        return self.account.extra_data.get('picture')

    def to_str(self):
        dflt = super().to_str()
        return self.account.extra_data.get('name', dflt)


class ElevateProvider(CustomOAuth2Provider):
    id = 'elevate'
    name = 'Elevate'
    account_class = ElevateAccount
    response_type = 'token'

    def extract_uid(self, data):
        if not data or 'id' not in data:
            raise RuntimeError('Google provider: there is no "id" field in extract_uid() arg or arg is empty')
        return str(data['id'])

    def extract_common_fields(self, data):
        user_data = {'email': data.get('email'),
                     'username': data.get('userName'),
                     'last_name': data.get('lastName'),
                     'first_name': data.get('firstName')}
        derive_user_name(user_data)
        log_info(format_data_message('Elevate IDP user data', data))
        return user_data

    def extract_email_addresses(self, data):
        ret = []
        email = data.get('email')
        if email:
            ret.append(EmailAddress(email=email,
                       verified=True,
                       primary=True))
        return ret

    def get_scope(self, request):
        return ['read']


provider_classes = [ElevateProvider]