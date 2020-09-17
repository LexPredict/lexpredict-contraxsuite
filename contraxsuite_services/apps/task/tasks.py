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
import datetime
import hashlib
import importlib
import json
import mimetypes
import os
import string
import sys
import tempfile
import threading
import time
import traceback
from inspect import isclass
from typing import List, Dict, Tuple, Any, Callable, Optional

# Third-party imports
import magic
import nltk
import pandas as pd
import pycountry
import regex as re
from celery import shared_task, signature
from celery.canvas import Signature
from celery.exceptions import SoftTimeLimitExceeded, Retry
from celery.result import AsyncResult
from celery.states import FAILURE, UNREADY_STATES
from celery.utils.log import get_task_logger
from celery.utils.time import get_exponential_backoff_interval
# Django imports
from django.conf import settings
from django.db import transaction, connection, IntegrityError
from django.db.models import QuerySet
from django.utils.timezone import now
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
from lexnlp.extract.common.text_beautifier import TextBeautifier
from lexnlp.extract.en.contracts.detector import is_contract
from lexnlp.nlp.en.segments.paragraphs import get_paragraphs
from lexnlp.nlp.en.segments.sections import get_section_spans
from lexnlp.nlp.en.segments.sentences import get_sentence_span_list, pre_process_document
from lexnlp.nlp.en.segments.titles import get_titles
from psycopg2 import InterfaceError, OperationalError
from uuid import getnode as get_mac

# Project imports
import task_names
from apps.celery import app
from apps.common.archive_file import ArchiveFile
from apps.common.errors import find_cause_of_type
from apps.common.file_storage import get_file_storage
from apps.common.log_utils import ProcessLogger
from apps.common.processes import terminate_processes_by_ids
from apps.common.utils import fast_uuid
from apps.deployment.app_data import load_geo_entities, load_terms, load_courts
from apps.document import signals
from apps.document.constants import DOCUMENT_TYPE_PK_GENERIC_DOCUMENT, \
    DOC_METADATA_DOCUMENT_CLASS_PROB, DOCUMENT_FIELD_CODE_CLASS
from apps.document.document_class import DocumentClass
from apps.document.field_detection.field_detection import detect_and_cache_field_values_for_document
from apps.document.models import (
    Document, DocumentText, DocumentMetadata, DocumentProperty, DocumentType,
    TextUnit, TextUnitTag, DocumentTable, TextUnitText, DocumentPage)
from apps.document.repository.document_field_repository import DocumentFieldRepository
from apps.document.sync_tasks.document_files_cleaner import DocumentFilesCleaner
from apps.extract import dict_data_cache
from apps.extract import models as extract_models
from apps.extract.locators import LocatorsCollection, LocationResults
from apps.extract.locators import request_mat_views_refresh
from apps.extract.models import Court, GeoAlias, GeoEntity, GeoRelation, Term
from apps.project.models import Project, UploadSession
from apps.task.celery_backend.task_utils import revoke_task
from apps.task.models import Task, TaskConfig
from apps.task.parsing_tasks import ParsingTaskParams, XmlWordxDocumentParser, \
    TikaDocumentParser, TextractDocumentParser, PlainTextDocumentParser, DocumentParsingResults
from apps.task.task_monitor import TaskMonitor
from apps.task.task_visibility import TaskVisibility
from apps.task.utils.marked_up_text import MarkedUpText
from apps.task.utils.nlp.heading_heuristics import HeadingHeuristics
from apps.task.utils.nlp.lang import get_language
from apps.task.utils.nlp.parsed_text_corrector import ParsedTextCorrector
from apps.task.utils.task_utils import TaskUtils, pre_serialize, check_blocks, check_blocks_decorator
from apps.task.utils.text_extraction.pdf_tools import pdf_has_images
from apps.task.utils.text_extraction.pdf2pdfa import pdf2pdfa
from apps.users.models import User
from contraxsuite_logging import write_task_log

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


file_storage = get_file_storage()

# Logger setup
this_module = sys.modules[__name__]
logger = get_task_logger(__name__)

# singularizer
wnl = nltk.stem.WordNetLemmatizer()

# TODO: Configuration-based and language-based punctuation.
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

python_magic = magic.Magic(mime=True)

es = Elasticsearch(hosts=settings.ELASTICSEARCH_CONFIG['hosts'])

