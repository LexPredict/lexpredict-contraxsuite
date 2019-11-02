# Generated by Django 2.2.4 on 2019-10-04 19:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('common', '0018_auto_20190916_0730'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='Menu item group (folder) name.', max_length=100, unique=True)),
                ('public', models.BooleanField(default=False)),
                ('order', models.PositiveSmallIntegerField(default=0)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='created_menugroup_set', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='Menu item name.', max_length=100, unique=True)),
                ('url', models.CharField(db_index=True, help_text='Menu item name.', max_length=200, unique=True)),
                ('public', models.BooleanField(default=False)),
                ('order', models.PositiveSmallIntegerField(default=0)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.MenuGroup')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='created_menuitem_set', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
