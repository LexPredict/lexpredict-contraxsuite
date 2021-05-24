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

from unittest import TestCase
from apps.document.field_processing.field_processing_utils import \
    order_field_detection, get_dependent_fields

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestFieldsProcessingUtils(TestCase):
    def test_order_field_detection(self) -> None:
        fields = [('a', set()), ('b', set('a')), ('c', set('d')), ('d', set('b')), ('e', set())]
        ordered = order_field_detection(fields)
        ordered_pos = {ordered[i]: i for i in range(len(ordered))}
        self.assertEqual(len(fields), len(ordered))
        self.assertGreater(ordered_pos['b'], ordered_pos['a'])
        self.assertGreater(ordered_pos['c'], ordered_pos['d'])
        self.assertGreater(ordered_pos['d'], ordered_pos['b'])

    def test_required_fields(self) -> None:
        fields = [('a', set()), ('b', set('a')), ('c', set('d')), ('d', set('b')), ('e', set())]
        deps = get_dependent_fields(fields, {'b'})
        self.assertEqual(2, len(deps))
        self.assertIn('d', deps)
        self.assertIn('c', deps)

        deps = get_dependent_fields(fields, {'a'})
        self.assertEqual(3, len(deps))
        self.assertTrue('a' not in deps)

        deps = get_dependent_fields(fields, {'c'})
        self.assertEqual(0, len(deps))

    def test_order_field_detection_empty(self) -> None:
        ordered = order_field_detection([])
        self.assertEqual(0, len(ordered))
