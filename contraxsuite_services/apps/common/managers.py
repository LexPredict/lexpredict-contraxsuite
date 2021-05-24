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

from django.db import models
from apps.common.utils import Map

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DotValuesIterable(models.query.ValuesIterable):
    """
    Iterable returned by QuerySet.values() that yields a Map object with .dot access
    for each row.
    """
    def __iter__(self):
        for i in super().__iter__():
            yield Map(i)


class AdvancedQuerySet(models.query.QuerySet):
    """
    Substitution the QuerySet, and adding additional methods to QuerySet
    Patched .values() behaves like a class and allows access via dot
    """
    def dot_values(self, *fields, **expressions):
        fields += tuple(expressions)
        clone = self._values(*fields, **expressions)
        clone._iterable_class = DotValuesIterable
        return clone


class AdvancedManager(models.manager.BaseManager.from_queryset(AdvancedQuerySet)):
    pass


class BulkSignalsQuerySet(models.QuerySet):

    def update(self, **kwargs):
        ret = super().update(**kwargs)
        for obj in self:
            models.signals.post_save.send(obj.__class__, instance=obj, created=False)
        return ret

    def delete(self):
        ret = super().delete()
        for obj in self:
            models.signals.post_delete.send(obj.__class__, instance=obj)
        return ret


class BulkSignalsManager(models.Manager):

    def __init__(self, use_in_migrations=None, disallow_ignore_conflicts=True):
        super().__init__()
        if use_in_migrations is not None:
            self.use_in_migrations = use_in_migrations
        self.disallow_ignore_conflicts = disallow_ignore_conflicts

    def get_queryset(self):
        qs = BulkSignalsQuerySet(self.model, using=self._db)
        qs.use_in_migrations = self.use_in_migrations
        return qs

    def bulk_create(self, objs, ignore_conflicts=False, **kwargs):
        if ignore_conflicts and self.disallow_ignore_conflicts:
            raise RuntimeError('Setting ignore_conflicts = True is not allowed for this model. '
                               'Django does not return ids of the inserted objects when ignore_conflicts is True '
                               'and this may break behaviour of the receivers of the post_save signal fired from this '
                               'method. For example: django simple history expects ids to be set.')
        ret = super().bulk_create(objs, **kwargs)
        for obj in objs:
            models.signals.post_save.send(obj.__class__, instance=obj, created=True)
        return ret

    def bulk_update(self, objs, fields, **kwargs):
        ret = super().bulk_update(objs, fields, **kwargs)
        for obj in objs:
            models.signals.post_save.send(obj.__class__, instance=obj, created=False)
        return ret
