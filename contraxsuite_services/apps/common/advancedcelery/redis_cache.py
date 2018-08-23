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
import pickle
from typing import Set

import redis

import settings

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.3/LICENSE"
__version__ = "1.1.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class Cache:
    """
    Manages transferring large objects between Python processes and their caching in process local memory.
    Represents two-level cache:
        - process-local in-memory key storage
        - redis key storage

    Use Case:
        Parent Celery task prepared some data which is required for big number of its sub-tasks.
        This data is the same for all sub-tasks and have big size - so transferring it as a Celery
        task argument would be slow and non-effective.

    Solution:
        1. Each Celery process (tasks.py) keeps a global instance of TransferManager.
        2. Parent tasks prepares the data to transfer to subtasks and uses
        TransferManager.put(key, value) to send it to the cache.
        3. Parent tasks starts a celery chord of sub-tasks list as the header providing cache key
        to them. Body of the chord should be a task which will do TransferManager.cleanup(key).
        4. Sub-tasks started by chord use TransferManager.get(key) to get the big data.

    """

    def __init__(self):
        self._local_cache = {}
        self._redis = redis.Redis.from_url(url=settings.CELERY_CACHE_REDIS_URL)

    @staticmethod
    def _full_key(key: str):
        return '{0}_{1}'.format(settings.CELERY_CACHE_REDIS_KEY_PREFIX, key)

    def _load_value_from_storage(self, full_key: str):
        bb = self._redis.get(full_key)
        # if not bb:
        #     print('Missing in redis: {0}'.format(full_key))
        return pickle.loads(bb) if bb else None

    def _put_value_to_storage(self, full_key: str, value):
        # print('Putting to redis: {0}'.format(full_key))
        bb = pickle.dumps(value) if value else None
        self._redis.set(full_key, bb)

    def get(self, key):
        """
        Get the value by key using two-level caching: first checking the local cache and next - Redis.
        :param key:
        :return:
        """
        full_key = Cache._full_key(key)
        if full_key in self._local_cache:
            # print('using local cache')
            return self._local_cache[full_key]
        else:
            # print('loading from redis')
            value = self._load_value_from_storage(full_key)
            self._local_cache[full_key] = value
            return value

    def put(self, key, value):
        """
        Put the value into Redis under the specified key.
        :param key:
        :param value:
        :param active_keys:
        :return:
        """
        self._put_value_to_storage(self._full_key(key), value)
        return key

    def cleanup(self, key):
        """
        Delete value having this key from local cache and from redis.
        :param key:
        :return:
        """
        full_key = Cache._full_key(key)
        if full_key in self._local_cache.keys():
            del self._local_cache[full_key]
        try:
            self._redis.delete([full_key])
        except KeyError:
            pass
