import re
from datetime import datetime, date
from enum import Enum
from typing import List, Optional, Any, Tuple, Dict

import dateparser

from apps.common.sql_commons import escape_column_name, first_or_none, SQLClause, SQLInsertClause
from apps.rawdb.rawdb.errors import FilterSyntaxError, FilterValueParsingError

PG_DEFAULT_LANGUAGE = 'english'


class PgTypes(Enum):
    """PostgreSQL data type written exactly in the form pg_catalog.format_type() returns them."""
    INTEGER_PRIMARY_KEY = 'integer primary key'
    DOUBLE = 'double precision'
    INTEGER = 'integer'
    BOOLEAN = 'boolean'
    VARCHAR = 'character varying'
    TSVECTOR = 'tsvector'
    TIMESTAMP = 'timestamp without time zone'
    DATE = 'date'
    NUMERIC_50_4 = 'numeric(50,4)'
    TEXT = 'text'


class ValueType(Enum):
    INTEGER = 'integer'
    FLOAT = 'float'
    STRING = 'string'
    DATE = 'date'
    BOOLEAN = 'boolean'
    CURRENCY = 'currency'
    RELATED_INFO = 'related_info'


class ColumnDesc:
    """
    Column description for client usage.
    Column name, human-readable title, type of values understandable by client, choices
    """
    __slots__ = ['field_code', 'name', 'title', 'value_type', 'choices']

    def __init__(self, field_code: str, name: str, title: str, value_type: ValueType,
                 choices: Optional[List] = None) -> None:
        super().__init__()
        self.field_code = field_code
        self.name = name
        self.title = title
        self.value_type = value_type
        self.choices = choices

    def get_where_sql_clause(self, field_filter: str) -> Optional[SQLClause]:
        return None

    def get_field_filter_syntax_hint(self) -> List[Tuple[str, str]]:
        return []


class TextSearchColumnDesc(ColumnDesc):
    __slots__ = ['field_code', 'name', 'title', 'value_type', 'choices', 'tsvector_column']

    def __init__(self, field_code: str, name: str, title: str, value_type: ValueType, tsvector_column: str,
                 choices: Optional[List] = None) -> None:
        super().__init__(field_code, name, title, value_type, choices)
        self.tsvector_column = tsvector_column

    def get_where_sql_clause(self, field_filter: str) -> Optional[SQLClause]:
        if not field_filter:
            return SQLClause('"{output_column}" is Null'.format(output_column=self.name), [])
        elif field_filter == '*':
            return SQLClause('"{output_column}" is not Null'.format(output_column=self.name), [])
        else:
            return SQLClause('"{tsvector_column}" @@ to_tsquery(%s, %s)'
                             .format(tsvector_column=self.tsvector_column),
                             [PG_DEFAULT_LANGUAGE, field_filter])

    def get_field_filter_syntax_hint(self) -> List[Tuple[str, str]]:
        return [
            ('word',
             'Find documents containing "word" in column "{0}" with full-text search engine.'.format(self.title)),
            ('*', 'Find documents having non-empty column "{0}".'.format(self.title)),
            ('', 'Find documents having empty column "{0}".'.format(self.title))
        ]


class RelatedInfoColumnDesc(ColumnDesc):
    __slots__ = ['field_code', 'name', 'title', 'value_type', 'choices', 'text_column']

    def __init__(self, field_code: str, name: str, title: str, text_column: str) -> None:
        super().__init__(field_code, name, title, ValueType.RELATED_INFO, None)
        self.text_column = text_column

    def get_where_sql_clause(self, field_filter: str) -> Optional[SQLClause]:
        if not field_filter or field_filter.lower() == 'false':
            return SQLClause('"{text_column}" is Null'.format(text_column=self.text_column), [])
        elif field_filter == '*' or field_filter.lower() == 'true':
            return SQLClause('"{text_column}" is not Null'.format(text_column=self.text_column), [])
        else:
            return SQLClause('"{text_column}" ilike %s'.format(text_column=self.text_column),
                             ['%' + field_filter + '%'])

    def get_field_filter_syntax_hint(self) -> List[Tuple[str, str]]:
        return [
            ('substring',
             'Find documents containing "word" in the parts of text related to "{0}".'.format(self.title)),
            ('true', 'Find documents containing a sentence/paragraph related to "{0}".'.format(self.title)),
            ('false',
             'Find documents which does not contain any sentence/paragraph related to "{0}".'.format(self.title))
        ]


