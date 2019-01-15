import datetime
import errno
import os
import pytz

import json_log_formatter


def prepare_log_dirs(fn):
    if not os.path.exists(os.path.dirname(fn)):
        try:
            os.makedirs(os.path.dirname(fn))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise


class ContraxsuiteJSONFormatter(json_log_formatter.JSONFormatter):
    def mutate_json_record(self, json_record):
        return json_record

    def json_record(self, message, extra, record):
        res = {
            '@timestamp': datetime.datetime.utcfromtimestamp(record.created).replace(
                tzinfo=pytz.utc).astimezone().isoformat(),
            'message': message,
            'level': record.levelname,
            'level_no': record.levelno,
            'process_name': record.processName,
            'process_id': record.process,
            'thread_name': record.threadName,
            'thread_id': record.thread,
            'file_name': record.filename,
            'func_name': record.funcName,
            'line_no': record.lineno,
            'pathname': record.pathname
        }

        if extra:
            for k, v in extra.items():
                if k.startswith('log_'):
                    res[k] = v if v is None \
                                  or isinstance(v, str) \
                                  or isinstance(v, bool) \
                                  or isinstance(v, int) else str(v)
        return res
