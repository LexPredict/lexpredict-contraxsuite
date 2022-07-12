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


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from time import sleep
from typing import Any

import regex as re
from django.db import connection, OperationalError

from apps.common.logger import CsLogger

logger = CsLogger.get_django_db_backends_logger()


class OperationalErrorExplorer:
    """
    The class digs into error detail finding the queries that produced
    the error.
    """
    REG_PROC_ID = re.compile(r'(?<=process\s)\d+', re.IGNORECASE)

    @classmethod
    def fullname(cls, o):
        module = o.__class__.__module__
        if module is None or module == str.__class__.__module__:
            return o.__class__.__name__
        return module + '.' + o.__class__.__name__

    @classmethod
    def log_operational_error(cls, exception: Any):
        '''
        deadlock detected
        DETAIL:  Process 26659 waits for ShareLock on transaction 1115066; blocked by process 26661.
        Process 26661 waits for ShareLock on transaction 1115065; blocked by process 26659.
        HINT:  See server log for query details.
        CONTEXT:  while updating tuple (0,3) in relation "vm_task"
        '''
        er_msg = f'Caught exception: {cls.fullname(exception)}\n'
        exc_message = str(exception)
        er_msg += f'{exc_message}\n'
        process_ids = set()
        for m in cls.REG_PROC_ID.finditer(exc_message):
            process_ids.add(int(m.group(0)))
        process_ids = list(process_ids)
        process_ids.sort()
        for pid in process_ids:
            msg = f'Process #{pid} query {"*"*40}:'
            er_msg += f'{msg}\n'
            er_msg += cls.find_process_query(pid).strip()
            er_msg += f'\n{"*"*len(msg)}\n'
        cls.log_message(er_msg)

    @classmethod
    def find_process_query(cls, pid: int) -> str:
        tries_left = 3
        last_error = None
        for _ in range(tries_left):
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f'''SELECT query FROM pg_stat_activity where pid = {pid};''')
                    result = cursor.fetchone()
                    if result:
                        return result[0]
                    return "process wasn't found"
            except Exception as e:
                last_error = e
                connection.close()
        return f'{tries_left} attempts to read process queries failed:\n{last_error}'

    @classmethod
    def log_message(cls, msg: str = ''):
        if not msg:
            return
        logger.error(msg)
        print(msg)


def retry_for_operational_error(
        function=None,
        retries_count: int = 2,
        cooldown_interval: float = 1.0):
    """
    Allows N retries for specific error - django.db.OperationalError
    and writes detailed log
    """
    def _dec(run_func):
        def _caller(*args, **kwargs):
            ret_value = None
            for try_num in range(1, retries_count + 1):
                try:
                    ret_value = run_func(*args, **kwargs)
                    break
                except Exception as e:
                    known_error = False
                    if isinstance(e, OperationalError) or type(e).__name__ == 'OperationalError':
                        known_error = True
                    if known_error:
                        msg = f'{run_func.__name__}: {try_num} ' + \
                              f'attempt of {retries_count} failed ({type(e).__name__})'
                        logger.error(msg)
                        print(msg)
                        OperationalErrorExplorer.log_operational_error(e)
                        if try_num < retries_count:
                            sleep(cooldown_interval)
                            continue
                    raise
            return ret_value
        return _caller
    return _dec(function) if function is not None else _dec
