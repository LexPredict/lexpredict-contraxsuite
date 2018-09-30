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

# Standard imports
import importlib

# Third-party imports
from filebrowser.sites import site as filebrowser_site

# Django imports
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views

# Project imports
from settings import REST_FRAMEWORK
from swagger_view import get_swagger_view
from apps.project.views import DashboardView
from apps.document.python_coded_fields import init_field_registry

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.4/LICENSE"
__version__ = "1.1.4"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# Manually add all standard patterns
urlpatterns = [
    # Base pages
    url(r'^{0}$'.format(settings.BASE_URL), DashboardView.as_view(), name='home'),
    url(r'^{0}'.format(settings.BASE_URL), include('django.contrib.auth.urls')),
    # url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^{0}about/$'.format(settings.BASE_URL), TemplateView.as_view(template_name='about.html'), name='about'),
    # Django Admin, use {% url 'admin:index' %}
    url(r'^{0}admin/'.format(settings.BASE_URL), admin.site.urls),
    # User management
    # url(r'^accounts/', include('apps.users.urls', namespace='users')),
    url(r'^{0}accounts/'.format(settings.BASE_URL), include('allauth_2fa.urls')),
    url(r'^{0}accounts/'.format(settings.BASE_URL), include('allauth.urls')),
    # Apps
    # url(r'^', include('apps.common.urls', namespace='common')),
    # url(r'^document/', include('apps.document.urls', namespace='document')),
    # url(r'^analyze/', include('apps.analyze.urls', namespace='analyze')),
    # url(r'^extract/', include('apps.extract.urls', namespace='extract')),
    # url(r'^project/', include('apps.project.urls', namespace='project')),
    # url(r'^task/', include('apps.task.urls', namespace='task')),
    # Custom
    url(r'^{0}admin/filebrowser/'.format(settings.BASE_URL), include(filebrowser_site.urls)),
    url(r'^{0}api-auth/'.format(settings.BASE_URL), include('rest_framework.urls')),
    url(r'^rest-auth/'.format(settings.BASE_URL), include('rest_auth.urls')),
    url(r'^rest-auth/registration/'.format(settings.BASE_URL), include('rest_auth.registration.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# autodiscover urls from custom apps
namespaces = {getattr(i, 'namespace', None) for i in urlpatterns}
custom_apps = [i.replace('apps.', '') for i in settings.INSTALLED_APPS if i.startswith('apps.')]

api_urlpatterns = {api_version: [] for api_version in REST_FRAMEWORK['ALLOWED_VERSIONS']}

for app_name in custom_apps:
    if app_name in namespaces:
        continue

    module_str = 'apps.%s.urls' % app_name
    spec = importlib.util.find_spec(module_str)
    if spec:
        include_urls = include(module_str, namespace=app_name)
        urlpatterns += [url(r'^' + settings.BASE_URL + app_name + '/', include_urls)]

    # add api urlpatterns
    for api_version in REST_FRAMEWORK['ALLOWED_VERSIONS']:
        api_module_str = 'apps.{}.api.{}'.format(app_name, api_version)
        try:
            api_module = importlib.import_module(api_module_str)
        except ImportError:
            continue
        if hasattr(api_module, 'router'):
            api_urlpatterns[api_version] += [
                url(r'{version}/{app_name}/'.format(
                    version=api_version,
                    app_name=app_name),
                    include(api_module.router.urls)),
            ]
        if hasattr(api_module, 'api_routers'):
            for router in api_module.api_routers:
                api_urlpatterns[api_version] += [
                    url(r'{version}/{app_name}/'.format(
                        version=api_version,
                        app_name=app_name),
                        include(router.urls)),
                ]
        if hasattr(api_module, 'urlpatterns'):
            api_urlpatterns[api_version] += [
                url(r'{version}/{app_name}/'.format(
                    version=api_version,
                    app_name=app_name),
                    include(api_module.urlpatterns)),
            ]
for api_version, this_api_urlpatterns in api_urlpatterns.items():
    urlpatterns += [
        url(r'^api/', include(this_api_urlpatterns, namespace=api_version)),
    ]


# django-rest-swagger urls
# patched original rest_framework_swagger.views.get_swagger_view
schema_view = get_swagger_view()
urlpatterns += [
    url(r'^api/(?:(?P<group_by>version|app)/)?$', schema_view, name='swagger')
]


# Manually add debug patterns
if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these urls in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^' + settings.BASE_URL + '400/$', default_views.bad_request,
            kwargs={'exception': Exception('Bad Request!')}),
        url(r'^' + settings.BASE_URL + '403/$', default_views.permission_denied,
            kwargs={'exception': Exception('Permission Denied')}),
        url(r'^' + settings.BASE_URL + '404/$', default_views.page_not_found,
            kwargs={'exception': Exception('Page not Found')}),
        url(r'^' + settings.BASE_URL + '500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [
            url(r'^' + settings.BASE_URL + '__debug__/', include(debug_toolbar.urls)),
        ]


init_field_registry()
