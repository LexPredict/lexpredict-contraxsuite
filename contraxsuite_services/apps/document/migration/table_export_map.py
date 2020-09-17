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
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import math
from typing import List, Dict, Any, Callable, Optional
import numpy as np
import pandas as pd
from django.db import IntegrityError, connection

from apps.common.singleton import Singleton


class TableExportMap:
    def __init__(self,
                 table_name: str,
                 columns: Optional[List[str]] = None,
                 where_clause: Optional[str] = None):
        self.table_name = table_name
        self.columns = columns or []
        self.where_clause = where_clause

    def __repr__(self):
        return f'select ... from {self.table_name} where {self.where_clause}'

    def build_select_query(self, document_ids: List[int]):
        ids_str = ','.join([str(id) for id in document_ids])
        where_clause = self.where_clause.replace('{document_ids}', ids_str)
        column_query = ', '.join([f'"{c}"' for c in self.columns])
        return f'select {column_query} from "{self.table_name}" {where_clause}'

    def df_row_to_dict(self, row) -> Dict[str, Any]:
        values = {}
        for cl in self.columns:
            row_val = row[cl]
            if row_val == '\\N':
                row_val = None
            if row_val == np.nan or row_val == math.nan:
                row_val = None
            values[cl] = row_val
        return values

    def import_values_from_df(self,
                              read_dataframe: Callable[[str], pd.DataFrame],
                              log_info: Callable[[str], None],
                              build_entity_record: Callable[[Dict[str, Any]], Any],
                              on_record_saved: Optional[Callable[[Any, Dict[str, Any]], None]] = None) -> None:
        df = read_dataframe(f'{self.table_name}.zip')
        log_info(f'Importing {df.shape[0]} {self.table_name} records')
        already_imported = 0
        for _, row in df.iterrows():
            row_values = self.df_row_to_dict(row)
            entity = build_entity_record(row_values)
            if entity:
                try:
                    entity.save()
                    if on_record_saved:
                        on_record_saved(entity, row_values)
                except IntegrityError as e:
                    if e.args[0].startswith('duplicate'):
                        already_imported += 1
                        continue
                    raise
            else:
                already_imported += 1
        if already_imported:
            log_info(f'{already_imported} of {df.shape[0]} {self.table_name} ' +
                     'records were already imported')

    def read_default_columns(self, cursor) -> None:
        sql = f"select column_name from information_schema.columns " +\
              f"where table_name = '{self.table_name}';"  # data_type
        cursor.execute(sql)
        for row in cursor.fetchall():
            self.columns.append(row[0])

    def iterate_dataframe(self, df: pd.DataFrame):
        for _, row in df.iterrows():
            values = self.df_row_to_dict(row)
            yield values


@Singleton
class TableExportMapCollection:
    def __init__(self):
        self.mappings = [
            TableExportMap('document_documenttype', ['uid', 'code'], ''),
            TableExportMap('document_documentfield', ['uid', 'code', 'document_type_id'], ''),

            TableExportMap('project_project',
                           where_clause='p where exists(select id from document_document ' +
                                        'd where d.project_id = p.id and d.id in ({document_ids}))'),
            TableExportMap('document_document',  # skip: assignee_id, upload_session_id
                           where_clause='where id in ({document_ids})'),
            TableExportMap('document_fieldvalue'),  # skip: modified_by_id
            TableExportMap('document_documentmetadata'),
            TableExportMap('document_documenttext'),
            TableExportMap('document_fieldannotation'),
            TableExportMap('document_textunit'),
            TableExportMap('document_textunittext',
                           where_clause='p where exists(select id from document_textunit d ' +\
                           'where d.id = p.text_unit_id and d.document_id in ({document_ids}))'),
            TableExportMap('document_documentnote'),
            TableExportMap('document_documentproperty'), # 'created_by_id', 'modified_by_id',
            TableExportMap('document_documentrelation',
                           where_clause='where document_a_id in ({document_ids}) ' +
                                        'and document_b_id in ({document_ids})'),
            TableExportMap('document_documenttable'),
            TableExportMap('document_documenttag'),
            TableExportMap('document_documentpage'),
            TableExportMap('document_fieldannotationfalsematch'),
            TableExportMap('document_textunitnote',
                           where_clause='p where exists(select id from document_textunit d ' +\
                           'where d.id = p.text_unit_id and d.document_id in ({document_ids}))'),
            TableExportMap('document_textunitproperty',
                           where_clause='p where exists(select id from document_textunit d ' + \
                           'where d.id = p.text_unit_id and d.document_id in ({document_ids}))'),
            TableExportMap('document_textunitrelation',
                           where_clause='p where exists(select id from document_textunit d ' + \
                           'where (d.id = p.text_unit_a_id or d.id = p.text_unit_b_id) ' + \
                           'and d.document_id in ({document_ids}))'),
            TableExportMap('document_textunittag',
                           where_clause='p where exists(select id from document_textunit d ' + \
                           'where d.id = p.text_unit_id and d.document_id in ({document_ids}))'),
        ]
        default_where_clause = 'where document_id in ({document_ids})'
        with connection.cursor() as cursor:
            for mapping in self.mappings:
                if not mapping.columns:
                    mapping.read_default_columns(cursor)
                if mapping.where_clause is None:
                    mapping.where_clause = default_where_clause

        self.mapping_by_table = {m.table_name: m for m in self.mappings}
