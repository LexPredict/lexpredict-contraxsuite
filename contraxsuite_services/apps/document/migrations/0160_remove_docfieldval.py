from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('document', '0159_auto_20191004_0608'),
    ]

    operations = [
        migrations.DeleteModel(name='documentfieldvalue')
    ]
