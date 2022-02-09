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

import threading
import time
from datetime import datetime

from apps.common.models import ObjectStorage

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


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
                    last_update_date, _ = self.in_memory_cache[key]
                    if (datetime.now() - last_update_date).seconds > self.CACHE_IN_MEMORY_REFRESH_SECONDS:
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
