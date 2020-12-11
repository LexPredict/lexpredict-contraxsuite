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
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import sys
from decimal import Decimal
from unittest import TestCase

from apps.document.field_processing.vectorizers import NumberVectorizer


class TestNumberVectorizer(TestCase):
    def test_convertible(self):
        vectors = NumberVectorizer().transform(
            ['3.14', 3.14, 3, Decimal(3.14), -3.14, -3.15,
             sys.float_info.min, sys.float_info.max])
        self.assertEqual(8, len(vectors))
        self.assertEqual(vectors[0][0], vectors[1][0])
        self.assertEqual(vectors[0][0], vectors[3][0])
        self.assertNotEqual(vectors[0][0], vectors[2][0])
        self.assertNotEqual(vectors[4][0], vectors[5][0])
        self.assertEqual(0.0, vectors[6][0])
        self.assertEqual(1.0, vectors[7][0])
