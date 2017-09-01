# -*- coding: utf-8 -*-

# Future imports
from __future__ import absolute_import, unicode_literals

# Django imports
from django.conf.urls import url

# Project imports
from apps.common.utils import create_standard_urls
from apps.document import views
from apps.document.models import (
    Document, DocumentProperty, DocumentRelation, DocumentNote, DocumentTag,
    TextUnit, TextUnitProperty, TextUnitNote, TextUnitTag)

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
register(Document, view_types=('list', 'detail'))
register(DocumentProperty, view_types=('list', 'update', 'delete'))
register(DocumentRelation, view_types=('list',))
register(DocumentTag, view_types=('list', 'delete'))
register(TextUnit, view_types=('list', 'detail'))
register(TextUnitProperty, view_types=('list', 'delete'))
register(TextUnitNote, view_types=('list', 'delete'))
register(DocumentNote, view_types=('list', 'delete'))
register(TextUnitTag, view_types=('list', 'delete'))

# Add hard-coded URL mappings
urlpatterns += [
    url(
        r'^search/$',
        views.search,
        name='search'
    ),
    url(
        r'^stats/$',
        views.view_stats,
        name='stats'
    ),
    url(
        r'^document-property/(?:(?P<pk>\d+)/)?add/$',
        views.DocumentPropertyCreateView.as_view(),
        name='document-property-add'
    ),
    url(
        r'^document/(?P<pk>\d+)/source/$',
        views.DocumentSourceView.as_view(),
        name='document-source'
    ),
    url(
        r'^document/(?P<pk>\d+)/enhanced-view/$',
        views.DocumentEnhancedView.as_view(),
        name='document-enhanced-view'
    ),
    url(
        r'^document/sentiment-chart/$',
        views.DocumentSentimentChartView.as_view(),
        name='document-sentiment-chart'
    ),

    url(
        r'^complete/document/description/$',
        views.TypeaheadDocumentDescription.as_view(),
        name='document-description-complete',
    ),
    url(
        r'^complete/document/name/$',
        views.TypeaheadDocumentName.as_view(),
        name='document-name-complete',
    ),
    url(
        r'^complete/document-property/key/$',
        views.TypeaheadDocumentPropertyKey.as_view(),
        name='document-property-key-complete',
    ),
    url(
        r'^complete/text-unit-tag/tag/$',
        views.TypeaheadTextUnitTag.as_view(),
        name='text-unit-tag-complete',
    ),

    url(
        r'^submit/document-tag/$',
        views.SubmitDocumentTagView.as_view(),
        name='document-tag-submit',
    ),
    url(
        r'^submit/text-unit-tag/$',
        views.SubmitTextUnitTagView.as_view(),
        name='text-unit-tag-submit',
    ),
    url(
        r'^submit/document-property/$',
        views.SubmitDocumentPropertyView.as_view(),
        name='document-property-submit',
    ),
    url(
        r'^submit/text-unit-property/$',
        views.SubmitTextUnitPropertyView.as_view(),
        name='text-unit-property-submit',
    ),
    url(
        r'^submit/note/$',
        views.SubmitNoteView.as_view(),
        name='note-submit',
    ),
]
