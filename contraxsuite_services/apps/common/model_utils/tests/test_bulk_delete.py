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
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import List

from apps.common.model_utils.table_deps import TableDeps, DependencyRecord
from tests.django_test_case import DjangoTestCase
from apps.common.model_utils.table_deps_builder import TableDepsBuilder


class TestBulkDelete(DjangoTestCase):
    def non_test_document(self):
        deps = TableDepsBuilder().build_table_dependences('document_document')
        dep_names = self.deps_to_table_names(deps)
        self.assertLess(dep_names.index('document_fieldannotation'),
                        dep_names.index('document_textunit'))
        self.assertLess(dep_names.index('extract_termusage'),
                        dep_names.index('document_textunit'))
        self.assertLess(dep_names.index('document_textunittext'),
                        dep_names.index('document_textunit'))

        # there are 2 document references in analyze_documentsimilarity
        self.assertEqual(2, sum(1 for d in dep_names if d == 'analyze_documentsimilarity'))

    def test_dependency_order(self):
        # b depends on (a), f: (d, e), d: (b), g: (f)
        deps = [TableDeps(None), TableDeps(None), TableDeps(None), TableDeps(None)]
        deps[0].deps = [DependencyRecord('b', 'rid', 'a', 'id')]
        deps[1].deps = [DependencyRecord('f', 'rid', 'd', 'id'),
                        DependencyRecord('d', 'rid', 'a', 'id')]
        deps[2].deps = [DependencyRecord('d', 'rid', 'b', 'id'),
                        DependencyRecord('b', 'rid', 'a', 'id')]
        deps[3].deps = [DependencyRecord('g', 'rid', 'f', 'id'),
                        DependencyRecord('f', 'rid', 'd', 'id'),
                        DependencyRecord('d', 'rid', 'a', 'id')]

        relations = [
            ('b', '', 'a', ''),
            ('f', '', 'd', ''),
            ('f', '', 'e', ''),
            ('d', '', 'b', ''),
            ('g', '', 'f', '')
        ]

        deps = TableDeps.sort_deps(deps, relations)
        dep_names = ''.join(self.deps_to_table_names(deps))
        self.assertEqual('gfdb', dep_names)

    def test_dependency_loops(self):
        deps = {'a': {'b', 'c'}, 'c': {}, 'b': {'c'}}
        self.assertFalse(TableDeps.check_loops_in_deps(deps))
        deps = {'a': {'b', 'c'}, 'c': {}, 'b': {'a'}}
        self.assertTrue(TableDeps.check_loops_in_deps(deps))

    @classmethod
    def deps_to_table_names(cls, deps: List[TableDeps]):
        return [d.deps[0].own_table for d in deps]
