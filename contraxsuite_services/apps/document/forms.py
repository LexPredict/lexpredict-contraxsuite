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
# -*- coding: utf-8 -*-

import json
import re
from django import forms
from django.conf import settings
from django.db.models import Count

from apps.common.widgets import FilterableProjectSelectField, FiltrableProjectSelectWidget
from apps.document.constants import DOCUMENT_TYPE_PK_GENERIC_DOCUMENT, DOCUMENT_FIELD_CODE_MAX_LEN
from apps.document.models import DocumentType, DocumentField
from apps.document.scheme_migrations.scheme_migration import CURRENT_VERSION, MIGRATION_TAGS
from apps.document.tasks import FindBrokenDocumentFieldValues, FixDocumentFieldCodes, MODULE_NAME
from apps.project.models import Project
from apps.document.tasks import ImportCSVFieldDetectionConfig
from task_names import TASK_NAME_IDENTIFY_CONTRACTS

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class ProjectModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f'{obj[1]} (#{obj[0]})'

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

    document_type = forms.ModelChoiceField(queryset=DocumentType.objects.exclude(pk=DOCUMENT_TYPE_PK_GENERIC_DOCUMENT),
                                           required=False)

    project_ids = ProjectModelMultipleChoiceField(
        queryset=Project.objects.exclude(type_id=DOCUMENT_TYPE_PK_GENERIC_DOCUMENT).order_by(
            '-pk').values_list('pk', 'name'),
        label='Projects',
        widget=forms.SelectMultiple(attrs={'class': 'chosen compact'}),
        required=False)

    document_name = forms.CharField(strip=True, required=False)

    existing_data_action = forms.ChoiceField(
        label='Existing Field Data',
        choices=(
            ('maintain', 'Maintain Reviewed Data'),
            ('delete', 'Delete all field data from the project and run fresh extraction'),
        ),
        help_text="""
        "Maintain Reviewed Data" will not modify anything on completed documents, 
        will not change the status on any accepted or rejected clauses, and will 
        not find any additional clauses for any fields that have already been 
        reviewed/modified. All other field data will be deleted and repopulated 
        based on current field detectors. Additional annotations may be added to 
        any documents which are not "completed".        
        """,
        initial='maintain',
        required=True)

    do_not_write = forms.BooleanField(label='Do not write detected values to DB (only log)',
                                      required=False)


class TrainDocumentFieldDetectorModelForm(PatchedForm):
    header = 'Train Document Field Detector Model'

    document_type = forms.ModelChoiceField(queryset=DocumentType.objects.all(), required=False)


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
        queryset=Project.objects.all().values_list('pk', 'name').order_by('-pk'),
        label='Train Data Projects',
        widget=forms.SelectMultiple(attrs={'class': 'chosen compact'}),
        required=False)

    test_data_projects_ids = ProjectModelMultipleChoiceField(
        queryset=Project.objects.all().values_list('pk', 'name').order_by('-pk'),
        label='Test Data Projects',
        widget=forms.SelectMultiple(attrs={'class': 'chosen compact'}),
        required=False)

    skip_training = forms.BooleanField(required=False)

    split_and_log_out_of_sample_test_report = forms.BooleanField(required=False)

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

    selected_columns = forms.CharField(required=False,
                                   help_text='''Columns to get detected value / search strings.
            Example: "A: B" means: column A contains value, column B - string to detect.\n
            "A,C: C,D" means: column A contains value, column C values are joined and prepended to 
            the value, search string resides in columns C and D''',
                                   initial='')

    save_in_csv_format = forms.BooleanField(
        required=False,
        initial=True,
        help_text='''Save detecting settings in one record''')

    wrap_in_wordbreaks = forms.BooleanField(
        required=False,
        initial=True,
        help_text='''Wrap search patterns in \\b ... \\b special symbols (word break)''')


class ExportDocumentTypeForm(forms.Form):
    header = 'Export Document Type'

    document_type = forms.ModelChoiceField(queryset=DocumentType.objects.all(), required=True)

    target_version = forms.ChoiceField(
        label='Target CS Version',
        choices=[(f'{MIGRATION_TAGS[c]}', c,) for c in MIGRATION_TAGS],
        help_text="""
            Optionally select previous ContraxSuite version here.
            """,
        initial='',
        required=False
    )


class ExportDocumentsForm(forms.Form):
    header = 'Export Documents'

    document_type = forms.ModelChoiceField(queryset=DocumentType.objects.all(), required=False)
    projects = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'class': 'chosen'}),
        required=False,
        help_text='Select one or several projects')
    export_files = forms.BooleanField(initial=True, required=False,
                                      help_text='Export original document files')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['projects'].choices = \
            [(p.pk, f'#{p.pk} {p.name} ({p.type.code}), {p.total} files') for p in
             Project.objects.annotate(total=Count('document')).order_by('-pk') if p.total]


