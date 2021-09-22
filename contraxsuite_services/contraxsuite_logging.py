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

import datetime
import errno
import logging
import os
import sys
from logging import LogRecord, Formatter
from traceback import TracebackException, StackSummary, format_exc
from typing import Dict, Tuple, List, Optional

import json_log_formatter
import pytz

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


LOG_STACK_TRACE = 'log_stack_trace'


def prepare_log_dirs(fn):
    if not os.path.exists(os.path.dirname(fn)):
        try:
            os.makedirs(os.path.dirname(fn))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise


class HumanReadableTraceBackException(TracebackException):
    _RECURSIVE_CUTOFF = 3

    @classmethod
    def format_stack(cls, stack: StackSummary):
        """Format the stack ready for printing.

        This method is a copy of StackSummary.format() with some readability improvements:
        1. "File: " replaced with "   " just for shortening.
        2. Removed line of code output - in out project we usually throw exceptions with quite verbose error
        messages and the line of code usually appears to be the "raise XXX(the same error message here)"
        and it confuses the reader because it usually contains the same text as the error message but with
        some formatting argument names instead of their values.
        """
        result = []
        last_file = None
        last_line = None
        last_name = None
        count = 0
        for frame in stack:
            if (last_file is None or last_file != frame.filename or
                    last_line is None or last_line != frame.lineno or
                    last_name is None or last_name != frame.name):
                if count > cls._RECURSIVE_CUTOFF:
                    count -= cls._RECURSIVE_CUTOFF
                    result.append(
                        f'  [Previous line repeated {count} more '
                        f'time{"s" if count > 1 else ""}]\n'
                    )
                last_file = frame.filename
                last_line = frame.lineno
                last_name = frame.name
                count = 0
            count += 1
            if count > cls._RECURSIVE_CUTOFF:
                continue
            row = []
            row.append('  File "{}", line {}, in {}\n'.format(
                frame.filename, frame.lineno, frame.name))
            result.append(''.join(row))
        if count > cls._RECURSIVE_CUTOFF:
            count -= cls._RECURSIVE_CUTOFF
            result.append(
                f'  [Previous line repeated {count} more '
                f'time{"s" if count > 1 else ""}]\n'
            )
        return result

    def human_readable_format(self, suppress_context_for_message: bool = True) -> str:
        message_lines, stack_lines = self.human_readable_format_msg_stack_lines()
        total = []
        if message_lines:
            total.extend(message_lines)
        if stack_lines:
            total.append('\nStack trace:')
            total.extend(stack_lines)
        return '\n'.join(total)

    def human_readable_format_msg_stack_lines(self,
                                              suppress_context_for_message: bool = True) -> Tuple[List[str], List[str]]:

        error_message = []
        error_stack = []

        ex = self  # type: HumanReadableTraceBackException
        prefix = ''

        while True:
            msg = ''.join(ex.format_exception_only())
            if hasattr(ex, 'detailed_error'):
                msg += f'\nDetailed error: {ex.detailed_error}'
            msg = msg.strip('\n')
            msg_multiline = '\n' in msg

            # Additional empty line before the next error message if it is multiline
            if prefix:
                if msg_multiline:
                    error_message.append(prefix)
                    error_message.append(msg)
                else:
                    error_message.append(prefix + msg)
            else:
                error_message.append(msg)

            if ex.__cause__ is not None:
                ex = ex.__cause__
                prefix = 'caused by: '
            elif not suppress_context_for_message and ex.__context__ is not None and not ex.__suppress_context__:
                ex = ex.__context__
                prefix = 'raised during processing: '
            else:
                break
            # Additional empty line after the prev error message if it was multi-line
            if msg_multiline:
                error_message.append('')

        ex = self  # type: HumanReadableTraceBackException

        while True:
            error_stack.extend([l.strip('\n') for l in self.format_stack(ex.stack)])
            if ex.__cause__ is not None:
                ex = ex.__cause__
            elif ex.__context__ is not None and not ex.__suppress_context__:
                ex = ex.__context__
            else:
                break
        return error_message, error_stack


