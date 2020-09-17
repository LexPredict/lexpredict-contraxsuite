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

import json
import re
from collections import OrderedDict

from django.conf import settings

from rest_framework import exceptions
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.renderers import CoreJSONRenderer, JSONOpenAPIRenderer, OpenAPIRenderer
from rest_framework.response import Response
from rest_framework.schemas import coreapi, get_schema_view
from rest_framework.schemas.openapi import AutoSchema, SchemaGenerator as OpenAPISchemaGenerator

from apps.common.model_utils.improved_django_json_encoder import ImprovedDjangoJSONEncoder

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def get_swagger_view():
    """
    Returns schema view which renders Swagger/OpenAPI.
    """
    from rest_framework.views import APIView
    from rest_framework.schemas import SchemaGenerator

    class CustomSchemaGenerator(SchemaGenerator):
        def create_view(self, callback, method, request=None):
            view = super().create_view(callback, method, request=request)
            try:
                view.schema = getattr(view, 'coreapi_schema', coreapi.AutoSchema())
            except AttributeError:
                pass
            return view

        def get_schema(self, request=None, public=False):
            """
            Generate a `coreapi.Document` representing the API schema.
            """
            schema = super().get_schema(request=request, public=public)
            schema._url = f'{settings.API_URL_PROTOCOL}://{settings.HOST_NAME}{request.path}'
            return schema

        def get_simple_links(self, request):
            links = []
            for path, method, callback in self.endpoints:
                view = self.create_view(callback, method, request)
                link = view.schema.get_link(path, method, base_url=self.url)
                api_version = group_name = None
                if link.url.startswith('/api'):
                    url_parts = link.url.split('/', 5)[1:5]
                    if len(url_parts) != 4:
                        continue
                    source, api_version, app_name, group_name = url_parts
                else:
                    url_parts = link.url.split('/', 3)[1:3]
                    source, app_name = url_parts
                links.append(
                    dict(
                        url=link.url,
                        source=source,
                        api_version=api_version,
                        app_name=app_name,
                        group_name=group_name,
                        method=link.action.upper(),
                        description=link.description,
                        title=link.description.split('\n')[0]
                        if link.description else view.__class__.__name__,
                    )
                )
            return links

    class SwaggerSchemaView(APIView):

        from rest_framework_swagger import renderers
        _ignore_model_permissions = True
        exclude_from_schema = True
        permission_classes = [AllowAny]
        authentication_classes = [SessionAuthentication]
        renderer_classes = [
            CoreJSONRenderer,
            renderers.OpenAPIRenderer,
            renderers.SwaggerUIRenderer
        ]

        def get(self, request, group_by='app'):
            generator = CustomSchemaGenerator()
            schema = generator.get_schema(request=request)

            if not schema:
                raise exceptions.ValidationError(
                    'The schema generator did not return a schema Document'
                )

            # regroup data according to passed "group_by" param
            _data = schema._data
            if 'api' in _data:
                if group_by == 'version':
                    _data.update(_data['api'])
                else:
                    for app_name in _data['api'].data.keys():
                        _data.update(_data['api'].data[app_name])
                _data.pop('api', None)
                schema._data = _data

            from apps.common.utils import download_xls
            if 'download' in request.GET:
                return download_xls(generator.get_simple_links(request),
                                    file_name='contraxsuite-api',
                                    sheet_name='api')

            return Response(schema)

    return SwaggerSchemaView.as_view()


def get_path_tags(path):
    path_tags = []
    path_parts = path.strip('/').split('/')
    if path_parts:
        if path_parts[0] == 'api':
            if re.match(r'v\d+', path_parts[1]):
                path_tags.append(path_parts[2])
            else:
                path_tags.append('api-other')
        else:
            path_tags.append(path_parts[0])
    return path_tags


class CustomAutoSchema(AutoSchema):

    def _get_operation_id(self, path, method):
        """
        Compute an operation ID from the model, serializer or view name.
        """
        method_name = getattr(self.view, 'action', method.lower())
        if method_name not in self.method_mapping:
            action = method_name
        else:
            action = self.method_mapping[method.lower()]

        name = re.sub(r'(?:ViewSet|APIView|ApiView|View)$', '', self.view.__class__.__name__)

        path_tag = ''.join(get_path_tags(path))

        return f'{path_tag}:{name}:{action}:{method}'


class CustomJSONOpenAPIRenderer(JSONOpenAPIRenderer):
    format = 'openapi-json'

    def render(self, data, media_type=None, renderer_context=None):
        return json.dumps(data, indent=2, cls=ImprovedDjangoJSONEncoder).encode('utf-8')


class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    methods = ['get', 'post', 'put', 'patch', 'delete', 'options']

    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request=request, public=public)

        # regroup data according to passed "group_by" param
        group_by = request.GET.get('group_by')
        if group_by == 'app':
            for path, path_schema in schema['paths'].items():
                path_tags = get_path_tags(path)
                if path_tags:
                    method = None
                    for _method in self.methods:
                        if _method in path_schema:
                            method = _method
                            break
                    if method:
                        path_schema[method]['tags'] = path_tags
                path_schema['tags'] = path_tags
            schema['paths'] = OrderedDict(sorted(schema['paths'].items()))

        return schema


# TODO: merge with get_swagger_view()
def get_openapi_view():
    return get_schema_view(
        title="Contraxsuite API",
        description="Contraxsuite API",
        generator_class=CustomOpenAPISchemaGenerator,
        permission_classes=[AllowAny],
        authentication_classes=[SessionAuthentication],
        renderer_classes=[
            OpenAPIRenderer,
            CustomJSONOpenAPIRenderer
        ]
    )
