from __future__ import unicode_literals
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0030_auto_20190424_1047'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='delete_pending',
            field=models.BooleanField(blank=False, null=False, default=False)
        )
    ]
