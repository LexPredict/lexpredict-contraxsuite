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
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import Birch, DBSCAN, KMeans, MiniBatchKMeans
from sklearn.decomposition import PCA

# Django imports
from django.utils.timezone import now

# Project imports
from apps.analyze.models import DocumentCluster
from apps.celery import app
from apps.common.utils import fast_uuid
from apps.document.models import Document
from apps.project.models import Project, ProjectClustering
from apps.task.models import Task
from apps.task.tasks import BaseTask
from urls import custom_apps


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.5/LICENSE"
__version__ = "1.0.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


THIS_MODULE = __name__


class ClusterProjectDocuments(BaseTask):
    """
    Cluster Project Documents
    """
    name = 'Cluster Project Documents'

    def process(self, **kwargs):

        n_clusters = kwargs.get('n_clusters')
        method = kwargs.get('method')
        project_id = kwargs.get('project_id')

        project_clustering_id = kwargs.get('project_clustering_id')
        project_clustering = ProjectClustering.objects.get(pk=project_clustering_id) if project_id else None
        project_clustering.task = self.task
        project_clustering.save()

        project = project_clustering.project

        self.log('Start clustering documents for project id={}'.format(project_id))
        self.log('Clustering method: "{}", n_clusters={}'.format(method, n_clusters))

        self.task.subtasks_total = 3
        self.task.save()

        # get documents data
        documents = Document.objects.filter(project_id=project_id)
        docs = np.array(documents.values_list('pk', 'name', 'full_text'))
        pks, names, data = docs[:, 0], docs[:, 1], docs[:, 2]
        docs_count = len(docs)

        vectorizer = TfidfVectorizer(max_df=0.5, max_features=100,
                                     min_df=2, stop_words='english',
                                     use_idf=True)
        X = vectorizer.fit_transform(data)
        terms = vectorizer.get_feature_names()

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
        # elif method == 'KMeans':
        else:
            method = 'KMeans'
            m = KMeans(
                n_clusters=n_clusters,
                init='k-means++',
                max_iter=100,
                n_init=1,
                verbose=False)
        # else:
        #     m = DBSCAN(
        #         eps=0.5,
        #         min_samples=5,
        #         leaf_size=30)
        m.fit(X)

        self.task.push()

        XX = X.toarray()
        pca = PCA(n_components=2).fit(XX)
        data2d = pca.transform(XX)

        if method == 'DBSCAN':
            clusters = m.labels_
            cluster_labels = set(clusters)
            # reshape cluster labels
            if -1 in cluster_labels:
                cluster_labels = [i+1 for i in cluster_labels]
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
            cluster_terms = [[terms[ind] for ind in order_centroids[i, :10]] for i in
                             range(n_clusters)]
            centers2d = pca.transform(cluster_centers)

        points_data = [{'document_id': pks[i],
                        'document_name': names[i],
                        'coord': data2d[i].tolist(),
                        'cluster_id': str(clusters[i])} for i in range(docs_count)]

        self.task.push()

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
                description='Cluster Project (id={}) with Multiple Contract Types'.format(project_id),
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

        self.task.push()
        self.log('Clustering completed')

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

        self.task.metadata = {
            'task_name': 'reassigning',
            'old_project_id': project_id,
            'new_project_id': new_project_id,
            'cluster_ids': cluster_ids,
        }
        self.task.save()

        reassigning = {
            'date': now().isoformat(),
            'new_project_id': new_project_id,
            'cluster_ids': cluster_ids,
            'task_id': self.task.id
        }
        p_cl = ProjectClustering.objects.get(document_clusters__pk=cluster_ids[0])
        reassignings = p_cl.metadata.get('reassigning', [])
        reassignings.append(reassigning)
        p_cl.metadata['reassigning'] = reassignings
        reassigned_cluster_ids = list(set(
            p_cl.metadata.get('reassigned_cluster_ids', []) + cluster_ids))
        p_cl.metadata['reassigned_cluster_ids'] = reassigned_cluster_ids
        p_cl.save()

        tasks = []
        for app_name in custom_apps:
            module_str = 'apps.%s.tasks' % app_name
            module = sys.modules.get(module_str)
            detector_task = getattr(module, 'DetectFieldValues', None)
            if detector_task and hasattr(detector_task, 'detect_field_values_for_document'):
                tasks.append(getattr(detector_task, 'detect_field_values_for_document'))

        if tasks:
            self.task.subtasks_total = documents.count() * len(tasks)
            self.task.save()

            for document in documents:
                for task in tasks:
                    task.apply_async(
                        args=(document.id, False, self.task.id, None),
                        task_id='%d_%s' % (self.task.id, fast_uuid()))


class CleanProject(BaseTask):
    """
    Cleanup Project - remove unassigned docs, sessions, clusters, etc.
    Only for "Multiple Contract Type"
    """
    name = 'Clean Project'

    def process(self, **kwargs):
        project_id = kwargs.get('project_id')
        project = Project.objects.get(pk=project_id)

        # delete prev. CleanProject Task
        Task.special_tasks({'task_name': 'clean-project',
                            '_project_id': project.pk}).delete()
        # delete prev. Reassigning Task
        Task.special_tasks({'task_name': 'reassigning',
                            'old_project_id': project.pk}).delete()

        self.task.subtasks_total = 1
        self.task.metadata = {
            'task_name': 'clean-project',
            '_project_id': project_id    # added "_" to avoid detecting task as project task
        }
        self.task.save()

        # delete DocumentClusters
        for pcl in project.projectclustering_set.all():
            pcl.document_clusters.all().delete()
        # delete ProjectClustering
        project.projectclustering_set.all().delete()
        # delete Documents
        project.document_set.all().delete()
        # delete Project Tasks
        project.project_tasks.delete()
        # delete UploadSession Tasks
        for ups in project.uploadsession_set.all():
            ups.document_set.update(upload_session=None)
            ups.session_tasks.delete()

        # delete UploadSessions
        project.uploadsession_set.all().delete()

        self.task.push()


app.register_task(ClusterProjectDocuments())
app.register_task(ReassignProjectClusterDocuments())
app.register_task(CleanProject())
