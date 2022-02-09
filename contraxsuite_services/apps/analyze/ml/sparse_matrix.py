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

from typing import Optional, List

import scipy.sparse as scp
import pandas as pd
import numpy as np
from pandas._libs.sparse import IntIndex
from pandas.core.arrays import SparseArray
from pandas.core.arrays.sparse import SparseFrameAccessor

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class SparseSingleFeatureTable:
    def __init__(self, feature_name: str):
        self.feature_name = feature_name
        self.matrix: Optional[scp.csr_matrix] = None

    def join(self, m: scp.csr_matrix):
        if self.matrix is None:
            self.matrix = m
        else:
            new_matrix = scp.vstack((self.matrix, m))
            del self.matrix
            del m
            self.matrix = new_matrix


class SparseAllFeaturesTable:
    def __init__(self, samples: List[int]):
        self.samples = samples  # document ids or text unit ids
        self.matrix: Optional[scp.csr_matrix] = None
        self.feature_names: List[str] = []

    def add_feature_table(self,
                          ft: SparseSingleFeatureTable,
                          feature_names: List[str]):
        if self.matrix is None:
            self.matrix = ft.matrix
        else:
            new_matrix = scp.hstack((self.matrix, ft.matrix))
            del self.matrix
            del ft.matrix
            self.matrix = new_matrix
        new_feature_names = [f'{ft.feature_name}({n})' for n in feature_names]
        self.feature_names += new_feature_names

    def to_dataframe(self, samples: Optional[List[int]] = None) -> pd.DataFrame:
        # we can't call
        #    pd.DataFrame.sparse.from_spmatrix(self.matrix, self.samples)
        # because it will replace all NaNs with 0s
        df = self.csr_to_df(self.matrix, samples or self.samples)
        df.columns = self.feature_names
        return df

    @classmethod
    def csr_to_df(cls, data, index=None, columns=None):
        data = data.tocsc()
        index, columns = SparseFrameAccessor._prep_index(data, index, columns)
        n_rows, n_columns = data.shape
        data.sort_indices()
        indices = data.indices
        indptr = data.indptr
        array_data = data.data
        dtype = pd.SparseDtype(array_data.dtype, np.nan)
        arrays = []
        for i in range(n_columns):
            sl = slice(indptr[i], indptr[i + 1])
            idx = IntIndex(n_rows, indices[sl], check_integrity=False)
            arr = SparseArray._simple_new(array_data[sl], idx, dtype)
            arrays.append(arr)
        return pd.DataFrame._from_arrays(
            arrays, columns=columns, index=index, verify_integrity=False)
