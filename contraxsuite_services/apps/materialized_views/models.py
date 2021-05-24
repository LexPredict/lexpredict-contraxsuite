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

# Standard imports

# Django imports
from django.db import models

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class MaterializedViewRefreshRequest(models.Model):
    view_name = models.CharField(max_length=100, db_index=True)

    request_date = models.DateTimeField(auto_now=True, db_index=True)


class MaterializedView(models.Model):
    view_name = models.CharField(max_length=100, db_index=True, unique=True)

    refresh_date = models.DateTimeField(auto_now=False, db_index=True)

    VIEW_STATUS_CREATED = 'CREATED'
    VIEW_STATUS_UPDATING = 'UPDATING'
    VIEW_STATUS_UPDATED = 'UPDATED'

    VIEW_STATUSES = ((VIEW_STATUS_CREATED, VIEW_STATUS_CREATED,),
                     (VIEW_STATUS_UPDATING, VIEW_STATUS_UPDATING,),
                     (VIEW_STATUS_UPDATED, VIEW_STATUS_UPDATED,))

    status = models.CharField(max_length=10,
                              choices=VIEW_STATUSES,
                              default=VIEW_STATUS_CREATED)
