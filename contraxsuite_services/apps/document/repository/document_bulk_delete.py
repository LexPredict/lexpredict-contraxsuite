import os
import settings
from typing import List, Dict
from apps.common.model_utils.model_bulk_delete import ModelBulkDelete
from apps.document.models import Document
from apps.document.repository.base_document_repository import BaseDocumentRepository
from apps.document.repository.document_repository import DocumentRepository
from apps.task.models import Task
from apps.task.tasks import purge_task
from apps.common.model_utils.table_deps_builder import TableDepsBuilder


class DocumentBulkDelete:
    def __init__(self, document_repository: BaseDocumentRepository):
        self.model_class = Document.objects.model._meta.db_table
        self.document_repository = document_repository
        self.bulk_del = self.build_model_bulk_delete()

    def calculate_deleting_count(self, ids: List[int], remove_empty: bool = True) -> Dict[str, int]:
        if len(ids) == 0:
            return {}
        where_clause = self.build_where_clause(ids) + ";"
        counts = self.bulk_del.calculate_total_objects_to_delete(where_clause)
        if remove_empty:
            counts = {c:counts[c] for c in counts if counts[c] > 0}
        return counts

    def delete_documents(self, ids: List[int]) -> None:
        if len(ids) == 0:
            return
        where_clause = self.build_where_clause(ids) + ");"

        self.bulk_del.delete_objects(where_clause)
        self.document_repository.delete_document_history_by_ids(ids)
        self.document_repository.delete_all_documents_by_ids(ids)

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

    def build_model_bulk_delete(self):
        deps = TableDepsBuilder.build_table_dependences(self.model_class)
        return ModelBulkDelete(deps)


def get_document_bulk_delete():
    return DocumentBulkDelete(DocumentRepository())
