# Generated by Django 2.2.4 on 2019-10-03 05:38

from django.db import migrations


def add_processed(apps, schema_editor):
    Document = apps.get_model('document', 'Document')
    Document.objects.all().update(processed=True)


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0157_migrate_fieldvalues'),
    ]

    operations = [
        migrations.RunPython(add_processed, reverse_code=migrations.RunPython.noop), ]
