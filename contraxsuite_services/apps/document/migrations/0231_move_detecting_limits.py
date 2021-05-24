from typing import Dict

from django.db import migrations, models, connection


class DetectingOptions:
    def __init__(self,
                 field_id: str,
                 limit_unit: str,
                 limit_count: int):
        self.field_id = field_id
        self.limit_unit = limit_unit
        self.limit_count = limit_count


def add_detector_limits(_apps, _schema_editor):
    field_options = []

    with connection.cursor() as cursor:
        cursor.execute('''SELECT "uid", detect_limit_unit, detect_limit_count FROM document_documentfield;''')
        for uid, detect_limit_unit, detect_limit_count in cursor.fetchall():
            field_options.append(DetectingOptions(uid, detect_limit_unit, detect_limit_count))

        for opt in field_options:
            cursor.execute('''UPDATE document_documentfielddetector SET 
                detect_limit_unit=%s, detect_limit_count=%s WHERE field_id = %s''',
                           [opt.limit_unit, opt.limit_count, opt.field_id])


def add_field_limits(_apps, _schema_editor):
    field_options: Dict[str, DetectingOptions] = {}

    with connection.cursor() as cursor:
        cursor.execute('''SELECT field_id, detect_limit_unit, detect_limit_count FROM document_documentfielddetector;''')
        for field_id, detect_limit_unit, detect_limit_count in cursor.fetchall():
            field_options[field_id] = DetectingOptions(field_id, detect_limit_unit, detect_limit_count)

        for field_id in field_options:
            opt = field_options[field_id]
            cursor.execute('''UPDATE document_documentfield SET 
                detect_limit_unit=%s, detect_limit_count=%s WHERE uid = %s''',
                           [opt.limit_unit, opt.limit_count, opt.field_id])
        

class Migration(migrations.Migration):

    dependencies = [
        ('document', '0230_auto_20210212_2324'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentfielddetector',
            name='detect_limit_count',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='documentfielddetector',
            name='detect_limit_unit',
            field=models.CharField(
                choices=[('NONE', 'No limits'),
                         ('UNIT', 'Limit to N documents units'), ('SENTENCE', 'Limit to N sentences'),
                         ('PARAGRAPH', 'Limit to N paragraphs'), ('PAGE', 'Limit to N pages'),
                         ('CHAR', 'Limit to N characters')], default='NONE', max_length=10),
        ),

        migrations.RunPython(add_detector_limits, reverse_code=add_field_limits),

        migrations.RemoveField(
            model_name='documentfield',
            name='detect_limit_unit',
        ),
        migrations.RemoveField(
            model_name='documentfield',
            name='detect_limit_count',
        )
    ]
