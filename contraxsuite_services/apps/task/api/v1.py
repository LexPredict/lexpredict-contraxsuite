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

import datetime
from dateutil import parser as date_parser

# Django imports
from django.db.models import Case, When, Value, CharField
from django.conf.urls import url
from django.utils.timezone import now

# Third-party imports
import croniter
from celery.states import PENDING
from elasticsearch_dsl import Search
from rest_framework import routers, serializers, viewsets, views
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.views import APIView

# Project imports
from apps.common.mixins import JqListAPIMixin
from apps.common.utils import download as download_file
from apps.extract.api.v1 import ViewSetDataMixin
from apps.task.models import es
from apps.task.schemas import TaskLogSerializer, TaskLogSchema, TaskStatusSchema, RunTaskBaseSchema, \
    CheckTaskScheduleSchema, ProjectTasksSchema, ProjectActiveTasksSchema, ProjectTasksSerializer
from apps.task.views import *

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    user__username = serializers.CharField(
        source='user.username',
        read_only=True)
    description = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['pk', 'name', 'date_start', 'date_work_start', 'user__username',
                  'date_done', 'duration', 'progress', 'status', 'has_error', 'description']

    def get_description(self, obj):
        result = None
        if obj.metadata:
            result = obj.metadata.get('description')
        return result


class TaskStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['status']


class TaskViewSet(JqListAPIMixin, viewsets.ReadOnlyModelViewSet):
    """
    list: Task List
    retrieve: Retrieve Task
    """
    queryset = Task.objects.main_tasks(show_failed_excluded_from_tracking=True)
    serializer_class = TaskSerializer
    permission_classes = [DjangoModelPermissions]

    def get_serializer_class(self):
        if self.action == 'stats':
            return TaskStatsSerializer
        if self.action in ['project_tasks', 'project_active_tasks']:
            return ProjectTasksSerializer
        return TaskSerializer

    def get_queryset(self):
        if self.action in ['project_tasks', 'project_active_tasks'] and 'project_id' in self.kwargs:
            qs = self.get_project_tasks(self.kwargs['project_id'])
            if self.action == 'project_active_tasks':
                qs = qs.filter(status=PENDING)
        else:
            qs = super().get_queryset()
        return qs.order_by('-date_start')

    @staticmethod
    def get_project_tasks(project_id):
        project_id = int(project_id)
        qs = Task.objects \
            .filter(
                Q(project_id=project_id) |
                Q(kwargs__project=project_id) |
                Q(kwargs__project_id=project_id) |
                Q(kwargs__project=[{'pk': project_id}])) \
            .annotate(total_time=Coalesce(F('date_done') - F('date_start'), Now() - F('date_start')),
                      work_time=Coalesce(F('date_done') - F('date_work_start'), Now() - F('date_work_start'),
                                         F('date_start') - F('date_start'))) \
            .annotate(verbose_name=Case(When(name='Locate', kwargs__tasks={'term': {'locate': True, 'delete': True}},
                                             then=Value('Locate Terms')),
                                        When(name='Locate', kwargs__tasks={'party': {'locate': True, 'delete': True}},
                                             then=Value('Locate Companies')),
                                        default=F('name'), output_field=CharField())) \
            .distinct()
        return qs

    @action(detail=False, schema=ProjectTasksSchema(), url_path=r'project/(?P<project_id>\d+)/tasks')
    def project_tasks(self, request, **kwargs):
        return self.list(request, **kwargs)

    @action(detail=False, schema=ProjectActiveTasksSchema(), url_path=r'project/(?P<project_id>\d+)/active-tasks')
    def project_active_tasks(self, request, **kwargs):
        res = super().list(request, **kwargs)
        if isinstance(res.data, list):
            res.data = {'tasks': res.data}
        elif isinstance(res.data, dict) and 'data' in res.data:
            # just rename response key to match schema
            res.data['tasks'] = res.data['data']
            del res.data['data']
        else:
            raise RuntimeError('Unknown response')

        # get specific task markers/flags
        qs = self.get_queryset()
        from apps.analyze.tasks import BuildDocumentVectorsTask, BuildTextUnitVectorsTask
        res.data.update({
            'document_transformer_change_in_progress': qs.filter(name=BuildDocumentVectorsTask.name).exists(),
            'text_unit_transformer_change_in_progress': qs.filter(name=BuildTextUnitVectorsTask.name).exists(),
            'locate_terms_in_progress': qs.filter(
                name='Locate', kwargs__tasks={'term': {'locate': True, 'delete': True}}).exists(),
            'locate_companies_in_progress': qs.filter(
                name='Locate', kwargs__tasks={'party': {'locate': True, 'delete': True}}).exists()
        })
        return res


