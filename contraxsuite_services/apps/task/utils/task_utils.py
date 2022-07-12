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

import datetime
import inspect
import json
import os
import sys
import tempfile
from contextlib import contextmanager
from typing import Dict, Any, Generator

from django.core.files.uploadedfile import UploadedFile
from django.core.serializers.python import Serializer
from django.db import close_old_connections, connections, models
from django.db.models.query import QuerySet

from apps.common.db_cache.db_cache import DbCache

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from apps.common.file_storage import get_file_storage
from apps.common.models import ExportFile


def is_celery_worker():
    for arg in sys.argv:
        if arg == 'worker':
            return True
    return False


class ArchiveOpenError(Exception):
    BASE_MESSAGE = 'file is injured or cannot be opened.'

    def __init__(self,
                 file_type: str,
                 message: str = ""):
        self.message = message or f'{file_type.lower().title()} {self.BASE_MESSAGE}'
        super().__init__(self.message)


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
    # all data will go to file storage
    try:
        json.dumps(value)
        return value
    except TypeError:
        if isinstance(value, models.Model):
            return SimpleObjectSerializer().serialize([value]).pop()
        if isinstance(value, QuerySet):
            try:
                return SimpleObjectSerializer().serialize(value)
            except AttributeError:
                # the above call may fail if the queryset (value) returns simple types
                values = list(value)
                return json.dumps(values)
        if isinstance(value, (dict, list, tuple, set)):
            return pre_serialize(task_id, key, value)
        if isinstance(value, UploadedFile):
            uploaded_file = value  # type: UploadedFile
            file_ref = ExportFile()
            file_ref.created_time = datetime.datetime.utcnow()
            file_ref.expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            file_ref.comment = f'Import documents from "{len(uploaded_file.name)}" file'
            time_part = str(datetime.datetime.utcnow()).replace('.', '_').replace(':', '_').replace(' ', '_')
            file_name = f'doc_export_{os.path.splitext(uploaded_file.name)[0]}_{time_part}.zip'

            storage = get_file_storage()
            docs_subfolder = storage.sub_path_join(storage.export_path, 'documents')
            try:
                storage.mkdir(docs_subfolder)
            except:
                pass
            file_ref.file_path = storage.sub_path_join(docs_subfolder, file_name)
            storage.write_file(file_ref.file_path, uploaded_file, uploaded_file.size)
            file_ref.file_created = True
            file_ref.stored_time = datetime.datetime.utcnow()
            file_ref.save()
            return {'file_ref_id': file_ref.pk}

        return str(value)


@contextmanager
def download_task_attached_file(document_import_file: Dict[str, Any]) -> Generator[str, None, None]:
    if 'cache_key' in document_import_file:
        # download from DB cache
        zip_bytes = DbCache.get(document_import_file['cache_key'])
        ext = os.path.splitext(document_import_file['file_name'])[1][1:].lower()
        _fd, fn = tempfile.mkstemp(suffix=ext)
        try:
            with open(fn, 'wb') as fw:
                fw.write(zip_bytes)
                yield fn  # TODO: fix yield ...
        finally:
            DbCache.clean_cache(document_import_file['cache_key'])
    else:
        # download from file storage cache
        file_ref_id = document_import_file['file_ref_id']
        file_ref = ExportFile.objects.get(pk=file_ref_id)  # type: ExportFile
        storage = get_file_storage()
        with storage.get_as_local_fn(file_ref.file_path) as f_path:
            yield f_path[0]


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
    if DISK_USAGE.val() > DISK_USAGE_BLOCK_TASKS.val() and FREE_DISK_SPACE.val() < MIN_FREE_DISK_BLOCK_TASKS.val():

        base_error_message = 'Current Disk Usage {}% is greater than limit {}% AND ' \
                             'current Free Disk space {} Gb is less than limit {} Gb.'.format(
                                 DISK_USAGE.val(), DISK_USAGE_BLOCK_TASKS.val(),
                                 FREE_DISK_SPACE.val(), MIN_FREE_DISK_BLOCK_TASKS.val())
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


def get_bounding_rectangle_coordinates(coordinates):
    if isinstance(coordinates, dict):
        return [coordinates['left'], coordinates['top'], coordinates['width'],
                coordinates['height']]
    return [coordinates.left, coordinates.top, coordinates.width, coordinates.height]
