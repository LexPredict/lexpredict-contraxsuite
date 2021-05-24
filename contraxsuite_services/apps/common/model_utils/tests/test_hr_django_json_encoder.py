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

from apps.common.model_utils.hr_django_json_encoder import HRDjangoJSONEncoder
from tests.django_test_case import DjangoTestCase

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestHRDjangoJSONEncoder(DjangoTestCase):
    class TestSrClass:
        def __init__(self, a: int, b: str):
            self.a = a
            self.b = b

    def test_date(self):
        d = datetime.datetime(2019, 9, 18, 21, 30, 7, 303)
        enc = HRDjangoJSONEncoder()
        s = enc.encode(d)
        self.assertGreater(len(s), 10)

        d = datetime.date(2019, 9, 18)
        s = enc.encode(d)
        self.assertGreater(len(s), 5)

    def test_set(self):
        d = {'alpha', 'bravo', '', 'delta'}
        enc = HRDjangoJSONEncoder()
        s = enc.encode(d)
        self.assertGreater(len(s), 10)

    def test_long_text(self):
        d = {'text': 'Blah' * 100}
        enc = HRDjangoJSONEncoder()
        s = enc.encode(d)
        self.assertLess(len(s), 260)

    def test_class(self):
        d = self.TestSrClass(10, 'miles')
        enc = HRDjangoJSONEncoder()
        s = enc.encode(d)
        self.assertGreater(len(s), 4)
