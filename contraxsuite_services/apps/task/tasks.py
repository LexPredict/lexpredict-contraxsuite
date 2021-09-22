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
import codecs
import datetime
import hashlib
import importlib
import io
import json
import mimetypes
import os
import shutil
import string
import sys
import tempfile
import threading
import time
import traceback
import zipfile
from inspect import isclass
from typing import List, Dict, Tuple, Any, Callable, Optional, Union, Generator, Iterable
from uuid import getnode as get_mac

# Third-party imports
import magic
import pandas as pd
from celery import shared_task, signature
from celery.exceptions import SoftTimeLimitExceeded, Retry
from celery.result import AsyncResult
from celery.states import FAILURE, UNREADY_STATES, SUCCESS
from celery.utils.log import get_task_logger
from celery.utils.time import get_exponential_backoff_interval
# Django imports
import croniter
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import transaction, connection, IntegrityError
from django.db.models import QuerySet
from django.db.utils import DatabaseError
from django.utils.timezone import now

from lexnlp.extract.common.ocr_rating.lang_vector_distribution_builder import LangVectorDistributionBuilder
from lexnlp.extract.en.contracts.detector import is_contract
from lexnlp.nlp.en.segments.paragraphs import get_paragraphs
from psycopg2 import InterfaceError, OperationalError
from text_extraction_system_api.client import TextExtractionSystemWebClient
from text_extraction_system_api.dto import PlainTextStructure, STATUS_DONE, OutputFormat, TableParser

# Project imports
import task_names
from apps.analyze.ml.contract_type_classifier import ContractTypeClassifier
from apps.celery import app
from apps.common.archive_file import ArchiveFile
from apps.common import redis
from apps.common.errors import find_cause_of_type
from apps.common.file_storage import get_file_storage
from apps.common.log_utils import ProcessLogger
from apps.common.models import Action
from apps.common.processes import terminate_processes_by_ids
from apps.common.utils import fast_uuid
from apps.deployment.app_data import load_geo_entities, load_terms, load_courts
from apps.document import signals
from apps.document.constants import DOCUMENT_TYPE_PK_GENERIC_DOCUMENT, \
    DOC_METADATA_DOCUMENT_CLASS_PROB, DOCUMENT_FIELD_CODE_CLASS, DOC_METADATA_DOCUMENT_CONTRACT_CLASS_VECTOR
from apps.document.document_class import DocumentClass
from apps.document.field_detection.field_detection import detect_and_cache_field_values_for_document
from apps.document.models import (
    Document, DocumentText, DocumentPDFRepresentation, DocumentMetadata, DocumentProperty, DocumentType,
    TextUnit, TextUnitTag, DocumentTable, TextUnitText, DocumentPage)
from apps.document.repository.document_field_repository import DocumentFieldRepository
from apps.extract import dict_data_cache
from apps.extract import models as extract_models
from apps.extract.locators import LocatorsCollection, LocationResults
from apps.extract.locators import request_mat_views_refresh
from apps.extract.models import Court, GeoAlias, GeoEntity, GeoRelation
from apps.project.models import Project, UploadSession
from apps.task.celery_backend.task_utils import revoke_task
from apps.task.models import Task, TaskConfig, ReindexRoutine
from apps.task.ocr_rating.ocr_rating_calculator import TextOCRRatingCalculator, CUSTOM_LANG_STORAGE_FOLDER
from apps.task.signals import task_deleted
from apps.task.task_monitor import TaskMonitor
from apps.task.task_visibility import TaskVisibility
from apps.task.utils.task_utils import TaskUtils, pre_serialize, check_blocks, check_blocks_decorator, \
    download_task_attached_file
from apps.users.models import User
from apps.websocket import channel_message_types as message_types
from apps.websocket.channel_message import ChannelMessage
from apps.websocket.websockets import Websockets
from contraxsuite_logging import write_task_log

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


file_storage = get_file_storage()

# Logger setup
this_module = sys.modules[__name__]
logger = get_task_logger(__name__)

# TODO: Configuration-based and language-based punctuation.
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

python_magic = magic.Magic(mime=True)


def _get_or_create_task_config(celery_task) -> TaskConfig:
    return TaskConfig.objects.get_or_create(defaults={
        'name': celery_task.name,
        'soft_time_limit': celery_task.soft_time_limit
    }, name=celery_task.name)[0]


def get_task_priority(callable_or_class) -> int:
    priority = app.conf.task_default_priority
    if getattr(callable_or_class, 'priority', None) is not None:
        priority = callable_or_class.priority
    return priority


def get_queue_by_task_priority(priority: int) -> str:
    priority = priority or 0
    return settings.CELERY_QUEUE_HIGH_PRIO if priority > 7 else settings.CELERY_QUEUE_DEFAULT


class ExtendedTask(app.Task):
    """
    Extended Task class, allows to log exceptions
    Can be applied to concrete function like this:
      @shared_task(base=ExtendedTask)
      def concrete_task(*args, **kwargs):
          ....


    WARNING:    Beware storing anything in the self fields of instances of this class.
                Looks like they are reused and it is safer to store anything in self.request
    """

    db_connection_ping = False
    weight = 100

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cached_data = None
        self._log_kwargs = None  # type: Optional[Dict[str, Any]]

    def run(self, *args, **kwargs):
        run_count = Task.objects.increase_run_count(self.request.id)
        if hasattr(self, 'max_retries') and self.max_retries is not None and run_count > self.max_retries:
            raise RuntimeError(f'Exceeded maximum number of retries ({self.max_retries})')
        self.log_info(f'Start task "{self.task_name}", id={self.main_task_id}, '
                      f'run_count={run_count}\nKwargs: {str(kwargs)}')
        if '_log_extra' in kwargs:
            self._log_kwargs = kwargs['_log_extra']
        try:
            ret = self.process(**kwargs)
        finally:
            self.log_info(f'End of main task "{self.task_name}", id={self.main_task_id}. '
                          'Sub-tasks may be still running.')
        return ret or self.main_task_id

    @property
    def task(self) -> Task:
        self.init_cache()
        return self._cached_data['task']

    @property
    def task_name(self) -> str:
        return self.name

    @property
    def log_extra(self) -> Dict:
        return self.task.log_extra or self._log_kwargs

    @log_extra.setter
    def log_extra(self, v: Dict):
        this_task = self.task  # type: Task
        this_task.log_extra = v
        this_task.save(update_fields=['log_extra'])

    def write_log(self, message, level='info', exc_info: Exception = None, **kwargs):
        if self._log_kwargs:
            kwargs.update(self._log_kwargs)
        try:
            self.task.write_log(message, level, exc_info=exc_info, **kwargs)
        except:
            write_task_log(self.request.id,
                           'Task.' + message, level,
                           task_name=self.request.task,
                           log_extra=kwargs)

    def log_info(self, message, **kwargs):
        self.write_log(message, level='info', **kwargs)

    def log_error(self, message, exc_info: Exception = None, **kwargs):
        self.write_log(message, level='error', exc_info=exc_info, **kwargs)

    def log_debug(self, message, **kwargs):
        self.write_log(message, level='debug', **kwargs)

    def log_warn(self, message, exc_info: Exception = None, **kwargs):
        self.write_log(message, level='warn', exc_info=exc_info, **kwargs)

    def init_cache(self):
        if self._cached_data:
            return
        num_tries = 1
        while True:
            try:
                this_task = Task.objects.get(id=self.request.id)
                self._cached_data = {'task': this_task, 'main_task_id': this_task.main_task_id}
                break
            except Task.DoesNotExist:
                if num_tries:
                    num_tries -= 1
                    # wait before the task object is committed to the DB
                    time.sleep(0.5)
                    continue
                raise RuntimeError(f'ExtendedTask: task with id={self.request.id} was not found')

    @property
    def main_task_id(self):
        self.init_cache()
        return self._cached_data.get('main_task_id')

    def set_push_steps(self, value: int):
        this_task = self.task  # type: Task
        this_task.push_steps = value
        this_task.save(update_fields=['push_steps'])

    def push(self):
        this_task = self.task  # type: Task
        this_task.own_progress = this_task.own_progress + 100.0 / this_task.push_steps
        try:
            this_task.save(update_fields=['own_progress'])
        except DatabaseError:
            # that's probably "Save with update_fields did not affect any rows."
            pass

    def _render_task_failed_message(self,
                                    args,
                                    kwargs) -> str:

        return 'Task has been failed:\n' + \
               f'{self.name}\n' + \
               f'Args: {args}\n' + \
               f'Kwargs: {str(kwargs)}\n'

    def run_if_task_or_sub_tasks_failed(self,
                                        func: Callable,
                                        args,
                                        call_stack: str = None,
                                        parent_stack: str = None):
        task_config = _get_or_create_task_config(func)
        priority = get_task_priority(func)

        call_stack = call_stack or get_call_stack_line(-3)
        if parent_stack:
            call_stack = f'{parent_stack}\n{call_stack}'

        task = Task(name=func.name,
                    args=args,
                    main_task_id=self.main_task_id or self.request.id,
                    parent_task_id=self.request.id,
                    source_data=self.task.source_data,
                    title=func.name,
                    run_if_parent_task_failed=True,
                    status=None,  # None statuses are used in apps/task/celery_backend/managers.py
                    own_status=None,  # for checking for unprocessed tasks
                    metadata={
                        'args': args,
                        'options': {
                            'soft_time_limit': task_config.soft_time_limit,
                            'root_id': self.main_task_id
                        }
                    },
                    priority=priority or 0,
                    call_stack=call_stack,
                    restart_count=0,
                    bad_health_check_num=0,
                    weight=self.weight)
        task.save()
        self.task.has_sub_tasks = True

        # Using the filter instead of simply .save(update_fields=...) to avoid
        # Postgres unnecessary writes.
        Task.objects.filter(pk=self.task.pk).exclude(has_sub_tasks=True).update(has_sub_tasks=True)

    def run_after_sub_tasks_finished(self,
                                     tasks_group_title: str,
                                     sub_task_function,
                                     args_list: List[Tuple],
                                     source_data: List[str] = None,
                                     call_stack: str = None,
                                     parent_stack: str = None):
        task_config = _get_or_create_task_config(sub_task_function)
        tasks = []
        priority = get_task_priority(sub_task_function)

        call_stack = call_stack or get_call_stack_line(-3)
        if parent_stack:
            call_stack = f'{parent_stack}\n{call_stack}'

        for index, args in enumerate(args_list):
            tasks.append(Task(
                name=sub_task_function.name,
                args=args,
                main_task_id=self.main_task_id or self.request.id,
                parent_task_id=self.request.id,
                source_data=source_data[index] if source_data is not None else self.task.source_data,
                run_after_sub_tasks_finished=True,
                title=tasks_group_title,
                status=None,  # None statuses are used in apps/task/celery_backend/managers.py
                own_status=None,  # for checking for unprocessed tasks
                metadata={
                    'args': args,
                    'options': {
                        'soft_time_limit': task_config.soft_time_limit,
                        'root_id': self.main_task_id
                    }
                },
                priority=priority,
                call_stack=call_stack,
                failure_reported=False,
                restart_count=0,
                bad_health_check_num=0
            ))

        Task.objects.bulk_create(tasks)

        if tasks and not self.task.has_sub_tasks:
            self.task.has_sub_tasks = True
            self.task.save(update_fields=['has_sub_tasks'])

    def run_sub_tasks(self,
                      sub_tasks_group_title: str,
                      sub_task_function,
                      args_list: List[Tuple],
                      source_data: List[str] = None,
                      countdown: int = None,
                      priority: Optional[int] = None) -> None:
        """
        Asynchronously execute sub_task_method on each tuple of arguments from the provided list.

        :param sub_tasks_group_title:
        :param sub_task_function:
        :param args_list:
        :param source_data:
        :param countdown: Delay in seconds before running the sub-tasks.
        :param priority: int or None - task priority
        :return:
        """

        def _is_json_serializable(obj: Any) -> bool:
            """
            Check if arguments are JSON serializable.
            If they aren't, then throw a descriptive exception to aid debugging.
            Arguments will be JSON-serialized, passed to RabbitMQ, and lastly
                deserialized on another machine. This makes it imperative to
                ensure arguments can be properly distributed to the subtasks.
            """
            try:
                json.dumps(obj)
                return True
            except (TypeError, OverflowError):
                return False

        class ArgumentIsNotJSONSerializable(TypeError):
            def __init__(self, arg):
                message: str = 'Arguments passed to run_sub_tasks ' \
                               'must be JSON-serializable. ' \
                               f'`{arg}` could not be JSON-serialized. ' \
                               'Try passing basic Python types, ' \
                               'like the integer ID of an object.'
                super().__init__(message)

        if not args_list:
            return None
        priority = priority if priority is not None else get_task_priority(sub_task_function)
        sub_tasks = []
        task_config = _get_or_create_task_config(sub_task_function)
        for index, args in enumerate(args_list):

            for arg in args:
                if not _is_json_serializable(arg):
                    raise ArgumentIsNotJSONSerializable(arg)

            sub_task_signature = sub_task_function.subtask(
                args=args,
                source_data=source_data[index] if source_data is not None else self.task.source_data,
                soft_time_limit=task_config.soft_time_limit,
                root_id=self.main_task_id,
                main_task_id=self.main_task_id,
                parent_id=self.request.id,
                title=sub_tasks_group_title,
                priority=priority)
            sub_tasks.append(sub_task_signature)

        queue = sub_task_function.queue \
            if hasattr(sub_task_function, 'queue') \
            else get_queue_by_task_priority(priority)

        self.log_info(
            '{0}: {1} starting {2} sub-tasks...'.format(self.task_name, sub_tasks_group_title, len(sub_tasks)))
        for ss in sub_tasks:
            ss.apply_async(countdown=countdown,
                           priority=priority,
                           queue=queue)
        if sub_tasks and not self.task.has_sub_tasks:
            self.task.has_sub_tasks = True
            self.task.save(update_fields=['has_sub_tasks'])

    def run_sub_tasks_class_based(self,
                                  sub_tasks_group_title: str,
                                  sub_task_class,
                                  kwargs_list: List[Dict],
                                  source_data: List[str] = None,
                                  call_stack: str = None,
                                  parent_stack: str = None):
        """
        Asynchronously execute sub_task_method on each tuple of arguments from the provided list.
        """
        sub_tasks = []
        priority = get_task_priority(sub_task_class)
        task_config = _get_or_create_task_config(sub_task_class)

        call_stack = call_stack or get_call_stack_line(-3)
        if parent_stack:
            call_stack = f'{parent_stack}\n{call_stack}'

        for index, args in enumerate(kwargs_list):
            args['call_stack'] = call_stack
            if self.log_extra:
                args['_log_extra'] = self.log_extra
            sub_task_signature = sub_task_class().subtask(
                kwargs=args,
                source_data=source_data[index] if source_data is not None else self.task.source_data,
                soft_time_limit=task_config.soft_time_limit,
                root_id=self.main_task_id,
                main_task_id=self.main_task_id,
                parent_id=self.request.id,
                title=sub_tasks_group_title,
                priority=priority,
                call_stack=call_stack)
            sub_tasks.append(sub_task_signature)

        self.log_info(
            f'{self.task_name}: starting {len(sub_tasks)} sub-tasks...')
        for ss in sub_tasks:
            priority = get_task_priority(ss)
            ss.apply_async(priority=priority,
                           queue=get_queue_by_task_priority(priority))
        if sub_tasks and not self.task.has_sub_tasks:
            self.task.has_sub_tasks = True
            self.task.save(update_fields=['has_sub_tasks'])

    def on_success(self, retval, task_id, args, kwargs):
        task = self.task
        if task:
            if task.name == 'Locate':
                logger.info('Locate: on_success()')
            task.update_progress(100, True)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        task = self.task
        task.terminate_spawned_processes('locally')
        if not task:
            return
        try:
            task.update_progress(100, False)
        except IntegrityError:
            # task object might have been deleted
            pass

    def prepare_task_execution(self):
        TaskUtils.prepare_task_execution()
        self._cached_data = None

    def __call__(self, *args: Any, **kwargs: Any) -> Any:

        self.prepare_task_execution()

        # moved into run() method - seems sometimes task restarts without re-initiating
        # Task.objects.increase_run_count(self.request.id)

        working = [True]
        if self.db_connection_ping:
            def func_closure(cl_task_id, cl_working):
                def ping_db():
                    while cl_working[0]:
                        Task.objects.filter(pk=cl_task_id).values_list('status', flat=True)
                        time.sleep(60)

                return ping_db

            self.working = True
            threading.Thread(target=func_closure(self.request.id, working), daemon=True).start()

        try:
            return super().__call__(*args, **kwargs)
        except Exception as exc:

            # Here we can have the following variants:
            #
            # 1. Task code has thrown one of auto-retry exceptions (declared in task options).
            # Celery catches them in a wrapper around the above __call__ and executes the retry logic.
            # The retry logic can either throw a "Retry" exception if it restarted the task or any other error
            # if max retry number achieved or by some other reason. So in this code we will catch the "Retry"
            # or the error thrown by the retry logic.
            # Timeout exceptions (SoftTimeLimitExceeded) should be declared as auto-retry exceptions if needed.
            # When a timeout occurs Celery throws SoftTimeLimitExceeded right from the line of code on which
            # the timeout occurred.
            #
            # 2. Task code has caught one of auto-retry exceptions and re-thrown it enclosed into some other exception
            # similar to: "raise RuntimeError('Document XXX loading failed') from e" where e is SoftTimeLimitExceeded.
            # In this case Celery will not execute the retry.
            # Here we try to find - if one of "caused by" or "context" exceptions is in the auto-retry list
            # and execute the same auto-retry logic as Celery should do.
            # task.retry() method re-starts the task and throws either Retry exception or any other - we catch them
            # and log.

            # If it was not Retry - try finding one of enclosed auto-retry exceptions and process them.
            if not isinstance(exc, Retry) and getattr(self, 'autoretry_for', None):
                retry_exc = None
                for retry_exc_class in self.autoretry_for:
                    retry_exc = find_cause_of_type(exc, retry_exc_class)
                    if retry_exc:
                        break
                if retry_exc:
                    retry_kwargs = getattr(self, 'retry_kwargs', None) or dict()
                    retry_backoff = int(getattr(self, 'retry_backoff', False))
                    retry_backoff_max = int(getattr(self, 'retry_backoff_max', 600))
                    retry_jitter = getattr(self, 'retry_jitter', True)

                    if retry_backoff:
                        retry_kwargs['countdown'] = \
                            get_exponential_backoff_interval(
                                factor=retry_backoff,
                                retries=self.request.retries,
                                maximum=retry_backoff_max,
                                full_jitter=retry_jitter)

                    try:
                        # Next line raises Retry exception
                        self.retry(exc=retry_exc, **retry_kwargs)
                    except Exception as e1:
                        # Here we catch either Retry in case Celery is going to retry
                        # or any other exception thrown by task.retry()
                        # We log it and re-throw.
                        self.log_error(self._render_task_failed_message(args, kwargs), exc_info=e1)
                        raise e1

            # This line logs an error or a Retry exception.
            self.log_error(self._render_task_failed_message(args, kwargs), exc_info=exc)
            raise exc
        finally:
            working[0] = False


