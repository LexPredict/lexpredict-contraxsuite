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
import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Any, Tuple, Dict, Set

import dateparser
from django.utils.timezone import get_current_timezone

from apps.common.contraxsuite_urls import doc_editor_url
from apps.common.sql_commons import escape_column_name, SQLClause, SQLInsertClause
from apps.common.utils import parse_date
from apps.document.field_types import StringField
from apps.document.models import Document
from apps.rawdb.rawdb.errors import FilterSyntaxError, FilterValueParsingError

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


PG_DEFAULT_LANGUAGE = 'english'


class PgTypes(Enum):
    """PostgreSQL data type written exactly in the form pg_catalog.format_type() returns them."""
    INTEGER_PRIMARY_KEY = 'integer primary key'
    DOUBLE = 'double precision'
    INTEGER = 'bigint'
    BOOLEAN = 'boolean'
    VARCHAR = 'character varying'
    TSVECTOR = 'tsvector'
    TIMESTAMP = 'timestamp without time zone'
    TIMESTAMP_WITH_TIMEZONE = 'timestamp with time zone'
    DATE = 'date'
    NUMERIC_50_4 = 'numeric(50,4)'
    NUMERIC_50_6 = 'numeric(50,6)'
    NUMERIC_50_8 = 'numeric(50,8)'
    TEXT = 'text'
    STRING_ARRAY = 'character varying[]'


class ValueType(Enum):
    INTEGER = 'integer'
    FLOAT = 'float'
    RATIO = 'ratio'
    STRING = 'string'
    DATE = 'date'
    DATETIME = 'datetime'
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

    def get_output_column_sql_spec(self) -> str:
        return '"' + self.name + '"'

    def get_where_sql_clause(self, field_filter: str) -> Optional[SQLClause]:
        return None

    def get_field_filter_syntax_hint(self) -> List[Tuple[str, str]]:
        return []


class TextSearchColumnDesc(ColumnDesc):
    __slots__ = ['field_code', 'name', 'title', 'value_type', 'choices', 'tsvector_column', 'limit_output_char_num']

    def __init__(self, field_code: str, name: str, title: str, value_type: ValueType, tsvector_column: str,
                 choices: Optional[List] = None,
                 limit_output_char_num: int = None) -> None:
        super().__init__(field_code, name, title, value_type, choices)
        self.tsvector_column = tsvector_column
        self.limit_output_char_num = limit_output_char_num

    def get_output_column_sql_spec(self) -> str:
        return '(case when length("{col}") > {len} then substring("{col}" for {len}) || \'...\' else "{col}" end)' \
            .format(col=self.name, len=self.limit_output_char_num) \
            if self.limit_output_char_num else '"{col}"'.format(col=self.name)

    def get_where_sql_clause(self, field_filter: str) -> Optional[SQLClause]:
        if not field_filter:
            return SQLClause('"{output_column}" is Null'.format(output_column=self.name), [])
        if field_filter == '*':
            return SQLClause('"{output_column}" is not Null'.format(output_column=self.name), [])
        # NOTE: to_tsquery works with single words, to search phrases use "<->" operator
        # either "tsquery_phrase(to_tsquery('fat'), to_tsquery('cat'))"
        field_filter = ' <-> '.join(field_filter.split())
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
        if field_filter == '*' or field_filter.lower() == 'true':
            return SQLClause('"{text_column}" is not Null'.format(text_column=self.text_column), [])
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
    __slots__ = ['field_code', 'name', 'title', 'value_type', 'choices', 'limit_output_char_num', 'explicit_text_conversion']

    def __init__(self, field_code: str, name: str, title: str, value_type: ValueType,
                 choices: Optional[List] = None,
                 limit_output_char_num: int = None,
                 explicit_text_conversion: bool = False) -> None:
        super().__init__(field_code, name, title, value_type, choices)
        self.limit_output_char_num = limit_output_char_num
        self.explicit_text_conversion = explicit_text_conversion

    def get_output_column_sql_spec(self) -> str:
        return '(case when length("{col}") > {len} then substring("{col}" for {len}) || \'...\' else "{col}" end)' \
            .format(col=self.name, len=self.limit_output_char_num) \
            if self.limit_output_char_num else '"{col}"'.format(col=self.name)

    def get_where_sql_clause(self, field_filter: str) -> Optional[SQLClause]:
        column = f'"{self.name}"::text' if self.explicit_text_conversion is True else f'"{self.name}"'
        if not field_filter:
            return SQLClause('{column} is Null'.format(column=column), [])
        if field_filter == '*':
            return SQLClause('{column} is not Null'.format(column=column), [])
        if field_filter.startswith('!'):
            return SQLClause('{column} not ilike %s'.format(column=column), ['%' + field_filter[1:] + '%'])
        return SQLClause('{column} ilike %s'.format(column=column), ['%' + field_filter + '%'])

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

    date_format_re = re.compile(r'\d{4}-\d{2}-\d{2}')

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
        if field_filter == '*':
            return SQLClause('"{output_column}" is not Null'.format(output_column=self.name), [])

        m = self.range_query_re.match(field_filter)
        if m:
            start_bracket = m.group('start_bracket')
            start_operator = m.group('start_operator')
            start_value = m.group('start')
            end_operator = m.group('end_operator')
            end_value = m.group('end')
            end_bracket = m.group('end_bracket')

            # Add time to range date picker in order to include items of edge days
            if self.date_format_re.match(start_value) and self.date_format_re.match(end_value) \
                    and start_bracket == '[' and end_bracket == ']':
                start_value += ' 00:00:00'
                end_value += ' 23:59:59'

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


