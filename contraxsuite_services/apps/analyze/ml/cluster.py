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
import inspect
import sys
from typing import Callable

import numpy as np
import sklearn.cluster
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfTransformer

from apps.analyze.models import DocumentCluster, TextUnitCluster
from apps.document.models import Document, TextUnit
from apps.analyze.ml.features import DocumentFeatures, TextUnitFeatures, Document2VecFeatures, TextUnit2VecFeatures

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class ClusterEngine:
    """
    Base class to configure Cluster algorithm with default options
    and callable methods depending of algorithm class itself
    :Example:
        >>> engine_wrapper = Birch()
        >>> clustering = engine_wrapper(
        >>>    features=term_frequency_matrix,
        >>>    term_index=term_index,
        >>>    use_tfidf=True,
        >>>    **cluster_options)
    Returns ClusterEngine instance with attributes listed in __init__
    """
    engine = None

    def __init__(self):
        """
        Inject class instance attributes to return after clustering
        """
        self.cluster_labels = None
        self.cluster_label_set = None
        self.cluster_centers = None
        self.cluster_terms = None
        self.data2d = None
        self.centers2d = None
        self.features = None

    def __call__(self, features: np.array, term_index: list, use_tfidf: bool = True, **options):
        """
        Just call activated class instance to cluster data.
        :param features: np.array - term frequency matrix
        :param term_index:  list - list of term frequency matrix indexes
        :param use_tfidf: bool - whether to use TF IDF Transformer
        :param options: **dict - unpacked cluster algorithm options
        :return: ClusterEngine instance with attributes listed in __init__
        """
        self.features = features
        self.term_index = term_index
        self.num_records = features.shape[0]
        self.use_tfidf = use_tfidf
        self.user_options = options
        self.n_clusters = options.get('n_clusters')
        self.cluster_model = self.get_model()
        return self.cluster()

    def get_engine_options(self):
        """
        Get default clustering algorithm options from class attributes and substitute them with
        incoming user-defined options if they are, otherwise use defaults.
        Checks if get_some_callable_option method exists and uses it instead of class attribute.
        :return: dict - engine options dictionary
        """
        engine_options = dict()
        allowed_engine_option_names = list(inspect.signature(self.engine.__init__).parameters.keys())[1:]
        for option_name in allowed_engine_option_names:

            # get class attribute-option
            if hasattr(self, option_name):
                engine_options[option_name] = getattr(self, option_name)

            # get user option from incoming kwargs
            if option_name in self.user_options:
                engine_options[option_name] = self.user_options[option_name]

            # init callable option
            option_method = getattr(self, 'get_' + option_name, None)
            if option_method and callable(option_method):
                option_value = engine_options.get(option_name)
                engine_options[option_name] = option_method(option_value)

        return engine_options

    def get_some_callable_option(self, option_value=None):
        """
        Just a sample to show a signature of callable algorithm method
        """
        pass

    def get_model(self):
        """
        Activates cluster model with filled options
        :return: activated cluster model like Kmeans(**options)
        """
        options = self.get_engine_options()
        return self.engine(**options)

    def cluster(self):
        """
        Central method to process incomind data with chosen activated Clustering model
        :return: ClusterEngine instance with attributes listed in __init__
        """

        # Toggle TF-IDF and cluster
        if self.use_tfidf:
            self.features = TfidfTransformer().fit_transform(self.features).toarray()

        # Return labels and representative points/centers
        self.cluster_labels = self.cluster_model.fit_predict(self.features).tolist()

        # for DBSCAN (it produces -1 label)
        if -1 in self.cluster_labels:
            self.cluster_labels = [i + 1 for i in self.cluster_labels]

        self.cluster_centers = self.get_cluster_centers()

        pca = PCA(n_components=2).fit(self.features)
        self.data2d = pca.transform(self.features)

        self.cluster_label_set = set(self.cluster_labels)

        try:
            order_centroids = self.cluster_centers.argsort()[:, ::-1]
            self.cluster_terms = [[self.term_index[ind] for ind in order_centroids[i, :10]] for i in
                                  range(max(self.cluster_label_set) + 1)]
            self.centers2d = pca.transform(self.cluster_centers)
        except Exception as e:
            print(e)

        return self

    def get_cluster_centers(self):
        """
        Default method to locate cluster centers
        :return: list of cluster centers
        """
        return self.cluster_model.cluster_centers_


