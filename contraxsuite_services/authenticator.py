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

from django.conf import settings
from django.contrib.auth.forms import password_validation
from django.urls import reverse
from django.utils import timezone
from rest_auth.models import TokenModel
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication, exceptions
from django.utils.translation import ugettext_lazy as _
from apps.common.models import AppVar

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def token_creator(token_model, user, serializer):
    """
    Patched default creator method, see settings.REST_AUTH_TOKEN_CREATOR
    see default in  rest_auth.utils.default_create_token
    """
    token, created = token_model.objects.get_or_create(user=user)
    if created is False and getattr(settings, 'REST_AUTH_TOKEN_UPDATE_EXPIRATION_DATE', False):
        token.created = timezone.now()
        token.save()
    return token


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
        token_exempt_urls = [reverse('rest_login'), reverse('rest_password_reset')]

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

        # force authentication if auto_login feature is enabled
        # if not res and config.auto_login:
        #     user = get_test_user()
        #     token, _ = TokenModel.objects.get_or_create(user=user)
        #     res = (user, token)

        # res = (user, token) for authenticated user otherwise None
        return super().authenticate(request)

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Your session has expired. Please login again.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        if self.is_token_expired(token):
            raise exceptions.AuthenticationFailed('Your session has expired. Please login again')

        self.update_token_date(token)

        return token.user, token

    @staticmethod
    def is_token_expired(token):
        """
        Check token expiration date
        """
        expires_in = timezone.timedelta(days=getattr(settings, 'REST_AUTH_TOKEN_EXPIRES_DAYS', 1))
        expiration_date = token.created + expires_in
        return timezone.now() > expiration_date

    @staticmethod
    def update_token_date(token):
        """
        Update token expiration date
        """
        if getattr(settings, 'REST_AUTH_TOKEN_UPDATE_EXPIRATION_DATE', False):
            token.created = timezone.now()
            token.save()


class TokenSerializer(serializers.ModelSerializer):
    """
    Serializer for Token model.
    """
    user_name = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = TokenModel
        fields = ('key', 'user_name', 'user')

    def get_user_name(self, obj):
        try:
            return self.context['request'].user.get_full_name()
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


class CustomPasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)

    def __init__(self, *args, **kwargs):
        # TODO: made old_password field optional
        self.old_password_field_enabled = True

        self.logout_on_password_change = getattr(
            settings, 'LOGOUT_ON_PASSWORD_CHANGE', False
        )
        super().__init__(*args, **kwargs)

        if not self.old_password_field_enabled:
            self.fields.pop('old_password')

        self.request = self.context.get('request')
        self.user = getattr(self.request, 'user', None)

    def validate_old_password(self, value):
        invalid_password_conditions = (
            self.old_password_field_enabled,
            self.user,
            not self.user.check_password(value)
        )

        if all(invalid_password_conditions):
            raise serializers.ValidationError('Invalid password')
        return value

    def validate(self, attrs):
        password = attrs['new_password']
        errors = password_validation.validate_password(password, self.user)

        if errors:
            raise serializers.ValidationError(self.set_password_form.errors)
        return attrs

    def save(self):
        new_password = self.validated_data['new_password']
        self.user.set_password(new_password)
        self.user.save()
        if not self.logout_on_password_change:
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(self.request, self.user)
