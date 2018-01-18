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
import logging
import math
import os
import pickle
import re
import string
import sys
from copy import deepcopy
from io import StringIO
from traceback import format_exc

# Additional libraries
import fuzzywuzzy.fuzz
import geocoder
import nltk
import numpy as np
import pandas as pd
import sys
from constance import config
# Celery imports
from celery import shared_task
from celery.result import AsyncResult
from celery.utils.log import get_task_logger
# Django imports
from django.conf import settings
from django.db.models import Count, Q, Case, Value, When, IntegerField
from django.utils.timezone import now
from django_celery_results.models import TaskResult
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
from lexnlp.extract.en import (
    amounts, citations, copyright, courts, dates, distances, definitions,
    durations, geoentities, money, percents, ratios, regulations, trademarks, urls,
    dict_entities)
from lexnlp.extract.en.entities.nltk_maxent import get_companies
from lexnlp.nlp.en.tokens import get_stems, get_token_list
from lexnlp.nlp.en.segments.titles import get_titles
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

# Project imports
from apps.analyze.models import (
    DocumentCluster, TextUnitCluster,
    DocumentSimilarity, TextUnitSimilarity, PartySimilarity as PartySimilarityModel,
    TextUnitClassification, TextUnitClassifier, TextUnitClassifierSuggestion)
from apps.common.advancedcelery.transfer import TransferManager
from apps.common.advancedcelery.fileaccess.local_file_access import LocalFileAccess
from apps.common.advancedcelery.fileaccess.nginx_http_file_access import NginxHttpFileAccess
from apps.document.models import (
    Document, DocumentProperty, TextUnit, TextUnitProperty, TextUnitTag)
from apps.extract import models as extract_models
from apps.extract.models import (
    AmountUsage, CitationUsage, CopyrightUsage,
    Court, CourtUsage, CurrencyUsage,
    DateDurationUsage, DateUsage, DefinitionUsage, DistanceUsage,
    GeoAlias, GeoAliasUsage, GeoEntity, GeoEntityUsage, GeoRelation,
    PercentUsage, RatioUsage, RegulationUsage,
    Party, PartyUsage, Term, TermUsage, TrademarkUsage, UrlUsage)
from apps.celery import app
from apps.common.utils import fast_uuid
from apps.task.models import Task
from apps.task.utils.nlp import lang
from apps.task.utils.ocr.textract import textract2text
from apps.task.utils.text.segment import segment_paragraphs, segment_sentences

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.5/LICENSE"
__version__ = "1.0.5"
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

transfer = TransferManager()


def prepare_file_access_handler():
    type = settings.CELERY_FILE_ACCESS_TYPE
    if type == 'Local':
        return LocalFileAccess(settings.CELERY_FILE_ACCESS_LOCAL_ROOT_DIR)
    elif type == 'Nginx':
        return NginxHttpFileAccess(settings.CELERY_FILE_ACCESS_NGINX_ROOT_URL)
    else:
        return None


file_access_handler = prepare_file_access_handler()


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
    task_id = str(fast_uuid())
    task = Task.objects.create(
        name=task_name,
        celery_task_id=task_id,
        user_id=options.get('user_id'),
        metadata=options.get('metadata')
    )
    options['task_id'] = task.id
    task_class().apply_async(kwargs=options, task_id=task_id)
    return True


def log(message, level='info', task=None):
    """

    :param message:
    :param level:
    :param task:
    :return:
    """
    message = str(message)

    # capture log content into log obj ("log" field)
    log_capture_string = StringIO()
    ch = logging.StreamHandler(log_capture_string)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(settings.LOGGING['formatters']['verbose']['format'])
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    getattr(logger, level)(message)

    log_content = log_capture_string.getvalue()
    log_capture_string.close()
    logger.removeHandler(ch)

    # TODO: set default to "" in model
    if isinstance(task, (int, str)):
        task = Task.objects.get(pk=task)
    if task:
        task.log = (task.log or '') + log_content
        task.save()

    return True


