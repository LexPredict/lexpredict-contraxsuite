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

import hashlib
import time
import traceback
from typing import List, Dict, Optional, Tuple, Any, Generator, Set, Callable

from django.conf import settings
from django.db import connection, transaction, IntegrityError
from django.db.models import Q

from apps.common.log_utils import ProcessLogger
from apps.common.sql_commons import fetch_int, escape_column_name, sum_list, SQLClause, \
    SQLInsertClause, join_clauses, format_clause, fetch_dicts
from apps.document import field_types
from apps.document.constants import DOCUMENT_FIELD_CODE_MAX_LEN, DocumentGenericField, DocumentSystemField, FieldSpec, \
    DOC_METADATA_DOCUMENT_CLASS_PROB
from apps.document.document_class import DocumentClass
from apps.document.models import DocumentType, Document, DocumentField, FieldAnnotation
from apps.extract.models import DefinitionUsage, GeoEntityUsage, CurrencyUsage
from apps.rawdb.constants import TABLE_NAME_PREFIX, FIELD_CODE_DOC_NAME, FIELD_CODE_DOC_TITLE, \
    FIELD_CODE_DOC_LANGUAGE, FIELD_CODE_DOC_PROCESSED, \
    FIELD_CODE_DOC_FULL_TEXT_LENGTH, FIELD_CODE_DOC_ID, FIELD_CODE_CREATE_DATE, FIELD_CODE_IS_REVIEWED, \
    FIELD_CODE_IS_COMPLETED, FIELD_CODE_PROJECT_ID, FIELD_CODE_PROJECT_NAME, FIELD_CODE_ASSIGNEE_ID, \
    FIELD_CODE_ASSIGNEE_NAME, FIELD_CODE_ASSIGN_DATE, FIELD_CODE_STATUS_NAME, FIELD_CODE_DELETE_PENDING, \
    FIELD_CODE_NOTES, FIELD_CODE_DEFINITIONS, FIELD_CODE_HIDDEN_COLUMNS, FIELD_CODE_CLUSTER_ID, FIELD_CODE_PARTIES, \
    FIELD_CODE_EARLIEST_DATE, FIELD_CODE_LATEST_DATE, FIELD_CODE_LARGEST_CURRENCY, FIELD_CODES_SYSTEM, \
    FIELD_CODES_GENERIC, FIELD_CODE_ANNOTATION_SUFFIX, INDEX_NAME_PREFIX, DEFAULT_ORDER_BY, FIELD_CODE_FOLDER, \
    CACHE_FIELD_TO_DOC_FIELD, FIELD_CODE_DOCUMENT_CLASS, FIELD_CODE_DOCUMENT_CLASS_PROB, FIELD_CODE_IS_CONTRACT, \
    FIELD_CODE_GEOGRAPHIES, FIELD_CODE_CURRENCY_TYPES
from apps.common.error_explorer import retry_for_operational_error
from apps.rawdb.models import SavedFilter
from apps.rawdb.notifications import UserNotifications
from apps.rawdb.rawdb.rawdb_field_handlers import PgTypes, RawdbFieldHandler, ColumnDesc, StringRawdbFieldHandler, \
    AnnotationTextFieldHandler, MoneyRawdbFieldHandler, DateFieldHandler, IntFieldHandler, BooleanRawdbFieldHandler, \
    DateTimeFieldHandler, LongTextFromRelTableFieldHandler, LinkedDocumentsRawdbFieldHandler, RatioRawdbFieldHandler, \
    FloatFieldHandler, MultichoiceFieldHandler, RelatedInfoRawdbFieldHandler, AddressFieldHandler, PercentFieldHandler
from apps.rawdb.rawdb.errors import Forbidden, UnknownColumnError
from apps.rawdb.rawdb.query_parsing import SortDirection, parse_column_filters, parse_order_by
from apps.rawdb.repository.raw_db_repository import RawDbRepository, doc_fields_table_name
from apps.rawdb.signals import fire_document_fields_changed, DocumentEvent
from apps.task.utils.logger import get_django_logger
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# method return types
class DocumentQueryResults(list):
    def __init__(self,
                 offset: Optional[int],
                 limit: Optional[int],
                 total_sql: Optional[SQLClause],
                 reviewed_sql: Optional[SQLClause],
                 columns: List[ColumnDesc],
                 items_sql: Optional[SQLClause],
                 row_processor: Callable[[List], List] = None) -> None:
        super().__init__()
        self.offset = offset
        self.limit = limit
        self.columns = columns
        self.documents_cache = None
        self._items_sql = items_sql
        self.reviewed = None
        self.total = None
        self.row_processor = row_processor
        if total_sql or reviewed_sql:
            with connection.cursor() as cursor:
                self.reviewed = fetch_int(cursor, reviewed_sql) if reviewed_sql else None
                self.total = fetch_int(cursor, total_sql) if total_sql else None

    @property
    def column_codes(self) -> List[str]:
        return [c.name for c in self.columns]

    @property
    def column_titles(self):
        return [c.title for c in self.columns]

    def fetch(self) -> Generator[List, None, None]:
        if self._items_sql:
            with connection.cursor() as cursor:
                cursor.execute(self._items_sql.sql, self._items_sql.params)
                rows = cursor.fetchmany(100)
                while rows:
                    for row in rows:
                        yield self.row_processor(row) if self.row_processor else row
                    rows = cursor.fetchmany(100)

    def fetch_dicts(self) -> Generator[Dict, None, None]:
        for row in self.fetch():
            yield dict(zip(self.column_codes, row))

    @property
    def documents(self):
        if self.documents_cache is None:
            self.documents_cache = list(self.fetch_dicts() or [])
        return self.documents_cache

    def __iter__(self):
        return self.fetch_dicts()

    def __len__(self) -> int:
        return 1


class EmptyDocumentQueryResults(DocumentQueryResults):
    def __init__(self) -> None:
        super().__init__(None, None, None, None, list(), None)

    def __iter__(self):
        return None

    def __len__(self) -> int:
        return 0

    def fetch_dicts(self) -> Generator[Dict, None, None]:
        return None

    @property
    def documents(self):
        return list()

    def fetch(self) -> Generator[List, None, None]:
        return None


RAWDB_FIELD_HANDLER_REGISTRY = {
    field_types.StringField.type_code: StringRawdbFieldHandler,
    field_types.StringFieldWholeValueAsAToken.type_code: StringRawdbFieldHandler,
    field_types.LongTextField.type_code: StringRawdbFieldHandler,
    field_types.IntField.type_code: IntFieldHandler,
    field_types.FloatField.type_code: FloatFieldHandler,
    field_types.DateTimeField.type_code: DateTimeFieldHandler,
    field_types.DateField.type_code: DateFieldHandler,
    field_types.RecurringDateField.type_code: DateFieldHandler,
    field_types.CompanyField.type_code: StringRawdbFieldHandler,
    field_types.DurationField.type_code: FloatFieldHandler,
    field_types.PercentField.type_code: PercentFieldHandler,
    field_types.AddressField.type_code: AddressFieldHandler,
    field_types.RelatedInfoField.type_code: RelatedInfoRawdbFieldHandler,
    field_types.ChoiceField.type_code: StringRawdbFieldHandler,
    field_types.MultiChoiceField.type_code: MultichoiceFieldHandler,
    field_types.PersonField.type_code: StringRawdbFieldHandler,
    field_types.AmountField.type_code: FloatFieldHandler,
    field_types.MoneyField.type_code: MoneyRawdbFieldHandler,
    field_types.RatioField.type_code: RatioRawdbFieldHandler,
    field_types.GeographyField.type_code: StringRawdbFieldHandler,
    field_types.BooleanField.type_code: BooleanRawdbFieldHandler,
    field_types.LinkedDocumentsField.type_code: LinkedDocumentsRawdbFieldHandler
}


