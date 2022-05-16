# Generated by Django 2.2.20 on 2021-09-28 06:47

import apps.common.fields
from django.db import migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_add_doctype_manager_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='uid',
            field=apps.common.fields.StringUUIDField(default=uuid.uuid4, editable=False),
        ),
    ]