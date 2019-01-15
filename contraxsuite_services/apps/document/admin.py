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
import traceback
from typing import List

# Django imports
from django import forms
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib import admin
from django.contrib.postgres import fields
from django.db import transaction
from django.utils.html import format_html_join
from django_json_widget.widgets import JSONEditorWidget
from simple_history.admin import SimpleHistoryAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple

# Project imports
from apps.common.script_utils import ScriptError
from apps.document.field_types import FIELD_TYPES_REGISTRY
from apps.document.fields_detection.formula_based_field_detection import FormulaBasedFieldDetectionStrategy, \
    DocumentFieldFormulaError
from apps.document.fields_detection.formula_and_field_based_ml_field_detection import \
    FieldBasedMLOnlyFieldDetectionStrategy
from apps.document.fields_processing.field_processing_utils import order_field_detection
from apps.document.models import (
    Document, DocumentField, DocumentType,
    DocumentProperty, DocumentRelation, DocumentNote,
    DocumentFieldDetector, DocumentFieldValue, ExternalFieldValue,
    ClassifierModel, TextUnit, TextUnitProperty, TextUnitNote, TextUnitTag,
    DocumentFieldCategory)
from apps.document.python_coded_fields_registry import PYTHON_CODED_FIELDS_REGISTRY
from apps.document.fields_detection.stop_words import compile_stop_words, detect_value_with_stop_words
from apps.document.events import events

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.7/LICENSE"
__version__ = "1.1.7"
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
    list_display = ('name', 'document_type', 'source_type', 'paragraphs', 'sentences')
    search_fields = ['document_type__code', 'name']


