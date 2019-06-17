from __future__ import unicode_literals
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '00136_delete_pending'),
    ]

    operations = [
        migrations.AddField(
            model_name='HistoricalDocument',
            name='delete_pending',
            field=models.BooleanField(blank=False, null=False, default=False)
        )
    ]
