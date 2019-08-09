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

# Future imports
from __future__ import absolute_import, unicode_literals
import traceback

# Django imports
from django.conf import settings
from django.urls import reverse
from django.db.models import F
from django.db.models.functions import Now, Coalesce
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.views.generic.edit import FormView

# Project imports
from apps.analyze.models import TextUnitClassifier
import apps.common.mixins
from apps.common.utils import get_api_module
from apps.deployment.app_data import DICTIONARY_DATA_URL_MAP
from apps.document.models import DocumentProperty, TextUnitProperty
from apps.task.forms import (
    LoadDocumentsForm, LocateTermsForm, LocateForm,
    ExistedClassifierClassifyForm, CreateClassifierClassifyForm,
    ClusterForm, CleanProjectForm,
    UpdateElasticSearchForm, TaskDetailForm, TotalCleanupForm,
    LoadFixtureForm, DumpFixtureForm)
from apps.task.models import Task
from apps.task.tasks import call_task, clean_tasks, purge_task
from apps.dump.app_dump import get_model_fixture_dump, load_fixture_from_dump, download
from apps.imanage_integration.tasks import IManageSynchronization

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


project_api_module = get_api_module('project')


class BaseTaskView(apps.common.mixins.AdminRequiredMixin, FormView):
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


class BaseAjaxTaskView(apps.common.mixins.AdminRequiredMixin, apps.common.mixins.JSONResponseView):
    task_class = None
    task_name = 'Task'
    form_class = None
    html_form_class = 'popup-form'

    @staticmethod
    def json_response(data, **kwargs):
        return JsonResponse(data, encoder=apps.common.mixins.DjangoJSONEncoder, safe=False, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.disallow_start():
            return HttpResponseForbidden(
                'Forbidden. Task "%s" is already started.' % self.task_name)
        else:
            form = self.form_class()
            data = dict(header=form.header,
                        form_class=self.html_form_class,
                        form_data=form.as_p())
        return self.json_response(data)

    def get_metadata(self):
        return getattr(self, 'metadata', None)

    def start_task(self, data):
        call_task(self.task_class or self.task_name, **data)

    def disallow_start(self):
        return Task.disallow_start(self.task_name)

    def post(self, request, *args, **kwargs):
        if self.disallow_start():
            return HttpResponseForbidden('Forbidden. Such task is already started.')
        if self.form_class is None:
            data = request.POST.dict()
        else:
            form = self.form_class(data=request.POST, files=request.FILES)
            if not form.is_valid():
                return self.json_response(form.errors, status=400)
            data = form.cleaned_data
        data['user_id'] = request.user.pk
        data['metadata'] = self.get_metadata()
        data['module_name'] = getattr(self, 'module_name', None) or self.__module__.replace('views', 'tasks')
        self.start_task(data)
        return self.json_response('The task is started. It can take a while.')


class LoadTaskView(apps.common.mixins.AdminRequiredMixin, apps.common.mixins.JSONResponseView):
    tasks_map = dict(
        terms=dict(task_name='Load Terms'),
        courts=dict(task_name='Load Courts'),
        geoentities=dict(
            task_name='Load Geo Entities',
            result_links=[{'name': 'View Extracted Geo Entities',
                           'link': 'extract:geo-entity-usage-list'}])
    )

    @staticmethod
    def json_response(data, **kwargs):
        return JsonResponse(data, encoder=apps.common.mixins.DjangoJSONEncoder, safe=False, **kwargs)

    def post(self, request, *args, **kwargs):
        data = request.POST.dict()
        if not data:
            return self.json_response('error', status=404)
        data['user_id'] = request.user.pk

        rejected_tasks = []
        started_tasks = []
        for task_alias, metadata in self.tasks_map.items():
            task_name = metadata['task_name']
            if Task.disallow_start(task_name):
                rejected_tasks.append(task_name)
                continue
            repo_paths = ['{}/{}/{}'.format(settings.GIT_DATA_REPO_ROOT,
                                            j.replace('{}_locale_'.format(i), ''),
                                            DICTIONARY_DATA_URL_MAP[i])
                          for i in data if i.startswith(task_alias) and i in DICTIONARY_DATA_URL_MAP
                          for j in data if j.startswith('{}_locale_'.format(i))]
            file_path = data.get('{}_file_path'.format(task_alias)) or None
            delete = '{}_delete'.format(task_alias) in data
            if any([repo_paths, file_path, delete]):
                call_task(task_name,
                          repo_paths=repo_paths,
                          file_path=file_path,
                          delete=delete,
                          metadata=metadata)
                started_tasks.append(task_name)
        return self.json_response('The task is started. It can take a while.')


class LoadDocumentsView(BaseAjaxTaskView):
    task_name = 'Load Documents'
    form_class = LoadDocumentsForm
    metadata = dict(
        result_links=[{'name': 'View Document List', 'link': 'document:document-list'},
                      {'name': 'View Text Unit List', 'link': 'document:text-unit-list'}])


class LocateTaskView(BaseAjaxTaskView):
    form_class = LocateForm
    html_form_class = 'popup-form locate-form'
    custom_tasks = set(
        # 'LocateTerms',
    )
    metadata = dict(
        result_links=[{'name': 'View Document List', 'link': 'document:document-list'},
                      {'name': 'View Text Unit List', 'link': 'document:text-unit-list'}])
    locator_result_links_map = dict(
        geoentity={'name': 'View Geo Entity Usage List', 'link': 'extract:geo-entity-usage-list'},
        date={'name': 'View Date Usage List', 'link': 'extract:date-usage-list'},
        amount={'name': 'View Amount Usage List', 'link': 'extract:amount-usage-list'},
        citation={'name': 'View Citation Usage List', 'link': 'extract:citation-usage-list'},
        copyright={'name': 'View Copyright Usage List', 'link': 'extract:copyright-usage-list'},
        court={'name': 'View Court Usage List', 'link': 'extract:court-usage-list'},
        currency={'name': 'View Currency Usage List', 'link': 'extract:currency-usage-list'},
        duration={'name': 'View Duration Usage List', 'link': 'extract:date-duration-usage-list'},
        definition={'name': 'View Definition Usage List', 'link': 'extract:definition-usage-list'},
        distance={'name': 'View Distance Usage List', 'link': 'extract:distance-usage-list'},
        party={'name': 'View Party Usage List', 'link': 'extract:party-usage-list'},
        percent={'name': 'View Percent Usage List', 'link': 'extract:percent-usage-list'},
        ratio={'name': 'View Ratio Usage List', 'link': 'extract:ratio-usage-list'},
        regulation={'name': 'View Regulation Usage List', 'link': 'extract:regulation-usage-list'},
        term={'name': 'View Term Usage List', 'link': 'extract:term-usage-list'},
        trademark={'name': 'View Trademark Usage List', 'link': 'extract:trademark-usage-list'},
        url={'name': 'View Url Usage List', 'link': 'extract:url-usage-list'},
    )

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if not form.is_valid():
            return self.json_response(form.errors, status=404)
        data = form.cleaned_data

        project_id = None
        project_ref = data.get('project')
        if project_ref:
            del data['project']
            project_id = project_ref.pk

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
                    locator_result_link = self.locator_result_links_map.get(task_name)
                    if locator_result_link:
                        kwargs['metadata'] = {'result_links': [locator_result_link]}
                    call_task(task_name, **kwargs)

        # lexnlp tasks
        lexnlp_task_data = dict()
        for task_name in lexnlp_task_names:
            kwargs = {k.replace('%s_' % task_name, ''): v for k, v in data.items()
                      if k.startswith(task_name)}
            if any(kwargs.values()):
                lexnlp_task_data[task_name] = kwargs

        if lexnlp_task_data:
            # if Task.disallow_start('Locate'):
            #     rejected_tasks.append('Locate')
            # else:
            #     started_tasks.append('Locate')
            #     call_task('Locate',
            #               tasks=lexnlp_task_data,
            #               parse=data['parse'],
            #               user_id=request.user.pk,
            #               metadata={
            #                   'description': [i for i, j in lexnlp_task_data.items()
            #                                   if j.get('locate')],
            #                   'result_links': [self.locator_result_links_map[i]
            #                                    for i, j in lexnlp_task_data.items()
            #                                    if j.get('locate')]})

            # allow to start "Locate" task anytime
            started_tasks.append('Locate({})'.format(', '.join(lexnlp_task_data.keys())))
            call_task('Locate',
                      tasks=lexnlp_task_data,
                      parse=data['parse'],
                      user_id=request.user.pk,
                      project_id=project_id,
                      metadata={
                          'description': [i for i, j in lexnlp_task_data.items()
                                          if j.get('locate')],
                          'result_links': [self.locator_result_links_map[i]
                                           for i, j in lexnlp_task_data.items()
                                           if j.get('locate')]})
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


class ExistedClassifierClassifyView(BaseAjaxTaskView):
    task_name = 'Classify'
    form_class = ExistedClassifierClassifyForm

    def get_metadata(self):
        return dict(
            description='classifier:%s' % self.request.POST.get('classifier'),
            result_links=[{'name': 'View Text Unit Classification Suggestion List',
                           'link': 'analyze:text-unit-classifier-suggestion-list'}])


class CreateClassifierClassifyView(BaseAjaxTaskView):
    task_name = 'Classify'
    form_class = CreateClassifierClassifyForm
    html_form_class = 'popup-form classify-form'

    def get_metadata(self):
        return dict(
            description='classify_by:{}, algorithm:{}, class_name:{}'.format(
                self.request.POST.get('classify_by'),
                self.request.POST.get('algorithm'),
                self.request.POST.get('class_name')),
            result_links=[{'name': 'View Text Unit Classification List',
                           'link': 'analyze:text-unit-classifier-suggestion-list'},
                          {'name': 'View Text Unit Classifier List',
                           'link': 'analyze:text-unit-classifier-list'}])


class UpdateElasticsearchIndexView(BaseAjaxTaskView):
    task_name = 'Update Elasticsearch Index'
    form_class = UpdateElasticSearchForm


class ClusterView(BaseAjaxTaskView):
    task_name = 'Cluster'
    form_class = ClusterForm
    html_form_class = 'popup-form cluster-form'

    def get_metadata(self):
        cluster_items = []
        result_links = []
        do_cluster_documents = self.request.POST.get('do_cluster_documents')
        if do_cluster_documents:
            cluster_items.append('documents')
            result_links.append({'name': 'View Document Cluster List',
                                 'link': 'analyze:document-cluster-list'})
        do_cluster_text_units = self.request.POST.get('do_cluster_text_units')
        if do_cluster_text_units:
            cluster_items.append('text units')
            result_links.append({'name': 'View Text Unit Cluster List',
                                 'link': 'analyze:text-unit-cluster-list'})
        return dict(
            description='cluster:{}; by:{}; algorithm:{}; name:{}'.format(
                ', '.join(cluster_items),
                self.request.POST.get('cluster_by'),
                self.request.POST.get('using'),
                self.request.POST.get('name')),
            result_links=result_links)


class TaskDetailView(apps.common.mixins.CustomDetailView):
    model = Task

    def get_form_class(self):
        return TaskDetailForm

    def get_update_url(self):
        return None


class CleanTasksView(apps.common.mixins.TechAdminRequiredMixin, apps.common.mixins.JSONResponseView):
    def get_json_data(self, request, *args, **kwargs):
        return clean_tasks(delta_days=0)


class PurgeTaskView(apps.common.mixins.TechAdminRequiredMixin, apps.common.mixins.JSONResponseView):
    def get_json_data(self, request, *args, **kwargs):
        return purge_task(task_pk=request.POST.get('task_pk'))


class TaskListView(apps.common.mixins.AdminRequiredMixin, apps.common.mixins.JqPaginatedListView):
    model = Task
    ordering = '-date_start'
    json_fields = ['name', 'date_start', 'username', 'metadata',
                   'date_done', 'status', 'progress', 'time', 'date_work_start', 'work_time', 'worker', 'description']

    db_time = Coalesce(F('date_done') - F('date_start'), Now() - F('date_start'))
    db_work_time = Coalesce(F('date_done') - F('date_work_start'), Now() - F('date_work_start'),
                            F('date_start') - F('date_start'))
    db_user = Coalesce(F('user__username'), F('main_task__user__username'))
    template_name = 'task/task_list.html'

    def get_queryset(self):
        qs = Task.objects.main_tasks().order_by('-date_start')
        qs = qs.annotate(time=self.db_time, work_time=self.db_work_time, username=self.db_user)
        return qs

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = reverse('task:task-detail', args=[item['pk']])
            item['purge_url'] = reverse('task:purge-task')
            item['result_links'] = []
            if item['metadata']:
                if isinstance(item['metadata'], dict):
                    metadata = item['metadata']
                    item['description'] = metadata.get('description')
                    result_links = metadata.get('result_links', [])
                    for link_data in result_links:
                        link_data['link'] = reverse(link_data['link'])
                    item['result_links'] = result_links

        return data

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_classifiers'] = TextUnitClassifier.objects.filter(is_active=True).exists()
        if DocumentProperty.objects.exists():
            ctx['ls_document_properties'] = DocumentProperty.objects.order_by('key') \
                .values_list('key', flat=True).distinct()
        if TextUnitProperty.objects.exists():
            ctx['ls_text_unit_properties'] = TextUnitProperty.objects.order_by('key') \
                .values_list('key', flat=True).distinct()
        return ctx


class TotalCleanupView(BaseAjaxTaskView):
    task_name = 'Total Cleanup'
    form_class = TotalCleanupForm


class CleanProjectView(BaseAjaxTaskView):
    task_name = 'Clean Project'
    module_name = 'apps.project.tasks'
    form_class = CleanProjectForm


class LoadFixturesView(BaseAjaxTaskView):
    form_class = LoadFixtureForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        data = dict(header=form.header,
                    form_class=self.html_form_class,
                    form_data=form.as_p())
        return self.json_response(data)

    def post(self, request, *args, **kwargs):
        file_ = request.FILES.dict().get('fixture_file')
        if not file_:
            return JsonResponse({'fixture_file': ['This field is required']}, status=400)
        data = file_.read()
        mode = request.POST.get('mode', 'default')
        res = load_fixture_from_dump(data, mode)
        status = 200 if res['status'] == 'success' else 400
        return JsonResponse(res, status=status)


class DumpFixturesView(LoadFixturesView):
    form_class = DumpFixtureForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if not form.is_valid():
            return self.json_response(form.errors, status=400)
        form_data = form.cleaned_data
        file_name = form_data.pop('file_name')
        try:
            json_data = get_model_fixture_dump(**form_data)
        except Exception as e:
            tb = traceback.format_exc()
            error = 'Wrong app name/model name or filter options, see details:' \
                    '<br/>{}<br/>{}'.format(str(e), tb)
            return self.json_response({'app_name': [error]}, status=400)
        return download(json_data, file_name)
