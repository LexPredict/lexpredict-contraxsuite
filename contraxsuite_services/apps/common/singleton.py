from threading import Lock
from typing import Type


class Singleton:
    def __init__(self, clz: Type) -> None:
        super().__init__()
        self.clz = clz
        self.lock = Lock()
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            with self.lock:
                if self.instance is None:
                    self.instance = self.clz(*args, **kwargs)
        return self.instance
