from __future__ import unicode_literals
import ast
from django.db import migrations


def fix_geography_field(apps, schema_editor):
    DocumentFieldValue = apps.get_model('document', 'DocumentFieldValue')
    for document_value in DocumentFieldValue.objects.filter(field__type='geography'):
        value = document_value.value
        try:
            if value and isinstance(value, str):
                value_obj = ast.literal_eval(value)
                entity_name = value_obj.get('entity__name') if value_obj and isinstance(value_obj, dict) else None
                if entity_name and isinstance(entity_name, str):
                    document_value.value = entity_name
                    document_value.save()
        except:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0097_auto_20181022_0813'),
    ]

    operations = [
        migrations.RunPython(fix_geography_field, reverse_code=migrations.RunPython.noop),
    ]
