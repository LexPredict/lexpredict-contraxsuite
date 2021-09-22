from django.db import migrations, connection

class Migration(migrations.Migration):

    dependencies = [
        ('common', '0043_update_appvar_helptext'),
    ]

    operations = [
        migrations.RunSQL('''UPDATE common_appvar SET description = 'If True, additional uploads of the same file name and same content will be allowed and copy 01, copy 02, etc will be added to the name. If False, you will get an error rejecting the upload of duplicate documents.' 
        WHERE name = 'force_rewrite_doc';'''),
        # Invert previous value
        migrations.RunSQL('''UPDATE common_appvar SET value = '"duplicates"'::jsonb WHERE name = 'force_rewrite_doc' AND value = 'false'::jsonb;'''),
        migrations.RunSQL('''UPDATE common_appvar SET value = 'false'::jsonb WHERE name = 'force_rewrite_doc' AND value = 'true'::jsonb;'''),
        migrations.RunSQL('''UPDATE common_appvar SET value = 'true'::jsonb WHERE name = 'force_rewrite_doc' AND value = '"duplicates"'::jsonb;'''),
        # Rename appvar
        migrations.RunSQL('''        
            DO
            $do$
            BEGIN
               IF NOT EXISTS (SELECT * FROM common_appvar WHERE name='allow_duplicate_documents') THEN
                  UPDATE common_appvar SET name = 'allow_duplicate_documents' WHERE name = 'force_rewrite_doc';
               ELSE
                  DELETE FROM common_appvar WHERE name = 'force_rewrite_doc';
               END IF;
            END
            $do$        
        '''),
    ]
