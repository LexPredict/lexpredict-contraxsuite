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

from apps.common.models import AppVar
from apps.rawdb.constants import APP_VAR_DISABLE_RAW_DB_CACHING_NAME

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def validate_priority(value):
    if value < 0 or value > 9:
        raise RuntimeError('Value should belong to [0..9]')


APP_VAR_DISABLE_RAW_DB_CACHING = AppVar.set(
    'RawDB', APP_VAR_DISABLE_RAW_DB_CACHING_NAME, False,
    'Disables automatic caching of documents into raw db tables '
    'when document type / document field structures are changed '
    'via the admin app or when a document is loaded / changed. '
    'Values: true / false (json)')

APP_VAR_RAW_DB_REINDEX_PACK_SIZE = AppVar.set(
    'RawDB', 'app_var_raw_db_reindex_pack_size', 100,
    'Count of documents being cached per one Celery task. '
    '0 means unlimited count are to be processed within one task.')

APP_VAR_RAW_DB_REINDEX_PRIORITY = AppVar.set(
    'RawDB', 'app_var_raw_db_reindex_priority', 0,
    'Reindex Celery task priority from 1 (lowest) to 9 '
    '(highest). 0 means default priority (5). Setting priority above 7 is '
    'not recommended for the Reindex task, because the task would be routed '
    'to a separate high-priority worker.',
    validator=validate_priority)