REG_EXTRA_SPACE = re.compile(r'<[\s/]*(?:[A-Za-z]+|[Hh]\d)[\s/]*>|\x00')


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
    return 'high_priority' if priority > 7 else 'default'


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cached_data = None
        self._log_kwargs = None  # type: Optional[Dict[str, Any]]

    def run(self, *args, **kwargs):
        run_count = Task.objects.increase_run_count(self.request.id)
        if hasattr(self, 'max_retries') and self.max_retries is not None and run_count > self.max_retries:
            raise RuntimeError(
                'Exceeded maximum number of retries ({})'.format(self.max_retries))
        self.log_info(f'Start task "{self.task_name}", id={self.main_task_id}, ' +
                      f'run_count={run_count}\nKwargs: {str(kwargs)}')
        if '_log_extra' in kwargs:
            self._log_kwargs = kwargs['_log_extra']
        try:
            ret = self.process(**kwargs)
        finally:
            self.log_info(f'End of main task "{0}", id={1}. '
                          'Sub-tasks may be still running.'.format(self.task_name,
                                                                   self.main_task_id))
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
        if not self._cached_data:
            this_task = Task.objects.get(id=self.request.id)
            self._cached_data = dict()
            self._cached_data['task'] = this_task
            self._cached_data['main_task_id'] = this_task.main_task_id

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
        this_task.save(update_fields=['own_progress'])

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
                    call_stack=call_stack)
        task.save()
        self.task.has_sub_tasks = True
        self.task.save(update_fields=['has_sub_tasks'])

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
                failure_reported=False
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
                      countdown: int = None):
        """
        Asynchronously execute sub_task_method on each tuple of arguments from the provided list.

        :param sub_tasks_group_title:
        :param sub_task_function:
        :param args_list:
        :param source_data:
        :param countdown: Delay in seconds before running the sub-tasks.
        :return:
        """
        if not args_list:
            return
        priority = get_task_priority(sub_task_function)
        sub_tasks = []
        task_config = _get_or_create_task_config(sub_task_function)
        for index, args in enumerate(args_list):
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

        queue = sub_task_function.queue if hasattr(sub_task_function, 'queue') \
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
                    caller_task: Optional[ExtendedTask] = None):
    celery_task_id = str(fast_uuid())
    priority = get_task_priority(task_func)
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
        queue = task_class_resolved.queue \
            if hasattr(task_class_resolved, 'queue') \
            else get_queue_by_task_priority(priority)

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
    document_name = os.path.basename(file_name)
    document_source = os.path.dirname(file_name)

    document_ids = list(
        Document.objects
            .filter(name=document_name, source=document_source)
            .values_list('pk', flat=True))

    if document_ids:
        task.log_error(f'Loading documents task failed, deleting documents: {file_name} (ids: {document_ids})')

        try:
            from apps.document.tasks import DeleteDocuments
            del_task = DeleteDocuments()
            del_task.process(_document_ids=document_ids)
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
    queue = 'doc_load'

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

        load_docs_args = [{'uri': file_path, 'task_kwargs': kwargs} for file_path in file_list]

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
                 max_retries=3,
                 queue='doc_load')
    def create_document_from_bytes(task: ExtendedTask,
                                   doc_bytes: bytes,
                                   file_name: str,
                                   kwargs):
        with tempfile.NamedTemporaryFile() as fw:
            fw.write(doc_bytes)
            return LoadDocuments.create_document_local(
                task, fw.name, file_name, kwargs)

    # FIXME: this becomes unuseful as we CANNOT subclass from LoadDocument now - it hasn't self in methods!!!
    @staticmethod
    def save_extra_document_data(**kwargs):
        pass

    @staticmethod
    def get_title(text):
        titles = list(get_titles(text))
        return titles[0] if titles else None

    @staticmethod
    def create_document_local(task: ExtendedTask,
                              file_path,
                              file_name,
                              kwargs,
                              return_doc_id: bool = False,
                              pre_defined_doc_fields_code_to_val: Dict[str, Any] = None):
        task.task.title = 'Load Document: {0}'.format(file_name)
        task.log_extra = {Document.LOG_FIELD_DOC_NAME: file_name}

        ret = []
        document_name = os.path.basename(file_name)
        document_source = os.path.dirname(file_name)
        file_size = kwargs.get('file_size') or os.path.getsize(file_path)
        upload_session_id = kwargs['metadata'].get('session_id')
        should_run_standard_locators = bool(kwargs.get('run_standard_locators'))
        user_id = kwargs.get('user_id')
        project_id = kwargs.get('project_id')
        assignee_id = kwargs.get('assignee_id')
        document_type_id = kwargs.get('document_type_id')
        do_not_check_exists = bool(kwargs.get('do_not_check_exists'))

        # OLD API: Check for existing record
        if not do_not_check_exists and upload_session_id is None:
            document_id = Document.objects \
                .filter(name=document_name, source=document_source) \
                .values_list('pk', flat=True) \
                .first()
            if document_id:
                task.log_info('SKIP (EXISTS): ' + file_name)
                return document_id if return_doc_id else {'document_id': document_id}

        # get plain text and metadata from file
        propagate_exceptions = kwargs.get('propagate_exception')
        task.task.update_progress(10)  # document's just uploaded
        started = datetime.datetime.now()
        pars_results = None

        # try to convert PDF to searchable PDF-A
        ext, _ = LoadDocuments.get_file_extension(file_name, file_path)
        alt_source_path = None
        if ext == '.pdf':
            alt_source_path = LoadDocuments.convert_pdf2pdfa(task=task,
                                                             local_file_path=file_path,
                                                             source_path=file_name)
            if isinstance(alt_source_path, str):
                from apps.task.app_vars import USE_PDF2PDFA_CONVERTER_RESULT
                if USE_PDF2PDFA_CONVERTER_RESULT.val is True:
                    task.log_info(f'Use new-generated PDF-A "{alt_source_path}" content further')
                    with file_storage.get_document_as_local_fn(alt_source_path) as (local_fp, _):
                        pars_results = LoadDocuments.get_text_from_file(
                            file_name, local_fp, propagate_exceptions, task, ocr_enabled=False)

        if pars_results is None or pars_results.is_empty():
            pars_results = LoadDocuments.get_text_from_file(
                file_name, file_path, propagate_exceptions, task)

        elapsed = (datetime.datetime.now() - started).total_seconds()

        # do reconnect - postgres may have already closed the connection because of long-running OCR
        # WARN: this should be BEFORE any other interactions with DB
        # because DB connection may be already closed due to too long session
        if elapsed > 30:
            TaskUtils.prepare_task_execution()

        task.task.update_progress(40)  # document's just uploaded + parsed

        metadata = pars_results.metadata or {}
        parse_stat = metadata.get(Document.DocumentMetadataKey.KEY_PARSING_STATISTICS) or {}
        parse_stat['parser'] = pars_results.parser
        parser_name = pars_results.parser

        if pars_results.is_empty():
            # delete document source file
            DocumentFilesCleaner.delete_document_files([file_name])
            raise RuntimeError('No text extracted.')

            # if propagate_exceptions:
            #     raise RuntimeError('No text extracted.')
            # task.log_info('SKIP (ERROR): ' + file_name)
            # return None

        # remove extra line breaks
        old_len = len(pars_results.text.text)
        LoadDocuments.preprocess_parsed_text(pars_results)
        delta = len(pars_results.text.text) - old_len
        if delta != 0:
            task.log_info(f'After preprocessing text length has changed from {old_len} to {old_len + delta}')
        # remove markers and create labels
        pars_results.text.convert_markers_to_labels()

        if metadata is None:
            metadata = {}
        else:
            # INFO: postgresql crashes to store \x00 (\u0000) in json with message:
            # DataError: unsupported Unicode escape sequence
            # DETAIL:  \u0000 cannot be converted to text.
            metadata = json.loads(json.dumps(metadata).replace('\\u0000', ''))

        metadata['parsed_by'] = parser_name
        extra_metadata = kwargs.get('extra_metadata')
        if extra_metadata:
            metadata = {**metadata, **extra_metadata}

        # detect if document is contract (do detect by default)
        detect_contract = kwargs.get('detect_contract')
        if detect_contract is None:
            from apps.document.app_vars import DETECT_CONTRACT
            detect_contract = DETECT_CONTRACT.val
        if detect_contract:
            LoadDocuments.classify_document(metadata, pars_results, task)

        # Language identification
        if pars_results.text and pars_results.text.text:
            task.log_info(f'Document text length: {len(pars_results.text.text)}')
        language, lang_detector = get_language(pars_results.text.text, get_parser=True)
        if language:
            task.log_info('Detected language: %s' % language.upper())
            task.log_info('Language detector: %s' % lang_detector.upper())
        else:
            task.log_info('LANGUAGE IS NOT DETECTED: ' + file_name)

        # detect title
        title = metadata.get('title', None) or LoadDocuments.get_title(pars_results.text.text)
        task.log_info(f'Title detected as {title}')

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
                alt_source_path=alt_source_path if isinstance(alt_source_path, str) else None,
                language=language,
                title=title,
                file_size=file_size,
                folder=kwargs.get('directory_path'),
                document_class=metadata.get(DOCUMENT_FIELD_CODE_CLASS) or DocumentClass.GENERIC)
            DocumentText.objects.create(document=document, full_text=pars_results.text.text)
            DocumentMetadata.objects.create(document=document, metadata=metadata)

            task.log_extra[Document.LOG_FIELD_DOC_ID] = str(document.pk)

            # create Document Properties
            document_properties = [
                DocumentProperty(
                    created_by_id=user_id,
                    modified_by_id=user_id,
                    document_id=document.pk,
                    key=k,
                    value=v) for k, v in metadata.items() if v]
            DocumentProperty.objects.bulk_create(document_properties)

            # create text units
            paragraph_list = []  # type: List[TextUnit]

            # for now we ignore paragraphs obtained from parser
            task.log_info('Getting paragraphs...')
            paragraphs = LoadDocuments.safely_get_paragraphs(pars_results.text.text)
            for paragraph, pos_start, post_end in paragraphs:
                if not paragraph:
                    task.log_error(f'Paragraph text is null:\n'
                                   f'Document: {document.name} (#{document.pk})\n'
                                   f'Location: {pos_start} - {post_end}')
                ptr = TextUnit(
                    document=document,
                    unit_type="paragraph",
                    location_start=pos_start,
                    location_end=post_end,
                    project=document.project)
                ptr.language = get_language(paragraph)
                ptr.text_hash = hashlib.sha1(paragraph.encode("utf-8")).hexdigest()
                paragraph_list.append(ptr)

            paragraph_tu_objects = TextUnit.objects.bulk_create(paragraph_list)

            paragraph_text_list = []  # type: List[TextUnitText]
            for text_unit, paragraph_data in zip(paragraph_tu_objects, paragraphs):
                if not paragraph_data[0]:
                    task.log_error(f'Paragraph text is null:\n'
                                   f'Document: {document.name} (#{document.pk})\n'
                                   f'Location: {pos_start} - {post_end}')
                tu_text_obj = TextUnitText(
                    text_unit=text_unit,
                    text=paragraph_data[0]
                )
                paragraph_text_list.append(tu_text_obj)

            TextUnitText.objects.bulk_create(paragraph_text_list)

            sentence_list = []
            task.log_info('Getting sentences...')
            sentence_spans = get_sentence_span_list(pars_results.text.text)
            for span in sentence_spans:
                sentence = pars_results.text.text[span[0]:span[1]]
                text_unit = TextUnit(
                    document=document,
                    location_start=span[0],
                    location_end=span[1],
                    text_hash=hashlib.sha1(sentence.encode("utf-8")).hexdigest(),
                    unit_type="sentence",
                    language=get_language(sentence),
                    project=document.project)
                sentence_list.append(text_unit)

            sentence_tu_objects = TextUnit.objects.bulk_create(sentence_list)

            sentence_text_list = []  # type: List[TextUnitText]
            for text_unit, span in zip(sentence_tu_objects, sentence_spans):
                sentence = pars_results.text.text[span[0]:span[1]]
                tu_text_obj = TextUnitText(
                    text_unit=text_unit,
                    text=sentence
                )
                sentence_text_list.append(tu_text_obj)

            TextUnitText.objects.bulk_create(sentence_text_list)

            document.paragraphs = len(paragraph_list)
            document.sentences = len(sentence_list)
            document.save()

            LoadDocuments.save_document_pages(pars_results.text, document.pk)

            # detect sections
            task.log_info('Getting sections...')
            LoadDocuments.find_document_sections(metadata, pars_results, sentence_list)

            if pars_results.tables:
                doc_tables = []
                for table in pars_results.tables:
                    doc_table = DocumentTable(document=document, table=table)
                    doc_tables.append(doc_table)
                DocumentTable.objects.bulk_create(doc_tables)

            # store document language
            if not document.language:
                document.set_language_from_text_units()

            # save extra document info
            kwargs['document'] = document

        LoadDocuments.save_extra_document_data(**kwargs)

        task.log_info(message=f'LOADED ({parser_name.upper()}): {file_name}, {len(pars_results.text.text)} chars')
        task.log_info(message='Document pk: %d' % document.pk)

        # call post processing task
        linked_tasks = kwargs.get('linked_tasks') or list()  # type: List[Dict[str, Any]]

        if should_run_standard_locators:
            from apps.extract.app_vars import STANDARD_LOCATORS

            task.run_sub_tasks_class_based('Locate', Locate, [{
                'locate': list(set(STANDARD_LOCATORS.val + ['term'])),
                'parse': ['sentence'],
                'do_delete': False,
                'session_id': upload_session_id,
                'metadata': {'session_id': upload_session_id, 'file_name': file_name},
                'user_id': user_id,
                'document_id': document.pk,
                'doc_loaded_by_user_id': user_id,
                'document_initial_load': True,
                'predefined_field_codes_to_python_values': pre_defined_doc_fields_code_to_val
            }])
        else:
            if pre_defined_doc_fields_code_to_val:
                user = User.objects.get(pk=user_id) if user_id is not None else None
                field_repo = DocumentFieldRepository()
                field_repo \
                    .store_values_one_doc_many_fields_no_ants(doc=document,
                                                              field_codes_to_python_values=pre_defined_doc_fields_code_to_val,
                                                              user=user)

        for linked_task_kwargs in linked_tasks:
            linked_task_kwargs['document_id'] = document.pk
            linked_task_kwargs['source_data'] = task.task.source_data
            linked_task_id = call_task(**linked_task_kwargs)
            task.log_info(message='linked_task_id: {}'.format(linked_task_id))
            ret.append({'linked_task_id': linked_task_id,
                        'document_id': document.pk})

        # set status to avoid duplicates during uploading
        document.documentmetadata.metadata['upload_status'] = 'DONE'
        document.documentmetadata.save()

        if return_doc_id:
            return document.pk
        else:
            return json.dumps(ret) if ret else None

    @staticmethod
    def convert_pdf2pdfa(task, local_file_path, source_path, language='eng',
                         fail_silently=True, force=False, override_existing=False):
        """
        Check a file is PDF with images, save it as PDF-A (searchable PDF)
        :param task - Task
        :param local_file_path: str - local file path
        :param source_path: str - storage rel file path like /{session_uid}/filename.ext
        :param language: str - 2-3-chars lang name
        :param fail_silently: bool - fail without exception
        :param force: bool - process even if app vars disable process
        :param override_existing: bool - overwrite existing alternative file
        :return: None - if failed silently,
                 False - if processing is disabled,
                 True - if nothing converted (no images detected)
                 str - else new file path if converted
        """
        from apps.task.app_vars import USE_PDF2PDFA_CONVERTER
        from apps.document.app_vars import OCR_ENABLE

        do_convert = force or (OCR_ENABLE.val and USE_PDF2PDFA_CONVERTER.val)
        if not do_convert:
            task.log_warn('Generation PDF-A disabled')
            return False

        # skip if no images detected; suppose images exist by default
        try:
            has_images = pdf_has_images(file_path=local_file_path,
                                        task=task.task,
                                        logger=CeleryTaskLogger(task),
                                        timeout=300)
        except:
            has_images = True

        if has_images is False:
            task.log_warn('Skip Generation PDF-A, no images detected')
            return True

        task.log_info('Convert PDF to PDF-A')

        # convert 2-chars lang to 3-chars; suppose "eng" by default
        if len(language) == 2:
            try:
                language = pycountry.languages.get(alpha_2=language).alpha_3
            except AttributeError:
                language = 'eng'

        output_tmp_file_path = local_file_path + '.alt'
        alt_source_path = source_path + '.alt'
        try:
            from apps.task.app_vars import PDF2PDFA_CONVERTER_TIMEOUT
            pdf2pdfa(task=task.task,
                     input_file_path=local_file_path,
                     output_file_path=output_tmp_file_path,
                     language=language,
                     logger=CeleryTaskLogger(task),
                     timeout=PDF2PDFA_CONVERTER_TIMEOUT.val)
        except Exception as e:
            if fail_silently:
                task.log_warn('Failed to generate PDF-A')
                return None
            raise e

        # save generated pdf
        if override_existing or not file_storage.document_exists(alt_source_path):
            contents = open(output_tmp_file_path, 'rb').read()
            file_size = len(contents)
            file_storage.write_document(rel_file_path=alt_source_path,
                                        contents_file_like_object=contents,
                                        content_length=file_size)
            if os.path.exists(output_tmp_file_path):
                os.remove(output_tmp_file_path)

        return alt_source_path

    @staticmethod
    def save_document_pages(text: MarkedUpText,
                            doc_id: int):
        if 'pages' not in text.labels:
            return
        pages = text.labels['pages']
        if not pages:
            return

        doc_pages = []  # type: List[DocumentPage]
        for i in range(len(pages)):
            page = DocumentPage()
            page.document_id = doc_id
            page.number = i + 1
            page.location_start = pages[i][0]
            page.location_end = pages[i][1]
            doc_pages.append(page)

        DocumentPage.objects.bulk_create(doc_pages)

    @staticmethod
    def classify_document(metadata: Dict[str, Any],
                          pars_results: DocumentParsingResults,
                          task):
        try:
            res = is_contract(pars_results.text.text, return_probability=True)
            if res is not None:
                metadata[DOCUMENT_FIELD_CODE_CLASS] = \
                    DocumentClass.CONTRACT if res[0] else DocumentClass.GENERIC
                metadata[DOC_METADATA_DOCUMENT_CLASS_PROB] = [res[1]]
        except ImportError:
            task.log_warn('Cannot import lexnlp.extract.en.contracts.detector.is_contract')

    @staticmethod
    def find_document_sections(metadata, pars_results, sentence_list):

        sections = [s.to_dict() for s in pars_results.text.find_sections()]
        if not sections:
            sections = list(get_section_spans(pars_results.text.text,
                                              use_ml=False, return_text=False,
                                              skip_empty_headers=True))
            LoadDocuments.find_section_titles(sections, sentence_list,
                                              pars_results.text.text)
        metadata['sections'] = sections

    @staticmethod
    def find_section_titles(sections: List[Dict[str, Any]],
                            sentences: List[TextUnit],
                            full_text: str) -> None:
        """
        Methods tries to pick section titles as first sentences of
        referenced paragraphs

        :param sections: # [{'start': 460, 'end': 1283, 'title': 'A', 'title_start': 517, 'title_end': 518, 'level': 2..
        :param paragraphs: TextUnits - paragraphs of the document
        :param sentences: TextUnits - sentences of the document
        """
        if not sections:
            return
        sections.sort(key=lambda s: s['start'])
        sentences.sort(key=lambda t: t.location_start)
        sent_index = 0
        for section in sections:
            possible_title = ''
            for i in range(sent_index, len(sentences)):
                sent_index = i
                if section['start'] > sentences[i].location_end:
                    continue
                if section['start'] < sentences[i].location_start and \
                        section['end'] < sentences[i].location_start:
                    break
                possible_title = full_text[sentences[i].location_start: sentences[i].location_end]
                break
            if not possible_title:
                continue

            possible_title = possible_title.strip()
            sect_title = section['title'].strip()
            # choose title that looks better
            new_title = HeadingHeuristics.get_better_title(sect_title, possible_title)
            section['title'] = new_title

    @staticmethod
    def get_text_from_file(file_name: str,
                           file_path: str,
                           propagate_exceptions: bool,
                           task: ExtendedTask,
                           ocr_enabled: bool = None) -> DocumentParsingResults:
        """
        extract text from file using either Tika or Textract
        """
        from apps.document.app_vars import OCR_ENABLE, OCR_FILE_SIZE_LIMIT, \
            MSWORD_TO_TEXT_ENABLE, MIN_NOT_PLAIN_FILE_SIZE
        ocr_enabled = OCR_ENABLE.val if ocr_enabled is None else ocr_enabled

        # disable OCR anyway if file size exceeds limit
        fsize_bytes = os.path.getsize(file_path)
        if ocr_enabled:
            fsize_limit = OCR_FILE_SIZE_LIMIT.val
            fsize = fsize_bytes / 1024 / 1024
            ocr_enabled = ocr_enabled and fsize <= fsize_limit
        extracting_enabled = fsize_bytes > MIN_NOT_PLAIN_FILE_SIZE.val

        ext, file_type = LoadDocuments.get_file_extension(file_name, file_path)
        if file_type == 'ARCHIVE':
            raise Exception(f'File "{file_name}" ({file_path}) is archive. Archive inside '
                            'archives are not supported.')

        parse_ptrs = ParsingTaskParams(CeleryTaskLogger(task),
                                       file_path,
                                       ext,
                                       file_name,
                                       task.task,
                                       propagate_exceptions,
                                       ocr_enabled)

        # decide can we parse the file with Textract
        word_parse_enabled = MSWORD_TO_TEXT_ENABLE.val and extracting_enabled
        textract_enabled = (ocr_enabled or
                            ext in settings.TEXTRACT_NON_OCR_EXTENSIONS) \
                           and extracting_enabled
        tika_enabled = extracting_enabled

        if settings.TEXTRACT_FIRST_FOR_EXTENSIONS:
            parse_functions = [PlainTextDocumentParser(),
                               XmlWordxDocumentParser() if word_parse_enabled else None,
                               TextractDocumentParser() if textract_enabled else None,
                               TikaDocumentParser() if tika_enabled else None]
        else:
            parse_functions = [PlainTextDocumentParser(),
                               XmlWordxDocumentParser() if word_parse_enabled else None,
                               TikaDocumentParser() if tika_enabled else None,
                               TextractDocumentParser() if textract_enabled else None]

        results = None
        for parsr in parse_functions:
            if not parsr:
                continue
            try:
                results = parsr.try_parse_document(parse_ptrs)
            except Exception as e:
                parser_name = parsr.__class__.__name__
                raise RuntimeError(f'Error parsing {file_name} ({file_path}) by {parser_name}') from e
            if not results.is_empty():
                break

        if results and not results.is_empty():
            # TODO: migrate it in lexnlp if it works good
            results.text.text = pre_process_document(results.text.text)
            results.text.replace_by_regex(REG_EXTRA_SPACE, '')
            results.text.replace_by_string('\r\n', '\n')
        return results

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
    def preprocess_parsed_text(pars_result: DocumentParsingResults):
        from apps.document.app_vars import PREPROCESS_DOCTEXT_LINEBREAKS, PREPROCESS_DOCTEXT_PUNCT
        if PREPROCESS_DOCTEXT_LINEBREAKS.val:
            # fix extra line breaks
            corrector = ParsedTextCorrector()
            transformations = []
            pars_result.text.text = corrector.correct_if_corrupted(
                pars_result.text.text, transformations=transformations)
            if transformations:
                pars_result.text.apply_transformations(transformations)
        if PREPROCESS_DOCTEXT_PUNCT.val:
            pars_result.text.text = TextBeautifier.unify_quotes_braces(pars_result.text.text)

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
    queue = 'doc_load'
    name = 'Create Document'

    def process(self, uri: str, task_kwargs, *args, **kwargs):
        task_id = self.task.pk if self.task else '-'
        self.log_info(f'CreateDocument("{uri}"), task id #{task_id}')
        with file_storage.get_document_as_local_fn(uri) as (fn, file_name):
            self.run_if_task_or_sub_tasks_failed(delete_document_on_load_failed, args=(uri, task_kwargs))
            return LoadDocuments.create_document_local(self, fn, uri, task_kwargs)


