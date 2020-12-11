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
from django.conf.urls import url

# Third-party imports
from rest_framework import routers, serializers, viewsets, views
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response

# Project imports
from apps.common.mixins import JqListAPIMixin
from apps.task.views import *
from apps.task.schemas import TaskLogSchema, TaskStatusSchema, RunTaskBaseSchema

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# Serializers define the API representation.
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
    queryset = Task.objects.main_tasks(show_failed_excluded_from_tracking=True).order_by('-date_start')
    serializer_class = TaskSerializer
    permission_classes = [DjangoModelPermissions]

    def get_serializer_class(self):
        if self.action == 'stats':
            return TaskStatsSerializer
        return TaskSerializer


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
]
