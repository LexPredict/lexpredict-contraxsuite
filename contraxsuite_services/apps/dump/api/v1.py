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
import coreapi
import coreschema

from tempfile import NamedTemporaryFile

# Django imports
from django.conf.urls import url
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.http import HttpResponse

# Third-party imports
from rest_framework import serializers, generics, schemas, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Project imports
from apps.common.schemas import CustomAutoSchema, ObjectResponseSchema
from apps.dump.app_dump import get_full_dump, get_field_values_dump,\
    get_model_fixture_dump, load_fixture_from_dump, download, get_app_config_dump

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


json_ct = 'application/json'


class BaseDumpViewSchema(CustomAutoSchema):

    def get_responses(self, path, method):
        response = {'200': {'content': {json_ct: {'schema': ObjectResponseSchema.object_schema}}},
                    '400': {'content': {json_ct: {'schema': ObjectResponseSchema.object_schema}}}}
        if method == 'PUT':
            response = {
                '200': {
                    'content': {
                        json_ct: {
                            'schema': {'type': 'string',
                                       'format': 'binary',
                                       'description': 'Json file with dumped data'}
                        },
                    }
                }
            }
        return response


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
        return HttpResponse(self.get_json_dump(), content_type=json_ct)

    def put(self, request, *args, **kwargs):
        """
        Upload field values
        """
        data = self.get_request_data(request)
        buf = io.StringIO()
        try:
            with NamedTemporaryFile(mode='w+', suffix='.json') as f:
                json.dump(data, f)
                f.seek(0)
                call_command(self._command, f.name, stdout=buf)
                buf.seek(0)
            return HttpResponse(content=self.get_json_dump(),
                                content_type=json_ct,
                                status=200)
        except:
            log = buf.read()
            tb = traceback.format_exc()
            data = {
                'log': log,
                'exception': tb
            }
            return HttpResponse(content=json.dumps(data),
                                content_type=json_ct,
                                status=400)


class DumpConfigView(BaseDumpView):
    """
    Dump all users, roles, email addresses, review statuses, review status groups,
    app vars, document types, fields, field detectors and document filters to json.
    """

    def __init__(self, *args, **kwargs):
        kwargs['command'] = 'loadnewdata'
        super().__init__(*args, **kwargs)

    def get_json_dump(self) -> str:
        return get_full_dump()


class DumpDocumentConfigView(BaseDumpView):
    """
    Dump document types, fields, field detectors and  document filters to json.
    """
    def get_json_dump(self) -> str:
        document_type_codes = self.request.GET.get('document_type_codes') or None
        if document_type_codes:
            document_type_codes = document_type_codes.split(',')
        return get_app_config_dump(document_type_codes)


class FieldValuesDumpAPIView(BaseDumpView):
    """
    Dump field values to json.
    """
    def get(self, request, *args, **kwargs):
        """
        Download field values
        """
        response = HttpResponse(content_type=json_ct)
        response['Content-Disposition'] = 'attachment; filename="{}.{}.{}"'.format(
            Site.objects.get_current(), 'field-values', 'json')
        json_data = get_field_values_dump()
        response.write(json_data)
        return response

    def put(self, request, *args, **kwargs):
        """
        Upload field values
        """
        file_ = request.FILES.dict().get('file')
        data = file_.read()
        try:
            with NamedTemporaryFile(mode='w+b', suffix='.json') as f:
                f.write(data)
                f.flush()
                call_command('loaddata', f.name)
            return Response("OK")
        except Exception as e:
            tb = traceback.format_exc()
            data = {
                'log': str(e),
                'exception': tb
            }
            return HttpResponse(content=json.dumps(data),
                                content_type=json_ct,
                                status=400)


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
                    },
                }
            }
        }
        return response


class DumpFixtureAPIView(generics.CreateAPIView):
    """
    Dump model objects into fixture json file.
    """
    permission_classes = [RunTaskPermission]
    serializer_class = DumpFixtureSerializer
    schema = DumpFixtureAPIViewSchema()

    coreapi_schema = schemas.ManualSchema(fields=[
        coreapi.Field(
            "app_name",
            required=True,
            location="form",
            schema=coreschema.String(max_length=10)
        ),
        coreapi.Field(
            "model_name",
            required=True,
            location="form",
            schema=coreschema.String(max_length=50)
        ),
        coreapi.Field(
            "filter_options",
            required=False,
            location="form",
            schema=coreschema.Object()
        ),
        coreapi.Field(
            "file_name",
            required=True,
            location="form",
            schema=coreschema.String(max_length=50)
        ),
        coreapi.Field(
            "indent",
            required=False,
            location="form",
            schema=coreschema.Integer(default=4)
        ),
    ])

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
    mode = serializers.CharField(max_length=10, required=False)
    encoding = serializers.CharField(max_length=10, required=False)


class LoadFixtureAPIViewSchema(CustomAutoSchema):

    def get_responses(self, path, method):
        response = {'200': {'content': {json_ct: {'schema': ObjectResponseSchema.object_schema}}},
                    '400': {'content': {json_ct: {'schema': ObjectResponseSchema.object_schema}}}}
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
