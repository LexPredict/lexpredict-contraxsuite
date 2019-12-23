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

from typing import List

# Django imports
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.utils import NestedObjects
from django.db import router
from django.db.models import Count, F
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

# Project imports
from apps.common.utils import cap_words
from apps.document.models import Document
from apps.project.models import Project, TaskQueue, TaskQueueHistory,\
    ProjectClustering, UploadSession, ProjectTermConfiguration
from apps.common.model_utils.model_class_dictionary import ModelClassDictionary

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
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


def get_deleted_objects(objs, request, admin_site):
    """
    Patched django/contrib/admin/utils.py
    to skip collecting links for related nested objects
    """
    try:
        obj = objs[0]
    except IndexError:
        return [], {}, set(), []
    else:
        using = router.db_for_write(obj._meta.model)
    collector = NestedObjects(using=using)
    collector.collect(objs)
    model_count = {model._meta.verbose_name_plural: len(objs) for model, objs in collector.model_objs.items()}
    to_delete = ['{}: {}'.format(cap_words(k), v) for k, v in model_count.items()]
    return to_delete, model_count, None, None


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'status_name', 'description', 'documents_num', 'documents_to_delete')
    search_fields = ('name', 'description')
    filter_horizontal = ('task_queues',)

    def get_queryset(self, request):
        return Project.all_objects

    @staticmethod
    def status_name(obj):
        return obj.status.name

    @staticmethod
    def documents_num(obj):
        return obj.document_set.count()

    @staticmethod
    def documents_to_delete(obj):
        return obj.all_document_set.count() - obj.document_set.count()

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False

    def get_deleted_objects(self, objs, request):
        """
        Hook for customizing the delete process for the delete view and the
        "delete selected" action.
        Patched version.
        """
        return get_deleted_objects(objs, request, self.admin_site)


class ProjectClusteringAdmin(admin.ModelAdmin):
    list_display = ('pk', 'project_id', 'project_name', 'task_id', 'status', 'created_date')
    search_fields = ('pk', 'project__name')

    @staticmethod
    def project_name(obj):
        return obj.project.name


class UploadSessionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'project_id', 'project_name', 'completed', 'created_date')
    search_fields = ('pk', 'project__name')

    @staticmethod
    def project_name(obj):
        return obj.project.name


class SoftDeleteProject(Project):
    class Meta:
        proxy = True


class DeletePendingFilter(SimpleListFilter):
    title = _('Status')

    parameter_name = 'delete_pending'

    def lookups(self, request, model_admin):
        return (
            ('deleting', _('Deleting')),
            ('all', _('All')),
        )

    def queryset(self, request, queryset):
        queryset = Project.all_objects
        val = self.value().lower() if self.value() else ''
        if val == 'all':
            return queryset
        return queryset.filter(delete_pending=True)


def set_soft_delete(project_ids: List[int], delete_pending: bool):
    from apps.project.sync_tasks.soft_delete_project_task import SoftDeleteProjectSyncTask
    for project_id in project_ids:
        SoftDeleteProjectSyncTask().process(project_id=project_id,
                                            delete_pending=delete_pending,
                                            remove_all=True)


def mark_deleting(_, request, queryset):
    project_ids = queryset.values_list('pk', flat=True)
    set_soft_delete(project_ids, True)


mark_deleting.short_description = "Mark selected projects for deleting"


def unmark_deleting(_, request, queryset):
    project_ids = queryset.values_list('pk', flat=True)
    set_soft_delete(project_ids, False)


unmark_deleting.short_description = "Uncheck selected projects for deleting"


def delete_checked_projects(_, request, queryset):
    ids = [d.pk for d in queryset]
    request.session['_project_ids'] = ids
    from django.http import HttpResponseRedirect
    return HttpResponseRedirect("./confirm_delete_view/")


delete_checked_projects.short_description = "Delete checked projects"


class SoftDeleteProjectAdmin(ProjectAdmin):
    list_filter = [DeletePendingFilter]
    list_display = ('get_name', 'type', 'status', 'delete_pending')
    search_fields = ['type__code', 'name']
    actions = [mark_deleting, unmark_deleting, delete_checked_projects]
    change_list_template = 'admin/project/softdeleteproject/change_list.html'

    def get_name(self, obj):
        display_text = "<a href={}>{}</a>".format(
            reverse('admin:{}_{}_change'.format(obj._meta.app_label,
                                                obj._meta.model_name),
                    args=(obj.pk,)),
            obj.name)
        return mark_safe(display_text)

    get_name.short_description = 'Project'
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
        self.message_user(request, "Started deleting for all checked projects")
        ids = [d.pk for d in Project.all_objects.filter(delete_pending=True)]
        request.session['_project_ids'] = ids
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect("../confirm_delete_view/")

    def confirm_delete_view(self, request):
        project_ids = request.session.get('_project_ids')

        if request.method == 'GET':
            doc_ids = Document.all_objects.filter(
                project_id__in=project_ids).values_list('id', flat=True)

            from apps.document.repository.document_bulk_delete \
                import get_document_bulk_delete
            items_by_table = get_document_bulk_delete().calculate_deleting_count(doc_ids)
            mdc = ModelClassDictionary()
            del_count_hash = {mdc.get_model_class_name_hr(t): items_by_table[t]
                              for t in items_by_table if t in mdc.model_by_table}
            del_count = [(d, del_count_hash[d], False) for d in del_count_hash]
            del_count = sorted(del_count, key=lambda x: x[0])
            del_count.insert(0, ('Documents', len(doc_ids), True))
            del_count.insert(0, ('Projects', len(project_ids), True))

            context = {
                'deleting_count': del_count,
                'return_url': 'admin:project_softdeleteproject_changelist'
            }
            from django.shortcuts import render
            return render(request, "admin/common/confirm_delete_view.html", context)

        # POST: actual delete
        from apps.task.tasks import call_task
        call_task(
            task_name='CleanProjects',
            module_name='apps.project.tasks',
            _project_ids=project_ids,
            user_id=request.user.id,
            delete=True)
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


class ProjectTermConfigurationAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'project_id', 'terms_count')
    search_fields = ('pk', 'project__name')
    filter_horizontal = ('terms',)

    @staticmethod
    def project_name(obj):
        return obj.project_name

    @staticmethod
    def terms_count(obj):
        return obj.terms_count

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(project_name=F('project__name'), terms_count=Count('terms'))


admin.site.register(TaskQueue, TaskQueueAdmin)
admin.site.register(TaskQueueHistory, TaskQueueHistoryAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectClustering, ProjectClusteringAdmin)
admin.site.register(UploadSession, UploadSessionAdmin)
admin.site.register(SoftDeleteProject, SoftDeleteProjectAdmin)
admin.site.register(ProjectTermConfiguration, ProjectTermConfigurationAdmin)
