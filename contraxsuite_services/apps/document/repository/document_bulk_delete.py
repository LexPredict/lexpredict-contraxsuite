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

import os
import settings
from typing import List, Dict
from apps.common.model_utils.model_bulk_delete import ModelBulkDelete
from apps.document.models import Document, TextUnit
from apps.document.repository.base_document_repository import BaseDocumentRepository
from apps.document.repository.document_repository import DocumentRepository
from apps.extract.models import TermUsage
from apps.task.models import Task
from apps.task.tasks import purge_task
from apps.common.model_utils.table_deps_builder import TableDepsBuilder

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DocumentBulkDelete:
    def __init__(self,
                 document_repository: BaseDocumentRepository,
                 safe_mode: bool = True):
        self.model_class = Document.objects.model._meta.db_table
        self.document_repository = document_repository
        self.bulk_del = self.build_model_bulk_delete(safe_mode)

    def calculate_deleting_count(self, ids: List[int], remove_empty: bool = True) -> Dict[str, int]:
        if len(ids) == 0:
            return {}
        where_clause = self.build_where_clause(ids) + ";"
        counts = self.bulk_del.calculate_total_objects_to_delete(where_clause)
        if remove_empty:
            counts = {c: counts[c] for c in counts if counts[c] > 0}
        return counts

    def delete_documents(self, ids: List[int]) -> None:
        if len(ids) == 0:
            return
        where_clause = self.build_where_clause(ids) + ");"
        self.bulk_del.delete_objects(where_clause)
        try:
            self.document_repository.delete_document_history_by_ids(ids)
        except Exception as e:
            raise RuntimeError(f'error in delete_documents.delete_document_history_by_ids({len(ids)})') from e
        try:
            self.document_repository.delete_all_documents_by_ids(ids)
        except Exception as e:
            raise RuntimeError(f'error in delete_documents.delete_all_documents_by_ids({len(ids)})') from e

    def build_where_clause(self, ids: List[int]) -> str:
        if len(ids) > 1:
            ids_str = ','.join([str(id) for id in ids])
            where_clause = f'\n  WHERE "{self.model_class}"."id" IN ({ids_str})'
        else:
            where_clause = f'\n  WHERE "{self.model_class}"."id" = {ids[0]}'
        return where_clause

    def delete_files(self, ids: List[int]) -> None:
        paths = self.document_repository.get_all_document_source_paths(ids)
        for path in paths:
            file_path = os.path.join(
                settings.MEDIA_ROOT,
                settings.FILEBROWSER_DOCUMENTS_DIRECTORY,
                path)
            try:
                os.remove(file_path)
            except OSError:
                pass

    @staticmethod
    def purge_tasks(ids: List[int]):
        upload_session_ids = Document.all_objects.filter(pk__in=ids).values_list('upload_session_id', flat=True)
        doc_names = Document.all_objects.filter(pk__in=ids).values_list('name', flat=True)
        doc_names_hash = dict((key, True) for key in doc_names)

        file_tasks = Task.objects.filter(metadata__file_name__in=doc_names, upload_session_id__in=upload_session_ids)
        for file_task in file_tasks:
            if file_task.metadata.get('file_name') in doc_names_hash:
                purge_task(file_task.id)

    def build_model_bulk_delete(self,
                                safe_mode: bool = True):
        deps = TableDepsBuilder.build_table_dependences(self.model_class)
        return ModelBulkDelete(deps, safe_mode,
                               {TermUsage.objects.model._meta.db_table,
                                TextUnit.objects.model._meta.db_table})


def get_document_bulk_delete(safe_mode: bool = True):
    return DocumentBulkDelete(DocumentRepository(), safe_mode)
