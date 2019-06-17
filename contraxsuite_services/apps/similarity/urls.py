"""
    Copyright (C) 2017, ContraxSuite, LLC
"""
# -*- coding: utf-8 -*-

# Future imports
from __future__ import absolute_import, unicode_literals

# Django imports
from django.conf.urls import url

# Project imports
from . import views

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__version__ = "1.2.2"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

# URL pattern list
urlpatterns = []

# Add hard-coded URL mappings
urlpatterns += [
    url(
        r'^preconfigured-document-similarity-search/$',
        views.PreconfiguredDocumentSimilaritySearchView.as_view(),
        name='preconfigured-document-similarity-search',
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