class Dbscan(ClusterEngine):
    engine = sklearn.cluster.DBSCAN
    eps = 0.5
    min_samples = 2
    metric = 'euclidean'
    n_jobs = 1

    def get_min_samples(self, option_value):
        return min(option_value or self.num_records, self.num_records)

    def get_cluster_centers(self):
        return self.cluster_model.components_


class Birch(ClusterEngine):
    engine = sklearn.cluster.Birch
    threshold = 0.5
    branching_factor = 50

    def get_n_clusters(self, option_value):
        return min(option_value or self.num_records, self.num_records)

    def get_cluster_centers(self):
        return self.cluster_model.subcluster_centers_


class Optics(ClusterEngine):
    engine = sklearn.cluster.OPTICS
    min_samples = 2
    max_eps = 50
    n_jobs = 1

    def get_min_samples(self, option_value):
        return min(option_value or self.num_records, self.num_records)

    def get_cluster_centers(self):
        return np.array([])


class Kmeans(ClusterEngine):
    engine = sklearn.cluster.KMeans
    max_iter = 100

    def get_n_clusters(self, option_value):
        return min(option_value or self.num_records, self.num_records)


class MinibatchKmeans(ClusterEngine):
    engine = sklearn.cluster.MiniBatchKMeans
    init = 'k-means++'
    n_init = 3
    init_size = 100
    batch_size = 100
    max_iter = 100

    def get_n_clusters(self, option_value):
        return min(option_value or self.num_records, self.num_records)