class ImportDocumentTypeForm(forms.Form):
    header = 'Import Document Type'

    document_type_config_json_file = forms.FileField(required=True, label='Document Type JSON file')

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

    source_version = forms.ChoiceField(
        label='Source CS Version (optional)',
        choices=[(f'{MIGRATION_TAGS[c]}', c,) for c in MIGRATION_TAGS],
        help_text="""
                Optionally select version here if the input file was 
                obtained from older ContraxSuite installation.
                """,
        initial='',
        required=False
    )

    update_cache = forms.BooleanField(
        label='Documents: Cache document fields after import finished',
        initial=True,
        required=False)


class ImportDocumentsForm(forms.Form):
    header = 'Import Document Data'

    document_import_file = forms.FileField(required=True, label='Packed documents data (zip)')

    project = forms.ModelChoiceField(
        required=False,
        label='Import into existing project',
        queryset=Project.objects.order_by('-pk'),
        widget=forms.widgets.Select(attrs={'class': 'chosen'}))
    import_files = forms.BooleanField(initial=True, required=False,
                                      help_text='Import original document files')


class IdentifyContractsForm(forms.Form):
    header = TASK_NAME_IDENTIFY_CONTRACTS

    document_type = forms.ModelChoiceField(
        queryset=DocumentType.objects.all(),
        label='Document Type',
        required=False)

    recheck_contract = forms.BooleanField(required=False)

    project = FilterableProjectSelectField(queryset=Project.objects.all(),
                                           required=False,
                                           label='Restrict to project',
                                           widget=FiltrableProjectSelectWidget)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'].widget.manager_id = 'id_document_type'

    def _post_clean(self):
        super()._post_clean()
        self.cleaned_data['module_name'] = MODULE_NAME


class CloneDocumentFieldForm(forms.Form):
    R_FIELD_CODE = re.compile(r'^[a-z][a-z0-9_]*$')

    code = forms.CharField(
        max_length=DOCUMENT_FIELD_CODE_MAX_LEN,
        required=True)
    document_type = forms.ModelChoiceField(
        queryset=DocumentType.objects.all(),
        label='Clone to Document Type',
        required=True)

    def __init__(self, *args, **kwargs):
        # needed to use as ModalAdmin form
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['code'].initial = self.instance.code
            self.fields['document_type'].initial = self.instance.document_type

    class Meta:
        fields = ['code', 'document_type']
        readonly_fields = []

    def clean(self):

        code = self.cleaned_data.get('code')
        document_type = self.cleaned_data.get('document_type')

        if code:

            if not self.R_FIELD_CODE.match(code):
                self.add_error('code', '''Field codes must be lowercase, should start with a latin letter and contain 
                only latin letters, digits, and underscores. You cannot use a field code you have already used for this 
                document type.''')

            from apps.rawdb.constants import FIELD_CODE_ANNOTATION_SUFFIX
            reserved_suffixes = ('_sug', '_txt', FIELD_CODE_ANNOTATION_SUFFIX)
            # TODO: define reserved suffixes/names in field_value_tables.py? collect/autodetect?
            for suffix in reserved_suffixes:
                if code.endswith(suffix):
                    self.add_error('code', '''"{}" suffix is reserved.
                     You cannot use a field code which ends with this suffix.'''.format(suffix))

            if not document_type:
                return

            if DocumentField.objects.filter(document_type=document_type, code=code).exists():
                self.add_error('code', '''You cannot use a field code you have already used for this 
                document type.''')

    def save(self, commit=False):
        # needed to use as ModalAdmin form
        return self.instance

    def save_m2m(self):
        # needed to use as ModalAdmin form
        pass


class CloneDocumentTypeForm(forms.Form):
    R_FIELD_CODE = re.compile(r'^[a-z][a-z0-9_]*$')

    code = forms.CharField(
        max_length=DOCUMENT_FIELD_CODE_MAX_LEN,
        required=True)
    title = forms.CharField(
        max_length=100,
        required=True)

    def __init__(self, *args, **kwargs):
        # needed to use as ModalAdmin form
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['code'].initial = self.instance.code
            self.fields['title'].initial = self.instance.title

    def clean_code(self):

        code = self.cleaned_data.get('code')

        if code:
            if not self.R_FIELD_CODE.match(code):
                self.add_error('code', '''Document Type codes must be lowercase, 
                should start with a latin letter and contain 
                only latin letters, digits, and underscores.''')

            if DocumentType.objects.filter(code=code).exists():
                self.add_error('code', '''You cannot use a code you have already used for  
                Document Types.''')

        return code

    def save(self, commit=False):
        # needed to use as ModalAdmin form
        return self.instance

    def save_m2m(self):
        # needed to use as ModalAdmin form
        pass
