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
import pickle
import regex as re
import string
import sys
import threading
import time
import traceback
from inspect import isclass
from typing import List, Dict, Tuple, Any, Callable, Optional

# Third-party imports
import magic
import nltk
import numpy as np
import pandas as pd
from celery import app
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded, Retry
from celery.result import AsyncResult
from celery.states import SUCCESS, FAILURE, PENDING
from celery.utils.log import get_task_logger
from celery.utils.time import get_exponential_backoff_interval
# Django imports
from django.conf import settings
from django.db import transaction, connection
from django.db.models import Sum, Q, Case, Value, When, IntegerField, QuerySet
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
from sklearn.cluster import Birch, DBSCAN, KMeans, MiniBatchKMeans
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import LogisticRegressionCV
from sklearn.naive_bayes import MultinomialNB
from sklearn.semi_supervised import LabelSpreading
from sklearn.svm import SVC

# Project imports
import task_names
from apps.analyze.ml.cluster import ClusterDocuments, ClusterTextUnits
from apps.analyze.models import (
    DocumentCluster, TextUnitCluster,
    TextUnitClassification, TextUnitClassifier, TextUnitClassifierSuggestion)
from apps.celery import app
from apps.common.errors import find_cause_of_type
from apps.common.file_storage import get_file_storage
from apps.common.log_utils import ProcessLogger
from apps.common.utils import fast_uuid
from apps.deployment.app_data import load_geo_entities, load_terms, load_courts
from apps.document import signals
from apps.document.constants import DOCUMENT_TYPE_PK_GENERIC_DOCUMENT
from apps.document.field_detection.field_detection import detect_and_cache_field_values_for_document
from apps.document.models import (
    Document, DocumentText, DocumentMetadata, DocumentProperty, DocumentType,
    TextUnit, TextUnitTag, DocumentTable, TextUnitText)
from apps.document.repository.document_field_repository import DocumentFieldRepository
from apps.document.sync_tasks.document_files_cleaner import DocumentFilesCleaner
from apps.extract import dict_data_cache
from apps.extract import models as extract_models
from apps.extract.locators import LOCATORS, LocationResults
from apps.extract.models import (
    Court, GeoAlias, GeoEntity, GeoRelation, Party, Term)
from apps.project.models import Project, UploadSession
from apps.task.celery_backend.task_utils import revoke_task
from apps.task.models import Task, TaskConfig
from apps.task.parsing_tasks import ParsingTaskParams, XmlWordxDocumentParser, \
    TikaDocumentParser, TextractDocumentParser, PlainTextDocumentParser
from apps.task.utils.nlp.heading_heuristics import HeadingHeuristics
from apps.task.utils.nlp.lang import get_language
from apps.task.utils.nlp.parsed_text_corrector import ParsedTextCorrector
from apps.task.utils.task_utils import TaskUtils, pre_serialize
from apps.users.models import User
from contraxsuite_logging import write_task_log

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
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


def _get_or_create_task_config(celery_task) -> TaskConfig:
    return TaskConfig.objects.get_or_create(defaults={
        'name': celery_task.name,
        'soft_time_limit': celery_task.soft_time_limit
    }, name=celery_task.name)[0]


def get_task_priority(callable_or_class) -> int:
    priority = app.conf.task_default_priority
    if hasattr(callable_or_class, 'priority'):
        priority = callable_or_class.priority
    return priority


def get_queue_by_task_priority(priority: int) -> str:
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

    @property
    def task(self) -> Task:
        self.init_cache()
        return self._cached_data['task']

    @property
    def task_name(self) -> str:
        return self.name

    @property
    def log_extra(self) -> Dict:
        return self.task.log_extra

    @log_extra.setter
    def log_extra(self, v: Dict):
        this_task = self.task  # type: Task
        this_task.log_extra = v
        this_task.save(update_fields=['log_extra'])

    def write_log(self, message, level='info', exc_info: Exception = None, **kwargs):
        try:
            self.task.write_log(message, level, exc_info=exc_info, **kwargs)
        except Task.DoesNotExist:
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

        return f'Task has been failed:\n' + \
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
                    metadata={
                        'args': args,
                        'options': {
                            'soft_time_limit': task_config.soft_time_limit,
                            'root_id': self.main_task_id
                        }
                    },
                    priority=priority,
                    call_stack=call_stack
                    )
        task.save()

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
                metadata={
                    'args': args,
                    'options': {
                        'soft_time_limit': task_config.soft_time_limit,
                        'root_id': self.main_task_id
                    }
                },
                priority=priority,
                call_stack=call_stack
            ))
        Task.objects.bulk_create(tasks)

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

    def prepare_task_execution(self):
        TaskUtils.prepare_task_execution()
        self._cached_data = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cached_data = None

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.prepare_task_execution()
        Task.objects.increase_run_count(self.request.id)

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

    def info(self, message: str):
        return self._celery_task.log_info(message)

    def error(self, message: str, field_code: str = None, exc_info: Exception = None):
        if field_code:
            message = f'{field_code}: {message or "error"}'

        return self._celery_task.log_error(message, exc_info=exc_info, log_field_code=field_code)


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


