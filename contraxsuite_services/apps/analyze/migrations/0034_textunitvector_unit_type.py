from django.db import migrations, models, connection
import datetime
from apps.common.sql_commons import dropping_constraints_and_indexes
from apps.common.logger import CsLogger


logger = CsLogger.get_django_logger()


def log_message(msg: str):
    print(msg)
    logger.info(msg)


def add_column(_, __):
    table_name = 'analyze_textunitvector'
    log_message(f'0034_textunitvector_unit_type: start filling text unit detail at {datetime.datetime.now()}')
    with connection.cursor() as cursor:
        with dropping_constraints_and_indexes(cursor, table_name, logger_proc=lambda s: print(s)):
            start = datetime.datetime.now()
            cursor.execute(f'''
                UPDATE {table_name}
                SET unit_type = t.unit_type, 
                    vector_name = '[' || t.location_start::text || ', ' || t.location_end::text || ']'
                FROM document_textunit t 
                WHERE {table_name}.text_unit_id = t.id;''')
            taken = (datetime.datetime.now() - start).total_seconds()
    log_message(f'0034_textunitvector_unit_type: setting column values finished at {datetime.datetime.now()} ' +
                f'and took {taken} seconds')


class Migration(migrations.Migration):

    dependencies = [
        ('analyze', '0033_textunitvector_document'),
    ]

    operations = [
        # add new fields
        migrations.AddField(
            model_name='textunitvector',
            name='unit_type',
            field=models.CharField(blank=True, db_index=True, max_length=128, null=True),
        ),
        # fill values
        migrations.RunPython(add_column, reverse_code=migrations.RunPython.noop),
        # make fields obligatory
        migrations.AlterField(
            model_name='textunitvector',
            name='unit_type',
            field=models.CharField(db_index=True, null=False, blank=False, default='', max_length=128),
            preserve_default=False,
        ),
    ]
