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
from typing import Dict
from unittest import TestCase
import scipy.sparse as scp
from pandas import CategoricalDtype
import pandas as pd
import numpy as np

from apps.analyze.ml.sparse_matrix import SparseSingleFeatureTable, SparseAllFeaturesTable

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestSparseMatrix(TestCase):
    terms = ['abatement', 'abuse', 'abyss', 'arbeit', 'bond', 'mutual bond', 'CFD', 'future']
    currencies = ['EUR', 'RUB', 'USD']
    sample_id_field = 'document_id'
    dates = [datetime.datetime(2020, 2, 4), datetime.datetime(2020, 2, 5),
             datetime.datetime(2020, 2, 6), datetime.datetime(2020, 2, 8)]

    all_doc_ids = [31, 32, 33, 34, 35, 38]

    feature_source = [
        {
            'feature_name': 'term',
            'feature_field': 'term__term',
            'sample_ids': [[31, 32], [33, 34, 35, 38]],
            'data': [
                [{'document_id': 31, 'term__term': 'abatement', 'counter': 1},
                 {'document_id': 31, 'term__term': 'abuse', 'counter': 2},
                 {'document_id': 32, 'term__term': 'abatement', 'counter': 12},
                 {'document_id': 32, 'term__term': 'abyss', 'counter': 1},
                 {'document_id': 32, 'term__term': 'arbeit', 'counter': 3}],
                [{'document_id': 33, 'term__term': 'mutual bond', 'counter': 2},
                 {'document_id': 33, 'term__term': 'CFD', 'counter': 5},
                 {'document_id': 34, 'term__term': 'abatement', 'counter': 2},
                 {'document_id': 34, 'term__term': 'CFD', 'counter': 4},
                 {'document_id': 34, 'term__term': 'future', 'counter': 4}]
            ],
            'feature_names': terms
        },
        {
            'feature_name': 'currency',
            'feature_field': 'currency',
            'sample_ids': [[31, 32], [33, 34, 35, 38]],
            'data': [
                [{'document_id': 31, 'currency': 'EUR', 'counter': 1},
                 {'document_id': 31, 'currency': 'USD', 'counter': 2},
                 {'document_id': 32, 'currency': 'EUR', 'counter': 6},
                 {'document_id': 32, 'currency': 'USD', 'counter': 1},
                 {'document_id': 32, 'currency': 'RUB', 'counter': 1}], []],
            'feature_names': currencies
        }
    ]

    date_features = [
        {
            'feature_name': 'date',
            'feature_field': 'date',
            'sample_ids': [[31, 32], [33, 34, 35, 38]],
            'data': [
                [{'document_id': 31, 'date': datetime.date(2020, 2, 4), 'counter': 1},
                 {'document_id': 31, 'date': datetime.date(2020, 2, 5), 'counter': 2},
                 {'document_id': 32, 'date': datetime.date(2020, 2, 6), 'counter': 6},
                 {'document_id': 32, 'date': datetime.date(2020, 2, 8), 'counter': 1},
                 {'document_id': 32, 'date': datetime.date(2020, 2, 4), 'counter': 1}], []],
            'feature_names': dates
        }
    ]

    def test_sum_dates(self):
        df_a = self.get_term_df(self.date_features[0])
        t = SparseAllFeaturesTable(self.all_doc_ids)
        t.add_feature_table(df_a, self.date_features[0]['feature_names'])
        df = t.to_dataframe()
        self.assertEqual((6, 4,), df.shape)

    def test_sum_up(self):
        df_a = self.get_term_df(self.feature_source[0])
        df_b = self.get_term_df(self.feature_source[1])
        t = SparseAllFeaturesTable(self.all_doc_ids)
        t.add_feature_table(df_a, self.feature_source[0]['feature_names'])
        t.add_feature_table(df_b, self.feature_source[1]['feature_names'])
        dm = t.matrix.todense()
        print(dm)
        self.assertEqual('1  2  0  0  0  0  0  0  1  0  2', '  '.join([str(i) for i in dm.tolist()[0]]))
        self.assertEqual('2  0  0  0  0  0  4  4  0  0  0', '  '.join([str(i) for i in dm.tolist()[3]]))
        # TODO: csr_matrix.hstack() requires both matrices be of the same height
        # we need somehow made them equal - thus we need always have the same amount of model references
        # (including empty ones) while stacking feature tables
        df = t.to_dataframe()
        print(df)
        shape = df.shape
        df.dropna(axis=1, how='all', inplace=True)
        self.assertLess(df.shape[1], shape[1])

    def get_term_df(self, data_dict: Dict):
        feature_table = SparseSingleFeatureTable(data_dict['feature_name'])

        for i in range(len(data_dict['data'])):
            frame = data_dict['data'][i]
            sample_ids = data_dict['sample_ids'][i]

            df = pd.DataFrame.from_records(frame)
            doc_cat = CategoricalDtype(sample_ids, ordered=True)
            term_cat = CategoricalDtype(data_dict['feature_names'], ordered=True)
            row = [] if df.empty else df[self.sample_id_field].astype(doc_cat).cat.codes
            col = [] if df.empty else df[data_dict['feature_field']].astype(term_cat).cat.codes
            counter = [] if df.empty else df['counter']
            sparse_matrix = scp.csr_matrix(
                (counter, (row, col)),
                shape=(len(sample_ids), term_cat.categories.size),
                dtype=np.uint16)
            feature_table.join(sparse_matrix)

        return feature_table
