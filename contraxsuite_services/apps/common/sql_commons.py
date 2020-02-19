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
from typing import Dict, List, Optional, Tuple, Generator

from django.db import connection
from pydash.strings import snake_case

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


SORT_DIRECTIONS = {'asc', 'desc'}


def dict_fetch_all(columns: List[str], cursor) -> List[Dict]:
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def escape_column_name(field_code: str, do_snake_case: bool = True):
    res = snake_case(field_code) if do_snake_case else field_code
    res = ''.join([ch.lower() if ch.isalnum() else '_' for ch in res])
    res = res if len(res) > 0 and res[0].isalpha() else '_' + res
    while '__' in res:
        res = res.replace('__', '_')
    return res


def first_or_none(l: List):
    for i in l:
        return i
    return None


def extend_list(list1: List, list2: Optional[List]):
    if list2:
        list1.extend(list2)


def sum_list(lists: List[List]) -> List:
    res = list()
    for l in lists:
        if l:
            res.extend(l)
    return res


class SQLClause:
    __slots__ = ['sql', 'params']

    def __init__(self, sql: str, params: Optional[List] = None) -> None:
        super().__init__()
        self.sql = sql
        self.params = params or []  # type: List

    def __str__(self) -> str:
        return '{sql} | {params}'.format(sql=self.sql, params=', '.join([str(p) for p in self.params]))


def join_clauses(separator: str, clauses: List[Optional['SQLClause']], add_parentheses: bool = False) \
        -> Optional['SQLClause']:
    sql = list()
    params = list()
    for clause in clauses:  # type: SQLClause
        if clause is None:
            continue
        if add_parentheses:
            sql.append('(' + clause.sql + ')')
        else:
            sql.append(clause.sql)
        extend_list(params, clause.params)
    if not sql:
        return None
    return SQLClause(separator.join(sql), params)


def format_clause(sql_template: str, *args, **kwargs) -> SQLClause:
    format_args = [c.sql if isinstance(c, SQLClause) else (c or '') for c in args] if args else []
    format_kwargs = {name: value.sql if isinstance(value, SQLClause) else (value or '')
                     for name, value in kwargs.items()} if kwargs else {}
    sql = sql_template.format(*format_args, **format_kwargs)
    clauses_from_args = [c for c in args if isinstance(c, SQLClause)] if args else []

    clauses_from_kwargs = list()

    r = '{(?P<arg>' + '|'.join(['(' + arg_name + ')' for arg_name in kwargs.keys()]) + ')}'

    for m in re.finditer(r, sql_template):
        arg_name = m.group('arg')
        arg_value = kwargs.get(arg_name)
        if isinstance(arg_value, SQLClause):
            clauses_from_kwargs.append(arg_value)

    params = sum_list([clause.params for clause in clauses_from_args + clauses_from_kwargs])

    return SQLClause(sql, params)


class SQLInsertClause:
    __slots__ = ['columns_clause', 'values_clause']

    def __init__(self, columns_sql: str, columns_params: List, values_sql: str, values_params: List) -> None:
        super().__init__()
        self.columns_clause = SQLClause(columns_sql, columns_params)
        self.values_clause = SQLClause(values_sql, values_params)

    def __str__(self) -> str:
        return 'columns = ({columns}), values = ({values})' \
            .format(columns=self.columns_clause, values=self.values_clause)

    @staticmethod
    def join(clauses: List['SQLInsertClause']) -> Tuple[Optional[SQLClause], Optional[SQLClause]]:
        if not clauses:
            return None, None

        columns_clauses = list()
        values_clauses = list()
        for c in clauses:
            columns_clauses.append(c.columns_clause)
            values_clauses.append(c.values_clause)

        columns_joined = join_clauses(',\n', columns_clauses)
        values_joined = join_clauses(',\n', values_clauses)

        return columns_joined, values_joined


def fetch_dicts(cursor, sql: SQLClause, columns: List[str]) -> List[Dict]:
    cursor.execute(sql.sql, sql.params)
    return dict_fetch_all(columns, cursor)


def fetch_int(cursor, sql: SQLClause) -> int:
    cursor.execute(sql.sql, sql.params)
    return cursor.fetchone()[0]


def fetch_bool(cursor, sql: SQLClause) -> bool:
    cursor.execute(sql.sql, sql.params)
    return bool(cursor.fetchone()[0])


def sql_query(sql: str, params: List = None) -> Generator[Tuple, None, None]:
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        rows = cursor.fetchmany(100)
        while rows:
            for row in rows:
                yield row
            rows = cursor.fetchmany(100)
