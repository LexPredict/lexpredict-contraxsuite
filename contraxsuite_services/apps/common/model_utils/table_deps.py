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

from typing import List, Dict, Set, Tuple

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
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

    def stringify(self) -> str:
        return f'{self.own_table};{self.ref_key};{self.ref_table};{self.ref_table_pk}'


class TableDeps:
    """
    Class represents table dependencies chain, build on foreign key references
    Used in bulk delete procedure
    """
    def __init__(self, start_dep):
        self.own_table_pk = []  # type:List[str]
        if start_dep:
            self.own_table_pk = start_dep.own_table_pk
            self.deps = start_dep.deps[:]
            return
        self.deps = []  # type: List[DependencyRecord]

    def __repr__(self) -> str:
        pk_str = ','.join(self.own_table_pk)
        return f'pk:[{pk_str}], ' + ', '.join([str(d) for d in self.deps])

    def stringify(self) -> str:
        return '; '.join([d.stringify() for d in self.deps])

    @staticmethod
    def remove_duplicates(dep_list: 'List[TableDeps]') -> 'List[TableDeps]':
        uniq_dict = {x.stringify(): x for x in dep_list}
        return list(uniq_dict.values())

    @staticmethod
    def leave_shortest_chains(dep_list: 'List[TableDeps]') -> 'List[TableDeps]':
        shortest = []
        ln = 1000  # no chain could be so long
        for dep in dep_list:
            if len(dep.deps) > ln:
                continue
            if len(dep.deps) == ln:
                shortest.append(dep)
                continue
            shortest = [dep]
            ln = len(dep.deps)
        return shortest

    @staticmethod
    def sort_deps(dep_list: 'List[TableDeps]',
                  relations: List[Tuple[str, str, str, str]]) -> 'List[TableDeps]':
        dep_list.sort(key=lambda x: len(x.deps), reverse=True)
        # { a: { b, f }, b: ... } - table a depends on b and f
        table_deps: Dict[str, Set[str]] = {}
        for a, _, b, __ in relations:
            if a not in table_deps:
                table_deps[a] = {b}
            else:
                table_deps[a].add(b)

        while True:
            are_ordered = True
            for i in range(len(dep_list)):
                for j in range(i + 1, len(dep_list)):
                    # if subsequent table depends on one of the previous tables
                    # swap these tables
                    tab_a = dep_list[i].deps[0].own_table
                    tab_b = dep_list[j].deps[0].own_table
                    tab_b_deps = table_deps.get(tab_b)
                    if tab_b_deps and tab_a in tab_b_deps:
                        are_ordered = False
                        deps_a = dep_list[i]
                        dep_list[i] = dep_list[j]
                        dep_list[j] = deps_a
            if are_ordered:
                break
        return dep_list

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
