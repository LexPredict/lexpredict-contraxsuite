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
import json
import math
import mimetypes
import os
import pickle
import string
import sys
import traceback
from copy import deepcopy
from traceback import format_exc
from typing import List, Dict, Tuple, Any, Callable

# Additional libraries
import fuzzywuzzy.fuzz
import geocoder
import magic
import nltk
import numpy as np
import pandas as pd
import tabula
from celery import app
# Celery imports
from celery import shared_task, chord, chain
from celery.exceptions import SoftTimeLimitExceeded, TimeLimitExceeded, Retry
from celery.result import AsyncResult
# Django imports
from celery.states import READY_STATES, SUCCESS
from celery.utils.log import get_task_logger
from constance import config
from django.conf import settings
from django.db import transaction
from django.db.models import Count, Q, Case, Value, When, IntegerField, Subquery
from django.db.utils import IntegrityError, DataError
from django.utils.timezone import now
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
from lexnlp.extract.en import (
    amounts, citations, copyright, courts, dates, distances, definitions,
    durations, geoentities, money, percents, ratios, regulations, trademarks, urls,
    dict_entities)
from lexnlp.extract.en.contracts.detector import is_contract
from lexnlp.extract.en.entities.nltk_maxent import get_companies
from lexnlp.nlp.en.segments.sentences import get_sentence_span_list, pre_process_document
from lexnlp.nlp.en.segments.titles import get_titles
from lexnlp.nlp.en.tokens import get_stems, get_token_list
# Scikit-learn imports
from sklearn.cluster import Birch, DBSCAN, KMeans, MiniBatchKMeans
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegressionCV
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.naive_bayes import MultinomialNB
from sklearn.semi_supervised import LabelSpreading
from sklearn.svm import SVC
from textblob import TextBlob
from tika import parser
from psycopg2 import InterfaceError, OperationalError

# Project imports
import settings
from apps.analyze.models import (
    DocumentCluster, TextUnitCluster,
    DocumentSimilarity, TextUnitSimilarity, PartySimilarity as PartySimilarityModel,
    TextUnitClassification, TextUnitClassifier, TextUnitClassifierSuggestion)
from apps.celery import app
from apps.common.advancedcelery.db_cache import DbCache
from apps.common.advancedcelery.fileaccess.local_file_access import LocalFileAccess
from apps.common.advancedcelery.fileaccess.nginx_http_file_access import NginxHttpFileAccess
from apps.common.utils import fast_uuid
from apps.document.models import (
    Document, DocumentProperty, DocumentType, TextUnit, TextUnitProperty, TextUnitTag)
from apps.extract import models as extract_models
from apps.extract.models import (
    AmountUsage, CitationUsage, CopyrightUsage,
    Court, CourtUsage, CurrencyUsage,
    DateDurationUsage, DateUsage, DefinitionUsage, DistanceUsage,
    GeoAlias, GeoAliasUsage, GeoEntity, GeoEntityUsage, GeoRelation,
    PercentUsage, RatioUsage, RegulationUsage,
    Party, PartyUsage, Term, TermUsage, TrademarkUsage, UrlUsage)
from apps.project.models import Project, UploadSession
from apps.task.celery_backend.task_utils import revoke_task
from apps.task.models import Task, TaskConfig
from apps.task.utils.nlp.lang import get_language
from apps.task.utils.ocr.textract import textract2text
from apps.task.utils.task_utils import TaskUtils
from apps.task.utils.text.segment import segment_paragraphs

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.3/LICENSE"
__version__ = "1.1.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

# Logger setup
this_module = sys.modules[__name__]
logger = get_task_logger(__name__)

# TODO: Configuration-based and language-based stemmer.

# Create global stemmer
stemmer = nltk.stem.porter.PorterStemmer()

# singularizer
wnl = nltk.stem.WordNetLemmatizer()

# TODO: Configuration-based and language-based punctuation.
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

python_magic = magic.Magic(mime=True)

es = Elasticsearch(hosts=settings.ELASTICSEARCH_CONFIG['hosts'])


def prepare_file_access_handler():
    access_type = settings.CELERY_FILE_ACCESS_TYPE
    if access_type == 'Local':
        return LocalFileAccess(settings.CELERY_FILE_ACCESS_LOCAL_ROOT_DIR)
    elif access_type == 'Nginx':
        return NginxHttpFileAccess(settings.CELERY_FILE_ACCESS_NGINX_ROOT_URL)
    else:
        return None


file_access_handler = prepare_file_access_handler()


