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

# Standard imports
import inspect
import json
import re
import traceback
from typing import List, Dict, Any

# Django imports
from django import forms
from django.urls import reverse
from django.contrib import admin
from django.contrib.admin.actions import delete_selected
from django.contrib.admin.options import TO_FIELD_VAR
from django.contrib.admin.utils import get_deleted_objects, unquote
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.postgres import fields
from django.db import transaction
from django.db.models import Q
from django.template.response import TemplateResponse
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

# Third-party imports
from django_json_widget.widgets import JSONEditorWidget
from simple_history.admin import SimpleHistoryAdmin

# Project imports
from apps.common.script_utils import ScriptError
from apps.common.model_utils.model_class_dictionary import ModelClassDictionary
from apps.common.url_utils import as_bool
from apps.document import signals
from apps.document.field_types import RelatedInfoField
from apps.document.field_type_registry import FIELD_TYPE_REGISTRY
from apps.document.fields_detection.detector_field_matcher import DetectorFieldMatcher
from apps.document.fields_detection.field_based_ml_field_detection import init_classifier_impl
from apps.document.fields_detection.formula_based_field_detection import FormulaBasedFieldDetectionStrategy, \
    DocumentFieldFormulaError
from apps.document.fields_detection.stop_words import compile_stop_words, detect_value_with_stop_words
from apps.document.fields_processing.field_processing_utils import order_field_detection
from apps.document.models import (
    Document, DocumentField, DocumentType,
    DocumentProperty, DocumentRelation, DocumentNote,
    DocumentFieldDetector, DocumentFieldValue, ExternalFieldValue,
    ClassifierModel, TextUnit, TextUnitProperty, TextUnitNote, TextUnitTag,
    DocumentFieldCategory)
from apps.document.python_coded_fields_registry import PYTHON_CODED_FIELDS_REGISTRY
from apps.rawdb.field_value_tables import FIELD_CODE_ANNOTATION_SUFFIX
from apps.task.models import Task

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class ModelAdminWithPrettyJsonField(admin.ModelAdmin):
    """
    Mixin that prettifies JSON field representation
    """
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }


class PrettyJsonFieldMixin(object):
    """
    Mixin that prettifies JSON field representation
    """
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }


class DocumentAdmin(ModelAdminWithPrettyJsonField, SimpleHistoryAdmin):
    list_display = ('name', 'document_type', 'project', 'status_name', 'source_type', 'paragraphs', 'sentences')
    search_fields = ['document_type__code', 'name']

    def get_queryset(self, request):
        return Document.all_objects

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    @staticmethod
    def status_name(obj):
        return obj.status.name

    def has_delete_permission(self, request, obj=None):
        return False


class SoftDeleteDocument(Document):
    class Meta:
        proxy = True


class DeletePendingFilter(admin.SimpleListFilter):
    title = _('Status')

    parameter_name = 'delete_pending'

    def lookups(self, request, model_admin):
        return (
            ('deleting', _('Deleting')),
            ('all', _('All')),
        )

    def queryset(self, request, queryset):
        queryset = Document.all_objects
        val = self.value().lower() if self.value() else ''
        if val == 'all':
            return queryset
        return queryset.filter(delete_pending=True)


def set_soft_delete(document_ids:List[int], delete_not_undelete:bool, request):
    from apps.document.sync_tasks.soft_delete_document_task import SoftDeleteDocumentsSyncTask
    SoftDeleteDocumentsSyncTask().process(
        document_ids=document_ids,
        delete_not_undelete=delete_not_undelete)


def mark_deleting(modeladmin, request, queryset):
    # queryset.update(delete_pending=True)
    document_ids = list(queryset.values_list('pk', flat=True))
    set_soft_delete(document_ids, True, request)


mark_deleting.short_description = "Mark selected documents for deleting"


def unmark_deleting(_, request, queryset):
    document_ids = list(queryset.values_list('pk', flat=True))
    set_soft_delete(document_ids, False, request)


unmark_deleting.short_description = "Uncheck selected documents for deleting"


def delete_checked_documents(_, request, queryset):
    ids = [d.pk for d in queryset]
    request.session['_doc_ids'] = ids
    from django.http import HttpResponseRedirect
    return HttpResponseRedirect("./confirm_delete_view/")


delete_checked_documents.short_description = "Delete checked documents"


