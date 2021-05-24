from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('analyze', '0031_auto_20210514_0722'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mlmodel',
            name='codebase_version',
            field=models.CharField(blank=True, db_index=True,
                                   help_text='ContraxSuite version in which the model was created', max_length=64,
                                   null=True),
        ),
        migrations.AlterField(
            model_name='mlmodel',
            name='target_entity',
            field=models.CharField(blank=True, choices=[('transformer', 'Transformer'),
                                                        ('classifier', 'Classifier'),
                                                        ('contract_type_classifier', 'Contract Type Classifier'),
                                                        ('is_contract', 'Contract / Generic Document Classifier')],
                                   db_index=True, help_text='The model class', max_length=26, null=True),
        ),
        migrations.AlterField(
            model_name='mlmodel',
            name='user_modified',
            field=models.BooleanField(db_index=True, default=False,
                                      help_text='User modified models are not automatically updated'),
        ),
        migrations.RunSQL(f'''
        INSERT INTO analyze_mlmodel (name, version, vector_name, 
                model_path, is_active, "default", apply_to, target_entity, 
                language, project_id, user_modified, codebase_version) 
        VALUES
                ('Document is contract (en)', '', '',
                 'models/en/is_contract', true, true, 'document', 'is_contract',
                 'en', null, false, '{settings.VERSION_NUMBER}') ON CONFLICT DO NOTHING;
        ''', reverse_sql='')
    ]