class RatioColumnDesc(ComparableColumnDesc):
    def __init__(self, field_code: str, name: str, title: str) -> None:
        super().__init__(field_code, name, title, ValueType.RATIO, None)

    def convert_value_from_filter_to_db(self, filter_value: str) -> Any:
        return float(filter_value)

    def convert_ratio_value_from_filter_to_db(self, filter_value: str) -> Any:
        try:
            values = [float(i) if i else i for i in filter_value.split('/')]
            if not 0 < len(values) < 3:
                raise Exception('Too much or not enough parsed values')
            return values
        except Exception as e:
            raise FilterValueParsingError('Unable to parse value: ' + filter_value, caused_by=e)

    def get_where_sql_clause(self, field_filter: str) -> Optional[SQLClause]:
        if not self.name.endswith('_num_den'):
            return super().get_where_sql_clause(field_filter)
        output_num_column = self.name[:-8] + '_num'
        output_den_column = self.name[:-8] + '_den'
        if not field_filter:
            return SQLClause(f'"{output_num_column}" is Null OR "{output_den_column}" is Null', [])
        if field_filter == '*':
            return SQLClause(f'"{output_num_column}" is not Null '
                             f'OR "{output_den_column}" is not Null', [])

        m = self.compare_re.match(field_filter)
        if m:
            operator = m.group('operator') or '='
            values = self.convert_ratio_value_from_filter_to_db(m.group('value'))
            if len(values) == 1:
                return SQLClause(f'"{output_num_column}" {operator} %s OR "{output_den_column}" '
                                 f'{operator} %s', [values[0], values[0]])
            if values[0] and values[1]:
                return SQLClause(f'"{output_num_column}" {operator} %s AND "{output_den_column}" '
                                 f'{operator} %s', [values[0], values[1]])
            if values[0]:
                return SQLClause(f'"{output_num_column}" {operator} %s', [values[0]])
            if values[1]:
                return SQLClause(f'"{output_den_column}" {operator} %s', [values[1]])

        raise FilterSyntaxError('Filter syntax error: ' + field_filter)

    def get_field_filter_syntax_hint(self) -> List[Tuple[str, str]]:
        return super().get_field_filter_syntax_hint()[:-1]


class DateColumnDesc(ComparableColumnDesc):
    def __init__(self, field_code: str, name: str, title: str) -> None:
        super().__init__(field_code, name, title, ValueType.DATE, None)

    def convert_value_from_filter_to_db(self, filter_value: str) -> Any:
        return parse_date(str(filter_value)).date()


class DateTimeColumnDesc(ComparableColumnDesc):
    RE_DATE_FORMAT = re.compile(r'\d{4}-\d{2}-\d{2}')

    def __init__(self, field_code: str, name: str, title: str) -> None:
        super().__init__(field_code, name, title, ValueType.DATETIME, None)

    def convert_value_from_filter_to_db(self, filter_value: str) -> Any:
        return parse_date(str(filter_value))

    def get_where_sql_clause(self, field_filter: str) -> Optional[SQLClause]:
        # make range from field_filter if it's a date
        # i.e. "2008-06-01,2008-06-02" from 2008-06-01
        if not field_filter:
            return super().get_where_sql_clause(field_filter)
        if not self.RE_DATE_FORMAT.match(field_filter):
            return super().get_where_sql_clause(field_filter)

        try:
            date_part = parse_date(str(field_filter)).date()
        except:
            return super().get_where_sql_clause(field_filter)
        next_date = date_part + datetime.timedelta(days=1)
        filter_range = f"{date_part.strftime('%Y-%m-%d')},{next_date.strftime('%Y-%m-%d')}"
        return super().get_where_sql_clause(filter_range)


