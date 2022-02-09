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
from typing import Dict, List, Optional, Tuple, Generator, Set, Callable, Union

from django.db import connection
from pydash.strings import snake_case

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


SORT_DIRECTIONS = {'asc', 'desc'}


def dict_fetch_all(columns: Union[List[str], None], cursor) -> List[Dict]:
    if columns is None:
        columns = [col[0] for col in cursor.description]
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


def sum_list(lists: List[List]) -> List:
    res = []
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
    sql = []
    params = []
    for clause in clauses:  # type: SQLClause
        if clause is None:
            continue
        if add_parentheses:
            sql.append('(' + clause.sql + ')')
        else:
            sql.append(clause.sql)
        params += (clause.params or [])
    if not sql:
        return None
    return SQLClause(separator.join(sql), params)


def format_clause(sql_template: str, *args, **kwargs) -> SQLClause:
    format_args = [c.sql if isinstance(c, SQLClause) else (c or '') for c in args] if args else []
    format_kwargs = {name: value.sql if isinstance(value, SQLClause) else (value or '')
                     for name, value in kwargs.items()} if kwargs else {}
    sql = sql_template.format(*format_args, **format_kwargs)
    clauses_from_args = [c for c in args if isinstance(c, SQLClause)] if args else []

    clauses_from_kwargs = []

    r = '{(?P<arg>' + '|'.join(['(' + arg_name + ')' for arg_name in kwargs]) + ')}'

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

        columns_clauses = []
        values_clauses = []
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


def drop_indexes_for_table_and_generate_restore_query(cursor,
                                                      table_name: str,
                                                      related_to_columns_only: Set[str] = None,
                                                      schema_name: str = 'public') -> List[str]:
    q = '''
SELECT DISTINCT
       ci.relname AS INDEX_NAME, 
       pg_catalog.pg_get_indexdef(ci.oid)
FROM pg_catalog.pg_class ct 
  JOIN pg_catalog.pg_namespace n ON (ct.relnamespace = n.oid) 
  JOIN (SELECT i.indexrelid, i.indrelid, i.indoption, 
          i.indisunique, i.indisclustered, i.indpred, 
          i.indexprs, 
          information_schema._pg_expandarray(i.indkey) AS keys,
          i.indisprimary
        FROM pg_catalog.pg_index i) i 
    ON (ct.oid = i.indrelid) 
  JOIN pg_catalog.pg_class ci ON (ci.oid = i.indexrelid) 
WHERE n.nspname = %s
AND ct.relname = %s
AND NOT i.indisprimary
'''
    params = [schema_name, table_name]

    if related_to_columns_only:
        q += '\nAND pg_catalog.pg_get_indexdef(ci.oid, (i.keys).n, false) in (%s)'
        params.append(related_to_columns_only)
    q += ';'

    cursor.execute(q, params)
    restore_queries = set()
    drop_queries = set()

    for index_name, indexdef in cursor.fetchall():
        drop_queries.add(f'DROP INDEX {schema_name}."{index_name}"')
        restore_queries.add(indexdef + ';')

    for q in sorted(drop_queries):
        cursor.execute(q)
    return sorted(restore_queries)


def drop_constraints_for_table_and_generate_restore_queries(cursor,
                                                            table_name: str,
                                                            related_to_columns_only: Set[str] = None,
                                                            schema_name: str = 'public') -> List[str]:
    q = '''
SELECT DISTINCT
       c.conname, 
       pg_get_constraintdef(c.oid)
FROM               pg_constraint c
        INNER JOIN pg_namespace n
                   ON n.oid = c.connamespace
        CROSS JOIN LATERAL unnest(c.conkey) ak(k)
        INNER JOIN pg_attribute a
                   ON a.attrelid = c.conrelid
                      AND a.attnum = ak.k
WHERE n.nspname = %s and c.conrelid::regclass::text = %s
    '''
    params = [schema_name, table_name]

    if related_to_columns_only:
        q = q + ' and a.attname in (%s)'
        params.append(related_to_columns_only)
    q = q + ';'
    cursor.execute(q, params)

    restore_queries = set()
    drop_queries = set()

    for constraint_name, constraint_def in cursor.fetchall():
        if 'PRIMARY KEY ' in constraint_def:
            continue
        restore_queries.add(f'ALTER TABLE {schema_name}."{table_name}" '
                            f'ADD CONSTRAINT {constraint_name} {constraint_def};')
        drop_queries.add(f'ALTER TABLE {schema_name}."{table_name}" '
                         f'DROP CONSTRAINT {constraint_name};')

    for q in sorted(drop_queries):
        cursor.execute(q)
    return sorted(restore_queries)


