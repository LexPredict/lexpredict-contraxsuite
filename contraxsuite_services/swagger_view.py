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

from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONOpenAPIRenderer, OpenAPIRenderer
from rest_framework.schemas import get_schema_view
from rest_framework.schemas.openapi import SchemaGenerator as OpenAPISchemaGenerator

from apps.common.model_utils.improved_django_json_encoder import ImprovedDjangoJSONEncoder
from apps.users.authentication import CookieAuthentication

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class CustomJSONOpenAPIRenderer(JSONOpenAPIRenderer):
    format = 'openapi-json'

    def render(self, data, media_type=None, renderer_context=None):
        return json.dumps(data, indent=2, cls=ImprovedDjangoJSONEncoder).encode('utf-8')


class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    methods = ['get', 'post', 'put', 'patch', 'delete', 'options']

    def has_view_permissions(self, path, method, view):
        if view.request.user.is_superuser:
            return True
        return super().has_view_permissions(path, method, view)

    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request=request, public=public)
        schema['paths'] = OrderedDict(sorted(schema['paths'].items()))
        components = schema.get('components', {})
        security_schemes = components.get('securitySchemes', {})
        security_schemes['AuthToken'] = {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
        components['securitySchemes'] = security_schemes
        schema['components'] = components
        security = schema.get('security', [])
        security.append({'AuthToken': []})
        schema['security'] = security
        return schema


def get_openapi_view():
    return get_schema_view(
        title="Contraxsuite API",
        description="Contraxsuite API",
        version=settings.VERSION_NUMBER,
        generator_class=CustomOpenAPISchemaGenerator,
        permission_classes=[AllowAny],
        authentication_classes=[CookieAuthentication],
        renderer_classes=[
            OpenAPIRenderer,
            CustomJSONOpenAPIRenderer
        ]
    )
