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
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

from typing import Dict, List, Any

from apps.document.scheme_migrations.base_scheme_migration import BaseSchemeMigration


class FieldCategoryDocTypeMigration(BaseSchemeMigration):
    def __init__(self):
        super().__init__(75, migration_project='document', migration_number=202)

    def upgrade_doctype_json(self, rows_by_model: Dict[str, List[Dict[str, Any]]]) -> \
            Dict[str, List[Dict[str, Any]]]:
        fields = rows_by_model.get('document.documentfield')
        type_by_cat = {f['fields']['category']: f['fields']['document_type'] for f in fields}

        categories = rows_by_model.get('document.documentfieldcategory') or []
        # add document_type
        for doc_cat in categories:
            cat_id = doc_cat['pk']
            if cat_id in type_by_cat:
                doc_cat['fields']['document_type'] = type_by_cat[cat_id]
        return rows_by_model

    def downgrade_doctype_json(self, rows_by_model: Dict[str, List[Dict[str, Any]]]) -> \
            Dict[str, List[Dict[str, Any]]]:
        categories = rows_by_model.get('document.documentfieldcategory') or []
        # remove document_type
        for doc_cat in categories:
            del doc_cat['fields']['document_type']
        return rows_by_model


class FieldUnitCountMigration(BaseSchemeMigration):
    def __init__(self):
        super().__init__(65, migration_project='document', migration_number=196)

        def add_field(row: Dict[str, Any]) -> Dict[str, Any]:
            row['fields']['detect_limit_unit'] = 'NONE'
            return row

        def remove_field(row: Dict[str, Any]) -> Dict[str, Any]:
            del row['fields']['detect_limit_unit']
            return row

        self.forward_conversions['document.documentfield'] = add_field
        self.backward_conversions['document.documentfield'] = remove_field


class EmptyTaggedMigration(BaseSchemeMigration):
    """
    This migration just indicates the fact the resulting JSON
    file now (since #76) contains migration number in itself
    """
    def __init__(self):
        super().__init__(76, migration_project='', migration_number=0)

    def upgrade_doctype_json(self, rows_by_model: Dict[str, List[Dict[str, Any]]]):
        return rows_by_model

    def downgrade_doctype_json(self, rows_by_model: Dict[str, List[Dict[str, Any]]]):
        return rows_by_model
