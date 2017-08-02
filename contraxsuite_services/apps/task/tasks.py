# -*- coding: utf-8 -*-

# Standard imports
import datetime
import hashlib
import logging
import math
import os
import re
import pickle
import string
import sys
from io import StringIO
from traceback import format_exc

# Additional libraries
import datefinder
import fuzzywuzzy.fuzz
import geocoder
import nltk
import numpy as np
import pandas as pd
import pycountry
from textblob import TextBlob
from tika import parser

# Celery imports
from celery import shared_task
from celery.result import AsyncResult
from celery.utils.log import get_task_logger
from django_celery_results.models import TaskResult

# Scikit-learn imports
from sklearn.cluster import Birch, DBSCAN, KMeans, MiniBatchKMeans
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegressionCV
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC

# Django imports
from django.conf import settings
from django.core.management import call_command
from django.db.models import Q
from django.utils.timezone import now

# Project imports
from apps.document.models import (
    Document, DocumentProperty, TextUnit, TextUnitProperty, TextUnitTag)
from apps.analyze.models import (
    DocumentCluster, TextUnitCluster,
    DocumentSimilarity, TextUnitSimilarity, PartySimilarity as PartySimilarityModel,
    TextUnitClassification, TextUnitClassifier, TextUnitClassifierSuggestion)
from apps.extract.models import (
    GeoAlias, GeoAliasUsage, GeoEntity, GeoEntityUsage, GeoRelation,
    LegalTerm, LegalTermUsage, Party, PartyUsage,
    Court, CourtUsage, CurrencyUsage, RegulationUsage,
    DateDurationUsage, DateUsage, DefinitionUsage)
from apps.task.celery import app
from apps.task.models import Task
from apps.task.utils.custom import fast_uuid, extract_entity_list, text2num
from apps.task.utils.nlp import lang
from apps.task.utils.ocr.textract import textract2text
from apps.task.utils.text.segment import segment_paragraphs, segment_sentences

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0/LICENSE.pdf"
__version__ = "1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@lexpredict.com"


# Logger setup
this_module = sys.modules[__name__]
logger = get_task_logger(__name__)

# Create global stemmer
#TODO: Configuration-based and language-based stemmer.
stemmer = nltk.stem.porter.PorterStemmer()

#TODO: Configuration-based and language-based punctuation.
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)


