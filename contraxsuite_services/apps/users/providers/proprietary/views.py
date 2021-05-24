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


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import requests

from apps.users.providers.proprietary.provider import ProprietaryProvider
from apps.users.providers.custom_uris import AppAwareLoginView, AppAwareCallbackView
from apps.users.providers.okta.views import OktaOAuth2Adapter


class ElevateOAuth2Adapter(OktaOAuth2Adapter):
    provider_id = ProprietaryProvider.id

    def get_response(self, token):
        return requests.get(self.profile_url,
                            params={'access_token': token.token,
                                    'alt': 'json'})


oauth2_login = AppAwareLoginView.adapter_view(ElevateOAuth2Adapter)
oauth2_callback = AppAwareCallbackView.adapter_view(ElevateOAuth2Adapter)