class BooleanColumnDesc(ColumnDesc):
    def __init__(self, field_code: str, name: str, title: str) -> None:
        super().__init__(field_code, name, title, ValueType.BOOLEAN, None)

    def get_where_sql_clause(self, field_filter: str) -> Optional[SQLClause]:
        if not field_filter:
            return SQLClause('"{output_column}" is Null'.format(output_column=self.name), [])
        if field_filter == '*':
            return SQLClause('"{output_column}" is not Null'.format(output_column=self.name), [])
        filter_value = field_filter.strip().lower() if field_filter else None
        db_value = bool(filter_value and filter_value not in ('0', 'false'))
        return SQLClause('"{column}" = %s'.format(column=self.name), [db_value])

    def get_field_filter_syntax_hint(self) -> List[Tuple[str, str]]:
        return [
            ('*', 'Find documents having non-empty column "{0}.".'.format(self.title)),
            ('', 'Find documents having empty column "{0}.".'.format(self.title)),
            ('false or 0', 'Find documents having value in column "{0}" set to true.'.format(self.title)),
            ('true or 1 or any other value',
             'Find documents having value in column "{0}" set to true.'.format(self.title)),
        ]


class RawdbFieldHandler:
    """
    Knows which columns to create for a field, which indexes to create, how to insert/update values.

    Field => one or more columns
    ColumnDesc => info for frontend, methods for querying.
    """

    def __init__(self,
                 field_code: str,
                 field_type: Optional[str] = None,
                 field_title: Optional[str] = None,
                 table_name: Optional[str] = None,
                 default_value=None,
                 field_column_name_base: str = None) -> None:
        super().__init__()
        self.field_code = field_code
        self.field_type = field_type
        self.field_column_name_base = field_column_name_base or escape_column_name(field_code)
        self.field_title = field_title or field_code
        self.table_name = table_name
        self.default_value = default_value
        self.is_annotation = False

    def __str__(self) -> str:
        maybe_table = self.table_name + '.' if self.table_name else ''
        maybe_field_type = ': ' + self.field_type if self.field_type else ''
        return maybe_table + self.field_code + maybe_field_type

    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        pass

    def get_pg_column_definitions(self) -> Dict[str, PgTypes]:
        pass

    def get_pg_index_definitions(self) -> Optional[List[str]]:
        pass

    def get_pg_sql_insert_clause(self, document_language: str,
                                 fields_to_python_values: Dict[str, Any]) -> SQLInsertClause:
        pass

    def python_value_to_indexed_field_value(self, dfv_python_value) -> Any:
        pass

    def columns_to_field_value(self, columns: Dict[str, Any]) -> Any:
        pass

    def column_names_for_field_values(self) -> Set[str]:
        pass


class StringWithTextSearchRawdbFieldHandler(RawdbFieldHandler):
    def __init__(self,
                 field_code: str,
                 field_type: str,
                 field_title: str,
                 table_name: str,
                 default_value: str = None,
                 field_column_name_base: str = None,
                 output_column_char_limit: int = None) -> None:
        super().__init__(field_code, field_type, field_title, table_name, default_value, field_column_name_base)
        self.output_column = escape_column_name(self.field_column_name_base)
        self.text_search_column = escape_column_name(self.field_column_name_base + '_text_search')
        self.output_column_char_limit = output_column_char_limit

    def python_value_to_single_db_value_for_text_search(self, python_value) -> Optional[str]:
        return python_value or self.default_value

    def python_value_to_indexed_field_value(self, python_value) -> Optional[str]:
        return self.python_value_to_single_db_value_for_text_search(python_value)

    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        return [TextSearchColumnDesc(self.field_code,
                                     self.output_column,
                                     self.field_title,
                                     ValueType.STRING,
                                     self.text_search_column,
                                     limit_output_char_num=self.output_column_char_limit)]

    def get_pg_index_definitions(self) -> Optional[List[str]]:
        return [
            'using GIN ("{column}" tsvector_ops)'.format(column=self.text_search_column),
            'using GIN ("{column}" gin_trgm_ops)'.format(column=self.output_column)
        ]

    def get_pg_column_definitions(self) -> Dict[str, PgTypes]:
        return {
            self.output_column: PgTypes.TEXT,
            self.text_search_column: PgTypes.TSVECTOR
        }

    def get_pg_sql_insert_clause(self, document_language: str, python_values: Dict[str, Any]) -> SQLInsertClause:
        python_value = python_values.get(self.field_code)
        db_value_for_search = self.python_value_to_single_db_value_for_text_search(python_value)
        db_value_for_output = self.python_value_to_indexed_field_value(python_value)
        return SQLInsertClause('"{output_column}", "{text_search_column}"'
                               .format(output_column=self.output_column, text_search_column=self.text_search_column),
                               [],
                               '%s, to_tsvector(%s, %s)',
                               [db_value_for_output, PG_DEFAULT_LANGUAGE, db_value_for_search])

    def columns_to_field_value(self, columns: Dict[str, Any]) -> Any:
        return columns.get(self.output_column)

    def column_names_for_field_values(self) -> Set[str]:
        return {self.output_column}


