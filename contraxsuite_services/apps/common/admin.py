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
from django import forms
from django.db import models
from django.forms import TextInput, Textarea
from django.contrib import admin
from rest_framework_tracking.admin import APIRequestLogAdmin

from apps.common.decorators import get_function_from_str
# Project imports
from apps.common.models import AppVar, ReviewStatusGroup, ReviewStatus, Action, \
    CustomAPIRequestLog, APIRequestLog, MethodStats, MethodStatsCollectorPlugin, \
    MenuGroup, MenuItem, ThreadDumpRecord

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.3.0/LICENSE"
__version__ = "1.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class AppVarAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'user', 'description', 'date')
    search_fields = ('name', 'description')

    def save_model(self, request, obj: AppVar, form, change: bool):
        super().save_model(request, obj, form, change)


class ReviewStatusGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'order', 'is_active')
    search_fields = ('name', 'code')


class ReviewStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'order', 'group', 'is_active')
    search_fields = ('name', 'code')


class ActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'object', 'date')
    search_fields = ('name', 'user__username')


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
