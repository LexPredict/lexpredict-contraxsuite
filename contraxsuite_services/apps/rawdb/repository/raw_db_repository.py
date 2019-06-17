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

from typing import Dict, List, Any, Generator, Iterable, Set, Union, Optional
import regex as re
from django.db import connection

from apps.common.sql_commons import fetch_int, SQLClause, format_clause
from apps.document.models import Document, DocumentField, DocumentType
from apps.document.repository.document_field_repository import DocumentFieldRepository
from apps.rawdb.field_value_tables import FIELD_CODE_PROJECT_ID, FIELD_CODE_DOC_ID, FIELD_CODE_DOC_FULL_TEXT
from apps.rawdb.field_value_tables import doc_fields_table_name, build_field_handlers
from apps.rawdb.rawdb.field_handlers import FieldHandler

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.2/LICENSE"
__version__ = "1.2.2"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# TODO: check exclude_hidden_always_fields in build_field_handlers()
class RawDbRepository(DocumentFieldRepository):
    REG_FIELD_NAME_SUG = re.compile(r'_suggested$')
    DEFAULT_FIELD_CODE_FILTER = {FIELD_CODE_DOC_ID, FIELD_CODE_DOC_FULL_TEXT}

    def get_document_fields_hash(self, doc: Document) -> Dict[str, Any]:
        doc_type = doc.document_type
        table_name = doc_fields_table_name(doc_type.code)
        field_handlers = build_field_handlers(document_type=doc_type,
                                              table_name=table_name,
                                              include_generic_fields=False,
                                              include_suggested_fields=False,
                                              include_user_fields=True,
                                              exclude_hidden_always_fields=True)
        field_handlers = self.filter_field_handlers(field_handlers)
        columns = self.build_columns_sql(field_handlers)
        query = f'SELECT {columns} FROM "{table_name}" WHERE "{FIELD_CODE_DOC_ID}" = {doc.pk};'
        rows = list(self.parse_raw_db_into_fields(query, field_handlers))
        return rows[0] if len(rows) > 0 else {}

    def get_doc_field_values_by_uid(self, doc: Document) -> Dict[str, Any]:
        row_vals = self.get_document_fields_hash(doc)
        if not any(row_vals):
            return {}
        hash_ids = list(self.map_field_names_on_uids([row_vals], doc.document_type))
        return hash_ids[0] if len(hash_ids) > 0 else []

    def get_project_documents_field_values_by_uid(
            self,
            project_ids: List[int],
            max_count: int,
            doc_type: DocumentType) -> Generator[Dict[str, Any], None, None]:
        table_name = doc_fields_table_name(doc_type.code)
        proj_ids_str = ','.join([str(i) for i in project_ids])

        field_handlers = build_field_handlers(document_type=doc_type,
                                              table_name=table_name,
                                              exclude_hidden_always_fields=True)
        columns = self.build_columns_sql(field_handlers)
        columns = self.build_columns_sql(field_handlers)
        query_select = f'SELECT {columns} FROM "{table_name}"'
        query_where = f'WHERE "{FIELD_CODE_PROJECT_ID}" IN ({proj_ids_str})'
        limit_str = f' LIMIT({max_count})' if max_count > 0 else ''
        query = f'{query_select}\n{query_where}{limit_str};'

        rows = self.parse_raw_db_into_fields(query, field_handlers)
        return self.map_field_names_on_uids(rows, doc_type)

    def get_documents_field_values_by_uid(self, documents: Iterable[Document]) \
            -> Generator[Dict[str, Any], None, None]:
        doc_type = None
        for doc in documents:
            doc_type = doc.document_type
            break
        if not doc_type:
            return
        doc_ids_str = ','.join([str(doc.pk) for doc in documents])
        table_name = doc_fields_table_name(doc_type.code)
        field_handlers = build_field_handlers(document_type=doc_type,
                                              table_name=table_name,
                                              exclude_hidden_always_fields=True)
        columns = self.build_columns_sql(field_handlers)

        query_select = f'SELECT {columns} FROM "{table_name}"'
        query_where = f'WHERE "{FIELD_CODE_DOC_ID}" IN ({doc_ids_str})'
        query = f'{query_select}\n{query_where}'
        rows = self.parse_raw_db_into_fields(query, field_handlers)
        return self.map_field_names_on_uids(rows, doc_type)

    def map_field_names_on_uids(self, rows: Iterable[Dict[str, Any]],
                                document_type: DocumentType) -> Generator[Dict[str, Any], None, None]:
        fields = DocumentField.objects.filter(document_type=document_type)
        field_uid_by_name = {f.code: f.uid for f in fields}

        for hash in rows:
            if not any(hash):
                continue
            hash_uid = {}
            for field_name in hash:
                field_uid = field_uid_by_name.get(field_name)
                if not field_uid:
                    field_name_brief = self.REG_FIELD_NAME_SUG.sub('', field_name)
                    field_uid = field_uid_by_name.get(field_name_brief)
                    if not field_uid:
                        continue
                    field_uid += '_suggested'
                hash_uid[field_uid] = hash[field_name]
            yield hash_uid

    def parse_raw_db_into_fields(self, query: Union[str, SQLClause],
                                 field_handlers: List[FieldHandler]) -> Generator[Dict[str, Any], None, None]:
        if isinstance(query, str):
            query = SQLClause(query)
        with connection.cursor() as cursor:
            cursor.execute(query.sql, query.params)
            rows = cursor.fetchall()
            for row in rows:
                col_names = [n.name for n in cursor.description]
                row_values = {}
                for i in range(len(row)):
                    row_values[col_names[i]] = row[i]
                values = {}
                for handler in field_handlers:
                    val = handler.columns_to_field_value(row_values)
                    values[handler.field_code] = val
                yield values

    def filter_field_handlers(self, handlers: List[FieldHandler],
                              excluded_fields: Set[str] = None) -> List[FieldHandler]:
        excluded_fields = excluded_fields or self.DEFAULT_FIELD_CODE_FILTER
        return [h for h in handlers if h.field_code not in excluded_fields]

    def build_columns_sql(self, field_handlers: List[FieldHandler]) -> str:
        columns = set()
        for fh in field_handlers:
            columns.update(fh.column_names_for_field_values())
        return ', '.join([f'"{column_name}"' for column_name in columns])

    def count_docs(self,
                   document_type: DocumentType,
                   where_sql: Union[str, SQLClause],
                   table_name: str = None) -> int:
        if table_name is None:
            table_name = doc_fields_table_name(document_type_code=document_type.code)

        if isinstance(where_sql, str):
            where_sql = SQLClause(where_sql)

        with connection.cursor() as cursor:
            return fetch_int(cursor,
                             format_clause('select count(*) from "{table_name}"\n'
                                           'where {where_sql}'
                                           .format(table_name=table_name, where_sql=where_sql)))

    def get_field_values(self,
                         document_type: DocumentType,
                         where_sql: Optional[Union[str, SQLClause]] = None,
                         offset: int = None,
                         limit: int = None,
                         table_name: str = None,
                         field_codes: Set[str] = None) \
            -> Generator[Dict[str, str], None, None]:
        if table_name is None:
            table_name = doc_fields_table_name(document_type_code=document_type.code)

        field_handlers = build_field_handlers(document_type=document_type,
                                              table_name=table_name,
                                              include_generic_fields=True,
                                              include_suggested_fields=False,
                                              exclude_hidden_always_fields=True,
                                              include_user_fields=True)

        field_handlers = [fh for fh in field_handlers if fh.field_code in field_codes]

        columns_sql = self.build_columns_sql(field_handlers)

        sql = format_clause('select {columns_sql} from "{table_name}"\n'
                            '{where_sql}\n'
                            '{offset_sql}\n'
                            '{limit_sql}',
                            columns_sql=columns_sql,
                            table_name=table_name,
                            where_sql=format_clause('where {where_sql}', where_sql=where_sql) if where_sql else '',
                            offset_sql=SQLClause('offset %s', [offset]) if offset is not None else '',
                            limit_sql=SQLClause('limit %s', [limit]) if limit is not None else '')

        yield from self.parse_raw_db_into_fields(query=sql, field_handlers=field_handlers)
