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
import re
import string
import sys
import traceback
from inspect import isclass
from subprocess import CalledProcessError
from traceback import format_exc
from typing import List, Dict, Tuple, Any, Callable

# Additional libraries
import magic
import nltk
import numpy as np
import pandas as pd
from apps.task.utils.text_extraction import tabula
from celery import app
# Celery imports
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded, TimeLimitExceeded, Retry
from celery.result import AsyncResult
# Django imports
from celery.states import SUCCESS
from celery.utils.log import get_task_logger
from constance import config
from django.conf import settings
from django.db import transaction
from django.db.models import Count, Q, Case, Value, When, IntegerField
from django.utils.timezone import now
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
from lexnlp.extract.common.text_beautifier import TextBeautifier
from lexnlp.extract.en.contracts.detector import is_contract
from lexnlp.nlp.en.segments.paragraphs import get_paragraphs
from lexnlp.nlp.en.segments.sentences import get_sentence_span_list, pre_process_document
from lexnlp.nlp.en.segments.titles import get_titles
from psycopg2 import InterfaceError, OperationalError
# Scikit-learn imports
from sklearn.cluster import Birch, DBSCAN, KMeans, MiniBatchKMeans
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import LogisticRegressionCV
from sklearn.naive_bayes import MultinomialNB
from sklearn.semi_supervised import LabelSpreading
from sklearn.svm import SVC
from textblob import TextBlob

# Project imports
import settings
from apps.analyze.models import (
    DocumentCluster, TextUnitCluster,
    TextUnitClassification, TextUnitClassifier, TextUnitClassifierSuggestion)
from apps.celery import app
from apps.common.file_storage import get_file_storage
from apps.common.log_utils import ProcessLogger
from apps.common.utils import fast_uuid
from apps.deployment.app_data import load_geo_entities, load_terms, load_courts
from apps.document.constants import DOCUMENT_TYPE_PK_GENERIC_DOCUMENT
from apps.document.field_types import FieldType
from apps.document.fields_detection.field_detection import detect_and_cache_field_values_for_document
from apps.document.fields_processing import field_value_cache
from apps.document.models import (
    Document, DocumentField, DocumentProperty, DocumentType, TextUnit, TextUnitProperty, TextUnitTag)
from apps.extract import dict_data_cache
from apps.extract import models as extract_models
from apps.extract.locators import LOCATORS, LocationResults
from apps.extract.models import (
    Court, GeoAlias, GeoEntity, GeoRelation,
    Party, Term, TermUsage)
