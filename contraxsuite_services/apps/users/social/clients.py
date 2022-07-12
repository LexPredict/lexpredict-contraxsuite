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

from urllib.parse import parse_qsl

import requests
from allauth.socialaccount.providers.oauth2.client import OAuth2Client, OAuth2Error

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class CustomOAuth2Client(OAuth2Client):
    """Custom OAuth2 client class.

    The client is used to exchange `code` into `token`.
    Here we update `get_access_token` method to
    pass correct callback URL into provider's endpoint.

    Previously it was passed complex ParseResult object
    that is not correctly json-serializable
    """

    def get_access_token(self, code):
        """
        Exchange `code` into `access_token`
        """
        data = {
            "redirect_uri": self.callback_url, #self.callback_url.geturl(),
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.consumer_key,
            "client_secret": self.consumer_secret,
        }
        url = self.access_token_url
        # TODO: Proper exception handling
        resp = requests.post(url, data=data, headers=self.headers)

        access_token = None
        if resp.status_code in [200, 201]:
            # Weibo sends json via 'text/plain;charset=UTF-8'
            if (
                    resp.headers["content-type"].split(";")[0] == "application/json"
                    or resp.text[:2] == '{"'
            ):
                access_token = resp.json()
            else:
                access_token = dict(parse_qsl(resp.text))
        if not access_token or "access_token" not in access_token:
            raise OAuth2Error("Error retrieving access token: %s" % resp.content)
        return access_token
