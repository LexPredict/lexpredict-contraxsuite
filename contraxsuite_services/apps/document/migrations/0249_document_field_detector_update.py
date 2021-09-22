from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0248_textunittext_document')
    ]

    operations = [
        migrations.RunSQL('''
            UPDATE document_documentfielddetector
            SET detect_limit_count = 0
            WHERE detect_limit_unit = 'NONE' AND detect_limit_count != 0;''', reverse_sql=''),
    ]
