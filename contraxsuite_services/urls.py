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
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0/LICENSE.pdf"
__version__ = "1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@lexpredict.com"


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
                  url(r'^accounts/', include('allauth.urls')),
                  # Apps
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
