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

# Standard imports
import json

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
    LoadDocumentsForm, LocateTermsForm, LocateForm,
    ExistedClassifierClassifyForm, CreateClassifierClassifyForm,
    ClusterForm, SimilarityForm, PartySimilarityForm,
    UpdateElasticSearchForm)
from apps.task.models import Task
from apps.task.tasks import call_task, clean_tasks, purge_task

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.5/LICENSE"
__version__ = "1.0.6"
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

    def get_metadata(self):
        return getattr(self, 'metadata', None)

    def post(self, request, *args, **kwargs):
        if Task.disallow_start(self.task_name):
            return HttpResponseForbidden('Forbidden. Such task is already started.')
        if self.form_class is None:
            data = request.POST.dict()
        else:
            form = self.form_class(request.POST)
            if not form.is_valid():
                return self.json_response(form.errors, status=400)
            data = form.cleaned_data
        data['user_id'] = request.user.pk
        data['metadata'] = self.get_metadata()
        data['module_name'] = self.__module__.replace('views', 'tasks')
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
        terms_legal_4='legal/common_US_terms_top1000.csv',
        terms_scientific_1='scientific/us_hazardous_waste.csv',
        courts_1='legal/ca_courts.csv',
        courts_2='legal/us_courts.csv',
        geoentities_1='geopolitical/geopolitical_divisions.csv',
    )
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
        return JsonResponse(data, encoder=DjangoJSONEncoder, safe=False, **kwargs)

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
                                            self.paths_map[i])
                          for i in data if i.startswith(task_alias) and i in self.paths_map
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
            if Task.disallow_start('Locate'):
                rejected_tasks.append('Locate')
            else:
                started_tasks.append('Locate')
                call_task('Locate',
                          tasks=lexnlp_task_data,
                          parse=data['parse'],
                          user_id=request.user.pk,
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


class SimilarityView(BaseAjaxTaskView):
    task_name = 'Similarity'
    form_class = SimilarityForm

    def get_metadata(self):
        similarity_items = []
        result_links = []
        if self.request.POST.get('search_similar_documents'):
            similarity_items.append('documents')
            result_links.append({'name': 'View Document Similarity List',
                                 'link': 'analyze:document-similarity-list'})
        if self.request.POST.get('search_similar_text_units'):
            similarity_items.append('text units')
            result_links.append({'name': 'View Text Unit Similarity List',
                                 'link': 'analyze:text-unit-similarity-list'})
        return dict(
            description='similarity for:{}; threshold:{}'.format(
                ', '.join(similarity_items),
                self.request.POST.get('similarity_threshold')),
            result_links=result_links)


class PartySimilarityView(BaseAjaxTaskView):
    task_name = 'Party Similarity'
    form_class = PartySimilarityForm

    def get_metadata(self):
        return dict(
            description='similarity type:{}, threshold:{}'.format(
                self.request.POST.get('similarity_type'),
                self.request.POST.get('similarity_threshold')),
            result_links=[{'name': 'View Party Usage List',
                           'link': 'extract:party-usage-list'}])


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
    json_fields = ['name', 'date_start', 'user__username', 'metadata']

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
            if item['metadata']:
                metadata = json.loads(item['metadata'])
                item['description'] = metadata.get('description')
                result_links = metadata.get('result_links', [])
                for link_data in result_links:
                    link_data['link'] = reverse(link_data['link'])
                item['result_links'] = result_links
            else:
                item['result_links'] = []
        return data

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_classifiers'] = TextUnitClassifier.objects.filter(is_active=True).exists()
        return ctx