def call_task_func(task_func: Callable,
                   task_args: Tuple,
                   user_id,
                   source_data=None,
                   metadata: Dict = None,
                   visible: bool = True,
                   queue: str = None,
                   run_after_sub_tasks_finished: bool = False,
                   run_if_parent_task_failed: bool = False,
                   main_task_id: str = None,
                   call_stack: str = None,
                   parent_stack: str = None):
    celery_task_id = str(fast_uuid())
    priority = get_task_priority(task_func)
    call_stack = call_stack or get_call_stack_line(-3)
    if parent_stack:
        call_stack = f'{parent_stack}\n{call_stack}'

    task = Task.objects.create(
        id=celery_task_id,
        name=task_func.__name__,
        user_id=user_id,
        args=task_args,
        source_data=source_data,
        metadata=metadata,
        visible=visible if visible is not None else True,
        run_after_sub_tasks_finished=run_after_sub_tasks_finished,
        run_if_parent_task_failed=run_if_parent_task_failed,
        main_task_id=main_task_id,
        priority=priority,
        call_stack=call_stack
    )

    task.write_log('Celery task id: {}\n'.format(celery_task_id))
    task_config = _get_or_create_task_config(task_func)
    if not queue:
        queue = get_queue_by_task_priority(priority)
    task_func.apply_async(queue=queue,
                          args=task_args,
                          task_id=celery_task_id,
                          soft_time_limit=task_config.soft_time_limit,
                          priority=priority)
    return task.pk


def call_task(task_name, **options):
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
    task = Task.objects.create(
        id=celery_task_id,
        name=task_name_resolved,
        user_id=options.get('user_id'),
        metadata=options.get('metadata', {}),
        kwargs=pre_serialize(celery_task_id, None, options_wo_metadata),  # this changes the options_wo_metadata !
        source_data=options.get('source_data'),
        group_id=options.get('group_id'),
        visible=options.get('visible', True),
        project=Project.all_objects.get(pk=project_id) if project_id else None,
        upload_session=UploadSession.objects.get(pk=session_id) if session_id else None,
        priority=priority,
        call_stack=call_stack
    )

    # updating options with the changes made in options_wo_metadata by pre_serialize()
    options.update(options_wo_metadata)

    task.write_log('Celery task id: {}\n'.format(celery_task_id))
    options['task_id'] = task.id
    async = options.pop('async', True)
    task_config = _get_or_create_task_config(task_class_resolved)
    if async:
        queue = task_class_resolved.queue \
            if hasattr(task_class_resolved, 'queue') \
            else get_queue_by_task_priority(priority)

        task_class_resolved().apply_async(
            kwargs=options,
            task_id=celery_task_id,
            soft_time_limit=task_config.soft_time_limit,
            countdown=countdown,
            eta=eta,
            priority=priority,
            queue=queue)
    else:
        task_class_resolved()(**options)
    return task.pk


class BaseTask(ExtendedTask):
    """BaseTask class
    BaseTask extending celery app Task model.
    Adds logging for start/end events of task
     and optional error handling.
    """

    def run(self, *args, **kwargs):
        self.log_info(
            'Start task "{0}", id={1}\nKwargs: {2}'.format(self.task_name,
                                                           self.main_task_id,
                                                           str(kwargs)))
        try:
            ret = self.process(**kwargs)
        finally:
            self.log_info(f'End of main task "{0}", id={1}. '
                          'Sub-tasks may be still running.'.format(self.task_name,
                                                                   self.main_task_id))
        return ret or self.main_task_id


@shared_task(base=ExtendedTask,
             bind=True,
             soft_time_limit=3600,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError),
             max_retries=3)