# Generic Fields - should match keys from the output of field_value_cache.get_generic_values(doc)


def _build_system_field_handlers(table_name: str,
                                 include_system_fields: FieldSpec = True,
                                 is_select: bool = False) \
        -> List[RawdbFieldHandler]:
    res = list()

    # Create String handler to use LIKE operator over document id column for Select clauses
    if is_select:
        id_handler = StringRawdbFieldHandler(
            FIELD_CODE_DOC_ID,
            field_types.StringField.type_code, 'Document Id', table_name,
            explicit_text_conversion=True)
    else:
        id_handler = IntFieldHandler(
            FIELD_CODE_DOC_ID,
            field_types.IntField.type_code, 'Document Id', table_name)
        id_handler.pg_type = PgTypes.INTEGER_PRIMARY_KEY
    res.append(id_handler)

    if not include_system_fields:
        return res

    if include_system_fields is True:
        res.append(
            StringRawdbFieldHandler(FIELD_CODE_DOC_NAME, field_types.StringFieldWholeValueAsAToken.type_code,
                                    'Name', table_name))
        res.append(StringRawdbFieldHandler(FIELD_CODE_DOC_TITLE, field_types.StringField.type_code,
                                           'Title', table_name))
        res.append(StringRawdbFieldHandler(FIELD_CODE_DOC_LANGUAGE, field_types.StringField.type_code,
                                           'Language', table_name))

        lim = int(settings.RAW_DB_FULL_TEXT_SEARCH_CUT_ABOVE_TEXT_LENGTH)
        res.append(IntFieldHandler(FIELD_CODE_DOC_FULL_TEXT_LENGTH, field_types.IntField.type_code,
                                   'Text Length', table_name))
        res.append(DateTimeFieldHandler(FIELD_CODE_CREATE_DATE, field_types.DateTimeField.type_code,
                                        'Load Date', table_name))

        # append common fields for all types
        res.append(StringRawdbFieldHandler(FIELD_CODE_PARTIES, field_types.StringField.type_code,
                                           'Parties', table_name))
        res.append(DateFieldHandler(FIELD_CODE_EARLIEST_DATE, field_types.DateField.type_code,
                                    'Earliest Date', table_name))
        res.append(DateFieldHandler(FIELD_CODE_LATEST_DATE, field_types.DateField.type_code,
                                    'Latest Date', table_name))
        res.append(MoneyRawdbFieldHandler(FIELD_CODE_LARGEST_CURRENCY, field_types.MoneyField.type_code,
                                          'Largest Currency', table_name))
        res.append(StringRawdbFieldHandler(FIELD_CODE_DEFINITIONS, field_types.StringField.type_code,
                                           'Definitions', table_name))
        res.append(StringRawdbFieldHandler(FIELD_CODE_GEOGRAPHIES, field_types.StringField.type_code,
                                           'Geographies', table_name))
        res.append(StringRawdbFieldHandler(FIELD_CODE_CURRENCY_TYPES, field_types.StringField.type_code,
                                           'Currency Types', table_name))
        res.append(StringRawdbFieldHandler(FIELD_CODE_DOCUMENT_CLASS, field_types.StringField.type_code,
                                           'Document Class', table_name))
        res.append(StringRawdbFieldHandler(FIELD_CODE_DOCUMENT_CLASS_PROB, field_types.StringField.type_code,
                                           'Document Class Vector', table_name))
        res.append(BooleanRawdbFieldHandler(FIELD_CODE_IS_CONTRACT, field_types.BooleanField.type_code,
                                            'Is Contract', table_name))

    if DocumentSystemField.processed.specified_in(include_system_fields):
        res.append(BooleanRawdbFieldHandler(FIELD_CODE_DOC_PROCESSED, field_types.BooleanField.type_code,
                                            'Processed', table_name))

    if DocumentSystemField.project.specified_in(include_system_fields):
        res.append(IntFieldHandler(FIELD_CODE_PROJECT_ID, field_types.IntField.type_code,
                                   'Project Id', table_name))
        res.append(StringRawdbFieldHandler(FIELD_CODE_PROJECT_NAME, field_types.StringField.type_code,
                                           'Project', table_name))

    if DocumentSystemField.assignee.specified_in(include_system_fields):
        res.append(IntFieldHandler(FIELD_CODE_ASSIGNEE_ID, field_types.IntField.type_code,
                                   'Assignee Id', table_name))
        res.append(StringRawdbFieldHandler(FIELD_CODE_ASSIGNEE_NAME, field_types.StringField.type_code,
                                           'Assignee', table_name))
        res.append(DateTimeFieldHandler(FIELD_CODE_ASSIGN_DATE, field_types.DateTimeField.type_code,
                                        'Assign Date', table_name))

    if DocumentSystemField.status.specified_in(include_system_fields):
        res.append(
            StringRawdbFieldHandler(FIELD_CODE_STATUS_NAME, field_types.StringFieldWholeValueAsAToken.type_code,
                                    'Status', table_name))
        res.append(BooleanRawdbFieldHandler(FIELD_CODE_IS_REVIEWED, field_types.BooleanField.type_code,
                                            'Reviewed', table_name))
        res.append(BooleanRawdbFieldHandler(FIELD_CODE_IS_COMPLETED, field_types.BooleanField.type_code,
                                            'Completed', table_name))
    if DocumentSystemField.delete_pending.specified_in(include_system_fields):
        res.append(BooleanRawdbFieldHandler(FIELD_CODE_DELETE_PENDING, field_types.BooleanField.type_code,
                                            'Delete Pending', table_name))

    if DocumentSystemField.notes.specified_in(include_system_fields):
        res.append(StringRawdbFieldHandler(FIELD_CODE_NOTES, field_types.StringField.type_code,
                                           'Notes', table_name))

    if DocumentSystemField.folder.specified_in(include_system_fields):
        res.append(StringRawdbFieldHandler(FIELD_CODE_FOLDER, field_types.StringField.type_code,
                                           'Folder', table_name))

    return res


def _build_generic_field_handlers(table_name: str,
                                  include_generic_fields: FieldSpec = True) \
        -> List[RawdbFieldHandler]:
    res = list()

    if not include_generic_fields:
        return res

    if DocumentGenericField.cluster_id.specified_in(include_generic_fields):
        res.append(IntFieldHandler(FIELD_CODE_CLUSTER_ID, field_types.IntField.type_code,
                                   'Cluster Id', table_name))
    return res


