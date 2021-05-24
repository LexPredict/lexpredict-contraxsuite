from typing import List

from django.conf import settings
from django.db import migrations, connection


def remove_appvar_duplicates(_app, _schema):
    delete_list: List[int] = []
    existing_keys = set()
    with connection.cursor() as cursor:
        cursor.execute('''
            select id, category, name, project_id from common_appvar order by id desc;
        ''')
        for id, category, name, project_id in cursor.fetchall():
            key = (category, name, project_id,)
            if key in existing_keys:
                delete_list.append(id)
            else:
                existing_keys.add(key)
        print(f'Delete {len(delete_list)} duplicating AppVars')
        for id in delete_list:
            cursor.execute('delete from common_appvar where id = %s', [id])


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('common', '0040_document_locale_appvar'),
    ]

    operations = [
        migrations.RunPython(remove_appvar_duplicates, reverse_code=migrations.RunPython.noop)
    ]
