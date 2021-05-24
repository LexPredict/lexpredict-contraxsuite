from __future__ import unicode_literals
from django.db import migrations, connection, models


def add_index_task_config(_apps, _schema_editor):
    indexes = [
        ('analyze_textunitvector', 'transformer_id', 'analyze_textunitvector_transformer_id')
    ]
    with connection.cursor() as cursor:
        for tab_name, col_name, ind_pref in indexes:
            index_name = find_column_index(cursor, tab_name, col_name, ind_pref)
            cursor.execute('''
            INSERT INTO task_reindexroutine ("index_name", "target_entity", "schedule")
            VALUES (%s, %s, %s);''', [index_name, 'INDEX', '0 0 * * *'])


def find_column_index(cursor, table_name: str, column_name: str, index_name_preffix: str) -> str:
    cursor.execute(f'''
        select i.relname as index_name
        from
            pg_class t, pg_class i, pg_index ix, pg_attribute a
        where
            t.oid = ix.indrelid
            and i.oid = ix.indexrelid
            and a.attrelid = t.oid
            and a.attnum = ANY(ix.indkey)
            and t.relkind = 'r'
            and t.relname = %s
            and a.attname = %s
            and i.relname like '{index_name_preffix}%%';
        ''', (table_name, column_name,))
    for row in cursor.fetchall():
        return row[0]
    return ''


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0070_auto_20201208_1813'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReindexRoutine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index_name', models.CharField(db_index=True, max_length=512)),
                ('target_entity',
                 models.CharField(choices=[('INDEX', 'index'), ('TABLE', 'table')], db_index=True, default='INDEX',
                                  max_length=42)),
                ('schedule', models.CharField(db_index=True, max_length=42)),
            ],
        ),
        migrations.RunPython(add_index_task_config, reverse_code=migrations.RunPython.noop),
    ]
