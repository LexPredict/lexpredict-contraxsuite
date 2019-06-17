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
from __future__ import absolute_import, unicode_literals

# Django imports
from django.urls import reverse
from django.views.generic import RedirectView

# Project imports
import apps.common.mixins
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.2/LICENSE"
__version__ = "1.2.2"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class BaseUserView(object):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    fields = ['username', 'first_name', 'last_name', 'name',
              'organization', 'email', 'role', 'is_active', 'photo']

    def has_permission(self):
        obj = self.get_object()
        if self.request.user.is_reviewer and self.request.user != obj:
            return False
        return True


class UserUpdateView(BaseUserView, apps.common.mixins.CustomUpdateView):
    def get_fields(self):
        if self.request.user.is_reviewer:
            return ['username', 'first_name', 'last_name', 'name', 'photo']
        return self.fields

    def get_success_url(self):
        return reverse('users:user-detail', args=[self.kwargs[self.slug_field]])


class UserDetailView(BaseUserView, apps.common.mixins.CustomDetailView):
    context_object_name = 'a_user'

    def get_update_url(self):
        return reverse('users:user-update', args=[self.kwargs[self.slug_field]])

    def get_object(self, queryset=None):
        if self.kwargs.get('username') == '-':
            return self.request.user
        return super().get_object(queryset)


class UserRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse('users:user-detail',
                       kwargs={'username': self.request.user.username})


class UserListView(apps.common.mixins.TechAdminRequiredMixin, apps.common.mixins.JqPaginatedListView):
    model = User
    extra_json_fields = ['role__name']

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = reverse('users:user-detail', args=[item['username']]) + \
                          '?next=' + self.request.path
        return data


from allauth.account.views import PasswordChangeView, reverse_lazy
PasswordChangeView.success_url = reverse_lazy('users:user-detail', args=['-'])