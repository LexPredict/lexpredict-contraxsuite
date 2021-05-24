from django.db import migrations, models


def migrate_rawdb_contract_class(_apps, _schema_editor):
    from apps.rawdb.repository.raw_db_migrations import add_rawdb_migration_column
    add_rawdb_migration_column('document_contract_class', 'character varying')


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0222_auto_20201224_1533'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='document_contract_class',
            field=models.CharField(blank=True, db_index=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='historicaldocument',
            name='document_contract_class',
            field=models.CharField(blank=True, db_index=True, max_length=256, null=True),
        ),
        migrations.RunPython(migrate_rawdb_contract_class, reverse_code=migrations.RunPython.noop)
    ]
