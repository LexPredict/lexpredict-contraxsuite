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

# Django imports
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.dispatch import receiver

# Project imports
from apps.users.models import User


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.2/LICENSE"
__version__ = "1.1.2"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class AppVar(models.Model):
    """Storage for application variables"""

    # Task name
    name = models.CharField(max_length=100, db_index=True, unique=True)

    # additional data for a task
    value = JSONField(blank=True, null=True)

    # last modified date
    date = models.DateTimeField(auto_now=True, db_index=True)

    # last modified user
    user = models.ForeignKey(
        User, related_name="created_%(class)s_set", null=True, blank=True, db_index=True)

    def __str__(self):
        return "App Variable (name={})".format(self.name)

    @classmethod
    def set(cls, name, value):
        obj, _ = cls.objects.get_or_create(name=name)
        obj.value = value
        obj.save()
        return obj

    @classmethod
    def get(cls, name):
        try:
            return cls.objects.get(name=name)
        except cls.DoesNotExist:
            return None

    @classmethod
    def clear(cls, name):
        return cls.objects.get(name=name).delete()


@receiver(models.signals.post_save, sender=AppVar)
def save_var(sender, instance, created, **kwargs):
    """
    Store created_by from request
    """
    if hasattr(instance, 'request_user'):
        models.signals.post_save.disconnect(save_var, sender=sender)
        if created:
            instance.user = instance.request_user
            instance.save()
        models.signals.post_save.connect(save_var, sender=sender)


class ReviewStatusGroup(models.Model):
    """
    ReviewStatusGroup object model
    """
    # Group verbose name
    name = models.CharField(unique=True, max_length=100, db_index=True)

    # Group code
    code = models.CharField(unique=True, max_length=100, db_index=True,
                            blank=True, null=True)

    # Group order number
    order = models.PositiveSmallIntegerField()

    is_active = models.BooleanField(default=True, db_index=True)

    class Meta(object):
        ordering = ['order', 'name', 'code']

    def __str__(self):
        """"
        String representation
        """
        return "ReviewStatusGroup (pk={0}, name={1})" \
            .format(self.pk, self.name)

    def save(self, **kwargs):
        if not self.code:
            self.code = self.name.lower().replace(' ', '_')
        return super().save(**kwargs)


class ReviewStatus(models.Model):
    """
    ReviewStatus object model
    """
    # Status verbose name
    name = models.CharField(unique=True, max_length=100, db_index=True)

    # Status code
    code = models.CharField(unique=True, max_length=100, db_index=True,
                            blank=True, null=True)

    # Status order number
    order = models.PositiveSmallIntegerField()

    # Status group
    group = models.ForeignKey(ReviewStatusGroup, blank=True, null=True, db_index=True)

    # flag to detect f.e. whether we should recalculate fields for a document
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta(object):
        ordering = ['order', 'name', 'code']
        verbose_name_plural = 'Review Statuses'

    def __str__(self):
        """"
        String representation
        """
        return "ReviewStatus (pk={0}, name={1})" \
            .format(self.pk, self.name)

    def save(self, **kwargs):
        if not self.code:
            self.code = self.name.lower().replace(' ', '_')
        return super().save(**kwargs)

    @classmethod
    def initial_status(cls):
        try:
            return cls.objects.first()
        except cls.DoesNotExist:
            return None

    @classmethod
    def initial_status_pk(cls):
        status = cls.initial_status()
        return cls.initial_status().pk if status else None


def get_default_status():
    return ReviewStatus.initial_status_pk()