def delete_document_on_load_failed(task: ExtendedTask, file_name: str):
    document_name = os.path.basename(file_name)
    document_source = os.path.dirname(file_name)

    document_ids = list(Document.objects \
                        .filter(name=document_name, source=document_source) \
                        .values_list('pk', flat=True))

    if document_ids:
        task.log_error(f'Loading documents task failed, deleting documents: {file_name} (ids: {document_ids})')
        try:
            from apps.document.tasks import DeleteDocuments
            del_task = DeleteDocuments()
            del_task.process(_document_ids=document_ids)
        except Exception as e:
            task.log_error(f'Unable to delete documents, file_name={file_name}', exc_info=e)


class LoadDocuments(BaseTask):
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

        load_docs_args = [(file_path, kwargs) for file_path in file_list]
        self.run_sub_tasks('Load Each Document',
                           LoadDocuments.create_document,
                           load_docs_args,
                           file_list)

    @staticmethod
    @shared_task(base=ExtendedTask,
                 db_connection_ping=True,
                 bind=True,
                 soft_time_limit=3600,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError),
                 max_retries=3,
                 queue='doc_load')
    def create_document(task: ExtendedTask, uri: str, kwargs):
        with file_storage.get_document_as_local_fn(uri) as (fn, file_name):
            task.run_if_task_or_sub_tasks_failed(delete_document_on_load_failed, args=(uri,))
            return LoadDocuments.create_document_local(task, fn, uri, kwargs)

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
        task.log_extra = {'log_document_name': file_name}

        ret = []
        document_name = os.path.basename(file_name)
        document_source = os.path.dirname(file_name)
        file_size = os.path.getsize(file_path)
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
        pars_results = LoadDocuments.get_text_from_file(file_name, file_path,
                                                        propagate_exceptions, task)
        text = pars_results.text or ''
        metadata = pars_results.metadata
        parser_name = pars_results.parser

        # do reconnect - postgres may have already closed the connection because of long-running OCR
        connection.close()

        if not text:
            # delete document source file
            DocumentFilesCleaner.delete_document_files([file_name])
            raise RuntimeError('No text extracted.')

            # if propagate_exceptions:
            #     raise RuntimeError('No text extracted.')
            # task.log_info('SKIP (ERROR): ' + file_name)
            # return None

        if metadata is None:
            metadata = {}
        else:
            # INFO: postgresql crashes to store \x00 (\u0000) in json with message:
            # DataError: unsupported Unicode escape sequence
            # DETAIL:  \u0000 cannot be converted to text.
            metadata = json.loads(json.dumps(metadata).replace('\\u0000', ''))

        metadata['parsed_by'] = parser_name

        # detect if document is contract
        if kwargs.get('detect_contract'):
            try:
                res = is_contract(text, return_probability=True)
                if res is not None:
                    metadata['is_contract'], metadata['is_contract_probability'] = res
            except ImportError:
                task.log_warn('Cannot import lexnlp.extract.en.contracts.detector.is_contract')

        # remove extra line breaks
        text = LoadDocuments.preprocess_parsed_text(text)

        # Language identification
        language, lang_detector = get_language(text, get_parser=True)
        if language:
            task.log_info('Detected language: %s' % language.upper())
            task.log_info('Language detector: %s' % lang_detector.upper())
        else:
            task.log_info('LANGUAGE IS NOT DETECTED: ' + file_name)

        # detect title
        title = metadata.get('title', None) or LoadDocuments.get_title(text)

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
                task.log_info(message='Document Upload Session id={}'.format(upload_session.pk))
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
                language=language,
                title=title,
                file_size=file_size,
                folder=kwargs.get('directory_path'))
            DocumentText.objects.create(document=document, full_text=text)
            DocumentMetadata.objects.create(document=document, metadata=metadata)

            task.log_extra['log_document_id'] = document.pk

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

            paragraphs = LoadDocuments.safely_get_paragraphs(text)
            for paragraph, pos_start, post_end in paragraphs:
                if not paragraph:
                    task.log_error(f'Paragraph text is null:\n'
                                   f'Document: {document.name} (#{document.pk})\n'
                                   f'Location: {pos_start} - {post_end}')
                ptr = TextUnit(
                    document=document,
                    unit_type="paragraph",
                    location_start=pos_start,
                    location_end=post_end)
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
            sentence_spans = get_sentence_span_list(text)
            for span in sentence_spans:
                sentence = text[span[0]:span[1]]
                text_unit = TextUnit(
                    document=document,
                    location_start=span[0],
                    location_end=span[1],
                    text_hash=hashlib.sha1(sentence.encode("utf-8")).hexdigest(),
                    unit_type="sentence",
                    language=get_language(sentence))
                sentence_list.append(text_unit)

            sentence_tu_objects = TextUnit.objects.bulk_create(sentence_list)

            sentence_text_list = []  # type: List[TextUnitText]
            for text_unit, span in zip(sentence_tu_objects, sentence_spans):
                sentence = text[span[0]:span[1]]
                tu_text_obj = TextUnitText(
                    text_unit=text_unit,
                    text=sentence
                )
                sentence_text_list.append(tu_text_obj)

            TextUnitText.objects.bulk_create(sentence_text_list)

            document.paragraphs = len(paragraph_list)
            document.sentences = len(sentence_list)
            document.save()

            # detect sections
            sections = list(get_section_spans(text, use_ml=False, return_text=False,
                                              skip_empty_headers=True))
            LoadDocuments.find_section_titles(sections, paragraph_list, sentence_list, text)
            metadata['sections'] = sections

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

        task.log_info(message='LOADED (%s): %s' % (parser_name.upper(), file_name))
        task.log_info(message='Document pk: %d' % document.pk)

        # call post processing task
        linked_tasks = kwargs.get('linked_tasks') or list()  # type: List[Dict[str, Any]]

        if should_run_standard_locators:
            from apps.extract.app_vars import STANDARD_LOCATORS

            task.run_sub_tasks_class_based('Locate', Locate, [{
                'locate': STANDARD_LOCATORS.val,
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
    def find_section_titles(
        sections: List[Dict[str, Any]],
        paragraphs: List[TextUnit],
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
                           task: ExtendedTask):
        """
        extract text from file using either Tika or Textract
        """
        from apps.document.app_vars import OCR_ENABLE, OCR_FILE_SIZE_LIMIT, \
            MSWORD_TO_TEXT_ENABLE
        ocr_enabled = OCR_ENABLE.val

        # disable OCR anyway if file size exceeds limit
        if ocr_enabled:
            fsize_limit = OCR_FILE_SIZE_LIMIT.val
            fsize = os.path.getsize(file_path)
            fsize /= 1024 * 1024
            ocr_enabled = ocr_enabled and fsize <= fsize_limit

        _fn, ext = os.path.splitext(file_name)
        if not ext:
            mt = python_magic.from_file(file_path)
            ext = mimetypes.guess_extension(mt)
        ext = ext or ''

        parse_ptrs = ParsingTaskParams(CeleryTaskLogger(task),
                                       file_path,
                                       ext,
                                       file_name,
                                       propagate_exceptions,
                                       ocr_enabled)

        # decide can we parse the file with Textract
        word_parse_enabled = MSWORD_TO_TEXT_ENABLE.val
        textract_enabled = ocr_enabled or \
                           ext in settings.TEXTRACT_NON_OCR_EXTENSIONS

        if settings.TEXTRACT_FIRST_FOR_EXTENSIONS:
            parse_functions = [PlainTextDocumentParser(),
                               XmlWordxDocumentParser() if word_parse_enabled else None,
                               TextractDocumentParser() if textract_enabled else None,
                               TikaDocumentParser()]
        else:
            parse_functions = [PlainTextDocumentParser(),
                               XmlWordxDocumentParser() if word_parse_enabled else None,
                               TikaDocumentParser(),
                               TextractDocumentParser() if textract_enabled else None]

        results = None
        for parsr in parse_functions:
            if not parsr:
                continue
            results = parsr.try_parse_document(parse_ptrs)
            if not results.is_empty():
                break

        if results and not results.is_empty():
            text = results.text
            text = pre_process_document(text)
            # TODO: migrate it in lexnlp if it works good
            text = re.sub(r'<[\s/]*(?:[A-Za-z]+|[Hh]\d)[\s/]*>', '', text)
            results.text = text.replace('\r\n', '\n')
        return results

    @staticmethod
    def preprocess_parsed_text(text: str):
        from apps.document.app_vars import PREPROCESS_DOCTEXT_LINEBREAKS, PREPROCESS_DOCTEXT_PUNCT
        if PREPROCESS_DOCTEXT_LINEBREAKS.val:
            # fix extra line breaks
            corrector = ParsedTextCorrector()
            text = corrector.correct_if_corrupted(text)
        if PREPROCESS_DOCTEXT_PUNCT.val:
            text = TextBeautifier.unify_quotes_braces(text)
        return text

    @staticmethod
    def safely_get_paragraphs(text: str) -> List[Tuple[str, int, int]]:
        try:
            return list(get_paragraphs(text, return_spans=True))
        except:
            return [(text, 0, len(text) - 1)]


class UpdateElasticsearchIndex(BaseTask):
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


class LoadTerms(BaseTask):
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


class LoadGeoEntities(BaseTask):
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


class LoadCourts(BaseTask):
    """
    Load Courts data from a file OR github repo
    """
    name = 'Load Courts'
    priority = 9

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


class Locate(BaseTask):
    """
    Locate multiple items
    """
    name = "Locate"

    soft_time_limit = 6000
    default_retry_delay = 10
    retry_backoff = True
    autoretry_for = (SoftTimeLimitExceeded, InterfaceError, OperationalError,)
    max_retries = 3
    priority = 9

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
            text_units = text_units.filter(document__project__id=project_id)

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
            locate_args = [[text_unit_ids[i:i + package_size], kwargs['user_id'], locate] for i in
                           range(0, len(text_unit_ids), package_size)]
            self.run_sub_tasks('Locate Data In Each Text Unit', Locate.parse_text_units, locate_args)

        if document_id:
            document_ids = [document_id]
        elif project_id:
            document_ids = Document.objects.filter(
                project_id=project_id).values_list('pk', flat=True)
        else:
            return
        for document_id in document_ids:
            # otherwise run_after_sub_tasks_finished doesn't work if no subtasks
            # TODO: investigate and fix base methods like run_after_sub_tasks_finished
            if not text_unit_ids:
                self.run_sub_tasks('Cache Generic Document Data',
                                   Locate.on_locate_finished,
                                   [(document_id, doc_loaded_by_user_id,
                                     predefined_field_codes_to_python_values)])
            else:
                self.run_after_sub_tasks_finished(
                    'Cache Generic Document Data',
                    Locate.on_locate_finished,
                    [(document_id, doc_loaded_by_user_id, document_initial_load,
                      predefined_field_codes_to_python_values)])

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=6000,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3,
                 priority=9)
    def on_locate_finished(_self: ExtendedTask, doc_id, doc_loaded_by_user_id, document_initial_load,
                           predefined_field_codes_to_val: Dict[str, Any] = None):
        doc = Document.all_objects.filter(pk=doc_id).last()  # type: Document

        if not doc:
            _self.log_info(f'on_locate_finished: Document does not exist: {doc.name} (#{doc.pk})\n'
                           f'Maybe it was deleted previously because of failed loading or failed entity location '
                           f'stage.')
            return

        log = CeleryTaskLogger(_self)

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

        signals.fire_document_changed(sender=_self,
                                      log=log,
                                      document=doc,
                                      changed_by_user=None,
                                      system_fields_changed=True,
                                      user_fields_changed=False,
                                      generic_fields_changed=True)
        detect_and_cache_field_values_for_document(log=log,
                                                   document=doc,
                                                   save=True,
                                                   clear_old_values=True,
                                                   ignore_field_codes=ignore_field_codes,
                                                   changed_by_user=user,
                                                   document_initial_load=document_initial_load)

        Document.objects.filter(pk=doc_id).update(processed=True)

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=6000,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3
                 )
    def parse_text_units(self: ExtendedTask, text_unit_ids, user_id, locate):
        text_units = TextUnit.objects.filter(pk__in=text_unit_ids).values_list(
            'pk', 'textunittext__text', 'language', 'document__project_id')
        location_results = LocationResults()
        log = CeleryTaskLogger(self)

        for task_name, task_kwargs in locate.items():
            if task_name not in LOCATORS:
                raise Exception('Programming error. Unknown locator: {0}'.format(task_name))
            locator = LOCATORS[task_name]
            for text_unit_id, text, text_unit_lang, project_id in text_units:

                # inject project_id for TermLocator to use custom ProjectTermConfiguration
                if task_name == 'term':
                    task_kwargs['project_id'] = project_id

                locator.try_parsing(log, location_results, text,
                                    text_unit_id, text_unit_lang, **task_kwargs)
        location_results.save(log, user_id)


class Classify(BaseTask):
    """
    Classify Text Units
    """
    name = 'Classify'
    classifier_map = {
        'LogisticRegressionCV': LogisticRegressionCV,
        'MultinomialNB': MultinomialNB,
        'ExtraTreesClassifier': ExtraTreesClassifier,
        'RandomForestClassifier': RandomForestClassifier,
        'SVC': SVC,
    }
    classify_by_map = {
        'terms': {
            'term_model': Term,
            'term_set_name': 'termusage_set',
            'term_field': 'term'},
        'parties': {
            'term_model': Party,
            'term_set_name': 'partyusage_set',
            'term_field': 'party'},
        'entities': {
            'term_model': GeoEntity,
            'term_set_name': 'geoentityusage_set',
            'term_field': 'entity'}
    }

    def process(self, **kwargs):
        """
        Classify Text Units
        :param kwargs: dict, form data
        :return:
        """

        self.set_push_steps(3)

        classifier_selection = kwargs.get('classifier')
        classifier_id = classifier_selection['pk'] if classifier_selection else None

        class_name = kwargs.get('class_name') or ''
        if not classifier_id and not class_name:
            raise RuntimeError(f'Either "class_name" or "classifier" should be passed')

        min_confidence = kwargs['min_confidence'] / 100

        if classifier_id is None and kwargs.get('delete_classifier') and class_name:
            TextUnitClassifier.objects.filter(class_name=class_name).delete()

        if kwargs['delete_suggestions']:
            if classifier_id is None:
                filter_opts = {'class_name': class_name}
            else:
                filter_opts = {'classifier_id': classifier_id}
            TextUnitClassifierSuggestion.objects.filter(**filter_opts).delete()

        self.push()  # 1

        clf, clf_model = self.get_classifier(kwargs, classifier_id)

        self.push()  # 2

        # Apply to other documents
        tf_idf_transformer = TfidfTransformer()
        run_date = datetime.datetime.now()

        doc_query = Document.objects.all()
        if 'project' in kwargs and kwargs['project']:
            project_id = kwargs['project']['pk']
            doc_query = doc_query.filter(project_id=project_id)

        for d in doc_query[:kwargs['sample_size']]:
            # Build document feature matrix
            d_text_units = d.textunit_set.all()
            text_unit_ids = d_text_units.values_list('id', flat=True)
            text_unit_count = len(text_unit_ids)
            test_features = np.zeros((text_unit_count,
                                      len(clf_model.term_index)))

            # TODO: check for using db, especially text_unit.text
            for i in range(text_unit_count):
                for tu in getattr(d_text_units[i], clf_model.term_set_name).all():
                    term_id = clf_model.term_index.index(getattr(tu, clf_model.term_field).id)
                    test_features[i, term_id] = tu.count

            if clf_model.use_tfidf:
                test_features = tf_idf_transformer.fit_transform(test_features)

            proba_scores = clf_model.predict_proba(test_features)
            predicted = clf_model.predict(test_features)
            tucs_list = []

            for item_no, _ in enumerate(test_features):
                confidence = max(proba_scores[item_no])
                if confidence < min_confidence:
                    continue
                tucs = TextUnitClassifierSuggestion()
                tucs.classifier = clf
                tucs.classifier_run = run_date.isoformat()
                tucs.classifier_confidence = max(proba_scores[item_no])
                tucs.text_unit_id = text_unit_ids[item_no]
                tucs.class_name = clf.class_name
                tucs.class_value = predicted[item_no]
                tucs_list.append(tucs)
            TextUnitClassifierSuggestion.objects.bulk_create(tucs_list)

        self.push()  # 3

    def get_classifier(self, kwargs, classifier_id):
        """
        Get Classifier by id or create it using form data
        :param kwargs: dict, form data
        :param classifier_id: str or None, Classifier id
        :return: Classifier
        """

        if classifier_id is not None:
            clf = TextUnitClassifier.objects.get(pk=classifier_id)
            clf_model = pickle.loads(clf.model_object)
            return clf, clf_model

        algorithm = kwargs['algorithm']
        class_name = kwargs['class_name']
        use_tfidf = kwargs['use_tfidf']
        classify_by = kwargs['classify_by']
        classify_by_class = self.classify_by_map[classify_by]
        term_model = classify_by_class['term_model']
        term_set_name = classify_by_class['term_set_name']
        term_field = classify_by_class['term_field']

        # Iterate through all classifications
        tucs = TextUnitClassification.objects \
            .filter(class_name=class_name,
                    text_unit__unit_type__in=['paragraph'])
        training_text_units = [t.text_unit for t in tucs]
        training_targets = tucs.values_list('class_value', flat=True)

        # Create feature matrix
        term_index = list(term_model.objects.values_list('id', flat=True))
        training_features = np.zeros((len(training_text_units),
                                      len(term_index)))

        # Create matrix
        for i, _ in enumerate(training_text_units):
            for tu in getattr(training_text_units[i], term_set_name).all():
                training_features[i, term_index.index(getattr(tu, term_field).id)] = tu.count

        # get classifier options
        if algorithm == 'SVC':
            gamma = kwargs.get('svc_gamma', 'auto')
            classifier_opts = {
                'C': kwargs['svc_c'],
                'kernel': kwargs['svc_kernel'],
                'gamma': gamma,
                'probability': True
            }
        elif algorithm == 'MultinomialNB':
            classifier_opts = {
                'alpha': kwargs['mnb_alpha']
            }
        elif algorithm in ('ExtraTreesClassifier', 'RandomForestClassifier'):
            classifier_opts = {
                'n_estimators': kwargs['rfc_etc_n_estimators'],
                'criterion': kwargs['rfc_etc_criterion'],
                'max_features': kwargs.get('rfc_etc_max_features', 'auto'),
                'max_depth': kwargs['rfc_etc_max_depth'],
                'min_samples_split': kwargs['rfc_etc_min_samples_split'],
                'min_samples_leaf': kwargs['rfc_etc_min_samples_leaf'],
            }
        else:  # if algorithm == 'LogisticRegressionCV'
            classifier_opts = {
                'Cs': kwargs['lrcv_cs'],
                'fit_intercept': kwargs['lrcv_fit_intercept'],
                'multi_class': kwargs['lrcv_multi_class'],
                'solver': kwargs['lrcv_solver']
            }

        if use_tfidf:
            tf_idf_transformer = TfidfTransformer()
            training_features = tf_idf_transformer.fit_transform(training_features)

        clf_model = self.classifier_map[algorithm](**classifier_opts)
        clf_model.fit(training_features, training_targets)
        clf_model.use_tfidf = use_tfidf
        clf_model.term_index = term_index
        clf_model.term_set_name = term_set_name
        clf_model.term_field = term_field

        # Create suggestions
        run_date = datetime.datetime.now()

        # Create classifier object
        clf = TextUnitClassifier()
        clf.class_name = class_name
        clf.version = run_date.isoformat()
        clf.name = "model:{}, by:{}, class_name:{}, scheduled:{}".format(
            algorithm, classify_by, class_name, run_date.strftime('%Y-%m-%d.%H:%M'))
        clf.model_object = pickle.dumps(clf_model, protocol=pickle.HIGHEST_PROTOCOL)
        clf.save()

        return clf, clf_model


class Cluster(BaseTask):
    """
    Cluster Documents, Text Units
    """
    # TODO: cluster by expanded entity aliases

    name = 'Cluster'

    def process(self, **kwargs):

        do_cluster_documents = kwargs.pop('do_cluster_documents')
        do_cluster_text_units = kwargs.pop('do_cluster_text_units')

        project = kwargs.pop('project')
        project_id = project['pk'] if project else None
        cluster_name = kwargs.pop('name')
        cluster_desc = kwargs.pop('description')
        cluster_algorithm = kwargs.pop('using', 'kmeans')
        n_clusters = kwargs.pop('n_clusters', 3)
        cluster_by = kwargs.pop('cluster_by', 'term')
        use_tfidf = kwargs.pop('use_tfidf', True)
        unit_type = kwargs.pop('unit_type', 'sentence')

        # get cluster-algorithm-specific cluster options from form data
        cluster_options = dict()
        for option_name, option_value in kwargs.items():
            if option_name.startswith(cluster_algorithm + '_'):
                option_name = option_name.replace(cluster_algorithm + '_', '')
                cluster_options[option_name] = option_value

        cluster_classes = []
        if do_cluster_documents:
            cluster_classes.append(ClusterDocuments)
        if do_cluster_text_units:
            cluster_classes.append(ClusterTextUnits)

        for cluster_class in cluster_classes:
            cluster_model = cluster_class(project_id=project_id,
                                          cluster_algorithm=cluster_algorithm,
                                          n_clusters=n_clusters,
                                          cluster_by=cluster_by,
                                          name=cluster_name,
                                          description=cluster_desc,
                                          use_tfidf=use_tfidf,
                                          unit_type=unit_type,
                                          **cluster_options)
            cluster_model.run()


@shared_task(base=ExtendedTask,
             bind=True,
             soft_time_limit=3600,
             default_retry_delay=10,
             retry_backoff=True,
             autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError),
             max_retries=3)
