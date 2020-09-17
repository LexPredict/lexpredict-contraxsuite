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

import datetime
import importlib
import logging
import os
from dateutil.parser import parse

from django.conf import settings

# Project imports
from apps.common.models import AppVar

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
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
    'Common', 'track_api', False,
    'Enables/disables tracking API request processing time. Values: true / false.')
TRACK_API_GREATER_THAN = AppVar.set(
    'Common', 'track_api_greater_than', 250,
    'If API request processing time is enabled then the requests '
    'longer than this value in ms will be tracked. Values: milliseconds')
TRACK_API_SAVE_SQL_LOG = AppVar.set(
    'Common', 'track_api_save_sql_log', False,
    'If API request processing time is enabled then save sql logs')
ENABLE_AUTH_TOKEN_IN_QUERY_STRING = AppVar.set(
    'Common', 'enable_auth_token_in_query_string', False,
    'Enables/disables ability to authenticate via query string param auth_token in query string'
    'in API calls. WARNING: this is insecure setting for DEV purposes only!!!')
CUSTOM_LINKS_HEADER = AppVar.set(
    'Common', 'custom_links_header', 'Custom Links',
    '', 'Title for Custom Links menu item on left sidebar..')
CUSTOM_LOGO_URL = AppVar.set(
    'Common', 'custom_logo_url', None,
    'Url to custom logo.')
USE_FULL_TEXT_SEARCH = AppVar.set(
    'Common', 'use_full_text_search', False,
    'Use full test search via tsvector for TextField model fields included into'
    ' "full_text_search" model attribute. "False" - disable, "True" - enable, "auto" - use '
    '"auto_full_text_search_cutoff" AppVar to detect whether FTS should be enabled.')
AUTO_FULL_TEXT_SEARCH_CUTOFF = AppVar.set(
    'Common', 'auto_full_text_search_cutoff', 1000000,
    'Full test search starting from N table rows (if use_full_text_search is "auto") ')
PG_FULL_TEXT_SEARCH_LOCALE = AppVar.set(
    'Common', 'pg_full_text_search_locale', 'english',
    'Default locale for PostgreSQL full text search (for to_tsvector, to_tsquery).')


def get_build_date():
    try:
        with open(os.path.join('..', settings.BASE_DIR, 'build.date'), 'r') as f:
            build_date_str_ini = f.read().strip()
            build_date_obj = parse(build_date_str_ini)
            return datetime.datetime.strftime(build_date_obj, '%Y-%m-%d %H:%M:%S %Z')
    except:
        pass


build_date = get_build_date()


BUILD_DATE = AppVar.set(
    'Common', 'build_date', build_date,
    'Backend build date.',
    overwrite=build_date is not None
)


RELEASE_VERSION = AppVar.set(
    'Common', 'release_version', settings.VERSION_NUMBER, 'Backend release version.',
    overwrite=True
)


MAX_FILES_UPLOAD = AppVar.set(
    'Common', 'max_files_upload', 10000,
    'Max amount of files to upload at once.')

MAX_FILES_UPLOAD_PARALLEL = AppVar.set(
    'Common', 'max_files_upload_parallel', 20,
    'Max amount of files to upload at once in parallel.')

SUPPORT_EMAIL = AppVar.set(
    'Common', 'support_email', 'support@contraxsuite.com',
    'Custom email address to display on html pages.')
