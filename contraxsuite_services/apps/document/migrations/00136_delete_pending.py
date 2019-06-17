from __future__ import unicode_literals
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0135_auto_20190510_0727'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='delete_pending',
            field=models.BooleanField(blank=False, null=False, default=False)
        )
    ]
