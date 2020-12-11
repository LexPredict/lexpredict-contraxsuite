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

# Standard imports
import re

from django.utils.http import urlencode

# Django imports
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.db.models import signals
from django.http import HttpResponseNotAllowed, HttpResponseForbidden, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import curry

# Project imports
from apps.users.authentication import CookieAuthentication, token_cache
from apps.task.utils.task_utils import check_blocks
# from apps.common.utils import get_test_user

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


EXEMPT_URLS = [re.compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [re.compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]


class LoginRequiredMiddleware(MiddlewareMixin):
    """
    Middleware that requires a user to be authenticated to view any page other than LOGIN_URL.
    Exemptions to this requirement can optionally be specified in settings
    via a list of regular expressions in LOGIN_EXEMPT_URLS (which you can copy from your urls.py).

    MIDDLEWARE_CLASSES should have 'django.contrib.auth.middleware.AuthenticationMiddleware'.
    TEMPLATE_CONTEXT_PROCESSORS setting should include'django.core.context_processors.auth'.
    """
    def process_view(self, request, view_func, args, kwargs):
        assert hasattr(request, 'user')
        path = request.path_info.lstrip('/')
        # auth check
        if not request.user.is_authenticated:
            if not any(m.match(path) for m in EXEMPT_URLS):
                return custom_redirect(settings.LOGIN_URL, next=request.path_info)
        # perm to explorer check
        if not request.user.has_perm('users.view_explorer'):
            if not any([m.match(path) for m in EXEMPT_URLS]):
                response = HttpResponseForbidden()
                msg = 'You do not have access to explorer.'
                response.content = render(request, '403.html', context={'message': msg})
                return response


def custom_redirect(url, *_args, **kwargs):
    params = urlencode(kwargs)
    return HttpResponseRedirect(url + "?%s" % params)


# class AutoLoginMiddleware(MiddlewareMixin):
#     """
#     Auto login test user.
#     Create test user if needed.
#     settings should have AUTOLOGIN_TEST_USER_FORBIDDEN_URLS
#     and AUTOLOGIN_ALWAYS_OPEN_URLS
#     MIDDLEWARE_CLASSES should have 'django.contrib.auth.middleware.AuthenticationMiddleware'.
#     TEMPLATE_CONTEXT_PROCESSORS setting should include 'django.core.context_processors.auth'.
#
#     # settings for AutoLoginMiddleware
#     # urls available for unauthorized users,
#     # otherwise login as "test_user"
#     AUTOLOGIN_ALWAYS_OPEN_URLS = [
#         reverse_lazy('account_login'),
#     ]
#     # forbidden urls for "test user" (all account/* except login/logout)
#     AUTOLOGIN_TEST_USER_FORBIDDEN_URLS = [
#         'accounts/(?!login|logout)',
#     ]
#
#     """
#     TEST_USER_FORBIDDEN_URLS = [
#         re.compile(str(expr)) for expr in settings.AUTOLOGIN_TEST_USER_FORBIDDEN_URLS]
#
#     def process_view(self, request, view_func, args, kwargs):
#
#         if config.auto_login:
#
#             path = request.path_info
#             if path in settings.AUTOLOGIN_ALWAYS_OPEN_URLS:
#                 return
#
#             if not request.user.is_authenticated:
#                 get_test_user()
#                 user = authenticate(username='test_user', password='test_user')
#                 request.user = user
#                 login(request, user)
#
#             if request.user.username == 'test_user':
#                 if any(m.search(path) for m in self.TEST_USER_FORBIDDEN_URLS):
#                     return redirect(reverse_lazy('home'))


class HttpResponseNotAllowedMiddleware(MiddlewareMixin):
    """
    Custom page for HTTP method Not Allowed error 405.
    """
    def process_response(self, request, response):
        if isinstance(response, HttpResponseNotAllowed):
            response.content = render(request, '405.html')
        return response


class Response5xxErrorMiddleware(MiddlewareMixin):
    """
    Custom page for 5xx errors (502 Bad Gateway).
    """
    def process_response(self, request, response):
        if str(response.status_code).startswith('5'):
            response.status_code = 500
            response.content = render(request, '500.html')
        return response


class Response404ErrorMiddleware(MiddlewareMixin):
    """
    Custom page for 404 errors (404 Not Found).
    """
    def process_response(self, request, response):
        if response.status_code == 404:
            response = JsonResponse({'message': 'Not Found'})
            response.status_code = 404
        return response


class Response500ErrorMiddleware(MiddlewareMixin):
    """
    Custom page for 500 error
    """
    def process_response(self, request, response):
        if response.status_code == 500 and settings.DEBUG is False and '/api/' in request.path:
            response = JsonResponse({'message': response.reason_phrase,
                                     'content': response.content.decode('utf-8')})
            response.status_code = 500
        return response


class RequestUserMiddleware(MiddlewareMixin):
    """
    Provide access to request user in models
    """
    def process_request(self, request):
        if request.method not in ('HEAD', 'OPTIONS', 'TRACE'):
            if hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user
            elif 'apps.users.authentication.CookieAuthentication' in settings.REST_FRAMEWORK.get('DEFAULT_AUTHENTICATION_CLASSES', []):
                try:
                    user = CookieAuthentication().authenticate(request)[0]
                    if not user.is_authenticated:
                        user = None
                except:
                    user = None
            else:
                user = None
            update_save_info = curry(self.insert_user, user)
            signals.pre_save.connect(
                update_save_info, dispatch_uid=(self.__class__, request,), weak=False)
            signals.post_save.connect(
                update_save_info, dispatch_uid=(self.__class__, request,), weak=False)
            signals.m2m_changed.connect(
                update_save_info, dispatch_uid=(self.__class__, request,), weak=False)
            signals.pre_delete.connect(
                update_save_info, dispatch_uid=(self.__class__, request,), weak=False)
            signals.post_delete.connect(
                update_save_info, dispatch_uid=(self.__class__, request,), weak=False)

    def process_response(self, request, response):
        signals.pre_save.disconnect(dispatch_uid=(self.__class__, request,))
        signals.post_save.disconnect(dispatch_uid=(self.__class__, request,))
        signals.m2m_changed.disconnect(dispatch_uid=(self.__class__, request,))
        signals.pre_delete.disconnect(dispatch_uid=(self.__class__, request,))
        signals.post_delete.disconnect(dispatch_uid=(self.__class__, request,))
        return response

    def process_exception(self, request, exception):
        signals.pre_save.disconnect(dispatch_uid=(self.__class__, request,))
        signals.post_save.disconnect(dispatch_uid=(self.__class__, request,))
        signals.m2m_changed.disconnect(dispatch_uid=(self.__class__, request,))
        signals.pre_delete.disconnect(dispatch_uid=(self.__class__, request,))
        signals.post_delete.disconnect(dispatch_uid=(self.__class__, request,))

    def insert_user(self, user, sender, instance, **kwargs):
        try:
            instance.request_user = user
        except:
            # if instance is not object
            pass


class AppEnabledRequiredMiddleware(MiddlewareMixin):
    """
    Middleware that requires to enable certain kind of application enabled.
    in "application settings"
    """
    def process_view(self, request, view_func, args, kwargs):
        if hasattr(view_func, 'view_class') and hasattr(view_func.view_class, 'sub_app'):
            current_sub_app = view_func.view_class.sub_app
            from apps.extract.app_vars import STANDARD_LOCATORS, OPTIONAL_LOCATORS
            available_locators = set(STANDARD_LOCATORS.val) | set(OPTIONAL_LOCATORS.val)
            if current_sub_app not in available_locators:
                messages.error(request, 'This locator is not enabled.')
                if request.is_ajax() or request.META['CONTENT_TYPE'] == 'application/json':
                    return HttpResponseForbidden('Standard sub-application "%s" is not enabled.'
                                                 % current_sub_app)
                return redirect(reverse_lazy('common:application-settings'))


class CookieMiddleware(MiddlewareMixin):
    """
    Set cookie in response -
    1. set auth_token from AUTHORIZATION request header,
       see apps.users.authentication.CookieAuthentication
    2. set extra cookie variables

    Delete "auth_token" when django logout
    """

    def process_request(self, request):
        if request.META['PATH_INFO'] == reverse('account_logout') and request.method == 'POST':
            try:
                request.user.auth_token.delete()
            except (AttributeError, ObjectDoesNotExist):
                pass

    def process_response(self, request, response):
        current_path = request.META['PATH_INFO']

        # if restful login - set response cookie auth_token from login response - "key"
        if current_path == reverse('rest_login') \
                and getattr(response, 'data', None) and response.data.get('key'):
            response.set_cookie('auth_token', 'Token %s' % response.data['key'])

        # if django login - set token in cookies
        elif current_path == reverse('account_login') and request.method == 'POST'\
                and request.user.is_authenticated:
            _, __, token = token_cache.get_token_keys(user=request.user)
            response.set_cookie('auth_token', 'Token %s' % token)

        # delete user-specific cookies after logout
        elif current_path in (reverse('account_logout'), reverse('rest_logout')) \
                and request.method == 'POST':
            response.delete_cookie('auth_token')
            response.delete_cookie('user_name')
            response.delete_cookie('user_id')
            # INFO: token is deleted in apps.users.adapters.AccountAdapter.logout
            # because here we have AnonimousUser

        # otherwise set auth_token from incoming headers or cookie
        else:
            auth_token = request.COOKIES.get('auth_token', request.META.get('HTTP_AUTHORIZATION'))
            if auth_token:
                response.set_cookie('auth_token', auth_token)

        # set extra cookie variables if user exists
        if request.user and hasattr(request.user, 'name'):
            response.set_cookie('user_name', request.user.name)
            response.set_cookie('user_id', request.user.pk)
        response.set_cookie('release_version', settings.VERSION_NUMBER)

        return response


ALLOWED_ALWAYS_NON_GET_URLS = re.compile(r'/{}(?:admin|accounts)/|/rest-auth/|/api/v1/users/verify-token/'.format(settings.BASE_URL))


class AppBlocksMiddleware(MiddlewareMixin):
    """
    Middleware that checks any blocks before processing
    """
    def process_view(self, request, view_func, args, kwargs):
        # check for any app-wide blocks
        if request.method != 'GET':
            # allow any actions under /admin
            if ALLOWED_ALWAYS_NON_GET_URLS.search(request.path):
                return
            block_msg = check_blocks(raise_error=False, error_message='Unable to process request.')
            if block_msg is not False:
                # 1. request is ajax
                # 2. content type is json
                # 3. any api request (except /api/app/ or /api/version/ - mostly this check is for
                # apps.project.api.v1.ProjectViewSet.send_clusters_to_project which receives form data
                if request.is_ajax() or request.META['CONTENT_TYPE'] == 'application/json' or re.search(r'^/api/v\d', request.path):
                    response = JsonResponse({'detail': block_msg}, status=403)
                else:
                    response = HttpResponseForbidden()
                    response.content = render(request, '403.html', context={'message': block_msg})
                return response
