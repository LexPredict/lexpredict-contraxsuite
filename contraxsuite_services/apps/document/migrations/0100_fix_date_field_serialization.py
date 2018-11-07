from __future__ import unicode_literals

from django.db import migrations


def do_migrate(apps, schema_editor):
    DocumentFieldValue = apps.get_model('document', 'DocumentFieldValue')
    for document_value in DocumentFieldValue.objects.filter(field__type='date'):
        value = document_value.value
        try:
            if isinstance(value, int):
                document_value.delete()
        except:
            pass


class Migration(migrations.Migration):
    dependencies = [
        ('document', '0099_auto_20181025_1253'),
    ]

    operations = [
        migrations.RunPython(do_migrate, reverse_code=migrations.RunPython.noop),
    ]
