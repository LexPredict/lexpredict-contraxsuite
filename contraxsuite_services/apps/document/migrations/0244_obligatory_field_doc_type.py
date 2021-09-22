from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0243_remove_orphan_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentfield',
            name='document_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='document.DocumentType'),
        ),
    ]
