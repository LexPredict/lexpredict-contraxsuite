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

# Standard imports
import abc
import io
import json
import traceback
from tempfile import NamedTemporaryFile

# Django imports
from django.conf.urls import url
from django.core.management import call_command
from django.http import JsonResponse, HttpResponse

# Third-party imports
from rest_framework import serializers, generics, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Project imports
from apps.common.schemas import CustomAutoSchema, json_ct, string_content, object_content, object_list_content
from apps.dump.app_dump import get_full_dump, get_field_values_dump, \
    get_model_fixture_dump, load_fixture_from_dump, download, get_app_config_dump

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DumpPUTErrorResponseSerializer(serializers.Serializer):
    log = serializers.CharField()
    exception = serializers.CharField()


class BaseDumpViewSchema(CustomAutoSchema):

    get_parameters = [
        {'name': 'download',
         'in': 'query',
         'required': False,
         'description': 'Download as file',
         'schema': {
             'type': 'boolean'}
         }
    ]

    def get_responses(self, path, method):
        if method == 'GET':
            return {'200': {
                        'content': {
                            json_ct: {
                                'schema': {
                                    'oneOf': [
                                        {'type': 'array', 'items': {'type': 'object', 'additionalProperties': True}},
                                        {'type': 'string', 'format': 'binary',
                                         'description': 'Json file with dumped fixture'}]}}},
                        'description': ''},
                    '400': object_content}

        if method == 'PUT':
            return {'200': string_content,
                    '400': {
                        'content': {
                            json_ct: {
                                'schema': self._get_reference(DumpPUTErrorResponseSerializer())}},
                        'description': ''}}
        raise NotImplementedError()

    def get_components(self, path, method):
        res = super().get_components(path, method)
        bad_response_component_name = self.get_component_name(DumpPUTErrorResponseSerializer())
        bad_response_component_content = self.map_serializer(DumpPUTErrorResponseSerializer())
        res[bad_response_component_name] = bad_response_component_content
        return res

    def get_operation(self, path, method):
        op = super().get_operation(path, method)

        if method == 'GET':
            op['parameters'].extend(self.get_parameters)
            if hasattr(self, '_get_parameters'):
                op['parameters'].extend(self._get_parameters)

        elif method == 'PUT' and not self.get_request_serializer(path, method):
            op['requestBody'] = object_list_content

        return op


class RunTaskPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.has_perm('task.add_task')


class BaseDumpView(views.APIView):
    permission_classes = [RunTaskPermission]
    schema = BaseDumpViewSchema()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._command = kwargs.get('command') or 'loaddata'

    def get_request_data(self, request):
        return request.data

    @abc.abstractmethod
    def get_json_dump(self) -> str:
        raise Exception('Not implemented')

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content=self.get_json_dump(), content_type=json_ct)
        if request.GET.get('download') == 'true':
            response['Content-Disposition'] = 'attachment; filename="dump.json"'
        return response

    def put(self, request, *args, **kwargs):
        data = self.get_request_data(request)
        buf = io.StringIO()
        try:
            with NamedTemporaryFile(mode='w+', suffix='.json') as f:
                json.dump(data, f)
                f.seek(0)
                call_command(self._command, f.name, stdout=buf)
                buf.seek(0)
            return JsonResponse(data='OK', status=200, safe=False)
        except:
            log = buf.read()
            tb = traceback.format_exc()
            data = {'log': log, 'exception': tb}
            return JsonResponse(data=data, status=400)


class DumpConfigView(BaseDumpView):
    """
    Dump all users, email addresses, review statuses, review status groups,
    app vars, document types, fields, field detectors and document filters to json.
    """

    def __init__(self, *args, **kwargs):
        kwargs['command'] = 'loadnewdata'
        super().__init__(*args, **kwargs)

    def get_json_dump(self) -> str:
        return get_full_dump()


class DumpDocumentConfigSchema(BaseDumpViewSchema):

    _get_parameters = [
        {'name': 'document_type_codes',
         'in': 'query',
         'required': False,
         'description': 'Document Type codes separated by comma',
         'schema': {
             'type': 'string'}
         }
    ]