class BaseTask(app.Task):
    """BaseTask object

    BaseTask extending celery app Task model.
    """
    task = None

    def run(self, *args, **kwargs):
        self.task = Task.objects.get(id=kwargs.get('task_id'))
        self.log('Start task "%s", id=%d' % (self.task.name, self.task.id))
        try:
            self.process(**kwargs)
        except:
            level = 'error'
            self.log('ERROR', level=level)
            trace = format_exc()
            exc_class, exception, _ = sys.exc_info()
            exception_str = '%s: %s' % (exc_class.__name__, str(exception))
            self.log(exception_str, level=level)
            self.log(trace, level=level)
            self.task.has_error = True
            self.task.save()
            raise
        finally:
            self.log('End of main task "%s", id=%d' % (self.task.name, self.task.id))
            if self.task.uncompleted_subtasks:
                self.log('There are %d uncompleted subtasks remaining. Please wait.'
                         % self.task.uncompleted_subtasks)
        return "ok"

    def log(self, message, level='info'):
        log(message, level, task=self.task)
        return True


class LoadDocuments(BaseTask):
    """
    Load Document, i.e. create Document and TextUnit objects
    from uploaded document files in a given directory
    :param kwargs: task_id - Task id
                   source_path - (str) relative dir path in media/FILEBROWSER_DIRECTORY
                   delete - (bool) delete old objects
                   document_type - (str) f.e. "agreement"
                   source_type - (str) f.e. "SEC data"
    :return:
    """
    name = 'Load Documents'

    def process(self, **kwargs):

        path = kwargs['source_path']
        self.log('Parse {0} at {1}'.format(path, file_access_handler))
        file_list = file_access_handler.list(path)
        self.log("Detected {0} files. Added {0} subtasks.".format(len(file_list)))

        if kwargs['delete']:
            Document.objects.all().delete()

        self.task.subtasks_total = len(file_list)
        self.task.save()

        # Note: we use tika-server, tika-app works slowly ~ x4 times
        for file_path in file_list:
            self.create_document.apply_async(
                args=(file_path, kwargs),
                task_id='%d_%s' % (self.task.id, fast_uuid()))

    @staticmethod
    @shared_task
    def create_document(uri: str, kwargs):
        with file_access_handler.get_local_fn(uri) as (fn, file_name):
            LoadDocuments.create_document_local(fn, uri, kwargs)

    @staticmethod
    def create_document_local(file_path, file_name, kwargs):

        task_id = kwargs['task_id']

        # Check for existing record
        if Document.objects.filter(description=file_name).exists():
            log(task_id, 'SKIP (EXISTS): ' + file_name)
            return

        # process by tika
        parser_name = 'tika'
        metadata = {}
        try:
            data = parser.from_file(file_path)
            parsed = data['content']
            metadata = data['metadata']
            # text = process_text(parsed)
            text = parsed
            if len(text) < 100:
                text = None
        except:
            text = None

        # process by textract
        if text is None:
            try:
                text = textract2text(file_path)
                parser_name = 'textract'
            except:
                log(task_id, 'SKIP (ERROR): ' + file_name)
                return

        if not text:
            log(task_id, 'SKIP (ERROR): ' + file_name)
            return

        metadata['parsed_by'] = parser_name

        # Language identification
        try:
            language = lang.get_language_langid(text)[0]
        except:
            log(task_id, 'SKIP (LANGUAGE NOT DETECTED): ' + file_name)
            return

        # detect title
        title = metadata.get('title', None)
        if not title:
            _titles = list(get_titles(text))
            title = _titles[0] if _titles else None

        # Create document object
        document = Document.objects.create(
            document_type=kwargs['document_type'],
            name=os.path.basename(file_name),
            description=file_name,
            source=os.path.dirname(file_name),
            source_type=kwargs['source_type'],
            source_path=file_name,
            metadata=metadata,
            title=title)

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
            language=language) for paragraph in segment_paragraphs(text)]
        sentence_list = [TextUnit(
            document=document,
            text=sentence,
            text_hash=hashlib.sha1(sentence.encode("utf-8")).hexdigest(),
            unit_type="sentence",
            language=language) for sentence in segment_sentences(text)]

        document.paragraphs = len(paragraph_list)
        document.sentences = len(sentence_list)
        document.save()

        TextUnit.objects.bulk_create(paragraph_list + sentence_list)

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

        log(message='LOADED (%s): %s' % (parser_name.upper(), file_name),
            task=task_id)


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

        res = es.index(index=settings.ELASTICSEARCH_CONFIG['index'], doc_type='text_unit', id=tu.pk, body=es_doc)

    def process(self, **kwargs):
        self.task.subtasks_total = 1
        self.task.save()
        es = Elasticsearch(hosts=settings.ELASTICSEARCH_CONFIG['hosts'])

        es_index = settings.ELASTICSEARCH_CONFIG['index']

        try:
            es.indices.create(index=es_index)
            self.log('Created index: {0}'.format(es_index))
        except RequestError:
            self.log('Index already exists: {0}'.format(es_index))

        count = 0
        for tu in TextUnit.objects.iterator():
            self.elastic_index(es, tu)
            count += 1
            if count % 100 == 0:
                self.log('Indexing text units: {0} done'.format(count))
        self.log('Finished indexing text units. Refreshing ES index.')
        es.indices.refresh(index=es_index)
        self.log('Done')
        self.task.push()


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

        self.task.subtasks_total = 3
        self.task.save()

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

        self.task.push()

        if kwargs['delete']:
            Term.objects.all().delete()
        self.task.push()

        terms_df = pd.DataFrame()
        for path in paths:
            self.log('Parse "%s"' % path)
            data = pd.read_csv(path)
            self.log('Detected %d terms' % len(data))
            terms_df = terms_df.append(data)

        terms_df.drop_duplicates(inplace=True)
        terms_df.loc[terms_df["CaseSensitive"] == False, "Term"] = terms_df.loc[
            terms_df["CaseSensitive"] == False, "Term"].str.lower()
        terms_df = terms_df.drop_duplicates(subset="Term").dropna(subset=["Term"])
        self.log('Total %d unique terms' % len(terms_df))

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
        self.task.push()


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
            self.log('Parse "%s"' % path)
            data = pd.read_csv(path)
            self.log('Detected %d entities' % len(data))
            entities_df = entities_df.append(data)
        if entities_df.empty:
            raise RuntimeError('Received 0 entities to process, exit.')
        entities_df = entities_df.drop_duplicates().fillna('')

        self.task.subtasks_total = len(entities_df) + 2
        self.task.save()
        self.task.push()

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
            self.task.push()

        GeoAlias.objects.bulk_create(geo_aliases)
        self.log('Total created: %d GeoAliases' % len(geo_aliases))
        self.log('Total created: %d GeoEntities' % geo_entities_count)
        self.task.push()


