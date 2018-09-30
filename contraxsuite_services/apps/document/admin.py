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

# Django imports
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.html import format_html_join
from simple_history.admin import SimpleHistoryAdmin

# Project imports
from apps.document.models import (
    Document, DocumentField, DocumentType,
    DocumentProperty, DocumentRelation, DocumentNote,
    DocumentFieldDetector, DocumentFieldValue, ExternalFieldValue,
    ClassifierModel, TextUnit, TextUnitProperty, TextUnitNote, TextUnitTag, DocumentTypeField,
    DocumentFieldFormulaError, DocumentTypeFieldCategory)
from apps.document.field_types import FIELD_TYPES_REGISTRY
from apps.document.python_coded_fields import PythonCodedField, PYTHON_CODED_FIELDS_REGISTRY


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.4/LICENSE"
__version__ = "1.1.4"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DocumentAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'document_type', 'source_type', 'paragraphs', 'sentences')
    search_fields = ['document_type__code', 'name']


class DocumentFieldForm(forms.ModelForm):
    class Meta:
        model = DocumentField
        fields = '__all__'

    def clean(self):
        field_code = self.cleaned_data.get('code')
        formula = self.cleaned_data.get('formula')
        type_code = self.cleaned_data.get('type')
        depends_on_fields = self.cleaned_data.get('depends_on_fields') or []
        fields_to_values = {field: FIELD_TYPES_REGISTRY[field.type].example_json_value(field)
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
            return

        try:
            DocumentField.calc_formula(field_code, type_code, formula, fields_to_values)
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
    list_display = ('code', 'title', 'description', 'type', 'formula', 'value_regexp', 'user', 'modified_date', 'confidence')
    search_fields = ['code', 'title', 'description', 'created_by__username', 'confidence']
    filter_horizontal = ('depends_on_fields',)

    @staticmethod
    def user(obj):
        return obj.modified_by.username if obj.modified_by else None


class DocumentFieldDetectorAdmin(admin.ModelAdmin):
    list_display = (
        'document_type', 'field', 'detected_value', 'extraction_hint',
        'include', 'regexps_pre_process_lower',
        'regexps_pre_process_remove_numeric_separators')
    search_fields = ['document_type', 'field', 'detected_value', 'extraction_hint',
                     'include_regexps']

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
    raw_id_fields = ('document', 'sentence',)
    list_display = ('document_type', 'document', 'field', 'value', 'location_start',
                    'location_end', 'location_text', 'extraction_hint', 'user')
    search_fields = ['document__document_type', 'document', 'field', 'value', 'location_text',
                     'extraction_hint', 'user']

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
    list_display = ('type_id', 'field_id', 'value', 'extraction_hint')
    search_fields = ('type_id', 'field_id', 'value', 'extraction_hint')


class DocumentFieldInlineFormset(forms.models.BaseInlineFormSet):

    def clean(self):
        field_ids = set()
        dependencies = list()
        for form in self.forms:
            document_field = form.cleaned_data.get('document_field')
            if document_field:
                field_ids.add(document_field.pk)
                if document_field.depends_on_fields.count() > 0:
                    dependencies.append(form)
        for form in dependencies:
            document_field = form.cleaned_data['document_field']
            missed_fields = list()
            for field in document_field.depends_on_fields.all():
                if field.pk not in field_ids:
                    missed_fields.append(field.code)
            if len(missed_fields) == 1:
                form.add_error(None, 'Field {0} is required for {1} field'.format(missed_fields[0],
                                                                                  document_field.code))
            elif len(missed_fields) > 1:
                form.add_error(None, 'Fields {0} is required for {1} field'.format(', '.join(missed_fields),
                                                                                   document_field.code))


class DocumentFieldInlineAdmin(admin.TabularInline):
    formset = DocumentFieldInlineFormset
    model = DocumentType.fields.through


class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'fields_num', 'user', 'fields', 'modified_date')
    search_fields = ['code', 'title', 'created_by__username']
    filter_horizontal = ('fields', 'search_fields')
    inlines = (DocumentFieldInlineAdmin,)

    @staticmethod
    def fields_num(obj):
        return obj.fields.count()

    @staticmethod
    def user(obj):
        return obj.modified_by.username if obj.modified_by else None


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
    list_display = ('document_type', 'document_field',)
    search_fields = ('document_type', 'document_field',)


class DocumentTypeFieldAdmin(admin.ModelAdmin):
    list_display = ('document_type', 'document_field', 'training_finished')
    search_fields = ['document_type', 'document_field']


class DocumentTypeFieldCategoryForm(forms.ModelForm):
    class Meta:
        model = DocumentTypeFieldCategory
        fields = ['name', 'order']

    type_fields = forms.ModelMultipleChoiceField(
        queryset=DocumentTypeField.objects.all(),
        label='Select Type Fields',
        required=False,
        widget=FilteredSelectMultiple('fields', False))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['type_fields'].initial = self.instance.documenttypefield_set.all()

    def save(self, *args, **kwargs):
        # FIXME: 'commit' argument is not handled
        # TODO: Wrap reassignments into transaction
        # NOTE: Previously assigned DocumentTypeFieldCategory are silently reset
        instance = super().save(commit=False)
        self.fields['type_fields'].initial.update(category=None)
        self.cleaned_data['type_fields'].update(category=instance)
        return instance


class DocumentTypeFieldCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    search_fields = ['name']
    form = DocumentTypeFieldCategoryForm


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
admin.site.register(DocumentTypeField, DocumentTypeFieldAdmin)
admin.site.register(DocumentTypeFieldCategory, DocumentTypeFieldCategoryAdmin)
