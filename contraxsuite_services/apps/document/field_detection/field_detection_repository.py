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

from typing import List, Optional

from django.db.models import QuerySet

from apps.common.singleton import Singleton
from apps.document.models import DocumentField, Document, DocumentType, FieldValue

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


@Singleton
class FieldDetectionRepository:
    def get_qs_active_modified_document_ids(self, field: DocumentField,
                                            project_ids: Optional[List[str]]) -> QuerySet:
        q = FieldValue.objects \
            .filter(field_id=field.pk, document__status__is_active=True, modified_by__isnull=False)
        if project_ids:
            q = q.filter(document__project_id__in=project_ids)
        return q.values_list('document_id', flat=True)

    def get_qs_finished_document_ids(self, document_type: DocumentType, project_ids: Optional[List[str]]) -> QuerySet:
        q = Document.objects \
            .filter(document_type=document_type, status__is_active=False)

        if project_ids:
            q = q.filter(project_id__in=project_ids)

        return q.values_list('pk', flat=True)

    def get_approved_documents_number(self, field: DocumentField, project_ids: Optional[List[str]]):
        count = len(self.get_qs_active_modified_document_ids(field, project_ids))
        count += len(self.get_qs_finished_document_ids(field.document_type, project_ids))
        return count
