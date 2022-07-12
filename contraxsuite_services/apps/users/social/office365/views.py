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

import logging

from django.conf import settings

from dj_rest_auth.registration.views import SocialLoginView

from apps.users.social.office365.adapters import Office365OAuth2Adapter
from apps.users.social.clients import CustomOAuth2Client
from apps.users.social.serializers import CustomSocialLoginSerializer

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


logger = logging.getLogger('django')


class Office365LoginView(SocialLoginView):
    """Authenticate user (register first if the profile doesn't exist)
    via Microsoft office365 in CLM.

    The login algorithm is next:

    1. Redirect to microsoft auth page `https://login.microsoftonline.com/consumers|common/oauth2/v2.0/authorize`
        with correct `client_id`, `redirect_url`, `response_type`, and `scope`;
    2. After microsoft auth user will be redirected to callback url;
    3. Pass the `code` from query params to this endpoint.
    """
    adapter_class = Office365OAuth2Adapter
    callback_url = settings.SOCIAL_OFFICE365_CALLBACK_URL
    client_class = CustomOAuth2Client
    serializer_class = CustomSocialLoginSerializer
