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
import io

import pandas as pd

from django.http import HttpResponse

from rest_framework import exceptions
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.renderers import CoreJSONRenderer
from rest_framework.response import Response
from rest_framework.schemas import SchemaGenerator
from rest_framework.views import APIView
from rest_framework_swagger import renderers

from apps.common.utils import download_xls


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.6/LICENSE"
__version__ = "1.1.6"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def get_swagger_view():
    """
    Returns schema view which renders Swagger/OpenAPI.
    """
    class SwaggerSchemaView(APIView):
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

            if 'download' in request.GET:
                return download_xls(generator.get_simple_links(request),
                                    file_name='contraxsuite-api',
                                    sheet_name='api')

            return Response(schema)

    return SwaggerSchemaView.as_view()


class CustomSchemaGenerator(SchemaGenerator):

    def get_simple_links(self, request):
        links = []
        for path, method, callback in self.endpoints:
            view = self.create_view(callback, method, request)
            link = view.schema.get_link(path, method, base_url=self.url)
            api_version = group_name = None
            if link.url.startswith('/api'):
                url_parts = link.url.split('/', 5)[1:5]
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
