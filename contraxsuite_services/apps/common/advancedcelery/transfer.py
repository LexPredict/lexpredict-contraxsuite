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
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.5/LICENSE"
__version__ = "1.0.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TransferManager:
    """
    Manages transferring large objects between Python processes and their caching in process local memory.
    Objects are transferred via an intermediate key-value storage - Redis.
    Objects are cached in process memory on the first request to avoid excessive serialization/deserialization to/from
    Redis.
    Removing of non-used values from both Redis and local cache is made upon each next request based on the list
    of known active keys provided by the users of put(..) method of this class.
    For the case of Contraxsuite Locate task - the list of active keys is always consisting of a single element because
    only one copy of the Locate task is allowed to run at a time.
    For other cases the list of active keys should be managed - keys should be treated as inactive after
    all child tasks requiring data under these keys are finished.

    Work scheme for Contraxsuite Locate task:
    1. Parent task prepares geo/court/terms configs and puts them into a separate object which is too large
    to transfer as a usual task argument.
    2. Parent task defines the key for this object - for Locate task it will be always the same as only one Locate
    task can be started at a time.
    3. Parent task stores the prepared large object object using put(key, value, known_active_keys) method.

        On this step LargeArgumentsManager:
        1. Cleans Redis from previously stored objects - having keys not in the provided known_active_keys list.
        2. Puts the new object into Redis under the specified key.

    4. Parent task starts a set of child tasks providing the cache key to them.
    5. Child tasks retrieve the large object via get(key) method.
        This method:
        1. Checks local in-memory cache of the worker subprocess for value possibly already retrieved from Redis
        for this key.
        2. Cleans local in-memory cache from inactive keys which do not exist in Redis.
        3. If there is no value for this key in the local cache - then retrieves it from Redis.

    Alternatives to two-level caching would be:
    1. Redis-only - simpler but a bit more time spent on deserializing objects from Redis on every run (~~ x2 times).
    2. In-memory only, rebuilding data from DB on the first time - simpler, much slower on first runs for each worker,
        but allows avoiding Redis limit on max 512MB for stored values.

    Keys and active_known_keys concepts are introduced to support possible run of multiple instances of the same
    task with different arguments at the same time. In this case the parent task should generate key as
    task name + random uuid before running each set of child tasks.
    Alternative would be a normal cache under a simple key but it would require the invalidation scheme which is
    hard to introduce in Celery.
    Usually broadcast "invalidate" tasks are considered but it looks like Celery has no way to broadcast them to
    each sub-process started on the worker node. Only the main process takes the broadcasted task and puts it to
    one of its subprocesses while other would have stale cache.
    To avoid it we need an approach based on different tokens/keys assigned to each version of data.
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

    def _get_active_keys_from_storage(self):
        """
        Get all keys in Redis having settings.CELERY_CACHE_REDIS_KEY_PREFIX as the prefix.
        Redis is cleaned from inactive in put() method while this one can be used on the receiving side
        to clean its local in-memory cache.
        :return:
        """
        return [bb.decode('utf-8') for bb in self._redis.keys(TransferManager._full_key('*'))]

    def _del_non_active_from_redis(self, known_active_keys):
        """
        Remove keys from Redis which are not in the specified list/set.
        settings.CELERY_CACHE_REDIS_KEY_PREFIX is added to each element in the provided list.
        :param known_active_keys:
        :return:
        """
        redis_keys = self._get_active_keys_from_storage()
        inactive_keys = set(redis_keys) - set([self._full_key(key) for key in known_active_keys])
        if inactive_keys:
            # print('Removing from redis: {0}'.format(inactive_keys))
            self._redis.delete(*inactive_keys)

    def get(self, key):
        """
        Get the value by key using two-level caching: first checking the local cache and next - Redis.
        Local cache is cleaned from non-active keys which are not in Redis on each run of this method.
        :param key:
        :return:
        """
        # leaving local cache results only for task runs which are present in redis
        full_key = TransferManager._full_key(key)
        active_keys = self._get_active_keys_from_storage()
        del_keys = set(self._local_cache.keys()) - set(active_keys)
        for del_key in del_keys:
            del self._local_cache[del_key]

        if full_key in self._local_cache:
            # print('using local cache')
            return self._local_cache[full_key]
        else:
            # print('loading from redis')
            value = self._load_value_from_storage(full_key)
            self._local_cache[full_key] = value
            return value

    def put(self, key, value, active_keys: Set = None):
        """
        Clean Redis from inactive keys - which are not in the provided set and put the value into Redis
        under the specified key.
        :param key:
        :param value:
        :param active_keys:
        :return:
        """
        active_keys = active_keys or []
        self._del_non_active_from_redis([key, *active_keys])
        self._put_value_to_storage(self._full_key(key), value)
        return key
