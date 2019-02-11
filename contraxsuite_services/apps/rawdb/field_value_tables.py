import hashlib
from collections import defaultdict
from typing import List, Dict, Optional, Tuple, Any, Generator, Set

from django.conf import settings
from django.db import connection, transaction
from django.db.models import Q

from apps.common.log_utils import ProcessLogger, render_error
from apps.common.sql_commons import fetch_int, escape_column_name, sum_list, SQLClause, \
    SQLInsertClause, join_clauses, format_clause
from apps.document import field_types
from apps.document.fields_processing.field_value_cache import get_generic_values
from apps.document.models import DocumentType, Document, DocumentField, DocumentFieldValue
from apps.rawdb.models import SavedFilter
from apps.rawdb.rawdb import field_handlers
from apps.rawdb.rawdb.errors import Forbidden, UnknownColumnError
from apps.rawdb.rawdb.query_parsing import SortDirection, parse_column_filters
from apps.users.models import User

TABLE_NAME_PREFIX = 'doc_fields_'


def build_table_name(document_type_code: str) -> str:
    return escape_column_name(TABLE_NAME_PREFIX + document_type_code)


# method return types
class DocumentQueryResults(list):
    def __init__(self,
                 offset: Optional[int],
                 limit: Optional[int],
                 total_sql: Optional[SQLClause],
                 reviewed_sql: Optional[SQLClause],
                 column_codes: List[str],
                 column_titles: List[str],
                 items_sql: Optional[SQLClause]) -> None:
        super().__init__()
        self.offset = offset
        self.limit = limit
        self.column_codes = column_codes
        self.column_titles = column_titles
        self._items_sql = items_sql
        self.reviewed = None
        self.total = None
        if total_sql or reviewed_sql:
            with connection.cursor() as cursor:
                self.reviewed = fetch_int(cursor, reviewed_sql) if reviewed_sql else None
                self.total = fetch_int(cursor, total_sql) if total_sql else None

    def fetch(self) -> Generator[List, None, None]:
        if self._items_sql:
            with connection.cursor() as cursor:
                cursor.execute(self._items_sql.sql, self._items_sql.params)
                rows = cursor.fetchmany(100)
                while rows:
                    for row in rows:
                        yield row
                    rows = cursor.fetchmany(100)

    def fetch_dicts(self) -> Generator[Dict, None, None]:
        for row in self.fetch():
            yield dict(zip(self.column_codes, row))

    def __iter__(self):
        return self.fetch_dicts()

    def __len__(self) -> int:
        return 1


FIELD_DB_SUPPORT_REGISTRY = {
    field_types.StringField.code: field_handlers.StringFieldHandler,
    field_types.StringFieldWholeValueAsAToken.code: field_handlers.StringFieldHandler,
    field_types.LongTextField.code: field_handlers.StringFieldHandler,
    field_types.IntField.code: field_handlers.IntFieldHandler,
    field_types.FloatField.code: field_handlers.FloatFieldHandler,
    field_types.DateField.code: field_handlers.DateFieldHandler,
    field_types.RecurringDateField.code: field_handlers.DateFieldHandler,
    field_types.CompanyField.code: field_handlers.StringFieldHandler,
    field_types.DurationField.code: field_handlers.IntFieldHandler,
    field_types.AddressField.code: field_handlers.AddressFieldHandler,
    field_types.RelatedInfoField.code: field_handlers.RelatedInfoFieldHandler,
    field_types.ChoiceField.code: field_handlers.StringFieldHandler,
    field_types.MultiChoiceField.code: field_handlers.MultichoiceFieldHandler,
    field_types.PersonField.code: field_handlers.StringFieldHandler,
    field_types.AmountField.code: field_handlers.FloatFieldHandler,
    field_types.MoneyField.code: field_handlers.MoneyFieldHandler,
    field_types.GeographyField.code: field_handlers.StringFieldHandler
}

