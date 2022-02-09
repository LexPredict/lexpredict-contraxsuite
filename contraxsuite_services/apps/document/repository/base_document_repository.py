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

from typing import List, Tuple
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class BaseDocumentRepository:

    def get_all_document_source_paths(self, ids: List[int]) -> List[str]:
        raise NotImplementedError()

    def get_document_source_paths_by_id(self,
                                        ids: List[int]) -> List[Tuple[int, str]]:
        raise NotImplementedError()

    def delete_all_documents_by_ids(self, ids: List[int], user: User = None) -> None:
        raise NotImplementedError()

    def delete_document_history_by_ids(self, ids: List[int]) -> None:
        raise NotImplementedError()

    def set_documents_soft_delete_flag(self, document_ids: List[int], delete_not_undelete: bool) -> None:
        raise NotImplementedError()

    def get_project_document_ids(self, project_id: str) -> List[int]:
        raise NotImplementedError()
