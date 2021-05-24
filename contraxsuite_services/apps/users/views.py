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

import json

# Django imports
from allauth.socialaccount.models import SocialApp
from django.apps import apps as django_apps
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Permission
from django.db.models import F, Value, CharField, IntegerField
from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import RedirectView
from guardian.shortcuts import get_content_type

# Project imports
from apps.common.mixins import CustomUpdateView, CustomDetailView, \
    JqPaginatedListView, AjaxListView
from apps.users.models import User, CustomUserObjectPermission

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class BaseUserView(PermissionRequiredMixin):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    fields = ['username', 'first_name', 'last_name', 'name',
              'organization', 'email', 'is_active', 'photo']


class UserUpdateView(BaseUserView, CustomUpdateView):

    def has_permission(self):
        # update only own user details
        obj = self.get_object()
        return self.request.user.has_perm('users.change_user', obj)

    def get_success_url(self):
        return reverse('users:user-detail', args=[self.kwargs[self.slug_field]])


class UserDetailView(BaseUserView, CustomDetailView):
    context_object_name = 'a_user'

    def has_permission(self):
        # see only own user details for all users, admins can see all user details
        obj = self.get_object()
        if obj != self.request.user:
            return self.request.user.has_perm('users.view_user', obj)
        return True

    def get_update_url(self):
        return reverse('users:user-update', args=[self.kwargs[self.slug_field]])

    def get_object(self, queryset=None):
        if self.kwargs.get('username') == '-':
            return self.request.user
        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['has_change_perm'] = self.request.user.has_perm('users.change_user', self.get_object())
        return ctx


class UserRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse('users:user-detail',
                       kwargs={'username': self.request.user.username})


class ViewUsersPermission(PermissionRequiredMixin):
    def has_permission(self):
        # only admins have 'users.view_user' permission
        return self.request.user.has_perm('users.view_user')


class UserListView(ViewUsersPermission, JqPaginatedListView):
    model = User

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = self.full_reverse('users:user-detail', args=[item['username']]) + \
                          '?next=' + self.request.path
        return data


