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
import logging

from django.conf import settings

# Project imports
from apps.common.models import AppVar

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.7/LICENSE"
__version__ = "1.1.7"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def init_app_vars():
    """
    Collect existing project variables from all app_vars.py modules into db
    """
    logging.info('Going to Collect existing project variables from all app_vars.py modules into db')
    custom_apps = [i for i in settings.INSTALLED_APPS if i.startswith('apps.')]
    for app_name in custom_apps:
        module_str = '%s.app_vars' % app_name
        try:
            _ = importlib.import_module(module_str)
            print('Initiated App Vars from module {}'.format(module_str))
        except ImportError:
            continue


TRACK_API = AppVar.set(
    'track_api', False,
    'Enables/disables tracking API request processing time. Values: true / false.')
TRACK_API_GREATER_THAN = AppVar.set(
    'track_api_greater_than', 250,
    'If API request processing time is enabled then the requests '
    'longer than this value in ms will be tracked. Values: milliseconds')
