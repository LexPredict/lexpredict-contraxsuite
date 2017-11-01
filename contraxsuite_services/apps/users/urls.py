# -*- coding: utf-8 -*-

# Future imports
from __future__ import absolute_import, unicode_literals

# Django imports
from django.conf.urls import url

# Project imports
from . import views

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.3/LICENSE"
__version__ = "1.0.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# Manually add hard-coded URLs
urlpatterns = [
    url(
        r'^~redirect/$',
        views.UserRedirectView.as_view(),
        name='redirect'
    ),
    url(
        r'^user/list/$',
        views.UserListView.as_view(),
        name='user-list'
    ),
    url(
        r'^user/(?P<username>[\w.@+-]+)/detail/$',
        views.UserDetailView.as_view(),
        name='user-detail'
    ),
    url(
        r'^user/(?P<username>[\w.@+-]+)/update/$',
        views.UserUpdateView.as_view(),
        name='user-update'
    ),
]