_FIELD_CODE_DOC_NAME = 'document_name'
_FIELD_CODE_DOC_TITLE = 'document_title'
_FIELD_CODE_DOC_FULL_TEXT = 'document_full_text'
_FIELD_CODE_DOC_FULL_TEXT_LENGTH = 'document_full_text_length'
_FIELD_CODE_DOC_ID = 'document_id'
_FIELD_CODE_IS_REVIEWED = 'document_is_reviewed'
_FIELD_CODE_PROJECT_ID = 'project_id'
_FIELD_CODE_ASSIGNEE_NAME = 'assignee_name'
_FIELD_CODE_STATUS_NAME = 'status_name'

# Generic Fields - should match keys from the output of field_value_cache.get_generic_values(doc)
_FIELD_CODE_CLUSTER_ID = 'cluster_id'
_FIELD_CODE_PARTIES = 'parties'
_FIELD_CODE_EARLIEST_DATE = 'min_date'
_FIELD_CODE_LATEST_DATE = 'max_date'
_FIELD_CODE_LARGEST_CURRENCY = 'max_currency'

_FIELD_CODES_SYSTEM = {_FIELD_CODE_PROJECT_ID, _FIELD_CODE_DOC_ID, _FIELD_CODE_DOC_NAME,
                       _FIELD_CODE_DOC_FULL_TEXT_LENGTH, _FIELD_CODE_DOC_TITLE,
                       _FIELD_CODE_DOC_FULL_TEXT, _FIELD_CODE_IS_REVIEWED, _FIELD_CODE_ASSIGNEE_NAME,
                       _FIELD_CODE_STATUS_NAME, _FIELD_CODE_CLUSTER_ID, _FIELD_CODE_PARTIES,
                       _FIELD_CODE_LARGEST_CURRENCY, _FIELD_CODE_EARLIEST_DATE, _FIELD_CODE_LATEST_DATE}

_FIELD_CODE_ALL_DOC_TYPES = {_FIELD_CODE_PROJECT_ID, _FIELD_CODE_DOC_ID, _FIELD_CODE_DOC_NAME,
                             _FIELD_CODE_DOC_FULL_TEXT_LENGTH, _FIELD_CODE_DOC_TITLE,
                             _FIELD_CODE_DOC_FULL_TEXT, _FIELD_CODE_IS_REVIEWED, _FIELD_CODE_ASSIGNEE_NAME,
                             _FIELD_CODE_STATUS_NAME}
_FIELD_CODES_GENERIC_ONLY = {_FIELD_CODE_CLUSTER_ID, _FIELD_CODE_PARTIES,
                             _FIELD_CODE_LARGEST_CURRENCY, _FIELD_CODE_EARLIEST_DATE, _FIELD_CODE_LATEST_DATE}

FIELD_CODES_SHOW_BY_DEFAULT_NON_GENERIC = {
    _FIELD_CODE_DOC_NAME, _FIELD_CODE_ASSIGNEE_NAME, _FIELD_CODE_STATUS_NAME
}

FIELD_CODES_SHOW_BY_DEFAULT_GENERIC = {
    _FIELD_CODE_DOC_NAME, _FIELD_CODE_CLUSTER_ID, _FIELD_CODE_DOC_TITLE, _FIELD_CODE_PARTIES, _FIELD_CODE_EARLIEST_DATE,
    _FIELD_CODE_LATEST_DATE, _FIELD_CODE_LARGEST_CURRENCY
}


def _build_system_field_handlers(table_name: str) -> List[field_handlers.FieldHandler]:
    res = list()
    id_handler = field_handlers.IntFieldHandler(_FIELD_CODE_DOC_ID, 'Id', table_name)
    id_handler.pg_type = field_handlers.PgTypes.INTEGER_PRIMARY_KEY
    res.append(id_handler)
    res.append(field_handlers.StringFieldHandler(_FIELD_CODE_DOC_NAME, 'Name', table_name))
    res.append(field_handlers.StringFieldHandler(_FIELD_CODE_DOC_TITLE, 'Title', table_name))
    res.append(field_handlers.StringWithTextSearchFieldHandler(_FIELD_CODE_DOC_FULL_TEXT, 'Text', table_name))
    res.append(field_handlers.IntFieldHandler(_FIELD_CODE_DOC_FULL_TEXT_LENGTH, 'Text Length', table_name))
    res.append(field_handlers.BooleanFieldHandler(_FIELD_CODE_IS_REVIEWED, 'Reviewed', table_name))
    res.append(field_handlers.IntFieldHandler(_FIELD_CODE_PROJECT_ID, 'Project Id', table_name))
    res.append(field_handlers.StringFieldHandler(_FIELD_CODE_ASSIGNEE_NAME, 'Assignee', table_name))
    res.append(field_handlers.StringFieldHandler(_FIELD_CODE_STATUS_NAME, 'Status', table_name))
    return res