def build_field_handlers(document_type: DocumentType, table_name: str = None,
                         include_system_fields: FieldSpec = True,
                         include_generic_fields: FieldSpec = True,
                         include_user_fields: FieldSpec = True,
                         include_annotation_fields: bool = True,
                         exclude_hidden_always_fields: bool = False,
                         is_select: bool = False) \
        -> List[RawdbFieldHandler]:
    res = list()  # type: List[RawdbFieldHandler]

    if not table_name:
        table_name = doc_fields_table_name(document_type.code)

    res.extend(_build_system_field_handlers(table_name,
                                            include_system_fields=include_system_fields,
                                            is_select=is_select))

    if include_generic_fields:
        res.extend(_build_generic_field_handlers(table_name, include_generic_fields=include_generic_fields))

    # Prevent repeating column names.
    # Lets assume generic field codes are unique as well as system field codes.
    # Assigning 1 to their usage count for further taking it into account when building
    # column name bases for the user fields.
    field_code_use_counts = {field_handler.field_column_name_base: 1 for field_handler in res}

    if include_user_fields:
        doc_field_qr = DocumentField.objects.filter(document_type=document_type)
        if isinstance(include_user_fields, set) or isinstance(include_user_fields, list):
            doc_field_qr = doc_field_qr.filter(code__in=include_user_fields)

        if exclude_hidden_always_fields:
            doc_field_qr = doc_field_qr.filter(hidden_always=False)

        for field in doc_field_qr.order_by('order', 'code'):  # type: DocumentField
            typed_field = field_types.TypedField.by(field)  # type: field_types.TypedField

            # Escape field code and take max N chars for using as the column name base
            field_code_escaped = escape_column_name(field.code)[:DOCUMENT_FIELD_CODE_MAX_LEN]

            # If we already have this escaped field code in the dict then
            # attach an index to it to avoid repeating of the column names.
            field_code_use_count = field_code_use_counts.get(field_code_escaped)
            if field_code_use_count is not None:
                field_code_use_counts[field_code_escaped] = field_code_use_count + 1
                counter_str = str(field_code_use_count)

                # make next repeated column name to be column1, column2, ...
                # make it fitting into N chars by cutting the field code
                # on the required number of chars to fit the num
                field_code_escaped = '{}_{}'.format(
                    field_code_escaped[:DOCUMENT_FIELD_CODE_MAX_LEN - len(counter_str) - 1],
                    counter_str)
            else:
                field_code_use_counts[field_code_escaped] = 1

            rawdb_field_handler_class = RAWDB_FIELD_HANDLER_REGISTRY[typed_field.type_code]
            rawdb_field_handler = rawdb_field_handler_class(
                field.code,
                typed_field.type_code,
                field.title,
                table_name,
                field.default_value,
                field_column_name_base=field_code_escaped)
            res.append(rawdb_field_handler)
            if include_annotation_fields:
                field_code_ann = field.code + FIELD_CODE_ANNOTATION_SUFFIX
                field_handler_ann = AnnotationTextFieldHandler(
                    field_code_ann,
                    typed_field.type_code,
                    field.title + ': Annotations',
                    table_name,
                    None,
                    field_column_name_base=field_code_escaped + FIELD_CODE_ANNOTATION_SUFFIX)
                res.append(field_handler_ann)

    return res


def table_exists(table_name: str) -> bool:
    sql = '''SELECT EXISTS (
               SELECT 1
               FROM   information_schema.tables
               WHERE  table_name = %s
               )'''
    with connection.cursor() as cursor:
        cursor.execute(sql, [table_name])
        res = cursor.fetchone()
        return res[0]


def get_table_columns_from_pg(cursor, table_name: str) -> Dict[str, str]:
    cursor.execute('select f.attname, pg_catalog.format_type(f.atttypid,f.atttypmod) AS type,\n'
                   '(select string_agg(p.contype, \'\') from pg_constraint p '
                   'where p.conrelid = c.oid and f.attnum = ANY (p.conkey)) as constr\n'
                   'from pg_attribute f\n'
                   'join pg_class c on c.oid = f.attrelid\n'
                   'where c.relname = %s and f.attnum > 0 and f.atttypid != 0', [table_name])
    return {column_name: column_type + (' primary key' if constr and 'p' in constr else '')
            for column_name, column_type, constr in cursor.fetchall()}


def build_index_name(table_name: str, index_definition: str) -> str:
    """
    Return a hash sum of the provided index definition as the index name.
    Postgres stores index definitions in the form of "CRETE INDEX..." queries which are pre-processed by its parser
    and which differ from the original queries used for creating the indexes. So there is no simple way to compare
    the index definitions. To avoid query parsing we use index names calculated as hash sums of the original
    index definitions. This way we can answer the question - if our index exists and if it has the same definition as
    we expect.
    :param table_name
    :param index_definition:
    :return:
    """
    index_identity = table_name + '_' + index_definition
    sha = hashlib.sha1(index_identity.encode('utf-8')).hexdigest()
    return INDEX_NAME_PREFIX + sha


def _build_create_index_statement(table_name: str, index_name: str, index_definition: str) -> str:
    return 'create index concurrently "{index_name}" on "{table_name}" {index_def}'.format(index_name=index_name,
                                                                                           table_name=table_name,
                                                                                           index_def=index_definition)


def get_table_index_names_from_pg(cursor, table_name: str) -> Set[str]:
    cursor.execute('select indexname from pg_indexes where tablename = %s', [table_name])
    res = {index_name[0] for index_name in cursor.fetchall()}  # type: Set[str]
    return {n for n in res if n.startswith(INDEX_NAME_PREFIX)}


def cleanup_saved_filters(document_type: DocumentType, should_be_column_names: Set[str]):
    for f in SavedFilter.objects.filter(document_type=document_type):
        save = False
        if f.columns and type(f.columns) is list:
            new_columns = [c for c in f.columns if c in should_be_column_names]
            if new_columns != f.columns:
                f.columns = new_columns
                save = True
        if f.column_filters and type(f.column_filters) is dict:
            new_column_filters = {c: ff for c, ff in f.column_filters.items() if c in should_be_column_names}
            if new_column_filters != f.column_filters:
                f.column_filters = new_column_filters
                save = True
        if f.order_by:
            new_order_by = list()  # type: List[Tuple[str, SortDirection]]
            if type(f.order_by) is list:
                for order_by_item in f.order_by:
                    try:
                        order_by_item_parsed = parse_order_by(order_by_item)
                        if order_by_item_parsed:
                            for column, sort_direction in list(order_by_item_parsed):
                                if column in should_be_column_names:
                                    new_order_by.append((column, sort_direction))
                    except:
                        pass
            elif type(f.order_by) is str:
                try:
                    order_by_item_parsed = parse_order_by(str(f.order_by))
                    if order_by_item_parsed:
                        for column, sort_direction in list(order_by_item_parsed):
                            if column in should_be_column_names:
                                new_order_by.append((column, sort_direction))
                except:
                    pass
            new_order_by = ['{c}:{sd}'.format(c=c, sd=sd) for c, sd in new_order_by] if new_order_by else None
            if new_order_by != f.order_by:
                f.order_by = new_order_by
                save = True
        if save:
            f.save()


