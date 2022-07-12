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

import re
import sys

from django.conf import settings
from rest_framework import serializers
from rest_framework.schemas.openapi import AutoSchema

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


json_ct = 'application/json'
string_content = {'content': {json_ct: {'schema': {'type': 'string'}}}, 'description': ''}
binary_string_schema = {'schema': {'type': 'string', 'format': 'binary'}}
binary_string_content = {'content': {json_ct: binary_string_schema}, 'description': ''}
object_content = {'content': {json_ct: {'schema': {'type': 'object', 'additionalProperties': True}}},
                 'description': ''}
object_list_content = {
    'content': {json_ct: {'schema': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': True}}}},
    'description': ''}


class CustomAutoSchema(AutoSchema):

    parameters = None
    request_serializer = None
    response_serializer = None
    object_request_type_for_methods = ['POST', 'PUT', 'PATCH']

    def get_operation_id(self, path, method):
        """
        Compute an operation ID from path and method name to be unique.
        """
        path_name = '-'.join([i for i in path.strip('/').split('/')
                              if i != 'api' and not re.match(r'v\d+', i)])
        path_name = re.sub(r'[{}]', '', path_name)
        return f'{path_name}:{method}'

    def get_operation(self, path, method):
        """
        Substitute schema parameters
        """
        op = super().get_operation(path, method)

        if self.parameters:
            op['parameters'].extend(self.parameters)

        if method in ('POST', 'PUT', 'PATCH') and not self.get_request_serializer(path, method):
            op['requestBody'] = {
                'content': {
                    ct: {'schema': {'type': 'object', 'additionalProperties': {'type': 'object'}}}
                    for ct in self.request_media_types
                }
            }
        return op

    def get_component_name(self, serializer):
        return getattr(serializer, 'schema_component_name', None) or \
            super().get_component_name(serializer)

    def get_components(self, path, method):
        """
        Return components with their properties from the serializer.
        """
        if method.lower() == 'delete':
            return {}

        result = {}
        
        request_serializer = self.get_request_serializer(path, method)
        if isinstance(request_serializer, serializers.Serializer):
            component_name = self.get_component_name(request_serializer)
            content = self.map_serializer(request_serializer)
            result[component_name] = content

        response_serializer = self.get_response_serializer(path, method)
        if isinstance(response_serializer, serializers.Serializer):
            component_name = self.get_component_name(response_serializer)
            content = self.map_serializer(response_serializer)
            result[component_name] = content

        return result

    def get_request_serializer(self, path, method):
        return self.request_serializer or super().get_serializer(path, method)

    def get_response_serializer(self, path, method):
        if self.response_serializer:
            return self.response_serializer
        if hasattr(self.view, 'get_response_serializer') and callable(self.view.get_response_serializer):
            serializer = self.view.get_response_serializer()
            return serializer()
        return super().get_serializer(path, method)

    def get_serializer(self, path, method):
        """
        Get serializer for request or response separately
        """
        try:
            # get caller name, see
            # https://stackoverflow.com/questions/2654113/how-to-get-the-callers-method-name-in-the-called-method
            caller_name = sys._getframe().f_back.f_code.co_name
            if caller_name == 'get_request_body':
                return self.get_request_serializer(path, method)
            return self.get_response_serializer(path, method)
        except:
            return super().get_serializer(path, method)

    def map_serializer(self, serializer):
        result = super().map_serializer(serializer)
        result['type'] = 'object'
        return result

    def get_tags(self, path, method):
        """
        Tag endpoint to group by app name
        """
        if self._tags:
            return self._tags
        path = re.sub(r'api/(?:v\d+/)?', '', path.lstrip('/'))
        return [path.split('/')[0].replace('-', '_'), settings.REST_FRAMEWORK['DEFAULT_VERSION']]

    def map_field(self, field):
        if isinstance(field, serializers.SerializerMethodField):
            try:
                field = getattr(field.parent, field.method_name).output_field
                assert isinstance(field.output_field, serializers.Field)
                field = field.output_field
            except:
                pass
        # for cases when field is child of serializers.BooleanField - see FormSerializer
        elif isinstance(field, serializers.BooleanField):
            return {'type': 'boolean'}
        return super().map_field(field)


class ObjectResponseSchema(CustomAutoSchema):

    object_schema = {'type': 'object', 'additionalProperties': {'type': 'object'}}
    object_response_for_methods = ['GET']

    def __init__(self, *args, **kwargs):
        if 'object_response_for_methods' in kwargs:
            self.object_response_for_methods = kwargs.pop('object_response_for_methods')
        self.response_status = kwargs.pop('response_status', '200')
        super().__init__(*args, **kwargs)

    def get_responses(self, path, method):
        resp = super().get_responses(path, method)
        if method in self.object_response_for_methods:
            resp = {
                self.response_status: {
                    'description': '',
                    'content': {
                        json_ct: {
                            'schema': self.object_schema}}}}
        return resp


class ObjectToItemResponseMixin:

    def get_responses(self, path, method):
        resp = super().get_responses(path, method)
        item_schema = resp['200']['content'][json_ct]['schema']
        resp['200']['content'][json_ct]['schema'] = {'type': 'array', 'items': item_schema}
        return resp


class ObjectItemsResponseSchema(ObjectToItemResponseMixin, ObjectResponseSchema):
    pass


class JqFiltersListViewSchema(CustomAutoSchema):
    filters_param_name = 'jq_filters'
    _get_parameters = [
        {'name': filters_param_name,
         'in': 'query',
         'required': False,
         'description': '''Filter params similar to JQWidgets grid filter params: 
                           filterscount=1, 
                           filterdatafield0="a", 
                           filtervalue0="b", 
                           filtercondition0="CONTAINS", 
                           filteroperator0=1, 
                           sortdatafied="c",
                           sortorder="asc"
                           ''',
         'schema': {
             'type': 'object',
             'additionalProperties': {'type': 'string'}},
         'style': 'form',
         'explode': True
         },
    ]

    def get_operation(self, path, method):
        op = super().get_operation(path, method)
        if method == 'GET':
            op['parameters'].extend(self._get_parameters)
        return op
