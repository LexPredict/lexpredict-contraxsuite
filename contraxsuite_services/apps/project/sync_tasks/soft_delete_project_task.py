from typing import List, Tuple
from apps.project.models import Project


class SoftDeleteProjectSyncTask:

    def process(self,
                project_id: int,
                remove_all: bool,
                excluded_ids: List[int],
                delete_not_undelete: bool) -> Tuple[int, int]:
        """
        Mark document as "soft deleted" or uncheck this flag.
        This "task" executes in the same thread unlike real celery tasks.
        :param project_id: documents' root project id
        :param remove_all: remove all documents within the project
        :param excluded_ids: document ids list
        :param delete_not_undelete: delete or uncheck "delete_pending" flag
        :return: (projects deleted, documents deleted)
        """
        project = Project.all_objects.get(pk=project_id)
        if not project:
            raise Exception(f'project pk={project_id} was not found')

        if remove_all or not delete_not_undelete:
            project.delete_pending = delete_not_undelete
            project.save()

        if delete_not_undelete and remove_all:
            return 1, 0

        from apps.document.models import Document
        doc_ids = Document.all_objects.filter(project=project_id). \
            exclude(id__in=excluded_ids).values_list('id', flat=True)

        count = Document.all_objects.filter(project=project_id).exclude(
            id__in=excluded_ids).update(delete_pending=delete_not_undelete)
        from apps.document import signals
        signals.fire_doc_soft_delete('SoftDeleteProjectSyncTask',
                                     doc_ids, delete_not_undelete)
        return 0, count
