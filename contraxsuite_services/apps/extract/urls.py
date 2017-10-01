# -*- coding: utf-8 -*-

# Future imports
from __future__ import absolute_import, unicode_literals

# Django imports
from django.conf.urls import url

# Project imports
from apps.common.utils import create_standard_urls
from apps.extract import views
from apps.extract.models import (
    CourtUsage, CurrencyUsage, DateDurationUsage, DateUsage,
    AmountUsage, DistanceUsage, PercentUsage, RatioUsage, CitationUsage,
    DefinitionUsage, GeoEntityUsage, TermUsage, PartyUsage, RegulationUsage)

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
register(TermUsage, view_types=('list',))
register(GeoEntityUsage, view_types=('list',))
register(PartyUsage, view_types=('list',))
register(AmountUsage, view_types=('list',))
register(CitationUsage, view_types=('list',))
register(DateUsage, view_types=('list',))
register(DateDurationUsage, view_types=('list',))
register(DefinitionUsage, view_types=('list',))
register(DistanceUsage, view_types=('list',))
register(PercentUsage, view_types=('list',))
register(RatioUsage, view_types=('list',))
register(RegulationUsage, view_types=('list',))
register(CourtUsage, view_types=('list',))
register(CurrencyUsage, view_types=('list',))

# Add hard-coded URL mappings
urlpatterns += [
    url(
        r'^top-term-usage/list/$',
        views.TopTermUsageListView.as_view(),
        name='top-term-usage-list',
    ),
    url(
        r'^top-geo-entity-usage/list/$',
        views.TopGeoEntityUsageListView.as_view(),
        name='top-geo-entity-usage-list',
    ),
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
        r'^top-party-usage/list/$',
        views.TopPartyUsageListView.as_view(),
        name='top-party-usage-list',
    ),
    url(
        r'^party-network-chart/$',
        views.PartyNetworkChartView.as_view(),
        name='party-network-chart',
    ),
    url(
        r'^top-date-usage/list/$',
        views.TopDateUsageListView.as_view(),
        name='top-date-usage-list',
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
        r'^top-date-duration-usage/list/$',
        views.TopDateDurationUsageListView.as_view(),
        name='top-date-duration-usage-list',
    ),
    url(
        r'^top-definition-usage/list/$',
        views.TopDefinitionUsageListView.as_view(),
        name='top-definition-usage-list',
    ),
    url(
        r'^top-amount-usage/list/$',
        views.TopAmountUsageListView.as_view(),
        name='top-amount-usage-list',
    ),
    url(
        r'^top-citation-usage/list/$',
        views.TopCitationUsageListView.as_view(),
        name='top-citation-usage-list',
    ),
    url(
        r'^top-distance-usage/list/$',
        views.TopDistanceUsageListView.as_view(),
        name='top-distance-usage-list',
    ),
    url(
        r'^top-percent-usage/list/$',
        views.TopPercentUsageListView.as_view(),
        name='top-percent-usage-list',
    ),
    url(
        r'^top-ratio-usage/list/$',
        views.TopRatioUsageListView.as_view(),
        name='top-ratio-usage-list',
    ),
    url(
        r'^top-regulation-usage/list/$',
        views.TopRegulationUsageListView.as_view(),
        name='top-regulation-usage-list',
    ),
    url(
        r'^top-court-usage/list/$',
        views.TopCourtUsageListView.as_view(),
        name='top-court-usage-list',
    ),
    url(
        r'^top-currency-usage/list/$',
        views.TopCurrencyUsageListView.as_view(),
        name='top-currency-usage-list',
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
]
