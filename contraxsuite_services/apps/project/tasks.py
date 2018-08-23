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

import sys

# Third-party imports
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer
from sklearn.cluster import Birch, KMeans, MiniBatchKMeans
from sklearn.decomposition import PCA

# Django imports
from django.utils.timezone import now
from django.db.models import Count

# Project imports
from apps.analyze.models import DocumentCluster
from apps.celery import app
from apps.document.models import Document
from apps.project.models import Project, ProjectClustering, UploadSession
from apps.task.tasks import BaseTask
from apps.task.utils.task_utils import TaskUtils
from urls import custom_apps

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.3/LICENSE"
__version__ = "1.1.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

THIS_MODULE = __name__


class ClusterProjectDocuments(BaseTask):
    """
    Cluster Project Documents
    """
    name = 'Cluster Project Documents'

    queue = 'high_priority'

    def process(self, **kwargs):

        n_clusters = kwargs.get('n_clusters')
        method = kwargs.get('method')
        project_id = kwargs.get('project_id')

        project_clustering_id = kwargs.get('project_clustering_id')
        project_clustering = ProjectClustering.objects.get(
            pk=project_clustering_id) if project_id else None
        project_clustering.task = self.task
        project_clustering.save()

        project = project_clustering.project

        self.log_info('Start clustering documents for project id={}'.format(project_id))
        self.log_info('Clustering method: "{}", n_clusters={}'.format(method, n_clusters))

        self.set_push_steps(3)

        # get documents data
        documents = Document.objects.filter(project_id=project_id)
        id_name_map = {k: v for k, v in documents.values_list('id', 'name')}
        docs_count = len(id_name_map)

        # cluster by full text
        if kwargs.get('cluster_by') == 'full_text':
            docs = np.array(documents.values_list('pk', 'full_text'))
            pks, data = docs[:, 0], docs[:, 1]

            # try increase min_df if exception occurs while fit_trasform
            for max_df in range(50, 101, 5):
                max_df = float(max_df / 100)
                try:
                    vectorizer = TfidfVectorizer(max_df=max_df, max_features=100,
                                                 min_df=2, stop_words='english',
                                                 use_idf=True)
                    X = vectorizer.fit_transform(data)
                except ValueError as e:
                    if 'Try a lower min_df or a higher max_df' in str(e):
                        continue
                    else:
                        raise e
                break

            terms = vectorizer.get_feature_names()

        # Cluster by terms
        else:
            id_field = 'id'
            prop_field = 'textunit__termusage__term__term'
            # filter non-null, null
            qs = documents.filter(textunit__termusage__isnull=False)
            if not qs.exists():
                raise RuntimeError('No terms in documents detected, try to re-run terms parser.')
            # get values
            ann_cond = dict(prop_count=Count(prop_field))
            qs = qs.values(id_field, prop_field).annotate(**ann_cond).distinct()
            # get data
            df = pd.DataFrame(list(qs)).dropna()
            null_qs = documents.exclude(textunit__termusage__isnull=False)
            if null_qs.exists():
                null_df = pd.DataFrame(list(null_qs.values('id'))).set_index('id')
                df = df.join(null_df, how='outer', on='id')
            df = df.pivot(index=id_field, columns=prop_field, values='prop_count').fillna(0)

            X = df.as_matrix()
            # convert CountVec into TFvec
            tf_transformer = TfidfTransformer(use_idf=False).fit(X)
            X = tf_transformer.transform(X)

            pks = df.index.tolist()
            terms = df.columns.tolist()

        if method == 'Birch':
            m = Birch(
                n_clusters=n_clusters,
                threshold=0.5,
                branching_factor=50)
        elif method == 'MiniBatchKMeans':
                m = MiniBatchKMeans(
                    n_clusters=n_clusters,
                    init='k-means++',
                    n_init=1,
                    init_size=100,
                    batch_size=100,
                    verbose=False)
        else:
            method = 'KMeans'
            m = KMeans(
                n_clusters=n_clusters,
                init='k-means++',
                max_iter=100,
                n_init=1,
                verbose=False)

        m.fit(X)
        self.push()

        X = X.toarray()
        pca = PCA(n_components=2).fit(X)
        data2d = pca.transform(X)

        if method == 'DBSCAN':
            clusters = m.labels_
            cluster_labels = set(clusters)
            # reshape cluster labels
            if -1 in cluster_labels:
                cluster_labels = [i + 1 for i in cluster_labels]
            cluster_terms = cluster_labels
            centers2d = None
        else:
            if method == 'Birch':
                cluster_centers = m.subcluster_centers_
            else:
                cluster_centers = m.cluster_centers_

            order_centroids = cluster_centers.argsort()[:, ::-1]
            clusters = m.labels_.tolist()
            cluster_labels = set(clusters)
            _n_clusters = len(cluster_labels)
            cluster_terms = [[terms[ind] for ind in order_centroids[i, :10]] for i in
                             range(_n_clusters)]
            centers2d = pca.transform(cluster_centers)

        points_data = [{'document_id': pks[i],
                        'document_name': id_name_map[pks[i]],
                        'coord': data2d[i].tolist(),
                        'cluster_id': str(clusters[i])} for i in range(docs_count)]

        self.push()

        clusters_data = {}
        created_date = now()
        for cluster_id in cluster_labels:
            cluster_label = cluster_terms[cluster_id]
            if isinstance(cluster_label, list):
                cluster_label = '-'.join(cluster_label[:5])
            cluster = DocumentCluster.objects.create(
                cluster_id=cluster_id,
                name='Project id={}'.format(project.pk if project else None),
                self_name=cluster_label,
                description='Cluster Project (id={}) with Multiple Contract Types'.format(
                    project_id),
                cluster_by='all',
                using=method,
                created_date=created_date)
            cluster_documents = [i['document_id'] for i in points_data
                                 if i['cluster_id'] == str(cluster_id)]
            cluster.documents.set(cluster_documents)
            clusters_data[str(cluster_id)] = dict(
                cluster_obj_id=cluster.pk,
                cluster_terms=cluster_terms[cluster_id],
                centroid_coord=centers2d[cluster_id].tolist() if centers2d is not None else None
            )
            project_clustering.document_clusters.add(cluster)

        result = {'method': method,
                  'n_clusters': n_clusters,
                  'points_data': points_data,
                  'clusters_data': clusters_data}
        project_clustering.metadata = result
        project_clustering.save()

        self.push()
        self.log_info('Clustering completed')

        return result


