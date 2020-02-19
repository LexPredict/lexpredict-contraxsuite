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

import pickle
from typing import Tuple

from apps.celery import app
from apps.analyze.ml.cluster import ClusterDocuments, ClusterTextUnits
from apps.analyze.ml.transform import Doc2VecTransformer
from apps.analyze.ml.classify import ClassifyTextUnits, ClassifyDocuments
from apps.document.models import Document, TextUnit
from apps.task.tasks import BaseTask

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


MODULE_NAME = __name__


class TrainDoc2VecModel(BaseTask):
    name = 'Train doc2vec Model'
    priority = 9

    def process(self, **kwargs):
        source = kwargs.get('source')

        self.log_info(
            'Going to train doc2vec model from {} objects...'.format(source.upper()))

        transformer_name = kwargs.get('transformer_name')
        project_ids = kwargs.get('project_ids')

        vector_size = kwargs.get('vector_size')
        window = kwargs.get('window')
        min_count = kwargs.get('min_count')
        dm = kwargs.get('dm')

        transformer = Doc2VecTransformer(vector_size=vector_size, window=window,
                                         min_count=min_count, dm=dm)

        model_builder_args = dict(project_ids=project_ids, transformer_name=transformer_name)
        if source == 'document':
            model_builder = transformer.build_doc2vec_document_model
        else:
            model_builder = transformer.build_doc2vec_text_unit_model
            model_builder_args['text_unit_type'] = kwargs.get('text_unit_type')

        model_builder(**model_builder_args)


class TrainClassifier(BaseTask):
    name = 'TrainClassifier'

    def process(self, **kwargs):
        self.set_push_steps(3)

        target = kwargs.pop('target')

        # restrict to certain project otherwise test set could be too large
        project = kwargs.pop('project')
        project_id = project['pk']    # if project else None

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
            train_project_id=project_id,
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


class RunClassifier(BaseTask):
    name = 'RunClassifier'

    def process(self, **kwargs):
        self.set_push_steps(3)

        target = kwargs.pop('target')

        # restrict to certain project otherwise test set could be too large
        project = kwargs.pop('project')
        project_id = project['pk']    # if project else None

        classifier_selection = kwargs.pop('classifier', None)
        classifier_id = classifier_selection['pk'] if classifier_selection else None

        min_confidence = kwargs.pop('min_confidence', 80)
        unit_type = kwargs.pop('unit_type', 'sentence')

        engine_cls = ClassifyDocuments if target == 'document' else ClassifyTextUnits
        engine = engine_cls()

        self.push()  # 1

        if kwargs['delete_suggestions']:
            deleted = engine.suggestion_db_model.objects.filter(classifier_id=classifier_id).delete()
            self.log_info('Deleted "{}"'.format(deleted[1]))

        self.push()  # 2

        classifier = engine.classifier_db_model.objects.get(pk=classifier_id)

        self.log_info('Run classifier "{}"'.format(classifier))
        # log info about classifier model args
        clf_model = pickle.loads(classifier.model_object)
        self.log_info('Classifier model: {}'.format(clf_model.get_params()['classifier']))

        count_created_suggestions = engine.run_classifier(
            classifier,
            test_project_id=project_id,
            unit_type=unit_type,
            min_confidence=min_confidence)

        self.log_info('Created {} "{}" objects'.format(count_created_suggestions,
                                                       engine.suggestion_db_model.__name__))
        self.push()  # 3


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

        if cluster_target == 'documents':
            query = Document.objects.all()
            if proj_id:
                query = query.filter(project_id=proj_id)
            count = query.count()
            count_limit = 1000  # 1669 might be (not necessarily) too much
        else:
            query = TextUnit.objects.all()
            if proj_id:
                query = query.filter(document__project_id=proj_id)
            count = query.count()
            count_limit = 500000  # 2 753 672 is definitely too much

        return count, count_limit


app.register_task(TrainDoc2VecModel())
app.register_task(TrainClassifier())
app.register_task(RunClassifier())
app.register_task(Cluster())
