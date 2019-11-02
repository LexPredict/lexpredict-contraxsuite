# Generated by Django 2.2 on 2019-07-10 13:14

from django.db import migrations, connection

from apps.rawdb.repository.raw_db_repository import doc_fields_table_name


def do_migrate(apps, schema_editor):
    DocumentType = apps.get_model('document', 'DocumentType')
    with connection.cursor() as cursor:
        for document_type in DocumentType.objects.all():
            table_name = doc_fields_table_name(document_type_code=document_type.code)
            cursor.execute(
                'DROP TABLE IF EXISTS "{table_name}"'.format(table_name=table_name)
            )


class Migration(migrations.Migration):

    dependencies = [
        ('rawdb', '0016_auto_20190705_1123'),
    ]

    operations = [
        migrations.RunPython(do_migrate, reverse_code=migrations.RunPython.noop),
    ]
