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
from typing import List, Set, Tuple, Callable

from apps.document.models import Document

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class RenameOldDocuments:
    # 0:name - 1:index - 2:extension (with dot)
    OLD_DOC_SUFFIX = '{0} copy {1:02d}{2}'

    def __init__(self, log_msg: Callable[[str], None]):
        self.log_func = log_msg
        self.project_doc_names = set()  # type: Set[str]

    def rename_project_old_documents(self, doc_ids: List[int]) -> None:
        """
        For each document in the [doc_ids] list (all the documents
        belong to the same project):
        - Make doc's name "<old_name>old 01.<ext>"
        - If "<old_name>old 01.<ext>" is duplicated, make
        - it "<old_name>old 02.<ext>"
        # Rename both document name and document file name
        :param doc_ids: documents' PKs
        """
        if not doc_ids:
            return
        self.get_project_doc_names(doc_ids[0])

        for doc_id in doc_ids:
            self.rename_old_document(doc_id)

    def rename_old_document(self, doc_id) -> None:
        doc = Document.all_objects.get(pk=doc_id)  # type: Document
        new_name, new_path = self.make_new_doc_name(doc)
        # rename file and document itself
        from apps.common.file_storage import get_file_storage
        stor = get_file_storage()
        try:
            stor.rename_document(doc.source_path, new_path)
            self.log_func(f'ForceUnique: "{doc.source_path}" is renamed to "{new_path}"')
        except Exception as ex:
            self.log_func(f'ForceUnique: error while renaming "{doc.source_path}" to "{new_path}":\n'
                          + str(ex))
            # return  # zombie document detected
        try:
            doc.source_path = new_path
            doc.name = os.path.basename(doc.source_path)
            doc.save()
        except Exception as ex:
            msg = f'ForceUnique: error while saving renamed doc at {doc.source_path}:\n' +\
                  str(ex)
            self.log_func(msg)
            raise Exception(msg)
        try:
            # "reindex" - update document's name in cache
            from apps.rawdb.field_value_tables import update_document_name
            update_document_name(doc.pk, doc.name)
        except Exception as ex:
            msg = f'ForceUnique: error updating RawDB cache (name) {doc.name}:\n' +\
                  str(ex)
            self.log_func(msg)

    def get_project_doc_names(self, doc_id: int):
        project = Document.all_objects.filter(
            pk=doc_id).values_list('project', flat=True)[0]
        project_doc_paths = Document.all_objects.filter(
            project=project).values_list('source_path', flat=True)
        self.project_doc_names = {os.path.basename(f) for f in project_doc_paths}

    def make_new_doc_name(self, doc: Document) -> Tuple[str, str]:
        document_name = os.path.basename(doc.source_path)
        document_folder = os.path.dirname(doc.source_path)
        name, ext = os.path.splitext(document_name)
        new_name = ''
        new_path = ''

        for suffix in range(1, 999):
            new_name = RenameOldDocuments.OLD_DOC_SUFFIX.format(name, suffix, ext)
            new_path = os.path.join(document_folder, new_name)
            if new_name not in self.project_doc_names:
                break

        return new_name, new_path
