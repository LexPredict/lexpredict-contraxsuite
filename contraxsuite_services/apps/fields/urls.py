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
from apps.common.utils import create_standard_urls
from apps.fields import views

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.5/LICENSE"
__version__ = "1.0.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

# URL pattern list
urlpatterns = []


def register(model, view_types):
    global urlpatterns
    urlpatterns += create_standard_urls(model, views, view_types)


urlpatterns += [
    url(
        r'^annotations/search$',
        views.DocumentAnnotationStorageSearchView.as_view(),
        name='annotations_search'
    ),

    url(
        r'^annotations(/annotations(/(?P<id>\d+))?)?$',
        views.DocumentAnnotationStorageView.as_view(),
        name='annotations'
    ),
    url(
        r'^field-editor/(?P<document_class>[^/]+)/(?P<document_id>\d+)$',
        views.FieldEditorBackendView.as_view(),
        name='field-editor'
    ),
    url(
        r'^fields-catalog/(?P<document_class>[^/]+)$',
        views.DocumentFieldsView.as_view(),
        name='fields-catalog'
    ),

    url(
        r'^build-field-detector-dataset/$',
        views.BuildFieldDetectorDatasetTaskView.as_view(),
        name='build-field-detector-dataset',
    ),

    url(
        r'^train-field-detector-model/$',
        views.TrainFieldDetectorModelTaskView.as_view(),
        name='train-field-detector-model',
    )
]