class DumpDocumentConfigView(BaseDumpView):
    """
    Dump document types, fields, field detectors and  document filters to json.
    """
    schema = DumpDocumentConfigSchema()

    def get_json_dump(self) -> str:
        document_type_codes = self.request.GET.get('document_type_codes') or None
        if document_type_codes:
            document_type_codes = document_type_codes.split(',')
        return get_app_config_dump(document_type_codes)


class FieldValuesDumpAPISchema(BaseDumpViewSchema):

    def get_operation(self, path, method):
        op = super().get_operation(path, method)
        if method == 'PUT':
            op['requestBody'] = object_list_content
        return op


class FieldValuesDumpAPIView(BaseDumpView):
    """
    Dump field values to json.
    """
    schema = FieldValuesDumpAPISchema()

    def get_json_dump(self) -> str:
        return get_field_values_dump()

    def put(self, request, *args, **kwargs):
        """
        Upload field values
        """
        try:
            with NamedTemporaryFile(mode='w+', suffix='.json') as f:
                f.write(json.dumps(request.data))
                f.flush()
                call_command('loaddata', f.name)
            return Response('OK')
        except Exception as e:
            tb = traceback.format_exc()
            data = {'log': str(e), 'exception': tb}
            return JsonResponse(data=data, status=400)


class DumpFixtureSerializer(serializers.Serializer):
    app_name = serializers.CharField(required=True)
    model_name = serializers.CharField(required=True)
    file_name = serializers.CharField(required=True)
    filter_options = serializers.JSONField(required=False)
    indent = serializers.IntegerField(required=False, default=4)


class DumpFixtureAPIViewSchema(CustomAutoSchema):
    request_serializer = DumpFixtureSerializer()

    def get_responses(self, path, method):
        response = {
            '200': {
                'content': {
                    json_ct: {
                        'schema': {'type': 'string',
                                   'format': 'binary',
                                   'description': 'Json file with dumped fixture'}
                    }},
                'description': ''}
            }
        return response


class DumpFixtureAPIView(generics.CreateAPIView):
    """
    Dump model objects into fixture json file.
    """
    permission_classes = [RunTaskPermission]
    serializer_class = DumpFixtureSerializer
    schema = DumpFixtureAPIViewSchema()

    def post(self, request, *args, **kwargs):
        """
        Download model fixture
        """
        serializer = DumpFixtureSerializer(data=request.data)
        if not serializer.is_valid():
            return Response('Data is not valid')
        form_data = serializer.data
        file_name = form_data.pop('file_name')
        json_data = get_model_fixture_dump(**form_data)
        return download(json_data, file_name)


class LoadFixtureSerializer(serializers.Serializer):
    fixture = serializers.CharField(required=True)
    mode = serializers.ChoiceField(choices=['default', 'shift', 'partial', 'soft'], required=False, default='default')
    encoding = serializers.CharField(max_length=10, required=False, default='utf=8')


class LoadFixtureAPIViewSchema(CustomAutoSchema):

    def get_responses(self, path, method):
        response = {'200': object_list_content,
                    '400': object_content}
        return response


class LoadFixtureAPIView(generics.CreateAPIView):
    """
    Load model objects from fixture json file.
    """
    serializer_class = LoadFixtureSerializer
    permission_classes = [RunTaskPermission]
    schema = LoadFixtureAPIViewSchema()

    def post(self, request, *args, **kwargs):
        """
        Install model fixtures
        """
        request_data = request.data or request.POST
        data = request_data['fixture']
        if isinstance(data, str):
            encoding = request_data.get('encoding', 'utf-8')
            data = data.encode(encoding)
        mode = request_data.get('mode', 'default')
        res = load_fixture_from_dump(data, mode)
        status = 200 if res['status'] == 'success' else 400
        return Response(res, status=status)


urlpatterns = [
    url(r'dump/', DumpConfigView.as_view(), name='dump'),
    url(r'field-values/', FieldValuesDumpAPIView.as_view(), name='field-values'),
    url(r'dump-fixture/', DumpFixtureAPIView.as_view(), name='dump-fixture'),
    url(r'load-fixture/', LoadFixtureAPIView.as_view(), name='load-fixture'),
    url(r'document-config/', DumpDocumentConfigView.as_view(), name='document-config'),
]