class UpdateElasticsearchIndex(ExtendedTask):
    """
    Update Elasticsearch Index: each time after new documents are added
    """
    name = 'Update Elasticsearch Index'

    def elastic_index(self, es: Elasticsearch, tu: TextUnit):
        es_doc = {
            'pk': tu.pk,
            'text': tu.textunittext.text,
            'document': tu.document.pk,
            'unit_type': tu.unit_type,
            'language': tu.language,
            'text_hash': tu.text_hash
        }
        es.index(index=settings.ELASTICSEARCH_CONFIG['index'], doc_type='text_unit', id=tu.pk,
                 body=es_doc)

    def process(self, **kwargs):
        self.set_push_steps(1)
        es = Elasticsearch(hosts=settings.ELASTICSEARCH_CONFIG['hosts'])

        es_index = settings.ELASTICSEARCH_CONFIG['index']

        try:
            es.indices.create(index=es_index)
            self.log_info('Created index: {0}'.format(es_index))
        except RequestError:
            self.log_info('Index already exists: {0}'.format(es_index))

        count = 0
        for tu in TextUnit.objects.iterator():
            self.elastic_index(es, tu)
            count += 1
            if count % 100 == 0:
                self.log_info('Indexing text units: {0} done'.format(count))
        self.log_info('Finished indexing text units. Refreshing ES index.')
        es.indices.refresh(index=es_index)
        self.log_info('Done')
        self.push()


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

        if kwargs['delete']:
            Term.objects.all().delete()

        terms_df = pd.DataFrame()
        for path in repo_paths:
            terms_df = self.load_terms_from_path(path, None, terms_df)

        if file_path:
            with file_storage.get_as_local_fn(file_path) as (fn, file_name):
                terms_df = self.load_terms_from_path(fn, file_name, terms_df)

        self.push()

        # terms should be cached here
        terms_count = load_terms(terms_df)
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

        geo_aliases_count, geo_entities_count = load_geo_entities(entities_df,
                                                                  lambda progress: self.set_total_progress(progress),
                                                                  lambda: self.push())

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
                        text_unit__document__project_id=project_id)

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
        available_locators = set(STANDARD_LOCATORS.val) | set(OPTIONAL_LOCATORS.val)

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
            locate_args = [[text_unit_ids[i:i + package_size], kwargs['user_id'], locate, document_initial_load]
                           for i in range(0, len(text_unit_ids), package_size)]
            self.run_sub_tasks('Locate Data In Each Text Unit', Locate.parse_text_units, locate_args)

        if document_id:
            document_ids = [document_id]
        elif project_id:
            document_ids = Document.objects.filter(
                project_id=project_id).values_list('pk', flat=True)
        else:
            return
        detect_field_values = kwargs.get('detect_field_values', True)
        fire_doc_changed = kwargs.get('fire_doc_changed', True)
        cache_field_values = kwargs.get('cache_field_values', False)

        for document_id in document_ids:
            # otherwise run_after_sub_tasks_finished doesn't work if no subtasks
            # TODO: investigate and fix base methods like run_after_sub_tasks_finished
            if not text_unit_ids:
                self.run_sub_tasks('Cache Generic Document Data',
                                   Locate.on_locate_finished,
                                   [(document_id,
                                     doc_loaded_by_user_id,
                                     document_initial_load,
                                     predefined_field_codes_to_python_values,
                                     locate,
                                     detect_field_values,
                                     fire_doc_changed,
                                     cache_field_values,
                                     True)])
            else:
                self.run_after_sub_tasks_finished(
                    'Cache Generic Document Data',
                    Locate.on_locate_finished,
                    [(document_id,
                      doc_loaded_by_user_id,
                      document_initial_load,
                      predefined_field_codes_to_python_values,
                      locate,
                      detect_field_values,
                      fire_doc_changed,
                      cache_field_values,
                      True)])

    @staticmethod
    def save_summary_on_locate_finished(log: ProcessLogger, doc_id: int, locate: Dict[str, Dict],
                                        document_initial_load: bool = False):
        request_mat_views_refresh()
        locators = LocatorsCollection.get_locators()

        for locator_name in locate.keys():
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
                 priority=9)
    def on_locate_finished(_self: ExtendedTask,
                           doc_id: int,
                           doc_loaded_by_user_id: Optional[int],
                           document_initial_load: bool,
                           predefined_field_codes_to_val: Optional[Dict[str, Any]] = None,
                           locate: Optional[Dict[str, Dict]] = None,
                           detect_field_values: bool = True,
                           fire_doc_changed: bool = True,
                           cache_field_values: bool = False,
                           disable_notifications: bool = False):
        doc = Document.all_objects.filter(pk=doc_id).last()  # type: Document

        if not doc:
            _self.log_info(f'on_locate_finished: Document does not exist: {doc.name} (#{doc.pk})\n'
                           f'Maybe it was deleted previously because of failed loading or failed entity location '
                           f'stage.')
            return

        log = CeleryTaskLogger(_self)

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
                                          generic_fields_changed=True)
        if detect_field_values:
            detect_and_cache_field_values_for_document(
                log=log,
                document=doc,
                save=True,
                clear_old_values=True,
                ignore_field_codes=ignore_field_codes,
                changed_by_user=user,
                document_initial_load=document_initial_load)

        # allow notifications only for the documents which are already processed
        disable_notifications = disable_notifications or not doc.processed

        doc.processed = True
        doc.save()

        if detect_field_values:
            from apps.rawdb.field_value_tables import cache_document_fields, FIELD_CODE_DOC_PROCESSED
            cache_document_fields(log=log,
                                  document=doc,
                                  cache_system_fields=[FIELD_CODE_DOC_PROCESSED],
                                  cache_generic_fields=False,
                                  cache_user_fields=False,
                                  changed_by_user=user,
                                  disable_notifications=disable_notifications)
        elif cache_field_values:
            from apps.rawdb.field_value_tables import cache_document_fields, FIELD_CODE_DOC_PROCESSED
            cache_document_fields(log=log,
                                  document=doc,
                                  cache_system_fields=True,
                                  cache_generic_fields=True,
                                  cache_user_fields=True,
                                  changed_by_user=user,
                                  disable_notifications=disable_notifications)

        _self.log_info('on_locate_finished: completed')

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=6000,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3
                 )
    def parse_text_units(self: ExtendedTask, text_unit_ids, user_id, locate: Dict[str, Dict],
                         document_initial_load: bool):
        text_units = TextUnit.objects.filter(pk__in=text_unit_ids).values_list(
            'pk', 'textunittext__text', 'language', 'document_id', 'document__project_id')
        location_results = LocationResults(document_initial_load=document_initial_load)
        log = CeleryTaskLogger(self)
        locators = LocatorsCollection.get_locators()

        for task_name, task_kwargs in locate.items():
            if task_name not in locators:
                raise Exception('Programming error. Unknown locator: {0}'.format(task_name))
            locator = locators[task_name]
            for text_unit_id, text, text_unit_lang, document_id, project_id in text_units:

                # inject project_id for TermLocator to use custom ProjectTermConfiguration
                if task_name == 'term':
                    task_kwargs['project_id'] = project_id

                locator.try_parsing(log, location_results, text,
                                    text_unit_id, text_unit_lang, document_id, project_id, **task_kwargs)
        location_results.save(log, user_id)


