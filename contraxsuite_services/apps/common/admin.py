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

# Django imports
import json
import os

from django import forms
from django.contrib import admin
from django.forms import ModelChoiceField
from django.http import HttpResponse, JsonResponse
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from rest_framework_tracking.admin import APIRequestLogAdmin
from django.db.models import Q, Case, Value, When, IntegerField

# Project imports
from apps.common.decorators import get_function_from_str
from apps.common.file_storage import get_file_storage
from apps.common.models import AppVar, ReviewStatusGroup, ReviewStatus, Action, \
    CustomAPIRequestLog, APIRequestLog, MethodStats, MethodStatsCollectorPlugin, \
    MenuGroup, MenuItem, ThreadDumpRecord, ObjectStorage, ExportFile, AppVarStorage, KnownAppVars
from apps.project.models import Project

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class AppVarListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Category'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'category'

    default_value = 'All'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        cats = set(AppVar.objects.values_list('category', flat=True))
        return sorted([(c, c) for c in cats], key=lambda c: c[0])
        # return [('Common', 'Common'), ('Document', 'Document'), ('Extract', 'Extract')]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if not self.value() or self.value() == 'All':
            return queryset
        return queryset.filter(category=self.value())


class AppVarAccessTypeFilter(admin.SimpleListFilter):
    title = 'Access Type'
    parameter_name = 'access_type'
    default_value = 'auth'

    def lookups(self, request, model_admin):
        return AppVar.ACCESS_TYPE_CHOICES

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(access_type=self.value())


class AppVarProjectFilter(admin.SimpleListFilter):
    title = 'Project'
    parameter_name = 'project'
    default_value = 'System'

    def lookups(self, request, model_admin):
        projects = set(Project.objects.values_list('id', 'name'))
        items = sorted([(id, f'{id}, {name}') for id, name in projects], key=lambda c: -c[0])
        return items

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if not self.value():
            return queryset.filter(project_id__isnull=True)
        return queryset.filter(Q(project_id=self.value()) | Q(project_id__isnull=True))


class AppVarProjectChoiceField(ModelChoiceField):
    def label_from_instance(self, obj: Project):
        return f'{obj.pk}, {obj.name}'


class AppVarAdminForm(forms.ModelForm):
    SELECTED_PROJECT = None

    class Meta:
        model = AppVar
        fields = ['category', 'name', 'value', 'user', 'description']
        widgets = {
            'value': forms.Textarea(
                attrs={
                    'rows': '2', 'cols': '95'
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Project.objects.order_by('-pk')
        if self.SELECTED_PROJECT:
            qs = Project.objects.annotate(
                custom_order=Case(
                    When(id=self.SELECTED_PROJECT, then=Value(999999)),
                    default='id',
                    output_field=IntegerField(),
                )
            ).order_by('-custom_order')

        self.fields['project'] = AppVarProjectChoiceField(queryset=qs, required=False)

    def clean(self):
        cleaned_data = super().clean()
        # {'value': 12, 'project': None, 'id': <AppVar: App Variable
        #  (category=Document name=allow_duplicate_documents project=None)>}
        app_var: AppVar = cleaned_data['id']
        if 'value' not in cleaned_data:
            return
        value = cleaned_data['value']
        try:
            AppVar.check_is_value_ok(app_var.category, app_var.name, value)
        except RuntimeError as e:
            self.add_error('value', e.args[0])


class AppVarAdmin(admin.ModelAdmin):
    actions = None
    list_display = ['category', 'name', 'access_type', 'project', 'value', 'custom_description']
    search_fields = ['name', 'description']
    list_editable = ['value', 'project']
    list_display_links = ['name']
    list_filter = (AppVarListFilter, AppVarProjectFilter, AppVarAccessTypeFilter)

    def custom_description(self, object):
        return mark_safe(object.description)

    custom_description.short_description = 'Description'

    def get_changelist_form(self, request, **kwargs):
        AppVarAdminForm.SELECTED_PROJECT = request.GET.get('project', None)
        return AppVarAdminForm

    def save_model(self, request, obj: AppVar, form, change: bool):
        # super().save_model(request, obj, form, change)
        
        AppVarStorage.set(obj.category, obj.name, obj.value,
                          obj.description, obj.access_type, obj.project_id, overwrite=True)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'project':
            kwargs['queryset'] = Project.objects.order_by('-id')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_display_links = None


class ExportFileAdminForm(forms.ModelForm):

    class Meta:
        model = AppVar
        fields = ['category', 'name', 'value', 'user', 'description']
        widgets = {
            'value': forms.Textarea(
                attrs={
                    'rows': '2', 'cols': '95'
                }
            )
        }


class ExportFileAdmin(admin.ModelAdmin):
    readonly_fields = ['get_link']
    list_display = ['file_path', 'get_link', 'comment',
                    'file_created', 'downloaded', 'email_sent',
                    'created_time']
    search_fields = ['file_path', 'comment']
    ordering = ('-created_time',)

    def get_changelist_form(self, request, **kwargs):
        return ExportFileAdminForm

    def get_link(self, obj: ExportFile):
        return obj.get_link()

    def download_file_data(self, request, *_args, **kwargs):
        exp_file = ExportFile.objects.get(pk=kwargs['object_id'])  # type: ExportFile
        storage = get_file_storage()
        file_data = storage.read(exp_file.file_path)
        file_name = os.path.basename(exp_file.file_path)
        response = HttpResponse(file_data, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        response['Content-Length'] = len(file_data)
        response['filename'] = file_name
        exp_file.downloaded = True
        exp_file.save()
        return response

    def file_download_ref(self, request, *_args, **kwargs):
        exp_file = ExportFile.objects.get(pk=kwargs['object_id'])  # type: ExportFile
        file_ref = ''
        if exp_file.file_created:
            file_ref = reverse('admin:download_file_data', args=[exp_file.pk])
        return JsonResponse({'file_reference': file_ref}, safe=False)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('download_file_data/<int:object_id>/',
                 self.download_file_data,
                 name='download_file_data'),
            path('file_download_ref/<int:object_id>/',
                 self.file_download_ref,
                 name='file_download_ref'),
        ]
        return my_urls + urls


class ReviewStatusGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'order', 'is_active')
    search_fields = ('name', 'code')


class ReviewStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'order', 'group', 'is_active')
    search_fields = ('name', 'code')


class ActionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'view_action', 'name', 'message', 'model_name', 'object_pk', 'date')
    search_fields = ('name', 'user__name', 'object_pk', 'message')


