# -*- coding: utf-8 -*-

# Future imports
from __future__ import absolute_import, unicode_literals

# Django imports
from django.conf.urls import url

# Project imports
from apps.common.utils import create_standard_urls
from apps.analyze import views
from apps.analyze.models import (
    DocumentCluster, DocumentSimilarity, PartySimilarity,
    TextUnitClassification, TextUnitClassifier, TextUnitClassifierSuggestion,
    TextUnitSimilarity, TextUnitCluster)

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.1/LICENSE"
__version__ = "1.0.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


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
register(DocumentCluster, view_types=('list',))
register(DocumentSimilarity, view_types=('list',))
register(TextUnitSimilarity, view_types=('list',))
register(PartySimilarity, view_types=('list',))
register(TextUnitCluster, view_types=('list',))
register(TextUnitClassifier, view_types=('list', 'delete'))
register(TextUnitClassification, view_types=('list', 'delete'))
register(TextUnitClassifierSuggestion, view_types=('list', 'delete'))

# Add hard-coded URL mappings
urlpatterns += [
    url(
        r'^complete/text-unit-classification/name/$',
        views.TypeaheadTextUnitClassName.as_view(),
        name='text-unit-classification-name-complete',
    ),
    url(
        r'^complete/text-unit-classification/value/$',
        views.TypeaheadTextUnitClassValue.as_view(),
        name='text-unit-classification-value-complete',
    ),
    url(
        r'^submit/text-unit-classification/$',
        views.SubmitTextUnitClassificationView.as_view(),
        name='text-unit-classification-submit',
    ),
]
