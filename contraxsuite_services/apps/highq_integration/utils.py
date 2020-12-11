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

import datetime
from abc import ABC
from urllib.parse import ParseResult, urlparse, urljoin
from typing import Dict, Generator, List, Optional, Union, Tuple
from requests.models import Response, HTTPError
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.tokens import OAuth2Token

from django.shortcuts import redirect, HttpResponseRedirect
from django.utils import timezone

from apps.highq_integration.models import HighQConfiguration
from apps.highq_integration.dto import *


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class _Router(ABC):
    """
    Provides generic REST methods.
    """

    def get(
        self,
        endpoint: str,
        parameters: dict = None,
    ) -> Response:
        request_url = urljoin(self.api_base_url.geturl(), endpoint)
        # logging.debug('GET from %s', request_url)
        return self.session.get(request_url, params=parameters)

    def post(
        self,
        endpoint: str,
        data: dict = None,
        json: dict = None,
        files: dict = None,
    ) -> Response:
        """
        Args:
            endpoint (str): An API endpoint to query.
            data (dict): Data to POST.
            files (dict): Files to POST.

        Returns:
            requests.models.Response: The request response.
        """
        request_url = urljoin(self.api_base_url.geturl(), endpoint)
        # logging.debug('POST to %s with data=%s and files=%s', request_url, data, files)
        return self.session.post(request_url, data=data, json=json, files=files)

    def put(
        self,
        endpoint: str,
        data: dict = None,
        json: dict = None,
    ) -> Response:
        """
        Args:
            endpoint (str): An API endpoint to query.
            data (dict): Data to PUT.

        Returns:
            requests.models.Response: The request response.
        """
        request_url = urljoin(self.api_base_url.geturl(), endpoint)
        # logging.debug('PUT to %s with data=%s', request_url, data)
        return self.session.put(request_url, data=data, json=json)


