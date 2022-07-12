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

from django.utils.duration import _get_duration_components
from rest_framework import serializers
from rest_framework.fields import DurationField

from apps.common.schemas import ObjectResponseSchema, ObjectToItemResponseMixin, JqFiltersListViewSchema, json_ct
from apps.common.mixins import SimpleRelationSerializer
from apps.task.models import Task

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TaskStatusSchema(ObjectResponseSchema):
    parameters = [
        {'name': 'task_id',
         'in': 'query',
         'required': False,
         'description': '',
         'schema': {'type': 'string'}}]

    def get_responses(self, path, method):
        res = super().get_responses(path, method)
        res['404'] = res['200']
        return res


class TaskLogSerializer(serializers.Serializer):
    task_name = serializers.CharField(source='log_task_name', required=False, default=None)
    log_level = serializers.CharField(source='level', required=False, default=None)
    message = serializers.CharField(required=False, default=None)
    timestamp = serializers.DateTimeField(source='@timestamp')
    stack_trace = serializers.CharField(source='log_stack_trace', required=False, default=None)
    regexp_search_fields = ['task_name', 'log_level']
    sortable_fields = ['task_name', 'log_level', 'timestamp']
    default_sort_field = 'timestamp'
    default_sort_order = 'asc'


class TaskLogResponseSerializer(serializers.Serializer):
    records = TaskLogSerializer()
    total_records_count = serializers.IntegerField()
    filtered_records_count = serializers.IntegerField()
    current_records_count = serializers.IntegerField()


class TaskLogSchema(JqFiltersListViewSchema):
    parameters = [
        {'name': 'task_id',
         'in': 'query',
         'required': True,
         'description': '',
         'schema': {'type': 'string'}},
        {'name': 'records_limit',
         'in': 'query',
         'required': False,
         'description': '',
         'schema': {'type': 'integer'}}
    ]
    response_serializer = TaskLogResponseSerializer()


class ProjectTaskLogSchema(TaskLogSchema):
    parameters = [
        {'name': 'records_limit',
         'in': 'query',
         'required': False,
         'description': '',
         'schema': {'type': 'integer'}}
    ]


class RunTaskBaseSchema(ObjectResponseSchema):
    object_response_for_methods = ['GET', 'POST']
    request_media_types = [json_ct, 'application/x-www-form-urlencoded', 'multipart/form-data']

    def get_responses(self, path, method):
        res = super().get_responses(path, method)
        if method == 'GET':
            return res
        return {
            '200': {
                'content': {json_ct: {'schema': self.object_schema}},
                'description': ''}}


class CheckTaskScheduleSchema(ObjectResponseSchema):

    class CheckTaskScheduleRequestSerializer(serializers.Serializer):
        schedule = serializers.CharField(required=False)

    request_serializer = CheckTaskScheduleRequestSerializer()

    def get_responses(self, path, method):
        resp = super().get_responses(path, method)
        resp['200'] = resp['201']
        del resp['201']
        resp['200']['content'][json_ct]['schema'] = self.object_schema
        return resp


class CustomDurationField(DurationField):

    def to_representation(self, value):
        days, hours, minutes, seconds, microseconds = _get_duration_components(value)

        string = '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
        if days:
            string = '{} '.format(days) + string
        if microseconds:
            if not any([days, hours, minutes, seconds]):
                string = '{:06d} ms'.format(microseconds)
            else:
                string += '.{:06d}'.format(microseconds)

        return string


class ProjectTasksSerializer(SimpleRelationSerializer):
    verbose_name = serializers.CharField()
    total_time = CustomDurationField()
    work_time = CustomDurationField()
    date_start = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    date_work_start = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    date_done = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    description = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'name', 'verbose_name', 'user__name', 'worker', 'status', 'progress', 'description',
                  'date_start', 'date_work_start', 'date_done', 'total_time', 'work_time']

    @staticmethod
    def format_args(args):
        if isinstance(args, (list, tuple)):
            return list(args)
        if isinstance(args, dict):
            return [f'{k}: {v}' for k, v in args.items()]
        if args:
            return [str(args)]
        return []

    def get_description(self, obj):
        args = self.format_args(obj.args)
        kwargs = self.format_args(obj.kwargs)
        metadata = self.format_args(obj.metadata)
        return '\n'.join(args + kwargs + metadata)


class ProjectTasksSchema(ObjectToItemResponseMixin, JqFiltersListViewSchema):
    response_serializer = ProjectTasksSerializer()


class ProjectActiveTasksSerializer(serializers.Serializer):
    tasks = ProjectTasksSerializer()
    document_transformer_change_in_progress = serializers.BooleanField()
    text_unit_transformer_change_in_progress = serializers.BooleanField()
    locate_terms_in_progress = serializers.BooleanField()
    locate_companies_in_progress = serializers.BooleanField()


class ProjectActiveTasksSchema(ObjectToItemResponseMixin, JqFiltersListViewSchema):
    response_serializer = ProjectActiveTasksSerializer()
