from django import forms

from apps.notifications.tasks import MODULE_NAME
from apps.users.models import User
from .models import DocumentDigestConfig


class SendDigestForm(forms.Form):
    header = 'Send Digest'

    config = forms.ModelChoiceField(DocumentDigestConfig.objects.all(), required=True)

    user = forms.ModelChoiceField(User.objects.all(), required=False)

    run_even_if_not_enabled = forms.BooleanField(required=False)

    def _post_clean(self):
        super()._post_clean()
        self.cleaned_data['module_name'] = MODULE_NAME
