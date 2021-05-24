from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0233_auto_20210222_0851'),
    ]

    operations = [
        migrations.RunSQL(
            '''update document_documentfield set "type" = 'related_info' where "type" = 'boolean'; '''
        ),
    ]