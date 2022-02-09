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
import math
import sys
from collections import defaultdict
from typing import Optional

import fuzzywuzzy.fuzz
import nltk
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from celery.states import FAILURE, SUCCESS, PENDING
from django.contrib.contenttypes.models import ContentType
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from psycopg2 import InterfaceError, OperationalError
from django.db import transaction
from django.db.models import Q
from django.db.models.functions import Length
from django.dispatch import receiver

import task_names
from apps.analyze.ml.similarity import DocumentSimilarityEngine, TextUnitSimilarityEngine
from apps.analyze.models import SimilarityRun, DocumentSimilarity, TextUnitSimilarity, \
    PartySimilarity as PartySimilarityModel
from apps.celery import app
from apps.common import redis
from apps.common.models import Action
from apps.document import signals
from apps.document.constants import DOCUMENT_TYPE_CODE_GENERIC_DOCUMENT
from apps.document.field_processing.document_vectorizers import document_feature_vector_pipeline
from apps.document.models import DocumentField, TextUnit, Document
from apps.extract.models import Party
from apps.project.models import Project
from apps.rawdb.constants import FIELD_CODE_DOC_ID
from apps.similarity.chunk_similarity_task import ChunkSimilarity
from apps.similarity.models import DocumentSimilarityConfig, DST_FIELD_SIMILARITY_CONFIG_ATTR
from apps.similarity.notifications import notify_similarity_task_completed, \
    notify_delete_similarity_completed
from apps.task.models import Task
from apps.task.signals import task_deleted
from apps.task.tasks import ExtendedTask, remove_punctuation_map, CeleryTaskLogger, purge_task, \
    _call_task
from apps.task.utils.task_utils import TaskUtils

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# TODO: Configuration-based and language-based stemmer.

# Create global stemmer
stemmer = nltk.stem.porter.PorterStemmer()


def normalize(text):
    """
    Simple text normalizer returning stemmed, lowercased tokens.
    :param text:
    :return:
    """
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))


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


class PartySimilarity(ExtendedTask):
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

        run = SimilarityRun.objects.create(
            name=kwargs.get('run_name'),
            created_date=datetime.datetime.now(),
            created_by_id=kwargs.get('user_id'),
            feature_source='party',
            similarity_threshold=kwargs['similarity_threshold'],
            # use_tfidf=kwargs.get('use_idf', False),    # TODO: not used in a form for now
            unit_source='party',
        )

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
                            run=run,
                            party_a_id=party_a_pk,
                            party_b_id=party_b_pk,
                            similarity=score))
            self.push()

        # 4. Bulk create similarity objects
        PartySimilarityModel.objects.bulk_create(similar_results, ignore_conflicts=True)
        self.push()

        Action.objects.create(name='Processed Similarity Tasks',
                              message=f'{self.name} task is finished',
                              user_id=kwargs.get('user_id'),
                              content_type=ContentType.objects.get_for_model(SimilarityRun),
                              model_name='SimilarityRun',
                              app_label='analyze',
                              object_pk=run.pk)


