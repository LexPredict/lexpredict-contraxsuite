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

from typing import List, Dict, Any, Optional

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class URLParamFormatException(Exception):
    pass


def as_bool(url_params: Dict[str, Any], name: str, default_value: Optional[bool] = None) -> Optional[bool]:
    url_param = url_params.get(name)
    if url_param is None:
        return default_value
    url_param = url_param.strip().lower()
    if url_param == 'true':
        return True
    elif default_value is False or url_param == 'false':
        return False
    raise URLParamFormatException('Unable to parse URL parameter {0}'
                                  '\nExpected: true or false'
                                  '\nGot: {1}'.format(name, url_param))


def as_int(url_params: Dict[str, Any], name: str, default_value: Optional[int] = None) -> Optional[int]:
    url_param = url_params.get(name)
    if url_param is None:
        return default_value

    try:
        return int(url_param)
    except ValueError:
        raise URLParamFormatException('Unable to parse URL parameter {0}'
                                      '\nExpected: integer number (e.g.: 42)'
                                      '\nGot: {1}'.format(name, url_param))


def as_int_list(url_params: Dict[str, Any], name: str, default_value: Optional[List[int]] = None) \
        -> Optional[List[int]]:
    url_param = url_params.get(name)
    if url_param is None:
        return default_value
    try:
        return [int(s.strip()) for s in url_param.split(',')]
    except:
        raise URLParamFormatException('Unable to parse URL parameter {0}'
                                      '\nExpected: comma-separated list of integer numbers (e.g.: 1,2,3)'
                                      '\nGot: {1}'.format(name, url_param))


def as_str_list(url_params: Dict[str, Any], name: str, default_value: Optional[List[str]] = None) \
        -> Optional[List[str]]:
    url_param = url_params.get(name)
    if url_param is None:
        return default_value
    try:
        return [str(s.strip()) for s in url_param.split(',')]
    except:
        raise URLParamFormatException('Unable to parse URL parameter {0}'
                                      '\nExpected: comma-separated list of strings (e.g.: aaa,bbb,ccc)'
                                      '\nGot: {1}'.format(name, url_param))