def clean_tasks(this_task: ExtendedTask):
    purged_pending_tasks = 0

    qr = Task.objects.main_tasks().filter(status=PENDING).exclude(id=this_task.request.id)  # type: QuerySet

    this_task.set_push_steps(qr.count() + 1)

    for task_to_purge in qr:
        this_task.log_info('Purging: Task="{}", status="{}", date_start="{}"'.format(
            task_to_purge.name, task_to_purge.status, task_to_purge.date_start))
        try:
            purge_task(task_to_purge)
            purged_pending_tasks += 1
        except Exception as e:
            # if we were unable to purge a task - log error and proceed to the next one, don't break
            this_task.log_error(f'Unable to purge task {task_to_purge.name} (#{task_to_purge.id})', exc_info=e)
        this_task.push()

    deleted_tasks, _unused = Task.objects.all().exclude(id=this_task.request.id).delete()
    this_task.push()

    ret = f'Purged {purged_pending_tasks} pending main tasks. Deleted {deleted_tasks} tasks after purging main tasks.'
    this_task.log_info(ret)


@app.task(name=task_names.TASK_NAME_TRACK_TASKS, bind=True, queue=settings.CELERY_QUEUE_SERIAL)
def track_tasks(_celery_task):
    TaskUtils.prepare_task_execution()
    for task_id in Task.objects.unready_parent_tasks().values_list('pk', flat=True):
        Task.objects.update_parent_task(task_id)