class Similarity(ExtendedTask):
    """
    Find Similar Documents, Text Units by vectorized text
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
        project = kwargs.get('project')
        project_id = project['pk'] if project else 0
        self.log_info('Min similarity: %d' % similarity_threshold)

        # get text units with min length 100 signs
        filters = dict(unit_type='paragraph', text__regex=r'.{100}.*')
        if project_id:
            filters['project_id'] = project_id
        text_units = TextUnit.objects.filter(**filters)
        len_tu_set = text_units.count()

        push_steps = 0
        if search_similar_documents:
            push_steps += 4
        if search_similar_text_units:
            push_steps += math.ceil(len_tu_set / self.step) ** 2 + 3
        self.set_push_steps(push_steps)

        documents = Document.objects.filter(project_id=project_id) if project_id \
            else Document.objects.all()

        # similar Documents
        total_stored = 0
        if search_similar_documents:
            # step #1 - delete
            if kwargs['delete']:
                if project_id:
                    DocumentSimilarity.objects.filter(
                        Q(document_a__project_id=project_id) |
                        Q(document_b__project_id=project_id)).delete()
                else:
                    DocumentSimilarity.objects.all().delete()
            self.push()

            # step #2 - prepare data
            texts_set = ['\n'.join(d.textunit_set.values_list('text', flat=True))
                         for d in documents]
            self.push()

            # step #3
            vectorizer = TfidfVectorizer(max_df=0.5, max_features=self.n_features,
                                         min_df=2, stop_words='english',
                                         use_idf=kwargs['use_idf'])
            X = vectorizer.fit_transform(texts_set)
            self.push()

            # step #4
            similarity_matrix = cosine_similarity(X) * 100
            pks = documents.values_list('pk', flat=True)
            sim_objs = []

            run = SimilarityRun.objects.create(
                name=kwargs.get('run_name'),
                created_date=datetime.datetime.now(),
                created_by_id=kwargs.get('user_id'),
                feature_source='text',
                similarity_threshold=similarity_threshold,
                use_tfidf=kwargs.get('use_idf', False),
                unit_source='document',
            )

            for x in range(len(pks) - 1):
                document_a = pks[x]
                # use it to search for unique a<>b relations
                # for y, document_b in enumerate(Document.objects.all()[x + 1:], start=x + 1):
                for y in range(x + 1, len(pks)):
                    document_b = pks[y]
                    similarity = similarity_matrix[x, y]
                    # TODO: check similarity and similarity_threshold are both the same type int
                    #  or floatL .75 vs 75
                    if similarity >= similarity_threshold:
                        sim_obj = DocumentSimilarity(
                            run=run,
                            document_a_id=document_a,
                            document_b_id=document_b,
                            similarity=similarity)
                        sim_objs.append(sim_obj)
            DocumentSimilarity.objects.bulk_create(sim_objs, ignore_conflicts=True)
            total_stored = len(sim_objs)
            self.push()
            project_ids = list(set(documents.values_list('project_id', flat=True)))

            for project_id in project_ids:
                Action.objects.create(name='Processed Similarity Tasks',
                                      message=f'{self.name} task for project '
                                              f'"{Project.objects.get(id=project_id)}" is finished',
                                      user_id=kwargs.get('user_id'),
                                      view_action='update',
                                      content_type=ContentType.objects.get_for_model(Project),
                                      model_name='Project',
                                      app_label='project',
                                      object_pk=project_id)
            self.notify_on_completed_similarity_action(project_ids, kwargs.get('user_id'),
                                                       "Document")

        # similar Text Units
        if search_similar_text_units:

            # step #1 - delete
            if kwargs['delete']:
                if project_id:
                    TextUnitSimilarity.objects.filter(
                        Q(project_a__id=project_id) |
                        Q(project_b__id=project_id)).delete()
                else:
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
            run = SimilarityRun.objects.create(
                name=kwargs.get('run_name'),
                created_date=datetime.datetime.now(),
                created_by_id=kwargs.get('user_id'),
                feature_source='text',
                similarity_threshold=similarity_threshold,
                distance_type='cosine',
                use_tfidf=kwargs.get('use_idf', False),
                unit_source='text_unit',
            )

            for i in range(0, len_tu_set, self.step):
                for j in range(i + 1, len_tu_set, self.step):
                    similarity_matrix = cosine_similarity(
                        X[i:min([i + self.step, len_tu_set])],
                        X[j:min([j + self.step, len_tu_set])]) * 100
                    for g in range(similarity_matrix.shape[0]):
                        tu_sim = [
                            TextUnitSimilarity(
                                run=run,
                                text_unit_a_id=pks[i + g],
                                text_unit_b_id=pks[j + h],
                                similarity=similarity_matrix[g, h])
                            for h in range(similarity_matrix.shape[1])
                            if i + g != j + h and similarity_matrix[g, h] >= similarity_threshold]
                        TextUnitSimilarityEngine().set_refs(tu_sim)
                        TextUnitSimilarity.objects.bulk_create(tu_sim, ignore_conflicts=True)
                        total_stored += len(tu_sim)
                    self.push()

            Action.objects.create(name='Processed Similarity Tasks',
                                  message=f'{self.name} task for Text Units in project '
                                          f'"{Project.objects.get(id=project_id)}" is finished',
                                  user_id=kwargs.get('user_id'),
                                  view_action='update',
                                  content_type=ContentType.objects.get_for_model(Project),
                                  model_name='Project',
                                  app_label='project',
                                  object_pk=project_id)
            self.notify_on_completed_similarity_action([project_id], kwargs.get('user_id'),
                                                       "TEXT_UNIT")

        self.log_info(f'{total_stored} records stored')

    @staticmethod
    def notify_on_completed_similarity_action(project_ids: list,
                                              user_id: int,
                                              similarity_type: str):
        from apps.notifications.models import WebNotificationMessage, WebNotificationTypes
        notifications = []
        if similarity_type == 'DOCUMENT':
            notification_type = WebNotificationTypes.DOCUMENT_SIMILARITY_SEARCH_FINISHED
        elif similarity_type == 'TEXT_UNIT':
            notification_type = WebNotificationTypes.TEXT_UNIT_SIMILARITY_SEARCH_FINISHED
        else:
            return
        for project_id in project_ids:
            project = Project.all_objects.get(id=project_id)
            message_data = {
                'project': project.name,
            }
            message_data = notification_type.check_message_data(message_data)
            redirect_link = {
                'type': notification_type.redirect_link_type(),
                'params': {
                    'project_type': 'batch_analysis'
                        if project.type.code == DOCUMENT_TYPE_CODE_GENERIC_DOCUMENT
                        else 'contract_analysis',
                    'project_id': project.pk
                },
            }
            recipients = [user_id, ]
            notifications.append((message_data, redirect_link, notification_type,
                                  recipients))
        WebNotificationMessage.bulk_create_notification_messages(notifications)


class DocumentSimilarityByFeatures(ExtendedTask):
    """
    Find Similar Documents by extracted features
    """
    name = 'Document Similarity By Features'
    engine_class = DocumentSimilarityEngine
    unit_source = 'document'
    run_id = None
    item_id = None

    def delete_existing(self, project_id, log_info, run_id=None, item_id=None,
                        feature_source_str=None, purge_existing=False):
        # added log_info param allow use this method from another tasks
        # TODO: delete more granular using item_id / feature_source / run_id
        run_qs = SimilarityRun.objects.filter(unit_source=self.unit_source)
        task_qs = Task.objects.filter(name=self.name, status=PENDING)
        if run_id:
            run_qs = run_qs.filter(id=run_id)
            task_qs = task_qs.filter(metadata__run_id=run_id)
        elif project_id:
            run_qs = run_qs.filter(project_id=project_id)
            task_qs = task_qs.filter(Q(kwargs__project=int(project_id)) |
                                     Q(kwargs__project=str(project_id)) |
                                     Q(project_id=project_id))
        else:
            raise RuntimeError('either project_id or run_id must be provided')

        try:
            task_qs = task_qs.exclude(pk=self.task.pk)
        except:
            # case then call is from another task
            pass

        if purge_existing:
            log_info(f'Purge {task_qs.count()} tasks')
            for task_id in task_qs.values_list('pk', flat=True):
                # set send_signal_task_deleted to False to prevent cyclic deletion from
                # remove_similarity_results_on_purge
                purge_task(task_id, log_func=log_info, send_signal_task_deleted=False)
        log_info(f'Delete SimilarityRun results for runs {list(run_qs.values_list("id", flat=True))}')
        deleted = run_qs.delete()
        log_info(f'Deleted {deleted[1]}')

    def get_item_id(self, kwargs):
        return kwargs.get('item_id'), kwargs

    def process(self, **kwargs):
        feature_source = kwargs.get('feature_source', 'term')
        similarity_threshold = kwargs.pop('similarity_threshold', 75)
        distance_type = kwargs.pop('distance_type', 'cosine')
        delete = kwargs.pop('delete', True)
        project_id = kwargs.get('project')

        item_id, kwargs = self.get_item_id(kwargs)
        if item_id:
            self.log_info(f'Search similar to object with id: {item_id}')
            self.item_id = item_id
        self.log_info(f'Min similarity: {similarity_threshold}')

        # for cases like when ['terms', 'dates'] passed
        feature_source_str = ', '.join(feature_source) \
            if isinstance(feature_source, (list, tuple)) \
            else feature_source

        # delete similarity objects from previous run
        if delete:
            self.delete_existing(project_id=project_id, log_info=self.log_info,
                                 item_id=item_id, feature_source_str=feature_source_str, purge_existing=True)

        run = SimilarityRun.objects.create(
            name=kwargs.get('run_name'),
            created_date=datetime.datetime.now(),
            created_by_id=kwargs.get('user_id'),
            project_id=project_id,
            feature_source=feature_source_str,
            similarity_threshold=similarity_threshold,
            distance_type=distance_type,
            use_tfidf=kwargs.get('use_tfidf', False),
            unit_source=self.unit_source,
            unit_type=kwargs.get('unit_type'),
            unit_id=item_id,
        )
        self.log_info(f'Created SimilarityRun {run}')

        self.run_id = run.pk

        if not self.task.metadata:
            self.task.metadata = {}
        self.task.metadata['run_id'] = run.id
        self.task.save()

        args = [project_id, kwargs.get('user_id'), self.task.id, self.name, run.id, item_id,
                self.unit_source, SUCCESS]
        self.run_after_sub_tasks_finished('Notify Task Succeed', self.finalize, [tuple(args)])
        args[-1] = FAILURE
        self.run_if_task_or_sub_tasks_failed(self.finalize, args=tuple(args))

        similarity_engine_kwargs = dict(
            project_id=project_id,
            threshold=similarity_threshold / 100,
            distance_type=distance_type,
            created_date=datetime.datetime.now().timestamp(),
            run_id=self.run_id,
            log_routine=self.log_info,
            **kwargs    # the rest kwargs are passed as is and may be different for inherited tasks
        )
        self.log_info(f'similarity_engine_kwargs: {similarity_engine_kwargs}')
        similarity_engine = self.engine_class(**similarity_engine_kwargs)

        self.log_info(f'Start getting features, engine: {similarity_engine.__class__.__name__}')
        features = similarity_engine.get_features()
        self.log_info(f'Features are obtained, shape: {features.feature_df.shape}; '
                      f'memory usage: {features.feature_df.memory_usage().sum()}')

        subtasks_args = []

        # let's use cached data expiration date the same as for similarity objects
        from apps.analyze.app_vars import DOCUMENT_SIMILARITY_OBJECTS_EXPIRE_IN, \
            TEXT_UNIT_SIMILARITY_OBJECTS_EXPIRE_IN
        exp_val = DOCUMENT_SIMILARITY_OBJECTS_EXPIRE_IN if self.unit_source == 'document' \
            else TEXT_UNIT_SIMILARITY_OBJECTS_EXPIRE_IN

        features_redis_key = f'sim_{self.task.pk}_features'
        features_data = (features.term_frequency_matrix, features.item_index)
        redis.push(key=features_redis_key, value=features_data, pickle_value=True, ex=exp_val.val())

        similarity_engine_kwargs.pop('log_routine', None)

        if item_id:
            subtasks_args.append((
                features_redis_key,
                None,
                None,
                item_id,
                self.engine_class.__name__,
                similarity_engine_kwargs,
            ))

        else:
            for block_start in range(0, features.term_frequency_matrix.shape[0],
                                     similarity_engine.block_step):
                block_end = block_start + similarity_engine.block_step
                subtasks_args.append((
                    features_redis_key,
                    block_start,
                    block_end,
                    None,
                    self.engine_class.__name__,
                    similarity_engine_kwargs,
                ))
        self.log_info(f'Start subtasks for SimilarityRun {SimilarityRun.objects.get(id=run.id)}')
        self.log_info(f'Similarity subtasks kwargs: {similarity_engine_kwargs}')

        self.run_sub_tasks(
            'Calculate similarities for feature_df blocks',
            self.calc_block_similarity,
            subtasks_args
        )

        Action.objects.create(name='Processed Similarity Tasks',
                              message=f'{self.name} task for project '
                                      f'{Project.objects.get(id=project_id)} is finished',
                              user_id=kwargs.get('user_id'),
                              view_action='update',
                              content_type=ContentType.objects.get_for_model(Project),
                              model_name='Project',
                              app_label='project',
                              object_pk=project_id)

    def log_routine(self, msg: str, msg_key='') -> None:
        self.log_info(msg)

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=6000,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError),
                 max_retries=3,
                 priority=3)
    def calc_block_similarity(task,
                              features_redis_key,
                              block_start,
                              block_end,
                              item_id,
                              engine_class_name,
                              engine_kwargs):
        TaskUtils.prepare_task_execution()

        task.log_info(f'Calculate similarity for features block ({block_start}-{block_end}) items')
        engine_kwargs['log_routine'] = task.log_info
        engine_class = getattr(sys.modules[__name__], engine_class_name)
        engine = engine_class(**engine_kwargs)

        feature_df_data, feature_df_index = redis.pop(features_redis_key)
        sim_obj_list = engine.calc_block_similarity(
            feature_df_data, feature_df_index, block_start, block_end, item_id)

        save_step = 1000
        for step_start in range(0, len(sim_obj_list), save_step):
            engine.similarity_model.objects.bulk_create(
                sim_obj_list[step_start:step_start + save_step],
                ignore_conflicts=True)

        count = len(sim_obj_list)
        task.log_info(f'Created {count} db records for block ({block_start}-{block_end}) items')

    @staticmethod
    @shared_task(base=ExtendedTask,
                 bind=True,
                 soft_time_limit=6000,
                 default_retry_delay=10,
                 retry_backoff=True,
                 autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError),
                 max_retries=3,
                 priority=9)
    def finalize(_self: ExtendedTask, project_id, user_id, task_id, task_name, run_id, item_id,
                 unit_source, task_status):
        _self.log_info('Cleanup redis keys')
        for k in redis.list_keys(f'sim_{task_id}_*'):
            redis.r.delete(k)
            _self.log_info(f'Deleted redis key "{k}"')

        if task_status == FAILURE:
            res = SimilarityRun.objects.filter(pk=run_id).delete()
            _self.log_info(f'Deleted on task failure: {res}')

        notify_similarity_task_completed(project_id, user_id, task_id, task_name, run_id, item_id,
                                         task_status)
        Similarity.notify_on_completed_similarity_action([project_id], user_id,
                                                         unit_source.upper())
        _self.log_info('Notification sent')

    @classmethod
    def estimate_similarity_records_count(cls, feature_src_len: int, threshold: int) -> int:
        # calculate how many similarity records we expect from <feature_src_len>
        # documents or text units with the given <threshold>

        # first, calculate expected sim. records count for the <threshold> = 75%
        A, B, C = 37385, -9.537, 0.0023
        x = feature_src_len
        y_75 = x * x if x < 200 else A + B * x + C * x * x

        # scale this value for the given <threshold>
        t = 100 - threshold
        scale = y_75 / 279078
        y = 300.164 * t * t + 3854.392 * t - 4158.586
        y *= scale
        return max(int(y), 1)


class TextUnitSimilarityByFeatures(DocumentSimilarityByFeatures):
    """
    Find Similar Text Units by extracted features
    """
    name = 'Text Unit Similarity By Features'
    engine_class = TextUnitSimilarityEngine
    unit_source = 'text_unit'
    soft_time_limit = 6000

    def get_item_id(self, kwargs):
        item_id = kwargs.get('item_id')
        document_id = kwargs.get('document_id')
        location_start = kwargs.get('location_start')
        location_end = kwargs.get('location_end')

        unit_type = kwargs.get('unit_type')
        unit_types = ['sentence', 'paragraph']
        # if unit type specified by a user, use it only
        if unit_type:
            unit_types = [unit_type]

        # get text unit ID having document coordinates
        if document_id and location_start and location_end:
            item_id = None
            for unit_type in unit_types:
                text_unit_qs = TextUnit.objects.filter(
                    document_id=document_id, unit_type=unit_type
                ).filter(
                    Q(location_start__lte=location_start, location_end__gte=location_start) |
                    Q(location_start__gte=location_start, location_end__lte=location_end) |
                    Q(location_start__lte=location_end, location_end__gte=location_end)
                ).distinct()
                if not text_unit_qs.exists():
                    continue
                if text_unit_qs.count() == 1:
                    item_id = text_unit_qs.last().id
                    break
                # if many - get the biggest one
                item_id = text_unit_qs.annotate(length=Length('text')).order_by(
                    'length').last().id
            if item_id is None:
                raise RuntimeError('Wrong location range - text units not found')
            unit_type = TextUnit.objects.get(pk=item_id).unit_type
            kwargs['unit_type'] = unit_type
        return item_id, kwargs


class PreconfiguredDocumentSimilaritySearch(ExtendedTask):
    name = 'PreconfiguredDocumentSimilaritySearch'
    verbose = True
    n_features = 100
    self_name_len = 3
    step = 2000

    def process(self, **kwargs):
        dst_field = kwargs['field']
        dst_field = DocumentField.objects.filter(pk=dst_field['pk']) \
            .prefetch_related('depends_on_fields') \
            .select_related(DST_FIELD_SIMILARITY_CONFIG_ATTR) \
            .first()  # type: DocumentField

        if not dst_field:
            raise RuntimeError('Document field not found: {0}'.format(kwargs['field']))

        proj = kwargs['project']
        proj_id = proj['pk'] if proj else None  # type:Optional[int]
        doc_query = Document.objects.filter(document_type=dst_field.document_type,
                                            project_id=proj_id) if proj_id \
            else Document.objects.filter(document_type=dst_field.document_type)

        config = getattr(dst_field,
                         DST_FIELD_SIMILARITY_CONFIG_ATTR)  # type: DocumentSimilarityConfig

        config.self_validate()

        similarity_threshold = config.similarity_threshold
        feature_vector_fields = list(dst_field.depends_on_fields.all())
        feature_vector_field_codes = [f.code for f in feature_vector_fields]

        self.log_info('{field}: Min similarity: {threshold}'
                      .format(field=dst_field.code, threshold=similarity_threshold))

        import apps.document.repository.document_field_repository as dfr
        field_repo = dfr.DocumentFieldRepository()
        qr_doc_ids = doc_query.values_list('pk', flat=True)
        doc_ids_to_code_to_value = field_repo.get_field_code_to_python_value_multiple_docs(
            document_type_id=dst_field.document_type_id,
            doc_ids=qr_doc_ids,
            field_codes_only=feature_vector_field_codes)

        field_values_list = []
        for doc_id, values in doc_ids_to_code_to_value:
            values[FIELD_CODE_DOC_ID] = doc_id
            field_values_list.append(values)

        total_docs = len(field_values_list)

        self.set_push_steps(int(5 + total_docs / 100))

        self.push()
        self.log_info(f'{dst_field.code}: Building feature vectors for {total_docs} documents')

        vectorizer = document_feature_vector_pipeline(feature_vector_fields, use_field_codes=True)
        feature_vectors = vectorizer.fit_transform(field_values_list)

        self.push()
        self.log_info('{field}: Finding similar documents (similarity >= {threshold})'
                      .format(field=dst_field.code, threshold=similarity_threshold))

        doc_ids_to_values = defaultdict(set)
        for x, doc_a_field_values in enumerate(field_values_list):
            doc_a_pk = doc_a_field_values[FIELD_CODE_DOC_ID]
            similarities = cosine_similarity(feature_vectors[x], feature_vectors)
            for y, doc_b_field_values in enumerate(field_values_list):
                doc_b_pk = doc_b_field_values[FIELD_CODE_DOC_ID]
                if doc_a_pk == doc_b_pk:
                    continue
                similarity = similarities[0, y]
                if similarity < similarity_threshold:
                    continue
                doc_ids_to_values[doc_a_pk].add(doc_b_pk)
                doc_ids_to_values[doc_b_pk].add(doc_a_pk)
            if x % 100 == 0:
                self.log_info('{field}: Checked for similarity {x} documents of {n}'
                              .format(field=dst_field.code, x=x + 1, n=total_docs))
                self.push()

        self.push()
        self.log_info(f'{dst_field.code}: Found {len(doc_ids_to_values)} similar documents. '
                      f'Storing links into the document fields.')

        doc_ids_to_values = {doc_id: list(v) if v else None for doc_id, v in doc_ids_to_values}
        field_repo.store_values_one_field_many_docs_no_ants(field=dst_field,
                                                            doc_ids_to_values=doc_ids_to_values)

        log = CeleryTaskLogger(self)
        for doc_id in doc_ids_to_values.keys():
            try:
                doc = Document.objects.get(pk=doc_id)
                signals.fire_document_changed(sender=self, log=log, document=doc,
                                              changed_by_user=None, system_fields_changed=False,
                                              generic_fields_changed=False,
                                              user_fields_changed=[dst_field.code])
            except Exception as ex:
                self.log_error(f'Unable to fire doc id change event for doc #{doc_id}', exc_info=ex)

        for project_id in set(doc_query.values_list('project_id', flat=True)):
            Action.objects.create(name='Processed Similarity Tasks',
                                  message=f'{self.name} task for project '
                                          f'"{Project.all_objects.get(id=project_id)}" is finished',
                                  user_id=kwargs.get('user_id'),
                                  view_action='update',
                                  content_type=ContentType.objects.get_for_model(Project),
                                  model_name='Project',
                                  app_label='project',
                                  object_pk=project_id)


class DeleteDocumentSimilarityResults(ExtendedTask):
    name = 'Delete Document Similarity Results'
    delete_task = DocumentSimilarityByFeatures

    def process(self, **kwargs):
        project_id = kwargs.get('project_id')
        purge_existing = kwargs.get('purge_existing', False)

        # if task revoked, there should be passed run_id - send notification for user who
        # ran similarity task
        # see remove_similarity_results_on_purge signal handler
        run_id = kwargs.get('run_id')
        if run_id and SimilarityRun.objects.filter(pk=run_id).exists():
            run = SimilarityRun.objects.get(pk=run_id)
            # store these params to get them in notification from self.task - see
            # notify_delete_similarity_completed
            self.task.kwargs['project_id'] = run.project_id
            self.task.user_id = kwargs.get('user_id')
            if not project_id:
                project_id = run.project_id

        try:
            project_repr = f'project "{Project.all_objects.get(id=project_id)}"'
        except Project.DoesNotExist:
            project_repr = 'deleted project'

        self.delete_task().delete_existing(project_id=project_id, run_id=run_id,
                                           purge_existing=purge_existing, log_info=self.log_info)

        Action.objects.create(name='Processed Similarity Tasks',
                              message=f'{self.name} task for {project_repr} is finished',
                              user_id=kwargs.get('user_id'),
                              view_action='update',
                              content_type=ContentType.objects.get_for_model(Project),
                              model_name='Project',
                              app_label='project',
                              object_pk=project_id)

    def on_success(self, *args, **kwargs):
        super().on_success(*args, **kwargs)
        notify_delete_similarity_completed(self.task, SUCCESS)

    def on_failure(self, *args, **kwargs):
        super().on_failure(*args, **kwargs)
        notify_delete_similarity_completed(self.task, FAILURE)


class DeleteTextUnitSimilarityResults(DeleteDocumentSimilarityResults):
    name = 'Delete Text Unit Similarity Results'
    delete_task = TextUnitSimilarityByFeatures


@receiver(task_deleted)
def remove_similarity_results_on_purge(sender, instance, **kwargs):
    if instance.name in [DocumentSimilarityByFeatures.name, TextUnitSimilarityByFeatures.name]:
        if isinstance(instance.metadata, dict) and 'run_id' in instance.metadata:
            run_id = instance.metadata['run_id']
            user_id = kwargs.get('user_id')
            project_id = instance.kwargs.get('project') if instance.kwargs else None
            delete_task = DeleteDocumentSimilarityResults \
                if instance.name == DocumentSimilarityByFeatures.name \
                else DeleteTextUnitSimilarityResults
            _call_task(delete_task, project_id=project_id, run_id=run_id, user_id=user_id, visible=False)


app.register_task(PreconfiguredDocumentSimilaritySearch())
app.register_task(Similarity())
app.register_task(DocumentSimilarityByFeatures())
app.register_task(TextUnitSimilarityByFeatures())
app.register_task(ChunkSimilarity())
app.register_task(PartySimilarity())
app.register_task(DeleteDocumentSimilarityResults())
app.register_task(DeleteTextUnitSimilarityResults())
