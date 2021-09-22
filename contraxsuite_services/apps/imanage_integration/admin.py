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

from django.contrib import admin
from django.forms import ModelForm
from django.forms.utils import ErrorList

from apps.common.forms import FriendlyPasswordField
from apps.common.log_utils import ErrorCollectingLogger
from apps.common.script_utils import exec_script
from apps.project.models import Project
from apps.users.models import User
from apps.imanage_integration.models import IManageConfig, IManageDocument

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class IManageConfigForm(ModelForm):
    auth_password = FriendlyPasswordField(required=False)

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
                         use_required_attribute)
        eval_locals = IManageConfig.prepare_eval_locals({}, log=ErrorCollectingLogger())
        self.fields['project_resolving_code'].help_text = '''Python code returning correct Project to put the imported 
        document. Executed with Python exec. Should set "result" variable to the value it returns 
        (e.g. contain "result = 123" as its last line). 
        Local context: {0}'''.format(eval_locals)
        self.fields['assignee_resolving_code'].help_text = '''Python code returning correct User to assign the imported 
        document to. Executed with Python exec. Should set "result" variable to the value it returns 
        (e.g. contain "result = 123" as its last line). Local context: {0}'''.format(eval_locals)

    def clean(self):
        super().clean()
        example_doc = {
            'id': '12345',
            'document_number': '67890'
        }
        eval_locals = IManageConfig.prepare_eval_locals(example_doc, log=ErrorCollectingLogger())
        password = self.cleaned_data.get('auth_password')
        if password is False and self.instance and self.instance.pk:
            conf = IManageConfig.objects.filter(pk=self.instance.pk).first()  # type: IManageConfig
            if conf:
                self.cleaned_data['auth_password'] = conf.auth_password

        assignee = self.cleaned_data['assignee']
        project = self.cleaned_data['project']
        assignee_code = self.cleaned_data['assignee_resolving_code']
        project_code = self.cleaned_data['project_resolving_code']

        if project and project_code:
            self.add_error('project', 'Both project and project resolving code specified. '
                                      'Please use only one of the options.')

        if assignee and assignee_code:
            self.add_error('assignee', 'Both assignee and assignee resolving code specified.'
                                       'Please use only one of the options.')

        if assignee_code:
            try:
                test_value = exec_script('assignee resolving on a test document', assignee_code, eval_locals)
                if test_value is not None and not isinstance(test_value, User):
                    raise RuntimeError('Assignee resolving script must return either None or a User.')
            except RuntimeError as err:
                self.add_error('assignee_resolving_code', str(err).split('\n'))

        if project_code:
            try:
                test_value = exec_script('test project resolving', project_code, eval_locals)
                if not isinstance(test_value, Project):
                    raise RuntimeError('Project resolving script must return either a Project.')
            except RuntimeError as err:
                self.add_error('project_resolving_code', str(err).split('\n'))


class IManageConfigAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'code', 'root_url', 'document_type_code', 'last_sync_start', 'sync_frequency_minutes', 'enabled')
    search_fields = ('pk', 'code', 'root_url', 'document_type__code')

    form = IManageConfigForm

    @staticmethod
    def document_type_code(obj):
        return obj.document_type.code if obj.document_type else None


class IManageDocumentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'imanage_config_code', 'imanage_doc_id', 'imanage_doc_number', 'document')
    search_fields = ('pk', 'imanage_config_code', 'imanage_doc_id', 'imanage_doc_number')

    @staticmethod
    def imanage_config_code(obj):
        return obj.imanage_config.code if obj.imanage_config else None


admin.site.register(IManageConfig, IManageConfigAdmin)
admin.site.register(IManageDocument, IManageDocumentAdmin)
