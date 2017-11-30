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
from apps.extract import views
from apps.extract.models import (
    AmountUsage, CitationUsage, CopyrightUsage, CourtUsage, CurrencyUsage,
    DateDurationUsage, DateUsage, DefinitionUsage, DistanceUsage, GeoEntityUsage,
    PartyUsage, PercentUsage, RatioUsage, RegulationUsage, TermUsage, TrademarkUsage,
    UrlUsage)

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.4/LICENSE"
__version__ = "1.0.4"
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


# Register urls through helper method
register(AmountUsage, view_types=('list', 'top_list'))
register(CitationUsage, view_types=('list', 'top_list'))
register(CopyrightUsage, view_types=('list', 'top_list'))
register(CourtUsage, view_types=('list', 'top_list'))
register(CurrencyUsage, view_types=('list', 'top_list'))
register(DateUsage, view_types=('list', 'top_list'))
register(DateDurationUsage, view_types=('list', 'top_list'))
register(DefinitionUsage, view_types=('list', 'top_list'))
register(DistanceUsage, view_types=('list', 'top_list'))
register(GeoEntityUsage, view_types=('list', 'top_list'))
register(PartyUsage, view_types=('list', 'top_list'))
register(PercentUsage, view_types=('list', 'top_list'))
register(RatioUsage, view_types=('list', 'top_list'))
register(RegulationUsage, view_types=('list', 'top_list'))
register(TermUsage, view_types=('list', 'top_list'))
register(TrademarkUsage, view_types=('list', 'top_list'))
register(UrlUsage, view_types=('list', 'top_list'))

# Add hard-coded URL mappings
urlpatterns += [
    url(
        r'^geo-entity-usage-map/$',
        views.GeoEntityUsageGoogleMapView.as_view(),
        name='geo-entity-usage-map',
    ),
    url(
        r'^geo-entity-usage-chart/(?P<entity_type>[\w_]+)/$',
        views.GeoEntityUsageGoogleChartView.as_view(),
        name='geo-entity-usage-chart',
    ),
    url(
        r'^party-network-chart/$',
        views.PartyNetworkChartView.as_view(),
        name='party-network-chart',
    ),
    url(
        r'^date-usage-timeline/$',
        views.DateUsageTimelineView.as_view(),
        name='date-usage-timeline',
    ),
    url(
        r'^date-usage-calendar/$',
        views.DateUsageCalendarView.as_view(),
        name='date-usage-calendar',
    ),
    url(
        r'^date-usage-export-ical/$',
        views.DateUsageToICalView.as_view(),
        name='date-usage-export-ical',
    ),
    url(
        r'^party/(?P<pk>\d+)/summary/$',
        views.PartySummary.as_view(),
        name='party-summary'
    ),

    url(
        r'^complete/term/term/$',
        views.TypeaheadTermTerm.as_view(),
        name='term-name-complete',
    ),
    url(
        r'^complete/geo-entity/name/$',
        views.TypeaheadGeoEntityName.as_view(),
        name='geo-entity-name-complete',
    ),
    url(
        r'^complete/party/name/$',
        views.TypeaheadPartyName.as_view(),
        name='party-name-complete',
    ),

    url(
        r'^search/term/$',
        views.TermSearchView.as_view(),
        name='search-term',
    ),
]