class ClusterDocuments:
    """
    Cluster incoming documents.
    :Example:
        >>> model = ClusterDocuments(project_id=29, cluster_algorithm='birch', n_clusters=3, some_param=some_val)
        >>> clustering = model.run()
        >>> clustering.metadata

    """
    default_cluster_name = 'Document Cluster'
    db_target_model = Document
    db_cluster_model = DocumentCluster
    db_cluster_model_m2m_name = 'documents'
    point_item_id_name = 'document_id'
    point_item_name_field = 'document_name'

    def __init__(self,
                 queryset=None,
                 project_id=None,
                 use_tfidf=True,
                 n_clusters=3,
                 cluster_algorithm='kmeans',
                 cluster_by='term',
                 unit_type='sentence',
                 name=None,
                 use_default_name=False,
                 description=None,
                 log_message: Callable[[str, str], None] = None,
                 create_cluster_for_unclustered: bool = True,
                 **cluster_options):
        """
        :param queryset: Document/TextUnit queryset
        :param project_id: int
        :param use_tfidf: bool - whether use TF IDF normalizer
        :param n_clusters: int - number of clusters to produce
        :param cluster_algorithm: str
        :param cluster_by: str or list[str] - source name - e.g. "term", or ["term", "date"]
        :param unit_type: str - one of "sentence", "paragraph"
        :param name: str - clustering custom name
        :param use_default_name: bool - use default name "Default({cluster_pk})"
        :param description: str - clustering custom description
        :param log_message: log routine(msg: str, msg_key: str)
        :param create_cluster_for_unclustered: create a cluster obj for unclustered items
        :param cluster_options: **kwargs for cluster model
        """
        self.features_model = DocumentFeatures
        self.project_id = project_id
        self.queryset = queryset
        self.use_tfidf = use_tfidf
        self.n_clusters = n_clusters
        cluster_options['n_clusters'] = n_clusters
        self.cluster_algorithm = cluster_algorithm.lower()
        self.cluster_options = cluster_options
        self.cluster_by = cluster_by
        self.cluster_by_str = ', '.join(self.cluster_by) if isinstance(cluster_by, (list, tuple)) else self.cluster_by
        self.unit_type = unit_type
        self.name = name
        self.use_default_name = use_default_name
        self.description = description
        self.engine_wrapper = self.get_engine_wrapper()
        self.start_date = None
        self.log_message_routine = log_message
        self.create_cluster_for_unclustered = create_cluster_for_unclustered
        self.init_classifier()

    def init_classifier(self):
        if self.cluster_by == 'text' or self.cluster_by == ['text']:
            self.features_model = Document2VecFeatures

    def get_engine_wrapper(self):
        """
        Get cluster engine representing wrapper around clustering algorithm
        :return: ClusterEngine()
        """
        this_module_classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        engine_wrappers = {name.lower(): obj for name, obj in this_module_classes
                           if issubclass(obj, ClusterEngine)}
        if self.cluster_algorithm in engine_wrappers:
            return engine_wrappers[self.cluster_algorithm]()
        raise RuntimeError(
            "Clustering algorithm {} not implemented; must be one of {}".format(
                self.cluster_algorithm, str(list(engine_wrappers))))

    def run(self):
        """
        Cluster generic records,
        create DB Cluster objects,
        generate "cluster_data" object representing clustering results like cluster ids, centers, coords, etc.
        :return: ClusterEngine instance with clusters data
        """
        self.start_date = datetime.datetime.now()

        # Get term frequency matrix and indexes
        feature_obj = self.features_model(
            queryset=self.queryset,
            project_id=self.project_id,
            feature_source=self.cluster_by,
            unit_type=self.unit_type,
            log_message=self.log_message_routine).get_features()
        elapsed = (datetime.datetime.now() - self.start_date).total_seconds()
        self.log_message(f'Getting features took {elapsed} seconds.')

        # Run cluster model - the magic is here!
        clustering = self.engine_wrapper(
            features=feature_obj.feature_df,
            term_index=feature_obj.feature_names,
            use_tfidf=self.use_tfidf,
            **self.cluster_options)

        # create clustering results "metadata" object to store f.e. in ProjectClustering instance
        metadata = dict(
            n_clusters=self.n_clusters,
            method=self.cluster_algorithm,
            use_tfidf=self.use_tfidf,
            cluster_by=self.cluster_by,
            unit_type=self.unit_type,
            project_id=self.project_id,
            method_options=self.cluster_options,
            clusters_data=dict(),
            points_data=list(),
            cluster_obj_ids=list(),
            unclustered_item_ids=feature_obj.unqualified_item_ids,
            unclustered_item_names=feature_obj.unqualified_item_names,
        )

        # TODO: consider some unification here to avoid duplication
        # TODO: consider to make separate models like DocumentClusterPoints, etc.
        # TODO: consider to make separate fields DocumentCluster.coord, DocumentCluster.terms, etc.

        # collect all points data to store in "global" metadata
        all_points_data = metadata['points_data']
        # collect per-cluster points data to store in Cluster db object
        cluster_items_points_data = dict()
        item_names = feature_obj.item_names

        if clustering.data2d is not None:
            if item_names is None:
                item_names = feature_obj.item_index
            mapped_vals = zip(clustering.cluster_labels, feature_obj.item_index, item_names, clustering.data2d)
            for cluster_label_id, item_id, item_name, coord in mapped_vals:
                item_data = dict(coord=coord.tolist(), cluster_id=cluster_label_id)
                item_data[self.point_item_name_field] = item_name
                item_data[self.point_item_id_name] = item_id

                if cluster_label_id not in cluster_items_points_data:
                    cluster_items_points_data[cluster_label_id] = list()
                cluster_items_points_data[cluster_label_id].append(item_data)

                all_points_data.append(item_data)

        # Create each document cluster,
        # transform "clustering" object into raw data
        # - store it in db_obj.metadata and clustering.metadata
        n = 0
        clusters_data = metadata['clusters_data']
        for n, cluster_label_id in enumerate(clustering.cluster_label_set):

            # Lookup doc-id in index
            cluster_item_id_list = [feature_obj.item_index[n] for n, label in enumerate(clustering.cluster_labels)
                                    if label == cluster_label_id]

            cluster_terms = clustering.cluster_terms[n] if clustering.cluster_terms else None

            # create DB Cluster object
            cluster_obj = self.create_db_cluster_object(cluster_label_id, cluster_terms, cluster_item_id_list)
            metadata['cluster_obj_ids'].append(cluster_obj.pk)

            cluster_obj_metadata = dict(
                cluster_terms=cluster_terms,
                centroid_coord=clustering.centers2d[n].tolist() if clustering.centers2d is not None else None,
                cluster_obj_id=cluster_obj.pk
            )
            clusters_data[cluster_label_id] = cluster_obj_metadata

            # store metadata for cluster object
            if cluster_label_id in cluster_items_points_data:
                cluster_obj_metadata['points_data'] = cluster_items_points_data[cluster_label_id]
            cluster_obj.metadata = cluster_obj_metadata
            cluster_obj.save()

        if self.create_cluster_for_unclustered and feature_obj.unqualified_item_ids:
            cluster_label_id = n + 1
            cluster_obj = self.create_db_cluster_object(cluster_label_id, ['unclustered'], feature_obj.unqualified_item_ids)
            metadata['cluster_obj_ids'].append(cluster_obj.pk)

            cluster_obj_metadata = dict(
                cluster_terms=['unclustered'],
                centroid_coord=[],
                points_data=[],
                cluster_obj_id=cluster_obj.pk
            )
            clusters_data[cluster_label_id] = cluster_obj_metadata
            cluster_obj.metadata = cluster_obj_metadata
            cluster_obj.name = 'Unclustered'
            cluster_obj.save()
            del metadata['unclustered_item_ids']
            del metadata['unclustered_item_names']

        clustering.metadata = metadata
        return clustering

    def create_db_cluster_object(self, cluster_label_id, cluster_terms, cluster_item_id_list):
        """
        Store a CLuster in DB, set M2M relation from cluster_item_id_list
        :param cluster_label_id: str
        :param cluster_self_name: str
        :param cluster_item_id_list: list of cluster item indexes
        :return: DB object pk
        """
        cluster_title = self.name or self.get_db_cluster_title(cluster_label_id)
        cluster_self_name = '-'.join([str(c) for c in cluster_terms[:5]]) if cluster_terms else None

        db_cluster_obj = self.db_cluster_model.objects.create(
            cluster_id=cluster_label_id,
            name=cluster_title,
            self_name=cluster_self_name,
            description=self.description or cluster_title,
            cluster_by=self.cluster_by_str,
            using=self.cluster_algorithm,
            created_date=self.start_date)

        # set m2m
        getattr(db_cluster_obj, self.db_cluster_model_m2m_name).set(cluster_item_id_list)

        # set default cluster name
        if self.use_default_name:
            db_cluster_obj.name = "Cluster #{}".format(db_cluster_obj.pk)
            db_cluster_obj.save()

        return db_cluster_obj

    def get_db_cluster_title(self, cluster_label_id=None):
        cluster_name = '''{cluster_name_prefix} {for_} cluster_label_id={cluster_label_id} \
        unit_type={unit_type} date={start_date}'''.format(
            cluster_name_prefix=self.name or self.default_cluster_name,
            for_='project_id={}'.format(self.project_id) if self.project_id else 'for=queryset',
            cluster_label_id=cluster_label_id,
            unit_type=self.unit_type,
            start_date=self.start_date)
        return cluster_name

    def log_message(self, msg: str, msg_key='') -> None:
        if self.log_message_routine:
            self.log_message_routine(msg, msg_key)


class ClusterTextUnits(ClusterDocuments):
    features_model = TextUnitFeatures
    default_cluster_name = 'Text Unit Cluster'
    db_target_model = TextUnit
    db_cluster_model = TextUnitCluster
    db_cluster_model_m2m_name = 'text_units'
    point_item_id_name = 'text_unit_id'
    point_item_name_field = 'text_unit_name'

    def init_classifier(self):
        if self.cluster_by == 'text' or self.cluster_by == ['text']:
            self.features_model = TextUnit2VecFeatures
