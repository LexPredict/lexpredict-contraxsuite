from rest_framework.authentication import TokenAuthentication
from django.core.urlresolvers import reverse


class CookieAuthentication(TokenAuthentication):

    def authenticate(self, request):
        # import ipdb;ipdb.set_trace()
        token_exempt_urls = [reverse('rest_login')]
        if not request.META.get('HTTP_AUTHORIZATION') and request.META['PATH_INFO'] not in token_exempt_urls:
            request.META['HTTP_AUTHORIZATION'] = request.COOKIES.get('auth_token', '')
        return super().authenticate(request)
