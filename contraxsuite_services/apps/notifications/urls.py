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

from django.conf.urls import url

from apps.notifications.views import SendDigestTaskView, RenderDigestView, DigestImageView, \
    NotificationImageView, RenderNotificationView

# URL pattern list

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


urlpatterns = []

urlpatterns += [

    url(
        r'^send-digest/$',
        SendDigestTaskView.as_view(),
        name='send-digest',
    ),
    url(
        r'^digest_configs/(?P<config_id>\d+)/render.(?P<content_format>\w+)$',
        RenderDigestView.as_view(),
        name='render-digest',
    ),
    url(
        r'^digest_configs/(?P<config_id>\d+)/images/(?P<image_fn>.+)$',
        DigestImageView.as_view(),
        name='digest-image',
    ),
    url(
        r'^notification_subscriptions/(?P<subscription_id>\d+)/render.(?P<content_format>\w+)$',
        RenderNotificationView.as_view(),
        name='render-notification',
    ),
    url(
        r'^notification_subscriptions/(?P<subscription_id>\d+)/images/(?P<image_fn>.+)$',
        NotificationImageView.as_view(),
        name='notification-image',
    ),
]