class CeleryTaskLogger(ProcessLogger):
    def __init__(self, celery_task: ExtendedTask) -> None:
        super().__init__()
        self._celery_task = celery_task

    def set_progress_steps_number(self, steps):
        self._celery_task.set_push_steps(steps)

    def step_progress(self):
        self._celery_task.push()

    def info(self, message: str, **kwargs):
        return self._celery_task.log_info(message, **kwargs)

    def debug(self, message: str, **kwargs):
        return self._celery_task.log_debug(message, **kwargs)

    def warn(self, message: str, **kwargs):
        return self._celery_task.log_warn(message, **kwargs)

    def error(self, message: str,
              field_code: str = None, exc_info: Exception = None,
              **kwargs):
        if field_code:
            message = f'{field_code}: {message or "error"}'

        return self._celery_task.log_error(
            message, exc_info=exc_info, log_field_code=field_code, **kwargs)


@shared_task(base=ExtendedTask, bind=True, name='advanced_celery.end_chord')
def end_chord(task: ExtendedTask, *args, **kwargs):
    status = kwargs.get('status')
    title = task.task.title or task.task.name

    try:
        if status == 'success':
            task.log_info(
                '{0}: all sub-tasks have been processed successfully'.format(title))
        else:
            task.log_error('{0}: sub-tasks processing crashed'.format(title))
    except:
        if status == 'success':
            logger.info('{0}: all sub-tasks have been processed successfully'.format(title))
        else:
            logger.error('{0}: sub-tasks processing crashed'.format(title))


@check_blocks_decorator(raise_error=True, error_message='Task is blocked.')
def call_task_func(*args, **kwargs):
    return _call_task_func(*args, **kwargs)


def _call_task_func(task_func: Callable,
                    task_args: Tuple,
                    user_id,
                    source_data=None,
                    metadata: Dict = None,
                    visible: bool = True,
                    queue: str = None,
                    exchange: str = None,
                    routing_key: str = None,
                    run_after_sub_tasks_finished: bool = False,
                    run_if_parent_task_failed: bool = False,
                    main_task_id: str = None,
                    call_stack: str = None,
                    parent_stack: str = None,
                    caller_task: Optional[ExtendedTask] = None,
                    priority: Union[int, None] = None):
    celery_task_id = str(fast_uuid())
    priority = priority if priority is not None else get_task_priority(task_func)
    call_stack = call_stack or get_call_stack_line(-3)
    if parent_stack:
        call_stack = f'{parent_stack}\n{call_stack}'

    task_name = (task_func.name if hasattr(task_func, 'name') else '') or task_func.__name__
    task = Task.objects.create(
        id=celery_task_id,
        name=task_name,
        user_id=user_id,
        args=task_args,
        source_data=source_data,
        metadata=metadata,
        visible=visible if visible is not None else True,
        run_after_sub_tasks_finished=run_after_sub_tasks_finished,
        run_if_parent_task_failed=run_if_parent_task_failed,
        main_task_id=main_task_id,
        priority=priority,
        queue=queue,
        bad_health_check_num=0,
        restart_count=0,
        call_stack=call_stack,
        failure_reported=False,
        log_extra=caller_task.log_extra if caller_task else None
    )

    task.write_log('Celery task id: {}\n'.format(celery_task_id))
    task_config = _get_or_create_task_config(task_func)
    if not queue:
        queue = get_queue_by_task_priority(priority)
    task_func.apply_async(queue=queue,
                          args=task_args,
                          task_id=celery_task_id,
                          soft_time_limit=task_config.soft_time_limit,
                          priority=priority,
                          exchange=exchange,
                          routing_key=routing_key)
    return task.pk


@check_blocks_decorator(raise_error=True, error_message='Task is blocked.')
def call_task(*args, **kwargs):
    return _call_task(*args, **kwargs)


def _call_task(task_name, **options):
    """
    Call celery task by name
    :param task_name: str task name or task class
    :param options: task params
    :return:
    """
    if isclass(task_name):
        task_class_resolved = task_name
        task_name_resolved = task_class_resolved.name
    else:
        task_name_resolved = str(task_name)
        this_module_name = options.pop('module_name', __name__)
        _this_module = importlib.import_module(this_module_name)
        task_class_resolved = getattr(_this_module, task_name_resolved.replace(' ', ''))

    priority = get_task_priority(task_class_resolved)

    if task_name_resolved == 'LoadDocuments' \
            and 'metadata' in options and 'session_id' in options['metadata']:
        options['propagate_exception'] = True
        options['metadata']['propagate_exception'] = True

    celery_task_id = str(fast_uuid())

    project_id = options.get('project_id')
    session_id = options.get('session_id')
    countdown = options.get('countdown')
    eta = options.get('eta')

    call_stack = options.get('call_stack') or get_call_stack_line(-3)

    # metadata should not be stored in kwargs, because kwargs is indexed
    # and can not be a large field
    options_wo_metadata = {o: options[o] for o in options if o != 'metadata'}
    display_name = task_names.TASK_FRIENDLY_NAME.get(task_name_resolved) or task_name_resolved
    queue = task_class_resolved.queue \
        if hasattr(task_class_resolved, 'queue') \
        else get_queue_by_task_priority(priority)

    task = Task.objects.create(
        id=celery_task_id,
        name=task_name_resolved,
        display_name=display_name,
        user_id=options.get('user_id'),
        metadata=options.get('metadata', {}),
        kwargs=pre_serialize(celery_task_id, None, options_wo_metadata),  # this changes the options_wo_metadata !
        source_data=options.get('source_data'),
        group_id=options.get('group_id'),
        visible=options.get('visible', True),
        project=Project.all_objects.get(pk=project_id) if project_id else None,
        upload_session=UploadSession.objects.get(pk=session_id) if session_id else None,
        priority=priority or 0,
        queue=queue,
        restart_count=0,
        bad_health_check_num=0,
        call_stack=call_stack,
        failure_reported=False
    )

    # updating options with the changes made in options_wo_metadata by pre_serialize()
    options.update(options_wo_metadata)

    task.write_log('Celery task id: {}\n'.format(celery_task_id))
    options['task_id'] = task.id
    is_async_task = options.pop('async', True)
    task_config = _get_or_create_task_config(task_class_resolved)

    if is_async_task:

        task_class_resolved().apply_async(
            kwargs=options,
            task_id=celery_task_id,
            soft_time_limit=task_config.soft_time_limit,
            countdown=countdown,
            eta=eta,
            priority=priority or 0,
            queue=queue)
    else:
        task_class_resolved()(**options)
    return task.pk