class ContraxsuiteTextFormatter(Formatter):

    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)

    def formatException(self, ei):
        exc_type, exception, exc_traceback = ei
        return HumanReadableTraceBackException \
            .from_exception(exception) \
            .human_readable_format()


class ContraxsuiteJSONFormatter(json_log_formatter.JSONFormatter):
    def mutate_json_record(self, json_record):
        return json_record

    def json_record(self, message: str, extra: Dict, record: LogRecord):

        stack = None
        if not (extra and LOG_STACK_TRACE in extra) and record.exc_info:
            exc_type, exception, exc_traceback = record.exc_info
            exc_message, exc_stack = HumanReadableTraceBackException \
                .from_exception(exception) \
                .human_readable_format_msg_stack_lines()
            message_lines = []
            if message:
                message_lines.append(message)
            if exc_message:
                message_lines.extend(exc_message)
            message = '\n'.join(message_lines)
            stack = '\n'.join(exc_stack)

        res = {
            '@timestamp': datetime.datetime.utcfromtimestamp(record.created).replace(
                tzinfo=pytz.utc).astimezone().isoformat(),
            'logger': record.name,
            'level': record.levelname,
            'message': message
        }

        if record.levelname in {'ERROR', 'DEBUG', 'WARN'}:
            res.update({
                'process_name': record.processName,
                'process_id': record.process,
                'thread_name': record.threadName,
                'thread_id': record.thread,
                'file_name': record.filename,
                'func_name': record.funcName,
                'line_no': record.lineno,
                'pathname': record.pathname
            })

        if extra:
            for k, v in extra.items():
                if k.startswith('log_'):
                    res[k] = v if v is None or isinstance(v, (str, bool, int)) else str(v)

        if stack and LOG_STACK_TRACE not in res:
            res[LOG_STACK_TRACE] = stack

        # This is used in the filebeat config to determine the index name.
        # Needed for splitting the important Contraxsuite task logs from other logs to keep CX logs longer.
        res['special_log_type'] = 'cx'

        return res


celery_task_logger = logging.getLogger('apps.task.models')


def write_task_log(task_id, message, level='info',
                   main_task_id=None, task_name: str = None, user_id=None, user_login: str = None,
                   exc_info: Exception = None, log_extra: dict = None):
    message = str(message)
    extra = {
        'log_task_id': task_id,
        'log_main_task_id': main_task_id,
        'log_task_name': task_name,
        'log_user_id': user_id,
        'log_user_login': user_login
    }

    if log_extra:
        extra.update(log_extra)

    try:
        getattr(celery_task_logger, level)(message, exc_info=exc_info, extra=extra)

        return True
    except Exception:
        trace = format_exc()
        exc_class, exception, _ = sys.exc_info()
        exception_str = '%s: %s' % (exc_class.__name__, str(exception))

        celery_task_logger.error(
            f'Exception caught while trying to log a message:\n{exception_str}\n{trace}',
            extra=extra)


class CausedException(Exception):
    """
    A base exception class for custom exceptions, allowing record of various exception triggers.

    Example:
        ```
        class CustomException(CausedException):
            def __init__(self, message: str, cause: Optional[Exception] = None):
                self._explanation = f'Some custom message.'
                super().__init__(message, cause)

        try:
            # do something
        except Exception as exception:
            raise CustomException('message', exception) from exception
        ```
    """
    def __init__(self, message: str, cause: Optional[Exception] = None):
        self._explanation: str
        self.__cause__: Exception = cause
        super().__init__(
            f'{self._explanation}\n'
            f'Cause: {self.__cause__.__class__.__name__}\n'
            f'Reason: {self.__cause__}\n'
            f'{message}\n'
        )
