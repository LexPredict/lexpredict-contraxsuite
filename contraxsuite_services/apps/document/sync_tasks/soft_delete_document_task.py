from typing import List
from apps.document.repository.base_document_repository import BaseDocumentRepository
from apps.document.repository.document_repository import default_document_repository


class SoftDeleteDocumentsSyncTask:
    def __init__(self, doc_repo: BaseDocumentRepository=None):
        self.doc_repo = doc_repo or default_document_repository

    def process(self, document_ids: List[int], delete_not_undelete: bool) -> int:
        self.doc_repo.set_documents_soft_delete_flag(document_ids, delete_not_undelete)
        from apps.document import signals
        signals.fire_doc_soft_delete('SoftDeleteDocumentsSyncTask', document_ids, delete_not_undelete)
        return len(document_ids)
