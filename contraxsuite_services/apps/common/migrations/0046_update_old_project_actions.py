from django.db import migrations, connection


def do_migrate(_apps, _schema_editor):
    with connection.cursor() as cursor:
        cursor.execute('''UPDATE common_action SET "view_action" = 'update' WHERE "model_name" = 'Project' AND "name" = 'Detected Field Values';''')
        cursor.execute('''UPDATE common_action SET "view_action" = 'update' WHERE "model_name" = 'Project' AND "name" = 'Processed Similarity Tasks';''')


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0045_change_email_backend'),
    ]

    operations = [
        migrations.RunPython(do_migrate, reverse_code=migrations.RunPython.noop),
    ]
