# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-06-22 11:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_reviewstatus_is_active'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reviewstatus',
            options={'ordering': ['order', 'name', 'code'], 'verbose_name_plural': 'Review Statuses'},
        ),
    ]