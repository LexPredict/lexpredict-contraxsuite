# Generated by Django 2.2.13 on 2021-01-05 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyze', '0019_auto_20210105_0836'),
    ]

    operations = [
        migrations.AddField(
            model_name='similarityrun',
            name='unit_id',
            field=models.IntegerField(blank=True, db_index=True, null=True),
        ),
    ]