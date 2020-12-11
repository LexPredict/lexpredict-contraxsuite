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
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count, Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from guardian.shortcuts import get_objects_for_user

# Project imports
from apps.analyze.models import DocumentCluster
from apps.common.mixins import CustomCreateView, JqPaginatedListView, CustomUpdateView, \
    JSONResponseView
from apps.common.model_utils.improved_django_json_encoder import ImprovedDjangoJSONEncoder
from apps.common.utils import cap_words
from apps.project.models import Project, TaskQueue, UserProjectsSavedFilter
from apps.project.forms import (
    TaskQueueChoiceForm, TaskQueueForm, ProjectChoiceForm, ProjectForm)

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class ProjectListView(JqPaginatedListView):
    model = Project
    json_fields = ['name', 'description', 'type__title', 'status__name', 'total_documents_count', 'reviewed_documents_count']

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = self.full_reverse('project:project-update', args=[item['pk']])
            item['progress'] = round(item['reviewed_documents_count'] / item['total_documents_count'] * 100, 1) \
                if item['total_documents_count'] else 0
            item['completed'] = item['progress'] == 100
        return data

    def get_queryset(self):
        # permission check
        qs = SelectProjectsView.get_user_projects(self.request.user)
        qs = qs.filter(delete_pending=False).annotate(
            total_documents_count=Count('document', filter=Q(document__delete_pending=False)),
            reviewed_documents_count=Count('document', filter=Q(document__delete_pending=False, status__group__is_active=False))
        )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['can_add_project'] = self.request.user.has_perm('project.add_project')
        return ctx


class ProjectCreateView(CustomCreateView):
    model = Project
    fields = ('name', 'description', 'task_queues')

    def has_permission(self):
        return self.request.user.has_perm('project.add_project')

    def get_success_url(self):
        return reverse('project:project-list')


class ProjectUpdateView(ProjectCreateView, CustomUpdateView):
    def has_permission(self):
        return self.request.user.has_perm('project.change_project', self.get_object())


class TaskQueueListView(PermissionRequiredMixin, JqPaginatedListView):
    model = TaskQueue
    json_fields = ['description', 'project__pk']
    annotate = {'reviewers_count': Count('reviewers', distinct=True)}
    template_name = 'project/task_queue_list.html'

    def has_permission(self):
        return self.request.user.has_perm('project.view_taskqueue')

    def get_json_data(self, **kwargs):
        only_completed = self.request.GET.get('only_completed')
        only_assigned = self.request.GET.get('only_assigned')
        document_pk = self.request.GET.get('document_pk')
        if any([only_completed, only_assigned, document_pk]):
            self.json_fields = ['description']
        results = []
        for item in super().get_json_data()['data']:
            queue = TaskQueue.objects.get(pk=item['pk'])
            completed = queue.completed
            if (only_completed and not completed) or \
                    (only_assigned and completed):
                continue
            item['url'] = self.full_reverse('project:task-queue-update', args=[item['pk']])
            progress = queue.progress(as_dict=True)
            item.update(progress)
            item['progress'] = round(item['progress'], 1)
            item['completed'] = item['progress'] == 100
            item['reviewers_usernames'] = '\n'.join(
                list(queue.reviewers.values_list('username', flat=True)))
            if document_pk:
                complete_history = queue.document_complete_history(document_pk)
                if complete_history:
                    item['complete_date'] = complete_history.date
                    item['complete_user'] = complete_history.user.username
                item['open_url'] = self.full_reverse('project:mark-document-completed',
                                           args=[queue.pk, document_pk])
                item['remove_url'] = self.full_reverse('project:add-to-task-queue',
                                             args=[queue.pk, document_pk])
            elif kwargs.get('with_documents', True):
                documents = []
                for num, document in enumerate(queue.complete_history):
                    document_data = dict(
                        pk=queue.pk,
                        num=num + 1,
                        name=document.name,
                        description=document.description,
                        type=document.document_type.title if document.document_type else None,
                        complete_date=None,
                        complete_user=None,
                        url=reverse('document:document-detail', args=[document.pk]),
                        open_url=reverse('project:mark-document-completed',
                                         args=[queue.pk, document.pk]),
                        remove_url=reverse('project:add-to-task-queue',
                                           args=[queue.pk, document.pk])
                    )
                    if document.complete_history:
                        document_data.update(dict(
                            complete_date=document.complete_history.date,
                            complete_user=document.complete_history.user.username))
                    documents.append(document_data)
                item['documents'] = documents
            results.append(item)
        return {'data': results, 'total_records': len(results)}

    def get_queryset(self):
        qs = super().get_queryset()

        if "document_pk" in self.request.GET:
            qs = qs.filter(documents__pk=self.request.GET['document_pk'])

        return qs


class TaskQueueCreateView(CustomCreateView):
    model = TaskQueue
    fields = ('description', 'documents', 'reviewers')

    def has_permission(self):
        return self.request.user.has_perm('project.add_taskqueue')

    def get_success_url(self):
        if 'project_id' in self.request.GET:
            project = Project.objects.get(pk=self.request.GET['project_id'])
            project.task_queues.add(self.object)
            return reverse('project:project-list') + '#' + self.request.GET.get('row_id', 0)
        return reverse('project:task-queue-list')


