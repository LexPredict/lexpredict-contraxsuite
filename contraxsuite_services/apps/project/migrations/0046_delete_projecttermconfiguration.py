# Generated by Django 2.2.13 on 2020-12-11 11:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0045_project_term_tags'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProjectTermConfiguration',
        ),
    ]