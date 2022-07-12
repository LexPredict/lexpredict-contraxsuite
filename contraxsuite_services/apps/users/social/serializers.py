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
from urllib.error import HTTPError

from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


logger = logging.getLogger('django')


class CustomSocialLoginSerializer(SocialLoginSerializer):
    """
    Social login serializer updated specifically
    to work with REST API.

    Also, it's updated to login user if
    one exists in DB. Otherwise, Validation error was raised in
    original serializer.
    """

    def set_callback_url(self, view, adapter_class):
        """
        Just set URL from view instead of `reverse` usage.
        `callback_url` is FE URL, not django's one.
        """
        self.callback_url = getattr(view, 'callback_url', None)

    def validate(self, attrs):
        view = self.context.get('view')
        request = self._get_request()

        if not view:
            raise serializers.ValidationError('View is not defined, pass it as a context variable')

        adapter_class = getattr(view, 'adapter_class', None)
        if not adapter_class:
            raise serializers.ValidationError('Define adapter_class in view')

        adapter = adapter_class(request)
        app = adapter.get_provider().get_app(request)

        # More info on code vs access_token
        # http://stackoverflow.com/questions/8666316/facebook-oauth-2-0-code-and-token

        access_token = attrs.get('access_token')
        code = attrs.get('code')
        # Case 1: We received the access_token
        if access_token:
            tokens_to_parse = {'access_token': access_token}
            token = access_token
            # For sign in with apple
            id_token = attrs.get('id_token')
            if id_token:
                tokens_to_parse['id_token'] = id_token

        # Case 2: We received the authorization code
        elif code:
            self.set_callback_url(view=view, adapter_class=adapter_class)
            self.client_class = getattr(view, 'client_class', None)

            if not self.client_class:
                raise serializers.ValidationError('Define client_class in view')

            provider = adapter.get_provider()
            scope = provider.get_scope(request)
            client = self.client_class(
                request,
                app.client_id,
                app.secret,
                adapter.access_token_method,
                adapter.access_token_url,
                self.callback_url,
                scope,
                scope_delimiter=adapter.scope_delimiter,
                headers=adapter.headers,
                basic_auth=adapter.basic_auth,
            )
            try:
                token = client.get_access_token(code)
            except OAuth2Error as e:
                logger.error(f"OAuth provider error: {e}")
                raise ValidationError("Incorrect input. access_token or code is invalid.")
            access_token = token['access_token']
            tokens_to_parse = {'access_token': access_token}

            # If available we add additional data to the dictionary
            for key in ['refresh_token', 'id_token', adapter.expires_in_key]:
                if key in token:
                    tokens_to_parse[key] = token[key]
        else:
            raise ValidationError('Incorrect input. access_token or code is required.')

        social_token = adapter.parse_token(tokens_to_parse)
        social_token.app = app

        try:
            login: SocialLogin = self.get_social_login(adapter, app, social_token, token)
            # complete_social_login(request, login)
        except HTTPError:
            raise ValidationError('Incorrect value')

        # This code differs from original serializer.
        # We lookup `login` user before checking his existence.
        # If user doesn't exist in DB -> create new user.
        login.lookup()
        if not login.is_existing:
            login.save(request, connect=True)

        if not login.account.user.is_active:
            raise PermissionDenied("User is not active.")

        attrs['user'] = login.account.user

        return attrs