@retry_for_operational_error(retries_count=2, cooldown_interval=2.0)
def adapt_table_structure(log: ProcessLogger,
                          document_type: DocumentType,
                          force: bool = False,
                          check_only: bool = False) -> bool:
    """
    Create or alter raw db table for it to match the field structure of the specified document type.
    :param log:
    :param document_type:
    :param force: Force re-creating the table.
    :param check_only Do not really alter the table but only check if the re-indexing will be required.
    :return: True/False - if any column has been added/removed/altered and re-index is required for this doc type.
    """
    table_name = doc_fields_table_name(document_type.code)

    fields = build_field_handlers(document_type, table_name)
    should_be_columns = dict()  # type: Dict[str, str]
    should_be_indexes = dict()  # type: Dict[str, str]
    for field_handler in fields:
        field_columns = field_handler.get_pg_column_definitions()  # type: Dict[str, PgTypes]
        should_be_columns.update({name: pg_type.value for name, pg_type in field_columns.items()})
        index_defs = field_handler.get_pg_index_definitions()
        if index_defs:
            should_be_indexes.update({build_index_name(table_name, index_def): index_def for index_def in index_defs})
    should_be_columns[FIELD_CODE_HIDDEN_COLUMNS] = PgTypes.STRING_ARRAY.value

    if not check_only and (force or not table_exists(table_name)):
        log_msg = 'force' if force else f'table "{table_name}" does not exist'
        log.info(f'adapt_table_structure({document_type.title}): {log_msg}')
        _recreate_document_fields_table(log, table_name, should_be_columns, should_be_indexes)
        cleanup_saved_filters(document_type, set(should_be_columns.keys()))
        return True

    dropped_columns = list()  # type: List[Tuple[str, str]]
    added_columns = list()  # type: List[Tuple[str, str]]

    with connection.cursor() as cursor:
        with transaction.atomic():
            existing_columns = get_table_columns_from_pg(cursor, table_name)  # type: Dict[str, str]

            alter_table_actions = list()  # type: List[str]

            for existing_name, existing_type in existing_columns.items():
                should_be_type = should_be_columns.get(existing_name)
                if not should_be_type or should_be_type != existing_type:
                    # column does not exist in "should_be_columns" or has different type
                    alter_table_actions.append('drop column "{column}"'.format(column=existing_name))
                    dropped_columns.append((existing_name, existing_type))

            for should_be_name, should_be_type in should_be_columns.items():
                existing_type = existing_columns.get(should_be_name)
                if not existing_type or existing_type != should_be_type:
                    # column does not exist in "existing_columns" or has
                    # different type (and has been dropped in prev loop)
                    alter_table_actions.append('add column "{column}" {pg_type}'
                                               .format(column=should_be_name, pg_type=should_be_type))
                    added_columns.append((should_be_name, should_be_type))

            if alter_table_actions:
                if not check_only:
                    alter_table_sql = 'alter table "{table_name}"\n{actions}' \
                        .format(table_name=table_name, actions=',\n'.join(alter_table_actions))
                    cursor.execute(alter_table_sql, [])
                    log.info('Altered table: {0}\nDropped columns:\n{1}\nAdded columns:\n{2}'
                             .format(table_name,
                                     '\n'.join([c + ': ' + t for c, t in dropped_columns]),
                                     '\n'.join([c + ': ' + t for c, t in added_columns])))
                    cleanup_saved_filters(document_type, set(should_be_columns.keys()))

        # actions of alter_table_actions that failed to execute
        actions_failed = 0
        if not check_only:
            # Changes in indexes do not require document re-indexing - the values will already be in the columns.
            existing_indexes = get_table_index_names_from_pg(cursor, table_name)  # type: Set[str]
            for existing_index_name in existing_indexes:
                if existing_index_name not in should_be_indexes:
                    cursor.execute('drop index concurrently "{index_name}"'.format(index_name=existing_index_name), [])

            for should_be_index_name, should_be_index_def in should_be_indexes.items():
                if should_be_index_name not in existing_indexes:
                    create_index_sql = _build_create_index_statement(table_name, should_be_index_name,
                                                                     should_be_index_def)
                    try:
                        cursor.execute(create_index_sql, [])
                    except Exception:
                        actions_failed += 1
                        src_error_txt = traceback.format_exc()
                        msg = 'adapt_table_structure: error creating index' + \
                              f' for {table_name}:{should_be_index_name},\n' + \
                              f'{should_be_index_def}.\nOriginal error: {src_error_txt}.'

                        if '"gin_trgm_ops"' in src_error_txt:
                            # not all the fields can be included in Trigram index
                            log.error(msg)
                        else:
                            raise RuntimeError(msg)

    actions_succeeded = len(alter_table_actions) - actions_failed
    return actions_succeeded > 0


def _recreate_document_fields_table(log: ProcessLogger, table_name: str, column_defs: Dict[str, str],
                                    index_defs: Dict[str, str]):
    log.info('Recreating raw sql table: {0}'.format(table_name))

    column_def_clauses = [SQLClause('"{column}" {pg_type}'.format(column=column, pg_type=pg_type))
                          for column, pg_type in column_defs.items()]

    create_table = format_clause('CREATE TABLE "{table_name}" (\n'
                                 '{columns}, \n'
                                 'FOREIGN KEY ({field_document_id}) '
                                 'REFERENCES document_document (id) ON DELETE CASCADE)',
                                 table_name=table_name,
                                 columns=join_clauses(', \n', column_def_clauses),
                                 field_document_id=FIELD_CODE_DOC_ID)  # type: SQLClause

    log.info('Create table SQL for table {0}:\n{1}\nParams: {2}'.format(table_name,
                                                                        create_table.sql,
                                                                        create_table.params))

    with connection.cursor() as cursor:
        cursor.execute('drop table if exists "{table_name}"'.format(table_name=table_name))
        cursor.execute(create_table.sql, create_table.params)
        for index_name, index_def in index_defs.items():  # type: str, str
            create_index = _build_create_index_statement(table_name, index_name, index_def)
            cursor.execute(create_index, [])


def _fill_system_fields_to_python_values(document: Document,
                                         field_to_python_values: Dict[str, List],
                                         include_system_fields: FieldSpec = True):
    field_to_python_values[FIELD_CODE_DOC_ID] = document.pk

    if not include_system_fields:
        return
    if isinstance(include_system_fields, list):
        include_system_fields = set(include_system_fields)

    if include_system_fields is True:
        field_to_python_values[FIELD_CODE_DOC_NAME] = document.name
        field_to_python_values[FIELD_CODE_DOC_TITLE] = document.title
        field_to_python_values[FIELD_CODE_DOC_LANGUAGE] = document.language
        field_to_python_values[FIELD_CODE_DOC_FULL_TEXT_LENGTH] = len(document.full_text) if document.full_text else 0

        field_to_python_values[FIELD_CODE_CREATE_DATE] = document.history.last().history_date \
            if document.history.exists() else document.upload_session.created_date \
            if document.upload_session else None

        if document.metadata:
            field_to_python_values[FIELD_CODE_IS_CONTRACT] = \
                document.document_class == DocumentClass.CONTRACT
            field_to_python_values[FIELD_CODE_DOCUMENT_CLASS] = \
                document.document_class or DocumentClass.GENERIC
            field_to_python_values[FIELD_CODE_DOCUMENT_CLASS_PROB] = \
                document.metadata.get(DOC_METADATA_DOCUMENT_CLASS_PROB) or [0]

        field_to_python_values[FIELD_CODE_DEFINITIONS] = '; '.join(
            DefinitionUsage.objects.filter(text_unit__document=document)
                .values_list('definition', flat=True)) or None
        field_to_python_values[FIELD_CODE_GEOGRAPHIES] = '; '.join(
            GeoEntityUsage.objects.filter(text_unit__document=document)
                .values_list('entity__name', flat=True).order_by('entity__name').distinct()) or None
        field_to_python_values[FIELD_CODE_CURRENCY_TYPES] = '; '.join(
            CurrencyUsage.objects.filter(text_unit__document=document)
                .values_list('currency', flat=True).order_by('currency').distinct()) or None

    if DocumentSystemField.processed.specified_in(include_system_fields):
        field_to_python_values[FIELD_CODE_DOC_PROCESSED] = document.processed

    if DocumentSystemField.status.specified_in(include_system_fields):
        field_to_python_values[FIELD_CODE_IS_REVIEWED] = document.is_reviewed()
        field_to_python_values[FIELD_CODE_IS_COMPLETED] = document.is_completed()
        field_to_python_values[FIELD_CODE_STATUS_NAME] = document.status.name if document.status else None

    if DocumentSystemField.assignee.specified_in(include_system_fields):
        field_to_python_values[FIELD_CODE_ASSIGNEE_ID] = document.assignee_id
        field_to_python_values[FIELD_CODE_ASSIGNEE_NAME] = document.assignee.get_full_name() \
            if document.assignee else None
        field_to_python_values[FIELD_CODE_ASSIGN_DATE] = document.assign_date

    if DocumentSystemField.delete_pending.specified_in(include_system_fields):
        field_to_python_values[FIELD_CODE_DELETE_PENDING] = document.delete_pending

    if DocumentSystemField.project.specified_in(include_system_fields):
        project = document.project
        field_to_python_values[FIELD_CODE_PROJECT_ID] = project.pk if project is not None else None
        field_to_python_values[FIELD_CODE_PROJECT_NAME] = project.name if project is not None else None

    if DocumentSystemField.notes.specified_in(include_system_fields):
        field_to_python_values[FIELD_CODE_NOTES] = '\n{}\n'.format('_' * 20).join(
            ['{user} {date} - {target} Level Note\n{note}'.format(
                user=n.history.last().history_user.get_full_name()
                if n.history.exists() and n.history.last().history_user else None,
                date=n.timestamp.strftime('%m-%d-%Y %I:%M %p %Z'),
                target='Text' if n.location_start is not None and n.location_end is not None else 'Document',
                note=n.note)
                for n in document.documentnote_set.all()]) or None

    if DocumentSystemField.folder.specified_in(include_system_fields):
        field_to_python_values[FIELD_CODE_FOLDER] = document.folder