@shared_task(base=ExtendedTask,
             bind=True,
             soft_time_limit=3600,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError),
             max_retries=3)
def delete_document_on_load_failed(task: ExtendedTask, file_name: str, kwargs: dict):
    def log_error(message, exc_info: Exception = None, **kwargs):
        task.log_error(message, exc_info, **kwargs)

    document_name = os.path.basename(file_name)
    document_source = os.path.dirname(file_name)

    document_ids = list(
        Document.objects
            .filter(name=document_name, source=document_source)
            .values_list('pk', flat=True))

    if document_ids:
        task.log_error(f'Loading documents task failed, deleting documents: {file_name} (ids: {document_ids})')

        task_user = None
        try:
            task_user = task.task.user if task.task else None
        except RuntimeError:
            # the task might have been deleted already
            pass

        try:
            from apps.document.tasks import DocumentCleaner
            cleaner = DocumentCleaner()
            cleaner.clean(document_ids=document_ids,
                          delete_files=False,
                          log_error=log_error,
                          user=task_user)
        except Exception as e:
            task.log_error(f'Unable to delete documents, file_name={file_name}', exc_info=e)


class LoadDocuments(ExtendedTask):
    """
    Load Document, i.e. create Document and TextUnit objects
    from uploaded document files in a given directory
    :param kwargs: task_id - Task id
                   source_path - (str) relative dir path in media/FILEBROWSER_DOCUMENTS_DIRECTORY
                   delete - (bool) delete old objects
                   document_type - (DocumentType) f.e. lease.LeaseDocument
                   source_type - (str) f.e. "SEC data"
    :return:
    """
    name = 'Load Documents'

    soft_time_limit = 3600
    default_retry_delay = 10
    retry_backoff = True
    autoretry_for = (SoftTimeLimitExceeded, InterfaceError, OperationalError)
    max_retries = 3
    weight = 10

    TASK_META_PREDEFINED_DOC_FIELDS_CODE_TO_VAL = 'pre_defined_doc_fields_code_to_val'
    TASK_META_FILE_NAME = 'file_name'
    TASK_META_SHOULD_RUN_STANDARD_LOCATORS = 'should_run_standard_locators'
    TASK_META_DOCUMENT_ID = 'document_id'
    TASK_META_LINKED_TASKS = 'linked_tasks'

    def process(self, **kwargs):
        path = kwargs['source_data']
        self.log_info('Parse {0} at {1}'.format(path, file_storage))
        file_list = file_storage.list_documents(path)

        self.log_info("Detected {0} files. Added {0} subtasks.".format(len(file_list)))

        if len(file_list) == 0:
            raise RuntimeError('Wrong file or directory name or directory is empty: {}'
                               .format(path))

        if kwargs.get('delete'):
            Document.all_objects.all().delete()

        # prevent transferring document type objects to sub-tasks
        document_type_dict = kwargs.get('document_type')  # type: Dict[str, Any]
        if document_type_dict:
            kwargs['document_type_id'] = document_type_dict['pk']
            del kwargs['document_type']

        project_dict = kwargs.get('project')  # type: Dict[str, Any]
        if project_dict:
            kwargs['project_id'] = project_dict['pk']
            del kwargs['project']

        load_docs_args = [{'uri': file_path,
                           'session_id': kwargs['session_id'],
                           'task_kwargs': kwargs} for file_path in file_list]

        self.run_sub_tasks_class_based(
            'Load Each Document',
            CreateDocument,
            load_docs_args,
            file_list)

    @staticmethod
    @shared_task(base=ExtendedTask,
                 db_connection_ping=True,
                 bind=True,
                 soft_time_limit=3600,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(InterfaceError, OperationalError),
                 max_retries=3)
    def create_document_from_bytes(task: ExtendedTask,
                                   doc_bytes: bytes,
                                   file_name: str,
                                   kwargs) -> int:
        session_id = kwargs['metadata']['session_id']
        with tempfile.NamedTemporaryFile() as fw:
            fw.write(doc_bytes)
            return LoadDocuments.create_document_local(
                task=task,
                file_path=fw.name,
                file_name=file_name,
                kwargs=kwargs,
                upload_session_id=session_id)

    @staticmethod
    def create_document_local(task: ExtendedTask,
                              file_path,
                              file_name,
                              kwargs,
                              pre_defined_doc_fields_code_to_val: Dict[str, Any] = None,
                              upload_session_id: Optional[str] = None) -> int:
        """
        :return: the new :class:`Document's<apps.document.models.Document>` ID
        """
        task.task.title = f'Load Document: {file_name}'
        task.log_extra = {Document.LOG_FIELD_DOC_NAME: file_name}

        document_name = os.path.basename(file_name)
        document_source = os.path.dirname(file_name)
        file_size = kwargs.get('file_size') or os.path.getsize(file_path)
        should_run_standard_locators = bool(kwargs.get('run_standard_locators'))
        user_id = kwargs.get('user_id')
        project_id = kwargs.get('project_id')
        assignee_id = kwargs.get('assignee_id')
        document_type_id = kwargs.get('document_type_id')
        do_not_check_exists = bool(kwargs.get('do_not_check_exists'))

        # Checking for existing document.
        # There were discussions on this topic:
        # - if we should allow uploading multiple docs with the same name into the same project;
        # - if we should rename them;
        # - if we should allow docs with the same file name but within different directories (when uploading dirs).
        #
        # Originally here we had a check for loading documents via old API used in /explorer (admin tasks):
        # if not do_not_check_exists and upload_session_id is None:
        # For old API we did not use the upload sessions.
        #
        # Adding logic for preventing uploading totally the same document by name, path, source)
        # within the same session.
        # This is to cover the case of restarting totally the same doc loading task by the task health
        # monitor which detected the first execution of this task as lost because of complicated cluster
        # autoscaling issues.
        if not do_not_check_exists:
            # base query for both old and new APIs/workflows
            qr_document_id = Document.objects \
                .filter(name=document_name, source=document_source)

            # if this is the new API/workflow
            if upload_session_id:
                qr_document_id = qr_document_id.filter(upload_session_id=upload_session_id,
                                                       file_size=file_size)

            document_id = qr_document_id.values_list('pk', flat=True).first()
            if document_id:
                task.log_info('SKIP (EXISTS): ' + file_name)
                return document_id

        with transaction.atomic():
            upload_session = None
            project = None

            if upload_session_id:
                upload_session = UploadSession.objects.get(pk=upload_session_id)
                task.log_extra['log_upload_session'] = upload_session.pk
                project = upload_session.project
                if project:
                    document_type = project.type
                else:  # let it crash if document_type_id is not specified too
                    document_type = DocumentType.objects.get(pk=document_type_id)
                document_type_str = f'{document_type.code} ({project.name})' if project else document_type.code
                task.log_info(message=f'Document Upload Session id={upload_session.pk}, {document_type_str}')
            elif project_id:
                project = Project.objects.get(pk=project_id)
                document_type = project.type
            elif document_type_id:
                document_type = DocumentType.objects.get(pk=document_type_id)
            else:
                document_type = DocumentType.objects.get(pk=DOCUMENT_TYPE_PK_GENERIC_DOCUMENT)

            document = Document.objects.create(
                document_type=document_type,
                project=project,
                assignee_id=assignee_id,
                assign_date=now() if assignee_id else None,
                upload_session=upload_session,
                name=document_name,
                description=file_name,
                source=document_source,
                source_type=kwargs.get('source_type'),
                source_path=file_name,
                alt_source_path=None,  # to be filled in process_text_extraction_results()
                language=None,  # to be filled in process_text_extraction_results()
                title=None,  # to be filled in process_text_extraction_results()
                file_size=file_size,
                folder=kwargs.get('directory_path'),
                document_class=None,  # to be filled in process_text_extraction_results()
                ocr_rating=None)  # to be filled in process_text_extraction_results()
            document.save()

            # to be filled in process_text_extraction_results()
            DocumentText.objects.create(document=document, full_text=None)
            DocumentPDFRepresentation.objects.create(document=document, char_bboxes=None)

            # to be filled in process_text_extraction_results()
            DocumentMetadata.objects.create(document=document, metadata={
                'upload_status': 'DONE'
            })

            task.log_extra[Document.LOG_FIELD_DOC_ID] = str(document.pk)

            linked_tasks: List[Dict[str, Any]] = kwargs.get('linked_tasks') or []

            # Document text and structure extraction will go to the text extraction system.
            # When the results are ready it will trigger process_text_extraction_results() with
            # this task id as the parent_id.
            # To maintain the proper task-sub-task hierarchy we create the Task model for the process... task here.
            # process_text_extraction_results() will schedule the Locate task and the field detection.
            # It will require some additional information which we save into this task's metadata.
            task.log_info(f'{task_names.TASK_NAME_PROCESS_TEXT_EXTRACTION_RESULTS} is scheduled, '
                          f'parent is "{task.request.id}", main task is "{task.main_task_id}"')

            process_results_task = Task(name=task_names.TASK_NAME_PROCESS_TEXT_EXTRACTION_RESULTS,
                                        main_task_id=task.main_task_id,
                                        parent_task_id=task.request.id,
                                        status=None,
                                        own_status=None,
                                        queue=settings.CELERY_QUEUE_DEFAULT,
                                        args=(),
                                        user_id=user_id,
                                        kwargs={},
                                        log_extra={},
                                        metadata={
                                            LoadDocuments.TASK_META_DOCUMENT_ID: document.pk,
                                            LoadDocuments.TASK_META_FILE_NAME: file_path,
                                            LoadDocuments.TASK_META_PREDEFINED_DOC_FIELDS_CODE_TO_VAL:
                                                pre_defined_doc_fields_code_to_val,
                                            LoadDocuments.TASK_META_SHOULD_RUN_STANDARD_LOCATORS:
                                                should_run_standard_locators,
                                            LoadDocuments.TASK_META_LINKED_TASKS: linked_tasks
                                        })
            process_results_task.save()

            Task.objects.filter(pk=task.request.id).exclude(has_sub_tasks=True).update(has_sub_tasks=True)

            client = TextExtractionSystemWebClient(settings.TEXT_EXTRACTION_SYSTEM_URL)

            from apps.document.app_vars import OCR_ENABLE, DESKEW_ENABLE, \
                DOCUMENT_LOCALE, OCR_FILE_SIZE_LIMIT, PDF_COORDINATES_DEBUG_ENABLE, TABLE_DETECTION_ENABLE, \
                TABLE_DETECTION_METHOD, OCR_PAGE_TIMEOUT, REMOVE_OCR_LAYERS
            ocr_enable = OCR_ENABLE.val(project_id=project_id) \
                         and os.path.getsize(file_path) <= OCR_FILE_SIZE_LIMIT.val(project_id=project_id) * 1024 * 1024
            remove_ocr_layers = REMOVE_OCR_LAYERS.val(project_id)
            deskew_enable = DESKEW_ENABLE.val(project_id=project_id)
            coords_debug_enable = PDF_COORDINATES_DEBUG_ENABLE.val(project_id=project_id)
            table_detection_enable = TABLE_DETECTION_ENABLE.val(project_id=project_id)
            table_parser_str = TABLE_DETECTION_METHOD.val(project_id=project_id)
            ocr_page_timeout = OCR_PAGE_TIMEOUT.val(project_id=project_id)

            call_back_url = f'{settings.TEXT_EXTRACTION_SYSTEM_CALLBACK_URL}/{process_results_task.id}/'

            # Define document language depending on the project language
            is_project_locale_correct = DOCUMENT_LOCALE.val(project_id=project_id) in settings.LOCALES.keys()
            doc_language = DOCUMENT_LOCALE.val(project_id=project_id) if is_project_locale_correct else ""
            client.schedule_data_extraction_task(fn=file_path,
                                                 request_id=process_results_task.id,
                                                 call_back_url=call_back_url,
                                                 doc_language=doc_language,
                                                 ocr_enable=ocr_enable,
                                                 deskew_enable=deskew_enable,
                                                 char_coords_debug_enable=coords_debug_enable,
                                                 table_extraction_enable=table_detection_enable,
                                                 log_extra={
                                                     'special_log_type': 'cx',
                                                     'log_main_task_id': task.main_task_id
                                                 },
                                                 output_format=OutputFormat.msgpack,
                                                 table_parser=TableParser(table_parser_str),
                                                 page_ocr_timeout_sec=ocr_page_timeout,
                                                 remove_ocr_layer=remove_ocr_layers)
            return document.pk

    @staticmethod
    def cancel_text_extraction(load_documents_main_task_id: str, log_func: Callable[[str], None]):
        request_ids = Task.objects.filter(name=task_names.TASK_NAME_PROCESS_TEXT_EXTRACTION_RESULTS,
                                          main_task_id=load_documents_main_task_id).values_list('pk', flat=True)
        client = TextExtractionSystemWebClient(settings.TEXT_EXTRACTION_SYSTEM_URL)
        for request_id in request_ids:
            try:
                cancel_result = client.purge_data_extraction_task(request_id)
                log_func(f'Canceled text/data extraction for request #{request_id}.\n'
                         f'Response:\n'
                         f'{cancel_result}')
            except Exception as e:
                from contraxsuite_logging import HumanReadableTraceBackException
                exc_msg = HumanReadableTraceBackException.from_exception(e).human_readable_format()
                log_func(f'Unable to cancel text/data extraction for request #{request_id}\n'
                         f'{exc_msg}')
                raise

    @staticmethod
    def safe_del_text_extraction_files(client: TextExtractionSystemWebClient,
                                       task: ExtendedTask,
                                       request_id: str,
                                       original_file_name: str):
        try:
            client.delete_data_extraction_task_files(request_id)
        except Exception as del_err:
            task.log_error(
                f'Unable to delete text/data extraction task files in LexPredict Text Extraction System\n'
                f'Request id: {request_id}\n'
                f'Original file name: {original_file_name}\n',
                exc_info=del_err)

    @staticmethod
    @shared_task(base=ExtendedTask,
                 name=task_names.TASK_NAME_PROCESS_TEXT_EXTRACTION_RESULTS,
                 bind=True,
                 soft_time_limit=600,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3)
    def process_text_extraction_results(task: ExtendedTask,
                                        **kwargs):

        # If everything went as planned the Task model for this was created manually
        # in .create_document_local() and all the information required to run this task was saved
        # into this task's metadata.
        # Also we passed this task's id as the request_id to the text extraction API.

        extraction_request_id = task.request.id
        client = TextExtractionSystemWebClient(settings.TEXT_EXTRACTION_SYSTEM_URL)
        extract_process_status = client.get_data_extraction_task_status(extraction_request_id)

        if extract_process_status.status != STATUS_DONE:
            # file name is not obligatory here, it's just for reference
            orig_doc_name = 'undefined'
            try:
                document_id = task.task.metadata[LoadDocuments.TASK_META_DOCUMENT_ID]
                orig_doc_name = Document.objects.filter(pk=document_id).values_list('name', flat=True)[0]
            except:
                pass
            LoadDocuments.safe_del_text_extraction_files(client, task, extraction_request_id, orig_doc_name)
            # This task fail should cause the parent Load Documents task failure.
            raise Exception(f'Document text and data extraction failed in LexPredict Text Extraction system.\n'
                            f'Request id: {extraction_request_id}\n'
                            f'Original file name: {extract_process_status.original_file_name}\n'
                            f'Status: {extract_process_status.status}')

        task_meta = task.task.metadata
        document_id = task_meta[LoadDocuments.TASK_META_DOCUMENT_ID]
        file_name = task_meta[LoadDocuments.TASK_META_FILE_NAME]
        should_run_standard_locators = task_meta[LoadDocuments.TASK_META_SHOULD_RUN_STANDARD_LOCATORS]
        predefined_doc_fields_code_to_val = task_meta[LoadDocuments.TASK_META_PREDEFINED_DOC_FIELDS_CODE_TO_VAL]
        linked_tasks = task_meta[LoadDocuments.TASK_META_LINKED_TASKS]

        # It is expected that the document id is passed into call_back_additional_info
        # when the text extraction is requested by LoadDocuments.create_document_local()
        task.log_extra = {Document.LOG_FIELD_DOC_ID: str(document_id)}

        # originally here was the metadata returned by Tika but I did not understand if we use it at all
        metadata = {}

        plain_text = client.get_plain_text(extraction_request_id)

        if not plain_text.strip():
            client.delete_data_extraction_task_files(extraction_request_id)
            raise RuntimeError('No text extracted.')

        task.log_info(f'Document plain text has {len(plain_text)} characters')

        plain_text_struct: PlainTextStructure = client.get_extracted_text_structure_as_msgpack(extraction_request_id)
        text_markup: Optional[bytes] = client.get_extracted_pdf_coordinates_as_msgpack_raw(extraction_request_id)
        if not text_markup:
            task.log_info('Text markup is empty')
        else:
            task.log_info(f'Text markup has {len(text_markup)} bytes')

        # detect if document is contract (do detect by default)
        detect_contract = kwargs.get('detect_contract')
        if detect_contract is None:
            from apps.document.app_vars import DETECT_CONTRACT
            detect_contract = DETECT_CONTRACT.val()

        doc_class = None
        if detect_contract:
            doc_class, doc_is_contract_proba = LoadDocuments.classify_document(plain_text)
            metadata[DOCUMENT_FIELD_CODE_CLASS] = doc_class
            metadata[DOC_METADATA_DOCUMENT_CLASS_PROB] = doc_is_contract_proba

        # calculate OCR grade
        ocr_rating_calc = TextOCRRatingCalculator()
        ocr_rating = ocr_rating_calc.calculate_rating(plain_text, plain_text_struct.language)

        metadata['title'] = metadata.get('title', None) or plain_text_struct.title

        # returns list of dict (start, end, title, title_start, title_end, level, abs_level)
        plain_text_struct.sections.sort(key=lambda s: s.title_start)
        metadata['sections'] = [s.to_dict() for s in plain_text_struct.sections]

        with transaction.atomic():
            doc: Document = Document.objects.get(pk=document_id)
            document_text: DocumentText = doc.documenttext
            document_text.full_text = plain_text
            document_text.save()

            document_pdf_repr: DocumentPDFRepresentation = doc.document_pdf_repr
            document_pdf_repr.char_bboxes = text_markup
            document_pdf_repr.set_pages([p.to_dict() for p in plain_text_struct.pages])
            document_pdf_repr.save()

            document_metadata: DocumentMetadata = doc.documentmetadata
            if not document_metadata.metadata:
                document_metadata.metadata = metadata
            else:
                document_metadata.metadata.update(metadata)
            document_metadata.save()

            user_id = task.task.user_id
            # create Document Properties
            document_properties = [
                DocumentProperty(
                    created_by_id=user_id,
                    modified_by_id=user_id,
                    document_id=doc.pk,
                    key=k,
                    value=v) for k, v in metadata.items() if v]
            DocumentProperty.objects.bulk_create(document_properties)

            # create text units
            paragraph_list = [
                TextUnit(
                    document=doc,
                    unit_type='paragraph',
                    location_start=p.start,
                    location_end=p.end,
                    language=p.language,
                    text_hash=hashlib.sha1(plain_text[p.start:p.end].encode("utf-8")).hexdigest(),
                    project=doc.project)
                for p in plain_text_struct.paragraphs
            ]
            paragraph_list = TextUnit.objects.bulk_create(paragraph_list)
            doc.paragraphs = len(paragraph_list)

            TextUnitText.objects.bulk_create([
                TextUnitText(
                    text_unit=text_unit,
                    document_id=doc.pk,
                    text=plain_text[p.start:p.end]
                ) for text_unit, p in zip(paragraph_list, plain_text_struct.paragraphs)
            ])

            sentence_list = [
                TextUnit(
                    document=doc,
                    location_start=s.start,
                    location_end=s.end,
                    text_hash=hashlib.sha1(plain_text[s.start:s.end].encode("utf-8")).hexdigest(),
                    unit_type='sentence',
                    language=s.language,
                    project=doc.project)
                for s in plain_text_struct.sentences
            ]
            sentence_list = TextUnit.objects.bulk_create(sentence_list)
            doc.sentences = len(sentence_list)
            TextUnitText.objects.bulk_create([
                TextUnitText(
                    text_unit=text_unit,
                    document_id=doc.pk,
                    text=plain_text[s.start:s.end]
                ) for text_unit, s in zip(sentence_list, plain_text_struct.sentences)
            ])
            task.log_info(f'{doc.sentences} sentences and {doc.paragraphs} paragraphs are stored')

            page_list = [
                DocumentPage(
                    document_id=doc.pk,
                    number=p.number,
                    location_start=p.start,
                    location_end=p.end)
                for p in plain_text_struct.pages
            ]
            DocumentPage.objects.bulk_create(page_list)
            task.log_info(f'Document has {len(page_list)} pages')

            base_fn, ext = os.path.splitext(doc.source_path)
            # download OCR-ed/prepared/alt PDF and re-upload to Contraxsuite storage
            # update alt_source_path if needed
            with client.get_pdf_as_local_file(extraction_request_id) as local_pdf_fn:
                doc.alt_source_path = base_fn + '.alt.pdf'
                task.log_info(f'File "{local_pdf_fn}" has {os.path.getsize(local_pdf_fn)} bytes.')
                with open(local_pdf_fn, 'rb') as local_pdf_f:
                    file_storage.write_document(doc.alt_source_path, local_pdf_f, skip_existing=True)

            doc.document_class = doc_class
            doc.ocr_rating = ocr_rating
            doc.language = plain_text_struct.language
            doc.title = plain_text_struct.title

            doc.save()
            doc_tables = None

            if extract_process_status.tables_extracted:
                tables_json = client.get_extracted_tables_as_msgpack(extraction_request_id)

                doc_tables = [
                    DocumentTable(document=doc,
                                  table=pd.DataFrame(t.data, columns=range(len(t.data[0]))),
                                  bounding_rect=[t.coordinates.left,
                                                 t.coordinates.top,
                                                 t.coordinates.width,
                                                 t.coordinates.height],
                                  page=t.page)
                    for t in tables_json.tables if t.data
                ]
                DocumentTable.objects.bulk_create(doc_tables)

            if document_metadata.metadata and 'sections' in document_metadata.metadata:
                if paragraph_list:
                    from apps.document.tasks import filter_multiple_sections_inside_paragraph
                    filter_multiple_sections_inside_paragraph(document_metadata.metadata, paragraph_list)

                # filter sections that are inside one of the tables
                if doc_tables:
                    from apps.document.tasks import filter_sections_inside_tables
                    filter_sections_inside_tables(document_metadata.metadata, document_pdf_repr, doc_tables)
                    document_metadata.save()

            from apps.document.app_vars import DETECT_CONTRACT_TYPE
            if DETECT_CONTRACT_TYPE.val():
                contract_type, type_vector = ContractTypeClassifier.get_document_contract_type(
                    plain_text, True, document_language=doc.language, project_id=doc.project_id)
                doc.document_contract_class = contract_type
                doc.save(update_fields=['document_contract_class'])
                document_metadata.metadata[DOC_METADATA_DOCUMENT_CONTRACT_CLASS_VECTOR] = type_vector
                document_metadata.save()

            # not trying to set the doc language based on the text units
            # because the text extraction system will always return some language
            # for the document text

            # save extra document info
            kwargs['document'] = doc

        task.log_info(message=f'LOADED: {extract_process_status.original_file_name}, {len(plain_text)} chars')
        task.log_info(message='Document pk: %d' % doc.pk)

        if should_run_standard_locators:
            from apps.extract.app_vars import STANDARD_LOCATORS

            task.run_sub_tasks_class_based('Locate', Locate, [{
                'locate': list(set(STANDARD_LOCATORS.val() + ['term'])),
                'parse': ['sentence'],
                'do_delete': False,
                'session_id': doc.upload_session_id,
                'metadata': {'session_id': doc.upload_session_id, 'file_name': file_name},
                'user_id': user_id,
                'document_id': doc.pk,
                'doc_loaded_by_user_id': user_id,
                'document_initial_load': True,
                'predefined_field_codes_to_python_values': predefined_doc_fields_code_to_val
            }])
        else:
            logger.info(f'process_text_extraction_results(#{doc.pk}, project {doc.project_id}) ' +
                        'is called, standard locators are not applied')
            if predefined_doc_fields_code_to_val:
                # note that the document will never be "processed" and cached
                user = User.objects.get(pk=user_id) if user_id is not None else None
                field_repo = DocumentFieldRepository()
                field_repo.store_values_one_doc_many_fields_no_ants(
                    doc=doc,
                    field_codes_to_python_values=predefined_doc_fields_code_to_val,
                    user=user)

        for linked_task_kwargs in linked_tasks:
            linked_task_kwargs['document_id'] = doc.pk
            linked_task_kwargs['source_data'] = task.task.source_data
            linked_task_id = call_task(**linked_task_kwargs)
            task.log_info(message='linked_task_id: {}'.format(linked_task_id))

        # Deleting the results from the storage of the text extraction system only after everything worked fine.
        # Expecting this task to be safely restarted otherwise.
        client.delete_data_extraction_task_files(extraction_request_id)
        LoadDocuments.save_document_uploaded_action(document_id, user_id)

    @staticmethod
    def save_document_uploaded_action(document_id: int, user_id: int):
        action = Action(name='Document Uploaded',
                        message='Document Uploaded',
                        view_action='upload',
                        user_id=user_id,
                        content_type=ContentType.objects.get_for_model(Document),
                        model_name='Document',
                        app_label='document',
                        object_pk=document_id)
        action.save()
        document = Document.objects.get(pk=document_id)
        document.created_by = action.user
        document.created_date = action.date
        document.modified_by = action.user
        document.modified_date = action.date
        document.save()

    @staticmethod
    def classify_document(doc_text: str) -> Tuple[str, float]:
        res = is_contract(doc_text, return_probability=True)
        return (DocumentClass.CONTRACT if res[0] else DocumentClass.GENERIC, res[1]) \
            if res is not None else (None, None)

    @staticmethod
    def get_file_extension(file_name: str, file_path: str) -> Tuple[str, str]:
        """
        Get file extension and determine file type. Any `text/plain` file is considered to have extension `.txt`.
        :param file_name: file name + extension
        :param file_path: full file path
        :return: (extension, type_string,), type_string: 'CONTENT' or 'ARCHIVE'
        """
        _fn, ext = os.path.splitext(file_name)
        if not ext:
            known_extensions = {'text/plain': 'txt'}
            mt = python_magic.from_file(file_path)
            ext = known_extensions.get(mt) or mimetypes.guess_extension(mt)
        ext = ext or ''
        file_content = 'ARCHIVE' if ArchiveFile.check_file_is_archive(file_path, ext) else 'CONTENT'
        return ext, file_content

    @staticmethod
    def safely_get_paragraphs(text: str) -> List[Tuple[str, int, int]]:
        try:
            return list(get_paragraphs(text, return_spans=True))
        except:
            return [(text, 0, len(text) - 1)]


