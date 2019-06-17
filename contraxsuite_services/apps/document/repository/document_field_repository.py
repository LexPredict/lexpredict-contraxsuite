from typing import Dict, Any, List, Generator, Iterable

from apps.document.models import Document, DocumentType


class DocumentFieldRepository:
    def get_document_fields_hash(self, doc: Document) -> Dict[str, Any]:
        raise NotImplemented()

    def get_doc_field_values_by_uid(self, doc: Document) -> Dict[str, Any]:
        raise NotImplemented()

    def get_project_documents_field_values_by_uid(self,
                                          project_ids: List[int],
                                          max_count: int,
                                          doc_type: DocumentType) -> Generator[Dict[str, Any], None, None]:
        raise NotImplemented()

    def get_documents_field_values_by_uid(self, documents: Iterable[Document]) \
            -> Generator[Dict[str, Any], None, None]:
        raise NotImplemented()