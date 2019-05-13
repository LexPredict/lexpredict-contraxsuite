import re
from enum import Enum
from typing import List, Tuple, Dict, Optional

from apps.common.sql_commons import SQLClause
from apps.rawdb.rawdb.field_handlers import ColumnDesc
from apps.rawdb.rawdb.errors import OrderByParsingError, FilterSyntaxError, UnknownColumnError, FilterValueParsingError


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