class CreateDocument(ExtendedTask):
    soft_time_limit = 6 * 3600
    default_retry_delay = 10
    retry_backoff = True
    autoretry_for = (SoftTimeLimitExceeded, InterfaceError, OperationalError)
    max_retries = 3
    weight = 10
    name = 'Create Document'

    def process(self,
                uri: str,
                session_id: str,
                task_kwargs: Optional[Dict[str, Any]], *args, **kwargs) -> int:
        task_id = self.task.pk if self.task else '-'
        self.log_info(f'CreateDocument("{uri}"), task id #{task_id}')
        with file_storage.get_document_as_local_fn(uri) as (fn, file_name):
            self.run_if_task_or_sub_tasks_failed(delete_document_on_load_failed, args=(uri, task_kwargs))
            return LoadDocuments.create_document_local(
                task=self,
                file_path=fn,
                file_name=uri,
                kwargs=task_kwargs,
                upload_session_id=session_id)


class LoadTerms(ExtendedTask):
    """
    Load Terms from a dictionary sample
    """
    name = 'Load Terms'

    def load_terms_from_path(self, path: str, real_fn: str, terms_df: pd):
        self.log_info(f'Parse "{real_fn or path}"')
        data = pd.read_csv(path)
        self.log_info(f'Detected {len(data)} terms')
        return terms_df.append(data)

    def process(self, **kwargs):
        """
        Load Terms
        :param kwargs: dict, form data
        :return:
        """
        self.set_push_steps(2)

        repo_paths = kwargs['repo_paths']
        file_path = kwargs.get('file_path')
        tags = None

        existing_action = 'update'
        if 'extra_args' in kwargs:
            tags = [t.strip() for t in kwargs['extra_args'].get('tags', '').split(',')]
            existing_action = kwargs['extra_args'].get('existing_action', 'update')

        terms_df = pd.DataFrame()
        for path in repo_paths:
            terms_df = self.load_terms_from_path(path, None, terms_df)

        if file_path:
            with file_storage.get_as_local_fn(file_path) as (fn, file_name):
                terms_df = self.load_terms_from_path(fn, file_name, terms_df)

        self.push()

        # terms should be cached here
        terms_count = load_terms(terms_df, existing_action=existing_action, tags=tags)
        self.log_info('Total %d unique terms' % terms_count)

        self.push()


