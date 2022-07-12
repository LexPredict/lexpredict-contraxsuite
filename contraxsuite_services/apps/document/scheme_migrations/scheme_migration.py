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


import inspect
import json
from typing import Dict, List, Any

import apps.document.scheme_migrations.document_scheme_migration as doc_migration
from apps.common.singleton import Singleton
from apps.document.scheme_migrations.base_scheme_migration import BaseSchemeMigration


CURRENT_VERSION = 80

# since this version migration file always includes version info
TAGGED_VERSION = 76

# key is what is displayed in GUI
# value is the actual version number, see CURRENT_VERSION
MIGRATION_TAGS: Dict[str, int] = {
    'current': CURRENT_VERSION,
    '2.0': 80,
    '1.9': 79,
    '1.8 with stop words': 78,
    '1.8': 77,
    '1.7': 76,
    '1.7 w/o schema versioning': 75,
    '1.6': 65
}


@Singleton
class SchemeMigration:
    def __init__(self):
        # { 65: migration_instance, 75: migration_instance, }
        self.migrations = {}  # type: Dict[int, BaseSchemeMigration]
        self.load_migrations()

    def load_migrations(self):
        migration_classes = [m for m in inspect.getmembers(doc_migration, inspect.isclass)
                             if m[1].__module__ == 'apps.document.scheme_migrations.document_scheme_migration']
        for cl in migration_classes:
            m_obj = cl[1]()  # type: BaseSchemeMigration
            self.migrations[m_obj.version] = m_obj

    def migrate_json(self,
                     json_str: str,
                     src_version: int,
                     dest_version: int) -> str:
        if src_version == dest_version:
            return json_str
        model_records = json.loads(json_str)
        updated_records = self.migrate_model_records(model_records, src_version, dest_version)
        return json.dumps(updated_records)

    def migrate_model_records(self,
                              model_records: List[Dict[str, Any]],
                              src_version: int,
                              dest_version: int) -> List[Dict[str, Any]]:
        if src_version == dest_version:
            return model_records
        rows_by_model = self.read_rows_by_model(model_records)

        # apply migrations
        start_version_num = src_version
        end_version_num = dest_version

        direction = 1 if end_version_num > start_version_num else -1
        start_migration = start_version_num + 1 if direction > 0 else start_version_num
        end_migration = end_version_num + direction + 1 if direction > 0 else end_version_num

        for vers_num in range(start_migration, end_migration, direction):
            if vers_num not in self.migrations:
                continue

            try:
                migration = self.migrations[vers_num]
                if direction == 1:
                    rows_by_model = migration.upgrade_doctype_json(rows_by_model)
                else:
                    rows_by_model = migration.downgrade_doctype_json(rows_by_model)
            except Exception as e:
                dir_str = 'upgrading' if direction == 1 else 'downgrading'
                raise RuntimeError(f'Error {dir_str} to {vers_num}') from e

        # serialize back
        all_rows = []
        for model in rows_by_model:
            for row in rows_by_model[model]:
                all_rows.append(row)
        return all_rows

    def read_rows_by_model(self, model_records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        rows_by_model = {}
        for row in model_records:
            rows = rows_by_model.get(row['model'])
            if not rows:
                rows = []
                rows_by_model[row['model']] = rows
            rows.append(row)
        return rows_by_model
