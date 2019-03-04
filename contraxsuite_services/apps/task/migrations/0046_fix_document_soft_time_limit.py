from __future__ import unicode_literals
from django.db import migrations


def fix_soft_time_limit_for_create_document_task(apps, schema_editor):
    TaskConfig = apps.get_model('task', 'TaskConfig')
    for task_config in TaskConfig.objects.filter(name='apps.task.tasks.create_document'):
        task_config.delete()
        break


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0045_fix_document_soft_time_limit'),
    ]

    operations = [
        migrations.RunPython(fix_soft_time_limit_for_create_document_task, reverse_code=migrations.RunPython.noop),
    ]
