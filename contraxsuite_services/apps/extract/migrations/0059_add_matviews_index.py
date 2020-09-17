
from django.db import migrations, models
import django.db.models.deletion
from apps.document.constants import DOCUMENT_TYPE_PK_GENERIC_DOCUMENT


class Migration(migrations.Migration):
    dependencies = [
        ('extract', '0058_auto_20200713_1430'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE UNIQUE INDEX ON extract_projecttermusage (project_id, term_id);"
        ),
        migrations.RunSQL(
            "CREATE UNIQUE INDEX ON extract_projectgeoentityusage (project_id, entity_id);"
        ),
        migrations.RunSQL(
            "CREATE UNIQUE INDEX ON extract_projectpartyusage (project_id, party_id);"
        ),
        migrations.RunSQL(
            "CREATE UNIQUE INDEX ON extract_projectdefinitionusage (project_id, definition);"
        ),
    ]
