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

import os
import platform
import psutil
import signal
import sys
import threading
from datetime import datetime
from io import StringIO
from traceback import extract_stack

from apps.common.logger import CsLogger
from contraxsuite_logging import HumanReadableTraceBackException
from django.conf import settings

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def print_stack(f=None, limit=None) -> str:
    """Print a stack trace from its invocation point.

    The optional 'f' argument can be used to specify an alternate
    stack frame at which to start. The optional 'limit' and 'file'
    arguments have the same meaning as for print_exception().
    """
    if f is None:
        f = sys._getframe().f_back

    lines = HumanReadableTraceBackException.format_stack(extract_stack(f, limit=limit))
    return ''.join(lines) if lines else '\n'


def print_stack_traces(sig, frame):
    try:
        from apps.common.models import ThreadDumpRecord

        dump = ThreadDumpRecord()
        dump.node = platform.node()
        dump.date = datetime.utcnow()

        py = psutil.Process(os.getpid())
        dump.cpu_usage_system = psutil.cpu_percent()
        dump.cpu_usage = py.cpu_percent()
        dump.memory_usage = py.memory_info()[0]
        dump.memory_usage_system_wide = psutil.virtual_memory().used
        dump.command_line = str(py.cmdline())
        dump.pid = py.pid

        dump_str = StringIO()

        for th in threading.enumerate():
            dump_str.write(str(th) + '\n')

            dump_str.write(print_stack(sys._current_frames()[th.ident]))
            dump_str.write('\n\n')

        dump.dump = dump_str.getvalue()

        dump.save()
    except Exception as e:
        CsLogger.get_django_logger().error('Unable to dump threads', exc_info=e)


def listen():

    if settings.DEBUG_STACK_DUMP_ENABLED and threading.current_thread() is threading.main_thread():
        signal.signal(settings.DEBUG_STACK_DUMP_SIGNAL, print_stack_traces)