class SoftDeleteDocumentAdmin(DocumentAdmin):
    list_filter = [DeletePendingFilter]
    list_display = ('get_name', 'get_project', 'document_type', 'paragraphs', 'sentences', 'delete_pending')
    search_fields = ['name', 'document_type__code']
    actions = [mark_deleting, unmark_deleting, delete_checked_documents]
    change_list_template = 'admin/document/softdeletedocument/change_list.html'

    def get_project(self, obj):
        return obj.project.name if obj.project else ''

    get_project.short_description = 'Project'
    get_project.admin_order_field = 'project__name'

    def get_name(self, obj):
        display_text = "<a href={}>{}</a>".format(
                reverse('admin:{}_{}_change'.format(obj._meta.app_label,
                                                    obj._meta.model_name),
                        args=(obj.pk,)),
                obj.name)
        return mark_safe(display_text)

    get_name.short_description = 'Document'
    get_name.admin_order_field = 'name'

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def delete_all_checked(self, request):
        self.message_user(request, "Started deleting for all checked documents")
        ids = [d.pk for d in Document.all_objects.filter(delete_pending=True)]
        request.session['_doc_ids'] = ids
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect("../confirm_delete_view/")

    def confirm_delete_view(self, request):
        from apps.document.repository.document_bulk_delete \
            import get_document_bulk_delete
        doc_ids = request.session.get('_doc_ids')

        if request.method == 'GET':
            items_by_table = get_document_bulk_delete().calculate_deleting_count(doc_ids)
            mdc = ModelClassDictionary()
            del_count_hash = {mdc.get_model_class_name_hr(t):items_by_table[t]
                         for t in items_by_table if t in mdc.model_by_table}
            del_count = [(d, del_count_hash[d], False) for d in del_count_hash]
            del_count = sorted(del_count, key=lambda x: x[0])
            del_count.insert(0, ('Documents', len(doc_ids), True))

            context = {
                'deleting_count': del_count,
                'return_url': 'admin:document_softdeletedocument_changelist'
            }
            from django.shortcuts import render
            return render(request, "admin/common/confirm_delete_view.html", context)

        # POST: actual delete
        from apps.task.tasks import call_task
        call_task(
            task_name='DeleteDocuments',
            module_name='apps.document.tasks',
            _document_ids=doc_ids,
            user_id=request.user.id)
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect("../")

    def get_urls(self):
        urls = super().get_urls()
        from django.urls import path
        my_urls = [
            path('delete_all_checked/', self.delete_all_checked),
            path('confirm_delete_view/', self.confirm_delete_view),
        ]
        return my_urls + urls


PARAM_OVERRIDE_WARNINGS = 'override_warnings'


class UsersTasksValidationAdmin(admin.ModelAdmin):
    save_warning_template = 'admin/document/users_tasks_warning_save_form.html'
    delete_confirmation_template = 'admin/document/users_tasks_warning_delete_form.html'
    delete_selected_confirmation_template = 'admin/document/users_tasks_warning_delete_selected_form.html'

    class QSList(list):
        def __init__(self, qs):
            super().__init__(qs)
            self.qs = qs
            self.verbose_name = qs.model._meta.verbose_name
            self.verbose_name_plural = qs.model._meta.verbose_name_plural

        def count(self, **kwargs):
            return len(self)

        def delete(self):
            self.qs.delete()

    @classmethod
    def users_tasks_validation_enabled(cls):
        from apps.rawdb.app_vars import APP_VAR_DISABLE_RAW_DB_CACHING
        from apps.document.app_vars import ADMIN_RUNNING_TASKS_VALIDATION_ENABLED
        return not APP_VAR_DISABLE_RAW_DB_CACHING.val and ADMIN_RUNNING_TASKS_VALIDATION_ENABLED.val

    @classmethod
    def get_user_task_names(cls):
        if cls.users_tasks_validation_enabled():
            tasks = Task.objects \
                .get_active_user_tasks() \
                .distinct('name') \
                .order_by('name') \
                .values_list('name', flat=True)
            return list(tasks)
        else:
            return None

    WARN_CODE_TASKS_RUNNING = 'warning:tasks_running'

    @classmethod
    def validate_running_tasks(cls, request, dst_errors_dict: Dict[str, Any]):
        if not cls.users_tasks_validation_enabled():
            return

        if not as_bool(request.GET, PARAM_OVERRIDE_WARNINGS):
            user_tasks = UsersTasksValidationAdmin.get_user_task_names()
            if user_tasks:
                user_tasks = '; <br />'.join(user_tasks)
                dst_errors_dict[cls.WARN_CODE_TASKS_RUNNING] = f'''The following background tasks are running at 
                the current moment:\n<br />{user_tasks}.\n<br />
                The Save operation can cause their crashing because of the document type / field structure changes.'''

    def delete_selected_action(self, model_admin, request, qs):
        objects = UsersTasksValidationAdmin.QSList(qs)
        if request.POST.get('post'):
            deletable_objects, model_count, perms_needed, protected = get_deleted_objects(
                objects, request, model_admin.admin_site)
            if not protected:
                res = delete_selected(model_admin, request, objects)
                for obj in objects:
                    self.on_object_deleted(obj)
                return res
        response = delete_selected(model_admin, request, objects)
        context = response.context_data
        context['running_tasks'] = self.get_user_task_names() or None
        return TemplateResponse(request, model_admin.delete_selected_confirmation_template, context)

    def get_actions(self, request):
        actions = super().get_actions(request)
        func, name, title = actions['delete_selected']
        actions['delete_selected'] = (self.delete_selected_action, name, title)
        return actions

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        self.on_object_deleted(obj)

    def on_object_deleted(self, obj):
        raise RuntimeError('Not implemented')

    @classmethod
    def _get_confirm_action_name(cls, base_action):
        return '_confirm' + base_action

    def build_warning_context(self, object_id, form) -> dict:
        warning_context = {}
        user_tasks = self.get_user_task_names()
        if user_tasks:
            warning_context['running_tasks'] = user_tasks
        return warning_context

    def _prepare_form_template(self, request, object_id, extra_context=None):
        self.change_form_template = None
        if request.method == 'POST':
            base_actions = ['_save', '_continue', '_addanother']
            source_action = None
            for action in base_actions:
                if self._get_confirm_action_name(action) in request.POST:
                    request.POST = request.POST.copy()
                    request.POST[action] = request.POST[self._get_confirm_action_name(action)]
                    source_action = action
                    break
            if not source_action:
                form = None
                to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
                if not to_field or (to_field and self.to_field_allowed(request, to_field)):
                    obj = self.get_object(request, unquote(object_id), to_field) if object_id else None
                    ModelForm = self.get_form(request, obj)
                    form = ModelForm(request.POST, request.FILES, instance=obj)
                if not form or not form.is_valid():
                    return extra_context
                warning_context = self.build_warning_context(object_id, form)
                if warning_context:
                    for action in base_actions:
                        if action in request.POST:
                            extra_context = {**warning_context, **extra_context} if extra_context else warning_context
                            self.change_form_template = self.save_warning_template
                            extra_context['confirmation_button_name'] = self._get_confirm_action_name(action)
                            extra_context['source_action'] = action
                            break
        return extra_context

    def change_view(self, request, object_id, form_url='', extra_context=None):
        with transaction.atomic():
            extra_context = self._prepare_form_template(request, object_id, extra_context)
            return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def render_delete_form(self, request, context):
        context = context or {}
        context['running_tasks'] = self.get_user_task_names() or None
        return super().render_delete_form(request, context)

    @classmethod
    def get_confirmation_form(cls, form_class):

        class ConfirmationForm(form_class):
            def is_valid(self):
                return False

        return ConfirmationForm

    def get_form(self, request, obj=None, **kwargs):
        form_class = super().get_form(request, obj=None, **kwargs)
        if self.change_form_template == self.save_warning_template:
            form_class = self.get_confirmation_form(form_class)
        return form_class


