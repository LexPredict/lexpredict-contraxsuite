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

import subprocess
import sys
from io import StringIO
from threading import Thread
from typing import List, Callable, TextIO, Optional

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.3.0/LICENSE"
__version__ = "1.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


READ_LEN = 100


class ProcessKilledByTimeout(Exception):
    pass


class ProcessReturnedErrorCode(Exception):
    pass


def io_pipe_lines(src: TextIO, dst: Callable[[str], None]):
    for buf in iter(src.readline, ''):
        dst(buf)


def exec(cmd: List[str],
         stdout: Callable[[str], None] = None,
         stderr: Callable[[str], None] = None,
         encoding: str = sys.getdefaultencoding(),
         timeout_sec: int = 60 * 60) -> int:
    with subprocess.Popen(cmd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          universal_newlines=True,
                          encoding=encoding) as ps:
        if stdout:
            Thread(target=io_pipe_lines, args=(ps.stdout, stdout), daemon=True).start()

        if stderr:
            Thread(target=io_pipe_lines, args=(ps.stderr, stderr), daemon=True).start()
        try:
            return ps.wait(timeout=timeout_sec)
        except subprocess.TimeoutExpired:
            ps.kill()
            ps.wait(timeout=5)
            raise ProcessKilledByTimeout()


def read_output(cmd: List[str],
                stderr_callback: Callable[[str], None],
                encoding: str = sys.getdefaultencoding(),
                timeout_sec: int = 60 * 60,
                error_if_returner_not: Optional[int] = 0) -> str:
    stdout = StringIO()
    stderr = StringIO()

    def err(line: str):
        stderr.write(line)
        stderr_callback(line)

    def out(line: str):
        stdout.write(line)

    try:
        error_code = exec(cmd, stdout=out, stderr=err, encoding=encoding, timeout_sec=timeout_sec)
    except ProcessKilledByTimeout:
        raise ProcessKilledByTimeout(f'Process has been killed by timeout.\n'
                                     f'Cmd: {cmd}\n'
                                     f'Timeout (sec): {timeout_sec}\n'
                                     f'Stderr:\n'
                                     f'{stderr.getvalue()}')

    if error_if_returner_not is not None and error_code != error_if_returner_not:
        raise ProcessReturnedErrorCode(f'Process returned wrong error code.\n'
                                       f'Cmd: {cmd}\n'
                                       f'Expected error code: {error_if_returner_not}\n'
                                       f'Actual error code: {error_code}\n'
                                       f'Stderr:\n'
                                       f'{stderr.getvalue()}')
    else:
        return stdout.getvalue()
