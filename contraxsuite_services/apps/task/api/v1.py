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

import rest_framework.views
# Django imports
from django.conf.urls import url
# Third-party imports
from rest_framework import routers, serializers, viewsets

import apps.common.mixins
# Project imports
from apps.task.views import *

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
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


class TaskViewSet(apps.common.mixins.JqListAPIMixin, viewsets.ReadOnlyModelViewSet):
    """
    list: Task List
    retrieve: Retrieve Task
    """
    queryset = Task.objects.main_tasks(show_failed_excluded_from_tracking=True).order_by('-date_start')
    serializer_class = TaskSerializer

    def get_serializer_class(self):
        if self.action == 'stats':
            return TaskStatsSerializer
        return TaskSerializer


class LoadDictionariesAPIView(rest_framework.views.APIView, LoadTaskView):
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
    http_method_names = ["post"]


class LoadDocumentsAPIView(rest_framework.views.APIView, LoadDocumentsView):
    """
    "Load Documents" admin task\n
    POST params:
        - source_path: str
        - source_type: str
        - document_type: str
        - delete: bool
    """
    http_method_names = ["get", "post"]


class LocateTaskAPIVIew(rest_framework.views.APIView, LocateTaskView):
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
        - parse: str[paragraph, sentence]
    """
    http_method_names = ["get", "post"]


class ExistingClassifierClassifyAPIView(rest_framework.views.APIView, ExistedClassifierClassifyView):
    """
    "Classify using existing classifier" admin task\n
    POST params:
        - classifier_id: int
        - sample_size: int
        - min_confidence: int
        - delete_suggestions: bool
    """
    http_method_names = ["get", "post"]


class NewClassifierClassifyAPIView(rest_framework.views.APIView, CreateClassifierClassifyView):
    """
    "Classify using new classifier" admin task\n
    POST params:
        - classify_by: str[]
        - algorithm: str[]
        - class_name: str
        - sample_size: int
        - min_confidence: int
        - options: huge amount of options
        - use_tfidf: bool
        - delete_classifier: bool
        - delete_suggestions: bool
    """
    http_method_names = ["get", "post"]


class UpdateElasticsearchIndexAPIView(rest_framework.views.APIView, UpdateElasticsearchIndexView):
    """
    "Update ElasticSearch Index" admin task\n
    """
    http_method_names = ["get", "post"]


class ClusterAPIView(rest_framework.views.APIView, ClusterView):
    """
    "Cluster" admin task\n
    POST params:
        - do_cluster_documents: bool
        - do_cluster_text_units: bool
        - cluster_by: str[]
        - using: str[]
        - name: str
        - description: str
        - options: huge amount of options
        - delete_type: bool
        - delete: bool
    """
    http_method_names = ["get", "post"]


class CleanTasksAPIView(rest_framework.views.APIView, CleanTasksView):
    """
    "Clean Tasks" admin task\n
    """
    http_method_names = ["post"]


class PurgeTaskAPIView(rest_framework.views.APIView, PurgeTaskView):
    """
    "Purge Task" admin task\n
    POST params:
        - task_pk: int
    """
    http_method_names = ["post"]


class TaskStatusAPIView(rest_framework.views.APIView):
    """
    Check admin task status\n
    GET params:
        - task_id: int
    """

    def get(self, request, *args, **kwargs):
        task_id = request.GET.get('task_id')
        try:
            task = Task.objects.get(pk=task_id)
            message = {'progress': task.progress,
                       'status': task.status,
                       'date_done': task.date_done,
                       'time': task.time,
                       'date_start': task.date_start,
                       'user': task.user.username,
                       'result': task.result}
        except Task.DoesNotExist:
            message = "Task is not found"
        return JsonResponse(message, safe=False)


router = routers.DefaultRouter()
router.register(r'tasks', TaskViewSet, 'task')

urlpatterns = [
    url(r'^load-dictionaries/$', LoadDictionariesAPIView.as_view(),
        name='load-dictionaries'),
    url(r'^load-documents/$', LoadDocumentsAPIView.as_view(),
        name='locate'),
    url(r'^locate/$', LocateTaskAPIVIew.as_view(),
        name='locate'),
    url(r'^classify/$', ExistingClassifierClassifyAPIView.as_view(),
        name='classify'),
    url(r'^classify/new/$', NewClassifierClassifyAPIView.as_view(),
        name='classify-new'),
    url(r'^update-elastic-index/$', UpdateElasticsearchIndexAPIView.as_view(),
        name='update-elastic-index'),
    url(r'^cluster/$', ClusterAPIView.as_view(),
        name='cluster'),
    url(r'^clean-tasks/$', CleanTasksAPIView.as_view(),
        name='clean-tasks'),
    url(r'^purge-task/$', PurgeTaskAPIView.as_view(),
        name='purge-task'),
    url(r'^task-status/$', TaskStatusAPIView.as_view(),
        name='task-status'),
]
