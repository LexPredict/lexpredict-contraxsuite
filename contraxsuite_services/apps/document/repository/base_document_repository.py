from typing import List


class BaseDocumentRepository:

    def get_all_document_source_paths(self, ids: List[int]) -> List[str]:
        raise NotImplemented()

    def delete_all_documents_by_ids(self, ids: List[int]) -> None:
        raise NotImplemented()

    def delete_document_history_by_ids(self, ids: List[int]) -> None:
        raise NotImplemented()

    def set_documents_soft_delete_flag(self, document_ids: List[int], delete_not_undelete: bool) -> None:
        raise NotImplemented()

    def get_project_document_ids(self, project_id: str) -> List[int]:
        raise NotImplemented()