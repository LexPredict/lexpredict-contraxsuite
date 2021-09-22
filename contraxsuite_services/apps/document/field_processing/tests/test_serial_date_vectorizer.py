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
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase
import datetime

from apps.document.field_processing.vectorizers import SerialDateVectorizer


class TestSerialDateVectorizer(TestCase):
    def test_feature_names(self):
        names = SerialDateVectorizer.FEATURE_NAMES
        self.assertTrue('year_norm_1970_2050' in names)
        self.assertTrue('month_norm_1_12' in names)

    def test_dates(self):
        vectors = SerialDateVectorizer().transform(
            [datetime.date(2020, 7, 14)])
        self.assertEqual(1, len(vectors))
        # year
        year_nrm = (2020 - SerialDateVectorizer.MIN_YEAR) / \
                   (SerialDateVectorizer.MAX_YEAR - SerialDateVectorizer.MIN_YEAR)
        self.assertEqual(year_nrm, vectors[0][0])
        # month
        self.assertEqual(0.5, vectors[0][1])
        # day
        self.assertEqual((14 - 1) / 31, vectors[0][2])
        # day of week
        self.assertEqual(1 / 7, vectors[0][3])
