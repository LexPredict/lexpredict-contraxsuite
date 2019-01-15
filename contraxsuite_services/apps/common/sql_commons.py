import re
from typing import Dict, List, Optional, Tuple

from pydash.strings import snake_case

SORT_DIRECTIONS = {'asc', 'desc'}


def dict_fetch_all(columns: List[str], cursor) -> List[Dict]:
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def escape_column_name(field_code: str, do_snake_case:bool = True):
    res = snake_case(field_code) if do_snake_case else field_code
    res = ''.join([ch.lower() if ch.isalnum() else '_' for ch in res])
    res = res if res[0].isalpha() else '_' + res
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


def format_clause(sql_template: str, *args, **kwargs):
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

