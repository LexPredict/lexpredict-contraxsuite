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
import decimal
from typing import Any, Collection, Mapping

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from apps.common.model_utils.improved_django_json_encoder import ImprovedDjangoJSONEncoder

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


@dataclass_json
@dataclass
class ChannelMessage:
    """
    Message as it is delivered to client through WebSocket, used in ChannelBroadcasting
    """

    message_type: str
    payload: Any  # dataclass or a JSON serializable value


def serialize(obj):
    if isinstance(obj, Mapping):
        for k, v in obj.items():
            obj[k] = serialize(v)
    elif isinstance(obj, Collection) and not isinstance(obj, str):
        for i in obj:
            i = serialize(i)
    elif isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
        obj = ImprovedDjangoJSONEncoder().default(obj)
    elif isinstance(obj, decimal.Decimal):
        obj = float(obj)    # ImprovedDjangoJSONEncoder().default(obj)
    return obj


def to_dict():
    def wrapper(func):
        def decorator(self):
            self.payload = serialize(self.payload)
            return func(self)
        return decorator
    return wrapper


ChannelMessage.to_dict = to_dict()(ChannelMessage.to_dict)
