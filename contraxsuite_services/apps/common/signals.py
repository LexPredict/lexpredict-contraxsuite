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
import django.dispatch

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from django.db.models import QuerySet
from django.db.models.signals import ModelSignal

review_status_saved = django.dispatch.Signal(providing_args=['instance', 'old_instance'])

# pylint: disable=invalid-name
pre_create = ModelSignal(providing_args=["kwargs"], use_caching=True)
post_create = ModelSignal(providing_args=["kwargs"], use_caching=True)
pre_update = ModelSignal(providing_args=["queryset", "kwargs"], use_caching=True)
post_update = ModelSignal(providing_args=["queryset", "kwargs"], use_caching=True)
pre_bulk_create = ModelSignal(providing_args=["queryset", "kwargs"], use_caching=True)
post_bulk_create = ModelSignal(providing_args=["queryset", "created", "kwargs"], use_caching=True)

METHODS = {
    'bulk_create': QuerySet.bulk_create,
    'create': QuerySet.create,
    'update': QuerySet.update
}


def _bulk_create(self, objs, batch_size=None, ignore_conflicts=False, **kwargs):
    bulk_create_method = METHODS['bulk_create']
    pre_bulk_create.send(sender=self.model, queryset=objs, kwargs=kwargs)
    try:
        instances = bulk_create_method(self, objs, batch_size, ignore_conflicts)
    except ValueError:
        instances = None
    post_bulk_create.send(sender=self.model, queryset=instances,
                          created=bool(instances), kwargs=kwargs)
    return instances


def _create(self, **kwargs):
    create_method = METHODS['create']
    pre_create.send(sender=self.model, kwargs=kwargs)
    try:
        instance = create_method(self, **kwargs)
    except ValueError:
        instance = None
    post_create.send(sender=self.model, kwargs=kwargs)
    return instance


def _update(self, **kwargs):
    update_method = METHODS['update']
    pre_update.send(sender=self.model, queryset=self, kwargs=kwargs)
    updated_rows_count = update_method(self, **kwargs)
    post_update.send(sender=self.model, queryset=self, kwargs=kwargs)
    return updated_rows_count


QuerySet.bulk_create = _bulk_create
QuerySet.create = _create
QuerySet.update = _update
