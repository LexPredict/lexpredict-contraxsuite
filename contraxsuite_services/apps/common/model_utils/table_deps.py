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

from typing import List

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DependencyRecord:
    def __init__(self, own_table: str = '', ref_key: str = '', ref_table: str = '', ref_table_pk: str = ''):
        self.own_table = own_table
        self.ref_table = ref_table
        self.ref_key = ref_key
        self.ref_table_pk = ref_table_pk

    def __repr__(self):
        return f'{self.own_table}.{self.ref_key} -> {self.ref_table}.{self.ref_table_pk}'


class TableDeps:
    """
    Class represents table dependencies chain, build on foreign key references
    Used in bulk delete procedure
    """
    def __init__(self, start_dep):
        self.own_table_pk = []  #type:List[str]
        if start_dep:
            self.own_table_pk = start_dep.own_table_pk
            self.deps = start_dep.deps[:]
            return
        self.deps = []  # type: List[DependencyRecord]

    def __repr__(self) -> str:
        pk_str = ','.join(self.own_table_pk)
        return f'pk:[{pk_str}], ' + ', '.join([str(d) for d in self.deps])

    @staticmethod
    def sort_deps(dep_list):
        return sorted(dep_list, key=lambda x: len(x.deps), reverse=True)

    @staticmethod
    def parse_stored_deps_multiline(text: str) -> List:
        dep_list = []
        for line in [l.strip(' ') for l in text.split('\n')]:
            if not line:
                continue
            dep = TableDeps.parse_stored_deps_line(line)
            if dep:
                dep_list.append(dep)
        return dep_list

    @staticmethod
    def parse_stored_deps_line(line: str):
        if not line.startswith('pk:['):
            return None
        parts = line.split(', ')
        if len(parts) == 0:
            return None

        td = TableDeps(None)
        td.own_table_pk = parts[0][len('pk:'):].strip('[]').split(',')
        subparts = [p.split(' -> ') for p in parts[1:]]
        rec_lists = [(p[0].split('.'), p[1].split('.')) for p in subparts]
        dep_recs = [DependencyRecord(p[0][0], p[0][1], p[1][0], p[1][1]) for p in rec_lists]

        td.deps = dep_recs
        return td
