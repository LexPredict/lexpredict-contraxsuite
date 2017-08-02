# -*- coding: utf-8 -*-

# Future imports
from __future__ import absolute_import, unicode_literals

# Django imports
from django.conf.urls import url

# Project imports
from apps.common.utils import create_standard_urls
from apps.project import views
from apps.project.models import Project, TaskQueue

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0/LICENSE.pdf"
__version__ = "1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@lexpredict.com"


# URL pattern list
urlpatterns = []


def register(model, view_types):
    """
    Convenience method for global URL registration.
    :param model:
    :param view_types:
    :return:
    """
    global urlpatterns
    urlpatterns += create_standard_urls(model, views, view_types)

# Register views through helper method
register(Project, view_types=('list', 'add', 'update'))
register(TaskQueue, view_types=('list', 'add', 'update'))

# Add hard-coded URL mappings
urlpatterns += [
    url(
        r'^dashboard/$',
        views.DashboardView.as_view(),
        name='dashboard'
    ),
    url(
        r'^task-queue/(?:(?P<task_queue_pk>\d+)/)?add/(?:(?P<document_pk>\d+)/)$',
        views.add_to_task_queue,
        name='add-to-task-queue'
    ),
    url(
        r'^task-queue/(?:(?P<task_queue_pk>\d+)/)?mark-completed/(?:(?P<document_pk>\d+)/)$',
        views.mark_document_completed,
        name='mark-document-completed'
    ),
    url(
        r'^assign-cluster-documents/$',
        views.TaskQueueAddClusterDocuments.as_view(),
        name='assign-cluster-documents'
    ),
]