class LoadGeoEntities(ExtendedTask):
    """
    Load Geopolitical Entities from given dictionaries
    """
    name = 'Load Geo Entities'
    # map column name to locale and alias type
    locales_map = (
        ('German Name', 'de', 'German Name'),
        ('Spanish Name', 'es', 'Spanish Name'),
        ('French Name', 'fr', 'French Name'),
        ('ISO-3166-2', 'en', 'iso-3166-2'),
        ('ISO-3166-3', 'en', 'iso-3166-3'),
        ('Alias', 'en', 'abbreviation'),
    )

    def load_geo_entities_from_path(self, path: str, real_fn: str, entities_df: pd.DataFrame):
        self.log_info(f'Parse "{real_fn or path}"')
        data = pd.read_csv(path)
        self.log_info(f'Detected {len(data)} entities')
        return entities_df.append(data)

    def set_total_progress(self, progress):
        self.set_push_steps(progress + 2)
        self.push()

    def process(self, **kwargs):
        """
        Load Geopolitical Entities
        :param kwargs: form data
        :return:
        """
        repo_paths = kwargs['repo_paths']
        file_path = kwargs.get('file_path')

        if kwargs['delete']:
            GeoEntity.objects.all().delete()
            GeoRelation.objects.all().delete()
            GeoAlias.objects.all().delete()

        entities_df = pd.DataFrame()
        for path in repo_paths:
            entities_df = self.load_geo_entities_from_path(path, None, entities_df)

        if file_path:
            with file_storage.get_as_local_fn(file_path) as (fn, file_name):
                entities_df = self.load_geo_entities_from_path(fn, file_name, entities_df)

        if entities_df.empty:
            raise RuntimeError('Received 0 entities to process, exit.')

        geo_aliases_count, geo_entities_count = load_geo_entities(entities_df, self.set_total_progress, self.push)

        self.log_info('Total created: %d GeoAliases' % geo_aliases_count)
        self.log_info('Total created: %d GeoEntities' % geo_entities_count)

        self.log_info('Caching geo config for Locate tasks...')
        dict_data_cache.cache_geo_config()

        self.push()


class LoadCourts(ExtendedTask):
    """
    Load Courts data from a file OR github repo
    """
    name = 'Load Courts'
    priority = 7

    def load_courts_from_path(self, path: str, real_fn: str):
        self.log_info(f'Parse "{real_fn or path}"')
        dictionary_data = pd.read_csv(path)
        courts_count = load_courts(dictionary_data)
        self.log_info(f'Detected {courts_count} courts')

    def process(self, **kwargs):
        """
        Load Courts data from a file OR github repo
        :param kwargs: dict, form data
        :return:
        """
        repo_paths = kwargs['repo_paths']
        file_path = kwargs.get('file_path')

        self.set_push_steps(3)

        if 'delete' in kwargs:
            Court.objects.all().delete()
        self.push()

        for path in repo_paths:
            self.load_courts_from_path(path, None)
        if file_path:
            with file_storage.get_as_local_fn(file_path) as (fn, file_name):
                self.load_courts_from_path(fn, file_name)
        self.push()

        self.log_info('Caching courts config for Locate tasks...')
        dict_data_cache.cache_court_config()
        self.push()


