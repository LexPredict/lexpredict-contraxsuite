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
from apps.common.schemas import ObjectResponseSchema, ObjectItemsResponseSchema, json_ct

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
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


class TaskLogSchema(ObjectResponseSchema):
    parameters = [
        {'name': 'task_id',
         'in': 'query',
         'required': False,
         'description': '',
         'schema': {'type': 'string'}},
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
                'content': {json_ct: {'schema': self.object_schema}}}}
