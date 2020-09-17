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

import asyncio
import os
import signal
import subprocess
import sys
import time
import psutil
from io import StringIO
from threading import Thread
from typing import List, Callable, TextIO, Optional, Any

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


READ_LEN = 100


class ProcessKilledByTimeout(Exception):
    pass


class ProcessReturnedErrorCode(Exception):
    pass


def io_pipe_lines(src: TextIO, dst: Callable[[str], None]):
    try:
        for buf in iter(src.readline, ''):
            dst(buf)
    except ValueError:
        pass


def exec(cmd: List[str],
         stdout: Callable[[str], None] = None,
         stderr: Callable[[str], None] = None,
         encoding: str = sys.getdefaultencoding(),
         timeout_sec: int = 60 * 60,
         task: Any = None) -> int:
    with subprocess.Popen(cmd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          universal_newlines=True,
                          encoding=encoding,
                          preexec_fn=os.setpgrp) as ps:
        if task:
            task.store_spawned_process(ps.pid)
        if stdout:
            Thread(target=io_pipe_lines, args=(ps.stdout, stdout), daemon=True).start()

        if stderr:
            Thread(target=io_pipe_lines, args=(ps.stderr, stderr), daemon=True).start()

        try:
            return ps.wait(timeout=timeout_sec)
        except subprocess.TimeoutExpired:
            # ps.kill()
            os.killpg(os.getpgid(ps.pid), signal.SIGTERM)
            ps.wait(timeout=5)
            raise ProcessKilledByTimeout()


def start_process(cmd: List[str],
                  stdout: Callable[[str], None] = None,
                  stderr: Callable[[str], None] = None,
                  encoding: str = sys.getdefaultencoding(),
                  cwd: str = None) -> subprocess.Popen:
    ps = subprocess.Popen(cmd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          universal_newlines=True,
                          encoding=encoding,
                          cwd=cwd)
    if stdout:
        Thread(target=io_pipe_lines, args=(ps.stdout, stdout), daemon=True).start()

    if stderr:
        Thread(target=io_pipe_lines, args=(ps.stderr, stderr), daemon=True).start()

    return ps


def read_output(cmd: List[str],
                stderr_callback: Callable[[str], None],
                encoding: str = sys.getdefaultencoding(),
                timeout_sec: int = 60 * 60,
                error_if_returner_not: Optional[int] = 0,
                task: Any = None) -> str:
    stdout = StringIO()
    stderr = StringIO()

    def err(line: str):
        stderr.write(line)
        stderr_callback(line)

    def out(line: str):
        stdout.write(line)

    try:
        error_code = exec(cmd, stdout=out, stderr=err,
                          encoding=encoding, timeout_sec=timeout_sec,
                          task=task)
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


async def async_read_pipe(pipe, dst: Callable[[str], None]):
    while True:
        buf = await pipe.read()
        if not buf:
            break
        dst(buf)


async def async_exec(program: str, args: List[str], stdout: Callable[[str], None] = None,
                     stderr: Callable[[str], None] = None):
    proc = await asyncio.create_subprocess_exec(program, *args,
                                                stdin=asyncio.subprocess.PIPE,
                                                stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.PIPE)

    io_tasks = list()
    if stderr:
        io_tasks.append(async_read_pipe(proc.stderr, stderr))
    if stdout:
        io_tasks.append(async_read_pipe(proc.stdout, stdout))

    if not io_tasks:
        return await proc.communicate()
    else:
        await asyncio.gather(*io_tasks)


async def async_wait_for_file(file_path, timeout_interval_sec: float = 30, check_interval_sec: float = 0.3):
    start = time.time()
    while True:
        if time.time() - start > timeout_interval_sec:
            raise TimeoutError(f'Timeout waiting for file creation: {file_path}')
        if not os.path.exists(file_path):
            await asyncio.sleep(check_interval_sec)
        else:
            break


def terminate_processes_by_ids(pids: List[int],
                               log_func: Optional[Callable[[str], None]] = None):
    count_terminated, count_skipped, count_failed = 0, 0, 0
    # terminate spawned processes
    for pid in pids:
        try:
            p = psutil.Process(pid)
            if p:
                p.terminate()
                count_terminated += 1
            else:
                count_skipped += 1
        except psutil.NoSuchProcess:
            count_skipped += 1
        except:
            count_failed += 1
    if log_func:
        log_func(f'terminate_processes(): {count_terminated} spawned processed are terminated, '
                 f'{count_skipped} skipped, {count_failed} failed to terminate')
