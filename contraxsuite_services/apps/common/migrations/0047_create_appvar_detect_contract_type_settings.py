from json import dumps
from django.db import migrations


def run_migration(apps, schema_editor):

    AppVar = apps.get_model('common', 'AppVar')

    app_var, created = AppVar.objects.get_or_create(
        category='Document',
        name='detect_contract_type_settings',
        defaults={
            'category': 'Document',
            'name': 'detect_contract_type_settings',
            'value': dumps({
                'min_probability': 0.15,
                'max_closest_probability': 0.75,
                'pipeline_file_name': '',
                'pipeline_file_member': '',
                'fallback_to_lexnlp_default_pipeline': True,
            }),
            'description': """
min_probability (float; 0.0 - 1.0):
    The minimum predicted probability required to be considered a positive sample.<br/><br/>
max_closest_probability (float; 0.0 - 1.0):
    The second-highest prediction probability must be this less than the highest prediction probability multiplied 
    by this value.<br/> That is, if `predictions[1] > (predictions[0] * max_closest_probability)` then the `unknown_classification` will be 
    returned.<br/><br/>
pipeline_file_name (string):
    The name of the pipeline file to load.<br/><br/>
pipeline_file_member (string):
    If `pipeline_file_name` is an archive (tar or zip) containing more than one file, then ContraxSuite will 
    attempt to extract this member name.<br/><br/>
fallback_to_lexnlp_default_pipeline (boolean):
    Whether to load LexNLP's default contract type classifier if no pipeline pickle file could be found.
""",
        }
    )

    if not created:
        app_var.save()

    AppVar.objects.filter(
        category='Document',
        name='contract_type_filter',
    ).delete()


def revert_migration(apps, schema_editor):
    # Unfortunately this migration can not be reverted.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0046_update_old_project_actions'),
    ]

    operations = [
        migrations.RunPython(run_migration, reverse_code=revert_migration),
    ]
