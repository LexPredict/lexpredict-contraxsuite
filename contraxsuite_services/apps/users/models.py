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
from __future__ import unicode_literals, absolute_import

# Standard imports
import tzlocal
import uuid
from allauth.socialaccount.models import SocialApp
from timezone_field import TimeZoneField
from typing import List, Tuple, Union

# Django imports
from django.contrib.auth.models import Permission, AbstractUser
from django.db import models, transaction
from django.db.models import Q, QuerySet
from django.db.models.deletion import CASCADE
from django.db.models.signals import m2m_changed, post_delete
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from guardian import shortcuts
from guardian.core import ObjectPermissionChecker
from guardian.ctypes import get_content_type
from guardian.managers import UserObjectPermissionManager
from guardian.models import UserObjectPermissionAbstract

# Project imports
from apps.common.fields import StringUUIDField
from apps.common.file_storage import get_media_file_storage
from apps.users import signals

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


AbstractUser._meta.get_field('email')._unique = True
AbstractUser._meta.get_field('email').blank = False
AbstractUser._meta.get_field('email').null = False


@python_2_unicode_compatible
class User(AbstractUser):
    """
    User object, as defined and customized for project implementation.
    """
    USER_ORIGIN_ADMIN = 'admin'
    USER_ORIGIN_SOCIAL = 'social'
    USER_ORIGIN_CHOICES = [(USER_ORIGIN_ADMIN, 'CS Admin',), (USER_ORIGIN_SOCIAL, 'Social Account',)]

    # First Name and Last Name do not cover name patterns
    # around the globe.
    uid = StringUUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(_('Name of User'), blank=True, max_length=255)
    initials = models.CharField(_('User Initials'), blank=True, max_length=2)
    organization = models.CharField(_('Organization'), max_length=100, blank=True, null=True)
    timezone = TimeZoneField(blank=True, null=True)
    photo = models.ImageField(upload_to='photo', max_length=100, blank=True, null=True,
                              storage=get_media_file_storage(folder='media'))
    origin = models.CharField(max_length=30, choices=USER_ORIGIN_CHOICES,
                              default=USER_ORIGIN_CHOICES[0][0],
                              blank=False, null=False)

    class Meta:
        ordering = ('username',)
        permissions = (
            ('view_user_stats', 'View user stats'),
            ('view_explorer', 'View explorer UI'),
        )

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        model_perm = super().has_perm(perm)
        object_perm = super().has_perm(perm, obj)
        return model_perm or object_perm

    def get_all_permissions(self, obj=None, get_non_object_perms=False):
        model_perms = super().get_all_permissions()
        if obj is not None and get_non_object_perms is False:
            try:
                perm_prefix = obj._meta.model._meta.model_name
                model_perms = {i for i in model_perms if i.startswith(f'{perm_prefix}.')}
            except:
                pass
        model_perms = {i.split('.', 1)[-1] for i in model_perms}
        object_perms = super().get_all_permissions(obj)
        return model_perms | object_perms

    def _fire_saved(self, old_instance=None):
        signals.user_saved.send(self.__class__, user=None, instance=self, old_instance=old_instance)

    def save(self, *args, **kwargs):
        self.name = self.get_full_name()
        self.initials = self.get_initials()
        old_instance = User.objects.filter(pk=self.pk).first()
        # this is made on FE side to use custom fonts via css
        # if not self.photo:
        #     from apps.users.user_utils import save_default_avatar
        #     save_default_avatar(self)
        super().save(*args, **kwargs)
        with transaction.atomic():
            transaction.on_commit(lambda: self._fire_saved(old_instance))

    def can_view_document(self, document):
        return self.has_perm('project.view_documents', document.project) or \
               self.has_perm('document.view_document', document)

    @property
    def user_projects(self):
        from apps.project.models import Project
        return shortcuts.get_objects_for_user(self, 'project.view_project', Project).only('pk')

    @property
    def user_document_ids(self):
        from apps.project.models import Project
        from apps.document.models import Document

        user_projects = self.user_projects
        if not user_projects.exists():
            return []
        user_project_docs = Document.objects.filter(
            project__in=shortcuts.get_objects_for_user(self, 'project.view_documents', Project))
        user_docs = shortcuts.get_objects_for_user(self, 'document.view_document', Document)
        return user_docs.union(user_project_docs).distinct().values_list('id', flat=True)

    @property
    def user_documents(self, as_qs=False):
        from apps.document.models import Document
        return Document.objects.filter(pk__in=self.user_document_ids)

    @staticmethod
    def get_users_for_object(object_pk, object_model, perm_name: str) -> Union[QuerySet, List['User']]:
        ctype_id = get_content_type(object_model).id

        users_with_obj_perm_ids = User.objects.filter(
            customuserobjectpermission__object_pk=object_pk,
            customuserobjectpermission__permission__codename=perm_name,
            customuserobjectpermission__content_type_id=ctype_id).distinct().values_list('pk', flat=True)
        users_with_user_model_perm_ids = User.objects.filter(
            user_permissions__codename=perm_name,
            user_permissions__content_type_id=ctype_id).values_list('pk', flat=True)
        users_with_group_model_perm_ids = User.objects.filter(
            groups__permissions__codename=perm_name,
            groups__permissions__content_type_id=ctype_id).values_list('pk', flat=True)

        user_ids = set(list(users_with_obj_perm_ids) +
                       list(users_with_user_model_perm_ids) +
                       list(users_with_group_model_perm_ids))

        return User.objects.filter(id__in=user_ids)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between
        or username
        """
        if self.name:
            return self.name
        if self.first_name and self.last_name:
            full_name = '%s %s' % (self.first_name, self.last_name)
            return full_name.strip()
        return self.username

    @classmethod
    def _get_initials(cls, name: str = "", first_name: str = "", last_name: str = ""):
        """
        Class method to use in migrations, Convert self.name into initials
        """
        name, first_name, last_name = name.strip(), first_name.strip(), last_name.strip()
        if first_name and last_name:
            return "".join([first_name[0].upper(), last_name[0].upper()])
        if len(first_name) > 1:
            # Remove spaces
            return first_name.replace(" ", "")[:1].upper()
        if name:
            name_parts = name.split()
            initials = name[:2] if len(name_parts) == 1 else name_parts[0][0] + name_parts[1][0]
            return initials.upper()
        return 'XX'

    def get_initials(self):
        """
        Object method, Convert self.name into initials
        """
        return self._get_initials(name=self.name,
                                  first_name=self.first_name,
                                  last_name=self.last_name)

    def get_time_zone(self):
        return self.timezone or tzlocal.get_localzone()


@receiver(signal=post_delete, sender=User)
def delete_user_permissions(instance, **kwargs):
    CustomUserObjectPermission.objects.filter(user=instance).delete()


@receiver(signal=m2m_changed, sender=User.groups.through)
def adjust_user_permissions(instance, action, reverse, model, pk_set, using, *args, **kwargs):
    # TODO: handle user permissions or project-groups like owners
    if action == 'post_remove':
        pass
    elif action == 'post_add':
        pass


class SocialAppUri(models.Model):
    """
    Class stores custom URIs that CS uses to request authorization, token
    or user claims
    """
    URI_TYPE_AUTH = 'auth'
    URI_TYPE_TOKEN = 'token'
    URI_TYPE_PROFILE = 'profile'

    social_app: models.ForeignKey = models.ForeignKey(
        SocialApp,
        blank=True,
        null=False,
        db_index=True,
        on_delete=CASCADE
    )

    URI_TYPE_CHOICES: List[Tuple[str, str]] = [
        (URI_TYPE_AUTH, URI_TYPE_AUTH,),
        (URI_TYPE_TOKEN, URI_TYPE_TOKEN,),
        (URI_TYPE_PROFILE, URI_TYPE_PROFILE,),
    ]

    """
    uri_type can be either of URI_TYPE_X values - each value
    means something to the specific OAuth provider 
    """
    uri_type: models.CharField = models.CharField(
        verbose_name='URI type',
        max_length=64,
        db_index=True,
        choices=URI_TYPE_CHOICES,
        null=False
    )

    """
    a URI like https://dev-12345.okta.com/oauth2/v1/clients for Okta
    provider, uri_type = "profile"
    """
    uri: models.CharField = models.CharField(
        verbose_name='URI',
        max_length=1024,
        db_index=True,
        null=True
    )

    class Meta:
        verbose_name = 'Social App URI'
        verbose_name_plural = 'Social App URIs'
        unique_together = (('social_app', 'uri_type',),)
        ordering = ('social_app', 'uri_type',)

    def __repr__(self):
        app_str = '-'
        try:
            app_str = self.social_app.name
        except:
            pass
        return f'App: "{app_str}", type: "{self.uri_type}", URI: "{self.uri}"'


class CustomObjectPermissionManager(UserObjectPermissionManager):

    def bulk_assign_perm(self, perm, user_or_group, queryset):
        """
        Patched original method to ignore conflicts
        """
        if isinstance(queryset, list):
            ctype = get_content_type(queryset[0])
        else:
            ctype = get_content_type(queryset.model)

        if not isinstance(perm, Permission):
            permission = Permission.objects.get(content_type=ctype, codename=perm)
        else:
            permission = perm

        checker = ObjectPermissionChecker(user_or_group)
        checker.prefetch_perms(queryset)

        assigned_perms = []
        for instance in queryset:
            if not checker.has_perm(permission.codename, instance):
                kwargs = {'permission': permission, self.user_or_group_field: user_or_group}
                if self.is_generic():
                    kwargs['content_type'] = ctype
                    kwargs['object_pk'] = instance.pk
                else:
                    kwargs['content_object'] = instance
                assigned_perms.append(self.model(**kwargs))
        self.model.objects.bulk_create(assigned_perms, ignore_conflicts=True)    # change is here

        return assigned_perms

    def assign_perm_to_many(self, perm, users_or_groups, obj):
        """
        Patched original method to ignore conflicts
        """
        ctype = get_content_type(obj)
        if not isinstance(perm, Permission):
            permission = Permission.objects.get(content_type=ctype,
                                                codename=perm)
        else:
            permission = perm

        kwargs = {'permission': permission}
        if self.is_generic():
            kwargs['content_type'] = ctype
            kwargs['object_pk'] = obj.pk
        else:
            kwargs['content_object'] = obj

        to_add = []
        field = self.user_or_group_field
        for user in users_or_groups:
            kwargs[field] = user
            to_add.append(
                self.model(**kwargs)
            )

        return self.model.objects.bulk_create(to_add, ignore_conflicts=True)    # change is here

    def bulk_remove_perm(self, perm, user_or_group, queryset):
        """
        Patched original method to work with user_or_group as Queryset
        and have queryset from "queryset" attr if it's just an instance
        """

        # start change
        if not isinstance(queryset, QuerySet):
            queryset = queryset._meta.model.objects.filter(pk=queryset.pk)

        if isinstance(user_or_group, (QuerySet, list)):
            ids = user_or_group.values_list('pk', flat=True)
            filters = Q(**{self.user_or_group_field + '__pk__in': ids})
        else:
            # end change
            filters = Q(**{self.user_or_group_field: user_or_group})

        if isinstance(perm, Permission):
            filters &= Q(permission=perm)
        else:
            ctype = get_content_type(queryset.model)
            filters &= Q(permission__codename=perm,
                         permission__content_type=ctype)

        if self.is_generic():
            filters &= Q(object_pk__in=[str(pk) for pk in queryset.values_list('pk', flat=True)])
        else:
            filters &= Q(content_object__in=queryset)

        return self.filter(filters).delete()


class CustomUserObjectPermission(UserObjectPermissionAbstract):

    objects = CustomObjectPermissionManager()

    class Meta(UserObjectPermissionAbstract.Meta):
        abstract = False
        indexes = [
            *UserObjectPermissionAbstract.Meta.indexes,
            models.Index(fields=['content_type', 'object_pk', 'user']),
        ]
