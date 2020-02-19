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
from django_celery_results.models import TaskResult
from simple_history.admin import SimpleHistoryAdmin

# Django imports
from django.contrib import admin

# Project imports
from apps.task.models import Task, TaskConfig

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
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


admin.site.register(Task, TaskAdmin)
admin.site.register(TaskConfig, TaskConfigAdmin)

admin.site.unregister(TaskResult)
admin.site.register(TaskResult, CeleryResultAdmin)