def _build_generic_field_handlers(table_name: str) -> List[field_handlers.FieldHandler]:
    res = list()
    res.append(field_handlers.IntFieldHandler(_FIELD_CODE_CLUSTER_ID, 'Cluster Id', table_name))
    res.append(field_handlers.StringFieldHandler(_FIELD_CODE_PARTIES, 'Parties', table_name))
    res.append(field_handlers.DateFieldHandler(_FIELD_CODE_EARLIEST_DATE, 'Earliest Date', table_name))
    res.append(field_handlers.DateFieldHandler(_FIELD_CODE_LATEST_DATE, 'Latest Date', table_name))
    res.append(field_handlers.MoneyFieldHandler(_FIELD_CODE_LARGEST_CURRENCY, 'Largest Currency', table_name))
    return res


def build_field_handlers(document_type: DocumentType, table_name: str,
                         include_generic_fields: bool = True,
                         include_user_fields: bool = True,
                         include_suggested_fields: bool = True,
                         exclude_hidden_always_fields: bool = False) \
        -> List[field_handlers.FieldHandler]:
    res = list()

    res.extend(_build_system_field_handlers(table_name))

    if include_generic_fields:
        res.extend(_build_generic_field_handlers(table_name))

    if include_user_fields:
        doc_field_qr = DocumentField.objects.filter(document_type=document_type)
        if exclude_hidden_always_fields:
            doc_field_qr = doc_field_qr.filter(hidden_always=False)
        for field in doc_field_qr.order_by('order', 'code'):  # type: DocumentField
            field_type = field.get_field_type()  # type: field_types.FieldType
            field_handler_class = FIELD_DB_SUPPORT_REGISTRY[field_type.code]
            field_handler = field_handler_class(field.code, field.title, table_name, field.default_value)
            res.append(field_handler)

            if include_suggested_fields and field.is_detectable() and not field.read_only:
                field_code_suggested = field.code + '_suggested'
                field_handler_suggested = field_handler_class(field_code_suggested,
                                                              field.title + ': Suggested',
                                                              table_name,
                                                              field.default_value)
                res.append(field_handler_suggested)

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


INDEX_NAME_PREFIX = 'cx_'


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
        if f.order_by and type(f.order_by) is list:
            new_order_by = [(c, d) for c, d in f.order_by if c in should_be_column_names]
            if new_order_by != f.order_by:
                f.order_by = new_order_by
                save = True
        if save:
            f.save()


