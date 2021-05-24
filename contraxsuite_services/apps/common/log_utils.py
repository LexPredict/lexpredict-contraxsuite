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

import sys
from typing import List

from apps.common.logger import CsLogger
from contraxsuite_logging import HumanReadableTraceBackException

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


logger = CsLogger.get_logger(__name__)


def render_error(message: str, caused_by: Exception = None) -> str:
    if not caused_by:
        caused_by_tuple = sys.exc_info()
        if not caused_by_tuple:
            caused_by = caused_by_tuple[1]

    msg_lines = []
    if message:
        msg_lines.append(message + ('\n' if caused_by else ''))

    if caused_by:
        msg_lines.append('\nDetails:\n')
        msg_lines.extend(HumanReadableTraceBackException.from_exception(caused_by).human_readable_format())

    return ''.join(msg_lines)


class ProcessLogger:
    def set_progress_steps_number(self, steps):
        pass

    def step_progress(self):
        pass

    def info(self, message: str, **kwargs):
        logger.info(message, **kwargs)

    def debug(self, message: str, **kwargs):
        logger.debug(message, **kwargs)

    def error(self,
              message: str,
              field_code: str = None,
              exc_info: Exception = None,
              **kwargs):
        if field_code:
            message = f'{field_code}: {message or "error"}'
        logger.error(message, exc_info=exc_info, **kwargs)


class ConsoleLogger(ProcessLogger):
    def set_progress_steps_number(self, steps):
        pass

    def step_progress(self):
        pass

    def info(self, message: str, **kwargs):
        print(f'INFO: {message}')

    def debug(self, message: str, **kwargs):
        print(f'DEBUG: {message}')

    def error(self,
              message: str,
              field_code: str = None,
              exc_info: Exception = None,
              **kwargs):
        if field_code:
            message = f'{field_code}: {message or "error"}'
        if exc_info:
            message += f'{message or ""}\nException: {exc_info}'
        print(message)


class ErrorCollectingLogger(ProcessLogger):
    def __init__(self) -> None:
        super().__init__()
        self.field_problems = {}
        self.common_problems = []

    def set_progress_steps_number(self, steps):
        pass

    def step_progress(self):
        pass

    def info(self, message: str):
        logger.info(message)

    def error(self, message: str, field_code: str = None, exc_info: Exception = None):

        if not field_code:
            logger.error(message, exc_info=exc_info)
            self.common_problems.append(message)
            return

        logger.error(f'{field_code}: {message}', exc_info=exc_info)

        problems = self.field_problems.get(field_code)

        if problems is None:
            problems = []
            self.field_problems[field_code] = problems
        problems.append(message)

    def get_error(self):
        if self.common_problems or self.field_problems:
            return {'error': {
                'common_problems': self.common_problems,
                'field_problems': self.field_problems
            }}

    def raise_if_error(self):
        if self.common_problems or self.field_problems:
            messages = []  # type: List[str]
            if self.common_problems:
                messages.extend(self.common_problems)
            if self.field_problems:
                messages.extend(['Field: {0}. Error: {1}'.format(field_code, field_error)
                                 for field_code, field_error in self.field_problems.items()])
            raise Exception('\n'.join(messages))


def render_exception(e: Exception) -> str:
    return ''.join(HumanReadableTraceBackException.from_exception(e).human_readable_format())


def auto_str(cls):
    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )

    cls.__str__ = __str__
    return cls
