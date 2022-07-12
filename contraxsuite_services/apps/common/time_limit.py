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

import signal
from contextlib import contextmanager
from typing import Callable, Optional

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TimeoutException(Exception):
    def __init__(self, msg: str = '', timeout_seconds: int = 0):
        super().__init__(msg)
        self.timeout_seconds = timeout_seconds


@contextmanager
def time_limit(seconds, on_timeout: Optional[Callable[[str], None]] = None):
    """
    :param seconds: timeout seconds, integer value:
    :param on_timeout: action being called on timeout, parameter is timeout seconds
    Usage:
    >>>     with time_limit(
    >>>         5, on_timeout=lambda s: print(f'Timeout in Locator - {s} seconds')):
    """
    def sig_handler(signum, frame):
        if on_timeout:
            on_timeout(seconds)
        else:
            raise TimeoutException("Timed out")
    signal.signal(signal.SIGALRM, sig_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