class StringColumnDesc(ColumnDesc):
    def get_where_sql_clause(self, field_filter: str) -> Optional[SQLClause]:
        if not field_filter:
            return SQLClause('"{column}" is Null'.format(column=self.name), [])
        elif field_filter == '*':
            return SQLClause('"{column}" is not Null'.format(column=self.name), [])
        elif field_filter.startswith('!'):
            return SQLClause('"{column}" not ilike %s'.format(column=self.name), ['%' + field_filter[1:] + '%'])
        else:
            return SQLClause('"{column}" ilike %s'.format(column=self.name), ['%' + field_filter + '%'])

    def get_field_filter_syntax_hint(self) -> List[Tuple[str, str]]:
        return [
            ('substr',
             'Find documents containing "substr" in column "{0}".'.format(self.title)),
            ('!substr', 'Find documents not containing "substr" in column "{0}".'.format(self.title)),
            ('*', 'Find documents having non-empty column "{0}".'.format(self.title)),
            ('', 'Find documents having empty column "{0}".'.format(self.title))
        ]


class ComparableColumnDesc(ColumnDesc):
    range_query_re = re.compile(
        r'(?P<start_bracket>[[(])?(?P<start_operator>[><]=?)?(?P<start>[^,\[\]()]+),(?P<end_operator>[><]=?)?(?P<end>[^,\[\]()]+)(?P<end_bracket>[])])?')

    compare_re = re.compile(r'(?P<operator>[><]?=?)?(?P<value>[^,\[\]()]+)')

    brackets_to_operators = {
        '(': '>',
        ')': '<',
        '[': '>=',
        ']': '<='
    }

    def convert_value_from_filter_to_db(self, filter_value: str) -> Any:
        return filter_value

    def safe_convert_value_from_filter_to_db(self, filter_value: str) -> Any:
        try:
            return self.convert_value_from_filter_to_db(filter_value)
        except Exception as e:
            raise FilterValueParsingError('Unable to parse value: ' + filter_value, caused_by=e)

    def get_where_sql_clause(self, field_filter: str) -> Optional[SQLClause]:
        if not field_filter:
            return SQLClause('"{output_column}" is Null'.format(output_column=self.name), [])
        elif field_filter == '*':
            return SQLClause('"{output_column}" is not Null'.format(output_column=self.name), [])

        m = self.range_query_re.match(field_filter)
        if m:
            start_bracket = m.group('start_bracket')
            start_operator = m.group('start_operator')
            start_value = m.group('start')
            end_operator = m.group('end_operator')
            end_value = m.group('end')
            end_bracket = m.group('end_bracket')

            start_operator = start_operator or self.brackets_to_operators.get(start_bracket) or '>='
            end_operator = end_operator or self.brackets_to_operators.get(end_bracket) or '<='
            start_value = self.safe_convert_value_from_filter_to_db(start_value)
            end_value = self.safe_convert_value_from_filter_to_db(end_value)

            return SQLClause('"{column}" {op_min} %s and "{column}" {op_max} %s'
                             .format(column=self.name, op_min=start_operator, op_max=end_operator),
                             [start_value, end_value])

        m = self.compare_re.match(field_filter)
        if m:
            operator = m.group('operator') or '='
            value = m.group('value')
            value = self.safe_convert_value_from_filter_to_db(value)
            return SQLClause('"{column}" {operator} %s'.format(column=self.name, operator=operator), [value])

        raise FilterSyntaxError('Filter syntax error: ' + field_filter)

    def get_field_filter_syntax_hint(self) -> List[Tuple[str, str]]:
        return [
            ('*', 'Find documents having non-empty column "{0}.".'.format(self.title)),
            ('', 'Find documents having empty column "{0}.".'.format(self.title)),
            ('>=v1',
             'Find documents having value in column "{0}" greater or equal than/to v1.'
             .format(self.title)),
            ('<=v1',
             'Find documents having value in column "{0}" lower or equal than/to v1.'
             .format(self.title)),
            ('>v1', 'Find documents having value in column "{0}" greater than v1.'
             .format(self.title)),
            ('<v1', 'Find documents having value in column "{0}" lower than v1.'
             .format(self.title)),
            ('v1', 'Find documents having value in column "{0}" equal to v1.'
             .format(self.title)),
            ('[v1, v2]', 'Find documents having value in column "{0}" between v1 and v2 '
                         '(including v1 and v2 ranges).'
             .format(self.title)),
        ]


