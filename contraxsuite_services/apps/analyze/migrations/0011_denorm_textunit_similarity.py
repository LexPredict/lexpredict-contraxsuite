from django.db import migrations, models, connection
import django.db.models.deletion

from settings import TEXTUNIT_SIMILARITY_MIGRATION_ACTION as migration_action

TABLE_NAME = 'analyze_textunitsimilarity'
MODEL_NAME = 'textunitsimilarity'


def purge():
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM {TABLE_NAME};")


def purge_or_skip(_apps, _schema_editor):
    if migration_action == 'delete':
        purge()


class Migration(migrations.Migration):
    dependencies = [
        ('document', '0203_auto_20200617_1327'),
        ('project', '0041_auto_20200522_0811'),
        ('analyze', '0010_transformer_unique_name'),
    ]

    operations = [
        migrations.RunPython(purge_or_skip, reverse_code=migrations.RunPython.noop),
        migrations.AddField(
            model_name=MODEL_NAME,
            name='document_a',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='similar_document_a_set',
                                    to='document.Document',
                                    null=True),
        ),
        migrations.AddField(
            model_name=MODEL_NAME,
            name='document_b',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='similar_document_b_set',
                                    to='document.Document',
                                    null=True),
        ),
        migrations.AddField(
            model_name=MODEL_NAME,
            name='project_a',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='similar_project_a_set',
                                    to='project.Project',
                                    null=True),
        ),
        migrations.AddField(
            model_name=MODEL_NAME,
            name='project_b',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='similar_project_b_set',
                                    to='project.Project',
                                    null=True),
        ),
    ]
