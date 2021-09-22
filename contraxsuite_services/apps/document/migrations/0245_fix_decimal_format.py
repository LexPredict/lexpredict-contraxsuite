from django.db import migrations, connection
import decimal

from apps.common.collection_utils import chunks

"""
This migration fixes Decimal (duration) field format as it's stored in the DB in
'document_fieldannotation' and 'document_fieldvalue' tables.

Before the migration:
select value from document_fieldvalue where field_id = '5490a5b2-ee21-4953-aeb1-b4c2ff54e554' and value is not null;
 "7.3E+2"
 "365"
 "7.3E+2"
 
After the migration:
select value ...
 "730"
 "365"
 "730"
"""


def update_fields(_, __):
    with connection.cursor() as cursor:
        # get all "duration" fields
        cursor.execute("SELECT uid, code FROM document_documentfield WHERE type = 'duration';")
        fields = [(uid, code, ) for uid, code in cursor.fetchall()]
        for uid, code in fields:
            print(f'Processing field "{code}"')
            fix_field_values(cursor, uid)


def fix_field_values(cursor, field_id: str):
    tables = ['document_fieldannotation', 'document_fieldannotationfalsematch', 'document_fieldvalue']
    for table_name in tables:
        cursor.execute(f"SELECT id, value FROM {table_name} WHERE field_id = %s AND value IS NOT null;", [field_id])
        values = [(id, value,) for id, value in cursor.fetchall()]

        values_per_insert = 50
        for values_pack in chunks(values, values_per_insert):
            values_formatted = [
                (id, f'{decimal.Decimal(value):f}')
                for id, value in values_pack]
            values_str = ', '.join([f"""({id}, '"{value}"'::jsonb)""" for id, value in values_formatted])

            cursor.execute(f"""
            UPDATE {table_name} AS t SET
                value = c.column_b
            from (values {values_str}) as c(column_a, column_b) 
            where c.column_a = t.id;""")


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0244_obligatory_field_doc_type'),
    ]

    operations = [
        migrations.RunPython(update_fields, reverse_code=migrations.RunPython.noop)
    ]
