# Generated by Django 2.2.13 on 2020-12-08 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0068_task_queue'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='restart_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='task',
            name='priority',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
