# Generated by Django 2.2.4 on 2019-10-03 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0008_documentnotificationsubscription_max_stack'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentnotificationsubscription',
            name='max_stack',
            field=models.IntegerField(blank=True, default=1, help_text='Messages limit per email.'),
        ),
    ]