class LongTextFromRelTableFieldHandler(StringWithTextSearchRawdbFieldHandler):

    def __init__(self, field_code: str, field_title: str, table_name: str,
                 select_text_sql: str,
                 select_text_ref_id_field_code: str,
                 output_column_char_limit: int = None) -> None:
        super().__init__(field_code,
                         field_type=StringField.type_code,
                         field_title=field_title,
                         table_name=table_name,
                         default_value=None,
                         field_column_name_base=field_code,
                         output_column_char_limit=output_column_char_limit)
        self.select_text_ref_id_field_code = select_text_ref_id_field_code
        self.select_text_sql = select_text_sql

    def get_pg_sql_insert_clause(self, document_language: str, python_values: Dict[str, Any]) -> SQLInsertClause:
        ref_id = python_values.get(self.select_text_ref_id_field_code)
        return SQLInsertClause(columns_sql=f'"{self.output_column}", "{self.text_search_column}"',
                               columns_params=[],
                               values_sql=f'({self.select_text_sql}), to_tsvector(%s, ({self.select_text_sql}))',
                               values_params=[ref_id, PG_DEFAULT_LANGUAGE, ref_id])


class StringRawdbFieldHandler(RawdbFieldHandler):
    def __init__(self,
                 field_code: str,
                 field_type: str,
                 field_title: str,
                 table_name: str,
                 default_value: str = None,
                 field_column_name_base: str = None,
                 column_output_char_limit: int = None,
                 explicit_text_conversion: bool = False) -> None:
        super().__init__(field_code, field_type, field_title, table_name, default_value, field_column_name_base)
        self.column = escape_column_name(self.field_column_name_base)
        self.column_output_char_limit = column_output_char_limit
        self.explicit_text_conversion = explicit_text_conversion

    def python_value_to_indexed_field_value(self, python_value):
        return python_value or self.default_value

    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        return [StringColumnDesc(self.field_code,
                                 self.column,
                                 self.field_title, ValueType.STRING,
                                 limit_output_char_num=self.column_output_char_limit,
                                 explicit_text_conversion=self.explicit_text_conversion)]

    def get_pg_index_definitions(self) -> Optional[List[str]]:
        return ['using GIN ("{column}" gin_trgm_ops)'.format(column=self.column)]

    def get_pg_column_definitions(self) -> Dict[str, PgTypes]:
        return {
            self.column: PgTypes.VARCHAR
        }

    def get_pg_sql_insert_clause(self, document_language: str, python_values: Dict[str, Any]) -> SQLInsertClause:
        python_value = python_values.get(self.field_code)
        db_value = self.python_value_to_indexed_field_value(python_value)
        return SQLInsertClause('"{column}"'.format(column=self.column), [], '%s', [db_value])

    def columns_to_field_value(self, columns: Dict[str, Any]) -> Any:
        return columns.get(self.column)

    def column_names_for_field_values(self) -> Set[str]:
        return {self.column}


