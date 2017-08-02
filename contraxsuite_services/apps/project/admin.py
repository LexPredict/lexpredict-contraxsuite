# -*- coding: utf-8 -*-

# Django imports
from django.contrib import admin

# Project imports
from .models import Project, TaskQueue, TaskQueueHistory

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0/LICENSE.pdf"
__version__ = "1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@lexpredict.com"


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
