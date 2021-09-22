from typing import Optional

from django.db import migrations, connection
from apps.common.model_utils.model_bulk_delete import ModelBulkDelete, WherePredicate
from apps.common.model_utils.table_deps_builder import TableDepsBuilder

"""
Delete document fields without document type reference
"""

MODEL_TABLE = 'document_documentfield'


def remove_fields(_, __):
    with connection.cursor() as cursor:
        # delete all references to the document fields w/o doc type
        model_delete = build_model_bulk_delete()
        where_clause = build_bulk_delete_where_clause(cursor)
        if not where_clause:
            return
        model_delete.delete_objects(where_clause)
        cursor.execute(f'DELETE FROM {MODEL_TABLE} WHERE document_type_id is null;')


def build_bulk_delete_where_clause(cursor) -> Optional[WherePredicate]:
    cursor.execute(f"SELECT uid from {MODEL_TABLE} WHERE document_type_id is null;")
    ids = [r[0] for r in cursor.fetchall()]
    if not ids:
        return None

    if len(ids) > 1:
        ids_str = ','.join([f"'{id}'" for id in ids])
        where_clause = WherePredicate(MODEL_TABLE, 'uid', f'IN ({ids_str})')
    else:
        where_clause = WherePredicate(MODEL_TABLE, 'uid', f"= '{ids[0]}'")
    return where_clause


def build_model_bulk_delete(safe_mode: bool = True) -> ModelBulkDelete:
    deps = TableDepsBuilder().build_table_dependences('document_documentfield')
    return ModelBulkDelete(deps, safe_mode)


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0242_auto_20210426_1209'),
    ]

    operations = [
        migrations.RunPython(remove_fields, reverse_code=migrations.RunPython.noop),
    ]