def adapt_table_structure(log: ProcessLogger, document_type: DocumentType,
                          force: bool = False, check_only: bool = False) -> bool:
    """
    Create or alter raw db table for it to match the field structure of the specified document type.
    :param log:
    :param document_type:
    :param force: Force re-creating the table.
    :param check_only Do not really alter the table but only check if the re-indexing will be required.
    :return: True/False - if any column has been added/removed/altered and re-index is required for this doc type.
    """
    table_name = build_table_name(document_type.code)

    fields = build_field_handlers(document_type, table_name)
    should_be_columns = dict()  # type: Dict[str, str]
    should_be_indexes = dict()  # type: Dict[str, str]
    for field_handler in fields:
        field_columns = field_handler.get_pg_column_definitions()  # type: Dict[str, field_handlers.PgTypes]
        should_be_columns.update({name: pg_type.value for name, pg_type in field_columns.items()})
        index_defs = field_handler.get_pg_index_definitions()
        if index_defs:
            should_be_indexes.update({build_index_name(table_name, index_def): index_def for index_def in index_defs})

    if not check_only and (force or not table_exists(table_name)):
        _recreate_document_fields_table(log, table_name, should_be_columns, should_be_indexes)
        cleanup_saved_filters(document_type, set(should_be_columns.keys()))
        return True

    reindex_needed = False

    with connection.cursor() as cursor:
        with transaction.atomic():
            existing_columns = get_table_columns_from_pg(cursor, table_name)  # type: Dict[str, str]

            alter_table_actions = list()  # type: List[str]

            for existing_name, existing_type in existing_columns.items():
                should_be_type = should_be_columns.get(existing_name)
                if not should_be_type or should_be_type != existing_type:
                    # column does not exist in "should_be_columns" or has different type
                    alter_table_actions.append('drop column "{column}"'.format(column=existing_name))

            for should_be_name, should_be_type in should_be_columns.items():
                existing_type = existing_columns.get(should_be_name)
                if not existing_type or existing_type != should_be_type:
                    # column does not exist in "existing_columns" or has
                    # different type (and has been dropped in prev loop)
                    alter_table_actions.append('add column "{column}" {pg_type}'
                                               .format(column=should_be_name, pg_type=should_be_type))
            if alter_table_actions:
                if not check_only:
                    alter_table_sql = 'alter table "{table_name}"\n{actions}' \
                        .format(table_name=table_name, actions=',\n'.join(alter_table_actions))
                    cursor.execute(alter_table_sql, [])
                    cleanup_saved_filters(document_type, set(should_be_columns.keys()))
                reindex_needed = True

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
                    cursor.execute(create_index_sql, [])

    return reindex_needed


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
                                 field_document_id=_FIELD_CODE_DOC_ID)  # type: SQLClause

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
                                         field_to_python_values: Dict[str, List]):
    field_to_python_values[_FIELD_CODE_DOC_ID] = [document.id]
    field_to_python_values[_FIELD_CODE_DOC_NAME] = [document.name]
    field_to_python_values[_FIELD_CODE_DOC_TITLE] = [document.title]
    field_to_python_values[_FIELD_CODE_IS_REVIEWED] = [document.is_reviewed()]
    field_to_python_values[_FIELD_CODE_DOC_FULL_TEXT] = \
        [document.full_text[:settings.RAW_DB_FULL_TEXT_SEARCH_CUT_ABOVE_TEXT_LENGTH] if document.full_text else None]
    field_to_python_values[_FIELD_CODE_DOC_FULL_TEXT_LENGTH] = [len(document.full_text) if document.full_text else 0]
    field_to_python_values[_FIELD_CODE_PROJECT_ID] = [document.project_id]
    field_to_python_values[_FIELD_CODE_ASSIGNEE_NAME] = [document.assignee.get_full_name()
                                                         if document.assignee else None]
    field_to_python_values[_FIELD_CODE_STATUS_NAME] = [document.status.name if document.status else None]


def _fill_generic_fields_to_python_values(document: Document,
                                          field_to_python_values: Dict[str, List]):
    generic_values = get_generic_values(document)
    field_to_python_values.update({k: [v] for k, v in generic_values.items()})


def _build_insert_clause(log: ProcessLogger,
                         table_name: str,
                         handlers: List[field_handlers.FieldHandler],
                         document: Document,
                         field_to_python_values: Dict[str, List]) -> SQLClause:
    insert_clauses = list()

    for handler in handlers:  # type: field_handlers.FieldHandler
        python_values = field_to_python_values[handler.field_code]
        try:
            insert_clause = handler.get_pg_sql_insert_clause(document.language,
                                                             python_values)  # type: SQLInsertClause
            insert_clauses.append(insert_clause)
        except Exception as ex:
            msg = render_error(
                'Unable to cache field values.\n'
                'Document: {0} (#{1}).\n'
                'Field: {2}'.format(document.name, document.id, handler.field_code), caused_by=ex)
            log.error(msg)

    columns_clause, values_clause = SQLInsertClause.join(insert_clauses)

    insert_clause = format_clause('insert into "{table_name}" ({columns}) '
                                  'values ({values}) on conflict ({column_document_id}) '
                                  'do update set ({columns}) = ({values})',
                                  table_name=table_name,
                                  columns=columns_clause,
                                  values=values_clause,
                                  column_document_id=_FIELD_CODE_DOC_ID)

    return insert_clause


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