def _fill_generic_fields_to_python_values(document: Document,
                                          field_to_python_values: Dict[str, List],
                                          generic_values_to_fill: FieldSpec = True):
    dal = RawDbRepository()
    generic_values = dal.get_generic_values(document, generic_values_to_fill)
    field_to_python_values.update(generic_values)


def _build_insert_clause(log: ProcessLogger,
                         table_name: str,
                         handlers: List[RawdbFieldHandler],
                         hidden_handlers: List[RawdbFieldHandler],
                         document: Document,
                         fields_to_python_values: Dict[str, Any],
                         hidden_field_codes: Set[str]) -> SQLClause:
    insert_clauses = list()

    fields_to_python_values = dict(fields_to_python_values)  # creating a copy to not modify the original one

    if hidden_field_codes is not None:
        hidden_columns = list()
        for h in hidden_handlers:
            if h.field_code and h.field_code in hidden_field_codes:
                cdefs = h.get_pg_column_definitions()
                if cdefs:
                    hidden_columns.extend(cdefs.keys())
                hidden_columns.append(h.field_code + FIELD_CODE_ANNOTATION_SUFFIX)
                fields_to_python_values[h.field_code] = None

        insert_clauses.append(SQLInsertClause(f'"{FIELD_CODE_HIDDEN_COLUMNS}"', [],
                                              '%s', [list(hidden_columns)]))

    for handler in handlers:  # type: FieldHandler
        try:
            insert_clause = handler.get_pg_sql_insert_clause(document.language,
                                                             fields_to_python_values)  # type: SQLInsertClause
            insert_clauses.append(insert_clause)
        except Exception as ex:
            log.error(f'Unable to cache field values.\n'
                      f'Document: {document.name} (#{document.pk}).\n'
                      f'Field: {handler.field_code}', exc_info=ex)

    columns_clause, values_clause = SQLInsertClause.join(insert_clauses)

    return format_clause('insert into "{table_name}" ({columns}) '
                         'values ({values}) on conflict ({column_document_id}) '
                         'do update set ({columns}) = ({values})',
                         table_name=table_name,
                         columns=columns_clause,
                         values=values_clause,
                         column_document_id=FIELD_CODE_DOC_ID)


def _delete_document_from_cache(cursor, document_id):
    sql = '''DO $$
DECLARE
    tables CURSOR FOR
        SELECT tablename
        FROM pg_tables
        WHERE tablename LIKE %s;
BEGIN
    FOR table_record IN tables LOOP
        EXECUTE 'DELETE FROM ' || table_record.tablename || ' WHERE document_id = %s';
    END LOOP;
END$$;'''
    cursor.execute(sql, [TABLE_NAME_PREFIX + '%', document_id])


def delete_document_from_cache(user: User, document: Document):
    document_type = document.document_type
    table_name = doc_fields_table_name(document.document_type.code)
    handlers = build_field_handlers(document_type, table_name)
    with connection.cursor() as cursor:
        document_fields_before = _get_document_fields(cursor=cursor,
                                                      document_id=document.pk,
                                                      table_name=table_name,
                                                      handlers=handlers)
        _delete_document_from_cache(cursor, document.pk)
        log = ProcessLogger()
        fire_document_fields_changed(cache_document_fields,
                                     log=log,
                                     document_event=DocumentEvent.DELETED.value,
                                     document_pk=document.pk,
                                     field_handlers={h.field_code: h for h in handlers},
                                     fields_before=document_fields_before, fields_after=None,
                                     changed_by_user=user)


def get_document_values_actual_and_cached(
        document: Document,
        skip_cached_values: bool = False,
        handlers: List[RawdbFieldHandler] = None,
        none_on_errors: bool = True):
    """
    Get fields either from document or, if it's not possible (cached fields are
    requested) from document + from RawDB
    :param document: document with all its fields
    :param skip_cached_values: get document values only
    :param handlers: RawdbFieldHandler collection or None for all handlers
    :param none_on_errors: return None values when error occured
    :return: {RawdbFieldHandler.field_code: field_value}
    """
    table_name = doc_fields_table_name(document.document_type.code)
    if not handlers:
        handlers = build_field_handlers(
            document.document_type, table_name, include_annotation_fields=False)

    raw_handlers = []
    doc_values = {}  # type: Dict[str, Any]
    for handler in handlers:
        if handler.field_code in CACHE_FIELD_TO_DOC_FIELD:
            doc_field = CACHE_FIELD_TO_DOC_FIELD[handler.field_code]
            doc_values[handler.field_code] = document.get_field_by_code(doc_field)
            continue
        raw_handlers.append(handler)

    if skip_cached_values:
        return doc_values

    if raw_handlers:
        with connection.cursor() as cursor:
            raw_values = _get_document_fields(
                document.pk, cursor=cursor, table_name=table_name,
                handlers=raw_handlers, none_on_errors=none_on_errors)
        if raw_values:
            doc_values.update(raw_values)
    return doc_values


def get_document_field_values(document_type: DocumentType,
                              document_id,
                              table_name: str = None,
                              handlers: List[RawdbFieldHandler] = None,
                              none_on_errors: bool = True) -> Optional[Dict[str, Any]]:
    with connection.cursor() as cursor:
        if not table_name:
            table_name = doc_fields_table_name(document_type.code)
        if not handlers:
            handlers = build_field_handlers(document_type, table_name, include_annotation_fields=False)
        return _get_document_fields(document_id, cursor=cursor, table_name=table_name, handlers=handlers,
                                    none_on_errors=none_on_errors)


def _get_document_fields(document_id,
                         cursor,
                         table_name: str,
                         handlers: List[RawdbFieldHandler],
                         none_on_errors: bool = True) -> Optional[Dict[str, Any]]:
    column_names = list()  # type: List[str]
    for h in handlers:  # type: FieldHandler
        columns = h.get_client_column_descriptions()  # type: List[ColumnDesc]
        for c in columns:  # type: ColumnDesc
            column_names.append(c.name)

    sql_columns = ', \n'.join(['"{column}"'.format(column=column) for column in column_names])

    sql = SQLClause('''select {columns} from {table_name} where document_id = %s limit 1'''
                    .format(columns=sql_columns, table_name=table_name), [document_id])

    for d in fetch_dicts(cursor, sql, column_names):
        res = dict()
        for h in handlers:
            try:
                fv = h.columns_to_field_value(d)
            except Exception as e:
                if not none_on_errors:
                    raise e
                fv = None
            res[h.field_code] = fv
        return res

    return None


