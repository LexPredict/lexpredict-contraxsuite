import threading
import time
from datetime import datetime

from apps.common.models import ObjectStorage


class DbCache:
    CACHE_IN_MEMORY_REFRESH_SECONDS = 20

    INSTANCE = None

    lock = threading.RLock()

    def __init__(self) -> None:
        super().__init__()
        self.in_memory_cache = {}
        self.watch_thread = threading.Thread(target=self._check_cache)
        self._stop_watcher = False
        self.watch_thread.start()

    def stop_watching(self):
        self._stop_watcher = True

    def _check_cache(self):
        while self.watch_thread.is_alive() and not self._stop_watcher:
            time.sleep(self.CACHE_IN_MEMORY_REFRESH_SECONDS)
            self.lock.acquire()
            try:
                for key in set(self.in_memory_cache.keys()):
                    last_update_date, value = self.in_memory_cache[key]
                    if (datetime.now() - last_update_date).seconds \
                            > self.CACHE_IN_MEMORY_REFRESH_SECONDS:
                        del self.in_memory_cache[key]

            finally:
                self.lock.release()

    @staticmethod
    def load_from_db(key: str):
        try:
            return ObjectStorage.objects.get(key=key).get_obj()
        except ObjectStorage.DoesNotExist:
            return None

    @staticmethod
    def clean_cache(key_prefix: str):
        try:
            return ObjectStorage.objects.filter(key__startswith=key_prefix).delete()
        except ObjectStorage.DoesNotExist:
            return None

    @staticmethod
    def put_to_db(key: str, value):
        ObjectStorage.update_or_create(key, value)

    def _get(self, key: str):
        self.lock.acquire()
        try:
            record = self.in_memory_cache.get(key)

            if not record or (datetime.now() - record[0]).seconds \
                    > DbCache.CACHE_IN_MEMORY_REFRESH_SECONDS:
                record = (datetime.now(), self.load_from_db(key))
                self.in_memory_cache[key] = record

            return record[1]
        finally:
            self.lock.release()

    @staticmethod
    def get(key: str):
        DbCache.lock.acquire()
        try:
            if DbCache.INSTANCE is None:
                DbCache.INSTANCE = DbCache()
            return DbCache.INSTANCE._get(key)
        finally:
            DbCache.lock.release()