def _get_or_create_task_config(celery_task) -> TaskConfig:
    return TaskConfig.objects.get_or_create(defaults={
        'name': celery_task.name,
        'soft_time_limit': celery_task.soft_time_limit
    }, name=celery_task.name)[0]


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

    # We can't cache task field, because it should be always actual but we can cache some static values
    _cached_data = None

    @property
    def task(self) -> Task:
        return Task.objects.get(id=self.request.id)

    @property
    def task_name(self) -> str:
        return self.name

    @property
    def log_extra(self) -> Dict:
        return self.task.log_extra

    @log_extra.setter
    def log_extra(self, v: Dict):
        Task.objects.set_log_extra(self.request.id, v)

    def log_info(self, message, **kwargs):
        self.task.write_log(message, level='info', **kwargs)

    def log_error(self, message, **kwargs):
        self.task.write_log(message, level='error', **kwargs)

    def log_debug(self, message, **kwargs):
        self.task.write_log(message, level='debug', **kwargs)

    def log_warn(self, message, **kwargs):
        self.task.write_log(message, level='warn', **kwargs)

    def init_cache(self):
        if not self._cached_data:
            this_task = self.task
            self._cached_data = dict()
            self._cached_data['main_task_id'] = this_task.main_task_id

    @property
    def main_task_id(self):
        self.init_cache()
        return self._cached_data.get('main_task_id')

    def set_push_steps(self, value: int):
        Task.objects.set_push_steps(self.request.id, value)

    def push(self):
        Task.objects.push(self.request.id)

    def get_progress(self):
        return Task.objects.get(id=self.request.id).progress

    def update_progress(self, value: float):
        Task.objects.update_progress(self.request.id, int(value))

    def _render_task_failed(self, args, kwargs, exc, exception_trace) -> str:
        if isinstance(exc, SoftTimeLimitExceeded):
            problem_str = 'Soft time limit exceeded: {0} seconds'.format(
                self.request.timelimit[1] or self.soft_time_limit)
        elif isinstance(exc, TimeLimitExceeded):
            problem_str = 'Time limit exceeded: {0} seconds'.format(
                self.request.timelimit[0] or self.time_limit)
        else:
            problem_str = '{0}\n{1}'.format(exc, traceback.format_exc())

        return 'Task has been failed{4}:\n' \
               '{0}\n' \
               'Args: {1}\n' \
               'Kwargs: {2}\n' \
               'Reason: {3}'.format(self.name, str(args), str(kwargs), problem_str,
                                    ' (retry {0})'.format(
                                        self.request.retries) if self.request.retries else '')

    def chord(self, sub_tasks):
        self.log_info(
            '{0}: starting {1} sub-tasks...'.format(self.task_name, len(sub_tasks)))
        for ss in sub_tasks:
            ss.apply_async()

    def run_sub_tasks(self,
                      sub_tasks_group_title: str,
                      sub_task_function,
                      args_list: List[Tuple],
                      source_data: List[str]=None):
        """
        Asynchronously execute sub_task_method on each tuple of arguments from the provided list.

        :param sub_tasks_group_title:
        :param sub_task_function:
        :param args_list:
        :param source_data:
        :return:
        """
        sub_tasks = []
        task_config = _get_or_create_task_config(sub_task_function)
        for index, args in enumerate(args_list):
            sub_task_signature = sub_task_function.subtask(
                args=args,
                source_data=source_data[index] if source_data is not None else self.task.source_data,
                soft_time_limit=task_config.soft_time_limit,
                root_id=self.main_task_id,
                parent_id=self.request.id,
                title=sub_tasks_group_title)
            sub_tasks.append(sub_task_signature)

        self.chord(sub_tasks)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        TaskUtils.prepare_task_execution()
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


def call_task_func(task_func: Callable, task_args: Tuple,
                   user_id, source_data=None, metadata: Dict = None, visible: bool = True):
    celery_task_id = str(fast_uuid())

    task = Task.objects.create(
        id=celery_task_id,
        name=task_func.__name__,
        user_id=user_id,
        source_data=source_data,
        metadata=metadata,
        visible=visible if visible is not None else True,
    )

    task.write_log('Celery task id: {}\n'.format(celery_task_id))
    task_config = _get_or_create_task_config(task_func)
    task_func.apply_async(args=task_args,
                          task_id=celery_task_id,
                          soft_time_limit=task_config.soft_time_limit)
    return task.pk


def call_task(task_name, **options):
    """
    Call celery task by name
    :param task_name: str, task tane
    :param options: task params
    :return:
    """
    this_module_name = options.pop('module_name', __name__)
    _this_module = sys.modules[this_module_name]
    task_class = getattr(_this_module, task_name.replace(' ', ''))

    if task_name == 'LoadDocuments' \
            and 'metadata' in options and 'session_id' in options['metadata']:
        options['propagate_exception'] = True
        options['metadata']['propagate_exception'] = True

    celery_task_id = str(fast_uuid())

    project_id = options.get('project_id')
    session_id = options.get('session_id')
    task = Task.objects.create(
        id=celery_task_id,
        name=task_name,
        user_id=options.get('user_id'),
        metadata=options.get('metadata'),
        source_data=options.get('source_data'),
        visible=options.get('visible', True),
        project=Project.objects.get(pk=project_id) if project_id else None,
        upload_session=UploadSession.objects.get(pk=session_id) if session_id else None
    )

    task.write_log('Celery task id: {}\n'.format(celery_task_id))
    options['task_id'] = task.id
    async = options.pop('async', True)
    task_config = _get_or_create_task_config(task_class)
    if async:
        task_class().apply_async(kwargs=options,
                                 task_id=celery_task_id,
                                 soft_time_limit=task_config.soft_time_limit)
    else:
        task_class()(**options)
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
            self.log_info('End of main task "{0}", id={1}. '
                          'Sub-tasks may be still running.'.format(self.task_name,
                                                                   self.main_task_id))
        return ret or self.main_task_id


