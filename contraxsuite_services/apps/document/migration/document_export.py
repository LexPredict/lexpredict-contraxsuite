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


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import io
import tempfile
import zipfile
from shutil import rmtree
from typing import List, Callable, Optional
import os
import pandas as pd
from django.db import connection

from apps.common.file_storage import get_file_storage
from apps.document.migration.table_export_map import TableExportMapCollection, TableExportMap
from apps.document.repository.document_repository import default_document_repository


class DocumentExporter:
    def __init__(self, log_msg: Optional[Callable[[str], None]] = None):
        self.target_path = ''
        self.mappings = TableExportMapCollection()
        self.document_repository = default_document_repository
        self.log_msg = log_msg

    def in_memory_export(self,
                         ids: List[int],
                         temp_folder: str,
                         export_files: bool) -> io.BytesIO:
        temp_dir = ''
        if not temp_folder:
            temp_dir = tempfile.mkdtemp()
            temp_folder = temp_dir
        try:
            self.export(ids, temp_folder)
            if export_files:
                self.export_document_files(ids, temp_folder)
            mem_stream = io.BytesIO()
            with zipfile.ZipFile(mem_stream, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for name_only in os.listdir(temp_folder):
                    fn = os.path.join(temp_folder, name_only)
                    if not os.path.isfile(fn):
                        continue
                    zip_file.write(fn, arcname=name_only)
            return mem_stream
        finally:
            if temp_dir:
                rmtree(temp_dir)

    def export(self, ids: List[int], target_path: str):
        self.target_path = target_path
        all_mappings = self.mappings.mappings

        for table_map in all_mappings:
            select_query = table_map.build_select_query(ids)
            self.export_filtered_table(table_map, select_query)

    def export_document_files(self, ids: List[int], target_path: str):
        storage = get_file_storage()
        file_paths = self.document_repository.get_document_source_paths_by_id(ids)
        for doc_id, file_path in file_paths:
            if not file_path:
                self.log_message(f"Document #{doc_id} doesn't have a link to the original file")
                continue
            doc_file_name = os.path.basename(file_path)
            new_name = f'{doc_id}_{doc_file_name}'
            target_filepath = os.path.join(target_path, new_name)
            try:
                doc_stor_path = storage.sub_path_join(storage.documents_path, file_path)
                file_obj = storage.read(doc_stor_path)
                if not file_obj:
                    self.log_message(f'Exporting document file "{file_path}" was not found')
                    continue
                with open(target_filepath, 'wb') as fw:
                    fw.write(file_obj)
            except Exception as e:
                self.log_message(f'Error storing "{doc_file_name}": {e}')

    def export_filtered_table(self,
                              source_mapping: TableExportMap,
                              select_query: str):
        dest_path = os.path.join(self.target_path, f'{source_mapping.table_name}.zip')
        df = pd.read_sql(select_query, connection, columns=source_mapping.columns)
        df.to_pickle(dest_path)

    def log_message(self, msg: str):
        if self.log_msg:
            self.log_msg(msg)
