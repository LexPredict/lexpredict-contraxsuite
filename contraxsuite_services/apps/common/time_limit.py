import signal
from contextlib import contextmanager
from typing import Callable, Optional


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