class ReindexRoutineViewSet(APIView, ViewSetDataMixin):
    http_method_names = ['post']

    @classmethod
    def get_extra_actions(cls):
        return []

    @action(detail=False, methods=['post'], schema=CheckTaskScheduleSchema())
    def post(self, request, **kwargs):
        schedule = request.POST.get('schedule', '')
        data = {'errors': None, 'next': None, 'prev': None}
        if schedule:
            now_time = now()
            if not croniter.croniter.is_valid(schedule):
                data['errors'] = [
                    'Schedule string is invalid'
                ]
            else:
                cr = croniter.croniter(schedule, now_time)
                data['next'] = cr.get_next(datetime.datetime)
                data['prev'] = cr.get_prev(datetime.datetime)
        else:
            data['errors'] = 'Schedule is empty'
        return Response(data, content_type='application/json')


class RunTaskPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.has_perm('task.add_task')


class RunTaskBaseView(views.APIView):
    schema = RunTaskBaseSchema()
    permission_classes = [RunTaskPermission]


class LoadDictionariesAPIView(RunTaskBaseView, LoadTaskView):
    """
    "Load Dictionaries" admin task\n
    POST params:
        - terms_accounting: bool:
        - terms_accounting_1: bool:
        - terms_accounting_1_locale_en: bool:
        - terms_accounting_2: bool:
        - terms_accounting_2_locale_en: bool:
        - terms_accounting_3: bool:
        - terms_accounting_3_locale_en: bool:
        - terms_accounting_4: bool:
        - terms_accounting_4_locale_en: bool:
        - terms_accounting_5: bool:
        - terms_accounting_5_locale_en: bool:
        - terms_scientific: bool:
        - terms_scientific_1: bool:
        - terms_scientific1_locale_en: bool:
        - terms_financial: bool:
        - terms_financial_1: bool:
        - terms_financial_1_locale_en: bool:
        - terms_legal: bool:
        - terms_legal_1: bool:
        - terms_legal_1_locale_en: bool:
        - terms_legal_2: bool:
        - terms_legal_2_locale_en: bool:
        - terms_legal_3: bool:
        - terms_legal_3_locale_en: bool:
        - terms_legal_4: bool:
        - terms_legal_4_locale_en: bool:
        - terms_file_path: str:
        - terms_delete: bool:
        - courts: bool:
        - courts_1: bool:
        - courts_1_locale_en: bool:
        - courts_2: bool:
        - courts_2_locale_en: bool:
        - courts_file_path: str:
        - courts_delete: bool:
        - geoentities: bool:
        - geoentities_1: bool:
        - geoentities_1_locale_multi: bool:
        - geoentities_file_path: str:
        - geoentities_delete: bool:
    """
    http_method_names = ['post']


class LoadDocumentsAPIView(RunTaskBaseView, LoadDocumentsView):
    """
    "Load Documents" admin task\n
    POST params:
        - project: int
        - source_data: str
        - source_type: str
        - document_type: str
        - delete: bool
        - run_standard_locators: bool
    """
    http_method_names = ['get', 'post']


class LocateTaskAPIVIew(RunTaskBaseView, LocateTaskView):
    """
    "Locate" admin task\n
    POST params:
        - locate_all: bool
        - geoentity_locate: bool
        - geoentity_priority: bool
        - geoentity_delete: bool
        - date_locate: bool
        - date_strict: bool
        - date_delete: bool
        - amount_locate: bool
        - amount_delete: bool
        - citation_locate: bool
        - citation_delete: bool
        - copyright_locate: bool
        - copyright_delete: bool
        - court_locate: bool
        - court_delete: bool
        - currency_locate: bool
        - currency_delete: bool
        - duration_locate: bool
        - duration_delete: bool
        - definition_locate: bool
        - definition_delete: bool
        - distance_locate: bool
        - distance_delete: bool
        - party_locate: bool
        - party_delete: bool
        - percent_locate: bool
        - percent_delete: bool
        - ratio_locate: bool
        - ratio_delete: bool
        - regulation_locate: bool
        - regulation_delete: bool
        - term_locate: bool
        - term_delete: bool
        - trademark_locate: bool
        - trademark_delete: bool
        - url_locate: bool
        - url_delete: bool
        - parse_choice_sentence: bool
        - parse_choice_paragraph: bool
        - project: int
    """
    http_method_names = ['get', 'post']


