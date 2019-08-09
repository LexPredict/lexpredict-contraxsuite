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

import importlib
from typing import Dict, Any

from django.conf import settings

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def collect_plugins_in_apps(module_name: str, module_attr: str) -> Dict[str, Any]:
    """
    Searches for [module_name].py in each app. If there is such module and it has
    [module_attr] attribute in it then add it to the resulting dictionary with key = application name.

    This way we can provide a pluggable architecture for various subsystems.
    For example:
        Documents app searches for "python_coded_fields.py" in each available app.
        It takes PYTHON_CODED_FIELDS list from each found module and puts fields from it in the
        big field registry.
    """
    res = dict()
    custom_apps = [i for i in settings.INSTALLED_APPS if i.startswith('apps.')]
    for app_name in custom_apps:
        module_str = '{0}.{1}'.format(app_name, module_name)
        try:
            app_module = importlib.import_module(module_str)
            if hasattr(app_module, module_attr):
                plugin = getattr(app_module, module_attr)
                res[app_name] = plugin
        except ImportError:
            continue

    return res