def clear_user_fields_no_events(document: Document,
                                user_fields: FieldSpec = True):
    document_type = document.document_type
    table_name = doc_fields_table_name(document_type.code)
    handlers = build_field_handlers(document_type,
                                    table_name,
                                    include_system_fields=False,
                                    include_generic_fields=False,
                                    include_user_fields=user_fields,
                                    include_annotation_fields=True)
    columns = set()
    for h in handlers:
        if h.field_code not in FIELD_CODES_SYSTEM and h.field_code not in FIELD_CODES_GENERIC:
            columns.update(h.get_pg_column_definitions().keys())

    if columns:
        columns_update = ',\n'.join([f'"{c}" = null' for c in columns])
        sql = f'update "{table_name}" set\n{columns_update}\nwhere "{FIELD_CODE_DOC_ID}" = %s'
        with connection.cursor() as cursor:
            cursor.execute(sql, [document.pk])


@retry_for_operational_error(retries_count=2, cooldown_interval=2.0)
def cache_document_fields(log: ProcessLogger,
                          document: Document,
                          cache_system_fields: FieldSpec = True,
                          cache_generic_fields: FieldSpec = True,
                          cache_user_fields: FieldSpec = True,
                          document_initial_load: bool = False,
                          changed_by_user: User = None,
                          old_field_values: Dict[str, Any] = None,
                          disable_notifications: bool = False):
    document_type = document.document_type
    table_name = doc_fields_table_name(document_type.code)

    handlers = build_field_handlers(document_type,
                                    table_name,
                                    include_system_fields=cache_system_fields,
                                    include_generic_fields=cache_generic_fields,
                                    include_user_fields=cache_user_fields,
                                    include_annotation_fields=True)
    system_field_handlers = list()  # type: List[RawdbFieldHandler]
    generic_field_handlers = list()  # type: List[RawdbFieldHandler]
    user_field_handlers = list()  # type: List[RawdbFieldHandler]
    user_field_annotations_handlers = list()

    for h in handlers:
        if h.field_code in FIELD_CODES_SYSTEM:
            system_field_handlers.append(h)
        elif h.field_code in FIELD_CODES_GENERIC:
            generic_field_handlers.append(h)
        elif h.field_code.endswith(FIELD_CODE_ANNOTATION_SUFFIX):
            user_field_annotations_handlers.append(h)
        else:
            user_field_handlers.append(h)

    insert_field_handlers = list()  # type: List[RawdbFieldHandler]
    field_to_python_values = dict()

    _fill_system_fields_to_python_values(document, field_to_python_values, cache_system_fields)
    insert_field_handlers += system_field_handlers

    if cache_generic_fields:
        _fill_generic_fields_to_python_values(document, field_to_python_values, cache_generic_fields)
        insert_field_handlers += generic_field_handlers

    hidden_field_codes = None  # None means no update

    hid_handlers = {}

    if cache_user_fields and user_field_handlers:
        insert_field_handlers += user_field_handlers
        insert_field_handlers += user_field_annotations_handlers
        from apps.document.repository.document_field_repository import DocumentFieldRepository
        field_repo = DocumentFieldRepository()

        user_fields_code_to_value = {code: None for code in
                                     document_type.fields.all().values_list('code', flat=True)}
        user_fields_code_to_value.update(field_repo.get_field_code_to_python_value(document_type_id=document_type.pk,
                                                                                   doc_id=document.pk))

        _hidden_field_ids, hidden_field_codes = field_repo.get_hidden_field_ids_codes(document,
                                                                                      user_fields_code_to_value)
        if hidden_field_codes:
            hid_handlers = build_field_handlers(document_type,
                                                table_name,
                                                include_system_fields=False,
                                                include_generic_fields=False,
                                                include_user_fields=list(hidden_field_codes),
                                                include_annotation_fields=True)

        field_to_python_values.update(user_fields_code_to_value)

        # now get field annotations only for those fields which we are really going to index
        field_codes = {h.field_code for h in user_field_handlers}
        for dfv in field_repo.get_docfield_ants_by_doc_and_code(document.pk,
                                                                field_codes=field_codes,
                                                                order_by_location=True):  # type: FieldAnnotation
            field_code = dfv.field.code + FIELD_CODE_ANNOTATION_SUFFIX
            field_to_python_values[field_code] = field_to_python_values.get(field_code, []) + [dfv.location_text]

    # do not do anything if finally there are no fields to cache
    # the single field handler - is document id
    if len(insert_field_handlers) == 1:
        return

    insert_clause = _build_insert_clause(log,
                                         table_name,
                                         insert_field_handlers,
                                         hid_handlers,
                                         document,
                                         field_to_python_values,
                                         hidden_field_codes=hidden_field_codes)

    with connection.cursor() as cursor:
        document_fields_before = _get_document_fields(cursor=cursor,
                                                      document_id=document.pk,
                                                      table_name=table_name,
                                                      handlers=handlers)
        if old_field_values:
            document_fields_before.update(old_field_values)
        try:
            cursor.execute(insert_clause.sql, insert_clause.params)
        except IntegrityError:
            # this error means that the document referred has been already deleted
            # in primary table (document_document) - so we can skip it
            er_str = f'is not present in table "{Document._meta.db_table}"'
            ex_str = traceback.format_exc()
            if er_str in ex_str:
                log.error(f'Document {document.pk} of {document_type} is '
                          f'deleted by the time it is being cached in cache_document_fields()')
                pass
        except:
            import sys
            etype, evalue, _ = sys.exc_info()
            log.error(f'Error {etype}: {evalue}\n'
                      f'in cache_document_fields(doc_id={document.pk})\nSQL: '
                      f'{insert_clause.sql}\nParams: {insert_clause.params}.\n\n')
            raise

    inserted_document_fields = {
        h.field_code: h.python_value_to_indexed_field_value(field_to_python_values.get(h.field_code))
        for h in insert_field_handlers}

    document_fields_after = dict(document_fields_before) if document_fields_before else dict()
    document_fields_after.update(inserted_document_fields)

    if document.processed and not disable_notifications:
        # send websocket notifications for the existing docs only
        # don't send on the docs being loaded to avoid excessive traffic/cpu usage

        attempts = 1    # number of attempts
        delay = 10    # delay in seconds for the first attempt
        multiplier = 1    # multiplier to increase time between further attempts

        for attempt_n in range(1, attempts + 1):
            try:
                UserNotifications.notify_user_on_document_values_changed(
                    document, document_fields_before, document_fields_after,
                    handlers, changed_by_user)
                break
            # case 1. when websocket channels cannot connect to redis. CS-5065
            except OSError:
                if attempt_n != attempts:
                    time.sleep(delay)
                    delay *= multiplier
                else:
                    src_error_txt = traceback.format_exc()
                    log.error('Failed to send notifications on document values changed. '
                              'Original exception is: {}'.format(src_error_txt))
    document.fields_dirty = None
    document.save(update_fields=['fields_dirty'])
    log.debug(f"Fields are cached for document {document.pk}",
              extra={Document.LOG_FIELD_DOC_ID: str(document.pk)})
    fire_document_fields_changed(cache_document_fields,
                                 log=log,
                                 document_event=DocumentEvent.CREATED.value if document_initial_load
                                 else DocumentEvent.CHANGED.value,
                                 document_pk=document.pk,
                                 field_handlers={h.field_code: h for h in handlers},
                                 fields_before=document_fields_before, fields_after=document_fields_after,
                                 changed_by_user=changed_by_user)


