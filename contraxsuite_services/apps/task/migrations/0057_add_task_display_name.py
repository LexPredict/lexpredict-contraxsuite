from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0056_auto_20200206_1030'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='display_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='failure_reported',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]