class TaskQueueUpdateView(TaskQueueCreateView, CustomUpdateView):
    def has_permission(self):
        return self.request.user.has_perm('project.change_taskqueue', self.get_object())


def add_to_task_queue(request, task_queue_pk, document_pk):
    """
    Add document to OR remove from Task Queue
    """
    task_queue = TaskQueue.objects.get(pk=task_queue_pk)
    if task_queue.documents.filter(pk=document_pk).exists():
        if not request.user.has_perm('project.change_taskqueue', task_queue):
            return HttpResponseForbidden()
        task_queue.documents.remove(document_pk)
        message = 'removed from'
    else:
        task_queue.documents.add(document_pk)
        message = 'added to'
    full_message = 'Document successfully %s %s' % (message, str(task_queue))
    if request.is_ajax():
        data = {'message': full_message, 'status': 'success'}
        return JsonResponse(data, encoder=ImprovedDjangoJSONEncoder, safe=False)
    messages.success(request, full_message)
    return redirect(reverse('document:document-detail', args=[document_pk]))


def mark_document_completed(request, task_queue_pk, document_pk):
    """
    Mark document completed OR reopen
    """
    task_queue = TaskQueue.objects.get(pk=task_queue_pk)
    if not request.user.can_view_document(document_pk):
        data = {'message': 'Forbidden', 'status': 'error'}
        return JsonResponse(data, encoder=ImprovedDjangoJSONEncoder, safe=False)
    if task_queue.completed_documents.filter(pk=document_pk).exists():
        task_queue.completed_documents.remove(document_pk)
        message = 'reopened'
    else:
        task_queue.completed_documents.add(document_pk)
        message = 'marked as completed'
    full_message = 'Successfully %s in %s' % (message, str(task_queue))
    if request.is_ajax():
        data = {'message': full_message, 'status': 'success'}
        return JsonResponse(data, encoder=ImprovedDjangoJSONEncoder, safe=False)
    messages.success(request, full_message)
    return redirect(reverse('document:document-detail', args=[document_pk]))


class TaskQueueAddClusterDocuments(PermissionRequiredMixin, JSONResponseView):

    def has_permission(self):
        return self.request.user.has_perm('project.change_taskqueue')

    def get(self, request, *args, **kwargs):
        return JsonResponse({'task_queue_choice_form': TaskQueueChoiceForm().as_p(),
                             'task_queue_create_form': TaskQueueForm().as_p(),
                             'project_choice_form': ProjectChoiceForm().as_p(),
                             'project_create_form': ProjectForm().as_p()},
                            encoder=ImprovedDjangoJSONEncoder, safe=False)

    def post(self, request, *args, **kwargs):
        message = 'Success'
        status = 'success'

        if 'new_task_queue' not in request.POST:
            tq_form = TaskQueueChoiceForm(request.POST)
            if not tq_form.is_valid():
                status = 'error'
                message = 'Please choose Task Queue'
        else:
            tq_form = TaskQueueForm(request.POST)
            project_form_class = ProjectForm if 'new_project' in request.POST else ProjectChoiceForm
            project_form = project_form_class(request.POST)
            if not tq_form.is_valid():
                status = 'error'
                message = 'Task Queue: %s' % '; '.join(
                    '{} - {}'.format(cap_words(field), ' ,'.join(errors))
                    for field, errors in tq_form.errors.items())
            elif 'new_project' in request.POST and not project_form.is_valid():
                status = 'error'
                message = 'Project: %s' % '; '.join(
                    '{} - {}'.format(cap_words(field), ' ,'.join(errors))
                    for field, errors in project_form.errors.items())

        if status == 'success':
            document_pks = DocumentCluster.objects.get(pk=request.GET['cluster_pk']) \
                .documents.values_list('pk', flat=True)
            if 'new_task_queue' in request.POST:
                task_queue = TaskQueue.objects.create(description=request.POST['description'])
                if 'reviewers' in request.POST:
                    task_queue.reviewers.set(request.POST.getlist('reviewers'))
            else:
                task_queue = TaskQueue.objects.get(pk=request.POST['task_queue'])
            task_queue.documents.add(*document_pks)
            project = None
            if 'new_project' in request.POST:
                project = Project.objects.create(
                    name=request.POST['name'],
                    description=request.POST['project_description'])
            elif 'project' in request.POST:
                project = Project.objects.get(pk=request.POST['project'])
            if project:
                project.task_queues.add(task_queue)
        return JsonResponse({'message': message, 'status': status},
                            encoder=ImprovedDjangoJSONEncoder, safe=False)


class SelectProjectsView(LoginRequiredMixin, JSONResponseView):
    """
    Select Project(s) to filter Document/TextUnit/ThingUsage views
    """
    @staticmethod
    def get_user_projects(user):
        return get_objects_for_user(user, 'project.view_project', Project)

    def post(self, request, *args, **kwargs):
        project_ids = request.POST.getlist('project_ids[]')

        user_projects = self.get_user_projects(request.user)

        project_ids = list(user_projects.filter(id__in=project_ids).values_list('pk', flat=True))

        obj, _ = UserProjectsSavedFilter.objects.get_or_create(user=request.user)
        obj.projects.set(project_ids)

        ret = dict(
            saved_filter_id=obj.id,
            user_id=request.user.id,
            project_ids=list(obj.projects.values_list('id', flat=True)),
            show_warning=not obj.projects.exists()
        )
        return JsonResponse(ret)