class Locate(ExtendedTask):
    """
    Locate multiple items
    """
    name = "Locate"

    soft_time_limit = 6000
    default_retry_delay = 10
    retry_backoff = True
    autoretry_for = (SoftTimeLimitExceeded, InterfaceError, OperationalError,)
    max_retries = 3
    priority = 7

    usage_model_map = dict(
        duration=['DateDurationUsage'],
        geoentity=['GeoEntityUsage', 'GeoAliasUsage']
    )

    CACHE_KEY_GEO_CONFIG = 'geo_config'
    CACHE_KEY_COURT_CONFIG = 'court_config'
    CACHE_KEY_TERM_STEMS = 'term_stems'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_id = 0
        self.root_task_id = ''

    def delete_existing_usages(self, locator_names, document_id, project_id):
        # delete ThingUsage and TextUnitTag(tag=thing)
        for locator_name in locator_names:
            usage_model_names = self.usage_model_map.get(
                locator_name,
                [locator_name.title() + 'Usage'])
            for usage_model_name in usage_model_names:
                usage_model = getattr(extract_models, usage_model_name)
                usage_model_objects = usage_model.objects.all()
                if document_id:
                    usage_model_objects = usage_model_objects.filter(
                        text_unit__document_id=document_id)
                elif project_id:
                    usage_model_objects = usage_model_objects.filter(
                        text_unit__project_id=project_id)

                deleted = usage_model_objects.delete()
                self.log_info(f'Deleted {deleted[0]} {usage_model_name} objects')
            tag_objects = TextUnitTag.objects.filter(tag=locator_name)
            if document_id:
                tag_objects = tag_objects.filter(text_unit__document_id=document_id)
            tags_deleted = tag_objects.delete()
            self.log_info('Deleted {} TextUnitTag(tag={})'.format(
                tags_deleted[0], locator_name))

    def process(self, **kwargs):
        document_id = kwargs.get('document_id')
        doc_loaded_by_user_id = kwargs.get('doc_loaded_by_user_id')
        document_initial_load = bool(kwargs.get('document_initial_load'))
        predefined_field_codes_to_python_values = kwargs.get('predefined_field_codes_to_python_values')
        project_id = kwargs.get('project_id')
        self.project_id = project_id
        self.root_task_id = self.task.id

        if project_id:
            # NB: we subscribe on failed event right from the beginning
            # but we subscribe on successful completion event later on when
            # all subtasks are created
            self.run_if_task_or_sub_tasks_failed(
                Locate.notify_on_completed_complete_action,
                args=(project_id, self.root_task_id, 'FAILURE'))

        # detect items to locate/delete
        if 'locate' in kwargs:
            locate = kwargs['locate']
            if isinstance(locate, (tuple, list)):
                locate = {i: {} for i in locate}
            do_delete = kwargs.get('do_delete', True)
            do_delete = locate if do_delete else []
        else:
            locate = {}
            do_delete = []
            for term_name, term_kwargs in kwargs['tasks'].items():
                if term_kwargs.get('delete') or term_kwargs.get('locate'):
                    do_delete.append(term_name)
                if term_kwargs.get('locate'):
                    locate[term_name] = {i: j for i, j in term_kwargs.items()
                                         if i not in ['locate', 'delete']}

        # cleanup items to locate/delete
        from apps.extract.app_vars import STANDARD_LOCATORS, OPTIONAL_LOCATORS
        available_locators = set(STANDARD_LOCATORS.val(project_id=project_id)) | set(
            OPTIONAL_LOCATORS.val(project_id=project_id))

        locate = {i: j for i, j in locate.items() if i in available_locators}
        do_delete = [i for i in do_delete if i in available_locators]

        # delete ThingUsage and TextUnitTag(tag=thing)
        self.delete_existing_usages(do_delete, document_id, project_id)

        # interrupt if no items to locate
        if not locate:
            return

        # define number of async tasks
        text_units = TextUnit.objects.all()

        if project_id:
            text_units = text_units.filter(project__id=project_id)

        if document_id:
            text_units = text_units.filter(document_id=document_id)

        locate_in = kwargs.get('parse', ['paragraph', 'sentence'])  # type:List[str]
        text_units = text_units.filter(unit_type__in=locate_in)

        self.log_info('Run location of [{}].'.format('; '.join(locate.keys())))
        self.log_info('Locate in {}.'.format(locate_in))
        self.log_info('Found {0} Text Units.'.format(text_units.count()))

        package_size = settings.TEXT_UNITS_TO_PARSE_PACKAGE_SIZE
        text_unit_ids = text_units.values_list('pk', flat=True)

        if text_unit_ids:
            locate_args = [[text_unit_ids[i:i + package_size],
                            kwargs['user_id'],
                            locate,
                            document_initial_load,
                            kwargs.get('selected_tags')]
                           for i in range(0, len(text_unit_ids), package_size)]
            self.run_sub_tasks('Locate Data In Each Text Unit', Locate.parse_text_units, locate_args)

        if document_id:
            document_ids = [document_id]
        elif project_id:
            document_ids = list(Document.objects.filter(
                project_id=project_id).values_list('pk', flat=True))
        else:
            return
        detect_field_values = kwargs.get('detect_field_values', True)
        fire_doc_changed = kwargs.get('fire_doc_changed', True)
        cache_field_values = kwargs.get('cache_field_values', False)

        self.run_after_sub_tasks_finished(
            '',
            self.cache_document_items,
            [(cache_field_values, detect_field_values,
              doc_loaded_by_user_id, document_ids,
              document_initial_load, fire_doc_changed, locate,
              predefined_field_codes_to_python_values,
              self.project_id,
              self.root_task_id)])

        if project_id:
            self.run_after_sub_tasks_finished(
                'Notify on Locate finished',
                Locate.notify_on_completed_complete_action,
                [(project_id, self.root_task_id, 'SUCCESS')])

    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=3600,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3)
    def cache_document_items(self,
                             cache_field_values: bool,
                             detect_field_values: bool,
                             doc_loaded_by_user_id: Optional[int],
                             document_ids: Iterable[int],
                             document_initial_load: bool,
                             fire_doc_changed: bool,
                             locate: Optional[Dict[str, Dict]],
                             predefined_field_codes_to_python_values: Optional[Dict[str, Any]],
                             project_id: int,
                             root_task_id: str):
        for document_id in document_ids:
            self.run_sub_tasks('Cache Generic Document Data',
                               Locate.on_locate_finished,
                               [(document_id,
                                 doc_loaded_by_user_id,
                                 document_initial_load,
                                 predefined_field_codes_to_python_values,
                                 locate,
                                 detect_field_values,
                                 fire_doc_changed)])

    @staticmethod
    def save_summary_on_locate_finished(log: ProcessLogger, doc_id: int, locate: Dict[str, Dict],
                                        document_initial_load: bool = False):
        locate_entities = list(locate.keys())
        request_mat_views_refresh(locate_entities)
        locators = LocatorsCollection.get_locators()

        for locator_name in locate_entities:
            locator = locators.get(locator_name)
            if not locator:
                continue
            locator.update_document_summary(log, doc_id, document_initial_load)

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=6000,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3,
                 priority=7)
    def on_locate_finished(_self: ExtendedTask,
                           doc_id: int,
                           doc_loaded_by_user_id: Optional[int],
                           document_initial_load: bool,
                           predefined_field_codes_to_val: Optional[Dict[str, Any]] = None,
                           locate: Optional[Dict[str, Dict]] = None,
                           detect_field_values: bool = True,
                           fire_doc_changed: bool = True):
        doc = Document.all_objects.filter(pk=doc_id).last()  # type: Document

        if not doc:
            _self.log_info(f'on_locate_finished: Document does not exist: {doc.name} (#{doc.pk})\n'
                           f'Maybe it was deleted previously because of failed loading or failed entity location '
                           f'stage.')
            return
        log = CeleryTaskLogger(_self)
        user: Optional[User] = None

        try:
            Locate.save_summary_on_locate_finished(log, doc_id, locate, document_initial_load)
            user = User.objects.get(pk=doc_loaded_by_user_id) \
                if doc_loaded_by_user_id is not None \
                else User.objects.filter(id=1).first()  # type: User

            if predefined_field_codes_to_val:
                field_repo = DocumentFieldRepository()
                field_repo \
                    .store_values_one_doc_many_fields_no_ants(doc=doc,
                                                              user=user,
                                                              field_codes_to_python_values=predefined_field_codes_to_val)

                ignore_field_codes = predefined_field_codes_to_val.keys()
            else:
                ignore_field_codes = None

            if fire_doc_changed:
                signals.fire_document_changed(sender=_self,
                                              log=log,
                                              document=doc,
                                              changed_by_user=None,
                                              system_fields_changed=True,
                                              user_fields_changed=False,
                                              generic_fields_changed=True,
                                              skip_caching=True)  # caching is to be called later on
            if detect_field_values:
                detect_and_cache_field_values_for_document(
                    log=log,
                    document=doc,
                    save=True,
                    clear_old_values=True,
                    ignore_field_codes=ignore_field_codes,
                    changed_by_user=user,
                    document_initial_load=document_initial_load,
                    task=_self,
                    skip_caching=True)

            # allow notifications only for the documents which are already processed
            # disable_notifications = disable_notifications or not doc.processed

            doc.processed = True
            doc.save()

        finally:
            signals.fire_document_changed(sender=_self,
                                          log=log,
                                          document=doc,
                                          changed_by_user=user,
                                          system_fields_changed=True,
                                          user_fields_changed=True,
                                          generic_fields_changed=True,
                                          skip_caching=False)

        _self.log_info('on_locate_finished: completed')

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=6000,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3)
    def parse_text_units(self: ExtendedTask,
                         text_unit_ids,
                         user_id,
                         locate: Dict[str, Dict],
                         document_initial_load: bool,
                         selected_tags: Optional[List[str]]=None):
        from apps.document.app_vars import DOCUMENT_LOCALE
        text_units = TextUnit.objects.filter(pk__in=text_unit_ids).values_list(
            'pk', 'textunittext__text', 'language', 'document_id', 'project_id')
        location_results = LocationResults(document_initial_load=document_initial_load)
        log = CeleryTaskLogger(self)
        locators = LocatorsCollection.get_locators()
        loc_cache_key = LocatorsCollection.make_parsing_context_id()

        try:
            for task_name, task_kwargs in locate.items():
                task_kwargs['selected_tags'] = selected_tags
                if task_name not in locators:
                    raise Exception('Programming error. Unknown locator: {0}'.format(task_name))
                locator = locators[task_name]
                for text_unit_id, text, text_unit_lang, document_id, project_id in text_units:
                    # inject project_id for TermLocator to use custom Project term set
                    if task_name in {'term', 'party'}:
                        task_kwargs['project_id'] = project_id

                    locator.try_parsing(log,
                                        location_results,
                                        text,
                                        text_unit_id,
                                        DOCUMENT_LOCALE.val(project_id=project_id) or text_unit_lang,
                                        document_id,
                                        project_id,
                                        loc_cache_key,
                                        **task_kwargs)
        finally:
            LocatorsCollection.clean_parsing_context(loc_cache_key)
        location_results.save(log, user_id)

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=3600,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3)
    def notify_on_completed_complete_action(_self,
                                            project_id: int,
                                            root_task_id: str,
                                            status: str):
        locate_task: Optional[Task] = Task.objects.filter(id=root_task_id).first()
        if locate_task:
            locate_task.status = SUCCESS
            locate_task.progress = 100
            locate_task.save(update_fields=['status', 'progress'])
        data = {'task_id': root_task_id, 'task_name': 'Locate',
                'task_status': status,
                'project_id': project_id}

        users = User.get_users_for_object(
            object_pk=project_id,
            object_model=Project,
            perm_name='detect_field_values')

        if not users:
            return
        logger.info(f'Notify {users.count()} on Locate task completed')
        message = ChannelMessage(message_types.CHANNEL_MSG_TYPE_TASK_COMPLETED, data)
        Websockets().send_to_users(qs_users=users, message_obj=message)


@shared_task(base=ExtendedTask,
             bind=True,
             soft_time_limit=3600,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError),
             max_retries=3,
             priority=7)
def clean_tasks(this_task: ExtendedTask):
    all_tasks = Task.objects.exclude(id=this_task.request.id)
    executing_tasks = [t for t in all_tasks if t.status in UNREADY_STATES]
    all_tasks = [t for t in all_tasks if t.status not in UNREADY_STATES]
    executing_tasks = order_tasks_by_hierarchy(executing_tasks)
    this_task.set_push_steps(len(executing_tasks) + 3)

    if executing_tasks:
        purge_tasks(this_task, executing_tasks, True)

        # while we were purging tasks new sub tasks might have been started
        root_ids = [t.pk for t in executing_tasks]
        tasks_to_purge = []
        for _ in range(3):
            child_tasks = list(Task.objects.filter(parent_task_id__in=root_ids))
            if not child_tasks:
                break
            tasks_to_purge = child_tasks + tasks_to_purge
            root_ids = [t.pk for t in child_tasks]

        if tasks_to_purge:
            purge_tasks(this_task, tasks_to_purge, False)

    this_task.push()

    purge_tasks(this_task, all_tasks, False)
    this_task.push()

    this_task.task.date_done = now()
    this_task.task.save()


def order_tasks_by_hierarchy(tasks: List[Task]) -> List[Task]:
    # children first, parents last
    task_by_id = {t.pk: (t, 0,) for t in tasks}
    for task in tasks:
        weight = 0
        parent_id = task.parent_task_id
        while parent_id:
            weight += 1
            parent = task_by_id.get(parent_id)
            parent_id = parent[0].parent_task_id if parent else None
        task_by_id[task.pk] = (task, weight)
    tasks_weighted = [t for _, t in task_by_id.items()]
    tasks_weighted.sort(key=lambda t: t[1], reverse=True)
    return [t for t, _ in tasks_weighted]


def purge_tasks(this_task: ExtendedTask, tasks: List[Task], log_progress: bool):
    purged_pending_tasks = 0

    for task_to_purge in tasks:
        this_task.log_info('Purging: Task="{}", status="{}", date_start="{}"'.format(
            task_to_purge.name, task_to_purge.status, task_to_purge.date_start))
        try:
            purge_task(task_to_purge)
            purged_pending_tasks += 1
        except Exception as e:
            # if we were unable to purge a task - log error and proceed to the next one, don't break
            this_task.log_error(f'Unable to purge task {task_to_purge.name} (#{task_to_purge.id})', exc_info=e)
        if log_progress:
            this_task.push()

    deleted_tasks, _unused = Task.objects.filter(pk__in=[t.pk for t in tasks]).delete()

    if log_progress:
        this_task.push()

    ret = f'Purged {purged_pending_tasks} pending main tasks. Deleted {deleted_tasks} tasks after purging main tasks.'
    this_task.log_info(ret)


@app.task(base=ExtendedTask,
          name=task_names.TASK_NAME_TERMINATE_PROCESSES,
          bind=True,
          ignore_result=True,
          queue=settings.CELERY_QUEUE_WORKER_BCAST,
          exchange=settings.CELERY_EXCHANGE_WORKER_BCAST)
def terminate_processes(task: ExtendedTask,
                        target_adr: Optional[int],
                        pids: List[int]):
    log = CeleryTaskLogger(task)
    if target_adr is not None:
        own_adr = get_mac()
        if own_adr != target_adr:
            log.info(f'terminate_processes() is executing on #{own_adr}, but was targeted to #{target_adr}')
            return

    terminate_processes_by_ids(pids, log.info)


def call_terminate_processes_task(
        target_adr: Optional[int], pids: List[int]):
    call_task_func(terminate_processes,
                   (target_adr, pids,),
                   user_id=None,
                   visible=True,
                   exchange=settings.CELERY_EXCHANGE_WORKER_BCAST,
                   routing_key='*')


