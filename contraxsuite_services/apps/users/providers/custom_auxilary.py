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
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import json
from typing import Dict, Any
import regex as re

from allauth.account.signals import user_logged_in
from django.core import serializers as core_serializers

from apps.common.logger import CsLogger

logger = CsLogger.get_django_logger()


def process_logged_in(sender, **kwargs):
    request = kwargs['request']
    if 'next' in request.session:
        if not request.GET._mutable:
            request.GET._mutable = True
        request.GET['next'] = request.session['next']

    if kwargs['user']:
        from apps.users.authentication import token_cache
        _, __, token = token_cache.get_token_keys(user=kwargs['user'])
        request.COOKIES['auth_token'] = f'Token {token}'


def route_next_param_to_query():
    # Connect django-allauth Signals
    try:
        user_logged_in.connect(process_logged_in)
    except Exception as e:
        logger.error(f'Error in route_next_param_to_query(): {e}')
        raise


def derive_user_name(user_data: Dict[str, Any]):
    if user_data.get('name'):
        return
    if 'first_name' in user_data or 'last_name' in user_data:
        name_parts = [p for p in [user_data.get('first_name') or '',
                                  user_data.get('last_name') or ''] if p]
        user_data['name'] = ' '.join(name_parts)


def format_data_message(msg: str, data_obj: Any) -> str:
    # try serializing data_obj
    data_str = ''
    if data_obj:
        try:
            data_str = json.dumps(data_obj)
        except:
            pass
        if not data_str:
            try:
                data_str = core_serializers.serialize('json', [data_obj])
            except:
                data_str = str(data_obj)
        msg = f'{msg}. Data:\n{data_str}'
    return msg


def log_error(msg: str):
    logger.error(msg)


def log_info(msg: str):
    logger.info(msg)


RE_CHECK_EMAIL = re.compile(r'''(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*''' +
                            r'''|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\''' +
                            r'''[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*''' +
                            r'''[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]''' +
                            r'''|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])''' +
                            r'''|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e''' +
                            r'''-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])''', re.IGNORECASE)


def is_email_addr_format(email: str) -> bool:
    if not email:
        return False
    return RE_CHECK_EMAIL.match(email) is not None
