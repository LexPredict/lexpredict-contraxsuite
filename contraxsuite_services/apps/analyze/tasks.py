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
import pickle
from celery.exceptions import SoftTimeLimitExceeded
from celery.utils.log import get_task_logger
from psycopg2 import InterfaceError, OperationalError
from typing import Tuple, List, Optional

from django.utils import timezone

import task_names
from apps.analyze.ml.utils import ProjectsNameFilter
from apps.analyze.models import BaseClassifier, DocumentVector, BaseVector, TextUnitVector, MLModel
from apps.celery import app
from apps.analyze.ml.cluster import ClusterDocuments, ClusterTextUnits
from apps.analyze.ml.transform import Doc2VecTransformer
from apps.analyze.ml.classify import ClassifyTextUnits, ClassifyDocuments
from apps.analyze.models import SimilarityRun
from apps.analyze.notifications import notify_build_vectors_completed
from apps.common.utils import get_free_mem
from apps.document.models import Document, TextUnit, DocumentText
from apps.project.models import Project
from apps.task.tasks import ExtendedTask
from apps.task.utils.task_utils import TaskUtils

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


logger = get_task_logger(__name__)

MODULE_NAME = __name__


class FeatureStoringTask(ExtendedTask):
    def save_feature_vectors(self):
        self.log_info('Saving feature vectors...')
        model_class = MLModel
        vector_class = DocumentVector if self.source == 'document' else TextUnitVector
        transformer = (self.transformer if hasattr(self, 'transformer') else None) or \
            model_class.objects.get(pk=self.transformer_id)
        id_field = 'document_id' if self.source == 'document' else 'id'

        if self.source == 'document':
            data_query = DocumentText.objects.all()
            if self.project_ids:
                data_query = data_query.filter(document__project_id__in=self.project_ids)
            data = data_query.values_list(id_field, 'full_text')
        else:
            data_query = TextUnit.objects.filter(unit_type=self.text_unit_type)
            if self.project_ids:
                data_query = data_query.filter(document__project_id__in=self.project_ids)
            data = data_query.values_list(id_field, 'text')

        if self.delete_existing:
            lookup = 'document_id__in' if self.source == 'document' else 'text_unit_id__in'
            data_ids = data_query.values_list(id_field, flat=True)
            try:
                vector_class.objects.filter(**{lookup: data_ids}).delete()
            except Exception as e:
                self.log_error('Error deleting existing records', exc_info=e)
                raise
        else:
            # try to avoid creating duplicated vectors of chosen transformer
            lookup = 'document__documentvector__transformer' if self.source == 'document'\
                else 'text_unit__textunitvector__transformer'
            self.log_info(f'{data.filter(**{lookup: transformer}).count()} vectors exist')
            data = data.exclude(**{lookup: transformer})

        vectors = Doc2VecTransformer.create_vectors(
            transformer,
            data,
            vector_class,
            id_field)  # type: List[BaseVector]
        # save vectors
        self.log_info(f'Save {len(vectors)} vectors')
        if not vectors:
            return
        try:
            vector_class.objects.bulk_create(vectors, ignore_conflicts=True)
        except Exception as e:
            self.log_error(f'Error storing {vector_class.__name__}', exc_info=e)
            raise


class TrainDoc2VecModel(FeatureStoringTask):
    name = 'Train doc2vec Model'
    priority = 7
    soft_time_limit = 3 * 3600

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_ids = []  # type: Optional[List[int]]
        self.transformer = None  # type: Optional[MLModel]
        self.source = 'document'
        self.text_unit_type = 'sentence'
        self.delete_existing = True

    def process(self, **kwargs):
        self.source = kwargs.get('source')
        transformer_class = MLModel
        self.log_info(f'Training doc2vec model from {self.source.upper()} objects...')
        self.log_info(f'Free memory initially: {get_free_mem()}')
        transformer_name = kwargs.get('transformer_name')
        if transformer_class.objects.filter(name=transformer_name).count() > 0:
            raise RuntimeError(f"There's already a(n) {transformer_class.__name__} with name '{transformer_name}'")

        self.project_ids = kwargs.get('project_ids')
        vector_size = kwargs.get('vector_size')
        window = kwargs.get('window')
        min_count = kwargs.get('min_count')
        dm = kwargs.get('dm')
        build_vectors = kwargs.get('build_vectors')
        self.text_unit_type = kwargs.get('text_unit_type') or self.text_unit_type

        transformer = Doc2VecTransformer(vector_size=vector_size,
                                         window=window,
                                         min_count=min_count,
                                         dm=dm,
                                         log_message=lambda m: self.log_info(m))

        model_builder_args = dict(project_ids=self.project_ids,
                                  transformer_name=transformer_name)
        if self.source == 'document':
            model_builder = transformer.build_doc2vec_document_model
        else:
            model_builder = transformer.build_doc2vec_text_unit_model
            model_builder_args['text_unit_type'] = self.text_unit_type
        self.log_info(f'Doc2vec model is built')

        _, transformer = model_builder(**model_builder_args)  # gensim.models.doc2vec.Doc2Vec, MLModel
        self.log_info(f'Doc2vec transformer is built')
        self.transformer = transformer
        if build_vectors:
            self.save_feature_vectors()


