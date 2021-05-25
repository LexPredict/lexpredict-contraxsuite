# Generated by Django 2.2.13 on 2021-01-06 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyze', '0020_similarityrun_unit_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='documenttransformer',
            name='default',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='textunittransformer',
            name='default',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]