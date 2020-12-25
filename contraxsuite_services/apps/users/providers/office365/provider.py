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

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

from apps.users.providers.custom_auxilary import route_next_param_to_query, derive_user_name, \
    format_data_message, is_email_addr_format, log_error

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class Office365Account(ProviderAccount):

    def to_str(self):
        name = '{0} {1}'.format(self.account.extra_data.get('first_name', ''),
                                self.account.extra_data.get('last_name', ''))
        if name.strip() != '':
            return name
        return super().to_str()


class Office365Provider(OAuth2Provider):
    id = str('office365')
    name = 'Office365'
    account_class = Office365Account

    def get_scope(self, request):
        scope = set(super().get_scope(request))
        scope.add('openid')
        return list(scope)

    def get_default_scope(self):
        return ['openid', 'User.read']

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        user_email = data.get('mail', '')
        if not user_email:
            from apps.users.app_vars import READ_AZURE_AD_PRINCIPAL_EMAIL
            if READ_AZURE_AD_PRINCIPAL_EMAIL.val:
                user_email = data.get('userPrincipalName', '')
                if not is_email_addr_format(user_email):
                    user_email = ''

        if not user_email:
            msg = format_data_message("Office365 user data doesn't contain email claim", data)
            log_error(msg)

        user_data = {'email': user_email,
                     'username': user_email,
                     'name': data.get(self.get_settings().get('USERNAME_FIELD', 'displayName')),
                     'last_name': data.get('surname'),
                     'first_name': data.get('givenName')}
        derive_user_name(user_data)

        return user_data


route_next_param_to_query()


provider_classes = [Office365Provider]