class FieldValuesValidationAdmin(UsersTasksValidationAdmin):
    save_warning_template = 'admin/document/field_values_warning_save_form.html'

    def build_warning_context(self, object_id, form) -> dict:
        warning_context = super().build_warning_context(object_id, form)
        document_type_changed = 'document_type' in form.changed_data
        field_type_changed = 'type' in form.changed_data
        if object_id is not None and self.model is DocumentField \
                and (document_type_changed or field_type_changed):
            values_number = DocumentFieldValue.objects.filter(field=form.instance).count()
            if values_number > 0:
                user_values_number = DocumentFieldValue.objects \
                    .filter(field=form.instance) \
                    .filter(Q(created_by__isnull=False) | Q(modified_by__isnull=False) | Q(removed_by_user=True)) \
                    .count()
                if values_number > 0:
                    detected_values_number = values_number - user_values_number
                    detected_values_number = detected_values_number if detected_values_number > 0 else 0
                    warning_context['values_validation_user_values_number'] = user_values_number
                    warning_context['values_validation_detected_values_number'] = detected_values_number
                    modified_fields = None
                    if document_type_changed and field_type_changed:
                        modified_fields = 'document type and field type'
                    elif document_type_changed:
                        modified_fields = 'document type'
                    elif field_type_changed:
                        modified_fields = 'field type'
                    warning_context['values_validation_modified_fields'] = modified_fields
        return warning_context

    def add_view(self, request, form_url='', extra_context=None):
        with transaction.atomic():
            extra_context = self._prepare_form_template(request, None, extra_context)
            return super().add_view(request, form_url, extra_context)


class ModelFormWithUnchangeableFields(forms.ModelForm):
    """
    Mixin provides ability to freeze some fields of objects via form_field.disabled attribute -
    i.e. it doesn't allow to modify fields declared in iterable UNCHANGEABLE_FIELDS.
    Note that db object and form field should have the same name to make it working.
    """
    UNCHANGEABLE_FIELDS = ()

    @property
    def is_update(self):
        """
        Usually this check looks like `if self.instance.pk is not None` but
        instances with uid instead of id initially has pk
        """
        return self.Meta.model.objects.filter(pk=self.instance.pk).exists()

    def __init__(self, *args, **kwargs):
        """
        Set "form_field.disabled" attribute from UNCHANGEABLE_FIELDS
        """
        super().__init__(*args, **kwargs)
        if self.is_update:
            for field_name in self.UNCHANGEABLE_FIELDS:
                if field_name in self.fields:
                    self.fields[field_name].disabled = True
        for field_name in getattr(self.Meta, 'readonly_fields', []):
            if field_name in self.fields:
                self.fields[field_name].disabled = True
        for field in self.fields.values():
            if field.disabled and not isinstance(field.widget, forms.widgets.CheckboxInput):
                field.widget = forms.TextInput(attrs={'readonly': True})