class ComparableRawdbFieldHandler(RawdbFieldHandler):
    pg_type = None  # type: PgTypes

    def python_value_to_indexed_field_value(self, python_value) -> Any:
        pass

    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        pass

    def __init__(self,
                 field_code: str,
                 field_type: Optional[str],
                 field_title: Optional[str],
                 table_name: Optional[str],
                 default_value=None,
                 field_column_name_base: str = None) -> None:
        super().__init__(field_code, field_type, field_title,
                         table_name, default_value, field_column_name_base)
        self.column = escape_column_name(self.field_column_name_base)

    def get_pg_index_definitions(self) -> Optional[List[str]]:
        return None

    def get_pg_column_definitions(self) -> Dict[str, PgTypes]:
        return {
            self.column: self.pg_type
        }

    def get_pg_sql_insert_clause(self, document_language: str, python_values: Dict[str, Any]) -> SQLInsertClause:
        python_value = python_values.get(self.field_code)
        return SQLInsertClause('"{column}"'.format(column=self.column), [],
                               '%s', [self.python_value_to_indexed_field_value(python_value)])

    def columns_to_field_value(self, columns: Dict[str, Any]) -> Any:
        return columns.get(self.column)

    def column_names_for_field_values(self) -> Set[str]:
        return {self.column}


class IntFieldHandler(ComparableRawdbFieldHandler):
    pg_type = PgTypes.INTEGER

    def python_value_to_indexed_field_value(self, python_value) -> Any:
        if isinstance(python_value, (str, int, float, Decimal)):
            try:
                return int(python_value)
            except (ValueError, TypeError):
                pass
        return self.default_value

    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        return [IntColumnDesc(self.field_code, self.column, self.field_title)]


class FloatFieldHandler(ComparableRawdbFieldHandler):
    pg_type = PgTypes.NUMERIC_50_8

    def python_value_to_indexed_field_value(self, python_value) -> Any:
        if isinstance(python_value, Decimal):
            return python_value
        if isinstance(python_value, (str, int, float)):
            try:
                return Decimal(str(python_value))
            except (ValueError, TypeError):
                pass
        return self.default_value

    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        return [FloatColumnDesc(self.field_code, self.column, self.field_title)]


class PercentFieldHandler(FloatFieldHandler):
    pg_type = PgTypes.NUMERIC_50_8


class DateFieldHandler(ComparableRawdbFieldHandler):
    pg_type = PgTypes.DATE

    def __init__(self,
                 field_code: str,
                 field_type: str,
                 field_title: str,
                 table_name: str,
                 default_value=None,
                 field_column_name_base: str = None) -> None:
        super().__init__(field_code, field_type, field_title, table_name,
                         parse_date(default_value) if default_value else None,
                         field_column_name_base)

    def python_value_to_indexed_field_value(self, python_value) -> Any:
        python_value = python_value or self.default_value
        return python_value if isinstance(python_value, datetime.date) \
            else python_value.date() if isinstance(python_value, datetime.datetime) \
            else None

    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        return [DateColumnDesc(self.field_code, self.column, self.field_title)]


class DateTimeFieldHandler(ComparableRawdbFieldHandler):
    pg_type = PgTypes.TIMESTAMP_WITH_TIMEZONE

    def __init__(self,
                 field_code: str,
                 field_type: str,
                 field_title: str,
                 table_name: str,
                 default_value=None,
                 field_column_name_base: str = None) -> None:
        super().__init__(field_code, field_type, field_title, table_name,
                         parse_date(default_value) if default_value else None,
                         field_column_name_base)

    def python_value_to_indexed_field_value(self, python_value) -> Any:
        python_value = python_value or self.default_value
        return python_value if isinstance(python_value, (datetime.date, datetime.datetime)) else None

    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        return [DateTimeColumnDesc(self.field_code, self.column, self.field_title)]


class MoneyRawdbFieldHandler(RawdbFieldHandler):
    def __init__(self,
                 field_code: str,
                 field_type: str,
                 field_title: str,
                 table_name: str,
                 default_value=None,
                 field_column_name_base: str = None) -> None:
        super().__init__(field_code, field_type, field_title, table_name, default_value, field_column_name_base)
        self.currency_column = escape_column_name(self.field_column_name_base + '_cur')
        self.amount_column = escape_column_name(self.field_column_name_base + '_amt')

    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        return [
            StringColumnDesc(self.field_code, self.currency_column, self.field_title + ': Currency', ValueType.STRING),
            FloatColumnDesc(self.field_code, self.amount_column, self.field_title + ': Amount')]

    def get_pg_column_definitions(self) -> Dict[str, PgTypes]:
        return {
            self.currency_column: PgTypes.VARCHAR,
            self.amount_column: PgTypes.NUMERIC_50_6
        }

    def python_value_to_indexed_field_value(self, dfv_python_value) -> Any:
        return dfv_python_value or self.default_value

    def get_pg_sql_insert_clause(self, document_language: str, python_values: Dict[str, Any]) -> SQLInsertClause:
        python_value = python_values.get(self.field_code)
        money = self.python_value_to_indexed_field_value(python_value)  # Dict
        currency = money.get('currency') if money else None
        amount = money.get('amount') if money else None
        return SQLInsertClause('"{currency_column}", '
                               '"{amount_column}"'.format(currency_column=self.currency_column,
                                                          amount_column=self.amount_column), [],
                               '%s, %s', [currency, amount])

    def columns_to_field_value(self, columns: Dict[str, Any]) -> Any:
        currency = columns.get(self.currency_column)
        amount = columns.get(self.amount_column)
        if amount is None and currency is None:
            return None
        return {
            'currency': currency,
            'amount': amount
        }

    def column_names_for_field_values(self) -> Set[str]:
        return {self.currency_column, self.amount_column}

    def get_pg_index_definitions(self) -> Optional[List[str]]:
        return []


