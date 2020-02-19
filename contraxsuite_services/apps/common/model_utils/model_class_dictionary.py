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

import regex as re
from threading import Lock
from django.apps import apps
from apps.common.singleton import Singleton

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


model_class_dictionary_lock = Lock()


@Singleton
class ModelClassDictionary:
    DEPRECATED_CLASS_NAMES = re.compile(r'^SoftDelete')

    def __init__(self) -> None:
        super().__init__()
        with model_class_dictionary_lock:
            self.models = []
            self.table_by_model = {}
            self.model_by_table = {}
            self.read_models()
            self.reg_name_parts = re.compile(r"[A-Z_]+[a-z0-9]+")

    def read_models(self) -> None:
        self.models = apps.get_models(include_auto_created=True, include_swapped=True)
        for model in self.models:
            if self.DEPRECATED_CLASS_NAMES.match(model.__name__):
                continue
            self.table_by_model[model] = model._meta.db_table
            self.model_by_table[self.table_by_model[model]] = model
        return

    def get_model_class_name(self, table_name: str) -> str:
        return self.model_by_table[table_name].__name__

    def get_model_class_name_hr(self, table_name: str) -> str:
        name = self.get_model_class_name(table_name)
        matches = [i.group(0) for i in self.reg_name_parts.finditer(name)]
        return ' '.join(matches)
