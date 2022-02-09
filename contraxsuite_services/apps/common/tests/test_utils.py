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
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from tests.django_test_case import *
import json
import pandas as pd
from typing import List

from django.test import TestCase

from apps.common.utils import download_xls, download_csv, download_pdf, format_number, Serializable
from apps.common.topological_sort import topological_sort


class AnimalViper(Serializable):
    def __init__(self, title: str = '', length: float = 0, sounds: List = None):
        super().__init__()
        self.title = title
        self.length = length
        self.sounds = sounds


class TestUils(TestCase):
    @classmethod
    def build_test_df(cls) -> pd.DataFrame:
        df = pd.DataFrame(columns=['Path', 'Name', 'Log SQL'])
        for i in range(10):
            df = df.append({
                "Path": f'file_{i}.txt',
                "Name": f'{i}_{i}',
                "Log SQL": i % 2 == 0
            }, ignore_index=True)
        return df

    def test_download_xls(self):
        df = self.build_test_df()
        resp = download_xls(df)
        self.assertIsNotNone(resp)
        self.assertGreater(len(resp.content), 200)

    def test_download_csv(self):
        df = self.build_test_df()
        resp = download_csv(df)
        self.assertIsNotNone(resp)
        self.assertGreater(len(resp.content), 200)
        data_str = resp.content.decode(resp.charset)
        self.assertTrue('file_0.txt,0_0,True' in data_str)

    def test_download_pdf(self):
        df = self.build_test_df()
        resp = download_pdf(df)
        self.assertGreater(len(resp.content), 200)

    def test_format_number(self):
        self.assertEqual('1,000', format_number(1000))
        # TODO: is this an expected behavior?
        self.assertEqual('1,000.0', format_number(float(1000)))
        self.assertEqual('-100,000.0', format_number(-1E5))

    def test_serializable(self):
        orig = AnimalViper('Vipera Berus', 0.85, ['shhh', 'psss'])
        dmp = json.dumps(orig)
        self.assertGreater(len(dmp), 10)
        counterpart = json.loads(dmp)
        self.assertIsNotNone(counterpart)
        self.assertEqual(orig.title, counterpart['title'])
        self.assertEqual(orig.length, counterpart['length'])
        self.assertEqual(orig.sounds, counterpart['sounds'])

    def test_topological_sort(self):
        field_deps = [('6', ['2', '3', '5'],),
                      ('2', ['1'],),
                      ('5', ['2', '1'],),
                      ('3', ['1'])]
        sorted_field_ids = list(topological_sort(field_deps))
        self.assertEqual(len(field_deps), len(sorted_field_ids))
        self.assertEqual('6235', ''.join([str(k[0]) for k in sorted_field_ids]))