class LoadCourts(BaseTask):
    """
    Load Courts data from a file OR github repo
    """
    name = 'LoadCourts'

    def process(self, **kwargs):
        """
        Load Courts data from a file OR github repo
        :param kwargs: dict, form data
        :return:
        """

        self.task.subtasks_total = 3
        self.task.save()

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

        self.task.push()

        if 'delete' in kwargs:
            Court.objects.all().delete()
        self.task.push()

        for path in paths:
            self.log('Parse "%s"' % path)
            dictionary_data = pd.read_csv(path).dropna(subset=['Court ID']).fillna('')
            dictionary_data['Court ID'] = dictionary_data['Court ID'].astype(int)
            self.log('Detected %d courts' % len(dictionary_data))

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
        self.task.push()


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
    def load_geo_config():

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
        return list(geo_config.values())

    @staticmethod
    def load_court_config():
        return [dict_entities.entity_config(
            entity_id=i.id,
            name=i.name,
            priority=0,
            aliases=i.alias.split(';') if i.alias else []
        ) for i in Court.objects.all()]

    @staticmethod
    def load_term_stems():
        term_stems = {}
        for t, pk in Term.objects.values_list('term', 'pk'):
            stemmed_term = ' %s ' % ' '.join(get_stems(t))
            stemmed_item = term_stems.get(stemmed_term, [])
            stemmed_item.append([t, pk])
            term_stems[stemmed_term] = stemmed_item
        for item in term_stems:
            term_stems[item] = dict(values=term_stems[item],
                                    length=len(term_stems[item]))
        return term_stems

    def process(self, **kwargs):

        # delete ThingUsage and TextUnitTag(tag=thing)
        locate = {}
        available_locators = list(settings.REQUIRED_LOCATORS) + list(config.standard_optional_locators)
        for term_name, term_kwargs in kwargs['tasks'].items():
            if term_name not in available_locators:
                continue
            if term_kwargs.get('delete') or term_kwargs.get('locate'):
                usage_model_names = self.usage_model_map.get(
                    term_name,
                    [term_name.title() + 'Usage'])
                for usage_model_name in usage_model_names:
                    usage_model = getattr(extract_models, usage_model_name)
                    deleted = usage_model.objects.all().delete()
                    self.log('Deleted {} {} objects'.format(
                        deleted[0], usage_model_name))
                tags_deleted = TextUnitTag.objects.filter(tag=term_name).delete()
                self.log('Deleted {} TextUnitTag(tag={})'.format(
                    tags_deleted[0], term_name))
                if term_kwargs.get('locate'):
                    locate[term_name] = {i: j for i, j in term_kwargs.items()
                                         if i not in ['locate', 'delete']}

        if not locate:
            self.task.force_complete()
            return

        # create data for specific tasks
        if 'term' in locate:
            locate['term']['term_stems'] = Locate.load_term_stems()

        if 'geoentity' in locate:
            locate['geoentity']['geo_config'] = Locate.load_geo_config()

        if 'court' in locate:
            locate['court']['court_config'] = Locate.load_court_config()

        # define number of async tasks
        text_units = TextUnit.objects.all()
        if kwargs['parse'] == 'paragraphs':
            text_units = text_units.filter(unit_type='paragraph')
            locate_in = 'paragraphs'
        else:
            locate_in = 'paragraphs and sentences'
        self.log('Run location of [{}].'.format('; '.join(locate.keys())))
        self.log('Locate in [{}].'.format(locate_in))
        self.task.subtasks_total = text_units.count()
        self.task.save()
        self.log('Found {0} Text Units. Added {0} subtasks.'.format(
            self.task.subtasks_total))

        # Putting 'locate' dict as large args for further multiple runs of parse_text_unit child tasks
        locate_cache_key = Locate.__name__ + str(self.task.id)
        transfer.put(key=locate_cache_key, value=locate)

        for text_unit_id, text, text_unit_lang in text_units.values_list('id', 'text', 'language'):
            self.parse_text_unit.apply_async(
                args=(text_unit_id, text_unit_lang, text, kwargs['user_id'], locate_cache_key),
                task_id='%d_%s' % (self.task.id, fast_uuid()))

    @staticmethod
    @shared_task
    def parse_text_unit(text_unit_id, text_unit_lang, text, user_id, cache_key):
        tags = []
        locate = transfer.get(cache_key) if cache_key else {}
        for task_name, task_kwargs in locate.items():
            func_name = 'parse_%s' % task_name
            try:
                task_func = getattr(this_module, func_name)
            except AttributeError:
                print('Warning: "%s" method not found' % func_name)
                continue
            found = task_func(text, text_unit_id, text_unit_lang, **task_kwargs)
            if found:
                tag_name = found if not isinstance(found, bool) else task_name
                tags.append(tag_name)
        if tags:
            for tag in tags:
                TextUnitTag.objects.get_or_create(
                    text_unit_id=text_unit_id,
                    tag=tag,
                    defaults=dict(user_id=user_id))


