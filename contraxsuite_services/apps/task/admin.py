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

# Third-party imports
from typing import List

import croniter
from django import forms
from django.db import connection
from django_celery_results.models import TaskResult
from simple_history.admin import SimpleHistoryAdmin

# Django imports
from django.contrib import admin

# Project imports
from apps.task.models import Task, TaskConfig, ReindexRoutine

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TaskAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'status', 'user', 'date_start', 'has_error')
    search_fields = ('name',)


class TaskConfigAdmin(SimpleHistoryAdmin):
    list_display = (
        'name', 'soft_time_limit')
    search_fields = ('name',)


class CeleryResultAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'status', 'date_done')
    search_fields = ('task_id',)


class ReindexRoutineChangeForm(forms.ModelForm):
    class Meta:
        model = ReindexRoutine
        fields = ('target_entity', 'index_name', 'schedule',)

    INDEX_CHOICES = ()

    index_name = forms.ChoiceField(choices=INDEX_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['index_name'].choices = \
            [(c, c) for c in ReindexRoutineAdmin.get_db_index_names()] + \
            [(c, c) for c in ReindexRoutineAdmin.get_db_table_names()]

    def clean(self):
        schedule = self.cleaned_data.get('schedule')
        if not croniter.croniter.is_valid(schedule):
            raise forms.ValidationError('Schedule is not a valid crontab string')


class ReindexRoutineAdmin(admin.ModelAdmin):
    INDEX_NAMES: List[str] = []
    TABLE_NAMES: List[str] = []

    list_display = ('target_entity', 'index_name', 'schedule')
    search_fields = ['target_entity', 'index_name', 'schedule']

    form = ReindexRoutineChangeForm
    change_form_template = 'admin/task/reindexroutine/change_form.html'

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or dict()
        extra_context['indexes'] = self.get_db_index_names()
        extra_context['tables'] = self.get_db_table_names()[:5]
        return super().add_view(request, form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or dict()
        extra_context['indexes'] = self.get_db_index_names()
        extra_context['tables'] = self.get_db_table_names()
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    @classmethod
    def get_db_index_names(cls) -> List[str]:
        if cls.INDEX_NAMES:
            return cls.INDEX_NAMES
        choices = []
        with connection.cursor() as cursor:
            cursor.execute('''
            select i.relname as index_name,
                   t.relname as table_name,
                   a.attname as column_name
            from
                   pg_class t, pg_class i, pg_index ix, pg_attribute a
            where
                   t.oid = ix.indrelid
                   and i.oid = ix.indexrelid
                   and a.attrelid = t.oid
                   and a.attnum = ANY(ix.indkey)
                   and t.relkind = 'r'
                   order by i.relname;
            ''')
            for index_name, _t, _c in cursor.fetchall():
                choices.append(index_name)
        cls.INDEX_NAMES = choices
        return choices

    @classmethod
    def get_db_table_names(cls) -> List[str]:
        if cls.TABLE_NAMES:
            return cls.TABLE_NAMES
        choices = []
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT table_name
                FROM   information_schema.tables
                WHERE  table_schema = 'public'
                ORDER  BY table_name;
                ''')
            for row in cursor.fetchall():
                choices.append(row[0])
        cls.TABLE_NAMES = choices
        return choices


admin.site.register(Task, TaskAdmin)
admin.site.register(TaskConfig, TaskConfigAdmin)
admin.site.register(ReindexRoutine, ReindexRoutineAdmin)

admin.site.unregister(TaskResult)
admin.site.register(TaskResult, CeleryResultAdmin)