class DocumentFieldForm(forms.ModelForm):
    depends_on_fields = forms.ModelMultipleChoiceField(
        queryset=DocumentField.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('depends_on_fields', False))

    class Meta:
        model = DocumentField
        fields = '__all__'
        exclude = ('long_code',)

    @classmethod
    def _extract_field_and_deps(cls, base_fields: List[DocumentField], fields_buffer: dict) -> dict:
        for field in base_fields:
            if field.code not in fields_buffer:
                fields_buffer[field.code] = field.get_depends_on_codes() or set()
                cls._extract_field_and_deps(field.depends_on_fields.all(), fields_buffer)
        return fields_buffer

    def clean(self):
        field_code = self.cleaned_data.get('code')
        formula = self.cleaned_data.get('formula')
        type_code = self.cleaned_data.get('type')
        depends_on_fields = self.cleaned_data.get('depends_on_fields') or []
        depends_on_fields = list(depends_on_fields)
        classifier_init_script = self.cleaned_data['classifier_init_script']
        stop_words = self.cleaned_data['stop_words']

        try:
            stop_words = compile_stop_words(stop_words)
            _v = detect_value_with_stop_words(stop_words, 'dummy text')
        except Exception as err:
            self.add_error('stop_words', str(err))

        try:
            FieldBasedMLOnlyFieldDetectionStrategy.init_classifier_impl(field_code, classifier_init_script)
        except ScriptError as err:
            self.add_error('classifier_init_script', str(err).split('\n'))

        fields_and_deps = {self.cleaned_data.get('code') or 'xxx': {f.code for f in depends_on_fields}}
        fields_and_deps = self._extract_field_and_deps(depends_on_fields, fields_and_deps)
        fields_and_deps = [(code, deps) for code, deps in fields_and_deps.items()]
        try:
            order_field_detection(fields_and_deps)
        except ValueError as ve:
            self.add_error(None, str(ve))

        fields_to_values = {field.code: FIELD_TYPES_REGISTRY[field.type].example_python_value(field)
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

        if not formula or not formula.strip() or not type_code:
            return self.cleaned_data

        try:
            FormulaBasedFieldDetectionStrategy.calc_formula(field_code, type_code, formula, fields_to_values)
        except DocumentFieldFormulaError as ex:
            base_error_class = type(ex.base_error).__name__
            base_error_msg = str(ex.base_error)
            lines = list()
            lines.append("Error caught while trying to execute formula on example values:")
            for field_name in ex.field_values:
                lines.append('{0}={1}'.format(field_name, ex.field_values[field_name]))
            lines.append("{0}. {1} in formula of field '{2}' at line {3}".format(base_error_class, base_error_msg,
                                                                                 ex.field_code, ex.line_number))
            self.add_error('formula', lines)
        except Exception:
            trace = traceback.format_exc()
            raise forms.ValidationError(
                'Tried to eval formula on example values:\n{0}\nGot error:\n{1}'.format(
                    str(fields_to_values), trace))

        return self.cleaned_data


class DocumentFieldAdmin(admin.ModelAdmin):
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
                'created_by', 'modified_by', 'code', 'title', 'type', 'document_type', 'category', 'order',
                'description',
                'confidence', 'requires_text_annotations', 'read_only', 'choices'),
        }),
        ('Frontend Options', {
            'fields': ('display_yes_no',),
        }),
        ('Field Detection: General', {
            'fields': ('value_detection_strategy', 'text_unit_type', 'depends_on_fields'),
        }),
        ('Field Detection: Regexp-based', {
            'fields': ('stop_words', 'value_regexp'),
        }),
        ('Field Detection: Machine Learning', {
            'fields': ('classifier_init_script', 'training_finished', 'dirty', 'trained_after_documents_number'),
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
        events.on_document_field_updated(obj)

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        events.on_document_field_deleted(obj)

    @staticmethod
    def user(obj):
        return obj.modified_by.username if obj.modified_by else None


class DocumentFieldDetectorAdmin(admin.ModelAdmin):
    list_display = (
        'field', 'detected_value', 'extraction_hint', 'include', 'regexps_pre_process_lower',
        'regexps_pre_process_remove_numeric_separators')
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
    def include(obj):
        return format_html_join('\n', '<pre>{}</pre>',
                                ((r,) for r in
                                 obj.include_regexps.split('\n'))) if obj.field else None


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
        required=False)

    def __init__(self, *args, **kwargs):
        prefix = kwargs.get('prefix')
        if prefix and kwargs.get('data') and kwargs.get('instance') is None:
            uid = kwargs['data'].get('{0}-uid'.format(prefix))
            if uid:
                kwargs['instance'] = DocumentField.objects.get(pk=uid)
        super().__init__(*args, **kwargs)
        self.base_instance = kwargs.get('instance')
        self._filter_tree = None
        for _, field in self.fields.items():
            print(field.widget.template_name)
        if self.base_instance:
            self.fields['field'].initial = self.base_instance
            self.fields['field'].widget.template_name = 'documentfield_admin_select.html'

    def save(self, *args, **kwargs):
        form_instance = self.cleaned_data['field']
        if form_instance != self.instance:
            self.instance.document_type = None
            self.instance.save()
            self.instance = form_instance
            self.instance.category = self.cleaned_data['category']
            self.instance.order = self.cleaned_data['order']
            self.instance.document_type = self.cleaned_data['document_type']
            with transaction.atomic():
                instance = super().save(commit=True)
                return instance


class DocumentFieldInlineAdmin(admin.TabularInline):
    field = forms.ModelChoiceField(
        queryset=DocumentField.objects.all(),
        required=False)

    fields = ['field', 'category', 'order']

    form = DocumentFieldFormInline
    model = DocumentField


class DocumentTypeForm(forms.ModelForm):
    search_fields = forms.ModelMultipleChoiceField(
        queryset=DocumentField.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('search_fields', False))


class DocumentTypeAdmin(ModelAdminWithPrettyJsonField):
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
        events.on_document_type_updated(obj)

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        events.on_document_type_deleted(obj)


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
        fields = ['name', 'order']

    fields = forms.ModelMultipleChoiceField(
        queryset=DocumentField.objects.all(),
        label='Select Type Fields',
        required=False,
        widget=FilteredSelectMultiple('fields', False))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
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
