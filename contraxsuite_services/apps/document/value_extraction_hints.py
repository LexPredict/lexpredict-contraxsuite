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

from enum import Enum, unique
from typing import Optional, List

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


EH_TAKE_MIN = 'TAKE_MIN'
EH_TAKE_MAX = 'TAKE_MAX'

ORDINAL_EXTRACTION_HINTS = [EH_TAKE_MIN, EH_TAKE_MAX]


@unique
class ValueExtractionHint(Enum):
    TAKE_FIRST = 'TAKE_FIRST'
    TAKE_SECOND = 'TAKE_SECOND'
    TAKE_LAST = 'TAKE_LAST'
    TAKE_MIN = EH_TAKE_MIN
    TAKE_MAX = EH_TAKE_MAX

    @staticmethod
    def _is_money(v) -> bool:
        return isinstance(v, dict) and 'amount' in v and 'currency' in v

    @staticmethod
    def _is_ratio(v) -> bool:
        return isinstance(v, dict) and 'numerator' in v and 'denominator' in v

    @staticmethod
    def get_value(l: Optional[List], hint: str):
        if not l:
            return
        if str(hint) == ValueExtractionHint.TAKE_LAST.name:
            return l[-1]
        if str(hint) == ValueExtractionHint.TAKE_SECOND.name and len(l) > 1:
            return l[1]
        if str(hint) == ValueExtractionHint.TAKE_FIRST.name and len(l) > 0:
            return l[0]
        # TODO: move if-else logic into TypedField methods as it depends on TypedField-dependent data structure
        if str(hint) == ValueExtractionHint.TAKE_MIN.name:
            if ValueExtractionHint._is_money(l[0]):
                return min(l, key=lambda dd: dd['amount'])
            elif ValueExtractionHint._is_ratio(l[0]):
                return min(l, key=lambda dd: dd['numerator'] / dd['denominator'])
            return min(l)
        if str(hint) == ValueExtractionHint.TAKE_MAX.name:
            if ValueExtractionHint._is_money(l[0]):
                return max(l, key=lambda dd: dd['amount'])
            elif ValueExtractionHint._is_ratio(l[0]):
                return max(l, key=lambda dd: dd['numerator'] / dd['denominator'])
            return max(l)
