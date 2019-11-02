# Generated by Django 2.2.4 on 2019-10-04 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0158_update_processed'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentfield',
            name='detect_limit_count',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='documentfield',
            name='detect_limit_unit',
            field=models.CharField(choices=[('UNIT', 'Limit to N documents units'), ('SENTENCE', 'Limit to N sentences'), ('PARAGRAPH', 'Limit to N paragraphs'), ('PAGE', 'Limit to N pages'), ('CHAR', 'Limit to N characters')], default='UNIT', max_length=10),
        ),
    ]