class IntColumnDesc(ComparableColumnDesc):
    def __init__(self, field_code: str, name: str, title: str) -> None:
        super().__init__(field_code, name, title, ValueType.INTEGER, None)

    def convert_value_from_filter_to_db(self, filter_value: str) -> Any:
        return int(filter_value)


class FloatColumnDesc(ComparableColumnDesc):
    def __init__(self, field_code: str, name: str, title: str) -> None:
        super().__init__(field_code, name, title, ValueType.FLOAT, None)

    def convert_value_from_filter_to_db(self, filter_value: str) -> Any:
        return float(filter_value)


class DateColumnDesc(ComparableColumnDesc):
    def __init__(self, field_code: str, name: str, title: str) -> None:
        super().__init__(field_code, name, title, ValueType.DATE, None)

    def convert_value_from_filter_to_db(self, filter_value: str) -> Any:
        return dateparser.parse(str(filter_value)).date()


class BooleanColumnDesc(ColumnDesc):
    def __init__(self, field_code: str, name: str, title: str) -> None:
        super().__init__(field_code, name, title, ValueType.BOOLEAN, None)

    def get_where_sql_clause(self, field_filter: str) -> Optional[SQLClause]:
        if not field_filter:
            return SQLClause('"{output_column}" is Null'.format(output_column=self.name), [])
        elif field_filter == '*':
            return SQLClause('"{output_column}" is not Null'.format(output_column=self.name), [])
        filter_value = field_filter.strip().lower() if field_filter else None
        db_value = False if not filter_value or filter_value in ('0', 'false') else True
        return SQLClause('"{column}" = %s'.format(column=self.name), [db_value])

    def get_field_filter_syntax_hint(self) -> List[Tuple[str, str]]:
        return [
            ('*', 'Find documents having non-empty column "{0}.".'.format(self.title)),
            ('', 'Find documents having empty column "{0}.".'.format(self.title)),
            ('false or 0', 'Find documents having value in column "{0}" set to true.'.format(self.title)),
            ('true or 1 or any other value',
             'Find documents having value in column "{0}" set to true.'.format(self.title)),
        ]


class FieldHandler:
    """
    Knows which columns to create for a field, which indexes to create, how to insert/update values.

    Field => one or more columns
    ColumnDesc => info for frontend, methods for querying.
    """

    def __init__(self, field_code: str, field_title: str, table_name: str, default_value=None) -> None:
        super().__init__()
        self.field_code = field_code
        self.field_title = field_title
        self.table_name = table_name
        self.default_value = default_value

    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        pass

    def get_pg_column_definitions(self) -> Dict[str, PgTypes]:
        pass

    def get_pg_index_definitions(self) -> Optional[List[str]]:
        pass

    def get_pg_sql_insert_clause(self, document_language: str, python_values: List) -> SQLInsertClause:
        pass


