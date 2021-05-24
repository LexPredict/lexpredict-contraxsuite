from django.conf import settings
from django.db import migrations, connection

from apps.common import redis


def clear_appvar_cache(_app, _schema):
    for key in redis.list_keys('app_var:*'):
        key = key.decode('utf-8')
        redis.popd(key, False)


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('common', '0036_auto_20210204_0833'),
    ]

    operations = [
        migrations.RunPython(clear_appvar_cache, reverse_code=migrations.RunPython.noop)
    ]