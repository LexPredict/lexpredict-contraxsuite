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
    DefinitionUsage, GeoEntityUsage, LegalTermUsage, PartyUsage)

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
register(LegalTermUsage, view_types=('list',))
register(GeoEntityUsage, view_types=('list',))
register(PartyUsage, view_types=('list',))
register(DateUsage, view_types=('list',))
register(DateDurationUsage, view_types=('list',))
register(DefinitionUsage, view_types=('list',))
register(CourtUsage, view_types=('list',))
register(CurrencyUsage, view_types=('list',))

# Add hard-coded URL mappings
urlpatterns += [
    url(
        r'^top-term-usage/list/$',
        views.TopLegalTermUsageListView.as_view(),
        name='top-legal-term-usage-list',
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
        r'^complete/legal-term/term/$',
        views.TypeaheadLegalTermTerm.as_view(),
        name='legal-term-name-complete',
    ),
    url(
        r'^complete/geo-entity/name/$',
        views.TypeaheadGeoEntityName.as_view(),
        name='geo-entity-name-complete',
    ),
]
