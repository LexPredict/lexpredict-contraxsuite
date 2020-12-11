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

from rest_framework import serializers

from apps.common.schemas import ObjectResponseSchema

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DocumentsAPIViewSchema(ObjectResponseSchema):
    object_response_for_methods = ['GET', 'POST']

    get_parameters = [
        {'name': 'project_ids',
         'in': 'query',
         'required': False,
         'description': 'Project ids separated by commas',
         'schema': {
             'type': 'string'}
         },
        {'name': 'columns',
         'in': 'query',
         'required': False,
         'description': 'Column names separated by commas',
         'schema': {
             'type': 'string'}
         },
        {'name': 'associated_text',
         'in': 'query',
         'required': False,
         'description': 'Boolean - show associated text',
         'schema': {
             'type': 'boolean'}
         },
        {'name': 'as_zip',
         'in': 'query',
         'required': False,
         'description': 'Boolean - export as zip',
         'schema': {
             'type': 'boolean'}
         },
        {'name': 'fmt',
         'in': 'query',
         'required': False,
         'description': 'Export format',
         'schema': {
             'type': 'string',
             'enum': ['json', 'csv', 'xlsx']}
         },
        {'name': 'limit',
         'in': 'query',
         'required': False,
         'description': 'Page Size',
         'schema': {
             'type': 'integer'}
         },
        {'name': 'order_by',
         'in': 'query',
         'required': False,
         'description': 'Sort order - column names separated by commas',
         'schema': {
             'type': 'string'}
         },
        {'name': 'saved_filters',
         'in': 'query',
         'required': False,
         'description': 'Saved filter ids separated by commas',
         'schema': {
             'type': 'string'}
         },
        {'name': 'save_filter',
         'in': 'query',
         'required': False,
         'description': 'Save filter',
         'schema': {
             'type': 'boolean'}
         },
        {'name': 'return_reviewed',
         'in': 'query',
         'required': False,
         'description': 'Return Reviewed documents count',
         'schema': {
             'type': 'boolean'}
         },
        {'name': 'return_total',
         'in': 'query',
         'required': False,
         'description': 'Return total documents count',
         'schema': {
             'type': 'boolean'}
         },
        {'name': 'return_data',
         'in': 'query',
         'required': False,
         'description': 'Return data',
         'schema': {
             'type': 'boolean'}
         },
        {'name': 'ignore_errors',
         'in': 'query',
         'required': False,
         'description': 'Ignore errors',
         'schema': {
             'type': 'boolean'}
         },
        {'name': 'filters',
         'in': 'query',
         'required': False,
         'description': 'Filter params',
         'schema': {
             'type': 'object',
             'additionalProperties': {'type': 'string'}},
         'style': 'form',
         'explode': True
         }
    ]
    post_schema_name = 'RawdbDocumentsPOSTRequest'

    def get_post_request_schema(self):
        """
        Copy GET query params into requestBody
        """
        props = {}
        for param in self.get_parameters:
            param_name = param['name']
            props[param_name] = {'type': param['schema']['type']}
            if 'additionalProperties' in param['schema']:
                props[param_name]['additionalProperties'] = param['schema']['additionalProperties']
        return {'type': 'object', 'properties': props}

    def get_request_body(self, path, method):
        res = super().get_request_body(path, method)
        if method == 'POST':
            for ct in res['content']:
                res['content'][ct]['schema'] = {
                    '$ref': f'#/components/schemas/{self.post_schema_name}'}
        return res

    def get_operation(self, path, method):
        op = super().get_operation(path, method)
        if method == 'GET':
            op['parameters'].extend(self.get_parameters)
        else:
            op['requestBody'] = self.get_request_body(path, method)
        return op

    def get_components(self, path, method):
        if method == 'POST':
            return {self.post_schema_name: self.get_post_request_schema()}
        return super().get_components(path, method)