class RatioRawdbFieldHandler(RawdbFieldHandler):
    def __init__(self,
                 field_code: str,
                 field_type: str,
                 field_title: str,
                 table_name: str,
                 default_value=None,
                 field_column_name_base: str = None) -> None:
        super().__init__(field_code, field_type, field_title, table_name, default_value, field_column_name_base)
        self.numerator = escape_column_name(self.field_column_name_base + '_num')
        self.denominator = escape_column_name(self.field_column_name_base + '_den')

    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        return [RatioColumnDesc(self.field_code, f'{self.field_column_name_base}_num_den',
                                self.field_title + ': Numerator/Denominator')]

    def get_pg_column_definitions(self) -> Dict[str, PgTypes]:
        return {
            self.numerator: PgTypes.NUMERIC_50_4,
            self.denominator: PgTypes.NUMERIC_50_4
        }

    def python_value_to_indexed_field_value(self, dfv_python_value) -> Any:
        return dfv_python_value or self.default_value

    def get_pg_sql_insert_clause(self, document_language: str, python_values: Dict[str, Any]) -> SQLInsertClause:
        python_value = python_values.get(self.field_code)
        res = self.python_value_to_indexed_field_value(python_value)  # Dict
        numerator = res.get('numerator') if res else None
        denominator = res.get('denominator') if res else None
        return SQLInsertClause('"{numerator_column}", '
                               '"{denominator_column}"'.format(numerator_column=self.numerator,
                                                               denominator_column=self.denominator), [],
                               '%s, %s', [numerator, denominator])

    def columns_to_field_value(self, columns: Dict[str, Any]) -> Any:
        numerator = columns.get(self.numerator)
        denominator = columns.get(self.denominator)
        if denominator is None and numerator is None:
            return None
        return {
            'numerator': numerator,
            'denominator': denominator
        }

    def column_names_for_field_values(self) -> Set[str]:
        return {self.numerator, self.denominator}

    def get_pg_index_definitions(self) -> Optional[List[str]]:
        return []


class AddressFieldHandler(StringRawdbFieldHandler):
    def get_pg_sql_insert_clause(self, document_language: str, python_values: Dict[str, Any]) -> SQLInsertClause:
        python_value = python_values.get(self.field_code)
        address = self.python_value_to_indexed_field_value(python_value)  # type: Dict[str, Any]
        db_value = str(address.get('address') or '') if address else None
        return SQLInsertClause('"{column}"'.format(column=self.column), [], '%s', [db_value])

    def columns_to_field_value(self, columns: Dict[str, Any]) -> Any:
        s = columns.get(self.column)
        if s is None:
            return None
        return {
            'address': s
        }