class maintenance_work_mem:
    def __init__(self,
                 cursor,
                 logger_proc: Callable[[str], None] = None) -> None:
        super().__init__()
        self.cursor = cursor
        self.log = logger_proc

    def __enter__(self):

        self.original_work_mem = fetch_int(self.cursor, SQLClause('show work_mem;'))
        maintenance_work_mem = fetch_int(self.cursor, SQLClause('show maintenance_work_mem;'))

        if self.log:
            self.log(f'Current work_mem is: {self.original_work_mem}\n'
                     f'Setting to the same value as maintenance_work_mem: {maintenance_work_mem}')
        self.cursor.execute(f'set work_mem to \'{maintenance_work_mem}\'')

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.log:
            self.log(f'Restoring work_mem to: {self.original_work_mem}')
        self.cursor.execute(f'set work_mem to \'{self.original_work_mem}\'')


class dropping_constraints_and_indexes:
    def __init__(self,
                 cursor,
                 table_name: str, schema_name: str = 'public',
                 logger_proc: Callable[[str], None] = None) -> None:
        super().__init__()
        self.cursor = cursor
        self.table_name = table_name
        self.schema_name = schema_name
        self.log = logger_proc
        self.restore_constraints = []  # type: List[str]
        self.restore_indexes = []  # type: List[str]

    def __enter__(self):
        if self.log:
            self.log(f'Acquiring access exclusive lock on table: {self.schema_name}."{self.table_name}"')
        self.cursor.execute(f'LOCK TABLE {self.schema_name}."{self.table_name}" IN ACCESS EXCLUSIVE MODE;')

        if self.log:
            self.log(f'Dropping constraints for table: {self.schema_name}."{self.table_name}"')
        self.restore_constraints = drop_constraints_for_table_and_generate_restore_queries(
            self.cursor, self.table_name, schema_name=self.schema_name)
        if self.log:
            self.log(f'Dropping indexes for table: {self.schema_name}."{self.table_name}"')
        self.restore_indexes = drop_indexes_for_table_and_generate_restore_query(
            self.cursor, self.table_name, schema_name=self.schema_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.log:
            self.log(f'Restoring constraints for table: {self.schema_name}."{self.table_name}"\n' + '\n'.join(
                self.restore_constraints))

        for q in self.restore_constraints:
            self.cursor.execute(q)

        if self.log:
            self.log(f'Restoring indexes for table: {self.schema_name}."{self.table_name}"\n' + '\n'.join(
                self.restore_indexes))

        for q in self.restore_indexes:
            self.cursor.execute(q)


class ModelLock:
    # Transaction-time table lock
    LOCK_MODE_EXCLUSIVE = 'EXCLUSIVE'
    LOCK_MODE_ACCESS_EXCLUSIVE = 'ACCESS EXCLUSIVE'

    def __init__(self,
                 cursor,
                 model,
                 lock='EXCLUSIVE') -> None:
        self.model = model
        self.cursor = cursor
        self.lock = lock
        self.close_cursor = False

    def __enter__(self):
        if not self.cursor:
            self.cursor = connection.cursor()
            self.close_cursor = True
        self.cursor.execute(f'LOCK TABLE {self.model._meta.db_table} IN {self.lock} MODE;')

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.close_cursor:
            self.cursor.close()
