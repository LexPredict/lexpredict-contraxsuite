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
from decimal import Decimal
from unittest import TestCase

from apps.common.model_utils.improved_django_json_encoder import ImprovedDjangoJSONEncoder

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestImprovedDjangoJSONEncoder(TestCase):
    class TestSrClass:
        def __init__(self, a: int, b: str, c=None):
            self.a = a
            self.b = b
            self.c = c

    def test_int(self):
        enc = ImprovedDjangoJSONEncoder()
        i = 12345
        s = enc.encode(i)
        self.assertEqual(s, '12345')

    def test_float(self):
        enc = ImprovedDjangoJSONEncoder()
        i = -123.45
        s = enc.encode(i)
        self.assertEqual(s, '-123.45')

    def test_long_float(self):
        enc = ImprovedDjangoJSONEncoder()
        f = 3.99999999999999999999999999999999999999999999999999999999999999999999999999999999
        self.assertEqual(f, 4)
        s = enc.encode(f)
        self.assertEqual(s, '4.0')

    def test_decimal(self):
        enc = ImprovedDjangoJSONEncoder()
        i_str = '3.99999999999999999999999999999999999999999999999999999999999999999999999999999999'
        d = Decimal(i_str)
        self.assertEqual(i_str, str(d))
        s = enc.encode(d)
        self.assertEqual(s, '"' + i_str + '"')

    def test_decimal_in_struct(self):
        enc = ImprovedDjangoJSONEncoder(indent=2)
        i_str = '3.99999999999999999999999999999999999999999999999999999999999999'
        d = Decimal(i_str)
        dd = {
            'a': 'b',
            'f': 0.1 + 0.2,
            'd': [d, d + 1, d + 2, d + (4 - d)]
        }

        expected = '''{
  "a": "b",
  "f": 0.30000000000000004,
  "d": [
    "3.99999999999999999999999999999999999999999999999999999999999999",
    "5.000000000000000000000000000",
    "6.000000000000000000000000000",
    "4.000000000000000000000000000"
  ]
}'''
        actual = enc.encode(dd)
        self.assertEqual(expected, actual)

    def test_date(self):
        d = datetime.datetime(2019, 9, 18, 21, 30, 7, 303)
        enc = ImprovedDjangoJSONEncoder()
        s = enc.encode(d)
        self.assertEqual(s, '"2019-09-18T21:30:07.000"')

        d = datetime.date(2019, 9, 18)
        s = enc.encode(d)
        self.assertEqual(s, '"2019-09-18"')

    def test_set(self):
        d = {'alpha', 'bravo', '', 'delta'}
        enc = ImprovedDjangoJSONEncoder()
        s = enc.encode(d)
        self.assertTrue(s.startswith('[') and s.endswith(']') and all(i in s for i in d))

    def test_class(self):
        d = self.TestSrClass(10, 'miles', c=self.TestSrClass(a=1, b='2', c={'35': 35}))
        enc = ImprovedDjangoJSONEncoder()
        s = enc.encode(d)
        # should be something like: {"a": 10, "b": "miles", "c": {"a": 1, "b": "2", "c": {"35": 35}}}
        self.assertTrue(s.startswith('{')
                        and s.endswith('}')
                        and '"a": 10' in s
                        and '"b": "miles"' in s
                        and '{"35": 35}' in s)
