from django.contrib.postgres.search import SearchVectorField
from django.db import migrations, connection, models
import datetime
from apps.common.sql_commons import dropping_constraints_and_indexes
from apps.common.logger import CsLogger


logger = CsLogger.get_django_logger()


def log_message(msg: str):
    print(msg)
    logger.info(msg)


def merge_textunit(_, __):
    tu_table = 'document_textunit'
    tx_table = 'document_textunittext'

    log_message(f'0250_auto_20210830_0843: start merging tables at {datetime.datetime.now()}')
    with connection.cursor() as cursor:
        with dropping_constraints_and_indexes(cursor, tu_table, logger_proc=lambda s: print(s)):
            start = datetime.datetime.now()
            cursor.execute(f'''
                UPDATE {tu_table}
                SET text = t.text, text_tsvector=t.text_tsvector
                FROM {tx_table} t 
                WHERE {tu_table}.id = t.text_unit_id;''')
            taken = (datetime.datetime.now() - start).total_seconds()
    log_message(f'0250_auto_20210830_0843: merging tables finished at {datetime.datetime.now()} ' +
                f'and took {taken} seconds')


"""
Use this SQL script to repopulate document_textunittext:
INSERT INTO document_textunittext (text, text_unit_id, document_id, text_tsvector)
SELECT text, id, document_id, text_tsvector FROM document_textunit;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0250_auto_20210830_0843'),
    ]

    operations = [
        migrations.AddField(
            model_name='textunit',
            name='text',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='textunit',
            name='text_tsvector',
            field=SearchVectorField(null=True)
        ),
        migrations.RunPython(merge_textunit, reverse_code=migrations.RunPython.noop)
    ]
