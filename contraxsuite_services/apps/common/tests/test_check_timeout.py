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

import threading
import time
from typing import List
from django.test import TestCase
from apps.common.time_limit import time_limit

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


log_records = []  # type: List[str]


class TestCheckTimeout(TestCase):

    def test_simple_check(self):
        log_records.clear()
        sample_func(0.2)
        self.assertEqual(0, len(log_records))

        sample_func(1.5)
        self.assertEqual(1, len(log_records))

    def test_two_calls_one_thread(self):
        log_records.clear()
        sample_func(1.5)
        b = long_sample_func(1.5)
        self.assertTrue(b)

        self.assertEqual(1, len(log_records))
        self.assertEqual("1 seconds timeout in sample_func() call",
                         log_records[0])

    def failed_test_two_calls_two_threads(self):
        log_records.clear()
        jobs = [threading.Thread(target=lambda: long_sample_func(1.2)),
                threading.Thread(target=lambda: sample_func(1.2))]
        for j in jobs:
            j.start()
        for j in jobs:
            j.join()

        self.assertEqual(1, len(log_records))
        self.assertEqual("1 seconds timeout in sample_func() call",
                         log_records[0])


def sample_func(delay: float) -> bool:
    with time_limit(1, on_timeout=lambda n: log_records.append(f"{n} seconds timeout in sample_func() call")):
        time.sleep(delay)
        return True


def long_sample_func(delay: float) -> bool:
    with time_limit(2, on_timeout=lambda n: log_records.append(f"{n} seconds timeout in long_sample_func() call")):
        time.sleep(delay)
        return True
