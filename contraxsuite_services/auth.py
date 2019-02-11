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

from allauth.account.forms import LoginForm
from rest_auth.models import TokenModel
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication, exceptions

from django.core.urlresolvers import reverse
from django.contrib.auth.forms import password_validation
from django import forms
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext as _

from apps.common.utils import get_api_module, get_test_user
from apps.common.models import AppVar
from apps.common.app_vars import ENABLE_AUTH_TOKEN_IN_QUERY_STRING

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.8/LICENSE"
__version__ = "1.1.8"
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
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        if self.is_token_expired(token):
            raise exceptions.AuthenticationFailed('Token has expired')

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


# do not move above CookieAuthentication as it throws error
user_api_module = get_api_module('users')


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
        serializer = user_api_module.UserSerializer(user)
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


class CustomSetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    new_password = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')
        password_validation.validate_password(password, self.user)
        return password

    def save(self, commit=True):
        password = self.cleaned_data["new_password"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class CustomLoginForm(LoginForm):
    """
    Inject auth_token in cookies right after successful login via plain django views
    """
    def login(self, request, **kwargs):
        response = super().login(request, **kwargs)
        token, _ = TokenModel.objects.get_or_create(user=request.user)
        response.set_cookie('auth_token', 'Token %s' % token)
        return response


class CustomPasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)

    set_password_form_class = CustomSetPasswordForm

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
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs
        )

        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        return attrs

    def save(self):
        self.set_password_form.save()
        if not self.logout_on_password_change:
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(self.request, self.user)
