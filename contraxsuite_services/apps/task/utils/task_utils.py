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

import inspect
import json
import sys

from django.core.files.uploadedfile import UploadedFile
from django.core.serializers.python import Serializer
from django.db import close_old_connections, connections, models
from django.db.models.query import QuerySet

from apps.common.db_cache.db_cache import DbCache

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def is_celery_worker():
    for arg in sys.argv:
        if arg == 'worker':
            return True
    return False


class TaskUtils:
    __is_celery_worker = is_celery_worker()
    __connection_initialization_finished = False

    @staticmethod
    def is_celery_worker():
        return TaskUtils.__is_celery_worker

    @staticmethod
    def prepare_task_execution():
        """

        Clearing of old database connections for CONN_MAX_AGE option (database connection settings)

        """
        if not TaskUtils.is_celery_worker():
            return

        try:
            if TaskUtils.__connection_initialization_finished:
                close_old_connections()
            else:
                for conn in connections.all():
                    conn.close()
                    TaskUtils.__connection_initialization_finished = True
        except Exception:
            pass


class SimpleObjectSerializer(Serializer):
    def get_dump_object(self, obj):
        res = super().get_dump_object(obj)
        return {'model': res['model'], 'pk': res['pk']}


def normalize(task_id, key, value):
    try:
        json.dumps(value)
        return value
    except TypeError:
        if isinstance(value, models.Model):
            return SimpleObjectSerializer().serialize([value]).pop()
        elif isinstance(value, QuerySet):
            return SimpleObjectSerializer().serialize(value)
        elif isinstance(value, (dict, list, tuple, set)):
            return pre_serialize(task_id, key, value)
        elif isinstance(value, UploadedFile):
            uploaded_file = value  # type: UploadedFile
            cache_key = str(task_id) + '__' + str(key) if key else str(task_id)
            DbCache.put_to_db(cache_key, uploaded_file.read())
            return {
                'file_name': uploaded_file.name,
                'cache_key': cache_key
            }
        return str(value)


def pre_serialize(task_id, key, obj):
    try:
        json.dumps(obj)
        return obj
    except TypeError:
        if isinstance(obj, dict):
            for sub_key, value in obj.items():
                sub_key_full = str(key) + '__' + str(sub_key) if key else str(sub_key)
                obj[sub_key] = normalize(task_id, sub_key_full, value)
        elif isinstance(obj, (tuple, list, set)):

            obj = [normalize(task_id, str(key) + '__' + str(index) if key else str(index), value)
                   for index, value in enumerate(obj)]
        else:
            normalize(task_id, key, obj)
        return obj


def check_blocks(raise_error=True, error_message=None):
    """
    If any blocks exist raise error or return error message
    Otherwise return False
    :param raise_error: bool - raise error if needed
    :param error_message: str
    :return:
    """
    from apps.task.app_vars import DISK_USAGE_BLOCK_TASKS, MIN_FREE_DISK_BLOCK_TASKS, DISK_USAGE, FREE_DISK_SPACE

    # blocks exist
    if DISK_USAGE.val > DISK_USAGE_BLOCK_TASKS.val and FREE_DISK_SPACE.val < MIN_FREE_DISK_BLOCK_TASKS.val:

        base_error_message = 'Current Disk Usage {}% is greater than limit {}% AND ' \
                             'current Free Disk space {} Gb is less than limit {} Gb.'.format(
                                 DISK_USAGE.val, DISK_USAGE_BLOCK_TASKS.val,
                                 FREE_DISK_SPACE.val, MIN_FREE_DISK_BLOCK_TASKS.val)
        if error_message:
            base_error_message += ' {}'.format(error_message)
        if raise_error:
            error = RuntimeError(base_error_message)
            error.as_api_exception = True
            error.status_code = 403
            raise error
        return base_error_message

    # no blocks
    return False


def check_blocks_decorator(raise_error=True, error_message=None):
    def outer(func):
        def inner(*args, **kwargs):
            check_blocks(raise_error=raise_error, error_message=error_message)
            if inspect.ismethod(func):
                if len(args) <= 1:
                    res = func(**kwargs)
                else:
                    res = func(args[1:], **kwargs)
            else:
                res = func(*args, **kwargs)
            return res
        return inner
    return outer