def parse_amount(text, text_unit_id, _text_unit_lang):
    found = list(amounts.get_amounts(text, return_sources=True))
    if found:
        unique = set(found)
        AmountUsage.objects.bulk_create(
            [AmountUsage(
                text_unit_id=text_unit_id,
                amount=item[0],
                amount_str=item[1],
                count=found.count(item)
            ) for item in unique])
    return bool(found)


def parse_citation(text, text_unit_id, _text_unit_lang):
    found = list(citations.get_citations(text, return_source=True))
    if found:
        unique = set(found)
        CitationUsage.objects.bulk_create(
            [CitationUsage(
                text_unit_id=text_unit_id,
                volume=item[0],
                reporter=item[1],
                reporter_full_name=item[2],
                page=item[3],
                page2=item[4],
                court=item[5],
                year=item[6],
                citation_str=item[7],
                count=found.count(item)
            ) for item in unique])
    return bool(found)


def parse_court(text, text_unit_id, text_unit_lang, **kwargs):
    court_config = kwargs['court_config']
    found = [dict_entities.get_entity_id(i[0])
             for i in courts.get_courts(text,
                                        court_config_list=court_config,
                                        text_languages=[text_unit_lang])]
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
    found = list(dates.get_dates(
        text,
        strict=kwargs.get('strict', False),
        return_source=False))
    if found:
        unique = set(found)
        DateUsage.objects.bulk_create(
            [DateUsage(
                text_unit_id=text_unit_id,
                date=item,
                count=found.count(item)
            ) for item in unique])
    return bool(found)


def parse_definition(text, text_unit_id, _text_unit_lang):
    found = list(definitions.get_definitions(text))
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
                type_abbr=type_abbr,
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
    if found:
        unique = set(found)
        CopyrightUsage.objects.bulk_create(
            [CopyrightUsage(
                text_unit_id=text_unit_id,
                year=item[1],
                name=item[2],
                copyright_str=item[3],
                count=found.count(item)
            ) for item in unique])
    return bool(found)