@app.task(name=task_names.TASK_NAME_UPDATE_PARENT_TASK, bind=True, queue=settings.CELERY_QUEUE_SERIAL)
def update_parent_task(_celery_task, parent_task_id: str,
                       linked_parent_task_id: Optional[str] = None):
    if parent_task_id == linked_parent_task_id:
        raise Exception(f'Task #{parent_task_id} updates itself')
    parent_task_id = linked_parent_task_id or parent_task_id
    TaskUtils.prepare_task_execution()
    Task.objects.update_parent_task(parent_task_id)


@app.task(name=task_names.TASK_NAME_CLEAN_TASKS_PERIODIC, bind=True, queue=settings.CELERY_QUEUE_SERIAL)
def clean_tasks_periodic(_celery_task):
    from apps.task.app_vars import REMOVE_READY_TASKS_DELAY_IN_HOURS

    TaskUtils.prepare_task_execution()

    del_sub_tasks_date = now() - datetime.timedelta(seconds=settings.REMOVE_SUB_TASKS_DELAY_IN_SEC)

    # Delete sub-tasks of all main tasks finished more than a minute ago
    Task.objects \
        .filter(main_task__date_done__lt=del_sub_tasks_date, own_status__in=[SUCCESS]) \
        .delete()

    # Delete all completed system/periodic tasks from DB
    Task.objects \
        .filter(name__in=Task.objects.EXCLUDE_FROM_TRACKING, own_date_done__lt=del_sub_tasks_date) \
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