from apps.project.models import Project, UploadSession
from apps.task.celery_backend.task_utils import revoke_task
from apps.task.models import Task, TaskConfig
from apps.task.utils.nlp.lang import get_language
from apps.task.utils.nlp.parsed_text_corrector import ParsedTextCorrector
from apps.task.utils.text_extraction.textract import textract2text
from apps.task.utils.text_extraction.tika import parametrized_tika_parser
from apps.task.utils.task_utils import TaskUtils, pre_serialize
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
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

    def write_log(self, message, level='info', **kwargs):
        try:
            self.task.write_log(message, level, **kwargs)
        except Task.DoesNotExist:
            Task.write_task_log(self.request.id, message, level, task_name=self.request.task, log_extra=kwargs)

    def log_info(self, message, **kwargs):
        self.write_log(message, level='info', **kwargs)

    def log_error(self, message, **kwargs):
        self.write_log(message, level='error', **kwargs)

    def log_debug(self, message, **kwargs):
        self.write_log(message, level='debug', **kwargs)

    def log_warn(self, message, **kwargs):
        self.write_log(message, level='warn', **kwargs)

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
        if this_task.is_sub_task():
            this_task.progress = this_task.progress + 100.0 / this_task.push_steps
            this_task.save(update_fields=['own_progress', 'progress'])
        else:
            this_task.save(update_fields=['own_progress'])

    def get_progress(self):
        return Task.objects.get(id=self.request.id).progress

    def update_progress(self, value: float):
        this_task = self.task  # type: Task
        this_task.own_progress = value
        if this_task.is_sub_task():
            this_task.progress = value
            this_task.save(update_fields=['own_progress', 'progress'])
        else:
            this_task.save(update_fields=['own_progress'])

    def _render_task_failed(self, args, kwargs, exc, exception_trace) -> str:
        if isinstance(exc, SoftTimeLimitExceeded):
            problem_str = 'Soft time limit exceeded: {0} seconds'.format(
                self.request.timelimit[1] or self.soft_time_limit)
        elif isinstance(exc, TimeLimitExceeded):
            problem_str = 'Time limit exceeded: {0} seconds'.format(
                self.request.timelimit[0] or self.time_limit)
        else:
            problem_str = '{0}\n{1}'.format(exc, traceback.format_exc())

        retry_msg = f'({self.request.retries} times retried)' \
            if self.request.retries else ''
        msg = f'Task has been failed{retry_msg}:\n' + \
              f'{self.name}\n' + \
              f'Args: {args}\n' + \
              f'Kwargs: {str(kwargs)}\n' + \
              f'Reason: {problem_str}'
        if hasattr(exc, 'detailed_error'):
            msg += f'\nDetail: {exc.detailed_error}'
        return msg

    def chord(self, sub_tasks):
        self.log_info(
            '{0}: starting {1} sub-tasks...'.format(self.task_name, len(sub_tasks)))
        for ss in sub_tasks:
            priority = get_task_priority(ss)
            ss.apply_async(priority=priority, queue=get_queue_by_task_priority(priority))

    def run_after_sub_tasks_finished(self,
                                     tasks_group_title: str,
                                     sub_task_function,
                                     args_list: List[Tuple],
                                     source_data: List[str] = None):
        task_config = _get_or_create_task_config(sub_task_function)
        tasks = []
        priority = get_task_priority(sub_task_function)

        for index, args in enumerate(args_list):
            tasks.append(Task(
                name=sub_task_function.name,
                main_task_id=self.main_task_id or self.request.id,
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
                priority=priority
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
                                  source_data: List[str] = None):
        """
        Asynchronously execute sub_task_method on each tuple of arguments from the provided list.

        :param sub_tasks_group_title:
        :param sub_task_function:
        :param args_list:
        :param source_data:
        :return:
        """
        sub_tasks = []
        priority = get_task_priority(sub_task_class)
        task_config = _get_or_create_task_config(sub_task_class)
        for index, args in enumerate(kwargs_list):
            sub_task_signature = sub_task_class().subtask(
                kwargs=args,
                source_data=source_data[index] if source_data is not None else self.task.source_data,
                soft_time_limit=task_config.soft_time_limit,
                root_id=self.main_task_id,
                main_task_id=self.main_task_id,
                parent_id=self.request.id,
                title=sub_tasks_group_title,
                priority=priority)
            sub_tasks.append(sub_task_signature)

        self.chord(sub_tasks)

    def prepare_task_execution(self):
        TaskUtils.prepare_task_execution()
        self._cached_data = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cached_data = None

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.prepare_task_execution()
        Task.objects.increase_run_count(self.request.id)
        try:
            return super().__call__(*args, **kwargs)
        except Exception as exc:
            if isinstance(exc, Retry):
                task_failed_msg = self._render_task_failed(args, kwargs, exc.exc,
                                                           traceback.format_exc())
                self.log_warn(
                    '{0}\nGoing to retry in {1} seconds...'.format(task_failed_msg, exc.when))
            else:
                self.log_error(self._render_task_failed(args, kwargs, exc, traceback.format_exc()))
            Task.objects.set_failure_processed(self.request.id, True)
            raise exc

    def on_failure(self, exc, task_id, args, kwargs, exc_traceback):
        if not self.task.failure_processed:
            self.log_error(self._render_task_failed(args, kwargs, exc, exc_traceback))


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

    def error(self, message: str, field_code: str = None):
        return self._celery_task.log_error('{0}: {1}'.format(field_code, message), log_field_code=field_code)


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
                   main_task_id: str = None):
    celery_task_id = str(fast_uuid())
    priority = get_task_priority(task_func)

    task = Task.objects.create(
        id=celery_task_id,
        name=task_func.__name__,
        user_id=user_id,
        source_data=source_data,
        metadata=metadata,
        visible=visible if visible is not None else True,
        run_after_sub_tasks_finished=run_after_sub_tasks_finished,
        main_task_id=main_task_id,
        priority=priority
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
        sequential_tasks=options.get('sequential_tasks'),
        group_id=options.get('group_id'),
        visible=options.get('visible', True),
        project=Project.all_objects.get(pk=project_id) if project_id else None,
        upload_session=UploadSession.objects.get(pk=session_id) if session_id else None,
        priority=priority
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

    standard_locators = ['date',
                         'party',
                         'term',
                         'geoentity',
                         'currency',
                         'citation',
                         'definition',
                         'duration']

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
                 bind=True,
                 soft_time_limit=3600,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError),
                 max_retries=3,
                 queue='doc_load')
    def create_document(task: ExtendedTask, uri: str, kwargs):
        with file_storage.get_document_as_local_fn(uri) as (fn, file_name):
            return LoadDocuments.create_document_local(task, fn, uri, kwargs)

    # FIXME: this becomes unuseful as we CANNOT subclass from LoadDocument now - it hasn't self in methods!!!
    @staticmethod
    def save_extra_document_data(**kwargs):
        pass

    @staticmethod
    def try_parsing_with_tika(task: ExtendedTask,
                              file_path: str,
                              original_file_name: str,
                              propagate_exceptions: bool = True,
                              enable_ocr: bool = True):

        # set OCR strategy (environment var)
        task.log_info('Trying TIKA for file: ' + original_file_name)
        if settings.TIKA_DISABLE:
            task.log_info('TIKA is disabled in config')
            return None, None, None

        from apps.document.app_vars import TIKA_TIMEOUT
        timeout = TIKA_TIMEOUT.val
        try:
            # here we command Tika to use OCR for image-based PDFs
            # or switch to 'native' call parser.from_file(file_path, settings. ...)

            # this app var is imported here in lazy manner to prevent
            # issues when tasks.py is imported in migrations before the tables for app vars are created
            from apps.document.app_vars import TIKA_SERVER_ENDPOINT
            tika_server_endpoint = TIKA_SERVER_ENDPOINT.val
            if tika_server_endpoint:
                task.log_info(f'TIKA server endpoint: {tika_server_endpoint}')
                # call Tika as server
                data = parametrized_tika_parser.parse_file_on_server(
                    'all', file_path, tika_server_endpoint,
                    enable_ocr=enable_ocr)
            else:
                # or execute Tika jar
                data = parametrized_tika_parser.parse_file_local(
                    file_path,
                    original_file_name=original_file_name,
                    timeout=timeout,
                    logger=CeleryTaskLogger(task),
                    enable_ocr=enable_ocr)

            parsed = data.get('content')
            metadata = data['metadata']
            if parsed and len(parsed) >= 100:
                return parsed, 'tika', metadata
            else:
                task.log_error('TIKA returned too small text for file: ' + original_file_name)
                return None, None, None
        except Exception as ex:
            task.log_error('Caught exception while trying to parse file with' +
                           f'Tika: {original_file_name}\n{format_exc()}, ' +
                           f'timeout is: {timeout}')
            if propagate_exceptions:
                raise ex
            return None, None, None

    @staticmethod
    def try_parsing_with_textract(task: ExtendedTask, file_path, ext, original_file_name,
                                  propagate_exceptions: bool = True):
        task.log_info('Trying Textract for file: ' + original_file_name)
        try:
            return textract2text(file_path, ext=ext), 'textract'
        except Exception as ex:
            task.log_info('Caught exception while trying to parse file with Textract: {0}\n{1}'
                          .format(original_file_name, format_exc()))
            if propagate_exceptions:
                raise ex
            return None, None

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
                              pre_defined_doc_fields_code_to_python_val: Dict[str, Any] = None):
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
        ext, metadata, parser_name, propagate_exceptions, text = \
            LoadDocuments.get_text_from_file(file_name, file_path,
                                             propagate_exceptions, task)

        if not text:
            if propagate_exceptions:
                raise RuntimeError('No text extracted.')
            task.log_info('SKIP (ERROR): ' + file_name)
            return None

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

        # detect tables
        # if kwargs.get('detect_tables') and ext == '.pdf':
        if ext == '.pdf':
            try:
                document_tables = tabula.read_pdf(
                    file_path,
                    multiple_tables=True,
                    pages='all')
                metadata['tables'] = [
                    [list(j) for j in list(i.fillna('').to_records(index=False)) if not i.empty]
                    for i in document_tables if not i.empty]
            except CalledProcessError:
                pass

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
                metadata=metadata,
                language=language,
                title=title,
                file_size=file_size,
                full_text=text)

            task.log_extra['log_document_id'] = document.pk

            # create Document Properties
            document_properties = [
                DocumentProperty(
                    created_by_id=user_id,
                    modified_by_id=user_id,
                    document_id=document.pk,
                    key=k,
                    value=v) for k, v in metadata.items() if v]

            try:
                polarity, subjectivity = TextBlob(text).sentiment
                document_properties += [
                    DocumentProperty(
                        created_by_id=user_id,
                        modified_by_id=user_id,
                        document_id=document.pk,
                        key='polarity',
                        value=str(round(polarity, 3))),
                    DocumentProperty(
                        created_by_id=user_id,
                        modified_by_id=user_id,
                        document_id=document.pk,
                        key='subjectivity',
                        value=str(round(subjectivity, 3)))]
            except AttributeError:
                pass
            DocumentProperty.objects.bulk_create(document_properties)

            # create text units
            paragraph_list = []  # type: List[TextUnit]
            paragraphs = LoadDocuments.safely_get_paragraphs(text)
            for paragraph, pos_start, post_end in paragraphs:
                ptr = TextUnit(
                    document=document,
                    text=paragraph,
                    unit_type="paragraph",
                    location_start=pos_start,
                    location_end=post_end)
                ptr.language = get_language(paragraph)
                ptr.text_hash = hashlib.sha1(paragraph.encode("utf-8")).hexdigest()
                paragraph_list.append(ptr)

            sentence_list = []
            for span in get_sentence_span_list(text):
                sentence = text[span[0]:span[1]]
                text_unit = TextUnit(
                    document=document,
                    text=sentence,
                    location_start=span[0],
                    location_end=span[1],
                    text_hash=hashlib.sha1(sentence.encode("utf-8")).hexdigest(),
                    unit_type="sentence",
                    language=get_language(sentence))
                sentence_list.append(text_unit)

            document.paragraphs = len(paragraph_list)
            document.sentences = len(sentence_list)
            document.save()

            TextUnit.objects.bulk_create(paragraph_list + sentence_list)

            # store document language
            if not document.language:
                document.set_language_from_text_units()

            # create Text Unit Properties
            from apps.document.app_vars import LOCATE_TEXTUNITPROPERTIES
            if LOCATE_TEXTUNITPROPERTIES.val:
                text_unit_properties = []
                for pk, text in document.textunit_set.values_list('pk', 'text'):
                    try:
                        polarity, subjectivity = TextBlob(text).sentiment
                        text_unit_properties += [
                            TextUnitProperty(
                                text_unit_id=pk,
                                key='polarity',
                                value=str(round(polarity))),
                            TextUnitProperty(
                                text_unit_id=pk,
                                key='subjectivity',
                                value=str(round(subjectivity)))]
                    except AttributeError:
                        continue
                if text_unit_properties:
                    TextUnitProperty.objects.bulk_create(text_unit_properties)

            # save extra document info
            kwargs['document'] = document
        LoadDocuments.save_extra_document_data(**kwargs)

        task.log_info(message='LOADED (%s): %s' % (parser_name.upper(), file_name))
        task.log_info(message='Document pk: %d' % document.pk)

        # call post processing task
        linked_tasks = kwargs.get('linked_tasks') or list()  # type: List[Dict[str, Any]]

        if should_run_standard_locators:
            task.run_sub_tasks_class_based('Locate', Locate, [{
                'locate': LoadDocuments.standard_locators,
                'parse': 'sentences',
                'do_delete': False,
                'session_id': upload_session_id,
                'metadata': {'session_id': upload_session_id, 'file_name': file_name},
                'user_id': user_id,
                'document_id': document.pk,
                'doc_loaded_by_user_id': user_id,
                'document_initial_load': True,
                'predefined_field_codes_to_python_values': pre_defined_doc_fields_code_to_python_val
            }])
        else:
            if pre_defined_doc_fields_code_to_python_val:
                user = User.objects.get(pk=user_id) if user_id is not None else None
                Locate. \
                    store_pre_defined_doc_fields(log=CeleryTaskLogger(task),
                                                 doc=document,
                                                 user=user,
                                                 fields_code_to_python_val=pre_defined_doc_fields_code_to_python_val)

        for linked_task_kwargs in linked_tasks:
            linked_task_kwargs['document_id'] = document.pk
            linked_task_kwargs['source_data'] = task.task.source_data
            linked_task_id = call_task(**linked_task_kwargs)
            task.log_info(message='linked_task_id: {}'.format(linked_task_id))
            ret.append({'linked_task_id': linked_task_id,
                        'document_id': document.pk})

        if return_doc_id:
            return document.pk
        else:
            return json.dumps(ret) if ret else None

    @staticmethod
    def get_text_from_file(file_name: str,
                           file_path: str,
                           propagate_exceptions: bool,
                           task: ExtendedTask):
        """
        extract text from file using either Tika or Textract
        """
        from apps.document.app_vars import OCR_ENABLE, OCR_FILE_SIZE_LIMIT
        ocr_enabled = OCR_ENABLE.val

        # disable OCR anyway if file size exceeds limit
        if ocr_enabled:
            fsize_limit = OCR_FILE_SIZE_LIMIT.val
            fsize = os.path.getsize(file_path)
            fsize /= 1024 * 1024
            ocr_enabled = ocr_enabled and fsize <= fsize_limit

        metadata = {}
        _fn, ext = os.path.splitext(file_name)
        if not ext:
            mt = python_magic.from_file(file_path)
            ext = mimetypes.guess_extension(mt)
        ext = ext or ''

        # decide can we parse the file with Textract
        textract_enabled = ocr_enabled or \
                           ext in settings.TEXTRACT_NON_OCR_EXTENSIONS
        first_try_textract = textract_enabled and \
                             ext in settings.TEXTRACT_FIRST_FOR_EXTENSIONS

        if first_try_textract:
            text, parser_name = LoadDocuments.try_parsing_with_textract(
                task, file_path, ext, file_name)
            if not text:
                text, parser_name, metadata = LoadDocuments.try_parsing_with_tika(
                    task, file_path, file_name,
                    enable_ocr=ocr_enabled)
        else:
            text, parser_name, metadata = LoadDocuments.try_parsing_with_tika(
                task, file_path, file_name,
                propagate_exceptions=propagate_exceptions,
                enable_ocr=ocr_enabled)
            if not text and textract_enabled:
                text, parser_name = LoadDocuments.try_parsing_with_textract(
                    task, file_path, ext, file_name,
                    propagate_exceptions=propagate_exceptions)

        if text is not None:
            text = pre_process_document(text)
            # TODO: migrate it in lexnlp if it works good
            text = re.sub(r'<[\s/]*(?:[A-Za-z]+|[Hh]\d)[\s/]*>', '', text)
            text = text.replace('\r\n', '\n')
        return ext, metadata, parser_name, propagate_exceptions, text

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
            'text': tu.text,
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
        self.log_info('Parse "%s"' % real_fn or path)
        data = pd.read_csv(path)
        self.log_info('Detected %d terms' % len(data))
        return terms_df.append(data)

    def process(self, **kwargs):
        """
        Load Terms
        :param kwargs: dict, form data
        :return:
        """

        self.set_push_steps(3)

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

        terms_count = load_terms(terms_df)
        self.log_info('Total %d unique terms' % terms_count)

        self.push()

        self.log_info('Caching term stems for Locate tasks...')
        dict_data_cache.cache_term_stems()

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
        self.log_info('Parse "%s"' % real_fn or path)
        data = pd.read_csv(path)
        self.log_info('Detected %d entities' % len(data))
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
        self.log_info('Parse "%s"' % real_fn or path)
        dictionary_data = pd.read_csv(path)
        courts_count = load_courts(dictionary_data)
        self.log_info('Detected %d courts' % courts_count)

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
                self.log_info('Deleted {} {} objects'.format(
                    deleted[0], usage_model_name))
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
        available_locators = list(settings.REQUIRED_LOCATORS) + list(
            config.standard_optional_locators)
        locate = {i: j for i, j in locate.items() if i in available_locators}
        do_delete = [i for i in do_delete if i in available_locators]

        # delete ThingUsage and TextUnitTag(tag=thing)
        self.delete_existing_usages(do_delete, document_id, project_id)

        # interrupt if no items to locate
        if not locate:
            return

        # define number of async tasks
        if project_id:
            text_units = TextUnit.objects.filter(document__project__id=project_id)
        else:
            text_units = TextUnit.objects.all()

        if document_id:
            text_units = text_units.filter(document_id=document_id)
        locate_in = kwargs.get('parse')
        if locate_in == 'paragraphs':
            text_units = text_units.filter(unit_type='paragraph')
        elif locate_in == 'sentences':
            text_units = text_units.filter(unit_type='sentence')
        else:
            locate_in = 'paragraphs and sentences'

        self.log_info('Run location of [{}].'.format('; '.join(locate.keys())))
        self.log_info('Locate in [{}].'.format(locate_in))
        self.log_info('Found {0} Text Units.'.format(text_units.count()))

        locate_args = []
        text_unit_package = []
        text_unit_packages = []

        for text_unit_id in text_units.values_list('pk', flat=True):
            if not text_unit_id:
                continue
            if settings.TEXT_UNITS_TO_PARSE_PACKAGE_SIZE <= len(text_unit_package):
                text_unit_packages.append(text_unit_package)
                text_unit_package = []
            text_unit_package.append(text_unit_id)

        if len(text_unit_package) > 0:
            text_unit_packages.append(text_unit_package)

        for text_unit_package in text_unit_packages:
            locate_args.append((text_unit_package, kwargs['user_id'], locate))

        self.run_sub_tasks('Locate Data In Each Text Unit', Locate.parse_text_units,
                           locate_args)

        if document_id:
            document_ids = [document_id]
        elif project_id:
            document_ids = Document.objects.filter(
                project_id=project_id).values_list('pk', flat=True)
        else:
            return
        for document_id in document_ids:
            self.run_after_sub_tasks_finished(
                'Cache Generic Document Data',
                Locate.on_locate_finished,
                [(document_id, doc_loaded_by_user_id, document_initial_load,
                  predefined_field_codes_to_python_values)])

    @staticmethod
    def store_pre_defined_doc_fields(log: ProcessLogger,
                                     doc: Document,
                                     user: User,
                                     fields_code_to_python_val: Dict[str, Any]):
        if not fields_code_to_python_val:
            return

        document_type = doc.document_type  # type: DocumentType

        all_fields = {f.code: f for f in DocumentField.objects.filter(document_type=document_type).all()}

        for field_code, python_val in fields_code_to_python_val.items():
            field = all_fields.get(field_code)  # type: DocumentField
            if not field:
                log.error('Refusing to store pre-defined document field value for field {0}.\n'
                          'Document type {1} does not have such field'.format(field_code, document_type.code))
                continue
            if field.requires_text_annotations:
                log.error('Refusing to store pre-defined document field value for field {0}.\n'
                          'The field requires text annotation.'.format(field_code, document_type.code))
                continue

            field_type = field.get_field_type()  # type: FieldType
            field_type.save_value(document=doc, field=field, location_start=None, location_end=None, location_text=None,
                                  text_unit=None, value=python_val, user=user, allow_overwriting_user_data=True,
                                  extraction_hint=None)

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
                           predefined_field_codes_to_python_values: Dict[str, Any] = None):
        try:
            doc = Document.all_objects.filter(pk=doc_id).last()
        except Exception as e:
            raise RuntimeError(f'on_locate_finished(doc_id={doc_id}): ' +
                               f'error obtaining document.\n{str(e)}')

        if doc:
            try:
                log = CeleryTaskLogger(_self)
            except Exception as e:
                er_msg = f'on_locate_finished(): ' + \
                         f'error obtaining CeleryTaskLogger.\n{str(e)}'
                raise RuntimeError(er_msg)
            try:
                user = User.objects.get(pk=doc_loaded_by_user_id) \
                    if doc_loaded_by_user_id is not None \
                    else User.objects.filter(id=1).first()  # type: User
            except Exception as e:
                er_msg = f'on_locate_finished(user_id={doc_loaded_by_user_id}): ' + \
                         f'error obtaining user.\n{str(e)}'
                raise RuntimeError(er_msg)

            # INFO: see CS-3420: FE team has implemented uploading documents as non-admin (CS-3361)
            # if not user or not user.is_admin:
            #     raise Exception('User who is loading the document is unspecified and the first user in '
            #                     'the system is not admin. Something is wrong.')
            if predefined_field_codes_to_python_values:
                try:
                    Locate.store_pre_defined_doc_fields(log=log,
                                                        doc=doc,
                                                        user=user,
                                                        fields_code_to_python_val=predefined_field_codes_to_python_values)
                except Exception as e:
                    er_msg = f'on_locate_finished(doc_id={doc_id}): ' + \
                             f'error storing doc fields.\n{str(e)}'
                    raise RuntimeError(er_msg)
                try:
                    ignore_field_codes = predefined_field_codes_to_python_values.keys()
                except Exception as e:
                    er_msg = f'on_locate_finished(doc_id={doc_id}): ' + \
                             f'error accessing predefined_field_codes_to_python_values keys().\n{str(e)}'
                    raise RuntimeError(er_msg)
            else:
                ignore_field_codes = None

            try:
                field_value_cache.cache_generic_values(doc, log=log, save=True, fire_doc_changed_event=False)
            except Exception as e:
                er_msg = f'on_locate_finished(doc_id={doc_id}): ' + \
                         f'error caching generic values.\n{str(e)}'
                raise RuntimeError(er_msg)
            try:
                detect_and_cache_field_values_for_document(log=log,
                                                           document=doc,
                                                           save=True,
                                                           clear_old_values=True,
                                                           ignore_field_codes=ignore_field_codes,
                                                           changed_by_user=user,
                                                           document_initial_load=document_initial_load)
            except Exception as e:
                er_msg = f'on_locate_finished(doc_id={doc_id}): ' + \
                         f'error detecting field values.\n{str(e)}'
                raise RuntimeError(er_msg)

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
        text_units = TextUnit.objects.filter(pk__in=text_unit_ids).values_list('pk', 'text', 'language')
        text_units = list(text_units)
        location_results = LocationResults()
        log = CeleryTaskLogger(self)
        for task_name, task_kwargs in locate.items():
            if task_name not in LOCATORS:
                raise Exception('Programming error. Unknown locator: {0}'.format(task_name))
            locator = LOCATORS[task_name]

            for text_unit_id, text, text_unit_lang in text_units:
                locator.try_parsing(log, location_results, text, text_unit_id, text_unit_lang, **task_kwargs)
        location_results.save(log, user_id)