class RelatedInfoRawdbFieldHandler(RawdbFieldHandler):
    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        return [RelatedInfoColumnDesc(self.field_code, self.column, self.field_title, self.text_column)]

    def __init__(self,
                 field_code: str,
                 field_type: str,
                 field_title: str,
                 table_name: str,
                 default_value=None,
                 field_column_name_base: str = None) -> None:
        super().__init__(field_code, field_type, field_title, table_name, default_value, field_column_name_base)
        self.column = escape_column_name(self.field_column_name_base)
        self.text_column = escape_column_name(self.field_column_name_base) + '_txt'

    def get_pg_index_definitions(self) -> Optional[List[str]]:
        return ['using GIN ("{column}" gin_trgm_ops)'.format(column=self.text_column)]

    def get_pg_column_definitions(self) -> Dict[str, PgTypes]:
        return {
            self.column: PgTypes.BOOLEAN,
            self.text_column: PgTypes.TEXT
        }

    def python_value_to_indexed_field_value(self, python_value) -> Any:
        return bool(python_value or self.default_value)

    def get_pg_sql_insert_clause(self, document_language: str, python_values: Dict[str, Any]) -> SQLInsertClause:
        python_value = python_values.get(self.field_code)
        yes_no = self.python_value_to_indexed_field_value(python_value)

        related_info_text = None
        if python_value:
            if hasattr(python_value, '__iter__'):
                related_info_text = '\n'.join([str(v) for v in python_value if v]) if python_value else None
            else:
                related_info_text = str(python_value)

        return SQLInsertClause('"{column}", "{text_column}"'.format(column=self.column, text_column=self.text_column),
                               [],
                               '%s, %s', [yes_no, related_info_text])

    def columns_to_field_value(self, columns: Dict[str, Any]) -> Any:
        return columns.get(self.column)

    def column_names_for_field_values(self) -> Set[str]:
        return {self.column}


class AnnotationTextFieldHandler(StringRawdbFieldHandler):

    def __init__(self,
                 field_code: str,
                 field_type: str,
                 field_title: str,
                 table_name: str,
                 default_value=None,
                 field_column_name_base: str = None) -> None:
        super().__init__(field_code, field_type, field_title, table_name, default_value, field_column_name_base)
        self.column = escape_column_name(self.field_column_name_base)
        self.is_annotation = True

    def get_pg_column_definitions(self) -> Dict[str, PgTypes]:
        return {self.column: PgTypes.TEXT}

    def get_pg_sql_insert_clause(self, document_language: str, python_values: Dict[str, Any]) -> SQLInsertClause:
        python_value = python_values.get(self.field_code)
        values = [i for i in python_value if i] if python_value else None
        db_value = '\n{}\n'.format('_' * 20).join(values) if values else None
        return SQLInsertClause('"{column}"'.format(column=self.column), [], '%s', [db_value])


class BooleanRawdbFieldHandler(RawdbFieldHandler):
    pg_type = PgTypes.BOOLEAN

    def python_value_to_indexed_field_value(self, python_value) -> Any:
        python_value = python_value if python_value is not None else self.default_value
        return bool(python_value) if python_value is not None else False

    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        return [BooleanColumnDesc(self.field_code, self.column, self.field_title)]

    def __init__(self,
                 field_code: str,
                 field_type: str,
                 field_title: str,
                 table_name: str,
                 default_value: bool = None,
                 field_column_name_base: str = None) -> None:
        super().__init__(field_code, field_type, field_title, table_name, default_value, field_column_name_base)
        self.column = escape_column_name(self.field_column_name_base)

    def get_pg_index_definitions(self) -> Optional[List[SQLClause]]:
        return None

    def get_pg_column_definitions(self) -> Dict[str, PgTypes]:
        return {
            self.column: self.pg_type
        }

    def get_pg_sql_insert_clause(self, document_language: str, python_values: Dict[str, Any]) -> SQLInsertClause:
        python_value = python_values.get(self.field_code)
        return SQLInsertClause('"{column}"'.format(column=self.column), [],
                               '%s', [self.python_value_to_indexed_field_value(python_value)])

    def columns_to_field_value(self, columns: Dict[str, Any]) -> Any:
        return columns.get(self.column)

    def column_names_for_field_values(self) -> Set[str]:
        return {self.column}


class MultichoiceFieldHandler(StringRawdbFieldHandler):
    def python_value_to_indexed_field_value(self, python_value) -> Any:
        if not python_value:
            if self.default_value and isinstance(self.default_value, str):
                return {self.default_value}
            return self.default_value
        return set(python_value)

    def get_pg_sql_insert_clause(self, document_language: str, python_values: Dict[str, Any]) -> SQLInsertClause:
        python_value = python_values.get(self.field_code)
        python_value = self.python_value_to_indexed_field_value(python_value)  # type: Set[str]
        db_value = ', '.join(sorted(python_value)) if python_value else None
        return SQLInsertClause('"{column}"'.format(column=self.column), [], '%s', [db_value])

    def columns_to_field_value(self, columns: Dict[str, Any]) -> Any:
        v = columns.get(self.column)  # type: str
        if not v:
            return None
        return set({vv.strip() for vv in v.split(',')})

    def column_names_for_field_values(self) -> Set[str]:
        return {self.column}


