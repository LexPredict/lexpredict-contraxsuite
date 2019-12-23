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

from typing import List, Tuple, Dict
from django.db import connection
from apps.common.model_utils.table_deps import TableDeps, DependencyRecord

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TableDepsBuilder:
    @staticmethod
    def build_table_dependences(table_name: str) -> List[TableDeps]:
        relations = TableDepsBuilder.get_relations()
        pkeys = TableDepsBuilder.get_all_primary_keys()
        all_deps = []  # type: List[TableDeps]
        TableDepsBuilder.find_dependend_tables(relations, all_deps, None, table_name)
        all_deps = TableDeps.sort_deps(all_deps)
        for dep in all_deps:
            dep.own_table_pk = pkeys[dep.deps[0].own_table]
        return all_deps

    @staticmethod
    def find_dependend_tables(
                       relations: List[Tuple[str, str, str, str]],
                       all_deps: List[TableDeps],
                       current_dep: TableDeps,
                       table_name: str) -> None:
        for rel in relations:
            if rel[2] != table_name:
                continue

            dep_record = DependencyRecord(rel[0], rel[1], rel[2], rel[3])
            if not current_dep:
                new_dep = TableDeps(None)
                new_dep.deps = [dep_record]
            else:
                new_dep = TableDeps(current_dep)
                new_dep.deps.insert(0, dep_record)

            all_deps.append(new_dep)

            # max recursion is limited
            if len(new_dep.deps) < 6:
                TableDepsBuilder.find_dependend_tables(relations, all_deps, new_dep, dep_record.own_table)

    @staticmethod
    def get_relations() -> List[Tuple[str, str, str, str]]:
        cmd = '''        
            SELECT      
                KCU1.TABLE_NAME AS FK_TABLE_NAME 
                ,KCU1.COLUMN_NAME AS FK_COLUMN_NAME  
                ,KCU2.TABLE_NAME AS REFERENCED_TABLE_NAME 
                ,KCU2.COLUMN_NAME AS REFERENCED_COLUMN_NAME     
            FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS AS RC 

            INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS KCU1 
                ON KCU1.CONSTRAINT_CATALOG = RC.CONSTRAINT_CATALOG  
                AND KCU1.CONSTRAINT_SCHEMA = RC.CONSTRAINT_SCHEMA 
                AND KCU1.CONSTRAINT_NAME = RC.CONSTRAINT_NAME 

            INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS KCU2 
                ON KCU2.CONSTRAINT_CATALOG = RC.UNIQUE_CONSTRAINT_CATALOG  
                AND KCU2.CONSTRAINT_SCHEMA = RC.UNIQUE_CONSTRAINT_SCHEMA 
                AND KCU2.CONSTRAINT_NAME = RC.UNIQUE_CONSTRAINT_NAME 
                AND KCU2.ORDINAL_POSITION = KCU1.ORDINAL_POSITION;
        '''

        with connection.cursor() as cursor:
            cursor.execute(cmd)
            row = cursor.fetchall()
            # rel_text = '\n\n'.join([str(r) for r in row])
            # print(rel_text)
            return list(row)

    @staticmethod
    def get_all_primary_keys() -> Dict[str, List[str]]:
        pkeys = {}  # type:Dict[str, List[str]]
        cmd = '''
            SELECT c.table_name, c.column_name, c.ordinal_position
            FROM information_schema.key_column_usage AS c
            LEFT JOIN information_schema.table_constraints AS t
            ON t.constraint_name = c.constraint_name
            WHERE t.constraint_type = 'PRIMARY KEY';
            '''
        with connection.cursor() as cursor:
            cursor.execute(cmd)
            row = cursor.fetchall()
            rvals = list(row)

        for rval in rvals:
            if rval[0] in pkeys:
                pkeys[rval[0]].append(rval[1])
            else:
                pkeys[rval[0]] = [rval[1]]
        return pkeys
