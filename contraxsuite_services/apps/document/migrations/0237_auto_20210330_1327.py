# Generated by Django 2.2.18 on 2021-03-30 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0236_auto_20210330_1150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentfield',
            name='value_detection_strategy',
            field=models.CharField(choices=[('disabled', 'Field detection disabled'), ('use_regexps_only', 'No ML. Use regexp Field Detectors'), ('use_formula_only', 'No ML. Use formula only'), ('regexp_table', 'Use Multi-Line Field Detectors'), ('regexps_and_text_based_ml', 'Start with regexps, switch to text-based ML when possible'), ('text_based_ml_only', 'Use pre-trained text-based ML only'), ('formula_and_fields_based_ml', 'Start with formula, switch to fields-based ML when possible'), ('fields_based_ml_only', 'Use pre-trained field-based ML only'), ('fields_based_prob_ml_only', 'Use pre-trained field-based ML with "Unsure" category'), ('python_coded_field', 'Use python class for value detection'), ('field_based_regexps', 'Apply regexp Field Detectors to depends-on field values'), ('mlflow_model', 'Use pre-trained MLflow model to find matching text units')], default='use_regexps_only', max_length=50),
        ),
    ]