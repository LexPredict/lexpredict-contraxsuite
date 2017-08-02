# -*- coding: utf-8 -*-

# Future imports
from __future__ import absolute_import, unicode_literals

# Django imports
from django.core.urlresolvers import reverse
from django.views.generic import RedirectView

# Project imports
from apps.common.mixins import (
    JqPaginatedListView, TechAdminRequiredMixin,
    CustomDetailView, CustomUpdateView)
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0/LICENSE.pdf"
__version__ = "1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@lexpredict.com"


class BaseUserView(object):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    fields = ['username', 'first_name', 'last_name', 'name',
              'organization', 'email', 'role', 'is_active']

    def has_permission(self):
        obj = self.get_object()
        if self.request.user.is_reviewer and self.request.user != obj:
            return False
        return True


class UserUpdateView(BaseUserView, CustomUpdateView):
    def get_fields(self):
        if self.request.user.is_reviewer:
            return ['username', 'first_name', 'last_name', 'name']
        return self.fields

    def get_success_url(self):
        return reverse('users:user-detail', args=[self.kwargs[self.slug_field]])


class UserDetailView(BaseUserView, CustomDetailView):
    context_object_name = 'a_user'

    def get_update_url(self):
        return reverse('users:user-update', args=[self.kwargs[self.slug_field]])


class UserRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse('users:user-detail',
                       kwargs={'username': self.request.user.username})


class UserListView(TechAdminRequiredMixin, JqPaginatedListView):
    model = User

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = reverse('users:user-detail', args=[item['username']]) + \
                          '?next=' + self.request.path
        return data
