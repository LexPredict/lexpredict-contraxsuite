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

from tests.django_test_case import *
from apps.similarity.tasks import DocumentSimilarityByFeatures
from unittest import TestCase

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestSimilarityProcessor(TestCase):
    def test_count_estimation(self):
        c1 = DocumentSimilarityByFeatures.estimate_similarity_records_count(10000, 75)
        self.assertGreater(c1, 100000)
        self.assertLess(c1, 1000000)

        c2 = DocumentSimilarityByFeatures.estimate_similarity_records_count(10000, 90)
        self.assertGreater(c2, 10000)
        self.assertLess(c2, 200000)
        self.assertLess(c2, c1)

        c3 = DocumentSimilarityByFeatures.estimate_similarity_records_count(50000, 75)
        self.assertGreater(c3, 1000000)
        self.assertLess(c3, 6000000)
        self.assertLess(c2, c3)

        c180 = DocumentSimilarityByFeatures.estimate_similarity_records_count(180, 75)
        self.assertGreater(c180, 10000)
        self.assertLess(c180, 40000)
