# -*- coding: utf-8 -*-

# Future imports
from __future__ import absolute_import, unicode_literals

# Django imports
from django.conf.urls import url

# Project imports
from . import views

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0/LICENSE.pdf"
__version__ = "1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@lexpredict.com"


# Add hard-coded URL mappings
urlpatterns = [
    url(
        r'^task/list/$',
        views.TaskListView.as_view(),
        name='task-list',
    ),
    url(
        r'^task/(?P<pk>\d+)/detail/$',
        views.TaskDetailView.as_view(),
        name='task-detail',
    ),

    url(
        r'^load-documents/$',
        views.LoadDocumentsView.as_view(),
        name='load-documents',
    ),
    url(
        r'^load-terms/$',
        views.LoadTermsView.as_view(),
        name='load-terms',
    ),
    url(
        r'^load-geo-entities/$',
        views.LoadGeoEntitiesView.as_view(),
        name='load-geo-entities',
    ),
    url(
        r'^load-courts/$',
        views.LoadCourtsView.as_view(),
        name='load-courts',
    ),

    url(
        r'^locate-terms/$',
        views.LocateTermsView.as_view(),
        name='locate-terms',
    ),
    url(
        r'^locate-geo-entities/$',
        views.LocateGeoEntitiesView.as_view(),
        name='locate-geo-entities',
    ),
    url(
        r'^locate-parties/$',
        views.LocatePartiesView.as_view(),
        name='locate-parties',
    ),
    url(
        r'^locate-dates/$',
        views.LocateDatesView.as_view(),
        name='locate-dates',
    ),
    url(
        r'^locate-date-durations/$',
        views.LocateDateDurationsView.as_view(),
        name='locate-date-durations',
    ),
    url(
        r'^locate-definitions/$',
        views.LocateDefinitionsView.as_view(),
        name='locate-definitions',
    ),
    url(
        r'^locate-courts/$',
        views.LocateCourtsView.as_view(),
        name='locate-courts',
    ),
    url(
        r'^locate-currencies/$',
        views.LocateCurrenciesView.as_view(),
        name='locate-currencies',
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
        r'^similarity/$',
        views.SimilarityView.as_view(),
        name='similarity',
    ),
    url(
        r'^party-similarity/$',
        views.PartySimilarityView.as_view(),
        name='party-similarity',
    ),
]
