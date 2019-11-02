# Generated by Django 2.2.4 on 2019-10-16 15:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0019_menugroup_menuitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='common.MenuGroup'),
        ),
    ]
