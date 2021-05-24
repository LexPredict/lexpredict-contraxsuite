from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('analyze', '0026_auto_20210324_1247'),
    ]

    # this migration creates DB records but don't upload actual files to webdav:
    # this should be done in start.sh
    operations = [
        migrations.RunSQL(
            '''
            INSERT INTO analyze_mlmodel (name, version, vector_name, 
                model_path, is_active, "default", apply_to, target_entity, 
                language, project_id) 
            VALUES
                ('Document default transformer (en)', '', '',
                 'models/en/transformer/document/model.pickle', 
                 true, true, 'document', 'transformer',
                 'en', null) ON CONFLICT DO NOTHING;
                 
            INSERT INTO analyze_mlmodel (name, version, vector_name, 
                model_path, is_active, "default", apply_to, target_entity, 
                language, project_id) 
            VALUES
                ('Text unit default transformer (en)', '', '',
                 'models/en/transformer/text_unit/model.pickle', 
                 true, true, 'text_unit', 'transformer',
                 'en', null) ON CONFLICT DO NOTHING;
            ''',
            reverse_sql=''
        )
    ]