class UpdateElasticsearchIndexAPIView(RunTaskBaseView, UpdateElasticsearchIndexView):
    """
    "Update ElasticSearch Index" admin task\n
    """
    http_method_names = ['get', 'post']


class CleanTasksAPIView(RunTaskBaseView, CleanTasksView):
    """
    "Clean Tasks" admin task\n
    """
    http_method_names = ['post']


class PurgeTaskAPIView(RunTaskBaseView, PurgeTaskView):
    """
    "Purge Task" admin task\n
    POST params:
        - task_pk: int
    """
    http_method_names = ['post']


class RecallTaskAPIView(RunTaskBaseView, RecallTaskView):
    """
    "Recall Task" admin task\n
    POST params:
        - task_pk: int
    """
    http_method_names = ['get', 'post']


class TaskAccessPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.has_perm('task.view_task')


class TaskStatusAPIView(views.APIView):
    """
    Check admin task status\n
    GET params:
        - task_id: int
    """
    http_method_names = ['get']
    schema = TaskStatusSchema()
    permission_classes = [TaskAccessPermission]

    def get(self, request, *args, **kwargs):
        task_id = request.GET.get('task_id')
        try:
            task = Task.objects.get(pk=task_id)
            message = {'progress': task.progress,
                       'status': task.status,
                       'date_done': task.date_done,
                       'time': task.duration,
                       'date_start': task.date_start,
                       'user': task.user.username if task.user else None,
                       'result': task.result}
        except Task.DoesNotExist:
            return Response({'detail': 'Task is not found'}, status=404)
        return Response(message)


class TaskLogAPIView(views.APIView):
    """
    Get task log records
    GET params:
        - task_id: int
        - records_limit: int
    """
    http_method_names = ['get']
    schema = TaskLogSchema()
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        task_id = request.GET.get('task_id')
        # via SDK call
        if task_id and isinstance(task_id, list):
            task_id = task_id[0]

        # filter/sort/paginate - otherwise use default logs extractor
        enable_filtering = self.request.GET.get('enable_filtering', 'true') == 'true'
        if enable_filtering:
            return self.filter_sort_and_paginate(task_id)

        records_limit = request.GET.get('records_limit') or 0
        try:
            task = Task.objects.get(pk=task_id)  # type: Task
            log_records = task.get_task_log_from_elasticsearch(records_limit=records_limit)

            message = {'records': [{
                'timestamp': r.timestamp,
                'log_level': r.log_level,
                'message': r.message,
                'stack_trace': r.stack_trace
            } for r in log_records]}
        except Task.DoesNotExist:
            return Response({'detail': 'Task is not found'}, status=404)
        return Response(message)

    def filter_sort_and_paginate(self, task_id, default_records_limit=10000):
        request_data = self.request.GET
        es_index = settings.LOGGING_ELASTICSEARCH_INDEX_TEMPLATE
        fields = TaskLogSerializer().fields

        source = [f.source or fn for fn, f in fields.items()]
        s = Search(using=es, index=es_index) \
            .filter("match", log_main_task_id=task_id) \
            .source(source)
        total_records_count = s.count()

        # FILTERS
        if request_data and 'filterscount' in request_data:

            for filter_n in range(int(request_data['filterscount'])):
                field_name = request_data.get(f'filterdatafield{filter_n}')
                value = request_data.get(f'filtervalue{filter_n}')
                if field_name is None or value is None:
                    continue
                if field_name not in fields:
                    continue
                field = fields[field_name]

                if isinstance(field, serializers.DateTimeField):
                    date = date_parser.parse(value)
                    s = s.query("range", **{'@timestamp': {'gte': date}})
                else:
                    es_field_name = field.source or field_name
                    if field_name in TaskLogSerializer.regexp_search_fields:
                        s = s.query("regexp", **{es_field_name: f'.*{value}.*'})
                        # TODO: for elasticsearch starting from 7.10.0 (debian requirement)
                        # s = s.query("regexp", **{es_field_name: {'value': f'.*{value}.*', 'case_insensitive': True}})
                        # s = s.query("wildcard", **{es_field_name: {'value': f'*{value}*', 'case_insensitive': True}})
                    else:
                        s = s.query("match", **{es_field_name: value})

        # SORTING
        # TODO: this doesn't work for "message" field because of indexes, need to change mapping/analyze, investigate
        if 'sortdatafield' in request_data and request_data['sortdatafield'] in fields \
                and request_data['sortdatafield'] in TaskLogSerializer.sortable_fields:
            sort_field_name = request_data['sortdatafield']
            sort_field = fields[sort_field_name]
            es_sort_field = sort_field.source or sort_field_name
            if request_data.get('sortorder') == 'desc':
                es_sort_field = '-' + es_sort_field
        else:
            sort_field_name = TaskLogSerializer.default_sort_field
            sort_field = fields[sort_field_name]
            es_sort_field = sort_field.source or sort_field_name
            if TaskLogSerializer.default_sort_order == 'desc':
                es_sort_field = '-' + es_sort_field
        s = s.sort(es_sort_field)

        # EXPORT - without paginated data - i.e. export all filtered/sorted rows up to default_records_limit
        if request_data.get('export_to') in ['csv', 'xlsx', 'pdf']:
            s = s[:default_records_limit]
            s = s.execute()
            log_data = TaskLogSerializer(s, many=True).data
            return download_file(log_data, request_data['export_to'], file_name='task_log')

        # PAGINATION - otherwise s.execute() takes first 10 records by default
        if 'pagenum' in request_data and 'pagesize' in request_data:
            start = int(request_data['pagenum']) * int(request_data['pagesize'])
            end = start + int(request_data['pagesize'])
            s = s[start:end]
        else:
            s = s[:default_records_limit]

        s = s.execute()
        log_data = TaskLogSerializer(s, many=True).data

        # response data signature should be equal to apps.task.schemas.TaskLogResponseSerializer
        data = {
            'records': log_data,
            'total_records_count': total_records_count,
            'filtered_records_count': s.hits.total.value,
            'current_records_count': len(log_data)
        }
        return Response(data)