class LoadDocuments(BaseTask):
    """
    Load Document, i.e. create Document and TextUnit objects
    from uploaded document files in a given directory
    :param kwargs: task_id - Task id
                   source_path - (str) relative dir path in media/FILEBROWSER_DIRECTORY
                   delete - (bool) delete old objects
                   document_type - (DocumentType) f.e. lease.LeaseDocument
                   source_type - (str) f.e. "SEC data"
    :return:
    """
    name = 'Load Documents'

    def process(self, **kwargs):

        path = kwargs['source_data']
        self.log_info('Parse {0} at {1}'.format(path, file_access_handler))
        file_list = file_access_handler.list(path)

        self.log_info("Detected {0} files. Added {0} subtasks.".format(len(file_list)))

        if len(file_list) == 0:
            raise RuntimeError('Wrong file or directory name or directory is empty: {}'
                               .format(path))

        if kwargs.get('delete'):
            Document.objects.all().delete()

        # prevent transferring document type objects to sub-tasks
        document_type = kwargs.get('document_type')
        if document_type:
            kwargs['document_type_pk'] = document_type.pk
            del kwargs['document_type']
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
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3
                 )
    def create_document(task: ExtendedTask, uri: str, kwargs):
        with file_access_handler.get_local_fn(uri) as (fn, file_name):
            task.task.title = 'Load Document: {0}'.format(uri)
            task.log_extra = {'log_document_name': uri}
            return LoadDocuments.create_document_local(task, fn, uri, kwargs)

    @staticmethod
    def save_extra_document_data(*args, **kwargs):
        pass

    @staticmethod
    def try_parsing_with_tika(task: ExtendedTask, file_path, ext, original_file_name):
        task.log_info('Trying TIKA for file: ' + original_file_name)
        if settings.TIKA_DISABLE:
            task.log_info('TIKA is disabled in config')
            return None, None
        try:
            data = parser.from_file(file_path, settings.TIKA_SERVER_ENDPOINT) \
                if settings.TIKA_SERVER_ENDPOINT else parser.from_file(file_path)
            parsed = data['content']
            if parsed and len(parsed) >= 100:
                return parsed, 'tika'
            else:
                task.log_error('TIKA returned too small test for file: ' + original_file_name)
                return None, None
        except:
            task.log_error('Caught exception while trying to parse file with Tika:{0}\n{1}'
                           .format(original_file_name, format_exc()))
            return None, None

    @staticmethod
    def try_parsing_with_textract(task: ExtendedTask, file_path, ext, original_file_name):
        task.log_info('Trying Textract for file: ' + original_file_name)
        try:
            return textract2text(file_path, ext=ext), 'textract'
        except:
            task.log_info('Caught exception while trying to parse file with Textract: {0}\n{1}'
                          .format(original_file_name, format_exc()))
            return None, None

    @staticmethod
    def get_title(text):
        titles = list(get_titles(text))
        return titles[0] if titles else None

    @staticmethod
    def create_document_local(task: ExtendedTask, file_path, file_name, kwargs):

        ret = []
        document_name = os.path.basename(file_name)
        document_source = os.path.dirname(file_name)
        file_size = os.path.getsize(file_path)

        # OLD API: Check for existing record
        if kwargs['metadata'].get('session_id') is None and \
                Document.objects.filter(name=document_name, source=document_source).exists():
            task.log_info('SKIP (EXISTS): ' + file_name)
            return

        text = None  # type: str
        metadata = {}
        new_ui = kwargs.get('propagate_exception')

        _fn, ext = os.path.splitext(file_name)
        if not ext:
            mt = python_magic.from_file(file_path)
            ext = mimetypes.guess_extension(mt)

        ext = ext or ''

        if ext in settings.TEXTRACT_FIRST_FOR_EXTENSIONS:
            text, parser_name = LoadDocuments.try_parsing_with_textract(task, file_path, ext,
                                                                        file_name)
            if not text:
                text, parser_name = LoadDocuments.try_parsing_with_tika(task, file_path, ext,
                                                                        file_name)
        else:
            text, parser_name = LoadDocuments.try_parsing_with_tika(task, file_path, ext,
                                                                    file_name)
            if not text:
                text, parser_name = LoadDocuments.try_parsing_with_textract(task, file_path,
                                                                            ext, file_name)
        if text is not None:
            text = pre_process_document(text)

        if not text:
            if new_ui:
                raise RuntimeError('No text extracted.')
            task.log_info('SKIP (ERROR): ' + file_name)
            return

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
            document_tables = tabula.read_pdf(
                file_path,
                multiple_tables=True,
                pages='all')
            metadata['tables'] = [
                [list(j) for j in list(i.fillna('').to_records(index=False)) if not i.empty]
                for i in document_tables if not i.empty]

        # Language identification
        language, lang_detector = get_language(text, get_parser=True)
        if language:
            task.log_info('Detected language: %s' % language.upper())
            task.log_info('Language detector: %s' % lang_detector.upper())
        else:
            task.log_info('LANGUAGE IS NOT DETECTED: ' + file_name)

        # detect title
        title = metadata.get('title', None) or LoadDocuments.get_title(text)

        document_type = None

        document_type_pk = kwargs.get('document_type_pk')
        try:
            if document_type_pk:
                document_type = DocumentType.objects.get(pk=document_type_pk)
            else:
                document_type = DocumentType.generic()
        except:
            pass

        with transaction.atomic():
            # Create document object
            document = Document.objects.create(
                document_type=document_type,
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

            try:
                session = UploadSession.objects.get(pk=kwargs['metadata']['session_id'])
                task.log_extra['log_upload_session'] = session.pk
                document.upload_session = session
                document.project = session.project
                document.document_type = session.project.type
                document.save()
                task.log_info(message='Document Upload Session id={}'.format(session.pk))
            except:
                task.log_warn(message='Document Upload Session Undefined!')

            # create Document Properties
            document_properties = [
                DocumentProperty(
                    created_by_id=kwargs['user_id'],
                    modified_by_id=kwargs['user_id'],
                    document_id=document.pk,
                    key=k,
                    value=v) for k, v in metadata.items() if v]

            polarity, subjectivity = TextBlob(text).sentiment
            document_properties += [
                DocumentProperty(
                    created_by_id=kwargs['user_id'],
                    modified_by_id=kwargs['user_id'],
                    document_id=document.pk,
                    key='polarity',
                    value=str(round(polarity, 3))),
                DocumentProperty(
                    created_by_id=kwargs['user_id'],
                    modified_by_id=kwargs['user_id'],
                    document_id=document.pk,
                    key='subjectivity',
                    value=str(round(subjectivity, 3)))]
            DocumentProperty.objects.bulk_create(document_properties)

            # create text units
            paragraph_list = [TextUnit(
                document=document,
                text=paragraph,
                text_hash=hashlib.sha1(paragraph.encode("utf-8")).hexdigest(),
                unit_type="paragraph",
                language=get_language(paragraph)) for paragraph in segment_paragraphs(text)]

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
            text_unit_properties = []
            for pk, text in document.textunit_set.values_list('pk', 'text'):
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
            TextUnitProperty.objects.bulk_create(text_unit_properties)

            # save extra document info
            kwargs['document'] = document
            LoadDocuments.save_extra_document_data(**kwargs)

        task.log_info(message='LOADED (%s): %s' % (parser_name.upper(), file_name))
        task.log_info(message='Document pk: %d' % document.pk)

        # call post processing task
        linked_tasks = kwargs.get('linked_tasks', [])
        for linked_task_kwargs in linked_tasks:
            linked_task_kwargs['document_id'] = document.pk
            linked_task_kwargs['source_data'] = task.task.source_data
            linked_task_id = call_task(**linked_task_kwargs)
            task.log_info(message='linked_task_id: {}'.format(linked_task_id))
            ret.append({'linked_task_id': linked_task_id,
                        'document_id': document.pk})

        return json.dumps(ret) if ret else None


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

    def process(self, **kwargs):
        """
        Load Terms
        :param kwargs: dict, form data
        :return:
        """

        self.set_push_steps(3)

        paths = kwargs['repo_paths']

        if kwargs['file_path']:
            file_path = kwargs['file_path'].strip('/')
            path = os.path.join(settings.DATA_ROOT, file_path)
            if not os.path.exists(path):
                path = os.path.join(settings.MEDIA_ROOT,
                                    settings.FILEBROWSER_DIRECTORY,
                                    file_path)
            if not os.path.exists(path) or not os.path.isfile(path):
                raise RuntimeError('Unable to parse path "%s"' % path)
            paths.append(path)

        self.push()

        if kwargs['delete']:
            Term.objects.all().delete()
        self.push()

        terms_df = pd.DataFrame()
        for path in paths:
            self.log_info('Parse "%s"' % path)
            data = pd.read_csv(path)
            self.log_info('Detected %d terms' % len(data))
            terms_df = terms_df.append(data)

        terms_df.drop_duplicates(inplace=True)
        terms_df.loc[terms_df["CaseSensitive"] == False, "Term"] = terms_df.loc[
            terms_df["CaseSensitive"] == False, "Term"].str.lower()
        terms_df = terms_df.drop_duplicates(subset="Term").dropna(subset=["Term"])
        self.log_info('Total %d unique terms' % len(terms_df))

        terms = []
        for row_id, row in terms_df.iterrows():
            term = row["Term"].strip()
            if not Term.objects.filter(term=term).exists():
                lt = Term()
                lt.term = term
                lt.source = row["Term Category"]
                lt.definition_url = row["Term Locale"]
                terms.append(lt)

        Term.objects.bulk_create(terms)

        self.log_info('Caching term stems for Locate tasks...')
        Locate.cache_term_stems()

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

    def process(self, **kwargs):
        """
        Load Geopolitical Entities
        :param kwargs: form data
        :return:
        """
        paths = kwargs['repo_paths']
        if kwargs['file_path']:
            file_path = kwargs['file_path'].strip('/')
            path = os.path.join(settings.DATA_ROOT, file_path)
            if not os.path.exists(path):
                path = os.path.join(settings.MEDIA_ROOT,
                                    settings.FILEBROWSER_DIRECTORY,
                                    file_path)
            if not os.path.exists(path) or not os.path.isfile(path):
                raise RuntimeError('Unable to parse path "%s"' % path)
            paths.append(path)

        if kwargs['delete']:
            GeoEntity.objects.all().delete()
            GeoRelation.objects.all().delete()
            GeoAlias.objects.all().delete()

        entities_df = pd.DataFrame()
        for path in paths:
            self.log_info('Parse "%s"' % path)
            data = pd.read_csv(path)
            self.log_info('Detected %d entities' % len(data))
            entities_df = entities_df.append(data)
        if entities_df.empty:
            raise RuntimeError('Received 0 entities to process, exit.')
        entities_df = entities_df.drop_duplicates().fillna('')

        self.set_push_steps(len(entities_df) + 2)
        self.push()

        # create Geo Entities
        geo_aliases = []
        geo_entities_count = 0
        for _, row in entities_df.iterrows():
            entity_id = row['Entity ID']
            entity_name = row['Entity Name'].strip()
            entity_priority = row.get('Entity Priority')
            if entity_priority:
                try:
                    entity_priority = int(entity_priority)
                except ValueError:
                    entity_priority = 0
            else:
                entity_priority = 0

            if 'latitude' in row and row['latitude']:
                latitude = row['latitude']
                longitude = row['longitude']
            else:
                g = geocoder.google(entity_name)
                if not g.latlng and ',' in entity_name:
                    g = geocoder.google(entity_name.split(',')[0])
                latitude, longitude = g.latlng if g.latlng else (None, None)

            the_entity = GeoEntity.objects.filter(entity_id=entity_id)
            if the_entity.exists:
                the_entity.delete()

            entity = GeoEntity.objects.create(
                entity_id=entity_id,
                name=entity_name,
                priority=entity_priority,
                category=row['Entity Category'].strip(),
                latitude=latitude,
                longitude=longitude)
            geo_entities_count += 1

            for column_name, locale, alias_type in self.locales_map:
                if not row[column_name]:
                    continue
                geo_aliases.append(
                    GeoAlias(
                        entity=entity,
                        locale=locale,
                        alias=row[column_name],
                        type=alias_type))
            self.push()

        GeoAlias.objects.bulk_create(geo_aliases)
        self.log_info('Total created: %d GeoAliases' % len(geo_aliases))
        self.log_info('Total created: %d GeoEntities' % geo_entities_count)

        self.log_info('Caching geo config for Locate tasks...')
        Locate.cache_geo_config()

        self.push()


class LoadCourts(BaseTask):
    """
    Load Courts data from a file OR github repo
    """
    name = 'Load Courts'

    def process(self, **kwargs):
        """
        Load Courts data from a file OR github repo
        :param kwargs: dict, form data
        :return:
        """

        self.set_push_steps(3)

        paths = kwargs['repo_paths']

        if kwargs['file_path']:
            file_path = kwargs['file_path'].strip('/')
            path = os.path.join(settings.DATA_ROOT, file_path)
            if not os.path.exists(path):
                path = os.path.join(settings.MEDIA_ROOT,
                                    settings.FILEBROWSER_DIRECTORY,
                                    file_path)
            if not os.path.exists(path) or not os.path.isfile(path):
                raise RuntimeError('Unable to parse path "%s"' % path)
            paths.append(path)

        self.push()

        if 'delete' in kwargs:
            Court.objects.all().delete()
        self.push()

        for path in paths:
            self.log_info('Parse "%s"' % path)
            dictionary_data = pd.read_csv(path).dropna(subset=['Court ID']).fillna('')
            dictionary_data['Court ID'] = dictionary_data['Court ID'].astype(int)
            self.log_info('Detected %d courts' % len(dictionary_data))

            courts = []
            for _, row in dictionary_data.iterrows():
                if not Court.objects.filter(
                        court_id=row['Court ID'],
                        alias=row['Alias']).exists():
                    court = Court(
                        court_id=row['Court ID'],
                        type=row['Court Type'],
                        name=row['Court Name'],
                        level=row['Level'],
                        jurisdiction=row['Jurisdiction'],
                        alias=row['Alias']
                    )
                    courts.append(court)

            Court.objects.bulk_create(courts)
        self.log_info('Caching courts config for Locate tasks...')
        Locate.cache_court_config()
        self.push()


CACHE_KEY_GEO_CONFIG = 'geo_config'
CACHE_KEY_COURT_CONFIG = 'court_config'
CACHE_KEY_TERM_STEMS = 'term_stems'


class Locate(BaseTask):
    """
    Locate multiple items
    """
    name = "Locate"
    usage_model_map = dict(
        duration=['DateDurationUsage'],
        geoentity=['GeoEntityUsage', 'GeoAliasUsage']
    )

    @staticmethod
    def cache_geo_config(*args, **kwargs):

        geo_config = {}
        for name, pk, priority in GeoEntity.objects.values_list('name', 'pk', 'priority'):
            entity = dict_entities.entity_config(pk, name, priority or 0, name_is_alias=True)
            geo_config[pk] = entity
        for alias_id, alias_text, alias_type, entity_id, alias_lang \
                in GeoAlias.objects.values_list('pk', 'alias', 'type', 'entity', 'locale'):
            entity = geo_config[entity_id]
            if entity:
                is_abbrev = alias_type.startswith('iso') or alias_type.startswith('abbrev')
                dict_entities.add_aliases_to_entity(entity,
                                                    aliases_csv=alias_text,
                                                    language=alias_lang,
                                                    is_abbreviation=is_abbrev,
                                                    alias_id=alias_id)
        res = list(geo_config.values())
        DbCache.put_to_db(CACHE_KEY_GEO_CONFIG, res)

    @staticmethod
    def cache_court_config(*args, **kwargs):
        res = [dict_entities.entity_config(
            entity_id=i.id,
            name=i.name,
            priority=0,
            aliases=i.alias.split(';') if i.alias else []
        ) for i in Court.objects.all()]
        DbCache.put_to_db(CACHE_KEY_COURT_CONFIG, res)

    @staticmethod
    def cache_term_stems(*args, **kwargs):
        term_stems = {}
        for t, pk in Term.objects.values_list('term', 'pk'):
            stemmed_term = ' %s ' % ' '.join(get_stems(t))
            stemmed_item = term_stems.get(stemmed_term, [])
            stemmed_item.append([t, pk])
            term_stems[stemmed_term] = stemmed_item
        for item in term_stems:
            term_stems[item] = dict(values=term_stems[item],
                                    length=len(term_stems[item]))
        DbCache.put_to_db(CACHE_KEY_TERM_STEMS, term_stems)

    def delete_existing_usages(self, locator_names, document_id):
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
        self.delete_existing_usages(do_delete, document_id)

        # interrupt if no items to locate
        if not locate:
            return

        # define number of async tasks
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

        for text_unit_id, text, text_unit_lang in text_units.values_list('pk', 'text', 'language'):
            if not text_unit_id:
                continue
            if settings.TEXT_UNITS_TO_PARSE_PACKAGE_SIZE <= len(text_unit_package):
                text_unit_packages.append(text_unit_package)
                text_unit_package = []
            text_unit_package.append((text_unit_id, text_unit_lang, text))

        if len(text_unit_package) > 0:
            text_unit_packages.append(text_unit_package)

        for text_unit_package in text_unit_packages:
            locate_args.append((text_unit_package, kwargs['user_id'], locate))

        self.run_sub_tasks('Locate Data In Each Text Unit', Locate.parse_text_units,
                           locate_args)

        if kwargs.get('notify_task_done'):
            self.run_sub_tasks('Uploading Completed',
                               Locate.notify_task_done,
                               locate_args)

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=6000,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError,),
                 max_retries=3
                 )
    def parse_text_units(self: ExtendedTask, text_units, user_id, locate):
        tags = []
        self.set_push_steps(len(locate) + 1)
        for task_name, task_kwargs in locate.items():
            self.push()
            func_name = 'parse_%s' % task_name
            try:
                task_func = getattr(this_module, func_name)
            except AttributeError:
                self.log_error('Warning: "%s" method not found' % func_name)
                continue

            for text_unit_id, text_unit_lang, text in text_units:
                found = None
                try:
                    found = task_func(text, text_unit_id, text_unit_lang, **task_kwargs)
                except IntegrityError as e:
                    # just skip if duplicated values BUT keep log to investigate issue
                    if 'duplicate key value violates unique constraint' in str(e):
                        self.log_error('Function "%s" caused error:' % func_name)
                        self.log_error(str(e))
                        continue
                if found:
                    tag_name = found if not isinstance(found, bool) else task_name
                    tags.append((text_unit_id, tag_name))
        if tags:
            for text_unit_id, tag in tags:
                TextUnitTag.objects.get_or_create(
                    text_unit_id=text_unit_id,
                    tag=tag,
                    defaults=dict(user_id=user_id))