class ReassignProjectClusterDocuments(BaseTask):
    """
    Reassign Project Cluster Documents
    """
    name = 'Reassign Project Cluster Documents'

    def process(self, **kwargs):

        project_id = kwargs.get('project_id')
        cluster_ids = kwargs.get('cluster_ids')
        new_project_id = kwargs.get('new_project_id')
        new_project = Project.objects.get(pk=new_project_id)

        documents = Document.objects.filter(documentcluster__pk__in=cluster_ids)
        documents.update(project_id=new_project, document_type=new_project.type)

        task_model = self.task
        task_model.metadata = {
            'task_name': 'reassigning',
            'old_project_id': project_id,
            'new_project_id': new_project_id,
            'cluster_ids': cluster_ids,
        }
        task_model.save()

        reassigning = {
            'date': now().isoformat(),
            'new_project_id': new_project_id,
            'cluster_ids': cluster_ids,
            'task_id': task_model.main_task_id
        }
        p_cl = ProjectClustering.objects.get(document_clusters__pk=cluster_ids[0])
        reassignings = p_cl.metadata.get('reassigning', [])
        reassignings.append(reassigning)
        p_cl.metadata['reassigning'] = reassignings
        reassigned_cluster_ids = list(set(
            p_cl.metadata.get('reassigned_cluster_ids', []) + cluster_ids))
        p_cl.metadata['reassigned_cluster_ids'] = reassigned_cluster_ids

        # remove reassigned clusters from metadata
        p_cl.metadata['clusters_data'] = {i: j for i, j in p_cl.metadata['clusters_data'].items()
                                          if j['cluster_obj_id'] not in reassigned_cluster_ids}
        reassigned_document_ids = documents.values_list('pk', flat=True)
        p_cl.metadata['points_data'] = [i for i in p_cl.metadata['points_data']
                                        if int(i['document_id']) not in reassigned_document_ids]

        p_cl.save()
        # DocumentCluster.objects.filter(pk__in=cluster_ids).delete()

        task_funcs = []
        for app_name in custom_apps:
            module_str = 'apps.%s.tasks' % app_name
            module = sys.modules.get(module_str)
            detector_task = getattr(module, 'DetectFieldValues', None)
            if detector_task and hasattr(detector_task, 'detect_field_values_for_document'):
                task_funcs.append(getattr(detector_task, 'detect_field_values_for_document'))

        if task_funcs:
            sub_tasks = []
            for document in documents:
                for task_func in task_funcs:
                    sub_task = task_func.subtask(
                        args=(document.id, False, None))
                    sub_tasks.append(sub_task)
            self.chord(sub_tasks)

        # TODO: metadata[project_id] in tasks related with reassigned documents
        # TODO: should be updated to new project id value?


class CleanProject(BaseTask):
    """
    Cleanup Project - remove unassigned docs, sessions, clusters, etc.
    Only for "Multiple Contract Type"
    """
    name = 'Clean Project'

    def process(self, **kwargs):
        project_id = kwargs.get('project_id')
        project = Project.objects.get(pk=project_id)

        # delete project and related objects
        project.cleanup()

        # store data about cleanup in ProjectCleanup Task
        task_model = self.task
        task_model.metadata = {
            'task_name': 'clean-project',
            '_project_id': project_id  # added "_" to avoid detecting task as project task
        }
        task_model.save()


@app.task(name='advanced_celery.track_session_completed', bind=True)
def track_session_completed(*args, **kwargs):
    """
    Filter sessions where users were notified that upload job started
    i.e. a user set "send email notifications" flag,
    filter sessions where users were not notified that a session job is completed and
    check that upload job is completed,
    send notification email.
    """
    TaskUtils.prepare_task_execution()

    for session in UploadSession.objects.filter(
            notified_upload_started=True,
            notified_upload_completed=False):
        if session.is_completed():
            session.notify_upload_completed()


app.register_task(ClusterProjectDocuments())
app.register_task(ReassignProjectClusterDocuments())
app.register_task(CleanProject())
