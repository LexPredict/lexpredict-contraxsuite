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

import binascii
import logging
import os
import re
from functools import lru_cache
from typing import Tuple

from django.conf import settings
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as ug

from rest_auth.models import TokenModel
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication, exceptions

from apps.common import redis
from apps.common.models import AppVar
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


logger = logging.getLogger('django')


class TokenCache:

    token_prefix = 'auth_token:'
    token_re = re.compile(rf'{token_prefix}(.+)')
    users_cache_key = f'{token_prefix}all'
    key_expiration_time = int(timezone.timedelta(
        days=getattr(settings, 'REST_AUTH_TOKEN_EXPIRES_DAYS', 1)).total_seconds())
    cached_users_expiration_time = 5 * 60

    @staticmethod
    def gen_auth_token():
        return binascii.hexlify(os.urandom(20)).decode()

    def get_token_key(self, token):
        return f'{self.token_prefix}{token}'

    def get_token_from_key(self, token_key):
        return self.token_re.findall(token_key)[0]

    def get_token_user_key(self, user_id):
        return f'{self.token_prefix}{user_id}'

    def create(self, user):
        token_user_key = self.get_token_user_key(user.id)
        token = self.gen_auth_token()
        token_key = self.get_token_key(token)
        # create token pair - because redis has no support for quick search by value (token)
        redis.push(token_user_key, token_key, ex=self.key_expiration_time)
        redis.push(token_key, token_user_key, ex=self.key_expiration_time)
        logger.info(f'Cached auth token "{token_user_key}:{token}" for user {user}')
        return token_user_key, self.get_token_object(user, token)

    def update(self, user):
        token_user_key, token_key, token = self.get_token_keys(user)
        if token_key is None:
            return self.create(user)
        if getattr(settings, 'REST_AUTH_TOKEN_UPDATE_EXPIRATION_DATE', False):
            # update token pair - set expiration time
            redis.r.expire(token_user_key, self.key_expiration_time)
            redis.r.expire(token_key, self.key_expiration_time)
        return token_user_key, self.get_token_object(user, token)

    def create_or_update(self, user):
        token_user_key = self.get_token_user_key(user.id)
        # user has no auth token - create token
        if not redis.exists(token_user_key):
            return self.create(user)
        # user has auth token - update expiration date
        return self.update(user)

    def delete(self, user):
        token_user_key = self.get_token_user_key(user.id)
        token_key = redis.pop(token_user_key)
        redis.r.delete(token_user_key, token_key)

    def cache_users(self, users):
        # cache user qs for 5 min
        redis.push(self.users_cache_key, users, ex=self.cached_users_expiration_time)

    def get_cached_user(self, user_id):
        users = redis.pop(self.users_cache_key)
        if not users:
            users = {str(i.pk): i for i in User.objects.all()}
            self.cache_users(users)
        # for new user
        if user_id not in users:
            users[user_id] = User.objects.get(id=user_id)
            self.cache_users(users)
        return users[user_id]

    def get_user(self, token):
        token_key = self.get_token_key(token)
        token_user_key = redis.pop(token_key)
        if token_user_key is None:
            logger.warning(f'Not found cached token user key for token "{token}"')
            return
        try:
            user_id = self.token_re.findall(token_user_key)[0]
            # try to avoid querying db users in each API request
            user = self.get_cached_user(user_id)
            # user = User.objects.get(id=user_id)
            return user
        except:
            logger.warning(f'Not found cached user for token "{token_user_key}:{token}"')
            return

    def get_token_keys(self, user):
        token_user_key = self.get_token_user_key(user.id)
        token_key = redis.pop(token_user_key)
        token = self.get_token_from_key(token_key)
        return token_user_key, token_key, token

    def get_token_object(self, user, token):
        """
        Mock Token instance to return by LoginView serializer
        - see rest_auth.views.LoginView.get_response and .TokenSerializer
        """
        if token.startswith(self.token_prefix):
            token = self.token_re.findall(token)[0]
        return TokenModel(user=user, key=token)


token_cache = TokenCache()


def token_creator(token_model, user, serializer):
    """
    Patched default creator method, see settings.REST_AUTH_TOKEN_CREATOR
    see default in  rest_auth.utils.default_create_token
    """
    _, token = token_cache.create_or_update(user)
    return token


@receiver(signal=post_save, sender=User)
def delete_token_on_inactivate_user(instance, **kwargs):
    if not instance.is_active:
        token_cache.delete(instance)


@receiver(signal=post_delete, sender=User)
def delete_token_on_delete_user(instance, **kwargs):
    token_cache.delete(instance)


@receiver(user_logged_out)
def delete_token_on_logout(sender, request, user, **kwargs):
    token_cache.delete(user)


@receiver(user_logged_in)
def create_token_on_login(sender, request, user, **kwargs):
    token_cache.create_or_update(user)


# FIXME: old impl.
# def token_creator(token_model, user, serializer):
#     """
#     Patched default creator method, see settings.REST_AUTH_TOKEN_CREATOR
#     see default in  rest_auth.utils.default_create_token
#     """
#     token, created = token_model.objects.get_or_create(user=user)
#     if created is False and getattr(settings, 'REST_AUTH_TOKEN_UPDATE_EXPIRATION_DATE', False):
#         token.created = timezone.now()
#         token.save()
#     return token