def _get_columns(handlers: List[RawdbFieldHandler]) -> List[ColumnDesc]:
    return sum_list([h.get_client_column_descriptions() for h in handlers])


def get_columns(document_type: DocumentType,
                include_annotations: bool = True,
                include_generic: FieldSpec = False) \
        -> List[ColumnDesc]:
    table_name = doc_fields_table_name(document_type.code)
    handlers = build_field_handlers(document_type,
                                    table_name,
                                    include_generic_fields=include_generic,
                                    include_annotation_fields=include_annotations,
                                    exclude_hidden_always_fields=True)
    return _get_columns(handlers)


def get_annotation_columns(document_type: DocumentType):
    return [i for i in get_columns(document_type, include_annotations=True)
            if i.field_code.endswith(FIELD_CODE_ANNOTATION_SUFFIX)]


def _prepare_project_ids_filter(requester: User, project_ids: List[int]) -> Optional[SQLClause]:
    if project_ids:
        project_ids = {int(project_id) for project_id in project_ids}

    # check for "project reviewers" logic
    if requester and requester.is_reviewer:
        allowed_project_ids = set(requester
                                  .project_reviewers.all()
                                  .union(requester.project_super_reviewers.all())
                                  .union(requester.project_owners.all())
                                  .values_list('pk', flat=True))
        project_ids = project_ids.intersection(allowed_project_ids) if project_ids else allowed_project_ids
        if not project_ids:
            # there are no allowed project ids or the requested project ids are not in the list of allowed
            raise Forbidden()

    if project_ids:
        # django uses "project_id in ARRAY(1, 2, ....)" instead of simply "project_id in (1, 2, ...)"
        # Postgresql throws an error on this.
        # Replacing with string manipulations.
        return SQLClause('"{project_id_column}" in ({values})'
                         .format(project_id_column=FIELD_CODE_PROJECT_ID,
                                 values=', '.join({str(project_id) for project_id in project_ids})))
    else:
        return None


def _extract_column_filters_and_order_by_from_saved_filters(document_type: DocumentType,
                                                            requester: User,
                                                            saved_filter_ids: List[int]) \
        -> Tuple[List[Tuple[str, str]], List[Tuple[str, SortDirection]]]:
    saved_filters = list(SavedFilter.objects
                         .filter(document_type=document_type)
                         .filter(pk__in=saved_filter_ids)
                         .filter(Q(user__isnull=True) | Q(user=requester))
                         .values_list('column_filters', 'order_by')
                         .all())  # type: List[Tuple[str, str]]
    if not saved_filters:
        raise Forbidden()
    column_filters = list()  # type: List[Tuple[str, str]]
    order_by = None  # type: List[Tuple[str, SortDirection]]

    for filter_json, order_by_json in saved_filters:
        if filter_json:
            column_filters.extend([(column, column_filter) for column, column_filter in filter_json.items()])

        if order_by_json and not order_by:
            if isinstance(order_by_json, str):
                order_by = parse_order_by(order_by_json)
            elif isinstance(order_by_json, list):
                order_by = list()
                for elem in order_by_json:
                    order_by_items = parse_order_by(elem)
                    if order_by_items:
                        order_by.extend(order_by_items)

    return column_filters, order_by


def query_documents(document_type: DocumentType,
                    requester: Optional[User] = None,
                    project_ids: Optional[List[int]] = None,
                    field_codes: Optional[List[str]] = None,
                    column_names: Optional[List[str]] = None,
                    column_filters: Optional[List[Tuple[str, str]]] = None,
                    filters_sql: Optional[SQLClause] = None,
                    saved_filter_ids: Optional[List[int]] = None,
                    order_by: Optional[List[Tuple[str, SortDirection]]] = None,
                    offset: int = None,
                    limit: int = None,
                    return_documents: bool = True,
                    return_total_count: bool = True,
                    return_reviewed_count: bool = False,
                    ignore_errors: bool = False,
                    include_annotation_fields: bool = False
                    ) -> Optional[DocumentQueryResults]:
    if not return_documents and not return_reviewed_count and not return_total_count:
        return None

    table_name = doc_fields_table_name(document_type.code)
    handlers = build_field_handlers(document_type=document_type,
                                    table_name=table_name,
                                    include_annotation_fields=include_annotation_fields,
                                    exclude_hidden_always_fields=True,
                                    is_select=True)  # type: List[RawdbFieldHandler]

    existing_columns = _get_columns(handlers)  # type: List[ColumnDesc]
    existing_column_name_to_desc = {column.name: column
                                    for column in
                                    existing_columns}  # type: Dict[str, ColumnDesc]
    existing_column_names = set(existing_column_name_to_desc.keys())
    field_codes_to_desc = {d.field_code: d for d in existing_columns}  # type: Dict[str, ColumnDesc]
    if return_documents or saved_filter_ids or column_filters:
        # build column handlers only if there can be filters on columns (saved filters or filters specified in request)
        # or if we are returning data which requires column names

        # filter requested column names to have only the existing ones
        if column_names:
            column_names = [column for column in column_names if column in existing_column_names]  # type: List[str]
        elif field_codes:
            column_names = [field_codes_to_desc[fc].name for fc in field_codes]  # type: List[str]
        else:
            column_names = [desc.name for desc in existing_columns]  # type: List[str]

        requested_columns = [existing_column_name_to_desc[column_name] for column_name in column_names]

        column_filters = list(column_filters) if column_filters is not None \
            else list()  # type: List[Tuple[str, str]]

        if saved_filter_ids:
            column_filters_from_filters, order_by_from_filters = \
                _extract_column_filters_and_order_by_from_saved_filters(document_type, requester, saved_filter_ids)
            if column_filters_from_filters:
                column_filters.extend(column_filters_from_filters)
            if order_by_from_filters and not order_by:
                order_by = order_by_from_filters

        column_filters_clauses = parse_column_filters(column_filters,
                                                      existing_column_name_to_desc,
                                                      ignore_errors=ignore_errors) if column_filters else []
        if filters_sql is not None:
            column_filters_clauses += [filters_sql]
    else:
        column_names = []
        column_filters_clauses = []
        requested_columns = []

    column_sql_specs = [existing_column_name_to_desc[column_name].get_output_column_sql_spec()
                        for column_name in column_names]

    project_ids_clause = _prepare_project_ids_filter(requester, project_ids)  # type: Optional[SQLClause]
    if project_ids_clause:
        column_filters_clauses += [project_ids_clause]

    soft_delete_clause = SQLClause('"{col_name}" = false'.format(col_name=FIELD_CODE_DELETE_PENDING))
    column_filters_clauses.append(soft_delete_clause)

    processed_clause = SQLClause('"{col_name}" = true'.format(col_name=FIELD_CODE_DOC_PROCESSED))
    column_filters_clauses.append(processed_clause)

    where_clause = join_clauses('\nand ', column_filters_clauses)

    data_clause = None
    count_total_clause = None
    count_reviewed_clause = None

    if return_reviewed_count:
        where_reviewed_clause = join_clauses('\nand', [where_clause,
                                                       SQLClause('"{is_reviewed}" = true'
                                                                 .format(is_reviewed=FIELD_CODE_IS_REVIEWED))])
        count_reviewed_clause = format_clause('SELECT count(*) FROM {table_name}\n'
                                              'where {where_reviewed}', table_name=table_name,
                                              where_reviewed=where_reviewed_clause)

    if where_clause:
        where_clause.sql = 'where ' + where_clause.sql

    if return_total_count:
        count_total_clause = format_clause('SELECT count(*) FROM {table_name}\n'
                                           '{where}', table_name=table_name,
                                           where=where_clause)

    def process_hidden_columns(row: List) -> List:
        if not row:
            return row
        if not isinstance(row, list):
            row = list(row)
        hidden_columns = row[-1]
        if hidden_columns:
            hidden_columns = set(hidden_columns)
            for n, column in enumerate(requested_columns):
                if column.name in hidden_columns:
                    row[n] = 'N/A'
        return row[:-1]

    if return_documents:
        sql_columns = ', \n'.join(column_sql_specs)

        correct_order_by = list()
        if order_by:
            for column, direction in order_by:
                if column not in existing_column_names:
                    if not ignore_errors:
                        raise UnknownColumnError('Unknown column: ' + column)
                    else:
                        continue
                else:
                    correct_order_by.append((column, direction))

        order_by = correct_order_by if correct_order_by else [DEFAULT_ORDER_BY]
        # If field IS in hidden list, "=ANY" returns 't' (true), that
        # goes after 'f' (false). Thus hidden values always go after visible ones.
        order_by_clause = SQLClause('order by ' +
                                    ', '.join(
                                        [
                                            '\'{column}\' = ANY({hid_columns}), "{column}" {direction} nulls {nulls_prio}'.format(
                                                column=column,
                                                hid_columns=FIELD_CODE_HIDDEN_COLUMNS,
                                                direction=direction.value,
                                                nulls_prio='first' if direction == SortDirection.ASC else 'last')
                                            for column, direction in order_by]))

        offset_clause = SQLClause('offset %s', [int(offset)]) if offset else None
        limit_clause = SQLClause('limit %s', [int(limit)]) if limit else None

        data_clause = format_clause('SELECT {sql_columns},\n'
                                    '{hidden_columns_name}\n'
                                    'FROM "{table_name}"\n'
                                    '{where}\n'
                                    '{sql_order_by}\n'
                                    '{offset_clause}\n'
                                    '{limit_clause}',
                                    sql_columns=sql_columns,
                                    hidden_columns_name=FIELD_CODE_HIDDEN_COLUMNS,
                                    table_name=table_name,
                                    where=where_clause,
                                    offset_clause=offset_clause,
                                    limit_clause=limit_clause,
                                    sql_order_by=order_by_clause)

    return DocumentQueryResults(offset=offset,
                                limit=limit,
                                total_sql=count_total_clause,
                                reviewed_sql=count_reviewed_clause,
                                columns=requested_columns,
                                items_sql=data_clause,
                                row_processor=process_hidden_columns if return_documents else None)


