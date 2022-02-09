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
from collections import OrderedDict

# Django imports
from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import F, Q
from django.db.models.functions import Now, Coalesce
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.edit import FormView

# Project imports
from apps.analyze.models import TextUnitClassifier, DocumentClassifier
from apps.common.logger import CsLogger
from apps.common.mixins import JSONResponseView, JqPaginatedListView, CustomDetailView
from apps.common.model_utils.improved_django_json_encoder import ImprovedDjangoJSONEncoder
from apps.common.utils import get_api_module
from apps.deployment.app_data import DICTIONARY_DATA_URL_MAP
from apps.document.models import DocumentProperty, TextUnitProperty, DocumentType
from apps.dump.app_dump import get_model_fixture_dump, load_fixture_from_dump, download
from apps.project.models import Project
from apps.task.forms import LoadDocumentsForm, LoadFixtureForm, LocateForm, \
    UpdateElasticSearchForm, DumpFixtureForm, TaskDetailForm, BuildOCRRatingLanguageModelForm
from apps.task.models import Task
from apps.task.tasks import call_task, clean_tasks, purge_task, _call_task_func, LoadDocuments, \
    recall_task, find_tasks_by_session_ids, BuildOCRRatingLanguageModel
from apps.task.utils.task_utils import check_blocks
from task_names import RECALL_DISABLED_TASKS

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


project_api_module = get_api_module('project')

TASK_STARTED_MESSAGE = 'The task has been started. Click OK to close this window. ' \
                       'Click the refresh icon ⟳ in the top right of the grid to view task progress.'

logger = CsLogger.get_django_logger()


class TaskAccessMixin(PermissionRequiredMixin):
    raise_exception = True

    def has_permission(self):
        if self.request.method == 'POST':
            return self.request.user.has_perm('task.add_task')
        return self.request.user.has_perm('task.view_task')


class BaseTaskView(TaskAccessMixin, FormView):
    template_name = 'task/task_form.html'
    task_name = 'Task'

    def form_valid(self, form):
        block_msg = check_blocks(raise_error=False)
        if block_msg is not False:
            return HttpResponseForbidden(block_msg)
        data = form.cleaned_data
        data['user_id'] = self.request.user.pk
        call_task(self.task_name, **data)
        return redirect(reverse('task:task-list'))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['task_name'] = self.task_name
        return ctx


class BaseAjaxTaskView(TaskAccessMixin, JSONResponseView):
    task_class = None
    task_name = 'Task'
    form_class = None
    html_form_class = 'popup-form'
    task_started_message = TASK_STARTED_MESSAGE

    @staticmethod
    def json_response(data, **kwargs):
        return JsonResponse(data, encoder=ImprovedDjangoJSONEncoder, safe=False, **kwargs)

    def get(self, request, *args, **kwargs):
        block_msg = check_blocks(raise_error=False, error_message='Task is blocked.')
        if block_msg is not False:
            return HttpResponseForbidden(block_msg)
        if self.disallow_start():
            return HttpResponseForbidden(
                'Forbidden. Task "%s" is already started.' % self.task_name)
        form = self.form_class()
        # try to reorder form fields according with form.Meta.fields
        try:
            form.fields = OrderedDict((field_name, form.fields[field_name])
                                      for field_name in form.Meta.fields)
        except AttributeError:
            pass
        data = dict(header=form.header,
                    form_class=self.html_form_class,
                    form_data=form.as_p())
        self.provide_extra_task_data(request, data, *args, **kwargs)
        return self.json_response(data)

    def provide_extra_task_data(self, request, data, *args, **kwargs):
        pass

    def get_metadata(self):
        return getattr(self, 'metadata', None)

    def start_task(self, data):
        return call_task(self.task_class or self.task_name, **data)

    def disallow_start(self):
        return Task.disallow_start(self.task_name)

    def post(self, request, *args, **kwargs):
        block_msg = check_blocks(raise_error=False, error_message='Task is blocked.')
        if block_msg is not False:
            return HttpResponseForbidden(block_msg)
        if self.disallow_start():
            return HttpResponseForbidden('Forbidden. Such task is already started.')
        request_data = request.POST or request.data

        if self.form_class is None:
            data = request.POST.dict() or request.data
        else:
            form = self.form_class(data=request_data, files=request.FILES)
            if not form.is_valid():
                return self.json_response(form.errors, status=400)
            data = form.cleaned_data
        data['user_id'] = request.user.pk
        data['metadata'] = self.get_metadata()
        data['module_name'] = getattr(self, 'module_name', None) or self.__module__.replace('views', 'tasks')
        data['skip_confirmation'] = request_data.get('skip_confirmation') or False
        return self.start_task_and_return(data)

    def start_task_and_return(self, data):
        try:
            task_id = self.start_task(data)
        except Exception as e:
            return self.json_response(str(e), status=400)
        return self.json_response({'detail': self.task_started_message, 'task_id': task_id})


