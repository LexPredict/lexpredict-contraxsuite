from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0234_boolean_to_related_type'),
    ]

    operations = [
        migrations.RunSQL(
            '''update document_documentfield set "type" = 'float' where "type" = 'amount'; '''
        ),
    ]