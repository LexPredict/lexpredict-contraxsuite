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

import json
import sys

from django.core.files.uploadedfile import UploadedFile
from django.core.serializers.python import Serializer
from django.db import close_old_connections, connections, models
from django.db.models.query import QuerySet

from apps.common.advancedcelery.db_cache import DbCache

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.2/LICENSE"
__version__ = "1.2.2"
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