def parse_trademark(text, text_unit_id, _text_unit_lang):
    found = list(trademarks.get_trademarks(text))
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
    geo_config = kwargs['geo_config']
    priority = kwargs['priority']
    entity_alias_pairs = list(geoentities.get_geoentities(text,
                                                          geo_config,
                                                          text_languages=[text_unit_lang],
                                                          priority=priority))

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
    term_stems = kwargs['term_stems']
    text_stems = ' %s ' % ' '.join(get_stems(text, lowercase=True))
    text_tokens = get_token_list(text, lowercase=True)
    term_usages = []
    for stemmed_term, _data in term_stems.items():
        # prevent modifying of term_stems
        data = deepcopy(_data)
        # stem not found in text
        if stemmed_term not in text_stems:
            continue
        # if stem has 1 variant only
        if data['length'] == 1:
            count = text_stems.count(stemmed_term)
            if count:
                term_data = data['values'][0]
                term_data.append(count)
                term_usages.append(term_data)
        # case when f.e. stem "respons" is equal to multiple terms
        # ["response", "responsive", "responsibility"]
        else:
            for term_data in data['values']:
                count = text_tokens.count(term_data[0])
                if count:
                    term_data.append(count)
                    term_usages.append(term_data)
                    # TODO: "responsibilities"
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
    name = 'LocateTerms'

    def process(self, **kwargs):
        """
        Locate terms
        :param kwargs:
        :return:
        """

        TextUnitClassifier.objects.filter(name__contains='by:terms').update(is_active=False)

        if kwargs['delete'] or kwargs['locate']:
            deleted = TermUsage.objects.all().delete()
            self.log('Deleted %d Term Usages' % deleted[0])

        if not kwargs['locate']:
            self.task.force_complete()
            return

        self.task.subtasks_total = Term.objects.count()
        self.task.save()
        self.log('Found {0} Terms. Added {0} subtasks.'.format(self.task.subtasks_total))

        for lt in Term.objects.all():
            term = lt.term.lower()
            if term != lt.term and \
                    Term.objects.filter(term=term).exists():
                continue
            self.create_ltu.apply_async(
                args=(term, lt.id),
                task_id='%d_%s' % (self.task.id, fast_uuid()))

    @staticmethod
    @shared_task
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

        self.task.subtasks_total = 3
        self.task.save()

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

        self.task.push()  # 1

        clf, clf_model = self.get_classifier(kwargs, classifier_id)

        self.task.push()  # 2

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

        self.task.push()  # 3

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
        self.task.push()

        # step #2 - prepare data
        # filter objects
        q_object = Q()
        for c in cluster_by:
            q_object.add(Q(**{filter_map[c]: False}), Q.OR)
        objects = source_model.objects.filter(q_object).distinct()
        self.task.push()

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
                df_['prop_count'] = df_.apply(lambda x: x[prop_field].toordinal() - min_value, axis=1)

            # use amount value as feature value
            elif cluster_by_item in ['duration', 'currency_value']:
                df_['prop_count'] = df_.apply(lambda x: x[prop_field], axis=1)

            dft = df_.pivot(index=id_field, columns=prop_field, values='prop_count')
            dft.columns = ["%s(%s)" % (cluster_by_item, str(i)) for i in dft.columns]
            df = df.join(dft, how='outer')

        if df.empty:
            self.log('Empty date set. Exit.')
            self.task.force_complete()
            return

        X = df.fillna(0).values.tolist()
        y = df.index.tolist()
        feature_names = df.columns.tolist()
        self.task.push()

        # step #4 - get model, clustering
        created_date = datetime.datetime.now()
        m = self.get_model(**kwargs)

        if using == 'LabelSpreading':
            # TODO: simplify
            objects_with_prop = {pk: prop for pk, prop in objects.filter(
                **{'{}__key'.format(target_attrs['property_lookup']): kwargs['ls_%s_property' % target]})
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
                    self.log('Unable to cluster, perhaps because of small data set.')
                    self.task.push()
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
                        [str(feature_names[j]) for j in order_centroids[cluster_id, :self.self_name_len]])
                    cluster = cluster_model.objects.create(
                        cluster_id=cluster_id + 1,
                        name=cluster_name[:100],
                        self_name=cluster_self_name[:100],
                        description=cluster_desc[:200],
                        cluster_by=cluster_by_str[:100],
                        using=using[:20],
                        created_date=created_date)
                    getattr(cluster, target).set(pks)
        self.task.push()

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

        self.task.subtasks_total = 8 if do_cluster_documents and do_cluster_text_units else 4
        self.task.save()

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
    name = 'PartySimilarity'

    def process(self, **kwargs):
        """
        Task process method.
        :param kwargs: dict, form data
        """
        parties = Party.objects.values_list('pk', 'name')
        self.task.subtasks_total = len(parties) + 1
        self.task.save()

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
            self.task.push()

        # 4. Bulk create similarity objects
        PartySimilarityModel.objects.bulk_create(similar_results)
        self.task.push()


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
        self.log('Min similarity: %d' % similarity_threshold)

        # get text units with min length 100 signs
        text_units = TextUnit.objects.filter(unit_type='paragraph',
                                             text__regex=r'.{100}.*')
        len_tu_set = text_units.count()

        subtasks_total = 0
        if search_similar_documents:
            subtasks_total += 4
        if search_similar_text_units:
            subtasks_total += math.ceil(len_tu_set / self.step) ** 2 + 3
        self.task.subtasks_total = subtasks_total
        self.task.save()

        # similar Documents
        if search_similar_documents:

            # step #1 - delete
            if kwargs['delete']:
                DocumentSimilarity.objects.all().delete()
            self.task.push()

            # step #2 - prepare data
            texts_set = ['\n'.join(d.textunit_set.values_list('text', flat=True))
                         for d in Document.objects.all()]
            self.task.push()

            # step #3
            vectorizer = TfidfVectorizer(max_df=0.5, max_features=self.n_features,
                                         min_df=2, stop_words='english',
                                         use_idf=kwargs['use_idf'])
            X = vectorizer.fit_transform(texts_set)
            self.task.push()

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
            self.task.push()

        # similar Text Units
        if search_similar_text_units:

            # step #1 - delete
            if kwargs['delete']:
                TextUnitSimilarity.objects.all().delete()
            self.task.push()

            # step #2 - prepare data
            texts_set, pks = zip(*text_units.values_list('text', 'pk'))
            self.task.push()

            # step #3
            vectorizer = TfidfVectorizer(tokenizer=normalize,
                                         max_df=0.5, max_features=self.n_features,
                                         min_df=2, stop_words='english',
                                         use_idf=kwargs['use_idf'])
            X = vectorizer.fit_transform(texts_set)
            self.task.push()

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
                    self.task.push()