class DocumentFieldForm(ModelFormWithUnchangeableFields):
    MAX_ESCAPED_FIELD_CODE_LEN = 50
    R_FIELD_CODE = re.compile(r'^[a-z][a-z0-9_]*$')

    UNCHANGEABLE_FIELDS = ('code', 'long_code', 'document_type', 'type', 'hide_until_js')

    depends_on_fields = forms.ModelMultipleChoiceField(
        queryset=DocumentField.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('depends_on_fields', False))

    hide_until_python = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text='Boolean expression in python syntax. Use field codes for this expression'
    )

    hide_until_js = forms.CharField(
        widget=forms.Textarea,
        required=False,
        disabled=True,
        help_text='Target expression ("Hide until python" expression converted to JavaScript syntax for frontend). '
                  'Allowed operators: +, -, *, /, ===, !==, ==, !=, &&, ||, >, <, >=, <=, %')

    long_code = forms.CharField(
        # widget=forms.Textarea,
        required=False,
        disabled=True)

    display_yes_no = forms.BooleanField(
        required=False,
        help_text='Display Yes if Related Info Text Found, otherwise No')

    classifier_init_script = forms.Field(required=False, widget=forms.Textarea,
                                         help_text=mark_safe('''Classifier initialization script. 
    Here is how it used: <br /><br />
    ''' + '<br />'.join(inspect.getsource(init_classifier_impl)
                        .replace(' ', '&nbsp;').replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
                        .split('\n'))))

    class Meta:
        model = DocumentField
        fields = '__all__'
        # exclude = ('long_code',)
        readonly_fields = ('created_by', 'modified_by')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'].required = True
        self.fields['order'].required = False
        self.fields['text_unit_type'].required = False
        self.fields['value_detection_strategy'].required = False
        self.fields['trained_after_documents_number'].required = False

    @classmethod
    def _extract_field_and_deps(cls, base_fields: List[DocumentField], fields_buffer: dict) -> dict:
        for field in base_fields:
            if field.code not in fields_buffer:
                fields_buffer[field.code] = field.get_depends_on_codes() or set()
                cls._extract_field_and_deps(field.depends_on_fields.all(), fields_buffer)
        return fields_buffer

    def calc_formula(self, field_code, type_code, formula, fields_to_values, form_field, formula_name='formula'):
        try:
            FormulaBasedFieldDetectionStrategy.calc_formula(field_code, type_code, formula, fields_to_values)
        except DocumentFieldFormulaError as ex:
            base_error_class = type(ex.base_error).__name__
            base_error_msg = str(ex.base_error)
            lines = list()
            lines.append('Error caught while trying to execute {0} on example values:'.format(formula_name))
            for field_name in ex.field_values:
                lines.append('{0}={1}'.format(field_name, ex.field_values[field_name]))
            lines.append("{0}. {1} in {2} of field '{3}' at line {4}".format(base_error_class,
                                                                             base_error_msg,
                                                                             formula_name,
                                                                             ex.field_code,
                                                                             ex.line_number))
            self.add_error(form_field, lines)
        except Exception:
            trace = traceback.format_exc()
            raise forms.ValidationError(
                'Tried to eval {0} on example values:\n{1}\nGot error:\n{2}'.format(formula_name,
                                                                                    str(fields_to_values),
                                                                                    trace))

    PARAM_CODE = 'code'

    def validate_field_code(self):

        field_code = self.cleaned_data.get(self.PARAM_CODE) or ''

        if not self.R_FIELD_CODE.match(field_code):
            self.add_error('code', '''Field codes must be lowercase, should start with a latin letter and contain 
            only latin letters, digits, and underscores. You cannot use a field code you have already used for this 
            document type.'''.format(field_code))

        reserved_suffixes = ('_sug', '_txt', FIELD_CODE_ANNOTATION_SUFFIX)
        # TODO: define reserved suffixes/names in field_value_tables.py? collect/autodetect?
        for suffix in reserved_suffixes:
            if field_code.endswith(suffix):
                self.add_error('code', '''"{}" suffix is reserved.
                 You cannot use a field code which ends with this suffix.'''.format(suffix))

    UNSURE_CHOICE_VALUE = 'unsure_choice_value'

    UNSURE_THRESHOLDS = 'unsure_thresholds_by_value'

    def clean(self):
        field_code = self.cleaned_data.get('code')
        formula = self.cleaned_data.get('formula')
        type_code = self.cleaned_data.get('type')
        depends_on_fields = self.cleaned_data.get('depends_on_fields') or []
        document_type = self.cleaned_data.get('document_type')
        depends_on_fields = list(depends_on_fields)
        classifier_init_script = self.cleaned_data['classifier_init_script']
        stop_words = self.cleaned_data.get('stop_words')
        hide_until_python = self.cleaned_data['hide_until_python']
        default_value = self.cleaned_data.get('default_value')
        unsure_choice_value = self.cleaned_data[self.UNSURE_CHOICE_VALUE]
        choice_values = DocumentField.parse_choice_values(self.cleaned_data['choices'])
        unsure_thresholds_by_value = self.cleaned_data.get(self.UNSURE_THRESHOLDS)

        try:
            field_type = FIELD_TYPE_REGISTRY[type_code]
        except KeyError:
            self.add_error('type', 'Unknown field type "{}".'.format(type_code))

        if unsure_choice_value and (not choice_values or unsure_choice_value not in choice_values):
            self.add_error(self.UNSURE_CHOICE_VALUE, '"Unsure choice value" must be listed in the choice values.')

        if unsure_thresholds_by_value is not None:
            if not hasattr(unsure_thresholds_by_value, 'items'):
                self.add_error(self.UNSURE_THRESHOLDS, 'Must be a dict of choice values to float thresholds [0..1]')
            else:
                if not choice_values:
                    self.add_error(self.UNSURE_THRESHOLDS, '"Unsure" thresholds are set but choice values are not.')
                if not unsure_choice_value:
                    self.add_error(self.UNSURE_THRESHOLDS, '"Unsure" thresholds are set but '
                                                           '"unsure" choice value is not.')

                if choice_values and unsure_choice_value:
                    for k, v in unsure_thresholds_by_value.items():
                        if k == unsure_choice_value:
                            self.add_error(self.UNSURE_THRESHOLDS, 'Please set thresholds only for "sure" choice '
                                                                   'values and not for ' + k)
                        elif k not in choice_values:
                            self.add_error(self.UNSURE_THRESHOLDS, 'Value not in choice values: ' + k)
                        if (not isinstance(v, int) and not isinstance(v, float)) or v < 0 or v > 1:
                            self.add_error(self.UNSURE_THRESHOLDS, 'Threshold should be a float value between 0 and 1: '
                                           + k)

        try:
            stop_words = compile_stop_words(stop_words)
            detect_value_with_stop_words(stop_words, 'dummy text')
        except Exception as err:
            self.add_error('stop_words', str(err))

        try:
            init_classifier_impl(field_code, classifier_init_script)
        except ScriptError as err:
            self.add_error('classifier_init_script', str(err).split('\n'))

        fields_and_deps = {self.cleaned_data.get('code') or 'xxx': {f.code for f in depends_on_fields}}
        fields_and_deps = self._extract_field_and_deps(depends_on_fields, fields_and_deps)
        fields_and_deps = [(code, deps) for code, deps in fields_and_deps.items()]
        try:
            order_field_detection(fields_and_deps)
        except ValueError as ve:
            self.add_error(None, str(ve))

        fields_to_values = {field.code: FIELD_TYPE_REGISTRY[field.type].example_python_value(field)
                            for field in depends_on_fields}

        python_coded_field_code = self.cleaned_data.get('python_coded_field')
        if python_coded_field_code:
            python_coded_field = PYTHON_CODED_FIELDS_REGISTRY.get(python_coded_field_code)
            if not python_coded_field:
                self.add_error('python_coded_field', 'Unknown Python-coded field: {0}'.format(python_coded_field_code))
            else:
                if type_code != python_coded_field.type:
                    self.add_error('type', 'Python-coded field {0} is of type {1} but {2} is specified'
                                           ' as the field type'.format(python_coded_field.title,
                                                                       python_coded_field.type,
                                                                       type_code))

        if formula and formula.strip() and type_code:
            self.calc_formula(field_code, type_code, formula, fields_to_values, 'formula')

        hide_until_python = hide_until_python.strip() if hide_until_python else None
        if hide_until_python:
            if not document_type:
                self.add_error('hide_until_python', 'Document type is not defined.')
            else:
                fields_to_values = {field.code: FIELD_TYPE_REGISTRY[field.type].example_python_value(field)
                                    for field in list(document_type.fields.all())}
                if field_code and field_code in fields_to_values:
                    del fields_to_values[field_code]
                if type_code:
                    fields_to_values[field_code] = FIELD_TYPE_REGISTRY[type_code] \
                        .example_python_value(self.instance)
    
                self.calc_formula(field_code,
                                  None,
                                  hide_until_python,
                                  fields_to_values,
                                  'hide_until_python',
                                  formula_name='hide until python')

        if default_value is not None:
            if type_code == RelatedInfoField.code:
                self.add_error('default_value', 'Related info field can\'t have default value')
            elif field_type.extract_from_possible_value(self.instance, default_value) != default_value:
                self.add_error('default_value', 'Wrong value for type {0}. Example: {1}'
                               .format(type_code, json.dumps(field_type.example_python_value(self.instance))))

        try:
            DocumentField.compile_value_regexp(self.cleaned_data['value_regexp'])
        except Exception as exc:
            self.add_error('value_regexp', exc)

        self.validate_field_code()

        if self.initial and 'type' in self.changed_data:
            wrong_field_detector_pks = []
            for field_detector in DocumentFieldDetector.objects.filter(field=self.instance):
                try:
                    DetectorFieldMatcher.validate_detected_value(type_code, field_detector.detected_value)
                except Exception:
                    wrong_field_detector_pks.append('#' + field_detector.pk)
            if wrong_field_detector_pks:
                self.add_error('type', 'Detected value is not allowed for this field type, please unset detected value '
                                       'for this field detectors: {0}'.format(', '.join(wrong_field_detector_pks)))

        return self.cleaned_data


