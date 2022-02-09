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
from django.conf.urls import url

# Project imports
from apps.similarity import views
from apps.similarity import signals    # noqa: need to activate signal handlers otherwise they are invisible for proj

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
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
        r'^document-similarity-by-features/$',
        views.DocumentSimilarityByFeaturesView.as_view(),
        name='document_similarity_by_features',
    ),
    url(
        r'^text-unit-similarity-by-features/$',
        views.TextUnitSimilarityByFeaturesView.as_view(),
        name='text_unit_similarity_by_features',
    ),
    url(
        r'^project-documents-similarity-by-vectors/$',
        views.ProjectDocumentsSimilarityByVectorsView.as_view(),
        name='project_documents_similarity_by_vectors',
    ),
    url(
        r'^project-text-units-similarity-by-vectors/$',
        views.ProjectTextUnitsSimilarityByVectorsView.as_view(),
        name='project_text_units_similarity_by_vectors',
    ),
    url(
        r'^chunk_similarity/$',
        views.ChunkSimilarityView.as_view(),
        name='chunk_similarity',
    ),
    url(
        r'^party-similarity/$',
        views.PartySimilarityView.as_view(),
        name='party-similarity',
    ),
]
