from typing import List
from apps.analyze.models import DocumentCluster, TextUnitCluster
from apps.document.models import Document, DocumentFieldValue, TextUnitNote, DocumentNote
from apps.document.repository.base_document_repository import BaseDocumentRepository
from apps.extract.models import Party


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