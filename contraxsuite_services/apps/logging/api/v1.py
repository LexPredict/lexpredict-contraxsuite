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
import logging
import sys
from traceback import format_exc
from typing import Dict, List

from django.conf.urls import url
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.errors import APIRequestError
from apps.common.logger import CsLogger
from apps.common.schemas import CustomAutoSchema, ObjectResponseSchema, string_content, json_ct

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


logger = CsLogger.get_frontend_logger()
server_logger = CsLogger.get_django_server_logger()


class ApiLogFilter(logging.Filter):
    """
    Here I filter messages about "request to XXX was successfully processed,
    if the request is made to the logging API
    """
    def filter(self, record):
        # filter messages like ('POST /api/v1/logging/log_message/HTTP/1.1', '200', '0')
        if record.args:
            if len(record.args) > 2:
                if record.args[0].startswith('POST /api/v1/logging/') and \
                        record.args[1] == '200':
                    return False
        return True


log_filter = ApiLogFilter()
server_logger.filters.append(log_filter)


class ClientLogMessage:
    ALLOWED_LEVELS = {'info', 'error', 'critical', 'warning', 'exception'}

    def __init__(self, msg: str, level: str = 'info', user: Dict[str, str] = None) -> None:
        self.msg = msg
        self.level = level if level in self.ALLOWED_LEVELS else 'info'
        self.user = user
        self.query_info = {
            'ip': ''
        }

    def __repr__(self):
        msg_sender = '[%s]' % self.user if self.user else ''
        return '[%s]%s %s' % (self.level, msg_sender, self.msg)

    def serialize(self):
        return json.dumps({k: v for k, v in self.__dict__.items() if k != 'level' and v})

    def make_message_extra_dict(self) -> Dict[str, str]:
        d = {'log_client_ip': self.query_info['ip'],
             'log_client_agent': self.query_info['agent']}
        if self.user:
            d['log_user_id'] = self.user['id']
            d['log_user_name'] = self.user['name']
        return d

    @staticmethod
    def deserialize_msg_pack(data: Dict) -> List:
        items = []
        records = data.get('records') or []
        query_info = data.get('queryInfo') or {}
        for record in records:
            cm = ClientLogMessage('')
            for k in record:
                if not hasattr(cm, k):
                    continue
                setattr(cm, k, record[k])
            if not cm.msg:
                continue
            cm.level = cm.level if cm.level in ClientLogMessage.ALLOWED_LEVELS else 'info'
            cm.query_info.update(query_info)
            items.append(cm)
        return items


class LoggingAPIViewSchema(CustomAutoSchema):

    class LoggingAPIViewRequestSerializer(serializers.Serializer):
        queryInfo = serializers.DictField()
        records = serializers.ListField(child=serializers.DictField())

    request_serializer = LoggingAPIViewRequestSerializer()

    def get_responses(self, path, method):
        response = {'200': {'content': {json_ct: {'schema': ObjectResponseSchema.object_schema}}, 'description': ''},
                    '400': string_content,
                    '500': string_content}
        return response


class LoggingAPIView(APIView):
    permission_classes = ()
    schema = LoggingAPIViewSchema()

    def post(self, request, *args, **kwargs) -> Response:
        """
        Log provided data
        """
        try:
            data = request.data
            messages = ClientLogMessage.deserialize_msg_pack(data)
            user = self.format_user_from_request(request)
            ip = self.get_client_ip(request)
            for msg in messages:
                if user:
                    msg.user = user
                msg.query_info['ip'] = ip
                self.write_log(msg)

        except APIRequestError as e:
            return e.to_response()
        except Exception as e:
            return APIRequestError(message='Unable to process request',
                                   caused_by=e, http_status_code=500).to_response()
        return Response()

    @staticmethod
    def format_user_from_request(request) -> Dict[str, str]:
        if request.user and request.user.username:
            return {'id': request.user.id, 'name': request.user.username}

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def write_log(self, message: ClientLogMessage) -> bool:
        level = message.level
        msg_text = message.msg
        msg_extra = message.make_message_extra_dict()
        try:
            lgr = getattr(logger, level)
            lgr(msg_text, extra=msg_extra)
            return True
        except Exception:
            trace = format_exc()
            exc_class, exception, _ = sys.exc_info()
            exception_str = '%s: %s' % (exc_class.__name__, str(exception))

            logger.error(
                'Exception caught while trying to log a message:\n{0}\n{1}'.format(exception_str,
                                                                                   trace),
                extra=msg_extra)


urlpatterns = [
    url('log_message/', LoggingAPIView.as_view(), name='log_message')
]