class StringWithTextSearchFieldHandler(FieldHandler):
    def __init__(self, field_code: str, field_title: str, table_name: str, default_value: str = None) -> None:
        super().__init__(field_code, field_title, table_name, default_value)
        self.output_column = escape_column_name(field_code)
        self.text_search_column = escape_column_name(field_code + '_text_search')

    def python_values_to_single_db_value_for_text_search(self, python_values: List) -> Optional[str]:
        return first_or_none(python_values) or self.default_value

    def python_values_to_single_db_value_for_output(self, python_values: List) -> Optional[str]:
        text = self.python_values_to_single_db_value_for_text_search(python_values)

        if not text:
            return None

        text = text.strip()
        if len(text) > 200:
            return text[:200] + '...'
        else:
            return text

    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        return [TextSearchColumnDesc(self.field_code, self.output_column, self.field_title, ValueType.STRING,
                                     self.text_search_column)]

    def get_pg_index_definitions(self) -> Optional[List[str]]:
        return ['using GIN ("{column}" tsvector_ops)'
                    .format(table_name=self.table_name, column=self.text_search_column)]

    def get_pg_column_definitions(self) -> Dict[str, PgTypes]:
        return {
            self.output_column: PgTypes.TEXT,
            self.text_search_column: PgTypes.TSVECTOR
        }

    def get_pg_sql_insert_clause(self, document_language: str, python_values: List) -> SQLInsertClause:
        db_value_for_search = self.python_values_to_single_db_value_for_text_search(python_values)
        db_value_for_output = self.python_values_to_single_db_value_for_output(python_values)
        return SQLInsertClause('"{output_column}", "{text_search_column}"'
                               .format(output_column=self.output_column, text_search_column=self.text_search_column),
                               [],
                               '%s, to_tsvector(%s, %s)',
                               [db_value_for_output, PG_DEFAULT_LANGUAGE, db_value_for_search])


class StringFieldHandler(FieldHandler):
    def __init__(self, field_code: str, field_title: str, table_name: str, default_value: str = None) -> None:
        super().__init__(field_code, field_title, table_name, default_value)
        self.column = escape_column_name(field_code)

    def python_values_to_single_db_value(self, python_values: List) -> Optional[str]:
        return first_or_none(python_values) or self.default_value

    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        return [StringColumnDesc(self.field_code, self.column, self.field_title, ValueType.STRING)]

    def get_pg_index_definitions(self) -> Optional[List[str]]:
        return ['using GIN ("{column}" gin_trgm_ops)'
                    .format(table_name=self.table_name, column=self.column)]

    def get_pg_column_definitions(self) -> Dict[str, PgTypes]:
        return {
            self.column: PgTypes.VARCHAR
        }

    def get_pg_sql_insert_clause(self, document_language: str, python_values: List) -> SQLInsertClause:
        db_value = self.python_values_to_single_db_value(python_values)
        return SQLInsertClause('"{column}"'.format(column=self.column), [], '%s', [db_value])


class ComparableFieldHandler(FieldHandler):
    pg_type = None  # type: PgTypes

    def python_values_to_single_db_value(self, python_values: List) -> Any:
        pass

    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        pass

    def __init__(self, field_code: str, field_title: str, table_name: str, default_value=None) -> None:
        super().__init__(field_code, field_title, table_name, default_value)
        self.column = escape_column_name(field_code)

    def get_pg_index_definitions(self) -> Optional[List[str]]:
        return None

    def get_pg_column_definitions(self) -> Dict[str, PgTypes]:
        return {
            self.column: self.pg_type
        }

    def get_pg_sql_insert_clause(self, document_language: str, python_values: List) -> SQLInsertClause:
        return SQLInsertClause('"{column}"'.format(column=self.column), [],
                               '%s', [self.python_values_to_single_db_value(python_values)])


class IntFieldHandler(ComparableFieldHandler):
    pg_type = PgTypes.INTEGER

    def python_values_to_single_db_value(self, python_values: List) -> Any:
        python_value = first_or_none(python_values) or self.default_value
        return int(python_value) if python_value else None

    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        return [IntColumnDesc(self.field_code, self.column, self.field_title)]


class FloatFieldHandler(ComparableFieldHandler):
    pg_type = PgTypes.DOUBLE

    def python_values_to_single_db_value(self, python_values: List) -> Any:
        python_value = first_or_none(python_values) or self.default_value
        return float(python_value) if python_value else None

    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        return [FloatColumnDesc(self.field_code, self.column, self.field_title)]


class DateFieldHandler(ComparableFieldHandler):
    pg_type = PgTypes.DATE

    def __init__(self, field_code: str, field_title: str, table_name: str, default_value=None) -> None:
        super().__init__(field_code, field_title, table_name,
                         dateparser.parse(default_value) if default_value else None)

    def python_values_to_single_db_value(self, python_values: List) -> Any:
        python_value = first_or_none(python_values) or self.default_value
        return python_value if type(python_value) is date \
            else python_value.date() if type(python_value) is datetime \
            else None

    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        return [DateColumnDesc(self.field_code, self.column, self.field_title)]