class LoadTaskView(TaskAccessMixin, JSONResponseView):
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
        return JsonResponse(data, encoder=ImprovedDjangoJSONEncoder, safe=False, **kwargs)

    def post(self, request, *args, **kwargs):
        data = request.POST.dict() or request.data
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
            delete = f'{task_alias}_delete' in data
            extra_prefix = f'{task_alias}_extra_'
            extra_args = {v[len(extra_prefix):]: data[v] for v in data if v.startswith(extra_prefix)}
            if any([repo_paths, file_path, delete]):
                try:
                    call_task(task_name,
                              repo_paths=repo_paths,
                              file_path=file_path,
                              delete=delete,
                              metadata=metadata,
                              extra_args=extra_args)
                except Exception as e:
                    return self.json_response(str(e), status=400)
                started_tasks.append(task_name)
        return self.json_response({'detail': TASK_STARTED_MESSAGE})


class LoadDocumentsView(BaseAjaxTaskView):
    task_class = LoadDocuments
    form_class = LoadDocumentsForm
    metadata = dict(
        result_links=[{'name': 'View Document List', 'link': 'document:document-list'},
                      {'name': 'View Text Unit List', 'link': 'document:text-unit-list'}])


class LocateTaskView(BaseAjaxTaskView):
    form_class = LocateForm
    html_form_class = 'popup-form locate-form'

    # ability to have custom tasks not declared in LOCATORS
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
        form = self.form_class(request.POST or request.data)
        if not form.is_valid():
            return self.json_response(form.errors, status=400)
        data = form.cleaned_data

        project_id = None
        project_ref = data.get('project')
        if project_ref:
            del data['project']
            project_id = project_ref.pk

        task_names = {i.split('_')[0] for i in data if i != 'parse'}
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
                    try:
                        call_task(task_name, **kwargs)
                    except Exception as e:
                        return self.json_response({'detail': str(e)}, status=400)

        # lexnlp tasks
        lexnlp_task_data = {}
        for task_name in lexnlp_task_names:
            kwargs = {k.replace('%s_' % task_name, ''): v for k, v in data.items()
                      if k.startswith(task_name)}
            if any(kwargs.values()):
                lexnlp_task_data[task_name] = kwargs

        if lexnlp_task_data:
            # allow to start "Locate" task anytime
            started_tasks.append('Locate({})'.format(', '.join(lexnlp_task_data.keys())))
            try:
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
            except Exception as e:
                return self.json_response({'detail': str(e)}, status=400)

        response_text = ''
        if started_tasks:
            response_text += f'{TASK_STARTED_MESSAGE}<br /><br />'
            response_text += 'Started tasks: [{}].<br />'.format(', '.join(started_tasks))
        if rejected_tasks:
            response_text += 'Some tasks were rejected (already started).<br />'
            response_text += 'Rejected Tasks: [{}]'.format(', '.join(rejected_tasks))
        return self.json_response({'detail': response_text})


class UpdateElasticsearchIndexView(BaseAjaxTaskView):
    task_name = 'Update Elasticsearch Index'
    form_class = UpdateElasticSearchForm


class TaskDetailView(TaskAccessMixin, CustomDetailView):
    model = Task

    def get_form_class(self):
        return TaskDetailForm

    def get_update_url(self):
        return None


class CleanTasksView(BaseAjaxTaskView):
    def post(self, request, *args, **kwargs):
        _call_task_func(clean_tasks, (), request.user.pk, queue=settings.CELERY_QUEUE_SERIAL)
        return self.json_response({'detail': 'Cleaning task started.'})


class PurgeTaskView(BaseAjaxTaskView):
    def post(self, request, *args, **kwargs):
        request_data = request.POST or request.data
        res = purge_task(task_pk=request_data.get('task_pk'), user_id=request.user.id if request.user else None)
        return JsonResponse(res, safe=False)


