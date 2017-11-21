# -*- coding: utf-8 -*-

# Future imports
from __future__ import absolute_import, unicode_literals

# Django imports
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.views.generic.edit import FormView

# Project imports
from apps.analyze.models import TextUnitClassifier
from apps.common.mixins import (
    AdminRequiredMixin, CustomDetailView, DjangoJSONEncoder,
    JSONResponseView, JqPaginatedListView, TechAdminRequiredMixin)
from apps.task.forms import (
    LoadDocumentsForm, LocateTermsForm, LocateForm, LocateEmployeesForm,
    ExistedClassifierClassifyForm, CreateClassifierClassifyForm,
    ClusterForm, SimilarityForm, PartySimilarityForm,
    UpdateElasticSearchForm)
from apps.task.models import Task
from apps.task.tasks import call_task, clean_tasks, purge_task

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.3/LICENSE"
__version__ = "1.0.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


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
    html_form_class = 'popup-form'

    @staticmethod
    def json_response(data, **kwargs):
        return JsonResponse(data, encoder=DjangoJSONEncoder, safe=False, **kwargs)

    def get(self, request, *args, **kwargs):
        if Task.disallow_start(self.task_name):
            return HttpResponseForbidden(
                'Forbidden. Task "%s" is already started.' % self.task_name)
        else:
            form = self.form_class()
            data = dict(header=form.header,
                        form_class=self.html_form_class,
                        form_data=form.as_p())
        return self.json_response(data)

    def post(self, request, *args, **kwargs):
        if Task.disallow_start(self.task_name):
            return HttpResponseForbidden('Forbidden. Such task is already started.')
        if self.form_class is None:
            data = request.POST.dict()
        else:
            form = self.form_class(request.POST)
            if not form.is_valid():
                return self.json_response(form.errors, status=404)
            data = form.cleaned_data
        data['user_id'] = request.user.pk
        call_task(self.task_name, **data)
        return self.json_response('The task is started. It can take a while.')


class LoadTaskView(AdminRequiredMixin, JSONResponseView):

    # TODO: parse github repo?
    # f.e.: https://api.github.com/repos/LexPredict/lexpredict-legal-dictionary/contents/en
    paths_map = dict(
        terms_accounting_1='accounting/ifrs_iasb.csv',
        terms_accounting_2='accounting/uk_gaap.csv',
        terms_accounting_3='accounting/us_fasb.csv',
        terms_accounting_4='accounting/us_gaap.csv',
        terms_accounting_5='accounting/us_gasb.csv',
        terms_financial_1='financial/financial.csv',
        terms_legal_1='legal/common_law.csv',
        terms_legal_2='legal/us_cfr.csv',
        terms_legal_3='legal/us_usc.csv',
        terms_legal_4='legal/common_law_top1000.csv',
        terms_scientific_1='scientific/us_hazardous_waste.csv',
        courts_1='legal/ca_courts.csv',
        courts_2='legal/us_courts.csv',
        geoentities_1='geopolitical/geopolitical_divisions.csv',
    )
    tasks_map = dict(
        terms='LoadTerms',
        courts='LoadCourts',
        geoentities='LoadGeoEntities'
    )

    @staticmethod
    def json_response(data, **kwargs):
        return JsonResponse(data, encoder=DjangoJSONEncoder, safe=False, **kwargs)

    def post(self, request, *args, **kwargs):
        data = request.POST.dict()
        if not data:
            return self.json_response('error', status=404)
        data['user_id'] = request.user.pk

        rejected_tasks = []
        started_tasks = []
        for task_alias, task_name in self.tasks_map.items():
            if Task.disallow_start(task_name):
                rejected_tasks.append(task_name)
                continue
            repo_paths = ['{}/{}/{}'.format(settings.GIT_DATA_REPO_ROOT,
                                            j.replace('{}_locale_'.format(i), ''),
                                            self.paths_map[i])
                          for i in data if i.startswith(task_alias) and i in self.paths_map
                          for j in data if j.startswith('{}_locale_'.format(i))]
            file_path = data.get('{}_file_path'.format(task_alias)) or None
            delete = '{}_delete'.format(task_alias) in data
            if any([repo_paths, file_path, delete]):
                call_task(task_name, repo_paths=repo_paths, file_path=file_path, delete=delete)
                started_tasks.append(task_name)
        return self.json_response('The task is started. It can take a while.')


class LoadDocumentsView(BaseAjaxTaskView):
    task_name = 'Load Documents'
    form_class = LoadDocumentsForm


class LocateTaskView(BaseAjaxTaskView):
    form_class = LocateForm
    html_form_class = 'popup-form locate-form'
    custom_tasks = set(
        # 'LocateTerms',
    )

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if not form.is_valid():
            return self.json_response(form.errors, status=404)
        data = form.cleaned_data
        task_names = set([i.split('_')[0] for i in data if i != 'parse'])
        custom_task_names = task_names & self.custom_tasks
        lexnlp_task_names = task_names - self.custom_tasks

        # custom tasks
        rejected_tasks = []
        started_tasks = []
        for task_name in custom_task_names:
            kwargs = {k.replace('%s_' % task_name, ''): v for k, v in data.items()
                      if k.startswith(task_name)}
            if any(kwargs.values()):
                kwargs['user_id'] = request.user.pk
                if Task.disallow_start(task_name):
                    rejected_tasks.append(task_name)
                else:
                    started_tasks.append(task_name)
                    call_task(task_name, **kwargs)

        # lexnlp tasks
        lexnlp_task_data = dict()
        for task_name in lexnlp_task_names:
            kwargs = {k.replace('%s_' % task_name, ''): v for k, v in data.items()
                      if k.startswith(task_name)}
            if any(kwargs.values()):
                lexnlp_task_data[task_name] = kwargs
        if lexnlp_task_data:
            if Task.disallow_start('Locate'):
                rejected_tasks.append('Locate')
            else:
                started_tasks.append('Locate')
                call_task('Locate',
                          tasks=lexnlp_task_data,
                          parse=data['parse'],
                          user_id=request.user.pk)

        response_text = ''
        if started_tasks:
            response_text += 'The Task is started. It can take a while.<br />'
            response_text += 'Started tasks: [{}].<br />'.format(', '.join(started_tasks))
        if rejected_tasks:
            response_text += 'Some tasks were rejected (already started).<br />'
            response_text += 'Rejected Tasks: [{}]'.format(', '.join(rejected_tasks))
        return self.json_response(response_text)


# sample view for custom task
class LocateTermsView(BaseAjaxTaskView):
    task_name = 'Locate Terms'
    form_class = LocateTermsForm


class LocateEmployeesView(BaseAjaxTaskView):
    task_name = 'Locate Employees'
    form_class = LocateEmployeesForm


class ExistedClassifierClassifyView(BaseAjaxTaskView):
    task_name = 'Classify'
    form_class = ExistedClassifierClassifyForm


class CreateClassifierClassifyView(BaseAjaxTaskView):
    task_name = 'Classify'
    form_class = CreateClassifierClassifyForm
    html_form_class = 'popup-form classify-form'


class UpdateElasticsearchIndexView(BaseAjaxTaskView):
    task_name = 'Update Elasticsearch Index'
    form_class = UpdateElasticSearchForm


class ClusterView(BaseAjaxTaskView):
    task_name = 'Cluster'
    form_class = ClusterForm
    html_form_class = 'popup-form cluster-form'


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
