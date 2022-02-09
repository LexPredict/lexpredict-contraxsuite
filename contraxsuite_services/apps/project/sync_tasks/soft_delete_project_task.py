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
from apps.project.models import Project
from apps.project.signals import project_soft_deleted

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class SoftDeleteProjectSyncTask:

    def process(self,
                project_id: int,
                delete_pending: bool,
                remove_all: bool = False,
                included_ids: List[int] = [],
                excluded_ids: List[int] = []
                ) -> Tuple[int, int]:
        """
        Mark document as "soft deleted" or uncheck this flag.
        This "task" executes in the same thread unlike real celery tasks.
        :param project_id: documents' root project id
        :param delete_pending: delete or uncheck "delete_pending" flag
        :param remove_all: remove all documents within the project
        :param included_ids: document ids list to mark/unmark
        :param excluded_ids: document ids list to leave as is
        :return: (projects deleted, documents deleted)
        """
        project = Project.all_objects.get(pk=project_id)
        if not project:
            raise Exception(f'project pk={project_id} was not found')

        if remove_all or not delete_pending:
            project.delete_pending = delete_pending
            project.save()
            if delete_pending:
                project_soft_deleted.send(sender='Project marked Soft Deleted', instance=proj, user=request.user)

        if delete_pending and remove_all:
            return 1, 0

        from apps.document.models import Document
        documents = Document.all_objects.filter(project=project_id).exclude(id__in=excluded_ids)
        if included_ids:
            documents = documents.filter(id__in=included_ids)
        doc_ids = documents.values_list('id', flat=True)

        count = documents.update(delete_pending=delete_pending)
        from apps.document import signals
        signals.fire_doc_soft_delete('SoftDeleteProjectSyncTask',
                                     doc_ids, delete_pending)
        return 0, count
