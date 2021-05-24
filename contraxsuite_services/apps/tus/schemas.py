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

from apps.common.schemas import CustomAutoSchema, json_ct, string_content, object_content, binary_string_schema

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TusUploadViewSetSchema(CustomAutoSchema):
    request_post_headers = [
        {'name': 'force',
         'in': 'header',
         'required': False,
         'description': 'Upload a file even if it exists.',
         'schema': {'type': 'boolean'}},
        {'name': 'Upload-Length',
         'in': 'header',
         'required': True,
         'description': 'File length.',
         'schema': {'type': 'integer'}},
        {'name': 'Upload-Metadata',
         'in': 'header',
         'required': True,
         'description': 'Upload metadata include file name, relative path, etc.',
         'schema': {'type': 'string'}},
        {'name': 'Tus-Resumable',
         'in': 'header',
         'required': True,
         'description': '1.0.0',
         'schema': {'type': 'string'}},
    ]
    request_patch_headers = [
        {'name': 'force',
         'in': 'header',
         'required': False,
         'description': 'Upload a file even if it exists.',
         'schema': {'type': 'boolean'}},
        {'name': 'Upload-Offset',
         'in': 'header',
         'required': True,
         'description': 'Upload offset, bytes.',
         'schema': {'type': 'integer'}},
        {'name': 'Tus-Resumable',
         'in': 'header',
         'required': True,
         'description': '1.0.0',
         'schema': {'type': 'string'}},
    ]
    response_post_headers = {
        'Location': {'schema': {'type': 'string'}},
        'Upload-Expires': {'schema': {'type': 'string'}},
        'Tus-Resumable': {'schema': {'type': 'string'}},
    }
    response_patch_headers = {
        'Upload-Offset': {'schema': {'type': 'integer'}},
        'Upload-Expires': {'schema': {'type': 'string'}},
        'Tus-Resumable': {'schema': {'type': 'string'}},
    }

    def get_operation(self, path, method):
        """
        Substitute schema parameters
        """
        op = super().get_operation(path, method)
        if method == 'POST':
            op['parameters'] += self.request_post_headers
        if method == 'PATCH':
            op['parameters'] += self.request_patch_headers
        return op

    def get_request_body(self, path, method):
        if method == 'PATCH':
            return {
                'content': {
                    'application/offset+octet-stream': binary_string_schema},
                'description': ''}
        return object_content

    def get_responses(self, path, method):
        response = {}
        status_schema_content = {
            json_ct: {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'status': {
                            'type': 'string'}}}}}

        if method == 'POST':
            response['201'] = {'headers': self.response_post_headers, 'description': ''}
            response['400'] = {'content': status_schema_content, 'description': ''}

        elif method == 'PATCH':
            response['204'] = {'headers': self.response_patch_headers,
                               'content': status_schema_content,
                               'description': ''}
            response['400'] = string_content
            response['460'] = string_content
            response['500'] = string_content
        return response
