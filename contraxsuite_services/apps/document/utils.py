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

# Project imports
from apps.common.file_storage import get_file_storage
from apps.document.repository.document_field_repository import DocumentFieldRepository
from apps.document.repository.document_repository import DocumentRepository
from apps.task.models import Task
from apps.task.tasks import purge_task

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


file_storage = get_file_storage()


def cleanup_document_relations(document):

    # 1. delete history
    document_repo = DocumentRepository()
    field_repo = DocumentFieldRepository()
    document_repo.delete_document_history_by_ids([document.pk])
    field_repo.delete_document_history_values(document.pk)

    # INFO: skip "delete step" (set delete=False) since we clean tasks periodically now
    # 2. delete Tasks, Task history, TaskResults, child tasks
    if document.metadata and document.metadata.get('cascade_delete_tasks', True):
        task_kwargs = dict(file_name=document.name)
        if document.upload_session_id:
            task_kwargs['session_id'] = str(document.upload_session_id)
        file_tasks = Task.objects.main_tasks().filter_metadata(**task_kwargs)
        for file_task in file_tasks:
            purge_task(file_task.id, delete=False)

    # 3. Remove files
    if file_storage.document_exists(document.source_path):
        file_storage.delete_document(document.source_path)