class UserPermissionsListView(ViewUsersPermission, AjaxListView):
    model = CustomUserObjectPermission
    template_name = 'users/user_object_permissions.html'

    source_model_map = {
        'project': {
            'verbose_name': 'Project',
            'app_label': 'project',
            'model_name': 'project',
            'title_field': 'name'
        },
        'document_type': {
            'verbose_name': 'Document Type',
            'app_label': 'document',
            'model_name': 'documenttype',
            'title_field': 'title'
        },
        'document_field': {
            'verbose_name': 'Document Field',
            'app_label': 'document',
            'model_name': 'documentfield',
            'title_field': 'title'
        },
        'document_field_category': {
            'verbose_name': 'Document Field Category',
            'app_label': 'document',
            'model_name': 'documentfieldcategory',
            'title_field': 'name'
        },
        'document_field_family': {
            'verbose_name': 'Document Field Family',
            'app_label': 'document',
            'model_name': 'documentfieldfamily',
            'title_field': 'title'
        },
    }

    def get_model(self):
        """
        Get db model by given "source" from self.source_model_map
        :return: db Model
        """
        source = self.request.GET.get('source', list(self.source_model_map.keys())[0])
        source_data = self.source_model_map[source]
        model = django_apps.get_model(source_data['app_label'], source_data['model_name'])
        return model

    def get_perm_list(self, codes_only=True):
        """
        Get available Permissions for a given db model
        :return: list(str(perm codes)) | list(dict(name, codename))
        """
        model = self.get_model()
        ctype = get_content_type(model)
        perms = Permission.objects.filter(content_type=ctype).order_by('codename')
        perms = perms.values_list('codename', flat=True) if codes_only else \
            perms.values('name', 'codename')
        return list(perms)

    def get_json_data(self, **kwargs):
        """
        Get Object Permission List by User / or By Object
        If "object_pk" provided - get perms by User for a given source/object
        If "user_id" provided - get perms by Object for a given source/user
        """
        request_data = self.request.GET
        model = self.get_model()
        ctype = get_content_type(model)
        perms_qs = CustomUserObjectPermission.objects.filter(content_type=ctype)
        object_pk, user_id = None, None
        if 'object_pk' in request_data:
            source_name = request_data.get('source', list(self.source_model_map.keys())[0])
            title_field = self.source_model_map[source_name]['title_field']
            object_qs = model.objects.order_by(title_field)
            object_pk = request_data['object_pk'] or object_qs.first().pk
            perms_qs = perms_qs.filter(object_pk=object_pk)
            source_model_qs = User.objects\
                .annotate(title_field=F('username'),
                          user_id=F('pk'),
                          object_pk=Value(object_pk, output_field=CharField()))
        elif 'user_id' in request_data:
            user_id = request_data['user_id'] or User.objects.order_by('pk').first().id
            perms_qs = perms_qs.filter(user_id=user_id)
            source = self.request.GET.get('source', list(self.source_model_map.keys())[0])
            title_field = self.source_model_map[source]['title_field']
            source_model_qs = model.objects\
                .annotate(title_field=F(title_field),
                          object_pk=F('pk'),
                          user_id=Value(user_id, output_field=IntegerField()))
        else:
            raise RuntimeError('Provide either user_id or document_type_id in query string.')

        source_model_qs = source_model_qs \
            .annotate(content_type_id=Value(ctype.id, output_field=IntegerField())) \
            .values('pk', 'title_field', 'content_type_id', 'object_pk', 'user_id')

        permissions = perms_qs.values('permission__codename', 'object_pk', 'user_id')

        perm_set = {i: False for i in self.get_perm_list()}

        # data should include all source model objects
        data = {str(i['pk']): dict(i) for i in source_model_qs}
        for pk in data:
            data[pk].update(perm_set)

        # permissions include already assigned model object perms
        for perm in permissions:
            key = 'object_pk' if 'user_id' in request_data else 'user_id'
            data[str(perm[key])][perm['permission__codename']] = True
        return list(data.values())

    def post(self, request, *args, **kwargs):
        """
        Save or Delete Object Permissions
        """
        perms_to_add = []
        perms_to_delete = []
        data = json.loads(request.body)    # TODO: may be unsafe

        # get perms map for perm id
        _permissions = Permission.objects.values('content_type_id', 'codename', 'id')
        permissions = {}
        for p in _permissions:
            content_type_id = p['content_type_id']
            if content_type_id not in permissions:
                permissions[content_type_id] = {}
            permissions[content_type_id][p['codename']] = p['id']

        # create perms
        for item in data:
            target = perms_to_add if item['value'] is True else perms_to_delete
            target.append({
                'object_pk': item['object_pk'],
                'content_type_id': item['content_type_id'],
                'permission_id': permissions[item['content_type_id']][item['perm_name']],
                'user_id': item['user_id']
            })
        perms_to_add = [CustomUserObjectPermission(**i) for i in perms_to_add]
        CustomUserObjectPermission.objects.bulk_create(perms_to_add, ignore_conflicts=True)

        # delete perms (TODO: make in one query through Q| )
        for i in perms_to_delete:
            CustomUserObjectPermission.objects.filter(**i).delete()

        return JsonResponse({'status': 'success'})

    def get_context_data(self, **kwargs):
        """
        Get context data for html page like select-box options and chosen ones
        """
        request_data = self.request.GET
        ctx = super().get_context_data(**kwargs)
        ctx['source_model_map'] = self.source_model_map
        source_name = request_data.get('source', list(self.source_model_map.keys())[0])
        ctx['chosen_source_name'] = source_name
        ctx['chosen_source_data'] = self.source_model_map[source_name]
        ctx['perm_list'] = self.get_perm_list(codes_only=False)
        if 'user_id' in request_data:
            ctx['users'] = list(User.objects.order_by('username').values('pk', 'username'))
            ctx['chosen_user_id'] = str(request_data.get('user_id') or User.objects.order_by('pk').first().id)
        else:
            model = self.get_model()
            title_field = self.source_model_map[source_name]['title_field']
            object_qs = model.objects.annotate(title_field=F(title_field)).order_by('title_field')
            ctx['objects'] = list(object_qs.values('pk', 'title_field'))
            ctx['chosen_object_pk'] = str(request_data.get('object_pk') or object_qs.first().pk)
        return ctx


from allauth.account.views import PasswordChangeView, reverse_lazy, LoginView


class MixedLoginView(LoginView):

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        ret['providers'] = SocialApp.objects.all()
        return ret


PasswordChangeView.success_url = reverse_lazy('users:user-detail', args=['-'])
