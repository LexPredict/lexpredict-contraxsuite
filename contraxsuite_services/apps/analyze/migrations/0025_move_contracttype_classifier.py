import os
from django.db import migrations, connection

from apps.common.file_storage import get_file_storage


def move_classifier(apps, schema_editor):
    # move "models/en/contract_class" folder's content
    # to models/en/contract_type_classifier/document
    src = 'models/en/contract_class'
    dest = 'models/en/contract_type_classifier/document'
    file_storage = get_file_storage()
    file_storage.ensure_folder_exists(dest)
    files_moved = 0
    for file in file_storage.list(src):
        file_name_only = os.path.basename(file)
        dest_path = os.path.join(dest, file_name_only)
        file_storage.rename_file(file, dest_path, move_file=True)
        files_moved += 1
    print(f'{files_moved} files are moved to "{dest}"')

    # create MLModel record
    with connection.cursor() as cursor:
        cursor.execute(f"""
            INSERT INTO analyze_mlmodel (name, version, vector_name, 
                model_path, is_active, "default", apply_to, target_entity, 
                language, project_id) 
            VALUES
                ('Document contract class classifier (en)', '', '',
                 %s, true, true, 'document', 'contract_type_classifier',
                 'en', null) ON CONFLICT DO NOTHING;""", [dest])


class Migration(migrations.Migration):
    dependencies = [
        ('analyze', '0024_add_mlmodel'),
    ]

    operations = [
        migrations.RunPython(move_classifier, reverse_code=migrations.RunPython.noop)
    ]