def parse_amount(text, text_unit_id, _text_unit_lang):
    found = list(amounts.get_amounts(text, return_sources=True, extended_sources=False))
    AmountUsage.objects.filter(text_unit_id=text_unit_id).delete()
    if found:
        unique = set(found)
        AmountUsage.objects.bulk_create(
            [AmountUsage(
                text_unit_id=text_unit_id,
                amount=item[0],
                amount_str=item[1][:300] if item[1] else None,
                count=found.count(item)
            ) for item in unique])
    return bool(found)


def parse_citation(text, text_unit_id, _text_unit_lang):
    found = list(citations.get_citations(text, return_source=True))
    CitationUsage.objects.filter(text_unit_id=text_unit_id).delete()
    if found:
        unique = set(found)
        unique_len = len(unique)
        for item in unique:
            try:
                CitationUsage.objects.create(
                    text_unit_id=text_unit_id,
                    volume=item[0],
                    reporter=item[1],
                    reporter_full_name=item[2],
                    page=item[3],
                    page2=item[4],
                    court=item[5],
                    year=item[6],
                    citation_str=item[7],
                    count=found.count(item))
            except DataError:
                unique_len -= 1
        return bool(unique_len)
    return False


def parse_court(text, text_unit_id, text_unit_lang, **kwargs):
    court_config = DbCache.get(CACHE_KEY_COURT_CONFIG)
    found = [dict_entities.get_entity_id(i[0])
             for i in courts.get_courts(text,
                                        court_config_list=court_config,
                                        text_languages=[text_unit_lang])]
    CourtUsage.objects.filter(text_unit_id=text_unit_id).delete()
    if found:
        unique = set(found)
        CourtUsage.objects.bulk_create(
            [CourtUsage(
                text_unit_id=text_unit_id,
                court_id=court_id,
                count=found.count(court_id)
            ) for court_id in unique])
    return bool(found)


