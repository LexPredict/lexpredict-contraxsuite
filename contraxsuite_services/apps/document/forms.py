"""
    Copyright (C) 2017, ContraxSuite, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    You can also be released from the requirements of the license by purchasing
    a commercial license from ContraxSuite, LLC. Buying such a license is
    mandatory as soon as you develop commercial activities involving ContraxSuite
    software without disclosing the source code of your own applications.  These
    activities include: offering paid services to customers as an ASP or "cloud"
    provider, processing documents on the fly in a web application,
    or shipping ContraxSuite within a closed source product.
"""

import json

from django import forms
from django.conf import settings

from apps.document.models import DocumentType, DocumentTypeField, DocumentField
from apps.document.tasks import MODULE_NAME
from apps.project.models import Project

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.6/LICENSE"
__version__ = "1.1.6"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DetectFieldValuesForm(forms.Form):
    header = 'Detect Field Values'

    document_type = forms.ModelChoiceField(queryset=DocumentType.objects.all(), required=False)

    document_name = forms.CharField(strip=True, required=False)

    do_not_write = forms.BooleanField(label='Do not write detected values to DB (only log)',
                                      required=False)

    drop_classifier_model = forms.BooleanField(
        label='Drop classifier and detect initial values with regexps', required=False)

    def _post_clean(self):
        super()._post_clean()
        self.cleaned_data['module_name'] = MODULE_NAME


class TrainDocumentFieldDetectorModelForm(forms.Form):
    header = 'Train Document Field Detector Model'

    document_type = forms.ModelChoiceField(queryset=DocumentType.objects.all(), required=False)

    def _post_clean(self):
        super()._post_clean()
        self.cleaned_data['module_name'] = MODULE_NAME


class CacheDocumentFieldsForm(forms.Form):
    header = 'Cache Document Fields'

    project = forms.ModelChoiceField(queryset=Project.objects.all(), required=False)

    def _post_clean(self):
        super()._post_clean()
        self.cleaned_data['module_name'] = MODULE_NAME


class DocumentTypeFieldModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "{0}: {1}".format(obj['document_type__code'], obj['document_field__code'])

    def clean(self, value):
        if not value:
            return super().clean(value)
        return json.loads(value.replace('\'', '"'))['pk']


class ProjectModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj[1]

    def clean(self, values):
        if not values:
            return super().clean(values)
        return [json.loads(value.replace('\'', '"'))[0] for value in values]


class TrainAndTestForm(forms.Form):
    header = 'Train And Test'

    document_type_field_id = DocumentTypeFieldModelChoiceField(
        queryset=DocumentTypeField.objects
            .exclude(document_field__value_detection_strategy__isnull=True)
            .exclude(document_field__value_detection_strategy=DocumentField.VD_DISABLED)
            .values('pk', 'document_type__code', 'document_field__code')
            .order_by('document_type__code', 'document_field__code'),
        label='Document Field',
        required=True)
    skip_training = forms.BooleanField(required=False)

    use_only_confirmed_field_values_for_training = forms.BooleanField(required=False)

    train_data_project_ids = ProjectModelMultipleChoiceField(
        queryset=Project.objects.all().values_list('pk', 'name'),
        label='Train Data Projects',
        widget=forms.SelectMultiple(attrs={'class': 'chosen compact'}),
        required=False)

    skip_testing = forms.BooleanField(required=False)

    use_only_confirmed_field_values_for_testing = forms.BooleanField(required=False)

    test_data_projects_ids = ProjectModelMultipleChoiceField(
        queryset=Project.objects.all().values_list('pk', 'name'),
        label='Test Data Projects',
        widget=forms.SelectMultiple(attrs={'class': 'chosen compact'}),
        required=False)

    def _post_clean(self):
        super()._post_clean()
        self.cleaned_data['module_name'] = MODULE_NAME


class LoadDocumentWithFieldsForm(forms.Form):
    header = 'Parse document fields in JSON format to create Document with Field Values.'
    project = forms.ModelChoiceField(queryset=Project.objects.all(), required=True)
    source_data = forms.CharField(
        max_length=1000,
        required=False,
        help_text='''
            Relative path to a folder with uploaded files. For example, "new" or "/".<br />
            You can choose any folder or file in "/media/%s" folder.<br />
            Create new folders and upload new documents if needed.
            ''' % settings.FILEBROWSER_DIRECTORY)
    document_name = forms.CharField(max_length=1024, required=False)
    document_fields = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text='Document fields in JSON format (field name - value pairs)'
    )
    run_detect_field_values = forms.BooleanField(required=False)


class ImportSimpleFieldDetectionConfigForm(forms.Form):
    header = 'Import Simple Field Detection Config'

    enctype = 'multipart/form-data'

    document_type = forms.ModelChoiceField(queryset=DocumentType.objects.all(), required=True)

    document_field = forms.ModelChoiceField(queryset=DocumentField.objects.all(), required=True)

    config_csv_file = forms.FileField(required=True)

    drop_previous_field_detectors = forms.BooleanField(required=False)

    update_field_choice_values = forms.BooleanField(required=False)

    def _post_clean(self):
        super()._post_clean()
        self.cleaned_data['module_name'] = MODULE_NAME