class ProcessTextExtractionResultsView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, request_id: str, *_args, **_kwargs):
        from apps.common.errors import APIRequestError
        from task_names import TASK_NAME_PROCESS_TEXT_EXTRACTION_RESULTS
        try:
            task_statuses = list(Task.objects
                                 .filter(pk=request_id, name=TASK_NAME_PROCESS_TEXT_EXTRACTION_RESULTS)
                                 .values_list('own_status', flat=True))
            if not task_statuses:
                return APIRequestError(http_status_code=404, message='No such task.').to_response()

            if task_statuses[0] is not None:
                return APIRequestError(http_status_code=400, message='This task is already processed.') \
                    .to_response()

            Task.objects.filter(pk=request_id).update(status='PENDING', own_status='PENDING')

            from apps.celery import app
            app.re_send_task(request_id)
            return Response(status=200)
        except Exception as e:
            return APIRequestError(http_status_code=500, message='Exception caught', caused_by=e) \
                .to_response()


router = routers.DefaultRouter()
router.register(r'tasks', TaskViewSet, 'task')

urlpatterns = [
    url(r'^load-dictionaries/$', LoadDictionariesAPIView.as_view(),
        name='load-dictionaries'),
    url(r'^load-documents/$', LoadDocumentsAPIView.as_view(),
        name='locate'),
    url(r'^locate/$', LocateTaskAPIVIew.as_view(),
        name='locate'),
    url(r'^update-elastic-index/$', UpdateElasticsearchIndexAPIView.as_view(),
        name='update-elastic-index'),
    url(r'^clean-tasks/$', CleanTasksAPIView.as_view(),
        name='clean-tasks'),
    url(r'^purge-task/$', PurgeTaskAPIView.as_view(),
        name='purge-task'),
    url(r'^recall-task/$', RecallTaskAPIView.as_view(),
        name='recall-task'),
    url(r'^task-status/$', TaskStatusAPIView.as_view(),
        name='task-status'),
    url(r'^task-log/$', TaskLogAPIView.as_view(),
        name='task-log'),
    url(r'process_text_extraction_results/(?P<request_id>[\w-]+)/$', ProcessTextExtractionResultsView.as_view(),
        name='process_text_extraction_results'),
    url(r'reindexroutines/check_schedule', ReindexRoutineViewSet.as_view(),
        name='task-check-schedule'),
]
