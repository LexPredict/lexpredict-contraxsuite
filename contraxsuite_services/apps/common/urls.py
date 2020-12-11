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
from apps.common import views

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


urlpatterns = [
    url(
        r'^method-stats-overview/$',
        views.MethodStatsOverviewListView.as_view(),
        name='method-stats-overview',
    ),
    url(
        r'^db-stats-overview/$',
        views.DBStatsView.as_view(),
        name='db-stats',
    ),
    url(
        r'^docker-stats-overview/$',
        views.DockerStatsView.as_view(),
        name='docker-stats',
    ),
    url(
        r'^redis-stats/$',
        views.RedisStatsView.as_view(),
        name='redis-stats',
    ),
    url(
        r'^500/$',
        views.test_500_view,
        name='test-500'
    ),
    url(
        r'^reindex-db/$',
        views.ReindexDBView.as_view(),
        name='reindex-db',
    ),
]