def delete_document_from_cache(document_id):
    with connection.cursor() as cursor:
        _delete_document_from_cache(cursor, document_id)


def cache_document_fields(log: ProcessLogger,
                          document: Document,
                          cache_generic_fields: bool = True,
                          cache_user_fields: bool = True,
                          pre_detected_field_codes_to_suggested_values: Optional[Dict[str, Any]] = None):
    document_type = document.document_type
    table_name = build_table_name(document_type.code)

    cache_suggested_fields = pre_detected_field_codes_to_suggested_values is not None

    handlers = build_field_handlers(document_type,
                                    table_name,
                                    include_generic_fields=cache_generic_fields,
                                    include_user_fields=cache_user_fields,
                                    include_suggested_fields=cache_suggested_fields)

    field_to_python_values = defaultdict(list)
    _fill_system_fields_to_python_values(document, field_to_python_values)
    if cache_generic_fields:
        _fill_generic_fields_to_python_values(document, field_to_python_values)

    if cache_user_fields:
        non_system_field_codes = [h.field_code for h in handlers if h.field_code not in _FIELD_CODES_SYSTEM]

        if non_system_field_codes:
            real_document_field_values = DocumentFieldValue.objects \
                .filter(document=document, field__code__in=non_system_field_codes) \
                .exclude(removed_by_user=True) \
                .select_related('field')  # type: List[DocumentFieldValue]

            for dfv in real_document_field_values:
                field_to_python_values[dfv.field.code].append(dfv.python_value)

            if cache_suggested_fields and pre_detected_field_codes_to_suggested_values is not None:
                for field_code, python_value in pre_detected_field_codes_to_suggested_values.items():
                    field_to_python_values[field_code + '_suggested'].append(python_value)

    insert_clause = _build_insert_clause(log, table_name, handlers, document, field_to_python_values)
    with connection.cursor() as cursor:
        cursor.execute(insert_clause.sql, insert_clause.params)


def _get_columns(handlers: List[field_handlers.FieldHandler]) -> List[field_handlers.ColumnDesc]:
    return sum_list([h.get_client_column_descriptions() for h in handlers])


def get_columns(document_type: DocumentType, include_suggested: bool = True, include_generic: bool = False) \
        -> List[field_handlers.ColumnDesc]:
    table_name = build_table_name(document_type.code)
    handlers = build_field_handlers(document_type,
                                    table_name,
                                    include_suggested_fields=include_suggested,
                                    include_generic_fields=include_generic,
                                    exclude_hidden_always_fields=True)
    return _get_columns(handlers)


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
                         .format(project_id_column=_FIELD_CODE_PROJECT_ID,
                                 values=', '.join({str(project_id) for project_id in project_ids})))
    else:
        return None


def _extract_column_filters_from_saved_filters(document_type: DocumentType,
                                               requester: User,
                                               saved_filter_ids: List[int]) -> List[Tuple[str, str]]:
    saved_filters = list(SavedFilter.objects
                         .filter(document_type=document_type)
                         .filter(pk__in=saved_filter_ids)
                         .filter(Q(user__isnull=True) | Q(user=requester))
                         .values_list('column_filters', flat=True)
                         .all())  # type: List[Tuple[str, str]]
    if not saved_filters:
        raise Forbidden()
    res = list()  # type: List[Tuple[str, str]]

    for filter_json in saved_filters:
        if filter_json:
            res.extend([(column, column_filter) for column, column_filter in filter_json.items()])

    return res


DEFAULT_ORDER_BY = (_FIELD_CODE_DOC_NAME, SortDirection.ASC)


