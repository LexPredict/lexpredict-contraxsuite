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


from typing import Dict, List, Callable, Any


class BaseSchemeMigration:
    def __init__(self,
                 version: int,
                 migration_project: str = '',
                 migration_number: int = 0):
        self.version = version
        self.migration_project = migration_project
        self.migration_number = migration_number
        self.forward_conversions = {}  # type: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]]
        self.backward_conversions = {}  # type: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]]

    def upgrade_doctype_json(self, rows_by_model: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        return self.up_or_downgrade_doctype_json(rows_by_model, self.forward_conversions)

    def downgrade_doctype_json(self, rows_by_model: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        return self.up_or_downgrade_doctype_json(rows_by_model, self.backward_conversions)

    def up_or_downgrade_doctype_json(self,
                                     rows_by_model: Dict[str, List[Dict[str, Any]]],
                                     conversions: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]]) -> \
            Dict[str, List[Dict[str, Any]]]:
        for model in rows_by_model:
            conversion = conversions.get(model)
            if not conversion:
                continue
            for i in range(len(rows_by_model[model])):
                rows_by_model[model][i] = conversion(rows_by_model[model][i])
        return rows_by_model