class DocumentFieldAdmin(FieldValuesValidationAdmin):
    form = DocumentFieldForm
    list_display = (
        'document_type', 'code', 'category', 'order', 'title', 'description', 'type', 'formula', 'value_regexp', 'user',
        'modified_date', 'confidence')
    search_fields = ['document_type__code', 'code', 'category__name', 'title', 'description', 'created_by__username',
                     'confidence']
    filter_horizontal = ('depends_on_fields',)

    fieldsets = [
        ('General', {
            'fields': (
                'created_by', 'modified_by', 'code', 'long_code',
                'title', 'type', 'document_type', 'category', 'order', 'description',
                'confidence', 'requires_text_annotations', 'read_only', 'default_value'),
        }),
        ('Choice / Multi-choice Fields', {
            'fields': ('choices', 'allow_values_not_specified_in_choices'),
        }),
        ('Frontend Options', {
            'fields': ('hidden_always', 'hide_until_python', 'hide_until_js', 'display_yes_no',),
        }),
        ('Field Detection: General', {
            'fields': ('value_detection_strategy', 'text_unit_type', 'depends_on_fields'),
        }),
        ('Field Detection: Regexp-based', {
            'fields': ('stop_words', 'value_regexp'),
        }),
        ('Field Detection: Machine Learning', {
            'fields': ('classifier_init_script', 'unsure_choice_value', 'unsure_thresholds_by_value',
                       'training_finished', 'dirty', 'trained_after_documents_number'),
        }),
        ('Field Detection: Calculated Fields', {
            'fields': ('formula',),
        }),
        ('Field Detection: Python-coded Fields', {
            'fields': ('python_coded_field',),
        }),
        ('Metadata', {
            'fields': ('metadata',),
        }),
    ]

    def get_search_results(self, request, queryset, search_term):
        qs, has_duplicates = super().get_search_results(request, queryset, search_term)
        return qs.select_related('document_type', 'modified_by'), has_duplicates

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        signals.document_field_changed.send(self.__class__, user=request.user, document_field=obj)

    def on_object_deleted(self, obj):
        signals.document_field_deleted.send(self.__class__, user=None, document_field=obj)

    @staticmethod
    def user(obj):
        return obj.modified_by.username if obj.modified_by else None


