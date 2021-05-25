# Generated by Django 2.2.13 on 2021-03-19 13:31

import apps.analyze.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0050_auto_20210222_0851'),
        ('analyze', '0023_auto_20210323_0714'),
    ]

    operations = [
        migrations.CreateModel(
            name='MLModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=1024)),
                ('version', models.CharField(db_index=True, max_length=1024)),
                ('vector_name', models.CharField(blank=True, db_index=True, max_length=1024, null=True)),
                ('model_path', models.CharField(db_index=True, max_length=1024, unique=True)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('default', models.BooleanField(db_index=True, default=False)),
                ('apply_to', models.CharField(blank=True, choices=[('document', 'Document'), ('text_unit', 'Text Unit')],
                                              db_index=True, max_length=26, null=True)),
                ('target_entity', models.CharField(blank=True,
                                                   choices=[('transformer', 'Transformer'),
                                                            ('classifier', 'Classifier'),
                                                            ('contract_type_classifier', 'Contract Type Classifier')],
                                                   db_index=True, max_length=26, null=True)),
                ('language', models.CharField(blank=True, db_index=True, max_length=12, null=True)),
                ('project', models.ForeignKey(blank=True, default=None, null=True,
                                              on_delete=django.db.models.deletion.CASCADE, to='project.Project')),
            ],
            options={
                'ordering': ('name', 'vector_name', 'target_entity', 'apply_to'),
                'unique_together': {('name', 'version', 'target_entity', 'apply_to', 'language', 'project')},
            },
            managers=[
                ('document_transformers', apps.analyze.models.MLDocumentTransformerModelManager()),
                ('textunit_transformers', apps.analyze.models.MLTextUnitTransformerModelManager()),
                ('document_classifiers', apps.analyze.models.MLDocumentClassifierModelManager()),
                ('textunit_classifiers', apps.analyze.models.MLTextUnitClassifierModelManager()),
                ('document_contract_classifiers', apps.analyze.models.MLDocumentContractClassifierModelManager()),
                ('textunit_contract_classifiers', apps.analyze.models.MLTextUnitContractClassifierModelManager()),
            ],
        ),
    ]