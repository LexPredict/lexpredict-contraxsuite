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

from django.http import HttpResponseForbidden

from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter, get_adapter
from allauth.socialaccount.providers import registry

from .provider import Office365Provider

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


logger = logging.getLogger('django')


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    # based on: https://github.com/thenewguy/django-allauth-adfs/blob/master/allauth_adfs/socialaccount/adapter.py

    def pre_social_login(self, request, sociallogin):
        # new user logins are handled by populate_user
        if sociallogin.is_existing:
            changed, user = self.update_user_fields(request, sociallogin)
            if changed:
                user.save()

    def populate_user(self, request, sociallogin, data):
        try:
            user = super().populate_user(request, sociallogin, data)
        except Exception as e:
            logger.error(f'SocialAccountAdapter.populate_user() error: {e}')
            raise
        self.update_user_fields(request, sociallogin, user)
        return user

    def update_user_fields(self, request, sociallogin=None, user=None):
        changed = False
        if user is None:
            user = sociallogin.account.user
        office365_provider = registry.by_id(Office365Provider.id, request)

        false_keys = ["is_staff", "is_superuser"]
        boolean_keys = false_keys + ["is_active"]
        copy_keys = boolean_keys + ["first_name", "last_name", "email", "username"]

        if sociallogin is not None and sociallogin.account.provider == Office365Provider.id:
            data = sociallogin.account.extra_data
            values = office365_provider.extract_common_fields(data)
            for key in copy_keys:
                # it is assumed that values are cleaned and set for all
                # fields and if any of the boolean_keys are not provided
                # in the raw data they should be set to False by
                # the extract_common_fields method
                if key in values and getattr(user, key) != values[key]:
                    setattr(user, key, values[key])
                    changed = True
        else:
            for key in false_keys:
                if getattr(user, key):
                    msg = "Staff users must authenticate via the %s provider!" % office365_provider.name
                    logger.error(f'SocialAccountAdapter: {msg}')
                    response = HttpResponseForbidden(msg)
                    raise ImmediateHttpResponse(response)
        return changed, user