class DocumentFieldDetectorForm(forms.ModelForm):
    def clean(self):
        try:
            DocumentFieldDetector.compile_regexps_string(self.cleaned_data['exclude_regexps'])
        except Exception as exc:
            self.add_error('exclude_regexps', exc)

        try:
            DocumentFieldDetector.compile_regexps_string(self.cleaned_data['include_regexps'])
        except Exception as exc:
            self.add_error('include_regexps', exc)

        try:
            DetectorFieldMatcher.validate_detected_value(self.cleaned_data['field'].type,
                                                         self.cleaned_data['detected_value'])
        except Exception as exc:
            self.add_error('detected_value', exc)

        return self.cleaned_data


class DocumentFieldDetectorAdmin(admin.ModelAdmin):
    form = DocumentFieldDetectorForm
    list_display = (
        'field', 'detected_value', 'extraction_hint', 'text_part', 'definition_words_',
        'exclude_regexps_', 'include_regexps_', 'regexps_pre_process_lower')
    search_fields = ['field__long_code', 'field__title', 'detected_value', 'extraction_hint', 'include_regexps']

    @staticmethod
    def document_type_code(obj):
        return obj.document_type.code if obj.document_type else None

    document_type_code.admin_order_field = 'document_type'

    @staticmethod
    def field_code(obj):
        return obj.field.code if obj.field else None

    field_code.admin_order_field = 'field'

    @staticmethod
    def include_regexps_(obj):
        return format_html_join('\n', '<pre>{}</pre>',
                                ((r,) for r in
                                 obj.include_regexps.split('\n'))) if obj.field and obj.include_regexps else None

    @staticmethod
    def exclude_regexps_(obj: DocumentFieldDetector):
        return format_html_join('\n', '<pre>{}</pre>',
                                ((r,) for r in
                                 obj.exclude_regexps.split('\n'))) if obj.field and obj.exclude_regexps else None


    @staticmethod
    def definition_words_(obj: DocumentFieldDetector):
        return format_html_join('\n', '<pre>{}</pre>',
                                ((r,) for r in
                                 obj.definition_words.split('\n'))) if obj.field and obj.definition_words else None