@app.task(name=task_names.TASK_NAME_TRACK_TASKS, bind=True, queue=settings.CELERY_QUEUE_SERIAL)
def track_tasks(_celery_task):
    TaskUtils.prepare_task_execution()

    start = time.time()

    # Running in separate cursors mostly because starting sub-tasks closes the connections

    # 1. Update all parent task statuses
    stage_start = time.time()
    with connection.cursor() as cursor:
        cursor.execute('''
update task_task t set 
    status = t0.calc_status,
    progress = t0.calc_progress
from    
    (
     select t1.id,
            task_status_to_str(t1.calc_status) as calc_status,
            round(fix_task_progress_with_status(t1.calc_progress, t1.calc_status)) as calc_progress
     from (
        select t2.id as id,
               calc_task_status(t2.id, t2.own_status, t2.has_sub_tasks) as calc_status, 
               calc_task_progress(t2.id, t2.own_progress, t2.own_status, t2.has_sub_tasks) as calc_progress
        from task_task t2
        where t2.own_status = 'REVOKED' or (t2.worker is not null and 
            (t2.status is null or t2.status in ('PENDING', 'RETRY', 'REJECTED', 'RECEIVED', 'STARTED')))
     ) as t1
    ) as t0
where t0.id = t.id and (t.status <> t0.calc_status or t.progress <> t0.calc_progress);
        ''')
    print(f'Task statuses updated for {cursor.rowcount} tasks in {time.time() - stage_start} seconds.')

    # 2. Get and start "on success" handlers
    stage_start = time.time()
    with connection.cursor() as cursor:
        cursor.execute('''
select t.id, t.name, t.metadata, t.main_task_id, t.title, t.priority
from task_task t 
where       t.run_after_sub_tasks_finished 
        and t.own_status is null 
        and not exists (select subt.id 
                        from task_task subt 
                        where       not subt.run_after_sub_tasks_finished 
                                and not subt.run_if_parent_task_failed 
                                and (   subt.parent_task_id = t.parent_task_id and subt.status <> 'SUCCESS' 
                                     or subt.id = t.parent_task_id and subt.own_status <> 'SUCCESS'
                                     )
                        );        
        ''')
        count = 0
        for task_id, name, metadata, main_task_id, title, priority in cursor.fetchall():
            run_task_finish_handler(task_id, name, title, metadata, priority)
            count += 1
        print(f'Started {count} "on success" task handlers in {time.time() - stage_start} seconds.')

    # 3. Get and start "on failure" handlers
    stage_start = time.time()
    with connection.cursor() as cursor:
        cursor.execute('''
select t.id, t.name, t.metadata, t.main_task_id, t.title, t.priority
from task_task t inner join task_task p on t.parent_task_id = p.id 
where       t.run_if_parent_task_failed 
        and t.own_status is null 
        and p.status in ('FAILURE', 'REVOKED');
                ''')
        count = 0
        for task_id, name, metadata, main_task_id, title, priority in cursor.fetchall():
            run_task_finish_handler(task_id, name, title, metadata, priority)
            count += 1
        print(f'Started {count} "on fail" task handlers in {time.time() - stage_start} seconds.')

    # 4. Delete all sub-tasks of the finished tasks
    stage_start = time.time()
    with connection.cursor() as cursor:
        cursor.execute('''
delete from task_task t 
where t.main_task_id in (select mt.id 
                         from task_task mt 
                         where mt.main_task_id is null and mt.status in ('SUCCESS', 'FAILURE', 'REVOKED')
                         );
        ''')
    print(f'Deleted {cursor.rowcount} sub-tasks of finished main tasks in {time.time() - stage_start} seconds.')

    stage_start = time.time()
    with connection.cursor() as cursor:
        cursor.execute('''update task_task set date_done = now() where 
                          date_done is null and status in ('SUCCESS', 'FAILURE', 'REVOKED');''')
    if cursor.rowcount:
        print(f'Updating {cursor.rowcount} task date_done fields took {time.time() - stage_start} seconds.')

    total_time = time.time() - start
    print(f'Task tracking procedure finished in {total_time} seconds')


def run_task_finish_handler(task_id, name, title, metadata, priority):
    options = metadata['options']
    options['task_id'] = task_id
    options['parent_id'] = None
    options['main_task_id'] = None
    options['title'] = title
    options['run_after_sub_tasks_finished'] = False
    options['run_if_parent_task_failed'] = False
    priority = priority
    queue = get_queue_by_task_priority(priority)
    task = signature(name, args=metadata['args'], **options)
    task.apply_async(priority=priority or 0, queue=queue)


@app.task(name=task_names.TASK_NAME_TRACK_FAILED_TASKS, bind=True, queue=settings.CELERY_QUEUE_SERIAL)
def track_failed_tasks(_celery_task):
    TaskMonitor.report_on_failed_tasks()


@app.task(name=task_names.TASK_NAME_CLEAN_TASKS_PERIODIC, bind=True, queue=settings.CELERY_QUEUE_SERIAL)
def clean_tasks_periodic(_celery_task):
    from apps.task.app_vars import REMOVE_READY_TASKS_DELAY_IN_HOURS

    TaskUtils.prepare_task_execution()

    del_sub_tasks_date = now() - datetime.timedelta(seconds=settings.REMOVE_SUB_TASKS_DELAY_IN_SEC)

    # Delete all completed system/periodic tasks from DB
    excluded = TaskVisibility.get_excluded_from_tracking()
    Task.objects \
        .filter(name__in=excluded, date_done__lt=del_sub_tasks_date) \
        .delete()

    # Delete excess tasks from task list
    h = REMOVE_READY_TASKS_DELAY_IN_HOURS.val()

    if h and h > 0:
        del_ready_tasks_date = now() - datetime.timedelta(hours=h)
        qr = Task.objects.filter(date_done__lt=del_ready_tasks_date)  # type: QuerySet

        if settings.TASKS_DO_NOT_REMOVE_WHEN_READY:
            qr = qr.exclude(settings.TASKS_DO_NOT_REMOVE_WHEN_READY)
        qr = qr.exclude(status=FAILURE)

        qr.delete()


@app.task(name=task_names.TASK_NAME_CLEAN_EXPORT_FILES_PERIODIC,
          bind=True, queue=settings.CELERY_QUEUE_SERIAL)
def clean_export_files_periodic(_celery_task):
    from apps.common.models import ExportFile
    now_time = datetime.datetime.utcnow()
    storage = get_file_storage()
    records = ExportFile.objects.filter(expires_at__lt=now_time)
    for record in records:  # type: ExportFile
        try:
            storage.delete_file(record.file_path)
        except Exception as e:
            logger.error(f'Error deleting file data ("{record.file_path}"): {e}')
    records.delete()


@app.task(name=task_names.TASK_NAME_MONITOR_DISK_USAGE, bind=True, queue=settings.CELERY_QUEUE_SERIAL)
def monitor_disk_usage(_celery_task):
    disk_usage_msg = check_blocks(raise_error=False)

    # exclude these already running tasks from purging
    exclude_task_names = [
        'advanced_celery.clean_tasks_periodic',
        'apps.task.tasks.clean_tasks',
        'Clean Project',
        'Clean Projects',
        'Delete Documents',
        'Cancel Upload'
    ]

    if disk_usage_msg is not False:
        logger.info(disk_usage_msg)

        executing_tasks = list(
            Task.objects
                .filter(status__in=UNREADY_STATES)
                .exclude(id=_celery_task.request.id)
                .exclude(name__in=exclude_task_names)
        )
        executing_tasks = order_tasks_by_hierarchy(executing_tasks)

        logger.info('Purge {} tasks.'.format(len(executing_tasks)))

        if not executing_tasks:
            return

        for task in executing_tasks:
            purge_task(task)


def recall_task(task_pk: str,
                session_id: Optional[str],
                user_id: int,
                log_func: Callable[[str], None] = None):
    log_func = log_func or print
    # try restarting All session tasks including the one passed
    if session_id:
        task = Task.objects.get(pk=task_pk)
        target_status = task.status if task.status == 'PENDING' else 'FAILURE'
        task_ids = find_tasks_by_session_ids(session_id, target_status)
        result = []

        for task_id in task_ids:
            result.append(recall_task(task_id, '', user_id, log_func))
        return result

    # restart specific task
    try:
        task: Task = Task.objects.get(pk=task_pk)
    except Task.DoesNotExist:
        return {'message': f"task {task_pk} wasn't found", 'status': 'success'}

    document_name = (task.metadata or {}).get('file_name')
    doc_session_id = (task.kwargs or {}).get('session_id')

    documents_to_delete: List[int] = []
    if document_name and doc_session_id:
        # don't delete the document (in fact, there can be just one) right now -
        # it might crash the task immediately
        documents_to_delete = list(Document.all_objects.filter(
            upload_session_id=doc_session_id,
            name=document_name).values_list('pk', flat=True))

    task_kwargs = task.kwargs
    task_args = task.args
    purge_task(task, log_func=log_func, delete_document_files=False)
    from celery import current_app
    if task_args:
        task_obj = current_app.tasks.get(task.name)
        task_id = _call_task_func(task_obj, task_args, user_id)
    else:
        task_kwargs = task_kwargs or {}
        if documents_to_delete:
            # allow having documents with the same name for a while until the first (empty)
            # document is deleted
            task_kwargs['do_not_check_exists'] = True
        task_obj = current_app.tasks.get(task.name)
        task_id = call_task(type(task_obj), **task_kwargs)

    if documents_to_delete:
        try:
            # prevent original doc file from being deleted in Document post_delete action
            Document.all_objects.filter(pk__in=documents_to_delete).update(source_path='')
            Document.all_objects.filter(pk__in=documents_to_delete).delete()
        except Exception as e:
            doc_ids_str = ", ".join([str(d) for d in documents_to_delete])
            log_func(f'recall_task(): error while deleting documents {doc_ids_str}: {e}')

    return {'message': f'task {task_id} started', 'status': 'success', 'task_id': task_id}


def find_tasks_by_session_ids(session_id: str,
                              status: str,
                              name_filter: str = '') -> List[str]:
    query = Task.objects.filter(
        status=status,
        kwargs__session_id=session_id)
    if name_filter:
        query = query.filter(name=name_filter)
    task_ids = list(query.values_list('pk', flat=True))
    return task_ids


def purge_task(task_pk: Union[Task, str],
               wait=False,
               timeout: Optional[int] = None,
               delete=True,
               log_func: Callable[[str], None] = None,
               delete_document_files: bool = True,
               send_signal_task_deleted: bool = True,
               user_id: int = None):
    """
    Purge task method.
    :param log_func:
    :param task_pk: Task id
    :param wait:
    :param timeout
    :param delete - bool - either delete task and its subtasks after purge
    :param delete_document_files - bool
    :param send_signal_task_deleted - bool
    :param user_id - int - user initialized this request
    :return:
    """
    log_func = log_func or logger.info

    # TODO: maybe move into separate Task.purge method ?

    status = 'success'
    task = task_pk

    if not isinstance(task, Task):
        try:
            task = Task.objects.get(pk=task)
        except Task.DoesNotExist:
            return

    task.terminate_spawned_processes('everywhere')

    task_desc = f'id={task.pk}; ' \
                f'name="{task.name}"; ' \
                f'kwargs={task.kwargs}; ' \
                f'metadata={task.metadata}; ' \
                f'date_start={task.date_start.isoformat() if task.date_start else None}; ' \
                f'date_work_start={task.date_work_start.isoformat() if task.date_work_start else None}'

    log_func(f'Task "Purge task" for app task: {task_desc}')

    if task.name == LoadDocuments.name and task.status in UNREADY_STATES:
        # TODO: Refactor this. Create a kind of on_purge() handler per task.
        # TODO: see task_deleted signal
        LoadDocuments.cancel_text_extraction(task.pk, log_func)

    for subtask in task.subtasks:
        subtask.terminate_spawned_processes('everywhere')
        subtask_celery_task = AsyncResult(subtask.id)
        revoke_task(subtask_celery_task, wait=wait, timeout=timeout)

    log_func('Celery task id={}'.format(task.id))

    main_celery_task = AsyncResult(task.id)
    revoke_task(main_celery_task, wait=wait, timeout=timeout)

    if delete:
        ret = 'Deleted '
        # delete TaskResults for subtasks
        subtask_results_deleted = task.subtasks.delete()

        # delete Task
        attempts = 3  # number of attempts
        delay = 1  # delay in seconds for the first attempt
        multiplier = 1  # multiplier to increase time between further attempts

        for attempt_n in range(1, attempts + 1):
            try:
                task.delete()
                if send_signal_task_deleted:
                    task_deleted.send('purge_task', instance=task, user_id=user_id)
                break
            # case 1. when task creates subtasks AFTER they are deleted in previous step
            except:
                if attempt_n != attempts:
                    time.sleep(delay)
                    delay *= multiplier

        ret += f'Task({task_desc}), TaskHistory, main celery task, children celery tasks, ' \
               f'{subtask_results_deleted[0] + 1} TaskResult(s)'
    else:
        ret = f'Revoked Task({task_desc})'

    log_func(ret)

    if task.name == LoadDocuments.name and task.status in UNREADY_STATES:
        # TODO: Refactor this. Create a kind of on_purge() handler per task.
        # TODO: see task_deleted signal
        if task.metadata and 'session_id' in task.metadata:
            try:
                document_ids = list(Document.objects.filter(
                    processed=False,
                    upload_session__uid=task.metadata['session_id'],
                    name=task.metadata['file_name']).values_list('pk', flat=True))
                if document_ids:
                    from apps.document.tasks import DeleteDocuments
                    _call_task(DeleteDocuments,
                               _document_ids=document_ids,
                               _delete_files=delete_document_files)
            except Exception as e:
                error_msg = 'Failed to start "DeleteDocuments" task. ' + str(e)
                log_func(error_msg)
                ret += '\n' + error_msg
                status = 'error'

    return {'message': ret, 'status': status}


