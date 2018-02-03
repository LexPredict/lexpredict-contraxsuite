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
from django.contrib import admin

# Project imports
from .models import Project, TaskQueue, TaskQueueHistory

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.5/LICENSE"
__version__ = "1.0.6"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TaskQueueAdmin(admin.ModelAdmin):
    list_display = ('description', 'documents_num', 'reviewers_num')
    search_fields = ('description',)
    filter_horizontal = ('documents', 'reviewers')

    @staticmethod
    def reviewers_num(obj):
        return obj.reviewers.count()

    @staticmethod
    def documents_num(obj):
        return obj.documents.count()


class TaskQueueHistoryAdmin(admin.ModelAdmin):
    list_display = ('task_queue', '_documents', 'date', 'user', 'action')
    search_fields = ('user', 'action')
    filter_horizontal = ('documents',)

    @staticmethod
    def _documents(obj):
        return list(obj.documents.values_list('pk', flat=True))


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'task_queues_num')
    search_fields = ('name', 'description')
    filter_horizontal = ('task_queues',)

    @staticmethod
    def task_queues_num(obj):
        return obj.task_queues.count()


admin.site.register(TaskQueue, TaskQueueAdmin)
admin.site.register(TaskQueueHistory, TaskQueueHistoryAdmin)
admin.site.register(Project, ProjectAdmin)
