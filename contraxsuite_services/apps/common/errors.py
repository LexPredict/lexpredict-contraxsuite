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

from typing import Type, Optional

from rest_framework.response import Response

from apps.common.log_utils import render_error

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class APIRequestError(Exception):
    def __init__(self, message: str = None, caused_by: Exception = None, http_status_code: int = 400) -> None:
        super().__init__(message)
        self.http_status_code = http_status_code
        self.message = message
        if caused_by:
            self.details = render_error(message, caused_by=caused_by)
        else:
            self.details = None

    def to_frontend_error(self):
        return {
            'error': self.__class__.__name__,
            'message': self.message,
            'details': self.details
        }

    def to_response(self):
        return Response(data=self.to_frontend_error(), status=self.http_status_code)


def find_cause_of_type(exception: Exception, of_type: Type[Exception]) -> Optional[Exception]:
    ex = exception

    while True:
        if isinstance(ex, of_type):
            return ex

        if ex.__cause__ is not None and ex.__cause__ != ex:
            ex = ex.__cause__
        elif ex.__context__ is not None and ex.__context__ != ex:
            ex = ex.__context__
        else:
            break

    return None
