# -*- coding: utf-8 -*-

# Standard imports
from re import compile as re_compile

# Django imports
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.db.models import signals
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import curry

# Project imports
from allauth.account.models import EmailAddress
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.3/LICENSE"
__version__ = "1.0.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


EXEMPT_URLS = [re_compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [re_compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]


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
        if not request.user.is_authenticated() and not settings.AUTOLOGIN:
            path = request.path_info.lstrip('/')
            if not any(m.match(path) for m in EXEMPT_URLS):
                return redirect(settings.LOGIN_URL)


class AutoLoginMiddleware(MiddlewareMixin):
    """
    Auto login test user.
    Create test user if needed.
    settings should have AUTOLOGIN_TEST_USER_FORBIDDEN_URLS
    and AUTOLOGIN_ALWAYS_OPEN_URLS
    MIDDLEWARE_CLASSES should have 'django.contrib.auth.middleware.AuthenticationMiddleware'.
    TEMPLATE_CONTEXT_PROCESSORS setting should include 'django.core.context_processors.auth'.
    """
    TEST_USER_FORBIDDEN_URLS = [
        re_compile(str(expr)) for expr in settings.AUTOLOGIN_TEST_USER_FORBIDDEN_URLS]

    def process_view(self, request, view_func, args, kwargs):

        path = request.path_info
        if path in settings.AUTOLOGIN_ALWAYS_OPEN_URLS:
            return

        # TODO: Document test_user account.
        # TODO: Allow configuration disable for test_user account.
        if not request.user.is_authenticated():
            test_user, created = User.objects.update_or_create(
                username='test_user',
                defaults=dict(
                    first_name='Test',
                    last_name='User',
                    name='Test User',
                    email='test@user.com',
                    role='manager',
                    is_active=True))
            if created:
                test_user.set_password('test_user')
                test_user.save()
                EmailAddress.objects.create(
                    user=test_user,
                    email=test_user.email,
                    verified=True,
                    primary=True)

            user = authenticate(username='test_user', password='test_user')
            request.user = user
            login(request, user)

        if request.user.username == 'test_user':
            if any(m.search(path) for m in self.TEST_USER_FORBIDDEN_URLS):
                return redirect(reverse_lazy('home'))


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


class RequestUserMiddleware(MiddlewareMixin):
    """
    Provide access to request user in models
    """
    def process_request(self, request):
        if request.method not in ('HEAD', 'OPTIONS', 'TRACE'):
            if hasattr(request, 'user') and request.user.is_authenticated():
                user = request.user
            else:
                user = None
            update_save_info = curry(self.insert_user, user)
            signals.pre_save.connect(
                update_save_info, dispatch_uid=(self.__class__, request,), weak=False)
            signals.post_save.connect(
                update_save_info, dispatch_uid=(self.__class__, request,), weak=False)
            signals.m2m_changed.connect(
                update_save_info, dispatch_uid=(self.__class__, request,), weak=False)

    def process_response(self, request, response):
        signals.pre_save.disconnect(dispatch_uid=(self.__class__, request,))
        signals.post_save.disconnect(dispatch_uid=(self.__class__, request,))
        signals.m2m_changed.disconnect(dispatch_uid=(self.__class__, request,))
        return response

    def process_exception(self, request, exception):
        signals.pre_save.disconnect(dispatch_uid=(self.__class__, request,))
        signals.post_save.disconnect(dispatch_uid=(self.__class__, request,))
        signals.m2m_changed.disconnect(dispatch_uid=(self.__class__, request,))
        return None

    def insert_user(self, user, sender, instance, **kwargs):
        instance.request_user = user