# sample of custom task
class LocateTerms(BaseTask):
    """
    Locate terms in text units
    """
    name = 'Locate Terms'

    def process(self, **kwargs):
        """
        Locate terms
        :param kwargs:
        :return:
        """

        TextUnitClassifier.objects.filter(name__contains='by:terms').update(is_active=False)

        if kwargs['delete'] or kwargs['locate']:
            deleted = TermUsage.objects.all().delete()
            self.log_info('Deleted %d Term Usages' % deleted[0])

        if not kwargs['locate']:
            return

        self.log_info('Found {0} Terms. Added {0} subtasks.'.format(Term.objects.count()))

        create_ltu_args = []
        for lt in Term.objects.all():
            term = lt.term.lower()
            if term != lt.term and \
                    Term.objects.filter(term=term).exists():
                continue
            create_ltu_args.append((term, lt.id))
        self.run_sub_tasks('Create LTU For Each Term',
                           LocateTerms.create_ltu,
                           create_ltu_args)

    @staticmethod
    @shared_task(base=ExtendedTask,
                 soft_time_limit=3600,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3
                 )
    def create_ltu(term, term_id):
        ltu_list = []

        for tu in TextUnit.objects.filter(
                unit_type='paragraph',
                text__iregex=r'([{}{}]{}s?|{}ies)[{}{}]'.format(
                    ''.join(string.punctuation),
                    ''.join(string.whitespace),
                    term,
                    term[:-1],
                    ''.join(string.punctuation),
                    ''.join(string.whitespace))).iterator():
            ltu = TermUsage()
            ltu.text_unit = tu
            ltu.term_id = term_id
            tu_count = tu.text.lower().count(term)
            if term.endswith('y'):
                tu_count += tu.text.lower().count(term[:-1] + 'ies')
            ltu.count = tu_count
            ltu_list.append(ltu)

        TermUsage.objects.bulk_create(ltu_list)


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

        class_name = kwargs['class_name']

        min_confidence = kwargs['min_confidence'] / 100

        if classifier_id is None and kwargs.get('delete_classifier'):
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

        for d in Document.objects.all()[:kwargs['sample_size']]:
            # Build document feature matrix
            d_text_units = d.textunit_set.all()
            text_unit_ids = d_text_units.values_list('id', flat=True)
            text_unit_count = len(text_unit_ids)
            test_features = np.zeros((text_unit_count,
                                      len(clf_model.term_index)))
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
    verbose = True
    n_features = 100
    self_name_len = 3

    cluster_map = {
        'documents': {
            'source_model': Document,
            'cluster_model': DocumentCluster,
            'property_lookup': 'documentproperty',
            'lookup_map': dict(
                source_type='source_type',
                document_type='document_type',
                metadata='metadata',
                date='textunit__dateusage__date',
                definition='textunit__definitionusage__definition',
                duration='textunit__datedurationusage__duration_days',
                court='textunit__courtusage__court__name',
                currency_name='textunit__currencyusage__currency',
                currency_value='textunit__currencyusage__amount',
                term='textunit__termusage__term__term',
                party='textunit__partyusage__party__name',
                entity='textunit__geoentityusage__entity__name'),
            'filter_map': dict(
                source_type='source_type__isnull',
                document_type='document_type__isnull',
                metadata='metadata__isnull',
                court='textunit__courtusage__isnull',
                currency_name='textunit__currencyusage__isnull',
                currency_value='textunit__currencyusage__isnull',
                date='textunit__dateusage__isnull',
                definition='textunit__definitionusage__isnull',
                duration='textunit__datedurationusage__isnull',
                term='textunit__termusage__isnull',
                party='textunit__partyusage__isnull',
                entity='textunit__geoentityusage__isnull')
        },
        'text_units': {
            'source_model': TextUnit,
            'cluster_model': TextUnitCluster,
            'property_lookup': 'textunitproperty',
            'lookup_map': dict(
                source_type='document__source_type',
                document_type='document__document_type',
                metadata='document__metadata',
                court='courtusage__court__name',
                currency_name='currencyusage__currency',
                currency_value='currencyusage__amount',
                date='dateusage__date',
                definition='definitionusage__definition',
                duration='datedurationusage__duration_days',
                terms='termusage__term__term',
                party='partyusage__party__name',
                entity='geoentityusage__entity__name'),
            'filter_map': dict(
                source_type='document__source_type__isnull',
                document_type='document__document_type__isnull',
                metadata='document__metadata__isnull',
                court='courtusage__isnull',
                currency_name='currencyusage__isnull',
                currency_value='currencyusage__isnull',
                date='dateusage__isnull',
                definition='definitionusage__isnull',
                duration='datedurationusage__isnull',
                term='termusage__isnull',
                party='partyusage__isnull',
                entity='geoentityusage__isnull')
        },
    }

    def cluster(self, target, kwargs):
        """
        Cluster Documents or Text Units using chosen algorithm
        :param target: either 'text_units' or 'documents'
        :param kwargs: dict, form data
        :return:
        """
        cluster_name = kwargs['name']
        cluster_desc = kwargs['description']
        using = kwargs['using']
        n_clusters = kwargs['n_clusters']
        cluster_by = kwargs['cluster_by']
        cluster_by_str = ', '.join(sorted(cluster_by))

        target_attrs = self.cluster_map[target]
        source_model = target_attrs['source_model']
        cluster_model = target_attrs['cluster_model']
        lookup_map = target_attrs['lookup_map']
        filter_map = target_attrs['filter_map']

        # step #1 - delete
        if kwargs['delete_type']:
            cluster_model.objects.filter(cluster_by=cluster_by_str, using=using).delete()
        if kwargs['delete']:
            cluster_model.objects.all().delete()
        self.push()

        # step #2 - prepare data
        # filter objects
        q_object = Q()
        for c in cluster_by:
            q_object.add(Q(**{filter_map[c]: False}), Q.OR)
        objects = source_model.objects.filter(q_object).distinct()
        self.push()

        # prepare features dataframe
        df = pd.DataFrame()
        for cluster_by_item in cluster_by:

            id_field = 'id'
            prop_field = lookup_map[cluster_by_item]
            count_as_bool = cluster_by_item == 'metadata'

            if count_as_bool:
                ann_cond = dict(prop_count=Case(
                    When(**{prop_field + '__isnull': False},
                         then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField()))
            else:
                ann_cond = dict(prop_count=Count(prop_field))
            qs = objects.values(id_field, prop_field).annotate(**ann_cond).distinct()
            if not qs:
                continue

            if cluster_by_item == 'metadata':
                qs_ = list(qs)
                qs = []
                for item in qs_:
                    for k, v in item[prop_field].items():
                        qs.append({
                            'id': item['id'],
                            prop_field: '%s: %s' % (k, str(v)),
                            'prop_count': 1})

            df_ = pd.DataFrame(list(qs)).dropna()

            # use number of days since min value as feature value
            if cluster_by_item == 'date':
                min_value = df_[prop_field].min().toordinal() - 1
                df_['prop_count'] = df_.apply(lambda x: x[prop_field].toordinal() - min_value,
                                              axis=1)

            # use amount value as feature value
            elif cluster_by_item in ['duration', 'currency_value']:
                df_['prop_count'] = df_.apply(lambda x: x[prop_field], axis=1)

            dft = df_.pivot(index=id_field, columns=prop_field, values='prop_count')
            dft.columns = ["%s(%s)" % (cluster_by_item, str(i)) for i in dft.columns]
            df = df.join(dft, how='outer')

        if df.empty:
            self.log_info('Empty data set. Exit.')
            return

        X = df.fillna(0).values.tolist()
        y = df.index.tolist()
        feature_names = df.columns.tolist()
        self.push()

        # step #4 - get model, clustering
        created_date = datetime.datetime.now()
        m = self.get_model(**kwargs)

        if using == 'LabelSpreading':
            # TODO: simplify
            objects_with_prop = {pk: prop for pk, prop in objects.filter(
                **{'{}__key'.format(target_attrs['property_lookup']): kwargs[
                    'ls_%s_property' % target]})
                .values_list('pk', '{}__value'.format(target_attrs['property_lookup']))
                .order_by('pk').distinct('pk')}
            prop_map = {n: prop for n, prop in enumerate(set(objects_with_prop.values()))}
            prop_map_rev = {prop: n for n, prop in prop_map.items()}
            objects_with_prop_n = {pk: prop_map_rev[prop] for pk, prop in objects_with_prop.items()}
            y = [objects_with_prop_n.get(i, -1) for i in objects.values_list('pk', flat=True)]
            m.fit(X, y)
            labeled = {pk: prop_map[m.transduction_[n]] for n, pk in
                       enumerate(objects.values_list('pk', flat=True))
                       if y[n] != -1}
            for cluster_id, cluster_label in enumerate(set(labeled.values())):
                cluster = cluster_model.objects.create(
                    cluster_id=cluster_id,
                    name=cluster_name,
                    self_name=cluster_label,
                    description=cluster_desc,
                    cluster_by=cluster_by_str,
                    using=using,
                    created_date=created_date)
                getattr(cluster, target).set(
                    [pk for pk, label in labeled.items() if label == cluster_label])

        else:
            m.fit(X)
            if using == 'DBSCAN':
                labels = m.labels_
                unique_labels = set(labels)
                if unique_labels == {-1}:
                    self.log_info('Unable to cluster, perhaps because of small data set.')
                    self.push()
                    return
                for cluster_id in unique_labels:
                    if cluster_id == -1:
                        continue
                    cluster_index = np.where(labels == cluster_id)[0]
                    cluster_self_name = 'cluster-{}'.format(cluster_id + 1)
                    cluster = cluster_model.objects.create(
                        cluster_id=cluster_id + 1,
                        name=cluster_name[:100],
                        self_name=cluster_self_name[:100],
                        description=cluster_desc[:200],
                        cluster_by=cluster_by_str[:100],
                        using=using,
                        created_date=created_date)
                    getattr(cluster, target).set([y[i] for i in cluster_index])
            else:
                if using == 'Birch':
                    order_centroids = m.subcluster_centers_.argsort()[:, ::-1]
                else:
                    order_centroids = m.cluster_centers_.argsort()[:, ::-1]

                # create clusters
                for cluster_id in range(n_clusters):
                    pks = [y[n] for n, label_id in enumerate(m.labels_.tolist())
                           if label_id == cluster_id]
                    if not pks:
                        continue
                    cluster_self_name = '>'.join(
                        [str(feature_names[j]) for j in
                         order_centroids[cluster_id, :self.self_name_len]])
                    cluster = cluster_model.objects.create(
                        cluster_id=cluster_id + 1,
                        name=cluster_name[:100],
                        self_name=cluster_self_name[:100],
                        description=cluster_desc[:200],
                        cluster_by=cluster_by_str[:100],
                        using=using[:20],
                        created_date=created_date)
                    getattr(cluster, target).set(pks)
        self.push()

    def get_model(self, **kwargs):
        using = kwargs['using']
        n_clusters = kwargs['n_clusters']
        if using == 'MiniBatchKMeans':
            m = MiniBatchKMeans(
                n_clusters=n_clusters,
                init='k-means++',
                max_iter=kwargs['kmeans_max_iter'],
                batch_size=kwargs['mb_kmeans_batch_size'],
                n_init=3,
                verbose=self.verbose)
        elif using == 'KMeans':
            m = KMeans(
                n_clusters=n_clusters,
                init='k-means++',
                max_iter=kwargs['kmeans_max_iter'],
                n_init=kwargs['kmeans_n_init'],
                verbose=self.verbose)
        elif using == 'Birch':
            m = Birch(
                n_clusters=n_clusters,
                threshold=kwargs['birch_threshold'],
                branching_factor=kwargs['birch_branching_factor'])
        elif using == 'DBSCAN':
            m = DBSCAN(
                eps=kwargs['dbscan_eps'],
                min_samples=5,
                leaf_size=kwargs['dbscan_leaf_size'],
                p=kwargs['dbscan_p'])
        elif using == 'LabelSpreading':
            m = LabelSpreading(
                max_iter=kwargs['ls_max_iter'])
        else:
            raise RuntimeError('Clustering method is not defined')
        return m

    def process(self, **kwargs):

        do_cluster_documents = kwargs['do_cluster_documents']
        do_cluster_text_units = kwargs['do_cluster_text_units']

        self.set_push_steps(8 if do_cluster_documents and do_cluster_text_units else 4)

        # cluster Documents
        if do_cluster_documents:
            self.cluster('documents', kwargs)

        # cluster Text Units
        if do_cluster_text_units:
            self.cluster('text_units', kwargs)


@shared_task(name='advanced_celery.clean_tasks')
def clean_tasks(delta_days=2):
    """
    Clean Task and TaskResult
    """
    control_date = now() - datetime.timedelta(days=delta_days)
    logger.info('Clean tasks. Control date: {}'.format(control_date))

    removed_tasks = 0
    removed_task_results = 0
    for task in Task.objects.all():
        logger.info('Task="{}", status="{}", date_start="{}"'.format(
            task.name, task.status, task.date_start))
        if task.status == 'PENDING' or task.date_start > control_date:
            logger.info('skip...')
        else:
            logger.info('remove...')
            # remove subtasks
            res = Task.objects \
                .filter(Q(main_task_id=task.id) |
                        Q(id=task.id)) \
                .delete()
            removed_task_results += res[0]
            # remove task
            task.delete()
            removed_tasks += 1

    ret = 'Deleted %d Tasks and %d TaskResults' % (removed_tasks, removed_task_results)
    logger.info(ret)
    return ret


@app.task(name='advanced_celery.track_tasks', bind=True)
def track_tasks(self):
    TaskUtils.prepare_task_execution()

    for task in Task.objects.unready_main_tasks():
        Task.objects.update_main_task(task.id)

    # search for pending sequential tasks and start them
    for task in Task.objects \
            .succeed_main_tasks() \
            .filter(sequential_tasks__isnull=False,
                    sequential_tasks_started=False):
        task.sequential_tasks_started = True
        task.save()
        for seq_task_kwargs in task.sequential_tasks:
            try:
                for required_parent_kwarg in seq_task_kwargs.get('required_parent_task_kwargs', []):
                    kw = task.kwargs.get(required_parent_kwarg, 'none')
                    if kw == 'none':
                        raise RuntimeError('Missed "%s" required parent task kwarg'
                                           % required_parent_kwarg)
                    seq_task_kwargs[required_parent_kwarg] = kw
            except RuntimeError:
                continue
            call_task(**seq_task_kwargs)


@app.task(name='advanced_celery.clean_sub_tasks', bind=True)
def clean_sub_tasks(self):
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
    del_ready_tasks_date = now() - datetime.timedelta(seconds=settings.REMOVE_READY_TASKS_DELAY_IN_SEC)
    Task.objects \
        .filter(name__in=settings.REMOVE_WHEN_READY, date_done__lt=del_ready_tasks_date) \
        .delete()


def purge_task(task_pk, wait=False, timeout=None):
    """
    Purge task method.
    :param task_pk:
    :param wait:
    :param timeout
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
    ret = 'Deleted '

    # delete TaskResults for subtasks
    subtask_results_deleted = task.subtasks.delete()

    # delete Task
    task.delete()

    ret += 'Task(id={}), TaskHistory, '.format(task.pk)

    ret += 'main celery task, children celery tasks, {} TaskResult(s)'.format(
        subtask_results_deleted[0] + 1)

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


# Register all load tasks
app.register_task(LoadDocuments())
app.register_task(LoadTerms())
app.register_task(LoadGeoEntities())
app.register_task(LoadCourts())

# Register all locate tasks
app.register_task(Locate())
app.register_task(LocateTerms())

# Register all update/cluster/classify tasks
app.register_task(UpdateElasticsearchIndex())
app.register_task(TotalCleanup())
app.register_task(Classify())
app.register_task(Cluster())