def parse_distance(text, text_unit_id, _text_unit_lang):
    found = list(distances.get_distances(text, return_sources=True))
    DistanceUsage.objects.filter(text_unit_id=text_unit_id).delete()
    if found:
        unique = set(found)
        DistanceUsage.objects.bulk_create(
            [DistanceUsage(
                text_unit_id=text_unit_id,
                amount=item[0],
                amount_str=item[2],
                distance_type=item[1],
                count=found.count(item)
            ) for item in unique])
    return bool(found)


def parse_date(text, text_unit_id, _text_unit_lang, **kwargs):
    found = dates.get_dates_list(
        text,
        strict=kwargs.get('strict', False),
        return_source=False)
    DateUsage.objects.filter(text_unit_id=text_unit_id).delete()
    if found:
        unique = set([i.date() if isinstance(i, datetime.datetime) else i for i in found])
        DateUsage.objects.bulk_create(
            [DateUsage(
                text_unit_id=text_unit_id,
                date=item,
                count=found.count(item)
            ) for item in unique])
    return bool(found)


def parse_definition(text, text_unit_id, _text_unit_lang):
    found = list(definitions.get_definitions(text))
    DefinitionUsage.objects.filter(text_unit_id=text_unit_id).delete()
    if found:
        unique = set(found)
        DefinitionUsage.objects.bulk_create(
            [DefinitionUsage(
                text_unit_id=text_unit_id,
                definition=item,
                count=found.count(item)
            ) for item in unique])
    return bool(found)