class MethodStatsAdmin(admin.ModelAdmin):
    list_display = ('method', 'path', 'name', 'date', 'time', 'args', 'kwargs', 'has_error')
    search_fields = ('name', 'method')


class ThreadDumpRecordAdminForm(forms.ModelForm):
    command_line = forms.CharField(widget=forms.Textarea(attrs={'style': 'width: 90%', 'rows': 2}))
    dump = forms.CharField(widget=forms.Textarea(attrs={'style': 'width: 90%', 'rows': 50}))

    class Meta:
        model = ThreadDumpRecord
        fields = '__all__'


class ThreadDumpRecordAdmin(admin.ModelAdmin):
    form = ThreadDumpRecordAdminForm
    list_display = ('date', 'node', 'pid', 'command_line', 'cpu_usage', 'cpu_usage_system_wide',
                    'memory_usage', 'memory_usage_system_wide')
    search_fields = ('date', 'node', 'pid', 'command_line')


class MethodStatsCollectorPluginForm(forms.ModelForm):
    class Meta:
        model = MethodStatsCollectorPlugin
        fields = '__all__'

    def clean_path(self):
        path = self.cleaned_data.get('path')
        try:
            get_function_from_str(path)
        except Exception as e:
            raise forms.ValidationError(str(e))
        return path


class MethodStatsCollectorPluginAdmin(admin.ModelAdmin):
    form = MethodStatsCollectorPluginForm
    list_display = ('path', 'name', 'log_sql', 'batch_size', 'batch_time')
    search_fields = ('path', 'name')


class MenuGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'public', 'user', 'order')
    search_fields = ('name',)


class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'public', 'url', 'order', 'user')
    search_fields = ('name',)


class ObjectStorageAdmin(admin.ModelAdmin):
    list_display = ('key', 'last_updated')
    search_fields = ('key',)


admin.site.unregister(APIRequestLog)

admin.site.register(CustomAPIRequestLog, APIRequestLogAdmin)
admin.site.register(AppVar, AppVarAdmin)
admin.site.register(ReviewStatusGroup, ReviewStatusGroupAdmin)
admin.site.register(ReviewStatus, ReviewStatusAdmin)
admin.site.register(Action, ActionAdmin)
admin.site.register(MethodStats, MethodStatsAdmin)
admin.site.register(MethodStatsCollectorPlugin, MethodStatsCollectorPluginAdmin)
admin.site.register(MenuGroup, MenuGroupAdmin)
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(ThreadDumpRecord, ThreadDumpRecordAdmin)
admin.site.register(ObjectStorage, ObjectStorageAdmin)
admin.site.register(ExportFile, ExportFileAdmin)
