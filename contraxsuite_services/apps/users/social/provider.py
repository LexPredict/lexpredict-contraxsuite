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

from django.urls import reverse
from django.utils.http import urlencode

from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


logger = logging.getLogger('django')

# NOTE. This file should ALWAYS be named provider.py
#  otherwise allauth lib cannot register provider


class CustomOAuth2Provider(OAuth2Provider):
    """Custom OAuth2 Provider class.
    This is fine-tuned to CLM project.

    When user with email is found in DB. Exactly
    this user is attached to the social models.
    Otherwise new user is created in DB.
    """
    response_type = 'code'

    def sociallogin_from_response(self, request, response):
        # Import should be inside this function
        # Otherwise allauth lib refuses to work.
        from allauth.socialaccount.adapter import get_adapter
        from allauth.socialaccount.models import SocialAccount, SocialLogin

        adapter = get_adapter(request)
        uid = self.extract_uid(response)
        extra_data = self.extract_extra_data(response)
        common_fields = self.extract_common_fields(response)
        socialaccount = SocialAccount(extra_data=extra_data, uid=uid, provider=self.id)
        email_addresses = self.extract_email_addresses(response)
        self.cleanup_email_addresses(common_fields.get("email"), email_addresses)
        sociallogin = SocialLogin(
            account=socialaccount, email_addresses=email_addresses
        )

        # This line is changed from the super method
        # If user with email exists in the DB
        # we use this user but setting unusable user.
        #
        # If user with email does NOT exist in the DB
        # we create new user.
        from apps.users.models import User
        try:
            sociallogin.user = User.objects.get(email=common_fields['email'])
        except User.DoesNotExist:
            user = sociallogin.user = adapter.new_user(request, sociallogin)
            adapter.populate_user(request, sociallogin, common_fields)
            user.set_unusable_password()
        return sociallogin

    def get_login_url(self, request, **kwargs):
        url = reverse(f'v1:{self.id}_login')
        if kwargs:
            url = url + '?' + urlencode(kwargs)
        return url

    def get_extra_auth_kwargs(self):
        return {}