def call_task(task_name, **options):
    """

    :param task_name:
    :param options:
    :return:
    """
    task_class = getattr(this_module, task_name.replace(' ', ''))
    task_id = str(fast_uuid())
    task = Task.objects.create(
        name=task_name,
        celery_task_id=task_id,
        user_id=options.get('user_id')
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
    name = 'LoadDocuments'

    def process(self, **kwargs):

        file_list = []
        path = os.path.join(settings.MEDIA_ROOT,
                            settings.FILEBROWSER_DIRECTORY,
                            kwargs['source_path'].strip().strip('/'))
        self.log('Parse ' + path)

        if os.path.isfile(path):
            file_list.append(path)
        else:
            for root, _, files in os.walk(path):
                for filename in files:
                    file_list.append(os.path.join(root, filename))
        self.log("Detected {0} files. Added {0} subtasks.".format(len(file_list)))

        if 'delete' in kwargs:
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
    def create_document(file_path, kwargs):

        task_id = kwargs['task_id']

        # Check for existing record
        if Document.objects.filter(description=file_path).exists():
            log(task_id, 'SKIP (EXISTS): ' + file_path)
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
                log(task_id, 'SKIP (ERROR): ' + file_path)
                return

        if not text:
            log(task_id, 'SKIP (ERROR): ' + file_path)
            return

        metadata['parsed_by'] = parser_name

        # Language identification
        try:
            language = lang.get_language_langid(text)[0]
        except:
            log(task_id, 'SKIP (LANGUAGE NOT DETECTED): ' + file_path)
            return

        # Create document object
        rel_file_path = os.path.join(*re.split(r'(data/)', file_path)[-2:])
        document = Document.objects.create(
            document_type=kwargs.get('document_type', 'agreement'),
            name=os.path.basename(file_path),
            description=rel_file_path,
            source=os.path.dirname(rel_file_path),
            source_type=kwargs.get('source_type', 'SEC data'),
            source_path=rel_file_path,
            metadata=metadata)

        # create Document Properties
        document_properties = [
            DocumentProperty(
                document_id=document.pk,
                key=k,
                value=v) for k, v in metadata.items() if v]

        polarity, subjectivity = TextBlob(text).sentiment
        document_properties += [
            DocumentProperty(
                document_id=document.pk,
                key='polarity',
                value=str(round(polarity, 3))),
            DocumentProperty(
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

        log(message='LOADED (%s): %s' % (parser_name.upper(), file_path),
            task=task_id)


class UpdateElasticsearchIndex(BaseTask):
    """
    Update Elasticsearch Index: each time after new documents are added
    """
    name = 'UpdateElasticsearchIndex'

    def process(self, **kwargs):
        self.task.subtasks_total = 1
        self.task.save()
        out = StringIO()
        call_command('update_index', '--remove', stdout=out)
        self.log(out.getvalue())
        self.task.push()


class LoadTerms(BaseTask):
    """
    Load Legal Terms from a dictionary sample
    """
    name = 'LoadTerms'

    def process(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

        path = os.path.join(settings.DATA_ROOT, kwargs['dictionary_path'].strip('/'))
        if not os.path.exists(path):
            path = os.path.join(settings.MEDIA_ROOT,
                                settings.FILEBROWSER_DIRECTORY,
                                kwargs['dictionary_path'].strip('/'))

        if not os.path.exists(path) or not os.path.isfile(path):
            raise RuntimeError('Unable to parse path "%s"' % path)

        if 'delete' in kwargs:
            LegalTerm.objects.all().delete()

        self.log('Parse "%s"' % path)
        dictionary_data = pd.read_csv(path)

        batch_size = 1000
        last_row_id = len(dictionary_data) - 1
        terms_batch = []

        self.task.subtasks_total = int(
            len(dictionary_data) / batch_size) + (1 if len(dictionary_data) % batch_size else 0)
        self.task.save()
        self.log('Detected %d terms' % len(dictionary_data))

        for row_id, row in dictionary_data.iterrows():
            term = row["term"].lower().strip()
            if not LegalTerm.objects.filter(term=term).exists():
                lt = LegalTerm()
                lt.term = term
                lt.source = row["source"]
                lt.definition_url = row["url"]
                terms_batch.append(lt)
            if row_id > 0 and row_id % batch_size == 0 or row_id == last_row_id:
                LegalTerm.objects.bulk_create(terms_batch)
                terms_batch = []
                self.log('Total processed: %d LegalTerms' % row_id)
                self.task.push()


class LoadGeoEntities(BaseTask):
    """
    Load Geopolitical Entities from given dictionaries
    """
    name = 'LoadGeoEntities'

    def process(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

        geo_entities_path = os.path.join(settings.DATA_ROOT,
                                         kwargs['geo_entities_path'].strip('/'))
        if not os.path.exists(geo_entities_path):
            geo_entities_path = os.path.join(settings.MEDIA_ROOT,
                                             settings.FILEBROWSER_DIRECTORY,
                                             kwargs['geo_entities_path'].strip('/'))
        if not os.path.exists(geo_entities_path) or not os.path.isfile(geo_entities_path):
            raise RuntimeError('Unable to find geo entities file: "%s"' % geo_entities_path)
        else:
            geo_entities_data = pd.read_csv(geo_entities_path)

        geo_relations_path = os.path.join(settings.DATA_ROOT,
                                          kwargs['geo_relations_path'].strip('/'))
        if not os.path.exists(geo_relations_path):
            geo_relations_path = os.path.join(settings.MEDIA_ROOT,
                                              settings.FILEBROWSER_DIRECTORY,
                                              kwargs['geo_relations_path'].strip('/'))
        if not os.path.exists(geo_relations_path) or not os.path.isfile(geo_relations_path):
            geo_relations_data = []
        else:
            geo_relations_data = pd.read_csv(geo_relations_path)

        geo_aliases_path = os.path.join(settings.DATA_ROOT,
                                        kwargs['geo_aliases_path'].strip('/'))
        if not os.path.exists(geo_aliases_path):
            geo_aliases_path = os.path.join(settings.MEDIA_ROOT,
                                            settings.FILEBROWSER_DIRECTORY,
                                            kwargs['geo_aliases_path'].strip('/'))
        if not os.path.exists(geo_aliases_path) or not os.path.isfile(geo_aliases_path):
            geo_aliases_data = []
        else:
            geo_aliases_data = pd.read_csv(geo_aliases_path)

        if 'delete' in kwargs:
            GeoEntity.objects.all().delete()
            GeoRelation.objects.all().delete()
            GeoAlias.objects.all().delete()

        self.task.subtasks_total = 3
        self.task.save()

        # create Geo Entities
        geo_entities = []
        self.log('Detected %d geo entities' % len(geo_entities_data))

        for _, row in geo_entities_data.iterrows():
            entity_id = row['Entity ID']
            entity_name = row['Entity Name'].strip()
            if GeoEntity.objects.filter(Q(name=entity_name) | Q(entity_id=entity_id)).exists():
                self.log('Geo Entity with ID "{}" of name "{}" already exists, skip.'.format(
                    entity_id, entity_name))
                continue

            if 'latitude' in row and row['latitude']:
                latitude = row['latitude']
                longitude = row['longitude']
            else:
                g = geocoder.google(entity_name)
                if not g.latlng and ',' in entity_name:
                    g = geocoder.google(entity_name.split(',')[0])
                latitude, longitude = g.latlng

            geo_entities.append(
                GeoEntity(entity_id=entity_id,
                          name=entity_name,
                          category=row['Entity Category'].strip(),
                          latitude=latitude,
                          longitude=longitude))

        GeoEntity.objects.bulk_create(geo_entities)
        self.log('Total created: %d GeoEntities' % len(geo_entities))
        self.task.push()

        # create Geo Relations
        geo_relations = []
        self.log('Detected %d geo relations' % len(geo_relations_data))

        for _, row in geo_relations_data.iterrows():
            entity_a_id = row['Entity A ID']
            entity_b_id = row['Entity B ID']
            if GeoEntity.objects.filter(entity_id__in=[entity_a_id, entity_b_id]).count() < 2:
                self.log('Geo Entity with ID "{}" or "{}" doesn\'t exist, skip.'.format(
                    entity_a_id, entity_b_id))
                continue
            if GeoRelation.objects.filter(entity_a_id=entity_a_id, entity_b_id=entity_b_id) \
                    .exists():
                self.log('Geo Relation with Entity A ID "{}" and Entity B ID "{}"'
                         ' already exists, skip.'.format(entity_a_id, entity_b_id))
                continue
            entity_a = GeoEntity.objects.get(entity_id=entity_a_id)
            entity_b = GeoEntity.objects.get(entity_id=entity_b_id)
            geo_relations.append(
                GeoRelation(entity_a=entity_a,
                            entity_b=entity_b,
                            relation_type=row['Relationship Type'].strip()))

        GeoRelation.objects.bulk_create(geo_relations)
        self.log('Total created: %d GeoRelations' % len(geo_relations))
        self.task.push()

        # create Geo Aliases
        geo_aliases = []
        self.log('Detected %d geo aliases' % len(geo_aliases_data))

        for _, row in geo_aliases_data.iterrows():
            entity_id = row['Entity ID']
            entity_alias = row['Entity Alias'].strip()
            entity = GeoEntity.objects.get(entity_id=entity_id)

            if GeoAlias.objects.filter(entity=entity, alias=entity_alias).exists():
                self.log('Geo Alias with Entity "{}" and alis "{}"'
                         ' already exists, skip.'.format(entity, entity_alias))
                continue
            geo_aliases.append(
                GeoAlias(entity=entity,
                         alias=entity_alias,
                         locale=row['Entity Locale'].strip(),
                         type=row['Entity Alias Type'].strip()))

        GeoAlias.objects.bulk_create(geo_aliases)
        self.log('Total created: %d GeoAliases' % len(geo_aliases))
        self.task.push()


class LoadCourts(BaseTask):
    """
    Load Courts data from a file
    """
    name = 'LoadCourts'

    def process(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

        self.task.subtasks_total = 4
        self.task.save()

        path = os.path.join(settings.DATA_ROOT, kwargs['dictionary_path'].strip('/'))
        if not os.path.exists(path):
            path = os.path.join(settings.MEDIA_ROOT,
                                settings.FILEBROWSER_DIRECTORY,
                                kwargs['dictionary_path'].strip('/'))

        if not os.path.exists(path) or not os.path.isfile(path):
            raise RuntimeError('Unable to parse path "%s"' % path)
        self.task.push()

        if 'delete' in kwargs:
            Court.objects.all().delete()
        self.task.push()

        self.log('Parse "%s"' % path)
        dictionary_data = pd.read_csv(path)
        self.log('Detected %d terms' % len(dictionary_data))
        self.task.push()

        courts = []
        for _, row in dictionary_data.iterrows():
            if not Court.objects.filter(
                    court_id=row['Court ID'], abbreviation=row['Court Abbreviation']).exists():
                court = Court(
                    court_id=row['Court ID'],
                    type=row['Court Type'],
                    name=row['Court Name'],
                    abbreviation=row['Court Abbreviation']
                )
                courts.append(court)

        Court.objects.bulk_create(courts)
        self.task.push()


class LocateGeoEntities(BaseTask):
    """
    Locate geopolitical entities/aliases in text units
    """
    name = 'LocateGeoEntities'

    def process(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

        if 'delete' in kwargs:
            GeoAliasUsage.objects.all().delete()
            GeoEntityUsage.objects.all().delete()
        TextUnitClassifier.objects.filter(name__contains='by:entities').update(is_active=False)

        self.task.subtasks_total = GeoEntity.objects.count() + GeoAlias.objects.count()
        self.task.save()
        self.log('Found {0} Geo Entities and Geo Aliases. Added {0} subtasks.'.format(
            self.task.subtasks_total))

        entities = GeoEntity.objects
        if 'priority' in kwargs:
            entities = entities.distinct('name')

        for entity_id, entity_name in entities.values_list('id', 'name'):
            self.create_geo_entity_usages.apply_async(
                args=(entity_name, entity_id),
                task_id='%d_%s' % (self.task.id, fast_uuid()))

        # TODO: use "priority" flag for aliases?
        for alias_id, alias_name in GeoAlias.objects.values_list('id', 'alias'):
            self.create_geo_alias_usages.apply_async(
                args=(alias_name, alias_id),
                task_id='%d_%s' % (self.task.id, fast_uuid()))

    @staticmethod
    @shared_task
    def create_geo_entity_usages(entity, entity_id):
        regex = r'[{}{}]{}[{}{}]'.format(
            ''.join(string.punctuation),
            ''.join(string.whitespace),
            entity,
            ''.join(string.punctuation),
            ''.join(string.whitespace))
        text_units_with_entity = TextUnit.objects.filter(
            unit_type='paragraph',
            text__iregex=regex)
        if text_units_with_entity.exists():
            geo_entity_usage_list = [
                GeoEntityUsage(
                    text_unit=tu,
                    entity_id=entity_id,
                    count=len(re.findall(regex, tu.text, flags=re.IGNORECASE))
                ) for tu in text_units_with_entity]

            GeoEntityUsage.objects.bulk_create(geo_entity_usage_list)

    @staticmethod
    @shared_task
    def create_geo_alias_usages(alias, alias_id):
        regex = r'[{}{}]{}[{}{}]'.format(
            ''.join(string.punctuation),
            ''.join(string.whitespace),
            alias,
            ''.join(string.punctuation),
            ''.join(string.whitespace))
        text_units_with_alias = TextUnit.objects.filter(
            unit_type='paragraph',
            text__regex=regex)
        if text_units_with_alias.exists():
            geo_alias_usage_list = [
                GeoAliasUsage(
                    text_unit=tu,
                    alias_id=alias_id,
                    count=len(re.findall(regex, tu.text))
                ) for tu in text_units_with_alias
                if tu.text != tu.text.upper()]

            GeoAliasUsage.objects.bulk_create(geo_alias_usage_list)


class LocateTerms(BaseTask):
    """
    Locate terms in text units
    """
    name = 'LocateTerms'

    def process(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

        if 'delete' in kwargs:
            LegalTermUsage.objects.all().delete()
        TextUnitClassifier.objects.filter(name__contains='by:terms').update(is_active=False)

        self.task.subtasks_total = LegalTerm.objects.count()
        self.task.save()
        self.log('Found {0} Legal Terms. Added {0} subtasks.'.format(self.task.subtasks_total))

        for lt in LegalTerm.objects.all():
            term = lt.term.lower()
            if term != lt.term and \
                    LegalTerm.objects.filter(term=term).exists():
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
            ltu = LegalTermUsage()
            ltu.text_unit = tu
            ltu.term_id = term_id
            tu_count = tu.text.lower().count(term)
            if term.endswith('y'):
                tu_count += tu.text.lower().count(term[:-1] + 'ies')
            ltu.count = tu_count
            ltu_list.append(ltu)

        LegalTermUsage.objects.bulk_create(ltu_list)


class LocateParties(BaseTask):
    """
    Locate parties in text units
    """
    name = 'LocateParties'

    def process(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

        # TODO: ask: delete Parties instead of PartyUsages?
        if 'delete' in kwargs:
            Party.objects.all().delete()
            # PartyUsage.objects.all().delete()
        TextUnitClassifier.objects.filter(name__contains='by:parties').update(is_active=False)

        self.task.subtasks_total = Document.objects.count()
        self.task.save()
        self.log('Found {0} Documents. Added {0} subtasks.'.format(self.task.subtasks_total))

        for d in Document.objects.all():
            self.parse_document.apply_async(args=(d.id,),
                                            task_id='%d_%s' % (self.task.id, fast_uuid()))

    @staticmethod
    @shared_task
    def parse_document(document_id):

        pu_list = []

        for t in TextUnit.objects.filter(document_id=document_id, unit_type="paragraph").all():
            if t.text == t.text.upper():
                continue
            # Get entities
            entity_list = extract_entity_list(t.text)

            # Create usages
            for entity in set(entity_list):
                # Create/check if exists
                entity_name, entity_type = entity
                party, _ = Party.objects.get_or_create(
                    name=entity_name,
                    type=entity_type
                )

                # Create party usage
                count = entity_list.count(entity)
                pu = PartyUsage(text_unit=t, party=party, count=count)
                pu_list.append(pu)

        PartyUsage.objects.bulk_create(pu_list)


class LocateDates(BaseTask):
    """
    Locate dates in text units
    """
    name = 'LocateDates'

    def process(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

        if 'delete' in kwargs:
            DateUsage.objects.all().delete()
            TextUnitTag.objects.filter(tag="date").delete()
            DocumentProperty.objects.filter(key="date").delete()

        self.task.subtasks_total = Document.objects.count()
        self.task.save()
        self.log('Found {0} Documents. Added {0} subtasks.'.format(self.task.subtasks_total))

        for d_pk in Document.objects.values_list('pk', flat=True):
            self.parse_document_for_dates.apply_async(args=(d_pk, kwargs['user_id']),
                                                      task_id='%d_%s' % (self.task.id, fast_uuid()))

    @staticmethod
    @shared_task
    def parse_document_for_dates(document_id, user_id):
        """

        :param document_id:
        :param user_id:
        :return:
        """

        date_usages = []
        document_properties = []
        text_unit_tags = []
        min_date = datetime.datetime(1900, 1, 1)
        max_date = datetime.datetime(2100, 1, 1)

        for tu_pk, text in TextUnit.objects.filter(document_id=document_id) \
                .values_list('pk', 'text'):
            dates = [adate.date() for adate, source, index
                     in datefinder.find_dates(text, source=True, index=True, strict=True)
                     if adate > min_date < max_date and
                     '$' not in text[max([0, index[0] - 2]):index[1] + 2]]
            if len(dates) > 0:
                text_unit_tags.append(
                    TextUnitTag(
                        text_unit_id=tu_pk,
                        tag='date',
                        user_id=user_id))
                for adate in set(dates):
                    document_properties.append(
                        DocumentProperty(
                            document_id=document_id,
                            key='date',
                            value=adate.isoformat()))
                    date_usages.append(
                        DateUsage(
                            text_unit_id=tu_pk,
                            date=adate,
                            count=dates.count(adate)))
        TextUnitTag.objects.bulk_create(text_unit_tags)
        DocumentProperty.objects.bulk_create(document_properties)
        DateUsage.objects.bulk_create(date_usages)


class LocateDateDurations(BaseTask):
    """
    Locate durations in text units
    """
    name = 'LocateDateDurations'

    def process(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        regex1 = r"""
            (?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|
            fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|
            sixty|seventy|eighty|ninety|hundred|[\s\d\)\.-])+
            (?:business\s+)?(?:day|month|year)
        """
        regex_comp1 = re.compile(regex1)
        regex2 = r'[^\w\s]|\xa0'
        regex_comp2 = re.compile(regex2)
        regex3 = r'(.+?)[\)\s-]+(?:business\s+)?(day|month|year)'
        regex_comp3 = re.compile(regex3)

        text_units = TextUnit.objects.filter(text__iregex=regex1)

        self.task.subtasks_total = text_units.count() + 4
        self.task.save()
        self.log('Found {0} TextUnit with duration usages. Added {0} subtasks.'.format(
            self.task.subtasks_total))

        if 'delete' in kwargs:
            DateDurationUsage.objects.all().delete()
            TextUnitTag.objects.filter(tag="duration").delete()
            DocumentProperty.objects.filter(key="duration").delete()
        self.task.push()

        duration_usages = []
        document_properties = []
        text_unit_tags = []

        for tu_pk, document_id, text in text_units \
                .values_list('pk', 'document_id', 'text'):
            text = text.lower()
            durations = regex_comp1.findall(text)
            normalized_durations = []

            for duration in durations:
                try:
                    # TODO: simplify here and in text2num()
                    duration_item = regex_comp2.sub(' ', duration.replace('.0', '')).strip()
                    found = regex_comp3.findall(duration_item)
                    if not found or len(found[0]) != 2:
                        continue
                    number, duration_name = found[0]
                    if number.isdigit():
                        number = int(number)
                    elif number.replace(' ', '').isdigit():
                        if re.search(r'\s*%s\s*\)' % number, duration):
                            number = int(number.replace(' ', ''))
                        else:
                            number = int(number.split()[-1])
                    else:
                        number = text2num(number)
                    if number == 0:
                        self.log('Failed to fetch duration from "%s", text unit pk: %d'
                                 % (duration, tu_pk))
                        continue
                    elif number > 100 and duration_name in ['month', 'year']:
                        continue
                    normalized_durations.append('{} {}{}'.format(number, duration_name,
                                                                 's' if number > 1 else ''))
                except:
                    self.log('Failed to fetch duration from "%s", text unit pk: %d'
                             % (duration, tu_pk))
                    continue
            for duration_item in set(normalized_durations):
                document_properties.append(
                    DocumentProperty(
                        document_id=document_id,
                        key='duration',
                        value=duration_item))
                duration_usages.append(
                    DateDurationUsage(
                        text_unit_id=tu_pk,
                        duration=duration_item,
                        duration_str=duration_item,
                        count=normalized_durations.count(duration_item)))

            text_unit_tags.append(
                TextUnitTag(
                    text_unit_id=tu_pk,
                    tag='duration',
                    user_id=kwargs['user_id']))
            self.task.push()

        TextUnitTag.objects.bulk_create(text_unit_tags)
        self.task.push()
        DocumentProperty.objects.bulk_create(document_properties)
        self.task.push()
        DateDurationUsage.objects.bulk_create(duration_usages)
        self.task.push()


factor_map = dict(
    thousand=1000,
    million=1000000,
    billion=1000000000
)


class LocateCurrencies(BaseTask):
    """
    Locate currency usages in text units
    """
    name = 'LocateCurrencies'

    # TODO: Refactor Currency List to Data Model/Master Data.
    currency_symbol_list = ["$", "R$", "¥", "£", "€", "₨", "₩"]
    currency_short_name_list = ["Peso", "Dollar", "Franc", "Dinar", "Euro",
                                "Yuan", "Renminbi", "Koruna", "Krone", "Pound",
                                "Forint", "Krona", "Rupiah", "Yen",
                                "Won", "Shilling", "Rupee", "Ringgit", "Rial",
                                "Ruble", "Rand"]
    currency_abbrev_blacklist = ['all', 'ars', 'top']
    currency_abbrev_list = [c.alpha_3 for c in pycountry.currencies]

    def process(self, **kwargs):
        """
        Task process method.
        :param kwargs:
        :return:
        """

        # Setup task parameters
        use_symbols = 'use_symbols' in kwargs
        use_short_names = 'use_short_names' in kwargs
        use_abbreviations = 'use_abbreviations' in kwargs

        # TODO: skip cases when No/100 Dollar /d{2}/100 Dollar, etc.
        # TODO: catch cases when Two Millions Dollars (all numbers are words)
        symbols_re_list = '|'.join([re.escape(i) for i in self.currency_symbol_list])
        short_names_re_list = '|'.join(['%s[sS]?' % i for i in self.currency_short_name_list])
        abbreviations_re_list = '|'.join([i for i in self.currency_abbrev_list
                                          if i.lower() not in self.currency_abbrev_blacklist])

        number_re = r"""([\d\.,]+(?:\s+[Mm]illions?|\s+[Bb]illions?|
                     \s+MILLIONS?|\s+BILLIONS?)?)?"""
        base_re = r'{}[\s\(]*(%s)[\s\)]*{}'.format(number_re, number_re)
        symbols_re_comp = re.compile(base_re % symbols_re_list)
        short_names_re_comp = re.compile(
            r'{}[\s\(]*(?:\W|^)(%s)(?:[sS]|\W|$)[\s\)]*{}'.format(number_re, number_re)
            % '|'.join(self.currency_short_name_list))
        abbreviations_re_comp = re.compile(
            r'{}[\s\(]*(?:\W|^)(%s)(?:\W|$)[\s\)]*{}'.format(number_re, number_re)
            % '|'.join([i for i in self.currency_abbrev_list
                        if i.lower() not in self.currency_abbrev_blacklist]))

        # 1. Limit number of text units for further processing
        filter_items = []
        if use_symbols:
            filter_items.append(symbols_re_list)
        if use_short_names:
            filter_items.append(short_names_re_list)
        if use_abbreviations:
            filter_items.append(abbreviations_re_list)
        filter_regex = r'(?:\d|\W|^){}(?:\d|\W|$)'.format('|'.join(filter_items))

        text_units = TextUnit.objects.filter(unit_type="paragraph", text__iregex=filter_regex)
        self.task.subtasks_total = text_units.count()
        self.task.save()

        # 2. Delete if requested
        if 'delete' in kwargs:
            CurrencyUsage.objects.all().delete()
            TextUnitTag.objects.filter(tag="currency").delete()

        # 3. Iterate through all text units
        cu_results = []

        for tu in text_units:
            # TU flag
            financial_found = False
            text = tu.text

            # Check unicode character
            if use_symbols:
                for occurrence in symbols_re_comp.findall(text):
                    cu = CurrencyUsage()
                    cu.text_unit = tu
                    cu.usage_type = "symbol"
                    cu.currency = occurrence[1]
                    value, value_str = self.get_amount(occurrence, reverse=True)
                    cu.amount = {'value': value, 'value_str': value_str}
                    cu_results.append(cu)
                    financial_found = True

            # Check short name
            if use_short_names:
                for occurrence in short_names_re_comp.findall(text):
                    cu = CurrencyUsage()
                    cu.text_unit = tu
                    cu.usage_type = "short_name"
                    cu.currency = occurrence[1]
                    value, value_str = self.get_amount(occurrence)
                    cu.amount = {'value': value, 'value_str': value_str}
                    cu_results.append(cu)
                    financial_found = True

            # Check abbrev
            if use_abbreviations:
                for occurrence in abbreviations_re_comp.findall(text):
                    cu = CurrencyUsage()
                    cu.text_unit = tu
                    cu.usage_type = "abbreviation"
                    cu.currency = occurrence[1]
                    value, value_str = self.get_amount(occurrence)
                    cu.amount = {'value': value, 'value_str': value_str}
                    cu_results.append(cu)
                    financial_found = True

            # Create TU tag
            if financial_found:
                TextUnitTag.objects.get_or_create(
                    text_unit=tu,
                    tag="currency")

            self.task.push()

        # Bulk create currency usages
        CurrencyUsage.objects.bulk_create(cu_results)

    @staticmethod
    def get_amount(occurrence, reverse=False):
        """

        :param occurrence:
        :param reverse:
        :return:
        """
        a, b = occurrence[0], occurrence[2]
        if reverse:
            a, b = occurrence[2], occurrence[0]
        if not any([a, b]):
            return None, None
        for c in [a, b]:
            if not re.sub(r'\D', '', c):
                continue
            try:
                factor_search = re.search('thousand|million|billion', c.lower())
                if factor_search:
                    factor = factor_map[factor_search.group(0)]
                    c1 = re.sub(r'\s+(?:thousands?|millions?|billions?)', '', c, flags=re.I)
                    return round(float(c1) * factor, 2), c
                return round(float(re.sub(r'\D', '', c[:-3]) + c[-3:].replace(',', '.')), 2), c
            except:
                return None, c
        return None, None


class LocateDefinitions(BaseTask):
    """
    Locate definitions in text units
    """
    name = 'LocateDefinitions'

    def process(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

        if 'delete' in kwargs:
            DefinitionUsage.objects.all().delete()

        regex = r'\((?:the )?[\'\"]([^\'\"]+)[\'\"]\)'
        text_units = TextUnit.objects.filter(text__iregex=regex)
        self.task.subtasks_total = text_units.count()
        self.task.save()
        self.log('Found {0} Text Units with definitions. Added {0} subtasks.'.format(
            self.task.subtasks_total))

        for text_unit in text_units:
            definition_usages = []

            for definition_name in set(re.findall(regex, text_unit.text)):
                definition_usages.append(
                    DefinitionUsage(
                        text_unit=text_unit,
                        definition=definition_name,
                        count=text_unit.text.count(definition_name)))

            DefinitionUsage.objects.bulk_create(definition_usages)
            self.task.push()


class LocateRegulations(BaseTask):
    """
    Locate Regulations in text units
    """
    name = 'LocateRegulations'

    def process(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

        if 'delete' in kwargs:
            RegulationUsage.objects.all().delete()

        reg = r"([0-9]+)\s*((?:U\.?S\.?C\.?|C\.?F\.?R\.?))\s*(?:Section|§)?\s*([0-9][0-9a-zA-Z\-]*)"
        reg_comp = re.compile(reg, flags=re.UNICODE)
        text_units = TextUnit.objects.filter(text__regex=reg)
        self.task.subtasks_total = text_units.count()
        self.task.save()

        usages = []
        for tu_pk, text in text_units.values_list('pk', 'text'):
            matches = [(a, b.replace('.', '').upper(), c) for a, b, c in reg_comp.findall(text)]
            for match in set(matches):
                usages.append(
                    RegulationUsage(
                        entity=None,  # TODO: Get United States GeoEntity
                        regulation_type="United States Code" if match == 'USC' else match,
                        regulation_name=' '.join(match),
                        count=matches.count(match)
                    )
                )
            self.task.push()


class LocateCourts(BaseTask):
    """
    Locate Courts in text units
    """
    name = 'LocateCourts'

    def process(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

        if 'delete' in kwargs:
            CourtUsage.objects.all().delete()

        regex = '(?:{}|{}|{})'.format(
            '|'.join([r'(?:\W|^){}[^\.,]+ court(?:\W|$)'.format(i.replace(' ', r'\s+'))
                      for i in Court.objects.values_list('name', flat=True)]),
            '|'.join([r'(?:\W|^)court [^\.,]+{}(?:\W|$)'.format(i.replace(' ', r'\s+'))
                      for i in Court.objects.values_list('name', flat=True)]),
            '|'.join([r'(?:\W|^){}(?:\W|$)'.format(re.escape(i).replace('\\ ', r'\s*'))
                      for i in Court.objects.values_list('abbreviation', flat=True)[1:]]))

        text_units = TextUnit.objects.filter(text__iregex=regex)
        self.task.subtasks_total = text_units.count()
        self.task.save()
        self.log('Found {0} Text Units with courts. Added {0} subtasks.'.format(
            self.task.subtasks_total))

        for text_unit in text_units:
            court_usages = []
            # TODO: loop over regex.findall(text) and define Court on the fly
            for court_pk, court_name, court_abbr in Court.objects.values_list(
                    'pk', 'name', 'abbreviation'):
                court_name_re = r'(?:\W|^){}[^\.,]+ court(?:\W|$)|' \
                                r'(?:\W|^)court [^\.,]+{}(?:\W|$)'.format(
                    court_name.replace(' ', r'\s+'),
                    court_name.replace(' ', r'\s+'))
                court_abbr_re = r'(?:\W|^){}(?:\W|$)'.format(
                    re.escape(court_abbr).replace(r'\\ ', r'\s*'))
                if court_abbr != 'U.S.':
                    court_name_re = '{}|{}'.format(court_name_re, court_abbr_re)
                occurrences = re.findall(court_name_re, text_unit.text)
                if not occurrences:
                    continue
                court_usages.append(
                    CourtUsage(
                        text_unit=text_unit,
                        court_id=court_pk,
                        count=len(occurrences)))

            CourtUsage.objects.bulk_create(court_usages)
            self.task.push()


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
            'term_model': LegalTerm,
            'term_set_name': 'legaltermusage_set',
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

        :param kwargs:
        :return:
        """

        self.task.subtasks_total = 3
        self.task.save()

        sample_size = int(kwargs['sample_size']) if kwargs['sample_size'].isdigit() else None
        classifier_id = int(kwargs['classifier']) if 'classifier' in kwargs else None
        min_confidence = int(kwargs['min_confidence']) / 100

        if not classifier_id and 'delete_classifier' in kwargs:
            TextUnitClassifier.objects.filter(class_name=kwargs['class_name']).delete()

        if 'delete_suggestions' in kwargs:
            if not classifier_id:
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

        for d in Document.objects.all()[:sample_size]:
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

        :param kwargs:
        :param classifier_id:
        :return:
        """

        if classifier_id:
            clf = TextUnitClassifier.objects.get(pk=classifier_id)
            clf_model = pickle.loads(clf.model_object)
            return clf, clf_model

        algorithm = kwargs['algorithm']
        class_name = kwargs['class_name']
        use_tfidf = 'use_tfidf' in kwargs
        classify_by = kwargs.get('classify_by', 'terms')
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
            gamma = int(kwargs['svc_gamma']) if kwargs['svc_gamma'].isdigit() in kwargs else 'auto'
            classifier_opts = {
                'C': float(kwargs['svc_c']),
                'kernel': kwargs['svc_kernel'],
                'gamma': gamma,
                'probability': True
            }
        elif algorithm == 'MultinomialNB':
            classifier_opts = {
                'alpha': float(kwargs['mnb_alpha'])
            }
        elif algorithm in ('ExtraTreesClassifier', 'RandomForestClassifier'):
            classifier_opts = {
                'n_estimators': int(kwargs['rfc_etc_n_estimators']),
                'criterion': kwargs['rfc_etc_criterion'],
                'max_features': int(kwargs['rfc_etc_max_features'])
                if kwargs['rfc_etc_max_features'].isdigit() else 'auto',
                'max_depth': int(kwargs['rfc_etc_max_depth'])
                if kwargs['rfc_etc_max_depth'].isdigit() else None,
                'min_samples_split': int(kwargs['rfc_etc_min_samples_split']),
                'min_samples_leaf': int(kwargs['rfc_etc_min_samples_leaf']),
            }
        else:  # if algorithm == 'LogisticRegressionCV'
            classifier_opts = {
                'Cs': int(kwargs['lrcv_cs']),
                'fit_intercept': 'lrcv_fit_intercept' in kwargs,
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
            'lookup_map': dict(
                terms='legaltermusage__term__term',
                parties='partyusage__party__name',
                entities='geoentityusage__entity__name'),
            'filter_map': dict(
                terms='textunit__legaltermusage__isnull',
                parties='textunit__partyusage__isnull',
                entities='textunit__geoentityusage__isnull')
        },
        'text_units': {
            'source_model': TextUnit,
            'cluster_model': TextUnitCluster,
            'lookup_map': dict(
                terms=['legaltermusage_set', 'term__term'],
                parties=['partyusage_set', 'party__name'],
                entities=['geoentityusage_set', 'entity__name']),
            'filter_map': dict(
                terms='legaltermusage__isnull',
                parties='partyusage__isnull',
                entities='geoentityusage__isnull')
        },
    }

    def cluster(self, target, kwargs):
        """

        :param target:
        :param kwargs:
        :return:
        """
        cluster_name = kwargs['name']
        cluster_desc = kwargs['description']
        using = kwargs['using']
        n_clusters = int(kwargs['n_clusters'])
        cluster_by = kwargs['cluster_by']

        target_attrs = self.cluster_map[target]
        source_model = target_attrs['source_model']
        cluster_model = target_attrs['cluster_model']
        lookup_map = target_attrs['lookup_map']
        filter_map = target_attrs['filter_map']

        # step #1 - delete
        if 'delete_type' in kwargs:
            cluster_model.objects.filter(cluster_by=cluster_by, using=using).delete()
        if 'delete' in kwargs:
            cluster_model.objects.all().delete()
        self.task.push()

        # step #2 - prepare data
        objects = source_model.objects.filter(**{filter_map[cluster_by]: False}).distinct()
        pks = list(objects.values_list('pk', flat=True))
        if target == 'documents':
            minimized_texts_set = [
                ' '.join([i for i in o.textunit_set.values_list(lookup_map[cluster_by], flat=True)
                          if i])
                for o in objects]
        else:
            minimized_texts_set = [
                ' '.join(getattr(o, lookup_map[cluster_by][0])
                         .values_list(lookup_map[cluster_by][1], flat=True))
                for o in objects]
        self.task.push()

        # step #3
        vectorizer = TfidfVectorizer(max_df=0.5, max_features=self.n_features,
                                     min_df=2, stop_words='english',
                                     use_idf='use_idf' in kwargs)
        X = vectorizer.fit_transform(minimized_texts_set)
        self.task.push()

        # step #4
        if using == 'MiniBatchKMeans':
            m = MiniBatchKMeans(
                n_clusters=n_clusters,
                init='k-means++',
                max_iter=int(kwargs['kmeans_max_iter']),
                batch_size=int(kwargs['mb_kmeans_batch_size']),
                n_init=3,
                verbose=self.verbose)
        elif using == 'KMeans':
            m = KMeans(
                n_clusters=n_clusters,
                init='k-means++',
                max_iter=int(kwargs['kmeans_max_iter']),
                n_init=int(kwargs['kmeans_n_init']),
                verbose=self.verbose)
        elif using == 'Birch':
            m = Birch(
                n_clusters=n_clusters,
                threshold=float(kwargs['birch_threshold']),
                branching_factor=int(kwargs['birch_branching_factor']))
        elif using == 'DBSCAN':
            m = DBSCAN(
                eps=float(kwargs['dbscan_eps']),
                min_samples=5,
                leaf_size=int(kwargs['dbscan_leaf_size']),
                p=float(kwargs['dbscan_p']) if kwargs['dbscan_p'] != '' else None)
        else:
            raise RuntimeError('Clustering method is not defined')
        m.fit(X)
        self.task.push()

        # step #5
        terms = vectorizer.get_feature_names()
        created_date = datetime.datetime.now()

        if using == 'DBSCAN':
            labels = m.labels_
            for cluster_id in set(labels):
                cluster_index = np.where(labels == cluster_id)[0]
                cluster_tokens = []
                for item_index in cluster_index:
                    cluster_tokens.extend(nltk.word_tokenize(minimized_texts_set[item_index]))
                cluster_self_name = "-".join(pd.Series(cluster_tokens).value_counts()
                                             .head(self.self_name_len).index).lower()
                cluster = cluster_model.objects.create(
                    cluster_id=cluster_id + 1,
                    name=cluster_name,
                    self_name='empty' if cluster_id == -1 else cluster_self_name,
                    description=cluster_desc,
                    cluster_by=cluster_by,
                    using=using,
                    created_date=created_date)
                getattr(cluster, target).set([pks[i] for i in cluster_index])
        else:
            if using == 'Birch':
                order_centroids = m.subcluster_centers_.argsort()[:, ::-1]
            else:
                order_centroids = m.cluster_centers_.argsort()[:, ::-1]

            # create clusters
            for cluster_id in range(n_clusters):
                cluster_self_name = '-'.join(
                    [terms[j] for j in order_centroids[cluster_id, :self.self_name_len]])
                cluster = cluster_model.objects.create(
                    cluster_id=cluster_id + 1,
                    name=cluster_name,
                    self_name=cluster_self_name,
                    description=cluster_desc,
                    cluster_by=cluster_by,
                    using=using,
                    created_date=created_date)
                getattr(cluster, target).set(
                    [pks[n] for n, label_id in enumerate(m.labels_.tolist())
                     if label_id == cluster_id])

        # create cluster with empty values (if terms are not found in documents)
        cluster, _ = cluster_model.objects.get_or_create(
            cluster_id=0,
            name=cluster_name,
            self_name='empty',
            description=cluster_desc,
            cluster_by=cluster_by,
            using=using,
            created_date=created_date)
        getattr(cluster, target).add(*list(source_model.objects.exclude(pk__in=pks)))
        self.task.push()

    def process(self, **kwargs):

        do_cluster_documents = 'do_cluster_documents' in kwargs
        do_cluster_text_units = 'do_cluster_text_units' in kwargs

        self.task.subtasks_total = 10 if do_cluster_documents and do_cluster_text_units else 5
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
    return [stemmer.stem(item) for item in tokens]


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
    default_similarity_type = "token_set_ratio"
    default_similarity_threshold = 90

    def process(self, **kwargs):
        """
        Task process method.
        :param kwargs:
        """
        parties = Party.objects.values_list('pk', 'name')
        self.task.subtasks_total = len(parties) + 1
        self.task.save()

        # verbose = 'verbose' in kwargs
        case_sensitive = 'case_sensitive' in kwargs
        similarity_type = kwargs.get('similarity_type', self.default_similarity_type)
        similarity_threshold = float(kwargs.get('similarity_threshold',
                                                self.default_similarity_threshold))

        # 1. Delete if requested
        if 'delete' in kwargs:
            PartySimilarityModel.objects.all().delete()

        # 2. Select scorer
        scorer = getattr(fuzzywuzzy.fuzz, similarity_type)

        # 3. Iterate through all pairs
        similar_results = []
        for party_a_pk, party_a_name in parties:
            for party_b_pk, party_b_name in parties:
                if party_a_pk == party_b_pk:
                    continue

                # Calculate similarity
                if not case_sensitive:
                    party_a_name = party_a_name.upper()
                    party_b_name = party_b_name.upper()

                score = scorer(party_a_name, party_b_name)
                if score >= similarity_threshold:
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
    use_idf = False
    verbose = True
    n_features = 100
    self_name_len = 3
    step = 2000

    def process(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

        search_similar_documents = 'search_similar_documents' in kwargs
        search_similar_text_units = 'search_similar_text_units' in kwargs
        min_similarity_val = int(kwargs.get('min_similarity', 80))
        self.log('Min similarity: %d' % min_similarity_val)

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
            if 'delete' in kwargs:
                DocumentSimilarity.objects.all().delete()
            self.task.push()

            # step #2 - prepare data
            texts_set = ['\n'.join(d.textunit_set.values_list('text', flat=True))
                         for d in Document.objects.all()]
            self.task.push()

            # step #3
            vectorizer = TfidfVectorizer(max_df=0.5, max_features=self.n_features,
                                         min_df=2, stop_words='english',
                                         use_idf=self.use_idf)
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
                    if similarity < min_similarity_val:
                        continue
                    DocumentSimilarity.objects.create(
                        document_a_id=document_a,
                        document_b_id=document_b,
                        similarity=similarity)
            self.task.push()

        # similar Text Units
        if search_similar_text_units:

            # step #1 - delete
            if 'delete' in kwargs:
                TextUnitSimilarity.objects.all().delete()
            self.task.push()

            # step #2 - prepare data
            texts_set, pks = zip(*text_units.values_list('text', 'pk'))
            self.task.push()

            # step #3
            vectorizer = TfidfVectorizer(tokenizer=normalize,
                                         max_df=0.5, max_features=self.n_features,
                                         min_df=2, stop_words='english',
                                         use_idf=self.use_idf)
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
                                                                          similarity_matrix[g, h] >= min_similarity_val]
                        TextUnitSimilarity.objects.bulk_create(tu_sim)
                    self.task.push()


# Register all load tasks
app.tasks.register(LoadDocuments())
app.tasks.register(LoadTerms())
app.tasks.register(LoadGeoEntities())
app.tasks.register(LoadCourts())

# Register all locate tasks
app.tasks.register(LocateTerms())
app.tasks.register(LocateGeoEntities())
app.tasks.register(LocateParties())
app.tasks.register(LocateDates())
app.tasks.register(LocateDateDurations())
app.tasks.register(LocateDefinitions())
app.tasks.register(LocateCourts())
app.tasks.register(LocateCurrencies())
app.tasks.register(LocateRegulations())

# Register all update/cluster/classify tasks
app.tasks.register(UpdateElasticsearchIndex())
app.tasks.register(Classify())
app.tasks.register(Cluster())
app.tasks.register(Similarity())
app.tasks.register(PartySimilarity())


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
