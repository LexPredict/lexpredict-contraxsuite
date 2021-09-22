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
from django.test import TestCase

import random
import time
from collections import Iterable
from typing import List, Iterator, Generator

from apps.common.collection_utils import chunks, group_by, sequence_chunks
from apps.common.decorators import collect_stats
from apps.common.models import MethodStats

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class MyIterable(Iterable):

    def __init__(self, l: List) -> None:
        super().__init__()
        self.l = l
        self.iterator_used = False

    def __iter__(self) -> Iterator:
        self.iterator_used = True
        return self.l.__iter__()


class MySequence(MyIterable):

    def __init__(self, l: List) -> None:
        super().__init__(l)
        self.slicing_used = False

    def __getitem__(self, k):
        if isinstance(k, slice):
            self.slicing_used = True
        return self.l.__getitem__(k)


class CollectionUtilsTest(TestCase):

    def test_lists(self):
        col = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        actual = list(chunks(col, 4))
        expected = [[1, 2, 3, 4], [5, 6, 7, 8], [9]]
        self.assertEqual(expected, actual)

    def test_sets(self):
        col = {1, 2, 3, 4, 5, 6, 7, 8, 9}
        actual = list(chunks(col, 4))
        expected = [[1, 2, 3, 4], [5, 6, 7, 8], [9]]
        self.assertEqual(expected, actual)

    def test_generators(self):
        def gen() -> Generator[int, None, None]:
            for i in range(1, 10, 1):
                yield i

        actual = list(chunks(gen(), 4))
        expected = [[1, 2, 3, 4], [5, 6, 7, 8], [9]]
        self.assertEqual(expected, actual)

    def test_iterator_used(self):
        col = MyIterable([1, 2, 3, 4, 5, 6, 7, 8, 9])
        actual = list(chunks(col, 4))
        expected = [[1, 2, 3, 4], [5, 6, 7, 8], [9]]
        self.assertEqual(expected, actual)
        self.assertTrue(col.iterator_used)

    def test_slicing_used(self):
        col = MySequence([1, 2, 3, 4, 5, 6, 7, 8, 9])
        actual = list(chunks(col, 4))
        expected = [[1, 2, 3, 4], [5, 6, 7, 8], [9]]
        self.assertEqual(expected, actual)
        self.assertTrue(col.slicing_used)
        self.assertFalse(col.iterator_used)

    def non_test_collect_stat(self):
        # this code can't be run as a unit test because it requires DB connection
        for _ in range(1000):
            d = random.random()
            err = d < 0.1
            delay = d / 100
            make_lala(delay, err)

        records = list(MethodStats.objects.all())
        self.assertGreater(len(records), 999)

    def test_group_by(self):
        lst = [('a', 1), ('b', 2), ('a', 3), ('a', 4)]
        d = group_by(lst, lambda i: i[0])
        self.assertEqual(2, len(d))
        self.assertEqual(3, len(d['a']))
        self.assertEqual(1, len(d['b']))
        self.assertTrue('3' in ''.join([str(i[1]) for i in d['a']]))
        self.assertTrue('2' not in ''.join([str(i[1]) for i in d['a']]))

    def test_sequence_chunks(self):
        lst = list(range(95))
        uber_list = [c for c in sequence_chunks(lst, 10)]
        self.assertEqual(10, len(uber_list))
        self.assertEqual(10, len(uber_list[0]))
        self.assertEqual(5, len(uber_list[-1]))


@collect_stats(name='My Test for fn', comment='some long comment', log_sql=False)
def make_lala(delay: float, raiseerror: bool):
    time.sleep(delay)
    if raiseerror:
        raise Exception('Just error')
