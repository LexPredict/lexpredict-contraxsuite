from django.contrib import admin
from django.forms import ModelForm, PasswordInput
from django.forms.utils import ErrorList

from apps.common.script_utils import exec_script
from apps.project.models import Project
from apps.users.models import User
from .models import IManageConfig, IManageDocument


class IManageConfigForm(ModelForm):
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
                         use_required_attribute)
        eval_locals = IManageConfig.prepare_eval_locals({})
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
        eval_locals = IManageConfig.prepare_eval_locals(example_doc)
        password = self.cleaned_data.get('auth_password')
        if not password and self.instance and self.instance.pk:
            conf = IManageConfig.objects.filter(pk=self.instance.pk).first()  # type: IManageConfig
            if conf:
                self.cleaned_data['auth_password'] = conf.auth_password

        assignee_code = self.cleaned_data['assignee_resolving_code']
        project_code = self.cleaned_data['project_resolving_code']
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

    class Meta:
        model = IManageConfig
        fields = '__all__'
        widgets = {
            'auth_password': PasswordInput(),
        }


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