class DocumentFieldValueAdmin(admin.ModelAdmin):
    raw_id_fields = ('document', 'text_unit',)
    list_display = ('document_type', 'document', 'field', 'value', 'location_start',
                    'location_end', 'location_text', 'extraction_hint', 'user')
    search_fields = ['document__document_type__code', 'document__document_type__title',
                     'document__name', 'field__code', 'field__title', 'value', 'location_text',
                     'extraction_hint', 'modified_by__username', 'modified_by__first_name',
                     'modified_by__last_name']

    @staticmethod
    def document_type(obj):
        return obj.document.document_type if obj.document else None

    @staticmethod
    def field_code(obj):
        return obj.field.code if obj.field else None

    @staticmethod
    def user(obj):
        return obj.modified_by.username if obj.modified_by else None


class ExternalFieldValueAdmin(admin.ModelAdmin):
    list_display = ('field_id', 'value', 'extraction_hint')
    search_fields = ('field_id', 'value', 'extraction_hint')


class DocumentFieldInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        field_ids = set()
        dependencies = list()
        order_values = list()
        for form in self.forms:
            document_field = form.cleaned_data.get('document_field')
            if document_field:
                field_ids.add(document_field.pk)
                if document_field.depends_on_fields.count() > 0:
                    dependencies.append(form)
                order = form.cleaned_data.get('order')
                if order in order_values:
                    form.add_error(None, '"Order" value should be unique')
                else:
                    order_values.append(order)
        for form in dependencies:
            document_field = form.cleaned_data['document_field']
            missed_fields = list()
            depends_on_fields = list(document_field.depends_on_fields.all())
            for field in depends_on_fields:
                if field.pk not in field_ids:
                    missed_fields.append(field.code)
            if len(missed_fields) == 1:
                form.add_error(None, 'Field {0} is required for {1} field'.format(missed_fields[0],
                                                                                  document_field.code))
            elif len(missed_fields) > 1:
                form.add_error(None, 'Fields {0} is required for {1} field'.format(', '.join(missed_fields),
                                                                                   document_field.code))


class DocumentFieldFormInline(forms.ModelForm):
    field = forms.ModelChoiceField(
        queryset=DocumentField.objects.all(),
        required=False,
        empty_label=None)

    def __init__(self, *args, **kwargs):
        prefix = kwargs.get('prefix')
        if prefix and kwargs.get('data') and kwargs.get('instance') is None:
            uid = kwargs['data'].get('{0}-uid'.format(prefix))
            if uid:
                kwargs['instance'] = DocumentField.objects.get(pk=uid)
        super().__init__(*args, **kwargs)
        self.base_instance = kwargs.get('instance')

        if self.base_instance:
            self.fields['field'].queryset = DocumentField.objects\
                .filter(document_type=self.base_instance.document_type)\
                .order_by('long_code')

        self._filter_tree = None
        if self.base_instance:
            self.fields['field'].initial = self.base_instance
            self.fields['field'].widget.template_name = 'documentfield_admin_select.html'

    def save(self, *args, **kwargs):
        form_instance = self.cleaned_data['field']
        with transaction.atomic():
            if form_instance != self.instance:
                # self.instance.document_type = None
                # self.instance.save()
                self.instance = form_instance
                self.instance.category = self.cleaned_data['category']
                self.instance.order = self.cleaned_data['order']
                # self.instance.document_type = self.cleaned_data['document_type']
            return super().save(*args, **kwargs)


class DocumentFieldInlineAdmin(admin.TabularInline):
    field = forms.ModelChoiceField(
        queryset=DocumentField.objects.all(),
        required=False)

    fields = ['field', 'category', 'order']

    form = DocumentFieldFormInline
    model = DocumentField

    # We were going this inline table to only show the existing fields of this doc type but do not allow
    # adding them or deleting because adding in the current model actually means taking a field from another
    # doc type and putting it into this one. Changing doc type of a field makes all its existing values invalid
    # and they will be deleted.
    #
    # To disable add/delete django has the methods: has_add_permission(), has_delete_permission().
    # But when has_add_permission() returns False the table does not show the last row for some reason.
    #
    # Here is the workaround which makes the table showing only the existing items and no controls for adding:
    # - has_add_permission() returns True;
    # - number of extra rows is set to 0.
    #

    extra = 0
    max_num = 0

    def has_add_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False


