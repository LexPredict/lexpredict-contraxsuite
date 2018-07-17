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

import importlib

from django.conf.urls import include

import settings

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.1c/LICENSE"
__version__ = "1.1.1c"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

DOCUMENT_FIELDS = {}


def document_class_by_name(document_class_name: str):
    fields = DOCUMENT_FIELDS.get(document_class_name)
    if not fields:
        return None
    for field_config in fields.values():
        return field_config.document_class


def _init_document_fields():
    custom_apps = [i.replace('apps.', '') for i in settings.INSTALLED_APPS if i.startswith('apps.')]
    for app_name in custom_apps:
        module_str = 'apps.%s.document_fields' % app_name
        spec = importlib.util.find_spec(module_str)
        if not spec:
            continue
        include_fields = include(module_str, namespace=app_name)

        try:
            app_document_fields = include_fields[0].__getattribute__('DOCUMENT_FIELDS')
        except AttributeError:
            continue

        for field_config in app_document_fields:
            doc_class = field_config.document_class
            doc_class_name = '{0}.{1}'.format(app_name, doc_class.__name__)
            field = field_config.field
            doc_class_fields = DOCUMENT_FIELDS.get(doc_class_name)
            if not doc_class_fields:
                doc_class_fields = {}
                DOCUMENT_FIELDS[doc_class_name] = doc_class_fields
            doc_class_fields[field] = field_config


_init_document_fields()