def set_documents_delete_status(document_ids: List[int],
                                delete_pending: bool) -> None:
    if len(document_ids) == 0:
        return
    doc_types = Document.all_objects.filter(id__in=document_ids).values_list(
        'document_type__code', flat=True).distinct().order_by()
    total_checked = 0
    untracked_ids = []

    try:
        with connection.cursor() as cursor:
            for doc_type in doc_types:
                doc_type_doc_ids = Document.all_objects.filter(
                    document_type__code=doc_type, pk__in=document_ids).values_list('pk', flat=True)
                doc_type_doc_ids_str = ','.join([str(id) for id in doc_type_doc_ids])
                table_name = doc_fields_table_name(doc_type)
                cmd = f'UPDATE "{table_name}" set "{FIELD_CODE_DELETE_PENDING}"' + \
                      f'={delete_pending} where ' + \
                      f'"{FIELD_CODE_DOC_ID}" in ({doc_type_doc_ids_str});'
                cursor.execute(cmd)
                doc_type_docs_updated = cursor.rowcount
                total_checked += cursor.rowcount

                # check if documents ids don't exist in a table at all
                if doc_type_docs_updated < len(doc_type_doc_ids):
                    doc_type_doc_ids_str = ','.join([f'({id})' for id in doc_type_doc_ids])
                    sql = f"VALUES {doc_type_doc_ids_str} " \
                          f"EXCEPT ALL " \
                          f"SELECT document_id FROM {table_name};"
                    cursor.execute(sql)
                    doc_type_untracked_ids = [i[0] for i in cursor.fetchall()]
                    untracked_ids += doc_type_untracked_ids

    except Exception as e:
        er_msg = format_error_msg(document_ids, delete_pending, total_checked)
        logger = get_django_logger()
        logger.error(er_msg + '\n' + str(e))
        raise e

    # Run Index task for untracked documents
    if untracked_ids:
        from apps.rawdb.tasks import plan_reindex_tasks_in_chunks
        plan_reindex_tasks_in_chunks(untracked_ids)

    # Otherwise if some unpredicted case - ensure all documents are processed
    elif total_checked != len(document_ids):
        er_msg = format_error_msg(document_ids, delete_pending, total_checked)
        logger = get_django_logger()
        logger.error(er_msg)
        raise RuntimeError(er_msg)


def delete_documents(document_ids: List[int]) -> None:
    """
    Completely delete document from rawdb index
    :param document_ids:
    :return:
    """
    if len(document_ids) == 0:
        return
    doc_types = Document.all_objects.filter(id__in=document_ids).values_list(
        'document_type__code', flat=True).distinct().order_by()
    try:
        with connection.cursor() as cursor:
            for doc_type in doc_types:
                doc_type_doc_ids = Document.all_objects.filter(
                    document_type__code=doc_type, pk__in=document_ids).values_list('pk', flat=True)
                doc_type_doc_ids_str = ','.join([str(id) for id in doc_type_doc_ids])
                table_name = doc_fields_table_name(doc_type)
                cmd = f'DELETE FROM "{table_name}" WHERE ' + \
                      f'"{FIELD_CODE_DOC_ID}" IN ({doc_type_doc_ids_str});'
                cursor.execute(cmd)
    except Exception as e:
        logger = get_django_logger()
        logger.error('Failed to delete documents with ids {}'.format(str(document_ids)) + '\n' + str(e))
        raise e


def update_document_name(doc_id: int, doc_name: str) -> None:
    doc_type = Document.all_objects.filter(pk=doc_id).values_list(
        'document_type__code', flat=True)[0]
    table_name = doc_fields_table_name(doc_type)

    try:
        with connection.cursor() as cursor:
            cmd = f'UPDATE "{table_name}" set "{FIELD_CODE_DOC_NAME}"' + \
                  f"='{doc_name}' where " + \
                  f'"{FIELD_CODE_DOC_ID}" = {doc_id};'
            cursor.execute(cmd)
    except Exception as e:
        logger = get_django_logger()
        logger.error(f'RawDB: could not rename doc id = {doc_id} to "{doc_name}"', exc_info=e)
        raise e


def format_error_msg(doc_ids: List[int],
                     delete_pending: bool,
                     docs_checked: int) -> str:
    docs_msg = format_docs_ids_str(doc_ids)
    er_action = 'checked as deleted' if delete_pending \
        else 'unchecked as deleted'
    return f'set_documents_delete_status: only {docs_checked} of ' + \
           f'{len(doc_ids)} ([{docs_msg}]) docs were {er_action}.'


def format_docs_ids_str(doc_ids: List[int]) -> str:
    doc_ids = list(doc_ids)
    return ','.join([str(i) for i in doc_ids]) \
        if len(doc_ids) < 6 \
        else ','.join([str(i) for i in doc_ids[:4]]) + \
             f' ..., {doc_ids[:-1]}'
