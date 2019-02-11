from django import forms

from apps.document.tasks import MODULE_NAME
from apps.imanage_integration.models import IManageConfig
from apps.imanage_integration.tasks import IManageSynchronization


class IManageSyncTaskForm(forms.Form):
    header = IManageSynchronization.name

    imanage_config = forms.ModelChoiceField(
        queryset=IManageConfig.objects.all(),
        label='iManage Config',
        required=False)

    def _post_clean(self):
        super()._post_clean()
        self.cleaned_data['module_name'] = MODULE_NAME