def parse_duration(text, text_unit_id, _text_unit_lang):
    found = list(durations.get_durations(text, return_sources=True))
    DateDurationUsage.objects.filter(text_unit_id=text_unit_id).delete()
    if found:
        unique = set(found)
        DateDurationUsage.objects.bulk_create(
            [DateDurationUsage(
                text_unit_id=text_unit_id,
                amount=item[1],
                amount_str=item[3],
                duration_type=item[0],
                duration_days=item[2],
                count=found.count(item)
            ) for item in unique])
    return bool(found)


def parse_currency(text, text_unit_id, _text_unit_lang):
    found = list(money.get_money(text, return_sources=True))
    CurrencyUsage.objects.filter(text_unit_id=text_unit_id).delete()
    if found:
        unique = set(found)
        CurrencyUsage.objects.bulk_create(
            [CurrencyUsage(
                text_unit_id=text_unit_id,
                amount=item[0],
                amount_str=item[2],
                currency=item[1],
                count=found.count(item)
            ) for item in unique])
    return bool(found)


def parse_party(text, text_unit_id, _text_unit_lang):
    found = list(get_companies(text, count_unique=True, detail_type=True, name_upper=True))
    PartyUsage.objects.filter(text_unit_id=text_unit_id).delete()
    if found:
        pu_list = []
        for _party in found:
            name, _type, type_abbr, type_label, type_desc, count = _party
            defaults = dict(
                type=_type,
                type_label=type_label,
                type_description=type_desc
            )
            party, _ = Party.objects.get_or_create(
                name=name,
                type_abbr=type_abbr or '',
                defaults=defaults
            )
            pu_list.append(
                PartyUsage(text_unit_id=text_unit_id,
                           party=party,
                           count=count))
        PartyUsage.objects.bulk_create(pu_list)
    return bool(found)


def parse_percent(text, text_unit_id, _text_unit_lang):
    found = list(percents.get_percents(text, return_sources=True))
    PercentUsage.objects.filter(text_unit_id=text_unit_id).delete()
    if found:
        unique = set(found)
        PercentUsage.objects.bulk_create(
            [PercentUsage(
                text_unit_id=text_unit_id,
                amount=item[1],
                amount_str=item[3],
                unit_type=item[0],
                total=item[2],
                count=found.count(item)
            ) for item in unique])
    return bool(found)


