from __future__ import unicode_literals
from django.db import migrations
from django.db.models import IntegerField


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0046_fix_document_soft_time_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='priority',
            field=IntegerField(blank=False, null=False, default=0)
        )
    ]
