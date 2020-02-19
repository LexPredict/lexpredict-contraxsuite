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

import re
from enum import Enum
from typing import List, Tuple, Dict, Optional

from apps.common.sql_commons import SQLClause
from apps.rawdb.rawdb.rawdb_field_handlers import ColumnDesc
from apps.rawdb.rawdb.errors import OrderByParsingError, FilterSyntaxError, UnknownColumnError, FilterValueParsingError

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class SortDirection(Enum):
    ASC = 'asc'
    DESC = 'desc'


_ORDER_BY_MATCH = re.compile(r'(?P<column>\w+)(?::(?P<direction>(?:asc|desc)))?(?:[,\n]|$)', re.MULTILINE)


def parse_order_by(order_by: str) -> Optional[List[Tuple[str, SortDirection]]]:
    if order_by:
        res = list()  # type: List[Tuple[str, SortDirection]]
        for m in _ORDER_BY_MATCH.finditer(order_by.lower()):
            column = m.group('column')
            direction = m.group('direction')
            direction = SortDirection[direction.upper()] if direction else SortDirection.ASC
            res.append((column, direction))
        if not res:
            raise OrderByParsingError('Unable to parse order_by: {0}.\n'
                                      'Syntax example:\n'
                                      'column1:asc,column2:desc,column3'.format(order_by))
        return res
    else:
        return None


def parse_column_filters(column_filters: List[Tuple[str, str]], column_name_to_desc: Dict[str, ColumnDesc],
                         ignore_errors: bool = False) \
        -> List[SQLClause]:
    res = list()  # type: List[SQLClause]
    if column_filters:
        for column_name, column_filter in column_filters:
            column_desc = column_name_to_desc.get(column_name)  # type: ColumnDesc
            if not column_desc:
                if ignore_errors:
                    continue
                else:
                    raise UnknownColumnError('Unknown column: {0}. Allowed columns: {1}'
                                             .format(column_name, ', '.join(sorted(column_name_to_desc.keys()))))
            try:
                clause = column_desc.get_where_sql_clause(column_filter)  # type: SQLClause
                res.append(clause)
            except FilterSyntaxError or FilterValueParsingError as e:
                if ignore_errors:
                    continue
                else:
                    raise e
    return res
