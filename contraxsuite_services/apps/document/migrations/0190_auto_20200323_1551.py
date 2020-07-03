# Generated by Django 2.2.10 on 2020-03-23 15:51

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0189_auto_20200323_1551'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='textunittext',
            index=django.contrib.postgres.indexes.GinIndex(fields=['text_tsvector'],
                                                           name='idx_dtut_text_tsvector_gin'),
        ),
    ]