def get_documents(requester: User,
                  document_type: DocumentType,
                  project_ids: Optional[List[int]] = None,
                  column_names: Optional[List[str]] = None,
                  column_filters: Optional[List[Tuple[str, str]]] = None,
                  saved_filter_ids: Optional[List[int]] = None,
                  order_by: Optional[List[Tuple[str, SortDirection]]] = None,
                  offset: int = None,
                  limit: int = None,
                  return_documents: bool = True,
                  return_total_count: bool = True,
                  return_reviewed_count: bool = False,
                  ignore_errors: bool = False
                  ) -> Optional[DocumentQueryResults]:
    if not return_documents and not return_reviewed_count and not return_total_count:
        return None

    table_name = build_table_name(document_type.code)
    handlers = build_field_handlers(document_type, table_name, exclude_hidden_always_fields=True)
    existing_columns = _get_columns(handlers)  # type: List[field_handlers.ColumnDesc]
    existing_column_name_to_desc = {column.name: column
                                    for column in
                                    existing_columns}  # type: Dict[str, field_handlers.ColumnDesc]
    existing_column_names = set(existing_column_name_to_desc.keys())

    if return_documents or saved_filter_ids or column_filters:
        # build column handlers only if there can be filters on columns (saved filters or filters specified in request)
        # or if we are returning data which requires column names

        # filter requested column names to have only the existing ones
        if column_names:
            column_names = [column for column in column_names if column in existing_column_names]  # type: List[str]
        else:
            column_names = [column_desc.name for column_desc in existing_columns]  # type: List[str]

        column_titles = [existing_column_name_to_desc[column_name].title for column_name in column_names]

        column_filters = list(
            column_filters) if column_filters is not None else list()  # type: List[Tuple[str, str]]

        if saved_filter_ids:
            column_filters.extend(
                _extract_column_filters_from_saved_filters(document_type, requester, saved_filter_ids))

        column_filters_clauses = parse_column_filters(column_filters,
                                                      existing_column_name_to_desc,
                                                      ignore_errors=ignore_errors) if column_filters else []
    else:
        column_names = []
        column_filters_clauses = []
        column_titles = []

    project_ids_clause = _prepare_project_ids_filter(requester, project_ids)  # type: Optional[SQLClause]

    where_clause = join_clauses('\nand ', [project_ids_clause] + column_filters_clauses)

    data_clause = None
    count_total_clause = None
    count_reviewed_clause = None

    if return_reviewed_count:
        where_reviewed_clause = join_clauses('\nand', [where_clause,
                                                       SQLClause('"{is_reviewed}" = true'
                                                                 .format(is_reviewed=_FIELD_CODE_IS_REVIEWED))])
        count_reviewed_clause = format_clause('SELECT count(*) FROM {table_name}\n'
                                              'where {where_reviewed}', table_name=table_name,
                                              where_reviewed=where_reviewed_clause)

    if where_clause:
        where_clause.sql = 'where ' + where_clause.sql

    if return_total_count:
        count_total_clause = format_clause('SELECT count(*) FROM {table_name}\n'
                                           '{where}', table_name=table_name,
                                           where=where_clause)

    if return_documents:
        sql_columns = ', \n'.join(['"{column}"'.format(column=column) for column in column_names])

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

        order_by_clause = SQLClause('order by ' + ', '.join(
            ['"{column}" {direction} nulls {nulls_prio}'
                 .format(column=column,
                         direction=direction.value,
                         nulls_prio='first' if direction == SortDirection.ASC else 'last')
             for column, direction in order_by]))

        offset_clause = SQLClause('offset %s', [int(offset)]) if offset else None
        limit_clause = SQLClause('limit %s', [int(limit)]) if limit else None

        data_clause = format_clause('SELECT {sql_columns}\n'
                                    'FROM "{table_name}"\n'
                                    '{where}\n'
                                    '{sql_order_by}\n'
                                    '{offset_clause}\n'
                                    '{limit_clause}', sql_columns=sql_columns,
                                    table_name=table_name,
                                    where=where_clause,
                                    offset_clause=offset_clause,
                                    limit_clause=limit_clause,
                                    sql_order_by=order_by_clause)

    return DocumentQueryResults(offset=offset,
                                limit=limit,
                                total_sql=count_total_clause,
                                reviewed_sql=count_reviewed_clause,
                                column_codes=column_names,
                                column_titles=column_titles,
                                items_sql=data_clause)
