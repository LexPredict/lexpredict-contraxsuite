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

import importlib
import inspect
import logging
from typing import Optional
from urllib import parse

import regex as re

from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter

from django.conf import settings
from django.contrib.auth.models import Group
from django.utils.http import urlencode

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin, SocialApp
from allauth.socialaccount.providers import registry
from django.core.exceptions import PermissionDenied
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


logger = logging.getLogger('django')


@receiver(post_save, sender=User)
def set_new_social_user_default_group(sender, instance: User, **kwargs):
    if not kwargs.get('created', False):
        return
    if instance.origin != User.USER_ORIGIN_SOCIAL:
        return
    group_name = settings.DEFAULT_USER_GROUP
    if not group_name:
        return
    group = Group.objects.get(name=group_name)
    instance.groups.add(group)
    instance.save()


@receiver(pre_save, sender=User)
def set_new_social_user_inactive(sender, instance: User, **_kwargs):
    if instance._state.adding is not True:
        return
    if instance.id:
        return
    if instance.origin != User.USER_ORIGIN_SOCIAL:
        return

    email = instance.email
    is_auto_reg_email = email_follows_pattern(email, settings.AUTO_REG_EMAIL_DOMAINS)
    if is_auto_reg_email:
        return

    is_allowed_email = email_follows_pattern(email, settings.ALLOWED_EMAIL_DOMAINS)
    if is_allowed_email:
        # this is a new social account registration - we'll make it inactive
        # until the administrator confirms the user account
        instance.is_active = False
        return
    logger.error(f'email "{email}" is not allowed')
    raise PermissionDenied()


def email_follows_pattern(email: str, pattern: Optional[str] = None) -> bool:
    if pattern is None:
        pattern = settings.ALLOWED_EMAIL_DOMAINS
    if not email or not pattern:
        return False
    at_index = email.index('@')
    if not at_index:
        return False
    email = email[at_index + 1:]

    patterns = [p for p in (pattern or '*').split(',') if p]
    if not patterns:
        return False
    for pattern in patterns:
        ptrn = '^' + pattern.replace('.', r'\.').replace('*', '.*') + '$'
        reg = re.compile(ptrn)
        for _mth in reg.finditer(email):
            return True
    return False


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """SocialAccountAdapter object"""
    def pre_social_login(self, request, sociallogin: SocialLogin):
        """
        The user is authenticated in some "social app". Consider the following
        scenarios:
        1 - the user email is found in our DB among registered users' emails
        1.1 - the user email is registered. We just "connect" the social account
              to the user "CS native" account or if these 2 accounts are already connected
              we proceed with logging in.
        1.2 - the user email is not registered. We deny the request.

        2 - the user email is not found in our DB among registered users' emails
        2.1 - the user email is registered. We register an inactive user.
        2.2 - the user email is not registered. We either allow or deny registration
              based on SOCIALACCOUNT_EMAIL_REQUIRED setting
        """

        emails = [e for e in sociallogin.email_addresses if e.primary]
        if not emails:
            return
        email_adr, email_verified = emails[0].email, emails[0].verified

        if settings.SOCIALACCOUNT_EMAIL_VERIFIED_ONLY and not email_verified:
            msg = f'Email "{email_adr}" is not verified'
            logger.error(msg)
            raise PermissionDenied(msg)

        try:
            user = User.objects.get(email__iexact=email_adr)
        except User.DoesNotExist:
            return

        # we're here: 1 - the user email is found in our DB among registered users' emails
        if settings.SOCIALACCOUNT_EMAIL_VERIFIED_ONLY and not email_verified:
            # 1.2 - deny the request
            msg = f'Existing email "{email_adr}" is not verified'
            logger.error(msg)
            raise PermissionDenied(msg)

        try:
            if not sociallogin.is_existing:
                sociallogin.connect(request, user)
            else:
                sociallogin.state['process'] = 'login'
                # perform_login(request, user, 'none')  # TODO: login with JWT?
                # TODO: somewhere in this place it tries to http redirect to account_inactive
                # django.urls.exceptions.NoReverseMatch: Reverse for 'account_inactive' not found.
                # 'account_inactive' is not a valid view function or pattern name.
        except Exception as e:
            logger.error(f'Error entering social account ({email_adr}): {e}')
            raise

    def is_open_for_signup(self, request, sociallogin):
        return settings.SOCIAL_ACCOUNT_ALLOW_REGISTRATION

    def populate_user(self,
                      request,
                      sociallogin,
                      data):
        usr = super().populate_user(request, sociallogin, data)
        usr.username = data.get('username') or data.get('email')
        return usr


class CustomOAuth2Adapter(OAuth2Adapter):

    def get_redirect_uri(self):
        return settings.SOCIAL_CALLBACK_URL_TEMPLATE.format(self.provider_id)


def get_social_apps_urls():
    providers = registry.get_list()
    provider_map = {}
    for provider in providers:
        package = provider.get_package()
        try:
            adapter_module = importlib.import_module(package + '.adapters')
        except ImportError:
            continue
        is_class_member = lambda member: inspect.isclass(member) and member.__module__ == adapter_module.__name__ \
                                         and hasattr(member, 'provider_id') and member.provider_id == provider.id
        adapter_classes = inspect.getmembers(adapter_module, is_class_member)
        if not adapter_classes:
            continue
        adapter = adapter_classes[0][1](request=None)

        class request:
            GET = {}

        authorize_url_params = {
            'client_id': SocialApp.objects.get(provider=provider.id).client_id,
            'redirect_uri': adapter.get_redirect_uri(),
            'scope': adapter.scope_delimiter.join(set(provider.get_scope(request))),
            'response_type': provider.response_type,
        }
        authorize_url_params.update(provider.get_extra_auth_kwargs())

        authorize_url_parts = list(parse.urlparse(adapter.authorize_url))
        authorize_url_query = dict(parse.parse_qsl(authorize_url_parts[4]))
        authorize_url_query.update(authorize_url_params)
        authorize_url_parts[4] = urlencode(authorize_url_query)
        authorize_url = parse.urlunparse(authorize_url_parts)

        provider_map[provider.id] = dict(
            authorize_url=authorize_url,
            access_token_url=adapter.access_token_url,
            profile_url=adapter.profile_url,
            login_url=provider.get_login_url(None),
        )

    return provider_map
