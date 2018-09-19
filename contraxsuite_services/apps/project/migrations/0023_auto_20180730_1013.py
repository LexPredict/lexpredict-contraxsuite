# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-07-30 10:13
from __future__ import unicode_literals

import apps.common.fields
from django.db import migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0022_project_super_reviewers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadsession',
            name='uid',
            field=apps.common.fields.StringUUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]