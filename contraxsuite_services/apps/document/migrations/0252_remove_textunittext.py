import django.contrib.postgres.indexes
from django.db import migrations

from apps.common.migration_manager import RemoveIndexIfExists


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0251_merge_textunit'),
    ]

    operations = [
        RemoveIndexIfExists(
            model_name='textunittext',
            name='idx_dtut_text_gin',
        ),
        RemoveIndexIfExists(
            model_name='textunittext',
            name='idx_dtut_text_tsvector_gin',
        ),
        migrations.AddIndex(
            model_name='textunit',
            index=django.contrib.postgres.indexes.GinIndex(fields=['text'], name='idx_dtut_text_gin', opclasses=['gin_trgm_ops']),
        ),
        migrations.AddIndex(
            model_name='textunit',
            index=django.contrib.postgres.indexes.GinIndex(fields=['text_tsvector'], name='idx_dtut_text_tsvector_gin'),
        ),
        migrations.DeleteModel(
            name='TextUnitText',
        ),
    ]
