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

# Standard imports
import pickle
import time

# Third-party imports
from typing import List, Any

import redis

# Django imports
from django.conf import settings
from django.utils.timezone import now

from apps.common.utils import fast_uuid

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


r = redis.Redis.from_url(settings.CELERY_CACHE_REDIS_URL)


def unpickle(value):
    """
    Safely unpickle value
    """
    try:
        return pickle.loads(value)
    except pickle.UnpicklingError:
        return value


def lock(func):
    """
    A decorator to lock redis key for transactions
    """
    def wrapper(key, *args, **kwargs):
        with r.lock('lock_' + key):
            res = func(key, *args, **kwargs)
        return res
    return wrapper


def lpush(key, value, pickle_value=True):
    """
    Append pickled value to redis list
    """
    if pickle_value:
        value = pickle.dumps(value)
    return r.rpush(key, value)


def lrange(key, unpickle_value=True, start=0, end=-1, delete=False):
    """
    Extract unpickled values from redis list
    """
    res = r.lrange(key, start, end)
    if unpickle_value:
        res = [unpickle(i) for i in res]
    if delete:
        r.delete(key)
    return res


@lock
def lpush_or_pop(key, value, limit):
    """
    Push pickled values to redis list until some limit, then return unpickled list
    """
    existing_count = r.llen(key)
    if existing_count >= limit - 1:
        res = lrange(key, delete=True)
        res.append(value)
        resume = True
    else:
        res = lpush(key, value)
        resume = False
    return res, resume


def push(key, value, pickle_value=True):
    """
    Push pickled key value
    """
    if pickle_value:
        value = pickle.dumps(value)
    return r.set(key, value)


def pop(key, unpickle_value=True):
    """
    Get unpickled value to redis store
    """
    value = r.get(key)
    if value is None:
        return None
    if unpickle_value:
        value = unpickle(value)
    return value


def popd(key, unpickle_value=True):
    """
    Get unpickled key value and delete it
    """
    value = pop(key, unpickle_value=unpickle_value)
    r.delete(key)
    return value


def exists(key):
    """
    Check a key exists
    """
    return bool(r.exists(key))


def list_keys(pattern='*', as_list=True, sort=True):
    """
    List keys by pattern
    """
    res = r.scan_iter(pattern)
    if as_list:
        res = list(res)
        if sort:
            res = sorted(res)
    return res


@lock
def push_or_pop(key, value,
                batch_size=None, batch_time=None):
    """
    Push pickled values to redis store until some limit,
    use uid suffix to make keys unique,
    then return unpickled list using key mask
    """
    existing_keys = r.keys('{}__*'.format(key))
    batch_time_key = '{}_time'.format(key)
    time_cached_sec = r.get(batch_time_key)
    time_now_sec = time.mktime(now().timetuple())

    if (batch_size is not None and len(existing_keys) >= batch_size - 1) or \
            (batch_time is not None and time_cached_sec is not None
             and time_now_sec - float(time_cached_sec) >= batch_time):
        res = [popd(k) for k in existing_keys]
        res.append(value)
        r.delete(batch_time_key)
        resume = True
    else:
        key = '{}__{}'.format(key, fast_uuid())
        res = push(key, value)
        r.getset(batch_time_key, time.mktime(now().timetuple()))
        resume = False
    return res, resume


#@lock
def pop_exceeding(key,
                  unpickle_value=True,
                  batch_size=None,
                  batch_time=None) -> List[Any]:
    """
    Push pickled values to redis store until some limit,
    use uid suffix to make keys unique,
    then return unpickled list using key mask
    """
    existing_keys = r.keys('{}__*'.format(key))
    batch_time_key = '{}_time'.format(key)
    time_cached_sec = r.get(batch_time_key)
    time_now_sec = time.mktime(now().timetuple())

    batch_sz_limit = batch_size is not None and len(existing_keys) >= batch_size - 1
    batch_tm_limit = batch_time is not None and time_cached_sec is not None \
        and time_now_sec - float(time_cached_sec) >= batch_time

    if batch_sz_limit or batch_tm_limit:
        res = [pop(k) for k in existing_keys]
        r.delete(batch_time_key)
        if unpickle_value:
            res = [unpickle(value) for value in res]
        return res
    return []