class HighQ_API_Client(_Router):

    def __init__(
        self,
        highq_configuration: HighQConfiguration
    ) -> None:
        self.highq_configuration: HighQConfiguration = highq_configuration
        self.api_base_url: ParseResult = urlparse(
            highq_configuration.api_base_url
            if highq_configuration.api_base_url[-1] == '/'
            else f'{highq_configuration.api_base_url}/'
        )
        self.session: OAuth2Session = self._start_session()

    def _start_session(self) -> OAuth2Session:
        """
        """
        session = OAuth2Session(
            client_id=self.highq_configuration.api_client_id,
            token={'access_token': self.highq_configuration.access_token}
        )
        session.headers.update({'Accept': 'application/JSON'})
        return session

    def get_highq_file(
        self,
        file_id: int,
        original: bool = False,
    ) -> Response:
        """
        """
        return self.get(
            endpoint=f'3/files/{file_id}/content',
            parameters={'original': original}
        )

    def get_isheet_record_id(
        self,
        fileid: int,
    ) -> Response:
        """
        """
        return self.get(endpoint=f'3/files/{fileid}/isheetRecordID')

    def get_isheet_columns(
        self,
        isheetid: int,
    ) -> Response:
        """
        """
        return self.get(f'3/isheets/{isheetid}/columns')

    def get_isheet_columns_admin(
        self,
        isheetid: int,
    ) -> Response:
        """
        """
        return self.get(f'3/isheets/admin/{isheetid}/columns')


    def get_isheet_items(
        self,
        isheetid: int,
    ) -> Response:
        """
        """
        return self.get(f'3/isheet/{isheetid}/items')

    def get_isheet_item(
        self,
        isheetid: int,
        itemid: int,
    ) -> Response:
        """
        """
        return self.get(f'3/isheet/{isheetid}/items{itemid}')

    def post_isheet_items(
        self,
        isheetid: int,
        isheet_dto: ISheetDTO,
    ) -> Response:
        """
        """
        return self.post(
            endpoint=f'3/isheet/{isheetid}/items',
            json=isheet_dto.sanitize_for_serialization(isheet_dto)
        )

    def put_isheet_items(
        self,
        isheetid: int,
        itemid: int,
        isheet_dto: ISheetDTO,
    ) -> Response:
        """
        """
        return self.put(
            endpoint=f'3/isheet/{isheetid}/items/{itemid}',
            json=isheet_dto.sanitize_for_serialization(isheet_dto)
        )

    def refresh_access_token(
        self
    ) -> Response:
        """
        """
        parameters = {
            'client_id': self.highq_configuration.api_client_id,
            'client_secret': self.highq_configuration.api_secret_key,
            'grant_type': 'refresh_token',
            'refresh_token': self.highq_configuration.refresh_token
        }

        return self.session.post(
            url=self.highq_configuration.api_token_url,
            params=parameters,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

    def get_changes(
        self,
        siteid: int,
        nextsyncposition: int,
        contenttype: str = '',
    ) -> Response:
        parameters: Dict[str, Union[int, str]] = {
            'siteid': siteid,
            'syncpositionid': nextsyncposition,
            'contenttype': contenttype
        }

        return self.get(endpoint=f'3/changes', parameters=parameters)

    def get_files(
        self,
        folderid: int,
        offset: int = 0,
        limit: int = -1,
        orderby: str = 'desc',
        ordertype: str = 'lastModified'
    ) -> Response:
        """
        The value of limit parameter behaves as following
        - limit = 100 is the default value
        - if limit > 0 then (number of return data = limit)
        - if limit = -1 then return all data
        - if limit < -1 then default value of the limit will be returned

        The value of offset parameter behaves as under
        - default value of offset is 0
        - if offset > 0 the starting point will be the offset value.
        - if offset < 0 then the default value of 0 will be used by the system

        orderby: "asc" or "desc". Defaults to "desc"; the latest items are returned first.

        ordertype: can be one of name, size, author, lastModified, filetype
        """
        parameters: Dict[str, Union[int, str]] = {
            'q': f'"folderid={folderid}"',
            'offset': offset,
            'limit': limit,
            'orderby': orderby,
            'ordertype': ordertype
        }

        return self.get(endpoint=f'3/files', parameters=parameters)

    def fetch_item_ids_in_files_column(
        self,
        isheetid: int,
        files_columnid: int,
    ) -> Generator[Dict[str, int], None, None]:
        """
        """
        try:
            r_isheet_items: Response = self.get_isheet_items(isheetid=isheetid)
            r_isheet_items.raise_for_status()
            if r_isheet_items.ok:
                try:
                    isheet_items: Union[dict, List[dict]] = \
                        r_isheet_items.json()['isheet']['data']['item']
                    if isinstance(isheet_items, dict):
                        isheet_items: List[dict] = [isheet_items]
                    for item in isheet_items:
                        for column in item['column']:
                            if column['attributecolumnid'] == str(files_columnid):
                                try:
                                    highq_file_id: Optional[str] = \
                                        column['rawdata']['documents']['document']['docid']
                                    if highq_file_id is not None:
                                        yield {
                                            'highq_file_id':
                                                int(highq_file_id),
                                            'highq_isheet_item_id':
                                                int(item['itemid']),
                                        }
                                    else:
                                        continue
                                except KeyError:
                                    continue
                except KeyError:
                    return None
        except HTTPError:
            return None

    def fetch_isheet_column_dateformat(
        self,
        isheetid: int,
        attributecolumnid: int,
    ) -> Optional[str]:
        """
        Gets the dateformat of a given HighQ iSheet column and returns its
            corresponding strftime formatting string.

        Args:
            isheetid (int): The ID number of a HighQ iSheet.
            attributecolumnid (int): The ID number of an iSheet column.

        Returns:
            (str): the strftime formatting string
                for the HighQ column dateformat

        HighQ encodes dates in one of four formats:
            - DD MMM YYYY HH:MM
            - DD/MM/YYYY HH:MM
            - MM/DD/YYYY HH:MM
            - DD.MM.YYYY HH:MM
        HighQ expects dates to be in the column's specified date format,
            which can change at any time.
        """
        highq_to_strftime_format_map: Dict[str, str] = {
            'DD MMM YYYY': '%d %b %Y',
            'DD/MM/YYYY': '%d/%m/%Y',
            'MM/DD/YYYY': '%m/%d/%Y',
            'DD.MM.YYYY': '%d.%m.%Y',
        }

        try:
            r_isheet_columns_admin: Response = \
                self.get_isheet_columns_admin(isheetid=isheetid)
            r_isheet_columns_admin.raise_for_status()
            if r_isheet_columns_admin.ok:
                for column in r_isheet_columns_admin.json()['column']:
                    if column['columnid'] == attributecolumnid:
                        cdata: Optional[str] = \
                            column['columnspecificdetail']['dateformat']
                        if cdata is not None:
                            dateformat: str = cdata\
                                .split('<![CDATA[')[1]\
                                .split(']]>')[0]
                            return highq_to_strftime_format_map.get(dateformat)
        except HTTPError:
            return None

    def fetch_isheet_column_decimal_places(
        self,
        isheetid: int,
        attributecolumnid: int,
    ) -> Optional[int]:
        """
        Gets the decimalplaces property of a given HighQ iSheet column, if the
            column is of type `Number`.

        Args:
            isheetid (int): The ID number of a HighQ iSheet.
            attributecolumnid (int): The ID number of an iSheet column.

        Returns:
            (int): The decimal places of a given HighQ iSheet column.
        """
        try:
            r_isheet_columns_admin: Response = \
                self.get_isheet_columns_admin(isheetid=isheetid)
            r_isheet_columns_admin.raise_for_status()
            if r_isheet_columns_admin.ok:
                for column in r_isheet_columns_admin.json()['column']:
                    if column['columnid'] == attributecolumnid:
                        return column['columnspecificdetail']['decimalplaces']
        except HTTPError:
            return None

    def fetch_column_ids_names_choices(
        self,
        isheetid: int
    ) -> Generator[Tuple[str, int, Optional[List[Tuple[str, int]]]], None, None]:
        """
        Gets a subset of iSheet Column Admin data. Specifically, a tuple of
            just the column name, column ID number, and an optional list of the
            column's choices is yielded. This information proves useful for
            reference when manually populating HighQ iSheet Column ID Mappings
            using the ContraxSuite admin user interface.

        Args:
            isheetid (int): The ID number of a HighQ iSheet.

        Returns:
             A generator of tuples.
        """
        try:
            r_isheet_columns_admin: Response = \
                self.get_isheet_columns_admin(isheetid=isheetid)
            r_isheet_columns_admin.raise_for_status()
            if r_isheet_columns_admin.ok:
                try:
                    for column in r_isheet_columns_admin.json()['column']:
                        column_name: str = column['name']
                        column_id: int = column['columnid']

                        choices: Optional[Dict[str, List[dict]]] = \
                            column['columnspecificdetail']['choices']

                        if choices is not None:
                            column_choices: List[Tuple[str, int]] = [
                                (
                                    choice['label']\
                                        .split('<![CDATA[')[1]\
                                        .split(']]>')[0],

                                    int(choice['id'])
                                )
                                for choice in choices['choice']
                            ]
                        else:
                            column_choices: None = None
                        yield column_name, column_id, column_choices
                except KeyError:
                    return None
        except HTTPError:
            return None


def format_token_fields(
    token: Union[OAuth2Token, Dict[str, Union[str, float]]],
) -> Dict[str, Union[str, datetime.datetime]]:
    """
    Args:
        token (Union[OAuth2Token, Dict[str, Union[str, float]]]):

    Returns:
        Dict[str, Union[str, datetime]]

    Example:
        {'access_token': 'Gu_kyPsCZK6nI3lKtjH_IGg7O9yewRz9',
         'refresh_token_expires_in': '31536000',
         'expires_in': '18000',
         'refresh_token': 'pOMHmOxzBwu1oQTZ3xmKGilXGUmiXQHZ',
         'token_type': 'bearer',
         'useremail': 'email@example.com',
         'expires_at': 1603256113.2630794}

    Note:
        The refresh token response does not contain "expires_at",
        ...hence the additional calculations performed before the return.
    """
    expires_at: float = token.get('expires_at')
    expires_in = token.get('expires_in')
    if expires_at is None:
        if expires_in is not None:
            expires_at: datetime.datetime = \
                timezone.now() + \
                datetime.timedelta(seconds=int(expires_in))
        else:
            # TODO: write an exception for this case
            raise Exception
    else:
        expires_at: datetime.datetime = \
            datetime.datetime.fromtimestamp(expires_at)

    return {
        'refresh_token': token.get('refresh_token'),
        'access_token': token.get('access_token'),
        'access_token_expiration': expires_at,
    }


def get_initial_access_code(
    highq_configuration: HighQConfiguration
) -> HttpResponseRedirect:
    """
    Returns a redirect to HighQ's token authorization page. HighQ requires
        user-agent interaction (user clicks "Allow" in a web browser) to
        initially authorize an API access token. Subsequent authorizations
        can use a refresh token.

    Args:
        highq_configuration (HighQConfiguration):

    Returns:
        redirect to authorization_url
    """
    _callback_url = highq_configuration.api_callback_url.replace(
        '{highq_configuration_id}',
        str(highq_configuration.id)
    )

    session = OAuth2Session(
        client_id=highq_configuration.api_client_id,
        redirect_uri=_callback_url,
    )

    authorization_url, state = session.authorization_url(
        url=highq_configuration.api_authorization_url
    )

    return redirect(to=authorization_url, permanent=False)


def highq_datetime_to_py_datetime(
    date_time: str
) -> datetime.datetime:
    """
    """
    return datetime.datetime\
        .strptime(date_time, '%d %b %Y %H:%M')\
        .replace(tzinfo=datetime.timezone.utc)
