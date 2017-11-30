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
from __future__ import unicode_literals

# Django imports
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
from filebrowser.sites import site as filebrowser_site

# Project imports
from apps.project.views import DashboardView

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.4/LICENSE"
__version__ = "1.0.4"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# Manually add all standard patterns
urlpatterns = [
                  # Base pages
                  url(r'^$', DashboardView.as_view(), name='home'),
                  url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
                  url(r'^about/$', TemplateView.as_view(template_name='about.html'), name='about'),
                  # Django Admin, use {% url 'admin:index' %}
                  url(r'^admin/', admin.site.urls),
                  # User management
                  url(r'^accounts/', include('apps.users.urls', namespace='users')),
                  url(r'^accounts/', include('allauth_2fa.urls')),
                  url(r'^accounts/', include('allauth.urls')),
                  # Apps
                  url(r'^', include('apps.common.urls', namespace='common')),
                  url(r'^document/', include('apps.document.urls', namespace='document')),
                  url(r'^analyze/', include('apps.analyze.urls', namespace='analyze')),
                  url(r'^extract/', include('apps.extract.urls', namespace='extract')),
                  url(r'^project/', include('apps.project.urls', namespace='project')),
                  url(r'^task/', include('apps.task.urls', namespace='task')),
                  # Custom
                  url(r'^admin/filebrowser/', include(filebrowser_site.urls)),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Manually add debug patterns
if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request,
            kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied,
            kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found,
            kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]
