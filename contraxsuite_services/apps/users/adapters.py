# -*- coding: utf-8 -*-

# Django imports
from django.conf import settings
from django.core.urlresolvers import reverse

# allauth imports
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.utils import build_absolute_uri

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.3/LICENSE"
__version__ = "1.0.3"
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
