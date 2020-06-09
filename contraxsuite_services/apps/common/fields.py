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

# Standard imports
import json

# Django imports
from django.db.models import UUIDField, DecimalField, CharField
from django.contrib.postgres.fields import JSONField

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class StringUUIDField(UUIDField):
    def from_db_value(self, value, *args, **kwargs):
        return str(value) if value else None


class CustomJSONField(JSONField):
    def from_db_value(self, value, *args, **kwargs):
        try:
            return json.loads(value)
        except:
            return value


class RoundedFloatField(DecimalField):
    def __init__(self, verbose_name=None, name=None, max_digits=15, decimal_places=3, **kwargs):
        super().__init__(verbose_name, name, max_digits, decimal_places, **kwargs)

    def from_db_value(self, value, *args, **kwargs):
        return None if value is None else float(value)


class TruncatingCharField(CharField):
    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value:
            if len(value) > self.max_length:
                return value[:self.max_length - 2] + '..'
        return value
