from typing import List, Dict
from django.db import connection
from apps.common.model_utils.table_deps import TableDeps


class ModelBulkDelete:
    def __init__(self, deps: List[TableDeps]):
        # records like
        # document_documentnote.field_value_id -> document_documentfieldvalue.id,
        #   document_documentfieldvalue.text_unit_id -> document_textunit.id,
        #   document_textunit.document_id -> document_document.id
        self.deps = deps
        self.table_name = deps[0].deps[-1].ref_table
        self.key_column = deps[0].deps[-1].ref_table_pk

    def build_get_deleted_count_queries(self) -> List[str]:
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
            query = f'SELECT COUNT(*) FROM "{dep.deps[0].own_table}"'
            for d in dep.deps:
                query += f'\n  INNER JOIN "{d.ref_table}" ON "{d.ref_table}"."{d.ref_table_pk}"' +\
                         f' = "{d.own_table}"."{d.ref_key}"'

            queries.append(query)

        return queries

    def build_delete_all_queries(self) -> List[str]:
        queries = []  # type: List[str]
        # TODO: wont work for composite primary keys
        for dep in self.deps:
            query = f'DELETE FROM "{dep.deps[0].own_table}"'
            query += f'\n  WHERE "{dep.deps[0].own_table}"."{dep.own_table_pk[0]}" IN'
            query += f'\n (SELECT "{dep.deps[0].own_table}"."{dep.own_table_pk[0]}" FROM "{dep.deps[0].own_table}"'
            for d in dep.deps:
                query += f'\n    JOIN "{d.ref_table}" ON "{d.ref_table}"."{d.ref_table_pk}"' + \
                         f' = "{d.own_table}"."{d.ref_key}"'
            queries.append(query)
        return queries

    def calculate_total_objects_to_delete(self, where_suffix: str) -> Dict[str, int]:
        count_to_del = {}  # type: Dict[str, int]
        queries = self.build_get_deleted_count_queries()
        with connection.cursor() as cursor:
            for i in range(len(self.deps)):
                cursor.execute(queries[i] + ' ' + where_suffix)
                row = cursor.fetchone()
                count = row[0]
                table_name = self.deps[i].deps[0].own_table
                count_to_del[table_name] = count
        return count_to_del

    def delete_objects(self, where_suffix: str) -> Dict[str, int]:
        count_deleted = {}  # type: Dict[str, int]
        queries = self.build_delete_all_queries()
        with connection.cursor() as cursor:
            cursor.db.autocommit = True
            for i in range(len(self.deps)):
                query = queries[i] + ' ' + where_suffix
                cursor.execute(query)
                count = cursor.rowcount
                table_name = self.deps[i].deps[0].own_table
                count_deleted[table_name] = count
        return count_deleted
