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
from typing import Dict, List

from apps.common.plugins import collect_plugins_in_apps
from apps.document.python_coded_fields import PythonCodedField

# Registry of Python-coded fields in the form of: code -> PythonCodedField descendant instance.
# DocumentField.python_coded_field can have one of field codes as its value.
# In this case field values will be detected using the methods of PythonCodedField descendant registered in
# this dictionary.

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


PYTHON_CODED_FIELDS_REGISTRY = {}  # type: Dict[str, PythonCodedField]


def init_field_registry():
    """
    Searches for module called 'python_coded_fields' in each app. If there is such module and it has
    'PYTHON_CODED_FIELDS' list attribute in it then try to add each field from this list to
    PYTHON_CODED_FIELDS_REGISTRY.
    Additionally updates choice values of DocumentField.python_coded_field model.
    :return:
    """
    logging.info('Going to register Python-coded document fields from all Django apps...')

    plugins = collect_plugins_in_apps('python_coded_fields',
                                      'PYTHON_CODED_FIELDS')  # type: Dict[str, List[PythonCodedField]]
    for app_name, fields in plugins.items():
        try:
            fields = list(fields)
        except TypeError:
            raise TypeError('{0}.python_coded_fields.PYTHON_CODED_FIELDS is not iterable'.format(app_name))

        i = -1
        for field in fields:
            i += 1
            try:
                PYTHON_CODED_FIELDS_REGISTRY[field.code] = field
            except AttributeError:
                raise AttributeError('{0}.python_coded_fields.PYTHON_CODED_FIELDS[{1}] is something wrong'
                                     .format(app_name, i))
            print('Registered python-coded document field: {0} ({1})'.format(field.title, field.code))

    from apps.document.models import DocumentField
    for f in DocumentField._meta.fields:
        if f.name == 'python_coded_field':
            f.choices = list((k, PYTHON_CODED_FIELDS_REGISTRY[k].title or k)
                             for k in sorted(PYTHON_CODED_FIELDS_REGISTRY))
            break