class MoneyFieldHandler(FieldHandler):
    def __init__(self, field_code: str, field_title: str, table_name: str, default_value=None) -> None:
        super().__init__(field_code, field_title, table_name, default_value)
        self.currency_column = escape_column_name(field_code + '_currency')
        self.amount_column = escape_column_name(field_code + '_amount')

    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        return [
            StringColumnDesc(self.field_code, self.currency_column, self.field_title + ': Currency', ValueType.STRING),
            FloatColumnDesc(self.field_code, self.amount_column, self.field_title + ': Amount')]

    def get_pg_column_definitions(self) -> Dict[str, PgTypes]:
        return {
            self.currency_column: PgTypes.VARCHAR,
            self.amount_column: PgTypes.NUMERIC_50_4
        }

    def get_pg_sql_insert_clause(self, document_language: str, python_values: List) -> SQLInsertClause:
        money = first_or_none(python_values) or self.default_value  # Dict
        currency = money.get('currency') if money else None
        amount = money.get('amount') if money else None
        return SQLInsertClause('"{currency_column}", '
                               '"{amount_column}"'.format(currency_column=self.currency_column,
                                                          amount_column=self.amount_column), [],
                               '%s, %s', [currency, amount])

    def get_pg_index_definitions(self) -> Optional[List[str]]:
        return ['using GIN ("{column}" gin_trgm_ops)'
                    .format(table_name=self.table_name, column=self.currency_column)]


class AddressFieldHandler(StringFieldHandler):
    def python_values_to_single_db_value(self, python_values: List) -> Any:
        address = first_or_none(python_values) or self.default_value # Dict
        return str(address.get('address') or '') if address else None


class RelatedInfoFieldHandler(FieldHandler):
    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        return [RelatedInfoColumnDesc(self.field_code, self.column, self.field_title, self.text_column)]

    def __init__(self, field_code: str, field_title: str, table_name: str, default_value=None) -> None:
        super().__init__(field_code, field_title, table_name, default_value)
        self.column = escape_column_name(field_code)
        self.text_column = escape_column_name(field_code) + '_text'

    def get_pg_index_definitions(self) -> Optional[List[str]]:
        return ['using GIN ("{column}" gin_trgm_ops)'.format(table_name=self.table_name, column=self.text_column)]

    def get_pg_column_definitions(self) -> Dict[str, PgTypes]:
        return {
            self.column: PgTypes.BOOLEAN,
            self.text_column: PgTypes.TEXT
        }

    def get_pg_sql_insert_clause(self, document_language: str, python_values: List) -> SQLInsertClause:
        yes_no = bool(python_values or self.default_value)
        related_info_text = '\n'.join([str(v) for v in python_values if v]) if python_values else None
        return SQLInsertClause('"{column}", "{text_column}"'.format(column=self.column, text_column=self.text_column),
                               [],
                               '%s, %s', [yes_no, related_info_text])


class BooleanFieldHandler(FieldHandler):
    pg_type = PgTypes.BOOLEAN

    def python_values_to_single_db_value(self, python_values: List) -> Any:
        python_value = first_or_none(python_values) or self.default_value
        return bool(python_value) if python_value is not None else False

    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        return [BooleanColumnDesc(self.field_code, self.column, self.field_title)]

    def __init__(self, field_code: str, field_title: str, table_name: str, default_value:bool = None) -> None:
        super().__init__(field_code, field_title, table_name, default_value)
        self.column = escape_column_name(field_code)

    def get_pg_index_definitions(self) -> Optional[List[SQLClause]]:
        return None

    def get_pg_column_definitions(self) -> Dict[str, PgTypes]:
        return {
            self.column: self.pg_type
        }

    def get_pg_sql_insert_clause(self, document_language: str, python_values: List) -> SQLInsertClause:
        return SQLInsertClause('"{column}"'.format(column=self.column), [],
                               '%s', [self.python_values_to_single_db_value(python_values)])


class MultichoiceFieldHandler(StringFieldHandler):
    def python_values_to_single_db_value(self, python_values: List) -> Any:
        if not python_values:
            return self.default_value

        return ', '.join(sorted({str(v) for v in python_values}))
