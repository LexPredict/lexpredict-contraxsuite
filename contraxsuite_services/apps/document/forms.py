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

from apps.document.models import DocumentType, DocumentField
from apps.document.tasks import FindBrokenDocumentFieldValues, FixDocumentFieldCodes
from apps.document.tasks import MODULE_NAME
from apps.project.models import Project
from .tasks import ImportCSVFieldDetectionConfig

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.2/LICENSE"
__version__ = "1.2.2"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class ProjectModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj[1]

    def clean(self, values):
        if not values:
            return super().clean(values)
        return [json.loads(value.replace('\'', '"'))[0] for value in values]


class PatchedForm(forms.Form):
    def _post_clean(self):
        super()._post_clean()
        self.cleaned_data['module_name'] = MODULE_NAME


class DetectFieldValuesForm(PatchedForm):
    header = 'Detect Field Values'

    document_type = forms.ModelChoiceField(queryset=DocumentType.objects.all(), required=False)

    project_ids = ProjectModelMultipleChoiceField(
        queryset=Project.objects.all().values_list('pk', 'name'),
        label='Projects',
        widget=forms.SelectMultiple(attrs={'class': 'chosen compact'}),
        required=False)

    document_name = forms.CharField(strip=True, required=False)

    do_not_run_for_modified_documents = forms.BooleanField(
        label='Do not detect values for documents modified by user',
        initial=True,
        required=False)

    do_not_write = forms.BooleanField(label='Do not write detected values to DB (only log)',
                                      required=False)


class TrainDocumentFieldDetectorModelForm(PatchedForm):
    header = 'Train Document Field Detector Model'

    document_type = forms.ModelChoiceField(queryset=DocumentType.objects.all(), required=False)


class CacheDocumentFieldsForm(PatchedForm):
    header = 'Cache Document Fields'

    project = forms.ModelChoiceField(queryset=Project.objects.all(), required=False)


class FindBrokenDocumentFieldValuesForm(PatchedForm):
    header = FindBrokenDocumentFieldValues.name

    document_field = forms.ModelChoiceField(queryset=DocumentField.objects.all(), required=False)

    delete_broken = forms.BooleanField(required=False)


class FixDocumentFieldCodesForm(PatchedForm):
    header = FixDocumentFieldCodes.name


class TrainAndTestForm(forms.Form):
    header = 'Train And Test'

    document_field_id = forms.ModelChoiceField(
        queryset=DocumentField.objects.assigned_fields()
            .exclude(value_detection_strategy__isnull=True)
            .exclude(value_detection_strategy=DocumentField.VD_DISABLED),
        label='Document Field',
        required=True)

    train_data_project_ids = ProjectModelMultipleChoiceField(
        queryset=Project.objects.all().values_list('pk', 'name'),
        label='Train Data Projects',
        widget=forms.SelectMultiple(attrs={'class': 'chosen compact'}),
        required=False)

    test_data_projects_ids = ProjectModelMultipleChoiceField(
        queryset=Project.objects.all().values_list('pk', 'name'),
        label='Test Data Projects',
        widget=forms.SelectMultiple(attrs={'class': 'chosen compact'}),
        required=False)

    skip_training = forms.BooleanField(required=False)

    use_only_confirmed_field_values_for_training = forms.BooleanField(required=False)

    skip_testing = forms.BooleanField(required=False)

    use_only_confirmed_field_values_for_testing = forms.BooleanField(required=False)

    def _post_clean(self):
        super()._post_clean()
        self.cleaned_data['document_field_id'] = self.cleaned_data['document_field_id'].pk
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
            ''' % settings.FILEBROWSER_DOCUMENTS_DIRECTORY)
    document_name = forms.CharField(max_length=1024, required=False)
    document_fields = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text='Document fields in JSON format (field name - value pairs)'
    )
    run_detect_field_values = forms.BooleanField(required=False)


class ImportCSVFieldDetectionConfigForm(PatchedForm):
    header = ImportCSVFieldDetectionConfig.name

    enctype = 'multipart/form-data'

    document_field = forms.ModelChoiceField(queryset=DocumentField.objects.all(), required=True)

    config_csv_file = forms.FileField(required=True, help_text='''CSV file with rows of the following structure: 
    detected value,substring1,substring2,...,substringN . First row should contain column headers (ignored). 
    The task will create a regexp 
    field detector per each row. The detector will be returning the specified detected value if one of the 
    substrings found (include regexp will be: substring1\\nsubstring2\\n...\\nsubstringN). 
    ''')

    drop_previous_field_detectors = forms.BooleanField(required=False, help_text='''Drop previous field detectors 
    created by using this task for the specified field. The task marks the created field detectors with 
    "imported_simple_config" category and they can be easily found among the others.''', initial=True)

    update_field_choice_values = forms.BooleanField(required=False, help_text='''If set the choice values of the 
    specified field will be set to the sorted list of the "detected values" from the CSV file.''', initial=True)

    csv_contains_regexps = forms.BooleanField(required=False, help_text='''Check if the CSV file contains regexps in 
    aliases/substrings to search for. Otherwise the aliases will be treated as simply substrings to search for,
    spaces in them will be converted to \\s and maybe similar other conversions will be applied to bring them 
    to the regexp form usable in field detectors.''')


class ExportDocumentTypeForm(forms.Form):
    header = 'Export Document Type'

    document_type = forms.ModelChoiceField(queryset=DocumentType.objects.all(), required=True)


class ImportDocumentTypeForm(forms.Form):
    header = 'Import Document Type'

    document_type_config_csv_file = forms.FileField(required=True)

    action = forms.ChoiceField(
        label='Action',
        choices=(
            ('validate', 'Validate Only'),
            ('validate|import', 'Validate and import if valid'),
            ('import|auto_fix|retain_missing_objects',
             'Import and force auto-fixes – Retain extra fields / field detectors'),
            ('import|auto_fix|remove_missing_objects',
             'Import and force auto-fixes – Remove extra fields / field detectors from DB')
        ),
        help_text="""
        WARNING: 'Import and force auto-fixes – Remove extra fields/field detectors from DB' AND 'Import 
        and force auto-fixes – Retain extra fields/field detectors' can delete user data. It is recommended you 
        'Validate Only' first and review the log so you know what you are deleting.
        """,
        initial='validate',
        required=True)

    update_cache = forms.BooleanField(
        label='Documents: Cache document fields after import finished',
        initial=True,
        required=False)
