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
from sys import exc_info
import importlib
import re

# Third-party imports
from allauth.account.views import confirm_email as allauth_confirm_email_view

# Django imports
from django.conf import settings
from django.conf.urls import url
from django.urls import include, path
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.views.generic import TemplateView
from django.views import defaults as default_views
from django.views.static import serve
from django.urls import re_path

# Project imports
from apps.common.debug_utils import listen
from apps.common.decorators import init_decorators
from apps.common.file_storage import get_filebrowser_site
from apps.common.utils import migrating, get_api_module
from apps.common.log_utils import ProcessLogger
from apps.document.field_type_registry import init_field_type_registry
from apps.users.views import MixedLoginView
from swagger_view import get_swagger_view, get_openapi_view

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


listen()

process_logger = ProcessLogger()


def static(prefix, view=serve, **kwargs):
    """
    Unlike Django "static", this method serves static files even in production
    (DEBUG=False) mode.
    """
    if not prefix:
        raise ImproperlyConfigured("Empty static prefix not permitted")
    return [
        re_path(r'^%s(?P<path>.*)$' % re.escape(prefix.lstrip('/')), view, kwargs=kwargs),
    ]


# Manually add all standard patterns
urlpatterns = [
    # Base pages
    url(r'^{0}$'.format(settings.BASE_URL), TemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^{0}'.format(settings.BASE_URL), include('django.contrib.auth.urls')),
    url(r'^{0}about/$'.format(settings.BASE_URL), TemplateView.as_view(template_name='about.html'), name='about'),
    # Django Admin, use {% url 'admin:index' %}
    url(r'^{0}admin/'.format(settings.BASE_URL), admin.site.urls),
    # User management
    # url(r'^accounts/', include('apps.users.urls', namespace='users')),
    url(rf'^{settings.BASE_URL}accounts/login/', MixedLoginView.as_view(), name='account_login'),
    url(r'^{0}accounts/'.format(settings.BASE_URL), include('allauth_2fa.urls')),
    url(r'^{0}accounts/'.format(settings.BASE_URL), include('allauth.urls')),
    path('', TemplateView.as_view(template_name="social_app/index.html")),

    # Apps
    # url(r'^', include('apps.common.urls', namespace='common')),
    # url(r'^document/', include('apps.document.urls', namespace='document')),
    # url(r'^analyze/', include('apps.analyze.urls', namespace='analyze')),
    # url(r'^extract/', include('apps.extract.urls', namespace='extract')),
    # url(r'^project/', include('apps.project.urls', namespace='project')),
    # url(r'^task/', include('apps.task.urls', namespace='task')),
    # Custom
    url(r'^{0}admin/filebrowser/'.format(settings.BASE_URL), get_filebrowser_site().urls),
    url(r'^{0}api-auth/'.format(settings.BASE_URL), include('rest_framework.urls')),

    # url(r'^rest-auth/', include('rest_auth.urls')),
    # use patched urls definitions including view schemas
    url(r'^rest-auth/', include('apps.users.rest_auth_urls')),

    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r"^accounts/confirm-email/(?P<key>[-:\w]+)/$", allauth_confirm_email_view, name="allauth_account_confirm_email")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + \
    static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# autodiscover urls from custom apps
namespaces = {getattr(i, 'namespace', None) for i in urlpatterns}
custom_apps = [(i, i.replace(f'{settings.APPS_DIR_NAME}.', '')) for i in settings.PROJECT_APPS]

api_urlpatterns = {api_version: [] for api_version in settings.REST_FRAMEWORK['ALLOWED_VERSIONS']}

for app_loc, app_name in custom_apps:
    if app_name in namespaces:
        continue

    module_str = f'{app_loc}.urls'
    spec = importlib.util.find_spec(module_str)
    if spec:
        include_urls = include((module_str, app_name))  # namespace=app_name)
        urlpatterns += [url(r'^' + settings.BASE_URL + app_name + '/', include_urls)]

    # add api urlpatterns
    for api_version in settings.REST_FRAMEWORK['ALLOWED_VERSIONS']:
        try:
            api_module_str = f'{app_loc}.api.{api_version}.api'
            api_module = importlib.import_module(api_module_str)
        except ImportError:
            try:
                api_module_str = f'{app_loc}.api.{api_version}'
                api_module = importlib.import_module(api_module_str)
            except ImportError as import_error:
                exc_type, _, _ = exc_info()
                if exc_type == ModuleNotFoundError:
                    if '.api' in api_module_str:
                        continue
                process_logger.error(str(import_error))
                continue

        if hasattr(api_module, 'router'):
            api_urlpatterns[api_version] += [
                url(rf'{api_version}/{app_name}/', include(api_module.router.urls)),
            ]
        if hasattr(api_module, 'api_routers'):
            for router in api_module.api_routers:
                api_urlpatterns[api_version] += [
                    url(rf'{api_version}/{app_name}/', include(router.urls)),
                ]
        if hasattr(api_module, 'urlpatterns'):
            api_urlpatterns[api_version] += [
                url(rf'{api_version}/{app_name}/', include(api_module.urlpatterns)),
            ]
for api_version, this_api_urlpatterns in api_urlpatterns.items():
    urlpatterns += [
        url(r'^api/', include((this_api_urlpatterns, api_version))),
    ]


# django-rest-swagger urls
# patched original rest_framework_swagger.views.get_swagger_view
schema_view = get_swagger_view()
urlpatterns += [
    url(r'^api/(?:(?P<group_by>version|app)/)?$', schema_view, name='swagger')
]

# openapi urls
urlpatterns += [
    path('api/openapi/', get_openapi_view(), name='openapi-schema'),
    path('api/swagger-ui/',
         TemplateView.as_view(template_name='swagger_ui/base.html'),
         name='swagger-ui'),
]

# API for media files under /media/data directory
common_api_module = get_api_module('common')
urlpatterns += [
    url(r'^{}/(?P<path>.+)/$'.format(settings.MEDIA_API_URL.strip('/')),
        common_api_module.MediaFilesAPIView.as_view(),
        name='api-media')
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
            # url(r'^' + settings.BASE_URL + '__debug__/', include(debug_toolbar.urls)),
            path('__debug__/', include(debug_toolbar.urls)),
        ]


if not migrating() and not settings.TEST_RUN_MODE:
    init_decorators()
    init_field_type_registry()