@shared_task(base=ExtendedTask,
             name=task_names.TASK_NAME_TASK_HEALTH_CHECK,
             bind=True,
             queue=settings.CELERY_QUEUE_SERIAL)
def task_health_check(_celery_task):
    from apps.task.app_vars import ENABLE_TASK_HEALTH_CHECK
    if not ENABLE_TASK_HEALTH_CHECK.val():
        return

    from apps.task.task_health_check.task_health_check import check_task_health

    def _restart_task(task_pk: str):
        app.re_send_task(task_pk)
        Task.objects.filter(pk=task_pk).update(bad_health_check_num=0, run_count=0)

    check_task_health(CeleryTaskLogger(_celery_task), restart_task_func=_restart_task)


class TotalCleanup(ExtendedTask):
    """
    Remove projects, docs, sessions, clusters, etc.
    """
    name = 'Total Cleanup'

    def process(self, **kwargs):
        projects = Project.objects.all()

        self.set_push_steps(projects.count() + 2)

        # purge all tasks being executed
        app.control.purge()
        self.push()

        # delete projects one-by-one to not hang server
        for project in projects:
            project.cleanup()
            project.delete()
            self.push()

        # check that all tasks deleted EXCEPT THIS ONE
        Task.objects.exclude(pk=self.main_task_id).delete()
        self.push()


def get_call_stack_line(index: int) -> str:
    stack_lines = traceback.format_stack()
    if not stack_lines or len(stack_lines) < -index:
        return
    call_stack = stack_lines[index]
    lbr_pos = call_stack.find('\n')
    if lbr_pos:
        call_stack = call_stack[:lbr_pos]
    return call_stack


@shared_task(base=ExtendedTask, bind=True)
def debug_on_task_finished(_celery_task: ExtendedTask, arg1: str = None, deep: int = 0):
    print(f'on_debug_task_finished: {arg1}')
    # from time import sleep
    # sleep(2)


@shared_task(base=ExtendedTask, bind=True)
def debug_on_task_crash(_celery_task: ExtendedTask, arg1: str = None, deep: int = 0):
    print(f'on_debug_task_crashed: {arg1}')
    # from time import sleep
    # sleep(2)


@shared_task(base=ExtendedTask, bind=True)
def debug_sub_task(_celery_task: ExtendedTask, arg1: str = None, deep: int = 0):
    print(f'debug_sub_task: {arg1}')
    # sleep(1)
    if deep:
        args = [(str(i) + '_' + str(deep - 1), deep - 1) for i in range(1)]
        _celery_task.run_sub_tasks('debug', debug_sub_task, args)
        _celery_task.run_after_sub_tasks_finished('debug after sub-tasks finished', debug_on_task_finished, args)


@shared_task(base=ExtendedTask, bind=True)
def debug_main_task(_celery_task: ExtendedTask, arg1: str = None):
    print(f'debug_main_task: {arg1}')
    args = [(str(i), 3) for i in range(1)]
    _celery_task.run_sub_tasks('debug', debug_sub_task, args)
    _celery_task.run_after_sub_tasks_finished('debug after sub-tasks finished', debug_on_task_finished, args)
    _celery_task.run_if_task_or_sub_tasks_failed(debug_on_task_crash, args)


@shared_task(base=ExtendedTask, bind=True)
def debug_generate_error_logs(_celery_task: ExtendedTask, log_to_task_id: str, number_of_logs: int = 3000):
    task = Task.objects.get(pk=log_to_task_id)

    def crash(i):
        raise RuntimeError(f'Exception {i}')

    for i in range(number_of_logs):
        try:
            crash(i)
        except RuntimeError as e:
            task.write_log(f'Error {i}', level='error', exc_info=e)


@shared_task(base=ExtendedTask, bind=True)
def test_task_progress_single_task(_celery_task: ExtendedTask, arg1: str = None):
    _celery_task.log_info(
        f'Testing task progress. Going to change progress every 10 seconds for 1 minute.\narg1={arg1}')
    _celery_task.set_push_steps(10)
    for i in range(1, 10):
        time.sleep(10)
        _celery_task.push()
        _celery_task.log_info(f'Step {i}')
    _celery_task.log_info('Done. Bye.')


@shared_task(base=ExtendedTask, bind=True)
def test_task_progress_sub_task(_celery_task: ExtendedTask, arg1: str = None):
    _celery_task.log_info(f'Testing task progress - subtask. Sleeping 10 seconds...\narg1={arg1}')
    _celery_task.set_push_steps(10)
    time.sleep(10)


@shared_task(base=ExtendedTask, bind=True)
def test_task_progress_with_subtasks(_celery_task: ExtendedTask, arg1: str = None):
    print(f'Testing task progress - main task. Going to start 10 sub-tasks each to sleep 10 seconds...\narg1={arg1}')
    args = [(arg1,) for _i in range(1, 10)]
    _celery_task.run_sub_tasks('debug', test_task_progress_sub_task, args)


class BuildOCRRatingLanguageModel(ExtendedTask):
    """
    Build a distribution model (*.pickle file) from uploaded text file / archive file
    """
    name = task_names.TASK_NAME_BUILD_OCR_RATING_MODEL

    def process(self,
                lang: str,
                extension: str,
                source_files_archive: Dict,
                *_args, **_kwargs):
        bld = LangVectorDistributionBuilder()

        def explore_folder(folder: str, file_paths: List[str]):
            for file_name in os.listdir(folder):
                full_name = os.path.join(folder, file_name)
                if os.path.isfile(full_name):
                    _fn, ext = os.path.splitext(file_name)
                    ext = ext[1:].lower()
                    if not extension or extension == '*' or extension == ext:
                        file_paths.append(full_name)
                if os.path.isdir(full_name):
                    explore_folder(full_name, file_paths)

        def explore_archive() -> Generator[str, None, None]:
            with download_task_attached_file(source_files_archive) as fn:
                extracted_path = tempfile.mkdtemp()
                with zipfile.ZipFile(fn, 'r') as zip_ref:
                    zip_ref.extractall(extracted_path)

                file_paths = []
                explore_folder(extracted_path, file_paths)
                if not file_paths:
                    self.log_info(f'Source files not found in "{source_files_archive}"')
                    return
                self.set_push_steps(len(file_paths) + 1)

                for path in file_paths:
                    with codecs.open(path, 'r', encoding='utf-8') as fr:
                        self.push()
                        yield fr.read()
                try:
                    shutil.rmtree(extracted_path)
                except:
                    pass

        distr = bld.build_texts_reference_distribution(explore_archive())
        if distr is None:
            raise Exception('Failed to build language-specific Ngram distribution')

        mem_stream = io.BytesIO()
        distr.to_pickle(mem_stream, compression=None)
        mem_stream.seek(0)

        fstor = get_file_storage()
        try:
            fstor.mkdir(CUSTOM_LANG_STORAGE_FOLDER)
        except:
            pass

        target_stor_path = os.path.join(CUSTOM_LANG_STORAGE_FOLDER, f'{lang}.pickle')
        try:
            fstor.delete_file(target_stor_path)
        except FileNotFoundError:
            pass
        fstor.write_file(target_stor_path, mem_stream)
        self.log_info(f'File is created: {target_stor_path}')


@shared_task(base=ExtendedTask,
             name=task_names.TASK_NAME_CHECK_REINDEX_SCHEDULES,
             bind=True,
             soft_time_limit=6000)
def check_reindex_schedules(celery_task: ExtendedTask):
    # This is a recurring task that runs every minute to check the scheduled
    #   ReindexRoutine tasks.
    # Interval since trigger time to start the routine if the routine wasn't already
    # started at the same planned time (we check it in Redis)
    TRIGGER_WINDOW_SECONDS = 60 * 5

    routines: List[ReindexRoutine] = list(ReindexRoutine.objects.all())
    routines_to_run = []
    for routine in routines:
        now_time = now()
        entry = croniter.croniter(routine.schedule, now_time)
        trigger_time = entry.get_prev(datetime.datetime)
        sec_since_trigger = (now_time - trigger_time).total_seconds()
        if sec_since_trigger > TRIGGER_WINDOW_SECONDS:
            continue
        # check Redis for previous run of the routine
        redis_key = f'reindex_routine_{routine.target_entity}_{routine.index_name}_{routine.schedule}'
        last_run_time = redis.pop(redis_key)
        if last_run_time == trigger_time:
            continue
        # run (store) the routine
        redis.push(redis_key, trigger_time)
        routines_to_run.append(routine)

    if not routines_to_run:
        return
    call_task_func(reindex_db_entities,
                   ([(r.index_name, r.target_entity) for r in routines_to_run],),
                   None)


@shared_task(base=ExtendedTask,
             name=task_names.TASK_NAME_REINDEX_DB_ENTITIES,
             bind=True,
             soft_time_limit=6000)
def reindex_db_entities(celery_task: ExtendedTask,
                        routines_to_run: List[Tuple[str, str]]):
    celery_task.run_sub_tasks('Reindex DB',
                              reindex_db_entity,
                              routines_to_run)


@shared_task(base=ExtendedTask,
             name=task_names.TASK_NAME_REINDEX_DB_ENTITY,
             bind=True,
             soft_time_limit=6000)
def reindex_db_entity(celery_task: ExtendedTask,
                      index_or_table: str,
                      target_entity: str):
    with connection.cursor() as cursor:
        started = datetime.datetime.now()
        celery_task.log_info(f'Reindexing {target_entity} "{index_or_table}": started.')
        cursor.execute(f'''REINDEX {target_entity} "{index_or_table}";''')
        elapsed = (datetime.datetime.now() - started).total_seconds()
        celery_task.log_info(f'Reindexing "{index_or_table}": finished in {elapsed} seconds.')


def find_column_index(cursor, table_name: str, column_name: str, index_name_preffix: str) -> str:
    cursor.execute(f'''
        select i.relname as index_name
        from
            pg_class t, pg_class i, pg_index ix, pg_attribute a
        where
            t.oid = ix.indrelid
            and i.oid = ix.indexrelid
            and a.attrelid = t.oid
            and a.attnum = ANY(ix.indkey)
            and t.relkind = 'r'
            and t.relname = %s
            and a.attname = %s
            and i.relname like '{index_name_preffix}%%';
        ''', (table_name, column_name,))
    for row in cursor.fetchall():
        return row[0]
    return ''


# Register all load tasks
app.register_task(LoadDocuments())
app.register_task(CreateDocument())
app.register_task(LoadTerms())
app.register_task(LoadGeoEntities())
app.register_task(LoadCourts())

# Register all locate tasks
app.register_task(Locate())

# Register all update/cluster/classify tasks
app.register_task(TotalCleanup())
app.register_task(BuildOCRRatingLanguageModel())
