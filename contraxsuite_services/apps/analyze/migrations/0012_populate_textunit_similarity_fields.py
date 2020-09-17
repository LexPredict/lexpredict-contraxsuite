import datetime

from django.db import migrations, connection

from apps.analyze.similarity_textunit_migration_common import drop_textunitsim_constraints, \
    restore_textunitsim_constraints
from settings import TEXTUNIT_SIMILARITY_MIGRATION_ACTION as migration_action

TABLE_NAME = 'analyze_textunitsimilarity'
MODEL_NAME = 'textunitsimilarity'


def denormalize():
    started = datetime.datetime.now()
    with connection.cursor() as cursor:
        print('Denormalizing t.u.s.: updating "document_a_id" [1/4]')
        cursor.execute(f'''UPDATE {TABLE_NAME} AS ts 
                           SET document_a_id = tt.document_id FROM document_textunit AS tt 
                           WHERE ts.text_unit_a_id = tt.id;''')

        elapsed = (datetime.datetime.now() - started).total_seconds()
        print(f'Denormalizing t.u.s.: updating "document_b_id" [2/4], {elapsed}s passed')
        cursor.execute(f'''UPDATE {TABLE_NAME} AS ts 
                           SET document_b_id = tt.document_id FROM document_textunit AS tt 
                           WHERE ts.text_unit_b_id = tt.id;''')

        elapsed = (datetime.datetime.now() - started).total_seconds()
        print(f'Denormalizing t.u.s.: updating "project_a_id" [3/4], {elapsed}s passed')
        cursor.execute(f'''UPDATE {TABLE_NAME} AS ts 
                           SET project_a_id = tt.project_id FROM document_document AS tt 
                           WHERE ts.document_a_id = tt.id;''')

        elapsed = (datetime.datetime.now() - started).total_seconds()
        print(f'Denormalizing t.u.s.: updating "project_b_id" [4/4], {elapsed}s passed')
        cursor.execute(f'''UPDATE {TABLE_NAME} AS ts 
                           SET project_b_id = tt.project_id FROM document_document AS tt 
                           WHERE ts.document_b_id = tt.id;''')

    elapsed = (datetime.datetime.now() - started).total_seconds()
    print(f'TextUnitSimilarityRefBuilder: {elapsed} seconds. Completed.')


def update_or_skip(_apps, _schema_editor):
    if migration_action != 'delete':
        denormalize()


class Migration(migrations.Migration):
    dependencies = [
        ('analyze', '0011_denorm_textunit_similarity'),
    ]

    operations = [
        migrations.RunPython(drop_textunitsim_constraints,
                             reverse_code=restore_textunitsim_constraints),
        migrations.RunPython(update_or_skip, reverse_code=migrations.RunPython.noop),
    ]