class BuildDocumentVectorsTask(FeatureStoringTask):
    name = 'Build Document Vectors'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source = 'document'
        self.project_ids = []  # type: Optional[List[int]]
        self.delete_existing = True
        self.transformer_id = 0

    def process(self, **kwargs):
        project = kwargs.get('project') or []
        self.project_ids = [project] if isinstance(project, (int, str)) else project
        self.delete_existing = kwargs.get('delete_existing', False)
        self.transformer_id = kwargs.get('transformer_id')
        self.save_feature_vectors()

    def on_success(self, *args, **kwargs):
        super().on_success(*args, **kwargs)
        notify_build_vectors_completed(self.project_ids, self.task, 'success')

    def on_failure(self, *args, **kwargs):
        super().on_failure(*args, **kwargs)
        notify_build_vectors_completed(self.project_ids, self.task, 'failure')


class BuildTextUnitVectorsTask(BuildDocumentVectorsTask):
    name = 'Build Text Unit Vectors'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source = 'text_unit'
        self.text_unit_type = 'sentence'

    def process(self, **kwargs):
        project = kwargs.get('project') or []
        self.project_ids = [project] if isinstance(project, (int, str)) else project
        self.text_unit_type = kwargs.get('txt_unit_type', 'sentence')
        self.delete_existing = kwargs.get('delete_existing', False)
        self.transformer_id = kwargs.get('transformer_id')
        self.save_feature_vectors()


class TrainClassifier(ExtendedTask):
    name = 'TrainClassifier'

    def process(self, **kwargs):
        self.set_push_steps(3)

        target = kwargs.pop('target')

        # restrict to certain project otherwise test set could be too large
        projects = kwargs.pop('project')
        project_name_filter = kwargs.pop('project_name_filter')
        project_ids = [p['pk'] for p in projects] if projects else []

        class_name = kwargs.pop('class_name', None)
        classify_by = kwargs.pop('classify_by', 'term')
        classifier_algorithm = kwargs.pop('algorithm', 'RandomForestClassifier')
        classifier_name = kwargs.pop('classifier_name', None)
        metric_pos_label = kwargs.pop('metric_pos_label', None) or None
        use_tfidf = kwargs.pop('use_tfidf', True)
        unit_type = kwargs.pop('unit_type', 'sentence')
        classifier_options = kwargs

        engine_cls = ClassifyDocuments if target == 'document' else ClassifyTextUnits
        engine = engine_cls()

        self.push()  # 1

        if kwargs.get('delete_classifier'):
            deleted = engine.classifier_db_model.objects.filter(class_name=class_name).delete()
            self.log_info('Deleted "{}"'.format(deleted[1]))

        self.push()  # 2

        classifier = engine.build_classifier(
            train_project_id=project_ids,
            project_name_filter=project_name_filter,
            classify_by=classify_by,
            class_name=class_name,
            classifier_algorithm=classifier_algorithm,
            classifier_assessment=True,
            classifier_name=classifier_name,
            metric_pos_label=metric_pos_label,
            use_tfidf=use_tfidf,
            unit_type=unit_type,
            **classifier_options)

        self.log_info('Created "{}" classifier'.format(classifier))
        # log info about classifier model args
        clf_model = pickle.loads(classifier.model_object)
        self.log_info('Classifier model: {}'.format(clf_model.get_params()['classifier']))
        self.push()  # 3


