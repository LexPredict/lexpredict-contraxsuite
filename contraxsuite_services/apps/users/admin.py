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
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Permission

# Project imports
from apps.users.models import User, SocialAppUri, CustomUserObjectPermission

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget = forms.HiddenInput()


class MyUserCreationForm(UserCreationForm):
    error_message = UserCreationForm.error_messages.update({
        'duplicate_username': 'This username has already been taken.'
    })

    class Meta(UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


class MyUserAdmin(AuthUserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    readonly_fields = ['uid']
    fieldsets = (('User Profile',
                  {'fields': ('name', 'organization', 'timezone', 'photo', 'uid')}),) + AuthUserAdmin.fieldsets
    list_display = ('username', 'name', 'group_names', 'is_superuser', 'organization', 'timezone')
    sensitive_fields = ('password',)
    search_fields = ['username', 'name', 'organization']
    add_fieldsets = AuthUserAdmin.add_fieldsets + \
                    (
                        (None, {'classes': ('wide',), 'fields': ('email',)}),
                    )

    @staticmethod
    def group_names(obj):
        return ', '.join(obj.groups.values_list('name', flat=True))

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(pk=User.get_anonymous().id)


class SocialAppUriAdminForm(forms.ModelForm):

    class Meta:
        model = SocialAppUri
        fields = ['social_app', 'uri_type', 'uri']
        widgets = {
            'value': forms.Textarea(
                attrs={
                    'rows': '2', 'cols': '95'
                }
            )
        }


class SocialAppUriAdmin(admin.ModelAdmin):
    list_display = ['social_app', 'uri_type', 'uri']
    search_fields = ['social_app', 'uri_type', 'uri']
    list_editable = ['uri_type', 'uri']
    list_display_links = ['social_app']

    def get_changelist_form(self, request, **kwargs):
        return SocialAppUriAdminForm


class PermissionAdmin(admin.ModelAdmin):
    list_display = ['codename', 'name', 'content_type']
    search_fields = ['codename', 'name', 'content_type__model']


class UserObjectPermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'permission', 'content_object', 'content_type', 'object_pk']
    list_filter = ['user', 'permission', 'content_type']
    search_fields = ['user__username', 'permission__name', 'permission__codename',
                     'content_type__model', 'object_pk']


admin.site.register(User, MyUserAdmin)
admin.site.register(SocialAppUri, SocialAppUriAdmin)

admin.site.register(Permission, PermissionAdmin)
admin.site.register(CustomUserObjectPermission, UserObjectPermissionAdmin)
