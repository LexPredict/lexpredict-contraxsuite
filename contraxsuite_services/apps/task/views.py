# -*- coding: utf-8 -*-

# Future imports
from __future__ import absolute_import, unicode_literals

# Django imports
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic.edit import FormView

# Project imports
from apps.analyze.models import TextUnitClassifier
from apps.common.mixins import (
    AdminRequiredMixin, CustomDetailView, DjangoJSONEncoder,
    JSONResponseView, JqPaginatedListView, TechAdminRequiredMixin)
from apps.task.forms import (
    LoadDocumentsForm, LoadTermsForm, LoadGeoEntitiesForm, LoadCourtsForm,
    LocateTermsForm, LocateGeoEntitiesForm, LocatePartiesForm,
    LocateDatesForm, LocateDateDurationsForm, LocateDefinitionsForm,
    LocateCourtsForm, LocateCurrenciesForm,
    ExistedClassifierClassifyForm, CreateClassifierClassifyForm,
    ClusterForm, SimilarityForm, PartySimilarityForm)
from apps.task.models import Task
from apps.task.tasks import call_task, clean_tasks, purge_task

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0/LICENSE.pdf"
__version__ = "1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@lexpredict.com"


class BaseTaskView(AdminRequiredMixin, FormView):
    template_name = 'task/task_form.html'
    task_name = 'Task'

    def form_valid(self, form):
        data = form.cleaned_data
        data['user_id'] = self.request.user.pk
        call_task(self.task_name, **data)
        return redirect(reverse('task:task-list'))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['task_name'] = self.task_name
        return ctx


class BaseAjaxTaskView(AdminRequiredMixin, JSONResponseView):
    task_name = 'Task'
    form_class = None

    @staticmethod
    def json_response(data, **kwargs):
        return JsonResponse(data, encoder=DjangoJSONEncoder, safe=False, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        data = dict(header=form.header, form_data=form.as_p())
        return self.json_response(data)

    def post(self, request, *args, **kwargs):
        if self.form_class is not None:
            form = self.form_class(request.POST)
            if not form.is_valid():
                return self.json_response(form.errors, status=404)
        # TODO: use from.cleaned_data
        data = request.POST.dict()
        data['user_id'] = request.user.pk
        call_task(self.task_name, **data)
        return self.json_response('The task is started. It can take a while.')


class LoadDocumentsView(BaseAjaxTaskView):
    task_name = 'Load Documents'
    form_class = LoadDocumentsForm


class LoadTermsView(BaseAjaxTaskView):
    task_name = 'Load Terms'
    form_class = LoadTermsForm


class LoadGeoEntitiesView(BaseAjaxTaskView):
    task_name = 'Load Geo Entities'
    form_class = LoadGeoEntitiesForm


class LoadCourtsView(BaseAjaxTaskView):
    task_name = 'Load Courts'
    form_class = LoadCourtsForm


class LocateTermsView(BaseAjaxTaskView):
    task_name = 'Locate Terms'
    form_class = LocateTermsForm


class LocateGeoEntitiesView(BaseAjaxTaskView):
    task_name = 'Locate Geo Entities'
    form_class = LocateGeoEntitiesForm


class LocatePartiesView(BaseAjaxTaskView):
    task_name = 'Locate Parties'
    form_class = LocatePartiesForm


class LocateDatesView(BaseAjaxTaskView):
    task_name = 'Locate Dates'
    form_class = LocateDatesForm


class LocateDateDurationsView(BaseAjaxTaskView):
    task_name = 'Locate Date Durations'
    form_class = LocateDateDurationsForm


class LocateDefinitionsView(BaseAjaxTaskView):
    task_name = 'Locate Definitions'
    form_class = LocateDefinitionsForm


class LocateCourtsView(BaseAjaxTaskView):
    task_name = 'Locate Courts'
    form_class = LocateCourtsForm


class LocateCurrenciesView(BaseAjaxTaskView):
    task_name = 'Locate Currencies'
    form_class = LocateCurrenciesForm


class ExistedClassifierClassifyView(BaseAjaxTaskView):
    task_name = 'Classify'
    form_class = ExistedClassifierClassifyForm


class CreateClassifierClassifyView(BaseAjaxTaskView):
    task_name = 'Classify'
    form_class = CreateClassifierClassifyForm


class UpdateElasticsearchIndexView(BaseAjaxTaskView):
    task_name = 'Update Elasticsearch Index'


class ClusterView(BaseAjaxTaskView):
    task_name = 'Cluster'
    form_class = ClusterForm


class SimilarityView(BaseAjaxTaskView):
    task_name = 'Similarity'
    form_class = SimilarityForm


class PartySimilarityView(BaseAjaxTaskView):
    task_name = 'PartySimilarity'
    form_class = PartySimilarityForm


class TaskDetailView(CustomDetailView):
    model = Task
    fields = ('name', 'log')

    def get_update_url(self):
        return None


class CleanTasksView(TechAdminRequiredMixin, JSONResponseView):

    def get_json_data(self, request, *args, **kwargs):
        return clean_tasks(delta_days=0)


class PurgeTaskView(TechAdminRequiredMixin, JSONResponseView):

    def get_json_data(self, request, *args, **kwargs):
        return purge_task(task_pk=request.POST.get('task_pk'))


class TaskListView(AdminRequiredMixin, JqPaginatedListView):
    model = Task
    ordering = '-date_start'
    json_fields = ['name', 'date_start', 'user__username']

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = reverse('task:task-detail', args=[item['pk']])
            task = Task.objects.get(pk=item['pk'])
            item['date_done'] = task.date_done
            item['progress'] = task.progress
            item['time'] = task.time
            item['status'] = task.status
            item['has_error'] = task.has_error
            item['purge_url'] = reverse('task:purge-task')
        return data

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_classifiers'] = TextUnitClassifier.objects.filter(is_active=True).exists()
        return ctx