class RunClassifier(ExtendedTask):
    name = 'RunClassifier'

    def process(self, **kwargs):
        self.set_push_steps(3)

        target = kwargs.pop('target')

        # restrict to certain project otherwise test set could be too large
        projects = kwargs.pop('project')
        project_name_filter = kwargs.pop('project_name_filter')

        project_ids = [p['pk'] for p in projects] if projects else []
        if not project_ids and project_name_filter:
            project_ids = ProjectsNameFilter.filter_objects_by_name(Project, project_name_filter)

        classifier_selection = kwargs.pop('classifier', None)
        classifier_id = classifier_selection['pk'] if classifier_selection else None

        min_confidence = kwargs.pop('min_confidence', 80)
        unit_type = kwargs.pop('unit_type', 'sentence')

        engine_cls = ClassifyDocuments if target == 'document' else ClassifyTextUnits
        engine = engine_cls()

        self.push()  # 1

        if kwargs['delete_suggestions']:
            deleted = engine.suggestion_db_model.objects.filter(classifier_id=classifier_id).delete()
            self.log_info(f'Deleted "{deleted[1]}"')

        self.push()  # 2

        classifier = engine.classifier_db_model.objects.get(pk=classifier_id)  # type: BaseClassifier

        self.log_info(f'Run classifier "{classifier}"')
        # log info about classifier model args
        clf_model = pickle.loads(classifier.model_object)
        self.log_info('Classifier model: {}'.format(clf_model.get_params()['classifier']))

        count_created_suggestions = engine.run_classifier(
            classifier,
            test_project_id=project_ids,
            unit_type=unit_type,
            min_confidence=min_confidence)

        self.log_info(f'Created {count_created_suggestions} '
                      f'"{engine.suggestion_db_model.__name__}" objects')

        self.push()  # 3


class Cluster(ExtendedTask):
    """
    Cluster Documents, Text Units
    """
    # TODO: cluster by expanded entity aliases

    name = 'Cluster'

    soft_time_limit = 3 * 3600
    default_retry_delay = 10
    retry_backoff = True
    autoretry_for = (SoftTimeLimitExceeded, InterfaceError, OperationalError)
    max_retries = 3

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
        cluster_options = {}
        for option_name, option_value in kwargs.items():
            if option_name.startswith(cluster_algorithm + '_'):
                option_name = option_name.replace(cluster_algorithm + '_', '')
                cluster_options[option_name] = option_value

        if do_cluster_documents:
            cluster_class = ClusterDocuments
        elif do_cluster_text_units:
            cluster_class = ClusterTextUnits
        else:
            self.log_error("CLuster task target (documents or text units) is not specified.")
            return

        cluster_model = cluster_class(project_id=project_id,
                                      cluster_algorithm=cluster_algorithm,
                                      n_clusters=n_clusters,
                                      cluster_by=cluster_by,
                                      name=cluster_name,
                                      description=cluster_desc,
                                      use_tfidf=use_tfidf,
                                      unit_type=unit_type,
                                      **cluster_options)
        result = cluster_model.run()
        try:
            self.log_info('Created clusters (ids): {}'.format(result.metadata['cluster_obj_ids']))
        except:
            pass

    @classmethod
    def estimate_reaching_limit(cls, data) -> Tuple[int, int]:
        cluster_target = 'documents' if data.get('do_cluster_documents') else 'units'
        project = data.get('project')
        proj_id = project.id if project else None
        from apps.analyze.app_vars import NOTIFY_TOO_MANY_DOCUMENTS, NOTIFY_TOO_MANY_UNITS
        if cluster_target == 'documents':
            query = Document.objects.all()
            if proj_id:
                query = query.filter(project_id=proj_id)
            count = query.count()
            count_limit = NOTIFY_TOO_MANY_DOCUMENTS.val()  # 1669 might be (not necessarily) too much
        else:
            query = TextUnit.objects.all()
            if proj_id:
                query = query.filter(document__project_id=proj_id)
            count = query.count()
            count_limit = NOTIFY_TOO_MANY_UNITS.val()  # 2 753 672 is definitely too much

        return count, count_limit


@app.task(name=task_names.TASK_NAME_DELETE_EXPIRED_SIMILARITY, bind=True)
def delete_expired_similarity_objects(_celery_task):
    """
    Delete expired DocumentSimilarity/TextUnitSimilarity objects
    """
    TaskUtils.prepare_task_execution()

    from apps.analyze.app_vars import DOCUMENT_SIMILARITY_OBJECTS_EXPIRE_IN, TEXT_UNIT_SIMILARITY_OBJECTS_EXPIRE_IN
    arguments = [(DOCUMENT_SIMILARITY_OBJECTS_EXPIRE_IN, 'document', 'Document'),
                 (TEXT_UNIT_SIMILARITY_OBJECTS_EXPIRE_IN, 'text_unit', 'Text Unit')]
    for var, unit_source, unit_title in arguments:
        exp_date = timezone.now() - datetime.timedelta(seconds=var.val())
        qs = SimilarityRun.objects.filter(unit_source=unit_source,
                                          created_date__isnull=False,
                                          created_date__lte=exp_date)
        print(f'Track expired {unit_title} Similarity Runs: {qs.count()} runs expired')
        deleted = qs.delete()
        if deleted[0]:
            print(f'Deleted {deleted[1]}')


app.register_task(BuildDocumentVectorsTask())
app.register_task(BuildTextUnitVectorsTask())
app.register_task(TrainDoc2VecModel())
app.register_task(TrainClassifier())
app.register_task(RunClassifier())
app.register_task(Cluster())
