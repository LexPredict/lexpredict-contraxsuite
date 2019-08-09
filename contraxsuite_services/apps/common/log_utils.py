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

import logging
import sys
import traceback

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


logger = logging.getLogger(__name__)


def render_error(message: str, caused_by: Exception = None) -> str:
    if caused_by:
        exc_type = caused_by.__class__
        exc_obj = caused_by
        exc_tb = caused_by.__traceback__
    else:
        exc_type, exc_obj, exc_tb = sys.exc_info()
    details = traceback.extract_tb(exc_tb)
    msg = message + \
          f'\nError: {exc_type.__name__}: {exc_obj}.\nDetails: '
    msg += '\n'.join([str(d) for d in details])
    if caused_by and hasattr(caused_by, 'detailed_error'):
        msg += f'\nCustom message: {caused_by.detailed_error}'
    return msg


class ProcessLogger:
    def set_progress_steps_number(self, steps):
        pass

    def step_progress(self):
        pass

    def info(self, message: str):
        logger.info(message)

    def error(self, message: str, field_code: str = None):
        logger.error(message)


class ErrorCollectingLogger(ProcessLogger):
    def __init__(self) -> None:
        super().__init__()
        self.field_problems = {}
        self.common_problems = list()

    def set_progress_steps_number(self, steps):
        pass

    def step_progress(self):
        pass

    def info(self, message: str):
        logger.info(message)

    def error(self, message: str, field_code: str = None):
        logger.error('{0}: {1}'.format(field_code, message))
        if not field_code:
            self.common_problems.append(message)
            return

        problems = self.field_problems.get(field_code)

        if problems is None:
            problems = list()
            self.field_problems[field_code] = problems
        problems.append(message)

    def get_error(self):
        if self.common_problems or self.field_problems:
            return {'error': {
                'common_problems': self.common_problems,
                'field_problems': self.field_problems
            }}
        else:
            return None

    def raise_if_error(self):
        if self.common_problems or  self.field_problems:
            messages = list()  # type: List[str]
            if self.common_problems:
                messages.extend(self.common_problems)
            if self.field_problems:
                messages.extend(['Field: {0}. Error: {1}'.format(field_code, field_error)
                                 for field_code, field_error in self.field_problems.items()])
            raise Exception('\n'.join(messages))
