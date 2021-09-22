from __future__ import unicode_literals
from typing import Dict
from django.db import migrations, models


def make_trans_name_unique(apps, schema_editor):
    DocumentTransformer = apps.get_model('analyze', 'DocumentTransformer')
    TextUnitTransformer = apps.get_model('analyze', 'TextUnitTransformer')
    classes = [DocumentTransformer, TextUnitTransformer]

    for model_class in classes:
        objects = list(model_class.objects.order_by('pk').all().defer(
            'version', 'vector_name', 'model_object', 'is_active'))
        name_count = {}  # type: Dict[str, int]
        for obj in objects:
            if obj.name not in name_count:
                name_count[obj.name] = 1
                continue
            while new_name := f'{obj.name} copy {name_count[obj.name]}' in name_count:
                name_count[obj.name] = name_count[obj.name] + 1
            name_count[obj.name] = name_count[obj.name] + 1
            obj.name = new_name
            obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('analyze', '0009_auto_20200127_1252'),
    ]

    operations = [
        migrations.RunPython(make_trans_name_unique, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='documenttransformer',
            name='name',
            field=models.CharField(db_index=True, max_length=1024, unique=True),
        ),
        migrations.AlterField(
            model_name='textunittransformer',
            name='name',
            field=models.CharField(db_index=True, max_length=1024, unique=True),
        ),
    ]
