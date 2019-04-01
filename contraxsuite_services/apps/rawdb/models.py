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

from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from apps.document.models import DocumentType
from apps.project.models import Project
from apps.users.models import User
from apps.rawdb.constants import FT_COMMON_FILTER, FT_USER_DOC_GRID_CONFIG

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.0/LICENSE"
__version__ = "1.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class SavedFilter(models.Model):
    FILTER_TYPE_CHOICES = [
        (FT_COMMON_FILTER, 'Common Filter'),
        (FT_USER_DOC_GRID_CONFIG, 'User Document Grid Config')
    ]

    filter_type = models.CharField(max_length=50, blank=False, null=False, default=FT_COMMON_FILTER,
                                   choices=FILTER_TYPE_CHOICES)

    title = models.CharField(max_length=1024, blank=True, null=True)

    display_order = models.PositiveSmallIntegerField(default=0)

    project = models.ForeignKey(Project, null=True, blank=True, db_index=True)

    document_type = models.ForeignKey(DocumentType, null=False, blank=False, db_index=True)

    user = models.ForeignKey(User, blank=True, null=True, db_index=True)

    # filter_sql = models.TextField(blank=True, null=True)

    columns = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)

    column_filters = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)

    order_by = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)
