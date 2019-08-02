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

from typing import List
from apps.analyze.models import DocumentCluster, TextUnitCluster
from apps.document.models import Document, DocumentFieldValue, TextUnitNote, DocumentNote
from apps.document.repository.base_document_repository import BaseDocumentRepository
from apps.extract.models import Party

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DocumentRepository(BaseDocumentRepository):

    def get_all_document_source_paths(self, ids: List[int]) -> List[str]:
        return list(Document.all_objects.filter(pk__in=ids).values_list('source_path', flat=True))

    def delete_all_documents_by_ids(self, ids: List[int]) -> None:
        docs_query = Document.all_objects.filter(pk__in=ids)
        if docs_query.exists():
            docs_query._raw_delete(docs_query.db)

    def delete_document_history_by_ids(self, ids: List[int]) -> None:
        DocumentFieldValue.history.filter(document_id__in=ids).delete()
        TextUnitNote.history.filter(text_unit__document_id__in=ids)
        DocumentNote.history.filter(document_id__in=ids).delete()
        Document.history.filter(pk__in=ids).delete()
        # delete empty Party and Clusters
        Party.objects.filter(partyusage__isnull=True).delete()
        DocumentCluster.objects.filter(documents__isnull=True).delete()
        TextUnitCluster.objects.filter(text_units__isnull=True).delete()

    def set_documents_soft_delete_flag(self, document_ids: List[int], delete_not_undelete: bool) -> None:
        Document.all_objects.filter(id__in=document_ids).update(delete_pending=delete_not_undelete)

    def get_project_document_ids(self, project_id: str) -> List[int]:
        return Document.all_objects.filter(project_id=project_id).values_list('id', flat=True)


default_document_repository = DocumentRepository()