class RecallTaskView(BaseAjaxTaskView):
    def post(self, request, *args, **kwargs):
        request_data = request.POST or request.data
        res = recall_task(task_pk=request_data.get('task_pk'),
                          session_id=request_data.get('session_id'),
                          user_id=request.user.pk,
                          log_func=logger.error)
        return JsonResponse(res, safe=False)

    def get(self, request, *args, **kwargs):
        task_pk = request.GET.get('task_pk')
        task_ids = [task_pk]
        session_id = request.GET.get('session_id')
        task_status = Task.objects.get(pk=task_pk).status

        if session_id:
            task_ids = find_tasks_by_session_ids(session_id, task_status, 'Load Documents')

        return JsonResponse({'tasks': len(task_ids), 'status': task_status}, safe=False)


class TaskListView(TaskAccessMixin, JqPaginatedListView):
    model = Task
    ordering = '-date_start'
    json_fields = ['name', 'display_name', 'date_start', 'user_name', 'metadata',
                   'date_done', 'status', 'progress', 'time', 'date_work_start',
                   'work_time', 'worker', 'description', 'kwargs']

    db_time = Coalesce(F('date_done') - F('date_start'), Now() - F('date_start'))
    db_work_time = Coalesce(F('date_done') - F('date_work_start'), Now() - F('date_work_start'),
                            F('date_start') - F('date_start'))
    db_user = Coalesce(F('user__name'), F('main_task__user__name'))
    template_name = 'task/task_list.html'

    def get_queryset(self):
        qs = Task.objects.main_tasks(show_failed_excluded_from_tracking=True)\
            .exclude(Q(visible=False) & Q(status__in=Task.objects.NON_FAILED_STATES))\
            .order_by('-date_start')
        qs = qs.annotate(time=self.db_time, work_time=self.db_work_time, user_name=self.db_user)
        return qs

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['recallable'] = item['name'] not in RECALL_DISABLED_TASKS
            item['display_name'] = item['display_name'] or item['name']
            item['url'] = self.full_reverse('task:task-detail', args=[item['pk']])
            item['purge_url'] = reverse('task:purge-task')
            item['recall_url'] = reverse('task:recall-task')
            item['upload_session_id'] = ''
            if item['kwargs'] and 'session_id' in item['kwargs']:
                item['upload_session_id'] = item['kwargs']['session_id']
            item['result_links'] = []
            if item['metadata']:
                if isinstance(item['metadata'], dict):
                    metadata = item['metadata']
                    md = metadata.get('description')
                    if md:
                        item['description'] = md
                    result_links = metadata.get('result_links', [])
                    for link_data in result_links:
                        link_data['link'] = reverse(link_data['link'])
                    item['result_links'] = result_links

        return data

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from apps.task.app_vars import TASK_DIALOG_FREEZE_MS
        ctx['task_dialog_freeze_ms'] = TASK_DIALOG_FREEZE_MS.val()
        ctx['projects'] = \
            [(p.pk, p.name) for p in Project.objects.filter(type__code=DocumentType.GENERIC_TYPE_CODE)]
        ctx['active_text_unit_classifiers'] = TextUnitClassifier.objects.filter(is_active=True).exists()
        ctx['active_document_classifiers'] = DocumentClassifier.objects.filter(is_active=True).exists()
        if DocumentProperty.objects.exists():
            ctx['ls_document_properties'] = DocumentProperty.objects.order_by('key') \
                .values_list('key', flat=True).distinct()
        if TextUnitProperty.objects.exists():
            ctx['ls_text_unit_properties'] = TextUnitProperty.objects.order_by('key') \
                .values_list('key', flat=True).distinct()
        return ctx


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
        request_data = request.POST or request.data
        mode = request_data.get('mode', 'default')
        res = load_fixture_from_dump(data, mode)
        status = 200 if res['status'] == 'success' else 400
        return JsonResponse(res, status=status)


class DumpFixturesView(LoadFixturesView):
    form_class = DumpFixtureForm

    def post(self, request, *args, **kwargs):
        request_data = request.POST or request.data
        form = self.form_class(request_data)
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


class BuildOCRRatingLanguageModelView(BaseAjaxTaskView):
    task_name = BuildOCRRatingLanguageModel.name
    form_class = BuildOCRRatingLanguageModelForm

    html_form_class = 'popup-form import-documents-form'

    def provide_extra_task_data(self, request, data, *args, **kwargs):
        if hasattr(request, 'user') and request.user:
            data['user_id'] = request.user.pk
