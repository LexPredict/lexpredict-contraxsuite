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

import time
from typing import List, Dict, Set, Optional
from django.db import connection, OperationalError

from apps.common.error_explorer import retry_for_operational_error
from apps.common.model_utils.table_deps import TableDeps

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class WherePredicate:
    def __init__(self, table: str, column: str, predicate: str):
        self.table = table
        self.column = column
        self.predicate = predicate

    def __str__(self):
        return f'"{self.table}"."{self.column}" {self.predicate}'


class ModelBulkDelete:
    tries_per_query = 2

    def __init__(self,
                 deps: List[TableDeps],
                 safe_mode: bool = True,
                 unsafe_tables: Set[str] = None):
        # records like
        # document_documentnote.field_value_id -> document_documentfieldvalue.id,
        #   document_documentfieldvalue.text_unit_id -> document_textunit.id,
        #   document_textunit.document_id -> document_document.id
        self.deps = deps
        self.table_name = deps[0].deps[-1].ref_table
        self.key_column = deps[0].deps[-1].ref_table_pk
        self.safe_mode = safe_mode
        self.unsafe_tables = unsafe_tables

    def build_get_deleted_count_queries(self,
                                        tables_to_skip: Optional[Set[str]],
                                        where_suffix: WherePredicate) -> List[str]:
        # dep like
        # "pk:[id], document_documentfieldvalue.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id"
        # will produce
        # SELECT COUNT(*) FROM "document_documentfieldvalue"
        #   JOIN "document_textunit" ON "document_textunit"."id" = "document_documentfieldvalue"."text_unit_id"
        #   JOIN "document_document" ON "document_document"."id" = "document_textunit":"document_id"
        # + (optionally):
        #   WHERE "document_document"."id" = {id}
        queries = []  # type: List[str]

        for dep in self.deps:
            if tables_to_skip and dep.deps[0].own_table in tables_to_skip:
                queries.append(None)
                continue
            # try removing unnecessary join like:
            # SELECT COUNT(*) FROM "document_textunit"
            #   INNER JOIN "document_document" ON "document_document"."id" = "document_textunit"."document_id"
            #   WHERE "document_document"."id" IN (23335,24551
            # =============================>
            # SELECT COUNT(*) FROM "document_textunit"
            # WHERE "document_textunit"."document_id" IN (23335,24551
            query = f'SELECT COUNT(*) FROM "{dep.deps[0].own_table}"'
            query_sfx = where_suffix
            for d in dep.deps:
                if d.ref_table == where_suffix.table and d.ref_table_pk == where_suffix.column:
                    query_sfx = WherePredicate(d.own_table, d.ref_key, where_suffix.predicate)
                    continue
                query += f'\n  INNER JOIN "{d.ref_table}" ON "{d.ref_table}"."{d.ref_table_pk}"' +\
                         f' = "{d.own_table}"."{d.ref_key}"'

            query = f'{query}\nWHERE {query_sfx}'
            queries.append(query)

        return queries

    def build_delete_all_queries(self, where_suffix: WherePredicate) -> List[str]:
        queries = []  # type: List[str]
        '''
        DELETE FROM "document_textunit" t
        USING (
           SELECT "document_textunit"."id" FROM "document_textunit"
           JOIN "document_document" ON "document_document"."id" = "document_textunit"."document_id"
           WHERE "document_document"."id" = 161023
           FOR UPDATE
        ) del
        WHERE t.id = del.id;
        '''
        # TODO: wont work for composite primary keys
        query_sfx = where_suffix
        for dep in self.deps:
            query = f'DELETE FROM "{dep.deps[0].own_table}" target_table\n'
            query += 'USING (\n'
            query += f'  SELECT "{dep.deps[0].own_table}"."{dep.own_table_pk[0]}" FROM\n'
            query += f'  "{dep.deps[0].own_table}"'
            for d in dep.deps:
                if d.ref_table == where_suffix.table and d.ref_table_pk == where_suffix.column:
                    query_sfx = WherePredicate(d.own_table, d.ref_key, where_suffix.predicate)
                    continue
                query += f'\n    JOIN "{d.ref_table}" ON "{d.ref_table}"."{d.ref_table_pk}"' + \
                         f' = "{d.own_table}"."{d.ref_key}"'
            query += f'\n  WHERE {query_sfx}'
            query += f'\n  ORDER BY "{dep.deps[0].own_table}"."{dep.own_table_pk[0]}"'
            query += '\n  FOR UPDATE\n) table_del\n'
            query += f'WHERE target_table."{dep.own_table_pk[0]}" = table_del."{dep.own_table_pk[0]}";'

            queries.append(query)
        return queries

    def calculate_total_objects_to_delete(self,
                                          where_suffix: WherePredicate,
                                          tables_to_skip: Optional[Set[str]] = None) -> Dict[str, int]:
        count_to_del = {}  # type: Dict[str, int]
        queries = self.build_get_deleted_count_queries(tables_to_skip, where_suffix)
        with connection.cursor() as cursor:
            for i in range(len(self.deps)):
                if not queries[i]:
                    continue
                cursor.execute(queries[i])
                row = cursor.fetchone()
                count = row[0]
                table_name = self.deps[i].deps[0].own_table
                count_to_del[table_name] = count
        return count_to_del

    @retry_for_operational_error(retries_count=2, cooldown_interval=2.0)
    def delete_objects(self, where_suffix: WherePredicate) -> Dict[str, int]:
        count_deleted = {}  # type: Dict[str, int]
        queries = self.build_delete_all_queries(where_suffix)
        with connection.cursor() as cursor:
            cursor.db.autocommit = True
            for i, query in enumerate(queries):
                for iteration in range(self.tries_per_query + 1):
                    try:
                        table = self.deps[i].deps[0].own_table
                        if not self.safe_mode and table in self.unsafe_tables:
                            query = f'ALTER TABLE "{table}" DISABLE TRIGGER ALL;\n' + query
                            query += f'\nALTER TABLE "{table}" ENABLE TRIGGER ALL;'
                        cursor.execute(query)
                        count = cursor.rowcount
                        table_name = self.deps[i].deps[0].own_table
                        count_deleted[table_name] = count
                    except OperationalError as oe:
                        if iteration == self.tries_per_query:
                            raise RuntimeError(f'Error in bulk_delete.delete_objects(). Query:\n{query}') from oe
                        # if it's a deadlock - sleep a bit and the retry
                        time.sleep(0.5)
                        continue
                    except Exception as e:
                        raise RuntimeError(f'Error in bulk_delete.delete_objects(). Query:\n{query}') from e
        return count_deleted
