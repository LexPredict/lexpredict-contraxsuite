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
from apps.document.repository.base_document_repository import BaseDocumentRepository
from apps.document.repository.document_repository import default_document_repository

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class SoftDeleteDocumentsSyncTask:
    def __init__(self, doc_repo: BaseDocumentRepository=None):
        self.doc_repo = doc_repo or default_document_repository

    def process(self, document_ids: List[int], delete_not_undelete: bool) -> int:
        self.doc_repo.set_documents_soft_delete_flag(document_ids, delete_not_undelete)
        from apps.document import signals
        signals.fire_doc_soft_delete('SoftDeleteDocumentsSyncTask', document_ids, delete_not_undelete)
        return len(document_ids)
