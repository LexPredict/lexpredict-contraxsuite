# Generated by Django 2.2.4 on 2019-10-24 16:32

from typing import List, Tuple

from django.db import migrations, connection

from apps.rawdb.rawdb.rawdb_field_handlers import RatioRawdbFieldHandler, escape_column_name
from apps.rawdb.repository.raw_db_repository import doc_fields_table_name


def do_rename(apps, schema_editor):
    DocumentField = apps.get_model('document', 'DocumentField')
    to_rename = list()  # type: List[Tuple[str, str, str]]
    for field in DocumentField.objects.filter(type='ratio'):
        table_name = doc_fields_table_name(field.document_type.code)
        handler = RatioRawdbFieldHandler(field.code, field.type, field.title, table_name)
        to_rename.append((table_name,
                          escape_column_name(handler.field_column_name_base + '_con'),
                          escape_column_name(handler.field_column_name_base + '_den')))

    for table_name, column_from, column_to in to_rename:
        with connection.cursor() as cursor:
            cursor.execute(f'''
            DO $$
            BEGIN
                IF EXISTS(SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name='{table_name}' and column_name='{column_from}')
                    AND NOT 
                    EXISTS(SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name='{table_name}' and column_name='{column_to}')
                    THEN
                    ALTER TABLE {table_name} RENAME COLUMN {column_from} TO {column_to};
                END IF;
            END $$;
            ''')


class Migration(migrations.Migration):
    dependencies = [
        ('rawdb', '0018_initiate_reindex'),
    ]

    operations = [
        migrations.RunPython(do_rename, reverse_code=migrations.RunPython.noop),
    ]
