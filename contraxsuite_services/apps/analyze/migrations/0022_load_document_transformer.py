from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('analyze', '0021_auto_20210106_1009'),
    ]

    # this migration's no longer supported
    operations = [
        migrations.RunPython(migrations.RunPython.noop, reverse_code=migrations.RunPython.noop)
    ]
