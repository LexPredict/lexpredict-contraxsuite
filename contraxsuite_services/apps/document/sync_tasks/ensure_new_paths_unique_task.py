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

from typing import Callable, Iterable

from apps.document.sync_tasks.document_files_cleaner import DocumentFilesCleaner
from apps.document.sync_tasks.rename_old_documents_task import RenameOldDocuments
from apps.project.models import Project

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class EnsureNewPathsUnique:

    def __init__(self, log_msg: Callable[[str], None]):
        self.log_func = log_msg

    def get_duplicated_documents(self,
                                 project: Project,
                                 file_name: str) -> Iterable[int]:
        """
        Get documents with the same name (from file_path), that already
        exists within the project (project). Returns a list of
        "key_selector" property values
        """
        return project.document_set.filter(name=file_name).values_list('pk', flat=True)

    def ensure_new_file_unique(self,
                               project: Project,
                               source_path: str,
                               doc_name: str,
                               rename_old_document: bool) -> bool:
        """
        Check that no document shares the same name and
        no file stored by the same path
        :param project: document's project
        :param source_path: file path relative to document dir, e.g.: qwer-tyui-oppa-sdfg-hjkl/document1.docx
        :param doc_name: original file name, last component, e.g.: document1.docx
        :param rename_old_document: rename existing document if names are duplicated
        :return: True if conflicts are resolved
        """
        existing_docs = list(self.get_duplicated_documents(project, doc_name))

        # check the name is unique
        if existing_docs:
            if not rename_old_document:
                self.log_func(f'ForceUnique: there are {len(existing_docs)} documents with '
                              f'name "{doc_name}" in project {project.name} (#{project.pk}) already')
                return False
            ren_task = RenameOldDocuments(self.log_func)
            self.log_func(f'ForceUnique: ensure "{doc_name}" is unique in project {project.name} (#{project.pk}): '
                          f'found "{existing_docs}"')
            ren_task.rename_project_old_documents(existing_docs)
        else:
            self.log_func(f'ForceUnique: ensure "{doc_name}" is unique in project {project.name} (#{project.pk}): '
                          f'no dups found')

        # now check that there are no files with the same name
        try:
            DocumentFilesCleaner.delete_document_files([source_path])
        except FileNotFoundError:
            self.log_func(f'ForceUnique: not found "{source_path}" while deleting file')
            pass
        except Exception as ex:
            self.log_func(f'ForceUnique: error while deleting "{source_path}":\n{ex}')
            raise ex
        return True
