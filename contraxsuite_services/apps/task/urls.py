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

# Future imports
from __future__ import absolute_import, unicode_literals

# Django imports
from sys import path

from django.conf.urls import url

# Project imports
from apps.task import views, api

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.2/LICENSE"
__version__ = "1.2.2"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# Add hard-coded URL mappings
urlpatterns = [
    url(
        r'^task/list/$',
        views.TaskListView.as_view(),
        name='task-list',
    ),
    url(
        r'^task/(?P<pk>[^/]+)/detail/$',
        views.TaskDetailView.as_view(),
        name='task-detail',
    ),

    url(
        r'^load/$',
        views.LoadTaskView.as_view(),
        name='load',
    ),
    url(
        r'^load-documents/$',
        views.LoadDocumentsView.as_view(),
        name='load-documents',
    ),
    url(
        r'^locate/$',
        views.LocateTaskView.as_view(),
        name='locate',
    ),
    url(
        r'^locate-terms/$',
        views.LocateTermsView.as_view(),
        name='locate-terms',
    ),
    url(
        r'^existed-classifier-classify/$',
        views.ExistedClassifierClassifyView.as_view(),
        name='existed-classifier-classify',
    ),
    url(
        r'^create-classifier-classify/$',
        views.CreateClassifierClassifyView.as_view(),
        name='create-classifier-classify',
    ),
    url(
        r'^update-elasticsearch-index/$',
        views.UpdateElasticsearchIndexView.as_view(),
        name='update-elasticsearch-index',
    ),
    url(
        r'^total-cleanup/$',
        views.TotalCleanupView.as_view(),
        name='total-cleanup',
    ),

    url(
        r'^clean-tasks/$',
        views.CleanTasksView.as_view(),
        name='clean-tasks',
    ),
    url(
        r'^purge-task/$',
        views.PurgeTaskView.as_view(),
        name='purge-task',
    ),

    url(
        r'^cluster/$',
        views.ClusterView.as_view(),
        name='cluster',
    ),
    url(
        r'^clean-project/$',
        views.CleanProjectView.as_view(),
        name='clean-project',
    ),
    url(
        r'^load-fixtures/$',
        views.LoadFixturesView.as_view(),
        name='load-fixtures',
    ),
    url(
        r'^dump-fixtures/$',
        views.DumpFixturesView.as_view(),
        name='dump-fixtures',
    ),

]
