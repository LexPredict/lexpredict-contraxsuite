from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import ModelForm
from django.forms.utils import ErrorList

from apps.document.models import DocumentField
from .models import DocumentDigestConfig, DocumentDigestSendDate, DocumentNotificationSubscription


class DocumentDigestConfigForm(ModelForm):
    user_fields = forms.ModelMultipleChoiceField(
        queryset=DocumentField.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('user_fields', False))

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
                         use_required_attribute)

    def validate_int_csv(self, field: str, minn: int, maxx: int, max_items: int = 0):
        csv = self.cleaned_data.get(field)
        if csv is None:
            return

        errors = list()
        items = 0
        for s in csv.split(','):
            items += 1
            if max_items and items > max_items:
                self.add_error(field, 'Only {0} item(s) allowed.'.format(max_items))
                return

            s = s.strip()
            try:
                i = int(s)
                if i < minn:
                    errors.append('{i} is lesser than {min}'.format(i=i, min=minn))
                if i > maxx:
                    errors.append('{i} is greater than {max}'.format(i=i, max=maxx))
            except ValueError:
                errors.append('Can not convert to integer: {0}'.format(s))

        if errors:
            self.add_error(field, errors)

    def clean(self):
        dt = self.cleaned_data['document_type']
        fields = self.cleaned_data['user_fields']
        wrong_fields = list()
        for field in fields.all():  # type: DocumentField
            if field.document_type_id != dt.pk:
                wrong_fields.append(field)

        if wrong_fields:
            self.add_error('document_fields',
                           'Document fields should be owned by the specified document type.\n'
                           'The following fields do not match:\n'
                           '{wrong_fields}'.format(wrong_fields=';\n'.join([f.long_code for f in wrong_fields])))

        self.validate_int_csv('run_at_month', 1, 12)
        self.validate_int_csv('run_at_day_of_month', 1, 31)
        self.validate_int_csv('run_at_day_of_week', 1, 7)
        self.validate_int_csv('run_at_hour', 0, 23)
        self.validate_int_csv('run_at_minute', 0, 59, 1)


class DocumentNotificationSubscriptionForm(ModelForm):
    user_fields = forms.ModelMultipleChoiceField(
        queryset=DocumentField.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('user_fields', False))

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
                         use_required_attribute)

    def clean(self):
        dt = self.cleaned_data['document_type']
        fields = self.cleaned_data['user_fields']
        wrong_fields = list()
        for field in fields.all():  # type: DocumentField
            if field.document_type_id != dt.pk:
                wrong_fields.append(field)

        if wrong_fields:
            self.add_error('document_fields',
                           'Document fields should be owned by the specified document type.\n'
                           'The following fields do not match:\n'
                           '{wrong_fields}'.format(wrong_fields=';\n'.join([f.long_code for f in wrong_fields])))

        return super().clean()


class DocumentDigestSendDateForm(ModelForm):
    pass


class DocumentDigestSendDateAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'config', 'to', 'date')
    search_fields = ('pk',)

    form = DocumentDigestSendDateForm


class DocumentDigestConfigAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'document_type', 'for_role', 'for_user', 'documents_filter', 'period',
        'run_at_day_of_week', 'run_at_hour', 'run_at_minute')
    search_fields = ('pk', 'document_type__code', 'for_role__name', 'for_user__name', 'documents_filter', 'period')

    form = DocumentDigestConfigForm

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.change_form_template = 'notifications/digest_config_change.html'


class DocumentNotificationSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'document_type', 'event', 'recipients', 'specified_role', 'specified_user', 'enabled')
    search_fields = ('pk', 'document_type__code', 'event', 'recipients', 'specified_role__name', 'specified_user__name')

    form = DocumentNotificationSubscriptionForm

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.change_form_template = 'notifications/notification_subscription_change.html'


admin.site.register(DocumentDigestConfig, DocumentDigestConfigAdmin)
admin.site.register(DocumentNotificationSubscription, DocumentNotificationSubscriptionAdmin)
admin.site.register(DocumentDigestSendDate, DocumentDigestSendDateAdmin)
