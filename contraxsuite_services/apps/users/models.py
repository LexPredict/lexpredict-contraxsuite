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

import tzlocal
# Django imports
from django.contrib.auth.models import AbstractUser, UserManager as AuthUserManager
from django.db import models
from django.db import transaction
# Standard imports
from django.db.models.deletion import CASCADE
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from timezone_field import TimeZoneField

# Project imports
from apps.users import signals

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class RoleManager(models.Manager):

    def qs_admins_or_managers(self) -> models.QuerySet:
        return self.filter(models.Q(is_admin=True) | models.Q(is_manager=True))


class Role(models.Model):
    """
    Role model for user roles
    """
    name = models.CharField(_('Name of Role'), max_length=50)
    code = models.CharField(_('Role Code'), max_length=50)
    order = models.PositiveSmallIntegerField()
    is_admin = models.BooleanField(default=False, db_index=True)
    is_manager = models.BooleanField(default=False, db_index=True)

    objects = RoleManager()

    class Meta(object):
        ordering = ('order', 'name')

    def __str__(self):
        return '{} (pk={})'.format(self.name, self.pk)

    @property
    def is_reviewer(self):
        return not (self.is_manager or self.is_admin)

    @property
    def abbr(self):
        return ''.join([w[0].upper() for w in self.name.split()])


class UserManager(AuthUserManager):

    def qs_admins_and_managers(self) -> models.QuerySet:
        return self.filter(role__in=models.Subquery(Role.objects.qs_admins_or_managers().order_by().values_list('pk')))


@python_2_unicode_compatible
class User(AbstractUser):
    """User object

    User object, as defined and customized for project implementation.

    TODO: Document common patterns for User customization.
    """

    objects = UserManager()

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_('Name of User'), blank=True, max_length=255)
    role = models.ForeignKey(Role, blank=True, null=True, on_delete=CASCADE)
    organization = models.CharField(_('Organization'), max_length=100, blank=True, null=True)
    timezone = TimeZoneField(blank=True, null=True)
    photo = models.ImageField(upload_to='photos/', max_length=100, blank=True, null=True)

    class Meta(object):
        ordering = ('username',)

    def __str__(self):
        return self.get_full_name()

    @property
    def is_admin(self):
        return self.role.is_admin

    @property
    def is_manager(self):
        return self.role.is_manager

    @property
    def is_reviewer(self):
        return self.role.is_reviewer

    def _fire_saved(self, old_instance=None):
        signals.user_saved.send(self.__class__, user=None, instance=self, old_instance=old_instance)

    def save(self, *args, **kwargs):
        if self.role is None:
            self.role = Role.objects.filter(is_admin=False, is_manager=False).last() \
                        or Role.objects.first()
        old_instance = User.objects.filter(pk=self.pk).first()
        res = super().save(*args, **kwargs)
        with transaction.atomic():
            transaction.on_commit(lambda: self._fire_saved(old_instance))
        return res

    def can_view_document(self, document):
        # TODO: review with new user access strategies

        # allow to any "power" user
        is_able = self.is_superuser or self.is_admin or self.is_manager

        # project-level perm. for reviewers
        if not is_able and self.is_reviewer:
            is_able = document.project.reviewers.filter(pk=self.pk).exists()

        # task-queue-level perm. for reviewers
        if not is_able and self.is_reviewer:
            is_able = self.taskqueue_set.filter(documents=document).exists()

        return is_able

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

    def get_time_zone(self):
        return self.timezone or tzlocal.get_localzone()
