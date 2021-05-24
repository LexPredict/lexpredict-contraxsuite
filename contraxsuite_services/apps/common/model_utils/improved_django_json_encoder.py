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
import json
import pytz
import uuid
from collections import Collection, Mapping

from django.utils.duration import duration_iso_string
from django.utils.functional import Promise

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class ImprovedDjangoJSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        if isinstance(o, datetime.date):
            return o.isoformat()
        if isinstance(o, datetime.time):
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        if isinstance(o, datetime.timedelta):
            return duration_iso_string(o)
        if isinstance(o, (pytz.tzinfo.tzinfo, uuid.UUID, Promise, decimal.Decimal)):
            return str(o)
        if isinstance(o, dict):
            return o
        if isinstance(o, Mapping):
            return dict(o)
        if isinstance(o, Collection) and not isinstance(o, str):
            return list(o)
        # note that isinstance(True, int) == isinstance(False, int) == True as True and False are treated as 1 and 0
        if isinstance(o, (str, float, bool)) or type(o) is int:
            return o
        if hasattr(o, '__dict__'):
            return {k: self.default(v) for k, v in o.__dict__.items()}
        return super().default(o)
