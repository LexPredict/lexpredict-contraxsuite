from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0042_fix_appvar_indexes'),
    ]

    operations = [
        migrations.RunSQL('''UPDATE common_appvar SET description = 'Sets default document locale. Use ISO-639 codes, e.g., "en_US", "en_GB", or "de"' 
WHERE name = 'document_locale';'''),
    ]