@shared_task(base=ExtendedTask,
             bind=True,
             soft_time_limit=3600,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError),
             max_retries=3,
             priority=9)
def clean_tasks(this_task: ExtendedTask):
    all_tasks = list(Task.objects.all().exclude(id=this_task.request.id))
    executing_tasks = [t for t in all_tasks if t.status in UNREADY_STATES]
    all_tasks = [t for t in all_tasks if t.status not in UNREADY_STATES]
    executing_tasks = order_tasks_by_hierarchy(executing_tasks)
    this_task.set_push_steps(len(executing_tasks) + 3)

    if executing_tasks:
        purge_tasks(this_task, executing_tasks, True)

        # while we were purging tasks new sub tasks might have been started
        root_ids = [t.pk for t in executing_tasks]
        tasks_to_purge = []
        for i in range(3):
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

    terminate_processes_by_ids(pids, lambda m: log.info(m))


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
        .filter(name__in=excluded, own_date_done__lt=del_sub_tasks_date) \
        .delete()

    # Delete excess tasks from task list
    h = REMOVE_READY_TASKS_DELAY_IN_HOURS.val

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


def purge_task(task_pk, wait=False, timeout=None, delete=True,
               log_func: Callable[[str], None] = None):
    """
    Purge task method.
    :param log_func:
    :param task_pk: Task id
    :param wait:
    :param timeout
    :param delete - bool - either delete task and its subtasks after purge
    :return:
    """
    log_func = log_func or (lambda m: logger.info(m))

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

    for subtask in task.subtasks:
        subtask.terminate_spawned_processes('everywhere')
        subtask_celery_task = AsyncResult(subtask.id)
        revoke_task(subtask_celery_task, wait=wait, timeout=timeout)

    log_func('Celery task id={}'.format(task.id))

    main_celery_task = AsyncResult(task.id)
    revoke_task(main_celery_task, wait=wait, timeout=timeout)

    task_id = task.pk
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
        if task.metadata and 'session_id' in task.metadata:
            try:
                document_ids = list(Document.objects.filter(
                    processed=False,
                    upload_session__uid=task.metadata['session_id'],
                    name=task.metadata['file_name']).values_list('pk', flat=True))
                if document_ids:
                    from apps.document.tasks import DeleteDocuments
                    _call_task(DeleteDocuments, _document_ids=document_ids)
            except Exception as e:
                error_msg = 'Failed to start "DeleteDocuments" task. ' + str(e)
                log_func(error_msg)
                ret += '\n' + error_msg
                status = 'error'

    return {'message': ret, 'status': status}


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
    import time
    for i in range(1, 10):
        time.sleep(10)
        _celery_task.push()
        _celery_task.log_info(f'Step {i}')
    _celery_task.log_info('Done. Bye.')


@shared_task(base=ExtendedTask, bind=True)
def test_task_progress_sub_task(_celery_task: ExtendedTask, arg1: str = None):
    _celery_task.log_info(f'Testing task progress - subtask. Sleeping 10 seconds...\narg1={arg1}')
    _celery_task.set_push_steps(10)
    import time
    time.sleep(10)


@shared_task(base=ExtendedTask, bind=True)
def test_task_progress_with_subtasks(_celery_task: ExtendedTask, arg1: str = None):
    print(f'Testing task progress - main task. Going to start 10 sub-tasks each to sleep 10 seconds...\narg1={arg1}')
    args = [(arg1,) for _i in range(1, 10)]
    _celery_task.run_sub_tasks('debug', test_task_progress_sub_task, args)


# Register all load tasks
app.register_task(LoadDocuments())
app.register_task(CreateDocument())
app.register_task(LoadTerms())
app.register_task(LoadGeoEntities())
app.register_task(LoadCourts())

# Register all locate tasks
app.register_task(Locate())

# Register all update/cluster/classify tasks
app.register_task(UpdateElasticsearchIndex())
app.register_task(TotalCleanup())