def parse_ratio(text, text_unit_id, _text_unit_lang):
    found = list(ratios.get_ratios(text, return_sources=True))
    RatioUsage.objects.filter(text_unit_id=text_unit_id).delete()
    if found:
        unique = set(found)
        RatioUsage.objects.bulk_create(
            [RatioUsage(
                text_unit_id=text_unit_id,
                amount=item[0],
                amount2=item[1],
                amount_str=item[3],
                total=item[2],
                count=found.count(item)
            ) for item in unique])
    return bool(found)


def parse_regulation(text, text_unit_id, _text_unit_lang):
    found = list(regulations.get_regulations(text))
    RegulationUsage.objects.filter(text_unit_id=text_unit_id).delete()
    if found:
        unique = set(found)
        RegulationUsage.objects.bulk_create(
            [RegulationUsage(
                text_unit_id=text_unit_id,
                regulation_type=item[0],
                regulation_name=item[1],
                count=found.count(item)
            ) for item in unique])
    return bool(found)


def parse_copyright(text, text_unit_id, _text_unit_lang):
    found = list(copyright.get_copyright(text, return_sources=True))
    CopyrightUsage.objects.filter(text_unit_id=text_unit_id).delete()
    if found:
        unique = set(found)
        CopyrightUsage.objects.bulk_create(
            [CopyrightUsage(
                text_unit_id=text_unit_id,
                year=item[1],
                name=item[2][:200],
                copyright_str=item[3][:200],
                count=found.count(item)
            ) for item in unique if len(item[2]) < 100])
    return bool(found)


def parse_trademark(text, text_unit_id, _text_unit_lang):
    found = list(trademarks.get_trademarks(text))
    TrademarkUsage.objects.filter(text_unit_id=text_unit_id).delete()
    if found:
        unique = set(found)
        TrademarkUsage.objects.bulk_create(
            [TrademarkUsage(
                text_unit_id=text_unit_id,
                trademark=item,
                count=found.count(item)
            ) for item in unique])
    return bool(found)


def parse_url(text, text_unit_id, _text_unit_lang):
    found = list(urls.get_urls(text))
    UrlUsage.objects.filter(text_unit_id=text_unit_id).delete()
    if found:
        unique = set(found)
        UrlUsage.objects.bulk_create(
            [UrlUsage(
                text_unit_id=text_unit_id,
                source_url=item,
                count=found.count(item)
            ) for item in unique])
    return bool(found)


def parse_geoentity(text, text_unit_id, text_unit_lang, **kwargs):
    geo_config = DbCache.get(CACHE_KEY_GEO_CONFIG)
    priority = kwargs.get('priority', True)
    entity_alias_pairs = list(geoentities.get_geoentities(text,
                                                          geo_config,
                                                          text_languages=[text_unit_lang],
                                                          priority=priority))

    GeoEntityUsage.objects.filter(text_unit_id=text_unit_id).delete()
    GeoAliasUsage.objects.filter(text_unit_id=text_unit_id).delete()
    entity_ids = [dict_entities.get_entity_id(entity) for entity, _alias in entity_alias_pairs]
    if entity_ids:
        unique = set(entity_ids)
        GeoEntityUsage.objects.bulk_create([
            GeoEntityUsage(
                text_unit_id=text_unit_id,
                entity_id=idd,
                count=entity_ids.count(idd)) for idd in unique])

    alias_ids = [dict_entities.get_alias_id(alias) for _entity, alias in entity_alias_pairs]
    if alias_ids:
        unique = set(alias_ids)
        GeoAliasUsage.objects.bulk_create([
            GeoAliasUsage(
                text_unit_id=text_unit_id,
                alias_id=idd,
                count=alias_ids.count(idd)) for idd in unique if idd])

    return bool(entity_ids)


def parse_term(text, text_unit_id, _text_unit_lang, **kwargs):
    term_stems = DbCache.get(CACHE_KEY_TERM_STEMS)
    text_stems = ' %s ' % ' '.join(get_stems(text, lowercase=True))
    text_tokens = get_token_list(text, lowercase=True)
    term_usages = []
    for stemmed_term, data in term_stems.items():
        # stem not found in text
        if stemmed_term not in text_stems:
            continue
        # if stem has 1 variant only
        if data['length'] == 1:
            count = text_stems.count(stemmed_term)
            if count:
                term_data = list(data['values'][0])
                term_data.append(count)
                term_usages.append(term_data)
        # case when f.e. stem "respons" is equal to multiple terms
        # ["response", "responsive", "responsibility"]
        else:
            for term_data in data['values']:
                term_data = list(term_data)
                count = text_tokens.count(term_data[0])
                if count:
                    term_data.append(count)
                    term_usages.append(term_data)
                    # TODO: "responsibilities"

    TermUsage.objects.filter(text_unit_id=text_unit_id).delete()
    TermUsage.objects.bulk_create([
        TermUsage(
            text_unit_id=text_unit_id,
            term_id=pk,
            count=count) for _, pk, count in term_usages])
    return bool(term_usages)


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

        classifier_id = kwargs.get('classifier')
        min_confidence = kwargs['min_confidence'] / 100

        if classifier_id is None and kwargs.get('delete_classifier'):
            TextUnitClassifier.objects.filter(class_name=kwargs['class_name']).delete()

        if kwargs['delete_suggestions']:
            if classifier_id is None:
                filter_opts = {'class_name': kwargs['class_name']}
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


def stem_tokens(tokens):
    """
    Simple token stemmer.
    :param tokens:
    :return:
    """
    res = []
    for item in tokens:
        try:
            res.append(stemmer.stem(item))
        except IndexError:
            pass
    return res


def normalize(text):
    """
    Simple text normalizer returning stemmed, lowercased tokens.
    :param text:
    :return:
    """
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))


