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

import sys
from datetime import datetime, date
from typing import List, Union, Callable, Dict, Set

from sklearn.feature_extraction.text import strip_accents_unicode

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class VectorizerStep:
    def fit(self, field_values_or_anything: List, *args, **kwargs):
        return self

    def fit_transform(self, field_values_or_anything: List, *args, **kwargs):
        self.fit(field_values_or_anything)
        return self.transform(field_values_or_anything)

    def transform(self, field_values_or_anything: List, *args, **kwargs):
        pass

    def get_feature_names(self) -> List[str]:
        pass


class TupleItemSelector(VectorizerStep):
    def __init__(self, item_index: int) -> None:
        super().__init__()
        self.item_index = item_index

    def transform(self, tuples: List, *args, **kwargs):
        return [tpl[self.item_index] for tpl in tuples]

    def get_feature_names(self) -> List[str]:
        return ['']


def whole_value_as_token(value: str) -> List[str]:
    return [str(value)]


def set_items_as_tokens(value: Union[str, Set, List]) -> List[str]:
    return [str(i) for i in sorted(value)] if isinstance(value, (set, list)) else [str(value)]


def set_items_as_tokens_preprocessor(value: Union[str, Set, List]):
    return [strip_accents_unicode(str(i).lower()) for i in value] \
        if isinstance(value, (set, list)) \
        else [strip_accents_unicode(str(value).lower())]


class ReplaceNoneTransformer(VectorizerStep):
    def __init__(self, default_value) -> None:
        super().__init__()
        self.default_value = default_value

    def transform(self, field_values_or_anything: List, *args, **kwargs):
        return [v or self.default_value for v in field_values_or_anything]

    def get_feature_names(self) -> List[str]:
        return ['']


class DictItemSelector(VectorizerStep):
    def __init__(self, item: str, processor: Callable = None) -> None:
        super().__init__()
        self.item = item
        self.processor = processor if processor else lambda x: x

    def transform(self, field_values_or_anything: List[Dict], *args, **kwargs):
        return [self.processor(d.get(self.item) if d else None) for d in field_values_or_anything]

    def get_feature_names(self) -> List[str]:
        return [self.item]


class RecurringDateVectorizer(VectorizerStep):
    MAX_YEAR = 2050
    MIN_YEAR = 1970
    FEATURE_NAMES = ['year_' + str(year) for year in range(MAX_YEAR - MIN_YEAR)] \
                    + ['month_' + str(month + 1) for month in range(12)] \
                    + ['day_' + str(i + 1) for i in range(31)] \
                    + ['dow_' + str(i) for i in range(7)]

    def transform(self, field_values: List[Union[datetime, date]], *args, **kwargs):
        # TODO Optimize list manipulations

        res = []
        for d in field_values:
            vect = []

            year = d.year if d else 1  # 1 - 9999
            year = 0 if year < self.MIN_YEAR else self.MAX_YEAR if year > self.MAX_YEAR else year
            year = year - self.MIN_YEAR
            year_vect = [int(i == year) for i in range(self.MAX_YEAR - self.MIN_YEAR)]
            vect += year_vect

            month = d.month - 1 if d else 0  # 0 - 11
            month_vect = [int(month == i) for i in range(12)]
            vect += month_vect

            day = d.day - 1 if d else 0  # 0 - 30
            day_vect = [int(day == i) for i in range(31)]
            vect += day_vect

            day_of_week = d.weekday() if d else 0  # M0 - S6
            dow_vect = [int(day_of_week == i) for i in range(7)]
            vect += dow_vect

            res.append(vect)
        return res

    def get_feature_names(self) -> List[str]:
        return self.FEATURE_NAMES


class SerialDateVectorizer(VectorizerStep):
    MAX_YEAR = 2050
    MIN_YEAR = 1970
    FEATURE_NAMES = ['year_norm_' + str(MIN_YEAR) + '_' + str(MAX_YEAR),
                     'month_norm_1_12',
                     'day_norm_1_31',
                     'dow_norm_1_7']

    def get_feature_names(self) -> List[str]:
        return self.FEATURE_NAMES

    def transform(self, field_values: List[Union[datetime, date]], *args, **kwargs):
        # TODO Optimize list manipulations

        res = []
        for d in field_values:
            vect = []

            year = d.year if d else 1  # 0 ... 1
            year = 0 if year < self.MIN_YEAR else self.MAX_YEAR if year > self.MAX_YEAR else year
            year = year - self.MIN_YEAR
            vect.append(year / (self.MAX_YEAR - self.MIN_YEAR))

            month = d.month - 1 if d else 0  # 0 .. 1
            vect.append(month / 12)

            day = d.day - 1 if d else 0  # 0 .. 1
            vect.append(day / 31)

            day_of_week = d.weekday() if d else 0  # M0 - S6
            vect.append(day_of_week / 7)

            res.append(vect)
        return res


class NumberVectorizer(VectorizerStep):
    def __init__(self, to_float_converter: Callable = None) -> None:
        super().__init__()
        self.to_float_converter = to_float_converter if to_float_converter else \
            lambda n: float(n) if n is not None else 0
        self.min_value = sys.float_info.min
        self.max_value = sys.float_info.max

    def fit(self, field_values_or_anything: List, *args, **kwargs):
        min_value = sys.float_info.min
        max_value = sys.float_info.max

        for n in field_values_or_anything:
            n = self.to_float_converter(n)
            if n < min_value:
                min_value = n
            if n > max_value:
                max_value = n

        self.min_value = min_value
        self.max_value = max_value
        return self

    def fit_transform(self, field_values_or_anything: List, *args, **kwargs):
        self.fit(field_values_or_anything)
        return self.transform(field_values_or_anything)

    def transform(self, field_values_or_anything: List, *args, **kwargs):
        res = []
        for n in field_values_or_anything:
            n = self.to_float_converter(n) if self.to_float_converter else float(n)
            n = (n - self.min_value) / (self.max_value - self.min_value)
            res.append([n])
        return res

    def get_feature_names(self) -> List[str]:
        return ['num_norm_' + str(self.min_value) + '_' + str(self.max_value)]
