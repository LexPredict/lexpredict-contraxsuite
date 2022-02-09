from django.db import migrations, connection


trigger_name = 'dtut_text_tsvector_update'


def add_trigger(apps, schema_editor):
    AppVar = apps.get_model('common', 'AppVar')
    try:
        pg_full_text_search_locale = AppVar.objects.get(name='pg_full_text_search_locale').value
    except:
        pg_full_text_search_locale = 'english'

    with connection.cursor() as cursor:
        cursor.execute("""
            DROP TRIGGER IF EXISTS {} ON document_textunit;
        """.format(trigger_name))

    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TRIGGER {} BEFORE INSERT OR UPDATE
            ON document_textunit FOR EACH ROW EXECUTE FUNCTION
            tsvector_update_trigger(text_tsvector, 'pg_catalog.{}', text);
        """.format(trigger_name, pg_full_text_search_locale))


def drop_trigger(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("""
            DROP TRIGGER IF EXISTS {} ON document_textunit;
        """.format(trigger_name))


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0252_remove_textunittext'),
    ]

    operations = [
        migrations.RunPython(
            add_trigger,
            reverse_code=drop_trigger
        ),
    ]
