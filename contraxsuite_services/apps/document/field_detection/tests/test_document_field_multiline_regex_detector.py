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
from typing import Tuple, List
from io import StringIO
import pandas as pd
from apps.document.models import DocumentFieldMultilineRegexDetector

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestDocumentFieldMultilineRegexDetector(TestCase):
    csv_text = """
,value,pattern
0,"Big Bank & Company (004578) (Knight, Bobby (Charlotte); Bryant, Koby (Charlotte); Williams, Gary (Charlotte); Johnson, Magic (Charlotte); Lobo, Rebecca (Charlotte))","\bbig\s{1,5}bank\s{1,5}.{1,5}\s{1,5}company\s{1,5}(004578)\b"
1,"Family Name Limited (173437) (Tanner, Rebecca (Houston); Saget, Bob (Houston))","\bfamily\s{1,5}name(173437)\b"
2,"Financial Services & Co. (015607) (Spelling, Tori (Chicago); Priestley, Jason (Dallas); Perry, Luke (New York); Doherty, Shannon (Chicago); Garth, Jenny (Chicago))","\bfinancial\s{1,5}services\s{1,5}.{1,5}(015607)\b"
3,"Food Wholsale, Inc. (056230) (Jenner, Bruce (Chicago))","\bfood\s{1,5}wholsale,(056230)\b"
4,"All Eyes Communications (018951) (Moore, Michael (New York); Tarantino, Quentin (San Francisco); Lee, Spike (New York); Levinson, Barry (Charlotte))","\ball\s{1,5}eyes\s{1,5}communications\s{1,5}(018951)\b"
5,"Joe Smith Archives, LLC d/b/a Foxtrot (085292) (Flay, Bobby (New York))","\bfoxtrot\s{1,5}(085292)\b
\bjoe\s{1,5}smith\s{1,5}archives\b"
            """

    def test_checksum(self):
        detector = DocumentFieldMultilineRegexDetector()
        detector.csv_content = self.csv_text
        detector.update_checksum()
        self.assertGreater(len(detector.csv_checksum), 10)

        cs_old = detector.csv_checksum
        detector.csv_content = detector.csv_content[:-1] + ';'
        detector.update_checksum()
        self.assertGreater(len(detector.csv_checksum), 10)
        self.assertNotEqual(cs_old, detector.csv_checksum)

    def test_get_as_pd(self):
        detector = DocumentFieldMultilineRegexDetector()
        detector.csv_content = self.csv_text
        df = detector.get_as_pandas_df()
        self.assertIsNotNone(df)
        self.assertEqual((6, 2,), df.shape)

    def test_combine_dfs(self):
        # first row is the same, second row - same value, another pattern
        # third row - same pattern, another value, last row - brand new
        another_text = """
,value,pattern
0,"Big Bank & Company (004578) (Knight, Bobby (Charlotte); Bryant, Koby (Charlotte); Williams, Gary (Charlotte); Johnson, Magic (Charlotte); Lobo, Rebecca (Charlotte))","\bbig\s{1,5}bank\s{1,5}.{1,5}\s{1,5}company\s{1,5}(004578)\b"
1,"Family Name Limited (173437) (Tanner, Rebecca (Houston); Saget, Bob (Houston))","\bfamily\s{1,5}guy(173437)\b"
2,"Eye-Eyes Communications (018951)","\ball\s{1,5}eyes\s{1,5}communications\s{1,5}(018951)\b"
3,"John Smith Archives, LLC d/b/a Charlie (085292) (Flay, Bobby (New York))","\bcharlie\s{1,5}(085292)\b"
            """
        with StringIO(another_text) as cs_stream:
            df = pd.read_csv(cs_stream, usecols=[1, 2])

        detector = DocumentFieldMultilineRegexDetector()
        detector.csv_content = self.csv_text
        detector.update_checksum()
        detector.combine_with_dataframe(df)

        df_new = detector.get_as_pandas_df()
        row_val = []  # type: List[Tuple[str, str]]
        for i, row in df_new.iterrows():
            row_val.append((row[0], row[1],))

        self.assertEqual(8, len(row_val))
        self.assertTrue(('John Smith Archives, LLC d/b/a Charlie (085292) (Flay, Bobby (New York))',
                         '\bcharlie\s{1,5}(085292)\b',) in row_val)
        self.assertTrue(('Big Bank & Company (004578) (Knight, Bobby (Charlotte); Bryant, Koby ' +
                         '(Charlotte); Williams, Gary (Charlotte); Johnson, Magic (Charlotte); ' +
                         'Lobo, Rebecca (Charlotte))',
                         '\bbig\s{1,5}bank\s{1,5}.{1,5}\s{1,5}company\s{1,5}(004578)\b',) in row_val)
        self.assertTrue(('Family Name Limited (173437) (Tanner, Rebecca (Houston); Saget, Bob (Houston))',
                         '\bfamily\s{1,5}guy(173437)\b',) in row_val)
        self.assertTrue(('Family Name Limited (173437) (Tanner, Rebecca (Houston); Saget, Bob (Houston))',
                         '\bfamily\s{1,5}name(173437)\b',) in row_val)
        self.assertTrue(('Eye-Eyes Communications (018951)',
                         '\ball\s{1,5}eyes\s{1,5}communications\s{1,5}(018951)\b',) in row_val)
        # this one is replaced
        self.assertFalse(('All Eyes Communications (018951) (Moore, Michael (New York); Tarantino, Quentin ' +
                         '(San Francisco); Lee, Spike (New York); Levinson, Barry (Charlotte))',
                         '\ball\s{1,5}eyes\s{1,5}communications\s{1,5}(018951)\b',) in row_val)
