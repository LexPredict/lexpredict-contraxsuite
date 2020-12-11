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
from django.http import HttpRequest
from django.shortcuts import redirect, HttpResponseRedirect

from requests.exceptions import HTTPError
from requests.models import Response
from requests_oauthlib import OAuth2Session

from apps.highq_integration.forms import HighQSyncTaskForm
from apps.highq_integration.models import HighQConfiguration
from apps.highq_integration.tasks import HighQiSheetSynchronization
from apps.highq_integration.utils import HighQ_API_Client, format_token_fields
from apps.task.views import BaseAjaxTaskView

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# -----------------------------------------------------------------------------
# AUTHENTICATION
# -----------------------------------------------------------------------------
def callback(
        request: HttpRequest,
        highq_configuration_id: int,
) -> HttpResponseRedirect:
    """
    Args:
        request (HttpRequest):
        highq_configuration_id (int):
    Returns:
        HttpResponseRedirect
    """
    highq_configuration: HighQConfiguration = \
        HighQConfiguration.objects.get(id=highq_configuration_id)

    session: OAuth2Session = OAuth2Session(
        client_id=highq_configuration.api_client_id,
        state=request.GET.get('state'),
    )

    # TODO: find a better way to construct this URL
    authorization_response: str = \
        f'https://{request.META.get("HTTP_HOST")}' \
        f'{request.get_full_path()}'

    token = session.fetch_token(
        token_url=highq_configuration.api_token_url,
        authorization_response=authorization_response,
        client_secret=highq_configuration.api_secret_key,
        include_client_id=True
    )

    # set the access_token, access_token_expiration, and refresh_token fields
    qs = HighQConfiguration.objects.filter(id=highq_configuration.id)
    qs.update(**format_token_fields(token=token))

    # a quick demonstration showing that we have authenticated the HighQ API
    highq_configuration: HighQConfiguration = qs.first()
    client = HighQ_API_Client(highq_configuration=highq_configuration)
    highq_isheet_id: int = highq_configuration.highq_isheet_id

    try:
        r_isheet_columns_admin: Response = \
            client.get_isheet_columns_admin(highq_isheet_id)
        r_isheet_columns_admin.raise_for_status()
        if r_isheet_columns_admin.ok:
            return redirect(
                to=f'{settings.API_URL_PROTOCOL}://{settings.HOST_NAME}/explorer/admin/'
                   'highq_integration/highqconfiguration/',
                permanent=False
            )
        else:
            raise HTTPError
    except HTTPError:
        # TODO: some sort of error page
        pass


class HighQSyncTaskView(BaseAjaxTaskView):
    form_class = HighQSyncTaskForm
    html_form_class = 'popup-form highq-sync'
    task_class = HighQiSheetSynchronization
