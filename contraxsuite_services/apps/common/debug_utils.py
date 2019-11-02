import logging
import signal
import sys
from traceback import extract_stack
from contraxsuite_logging import HumanReadableTraceBackException
from django.conf import settings


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
        import faulthandler
        import platform
        from datetime import datetime
        import os
        from apps.common.models import ThreadDumpRecord
        import psutil
        from io import StringIO

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

        import threading
        import traceback
        import sys
        for th in threading.enumerate():
            dump_str.write(str(th) + '\n')

            dump_str.write(print_stack(sys._current_frames()[th.ident]))
            dump_str.write('\n\n')

        dump.dump = dump_str.getvalue()

        dump.save()
    except Exception as e:
        logging.getLogger('django').error('Unable to dump threads', exc_info=e)


def listen():
    if settings.DEBUG_STACK_DUMP_ENABLED:
        signal.signal(settings.DEBUG_STACK_DUMP_SIGNAL, print_stack_traces)
