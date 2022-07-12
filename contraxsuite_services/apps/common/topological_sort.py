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
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Tuple, Any, Iterable, Set, List, Dict
from collections import OrderedDict


class TopologicalNode:
    def __init__(self,
                 name: Any,
                 dependencies: Set[Any] = None,
                 is_hidden: bool = False):
        self.name = name
        self.dependencies = dependencies or set()
        self.is_hidden = is_hidden

    def __repr__(self):
        deps = ', '.join([str(d) for d in self.dependencies])
        s = f'{self.name}: [{deps}]'
        if self.is_hidden:
            s += ', hidden'
        return s


class TopologicalGraph:
    def __init__(self, items: Iterable[Tuple[Any, Iterable[Any]]]):
        self.graph = OrderedDict()  # type: OrderedDict[Any, TopologicalNode]
        for item in items:
            if item[0] in self.graph:
                node = self.graph[item[0]]
                node.is_hidden = False
                node.dependencies.update(item[1])
            else:
                node = TopologicalNode(item[0], set(item[1] or []))
                self.graph[item[0]] = node
            for dp in item[1]:
                if dp not in self.graph:
                    node = TopologicalNode(dp, None, True)
                    self.graph[dp] = node

    def topological_sort(self):
        visited = {k: False for k in self.graph}
        stack = []
        for k in visited:
            if not visited[k]:
                self.topological_sort_util(k, visited, stack)

    def to_tuple_list(self, show_hidden=False) -> List[Tuple[Any, List[Any]]]:
        src = self.graph if show_hidden else [k for k in self.graph if not self.graph[k].is_hidden]
        return [(k, list(self.graph[k].dependencies)) for k in src]

    def topological_sort_util(self, v: Any, visited: Dict[Any, bool], stack: List[Any]):
        visited[v] = True
        for i in self.graph[v].dependencies:
            if not visited[i]:
                self.topological_sort_util(i, visited, stack)
        stack.insert(0, v)


def topological_sort(items: Iterable[Tuple[Any, Iterable[Any]]]) -> List[Tuple[Any, List[Any]]]:
    graph = TopologicalGraph(items)
    graph.topological_sort()
    return graph.to_tuple_list()