class PartySimilarity(BaseTask):
    """
    Task for the identification of similar party names.
    """
    name = 'Party Similarity'

    def process(self, **kwargs):
        """
        Task process method.
        :param kwargs: dict, form data
        """
        parties = Party.objects.values_list('pk', 'name')
        self.set_push_steps(len(parties) + 1)

        # 1. Delete if requested
        if kwargs['delete']:
            PartySimilarityModel.objects.all().delete()

        # 2. Select scorer
        scorer = getattr(fuzzywuzzy.fuzz, kwargs['similarity_type'])

        # 3. Iterate through all pairs
        similar_results = []
        for party_a_pk, party_a_name in parties:
            for party_b_pk, party_b_name in parties:
                if party_a_pk == party_b_pk:
                    continue

                # Calculate similarity
                if not kwargs['case_sensitive']:
                    party_a_name = party_a_name.upper()
                    party_b_name = party_b_name.upper()

                score = scorer(party_a_name, party_b_name)
                if score >= kwargs['similarity_threshold']:
                    similar_results.append(
                        PartySimilarityModel(
                            party_a_id=party_a_pk,
                            party_b_id=party_b_pk,
                            similarity=score))
            self.push()

        # 4. Bulk create similarity objects
        PartySimilarityModel.objects.bulk_create(similar_results)
        self.push()


class Similarity(BaseTask):
    """
    Find Similar Documents, Text Units
    """
    name = 'Similarity'
    verbose = True
    n_features = 100
    self_name_len = 3
    step = 2000

    def process(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

        search_similar_documents = kwargs['search_similar_documents']
        search_similar_text_units = kwargs['search_similar_text_units']
        similarity_threshold = kwargs['similarity_threshold']
        self.log_info('Min similarity: %d' % similarity_threshold)

        # get text units with min length 100 signs
        text_units = TextUnit.objects.filter(unit_type='paragraph',
                                             text__regex=r'.{100}.*')
        len_tu_set = text_units.count()

        push_steps = 0
        if search_similar_documents:
            push_steps += 4
        if search_similar_text_units:
            push_steps += math.ceil(len_tu_set / self.step) ** 2 + 3
        self.set_push_steps(push_steps)

        # similar Documents
        if search_similar_documents:

            # step #1 - delete
            if kwargs['delete']:
                DocumentSimilarity.objects.all().delete()
            self.push()

            # step #2 - prepare data
            texts_set = ['\n'.join(d.textunit_set.values_list('text', flat=True))
                         for d in Document.objects.all()]
            self.push()

            # step #3
            vectorizer = TfidfVectorizer(max_df=0.5, max_features=self.n_features,
                                         min_df=2, stop_words='english',
                                         use_idf=kwargs['use_idf'])
            X = vectorizer.fit_transform(texts_set)
            self.push()

            # step #4
            similarity_matrix = cosine_similarity(X) * 100
            pks = Document.objects.values_list('pk', flat=True)
            for x, document_a in enumerate(pks):
                # use it to search for unique a<>b relations
                # for y, document_b in enumerate(Document.objects.all()[x + 1:], start=x + 1):
                for y, document_b in enumerate(pks):
                    if document_a == document_b:
                        continue
                    similarity = similarity_matrix[x, y]
                    if similarity < similarity_threshold:
                        continue
                    DocumentSimilarity.objects.create(
                        document_a_id=document_a,
                        document_b_id=document_b,
                        similarity=similarity)
            self.push()

        # similar Text Units
        if search_similar_text_units:

            # step #1 - delete
            if kwargs['delete']:
                TextUnitSimilarity.objects.all().delete()
            self.push()

            # step #2 - prepare data
            texts_set, pks = zip(*text_units.values_list('text', 'pk'))
            self.push()

            # step #3
            vectorizer = TfidfVectorizer(tokenizer=normalize,
                                         max_df=0.5, max_features=self.n_features,
                                         min_df=2, stop_words='english',
                                         use_idf=kwargs['use_idf'])
            X = vectorizer.fit_transform(texts_set)
            self.push()

            # step #4
            for i in range(0, len_tu_set, self.step):
                for j in range(0, len_tu_set, self.step):
                    similarity_matrix = cosine_similarity(
                        X[i:min([i + self.step, len_tu_set])],
                        X[j:min([j + self.step, len_tu_set])]) * 100
                    for g in range(similarity_matrix.shape[0]):
                        tu_sim = [
                            TextUnitSimilarity(
                                text_unit_a_id=pks[i + g],
                                text_unit_b_id=pks[j + h],
                                similarity=similarity_matrix[g, h])
                            for h in range(similarity_matrix.shape[1]) if i + g != j + h and
                                                                          similarity_matrix[
                                                                              g, h] >= similarity_threshold]
                        TextUnitSimilarity.objects.bulk_create(tu_sim)
                    self.push()


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


@app.task(name='advanced_celery.clean_sub_tasks', bind=True)
def clean_sub_tasks(self):
    TaskUtils.prepare_task_execution()

    del_sub_tasks_date = now() - datetime.timedelta(seconds=60)

    # Delete sub-tasks of all main tasks finished more than a minute ago
    Task.objects \
        .filter(main_task__date_done__lt=del_sub_tasks_date,
                own_status__in=[SUCCESS]) \
        .delete()

    # Delete all completed system/periodic tasks from DB
    Task.objects.filter(name__in=Task.objects.EXCLUDE_FROM_TRACKING,
                        own_date_done__lt=del_sub_tasks_date).delete()


def purge_task(task_pk):
    """
    Purge task method.
    :param task_pk:
    :return:
    """

    try:
        task = Task.objects.get(pk=task_pk)
    except Task.DoesNotExist:
        return

    message = 'Task "Purge task", app task id={}'.format(task_pk)
    logger.info(message)

    celery_task = AsyncResult(task.id)
    logger.info('Celery task id={}'.format(task.id))

    revoke_task(celery_task)
    ret = 'Deleted '

    # delete TaskResults for subtasks
    subtask_results_deleted = task.subtasks.delete()

    # delete Task
    task.delete()

    ret += 'Task(id={}), TaskHistory, '.format(task_pk)

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
app.register_task(Similarity())
app.register_task(PartySimilarity())