class DocumentTypeForm(ModelFormWithUnchangeableFields):
    UNCHANGEABLE_FIELDS = ('code',)

    search_fields = forms.ModelMultipleChoiceField(
        label='Default Grid Column Headers',
        queryset=DocumentField.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Default Grid Column Headers', False))

    class Meta:
        model = DocumentType
        fields = '__all__'
        readonly_fields = ('created_by', 'modified_by')


class DocumentTypeAdmin(ModelAdminWithPrettyJsonField, UsersTasksValidationAdmin):
    list_display = ('code', 'title', 'fields_num', 'user', 'modified_date')
    search_fields = ['code', 'title', 'created_by__username']
    filter_horizontal = ('search_fields',)
    inlines = (DocumentFieldInlineAdmin,)
    form = DocumentTypeForm

    fieldsets = [
        ('General', {
            'fields': (
                'created_by', 'modified_by', 'code', 'title', 'editor_type', 'search_fields',),
        }),

        ('Document Import', {
            'fields': (
                'field_code_aliases',),
        }),

        ('Metadata', {
            'fields': (
                'metadata',),
        }),
    ]

    @staticmethod
    def fields_num(obj):
        return obj.fields.count()

    @staticmethod
    def user(obj):
        return obj.modified_by.username if obj.modified_by else None

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        signals.document_type_changed.send(self.__class__, user=None, document_type=obj)

    def on_object_deleted(self, obj):
        signals.document_type_deleted.send(self.__class__, user=None, document_type=obj)


class DocumentPropertyAdmin(admin.ModelAdmin):
    list_display = ('document', 'key', 'value')
    search_fields = ['document__name', 'key', 'value']


class TextUnitPropertyAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text_unit', 'key', 'value')
    search_fields = ['key', 'value']


class DocumentRelationAdmin(admin.ModelAdmin):
    list_display = ('document_a', 'document_b', 'relation_type')
    search_fields = ['document_a__name', 'document_a__name', 'relation_type']


class TextUnitAdmin(admin.ModelAdmin):
    list_display = ('document', 'unit_type', 'language')
    search_fields = ('document__name', 'document__name', 'unit_type', 'language')


class TextUnitTagAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'tag')
    search_fields = ('text_unit__unit_type', 'tag')


class TextUnitNoteAdmin(SimpleHistoryAdmin):
    list_display = ('text_unit', 'timestamp')
    search_fields = ('text_unit__unit_type', 'timestamp', 'note')


class DocumentNoteAdmin(SimpleHistoryAdmin):
    list_display = ('document', 'timestamp')
    search_fields = ('document__name', 'timestamp', 'note')


class ClassifierModelAdmin(SimpleHistoryAdmin):
    list_display = ('document_field',)
    search_fields = ('document_field__long_code', 'document_field__title')


class DocumentFieldCategoryForm(forms.ModelForm):
    class Meta:
        model = DocumentFieldCategory
        fields = ['name', 'order', 'export_key']

    fields = forms.ModelMultipleChoiceField(
        queryset=DocumentField.objects.all(),
        label='Select Type Fields',
        required=False,
        widget=FilteredSelectMultiple('fields', False))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['fields'].initial = self.instance.documentfield_set.all()

    def save(self, *args, **kwargs):
        # TODO: Wrap reassignments into transaction
        # NOTE: Previously assigned DocumentFieldCategory are silently reset
        instance = super().save(commit=True)
        self.fields['fields'].initial.update(category=None)
        self.cleaned_data['fields'].update(category=instance)
        return instance

    def save_m2m(self, *args, **kwargs):
        pass


class DocumentFieldCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    search_fields = ('name',)
    form = DocumentFieldCategoryForm


admin.site.register(Document, DocumentAdmin)
admin.site.register(SoftDeleteDocument, SoftDeleteDocumentAdmin)
admin.site.register(DocumentField, DocumentFieldAdmin)
admin.site.register(DocumentFieldDetector, DocumentFieldDetectorAdmin)
admin.site.register(DocumentFieldValue, DocumentFieldValueAdmin)
admin.site.register(ExternalFieldValue, ExternalFieldValueAdmin)
admin.site.register(ClassifierModel, ClassifierModelAdmin)
admin.site.register(DocumentType, DocumentTypeAdmin)
admin.site.register(DocumentRelation, DocumentRelationAdmin)
admin.site.register(DocumentProperty, DocumentPropertyAdmin)
admin.site.register(TextUnitProperty, TextUnitPropertyAdmin)
admin.site.register(TextUnit, TextUnitAdmin)
admin.site.register(TextUnitTag, TextUnitTagAdmin)
admin.site.register(TextUnitNote, TextUnitNoteAdmin)
admin.site.register(DocumentNote, DocumentNoteAdmin)
admin.site.register(DocumentFieldCategory, DocumentFieldCategoryAdmin)
