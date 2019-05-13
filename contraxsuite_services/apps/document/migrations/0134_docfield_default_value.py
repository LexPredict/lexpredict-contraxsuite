from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0133_auto_20190424_1038'),
    ]

    operations = [
        migrations.RunSQL('update document_documentfield set default_value = \'null\' where default_value = \'""\';')
    ]