class CookieAuthentication(TokenAuthentication):
    """
    Authentication system for rest API requests
    1. check for auth token in request in `AUTHORIZATION` header
    2. if it doesn't exist and if request path is not in excepted urls:
    3. try to get auth token from query string (GET params)
    4. try to get auth token from cookies
    5. set AUTHORIZATION header to be equal to found token
    6. authenticate

    See response middleware in common.middleware.CookieMiddleware -
    it sets cookie from existing AUTHORIZATION header into response
    """

    def authenticate(self, request):
        # Add urls that don't require authorization
        token_exempt_urls = [reverse('rest_login'), reverse('rest_password_reset'), reverse('v1:app-variables')]

        # authenticate only if request path is not in excepted urls
        # first check for existing AUTHORIZATION header
        if not request.META.get('HTTP_AUTHORIZATION') and request.META['PATH_INFO'] not in token_exempt_urls:
            # second check to fetch auth_token from query string (GET params)
            # token should be just key without "Token "
            from apps.common.app_vars import ENABLE_AUTH_TOKEN_IN_QUERY_STRING

            if ENABLE_AUTH_TOKEN_IN_QUERY_STRING.val and request.GET.get('auth_token'):
                auth_token = request.GET.get('auth_token')
                if auth_token:
                    auth_token = 'Token ' + request.GET.get('auth_token')
            # either get auth token from cookies
            else:
                auth_token = request.COOKIES.get('auth_token', '')
            # inject auth token into AUTHORIZATION header to authenticate via standard rest auth
            request.META['HTTP_AUTHORIZATION'] = auth_token

        res = super().authenticate(request)
        return res

    def authenticate_credentials(self, key) -> Tuple[User, str]:
        user = token_cache.get_user(token=key)
        if user is None:
            raise exceptions.AuthenticationFailed(
                ug('Wrong authentication token or your session has expired. Please login.'))
        _, token = token_cache.update(user)
        return user, token


# FIXME: old impl.
# class _CookieAuthentication(TokenAuthentication):
#     """
#     Authentication system for rest API requests
#     1. check for auth token in request in `AUTHORIZATION` header
#     2. if it doesn't exist and if request path is not in excepted urls:
#     3. try to get auth token from query string (GET params)
#     4. try to get auth token from cookies
#     5. set AUTHORIZATION header to be equal to found token
#     6. authenticate
#
#     See response middleware in common.middleware.CookieMiddleware -
#     it sets cookie from existing AUTHORIZATION header into response
#     """
#
#     def authenticate(self, request):
#         # Add urls that don't require authorization
#         token_exempt_urls = [reverse('rest_login'), reverse('rest_password_reset'), reverse('v1:app-variables')]
#
#         # authenticate only if request path is not in excepted urls
#         # first check for existing AUTHORIZATION header
#         if not request.META.get('HTTP_AUTHORIZATION') and request.META['PATH_INFO'] not in token_exempt_urls:
#             # second check to fetch auth_token from query string (GET params)
#             # token should be just key without "Token "
#             from apps.common.app_vars import ENABLE_AUTH_TOKEN_IN_QUERY_STRING
#
#             if ENABLE_AUTH_TOKEN_IN_QUERY_STRING.val and request.GET.get('auth_token'):
#                 auth_token = request.GET.get('auth_token')
#                 if auth_token:
#                     auth_token = 'Token ' + request.GET.get('auth_token')
#             # either get auth token from cookies
#             else:
#                 auth_token = request.COOKIES.get('auth_token', '')
#             # inject auth token into AUTHORIZATION header to authenticate via standard rest auth
#             request.META['HTTP_AUTHORIZATION'] = auth_token
#
#         # force authentication if auto_login feature is enabled
#         # if not res and config.auto_login:
#         #     user = get_test_user()
#         #     token, _ = TokenModel.objects.get_or_create(user=user)
#         #     res = (user, token)
#
#         # res = (user, token) for authenticated user otherwise None
#
#         res = super().authenticate(request)
#         return res
#
#     def authenticate_credentials(self, key) -> Tuple[User, str]:
#         model = self.get_model()
#         try:
#             token = model.objects.select_related('user').get(key=key)
#         except model.DoesNotExist:
#             raise exceptions.AuthenticationFailed(_('Wrong authentication token. Please login.'))
#
#         if not token.user.is_active:
#             raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))
#
#         if self.is_token_expired(token):
#             raise exceptions.AuthenticationFailed('Your session has expired. Please login again')
#
#         self.update_token_date(token)
#
#         return token.user, token
#
#     @staticmethod
#     def is_token_expired(token):
#         """
#         Check token expiration date
#         """
#         expires_in = timezone.timedelta(days=getattr(settings, 'REST_AUTH_TOKEN_EXPIRES_DAYS', 1))
#         expiration_date = token.created + expires_in
#         return timezone.now() > expiration_date
#
#     @staticmethod
#     def update_token_date(token):
#         """
#         Update token expiration date
#         """
#         if getattr(settings, 'REST_AUTH_TOKEN_UPDATE_EXPIRATION_DATE', False):
#             token.created = timezone.now()
#             token.save()


class TokenSerializer(serializers.ModelSerializer):
    """
    Serializer for Token model.
    """
    user_name = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    schema_component_name = 'LoginResponse'

    class Meta:
        model = TokenModel
        fields = ('key', 'user_name', 'user')

    def get_user_name(self, obj):
        try:
            return self.context['request'].user.name
        except:
            return None

    def get_user(self, obj):
        user = self.context['request'].user
        from apps.users.api.v1 import UserSerializer
        serializer = UserSerializer(user)
        serializer.context['request'] = self.context['request']
        return serializer.data

    def to_representation(self, obj):
        """
        Inject additional data into login response
        """
        data = super().to_representation(obj)
        data['release_version'] = settings.VERSION_NUMBER
        frontend_vars = {i: j for i, j in AppVar.objects.filter(name__startswith='frontend_')
            .values_list('name', 'value')}
        data.update(frontend_vars)
        return data