class LinkedDocumentsRawdbFieldHandler(RawdbFieldHandler):
    def __init__(self,
                 field_code: str,
                 field_type: str,
                 field_title: str,
                 table_name: str,
                 default_value=None,
                 field_column_name_base: str = None) -> None:
        super().__init__(field_code, field_type, field_title, table_name, default_value, field_column_name_base)
        self.document_ids_column = escape_column_name(self.field_column_name_base + '_ids')
        self.document_links_column = escape_column_name(self.field_column_name_base + '_lnks')

    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        return [
            StringColumnDesc(self.field_code, self.document_ids_column,
                             self.field_title + ': Ids', ValueType.STRING),
            StringColumnDesc(self.field_code, self.document_links_column, self.field_title + ': Links',
                             ValueType.STRING)]

    def get_pg_column_definitions(self) -> Dict[str, PgTypes]:
        return {
            self.document_ids_column: PgTypes.VARCHAR,
            self.document_links_column: PgTypes.VARCHAR,
        }

    def python_value_to_indexed_field_value(self, python_value) -> Any:
        if not python_value:
            return self.default_value

        return set(python_value)

    def get_pg_sql_insert_clause(self, document_language: str, python_values: Dict[str, Any]) -> SQLInsertClause:
        document_ids = python_values.get(self.field_code)
        document_ids = self.python_value_to_indexed_field_value(document_ids)  # type: Set[int]

        links = []  # List[Tuple[str, str]]

        if document_ids:
            for document_id, document_name, document_type_code, project_id \
                    in Document.all_objects \
                    .filter(pk__in=document_ids) \
                    .values_list('id', 'name', 'document_type__code', 'project_id') \
                    .order_by('id'):
                links.append((document_name, doc_editor_url(document_type_code, project_id, document_id)))

            links = ['<a href="{1}">{0}</a>'.format(doc_name, doc_id) for doc_name, doc_id in links]
            document_ids = [str(doc_id) for doc_id in document_ids]

        return SQLInsertClause('"{ids_column}", '
                               '"{links_column}"'.format(ids_column=self.document_ids_column,
                                                         links_column=self.document_links_column), [],
                               '%s, %s', [', '.join(document_ids) if document_ids else None,
                                          '\n'.join(links) if links else None])

    def columns_to_field_value(self, columns: Dict[str, Any]) -> Any:
        v = columns.get(self.document_ids_column)  # type: str
        if not v:
            return None
        return set({int(vv.strip()) for vv in v.split(',')})

    def get_pg_index_definitions(self) -> Optional[List[str]]:
        return [
            'using GIN ("{column}" gin_trgm_ops)'.format(column=self.document_ids_column),
            'using GIN ("{column}" gin_trgm_ops)'.format(column=self.document_links_column)
        ]

    def column_names_for_field_values(self) -> Set[str]:
        return {self.document_ids_column}


class ProxyColumnDesc(StringColumnDesc):

    def __init__(self, *args, **kwargs) -> None:
        self.proxy_sql_spec = kwargs.pop('proxy_sql_spec')
        super().__init__(*args, **kwargs)

    def get_output_column_sql_spec(self) -> str:
        return f'{self.proxy_sql_spec} as "{self.name}"'

    def get_where_sql_clause(self, field_filter: str) -> Optional[SQLClause]:
        column = f'({self.proxy_sql_spec})::text' if self.explicit_text_conversion is True \
            else f'{self.proxy_sql_spec}'
        if not field_filter:
            return SQLClause('{column} is Null'.format(column=column), [])
        if field_filter == '*':
            return SQLClause('{column} is not Null'.format(column=column), [])
        if field_filter.startswith('!'):
            return SQLClause('{column} not ilike %s'.format(column=column), ['%' + field_filter[1:] + '%'])
        return SQLClause('{column} ilike %s'.format(column=column), ['%' + field_filter + '%'])


class ProxyFieldHandler(StringRawdbFieldHandler):
    def __init__(self, *args, **kwargs):
        self.proxy_sql_spec = kwargs.pop('proxy_sql_spec')
        super().__init__(*args, **kwargs)

    def get_pg_sql_insert_clause(self, *args, **kwargs):
        pass

    def get_client_column_descriptions(self) -> List[ColumnDesc]:
        return [ProxyColumnDesc(self.field_code,
                                self.column,
                                self.field_title, ValueType.STRING,
                                limit_output_char_num=self.column_output_char_limit,
                                explicit_text_conversion=self.explicit_text_conversion,
                                proxy_sql_spec=self.proxy_sql_spec)]
