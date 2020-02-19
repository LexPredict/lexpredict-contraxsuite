from django.db import migrations, models, connection


def do_migrate(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("""
        UPDATE "document_document" set document_class = 
         (SELECT "document_documentmetadata"."metadata" ->> 'document_class' 
          FROM "document_documentmetadata" WHERE "document_documentmetadata".document_id = document_document.id);
        """)


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0181_merge_20200123_2008'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='document_class',
            field=models.CharField(db_index=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='historicaldocument',
            name='document_class',
            field=models.CharField(db_index=True, max_length=256, null=True),
        ),
        migrations.RunPython(do_migrate, reverse_code=migrations.RunPython.noop),
    ]