@shared_task(name='celery.clean_tasks')
def clean_tasks(delta_days=2):
    """
    Clean Task and TaskResult
    """
    control_date = now() - datetime.timedelta(days=delta_days)
    log('Clean tasks. Control date: {}'.format(control_date))

    removed_tasks = 0
    removed_task_results = 0
    for task in Task.objects.all():
        log('Task="{}", status="{}", date_start="{}"'.format(
            task.name, task.status, task.date_start))
        if task.status == 'PENDING' or task.date_start > control_date:
            log('skip...')
        else:
            log('remove...')
            # remove subtasks
            res = TaskResult.objects \
                .filter(Q(task_id__startswith='%d_' % task.id) |
                        Q(task_id=task.celery_task_id)) \
                .delete()
            removed_task_results += res[0]
            # remove task
            task.delete()
            removed_tasks += 1

    ret = 'Deleted %d Tasks and %d TaskResults' % (removed_tasks, removed_task_results)
    log(ret)
    return ret


def purge_task(task_pk):
    """
    Purge task method.
    :param task_pk:
    :return:
    """

    log('Task "Purge task", app task id={}'.format(task_pk))
    app_task = Task.objects.get(pk=task_pk)

    celery_task = AsyncResult(app_task.celery_task_id)
    log('Celery task id={}'.format(app_task.celery_task_id))

    children_tasks = celery_task.children
    if children_tasks:
        children_tasks_no = len(children_tasks)
        if children_tasks:
            for child_task in children_tasks:
                child_task.revoke(terminate=True)
    else:
        children_tasks_no = 0
    celery_task.revoke(terminate=True, wait=True, timeout=2)
    app_task.delete()
    TaskResult.objects.filter(task_id__startswith='%s_' % task_pk).delete()

    ret = 'Deleted task, celery task, %d children celery tasks.' % children_tasks_no
    log(ret)
    return {'message': ret, 'status': 'success'}


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
app.register_task(Classify())
app.register_task(Cluster())
app.register_task(Similarity())
app.register_task(PartySimilarity())
