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

import json
from unittest import TestCase
from apps.document.scheme_migrations.scheme_migration import SchemeMigration
from tests.testutils import load_resource_document

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestSchemeMigration(TestCase):

    def test_load(self):
        sm = SchemeMigration()
        self.assertGreater(len(sm.migrations), 1)

    def test_migrate_back(self):
        jsn = load_resource_document('scheme_migrations/doc_type_v_17.json',
                                     encoding='utf-8')
        sm = SchemeMigration()
        migrated = sm.migrate_json(jsn, 76, 65)
        self.assertGreater(len(migrated), 1000)
        self.assertNotEqual(len(jsn), len(migrated))

    def test_migrate_forward(self):
        jsn = load_resource_document('scheme_migrations/doc_type_v_16.json',
                                     encoding='utf-8')
        jsn = json.dumps(json.loads(jsn)['data'])
        sm = SchemeMigration()
        migrated = sm.migrate_json(jsn, 65, 76)
        self.assertGreater(len(migrated), 1000)
        self.assertNotEqual(len(jsn), len(migrated))

        data = json.loads(migrated)
        dfc = [d for d in data if d['model'] == 'document.documentfieldcategory']
        self.assertTrue(all(['document_type' in d['fields'] for d in dfc]))