def purge_task(task_pk, wait=False, timeout=None, delete=True):
    """
    Purge task method.
    :param task_pk: Task id
    :param wait:
    :param timeout
    :oaram delete - bool - either delete task and its subtasks after purge
    :return:
    """

    task = task_pk

    if not isinstance(task, Task):
        try:
            task = Task.objects.get(pk=task)
        except Task.DoesNotExist:
            return

    message = 'Task "Purge task", app task id={}'.format(task.pk)
    logger.info(message)

    celery_task = AsyncResult(task.id)
    logger.info('Celery task id={}'.format(task.id))

    revoke_task(celery_task, wait=wait, timeout=timeout)

    if delete:
        ret = 'Deleted '
        # delete TaskResults for subtasks
        subtask_results_deleted = task.subtasks.delete()

        # delete Task
        task.delete()

        ret += 'Task(id={}), TaskHistory, '.format(task.pk)

        ret += 'main celery task, children celery tasks, {} TaskResult(s)'.format(
            subtask_results_deleted[0] + 1)
    else:
        ret = 'Revoked Task(id={})'

    logger.info(ret)

    return {'message': ret, 'status': 'success'}


class TotalCleanup(BaseTask):
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
        return None
    call_stack = stack_lines[index]
    lbr_pos = call_stack.find('\n')
    if lbr_pos:
        call_stack = call_stack[:lbr_pos]
    return call_stack


# Register all load tasks
app.register_task(LoadDocuments())
app.register_task(LoadTerms())
app.register_task(LoadGeoEntities())
app.register_task(LoadCourts())

# Register all locate tasks
app.register_task(Locate())

# Register all update/cluster/classify tasks
app.register_task(UpdateElasticsearchIndex())
app.register_task(TotalCleanup())
app.register_task(Classify())
app.register_task(Cluster())
