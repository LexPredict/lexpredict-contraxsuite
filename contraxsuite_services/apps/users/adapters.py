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

# Django imports
from django.conf import settings
from django.core.urlresolvers import reverse

# allauth imports
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.utils import build_absolute_uri

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.5/LICENSE"
__version__ = "1.0.7"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class AccountAdapter(DefaultAccountAdapter):
    """
    Generic account adapter.
    """

    def is_open_for_signup(self, request):
        """

        :param request:
        :return:
        """
        return getattr(settings, 'ACCOUNT_ALLOW_REGISTRATION', True)

    def get_email_confirmation_url(self, request, emailconfirmation):
        """Constructs the email confirmation (activation) url.

        Note that if you have architected your system such that email
        confirmations are sent outside of the request context `request`
        can be `None` here.

        Pass request=None to override host=localhost
        and use Site.objects.get_current().domain
        TODO: remove it after uwsgi/nginx will be configured
        """
        url = reverse(
            "account_confirm_email",
            args=[emailconfirmation.key])
        ret = build_absolute_uri(
            None,
            url)
        return ret


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """SocialAccountAdapter object
    """

    def is_open_for_signup(self, request, sociallogin):
        """

        :param request:
        :param sociallogin:
        :return:
        """
        return getattr(settings, 'ACCOUNT_ALLOW_REGISTRATION', True)
