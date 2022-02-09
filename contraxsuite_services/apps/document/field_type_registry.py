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

import logging
from typing import Dict, Type, Iterable

from apps.common.plugins import collect_plugins_in_apps
from apps.document.field_types import TypedField

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


FIELD_TYPE_REGISTRY = {}  # type: Dict[str, Type[TypedField]]


def init_field_type_registry():
    """
    Searches for module called 'python_coded_fields' in each app. If there is such module and it has
    'PYTHON_CODED_FIELDS' list attribute in it then try to add each field from this list to
    PYTHON_CODED_FIELDS_REGISTRY.
    Additionally updates choice values of DocumentField.python_coded_field model.
    :return:
    """
    logging.info('Going to register Python-coded document fields from all Django apps...')

    plugins = collect_plugins_in_apps('field_types',
                                      'FIELD_TYPES')  # type: Dict[str, Iterable[Type[TypedField]]]
    for app_name, field_types in plugins.items():
        try:
            field_types = list(field_types)
        except TypeError:
            raise TypeError('{0}.field_types.FIELD_TYPES is not iterable'.format(app_name))

        i = -1
        for field_type in field_types:
            i += 1
            try:
                FIELD_TYPE_REGISTRY[field_type.type_code] = field_type
            except AttributeError:
                raise AttributeError('{0}.field_types.FIELD_TYPES[{1}] is something wrong'
                                     .format(app_name, i))
            print('Registered field type: {0} ({1})'.format(field_type.title, field_type.type_code))

    from apps.document.models import DocumentField
    for f in DocumentField._meta.fields:
        if f.name == 'type':
            f.choices = list((k, FIELD_TYPE_REGISTRY[k].title or k)
                             for k in sorted(FIELD_TYPE_REGISTRY))
            break
