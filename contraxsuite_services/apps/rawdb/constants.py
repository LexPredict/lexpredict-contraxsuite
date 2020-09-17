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

from apps.document.constants import DOCUMENT_FIELD_CODE_NAME, DOCUMENT_FIELD_CODE_TITLE, \
    DOCUMENT_FIELD_CODE_DELETE_PENDING, DOCUMENT_FIELD_CODE_FOLDER, DOCUMENT_FIELD_CODE_PROJECT_ID, \
    DOCUMENT_FIELD_CODE_PROJECT_NAME, DOCUMENT_FIELD_CODE_STATUS_NAME, DOCUMENT_FIELD_CODE_ASSIGNEE_ID, \
    DOCUMENT_FIELD_CODE_ASSIGNEE_NAME, DOCUMENT_FIELD_CODE_ASSIGN_DATE, DOCUMENT_FIELD_CODE_CLUSTER_ID, \
    DOCUMENT_FIELD_CODE_LANGUAGE, DOCUMENT_FIELD_CODE_PROCESSED, ALL_DOCUMENT_FIELD_CODES
from apps.rawdb.rawdb.query_parsing import SortDirection

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


FT_COMMON_FILTER = 'common_filter'
FT_USER_DOC_GRID_CONFIG = 'user_doc_grid_config'
APP_VAR_DISABLE_RAW_DB_CACHING_NAME = 'rawdb_doc_grid_caching_disabled'

DOC_NUM_PER_SUB_TASK = 20
DOC_NUM_PER_MAIN_TASK = 100

TABLE_NAME_PREFIX = 'doc_fields_'
FIELD_CODE_DOC_NAME = 'document_name'
FIELD_CODE_DOC_TITLE = 'document_title'
FIELD_CODE_DOC_FULL_TEXT_LENGTH = 'document_full_text_length'
FIELD_CODE_DOC_ID = 'document_id'
FIELD_CODE_DOC_LANGUAGE = 'document_language'
FIELD_CODE_DOC_PROCESSED = 'document_processed'
FIELD_CODE_CREATE_DATE = 'create_date'
FIELD_CODE_IS_REVIEWED = 'document_is_reviewed'
FIELD_CODE_IS_COMPLETED = 'document_is_completed'
FIELD_CODE_PROJECT_ID = 'project_id'
FIELD_CODE_PROJECT_NAME = 'project_name'
FIELD_CODE_ASSIGNEE_ID = 'assignee_id'
FIELD_CODE_ASSIGNEE_NAME = 'assignee_name'
FIELD_CODE_ASSIGN_DATE = 'assign_date'
FIELD_CODE_STATUS_NAME = 'status_name'
FIELD_CODE_STATUS_ID = 'status_id'
FIELD_CODE_DELETE_PENDING = 'delete_pending'
FIELD_CODE_NOTES = 'notes'
FIELD_CODE_FORMULA = 'formula'
FIELD_CODE_DEFINITIONS = 'definitions'
FIELD_CODE_HIDDEN_COLUMNS = 'hidden_columns'
FIELD_CODE_HIDE_UNTIL_PYTHON = 'hide_until_python'
FIELD_CODE_CLUSTER_ID = 'cluster_id'
FIELD_CODE_FOLDER = 'folder'
FIELD_CODE_PARTIES = 'parties'
FIELD_CODE_EARLIEST_DATE = 'min_date'
FIELD_CODE_LATEST_DATE = 'max_date'
FIELD_CODE_LARGEST_CURRENCY = 'max_currency'
FIELD_CODE_DOCUMENT_CLASS = 'document_class'
FIELD_CODE_DOCUMENT_CLASS_PROB = 'document_class_probability'
FIELD_CODE_IS_CONTRACT = 'is_contract'
FIELD_CODE_GEOGRAPHIES = 'geographies'
FIELD_CODE_CURRENCY_TYPES = 'currency_types'

FIELD_CODES_SYSTEM = {FIELD_CODE_PROJECT_ID, FIELD_CODE_PROJECT_NAME, FIELD_CODE_DOC_LANGUAGE,
                      FIELD_CODE_DOC_ID, FIELD_CODE_CREATE_DATE, FIELD_CODE_DOC_NAME,
                      FIELD_CODE_DOC_FULL_TEXT_LENGTH, FIELD_CODE_DOC_TITLE, FIELD_CODE_DOC_PROCESSED,
                      FIELD_CODE_IS_REVIEWED, FIELD_CODE_IS_COMPLETED,
                      FIELD_CODE_ASSIGNEE_ID, FIELD_CODE_ASSIGNEE_NAME, FIELD_CODE_ASSIGN_DATE,
                      FIELD_CODE_STATUS_NAME, FIELD_CODE_DELETE_PENDING,
                      FIELD_CODE_NOTES, FIELD_CODE_DEFINITIONS, FIELD_CODE_FOLDER,
                      FIELD_CODE_GEOGRAPHIES, FIELD_CODE_CURRENCY_TYPES,
                      FIELD_CODE_DOCUMENT_CLASS, FIELD_CODE_DOCUMENT_CLASS_PROB, FIELD_CODE_IS_CONTRACT}
FIELD_CODE_ALL_DOC_TYPES = {FIELD_CODE_PROJECT_ID, FIELD_CODE_DOC_ID, FIELD_CODE_CREATE_DATE,
                            FIELD_CODE_DOC_NAME, FIELD_CODE_DOC_LANGUAGE,
                            FIELD_CODE_DOC_FULL_TEXT_LENGTH, FIELD_CODE_DOC_TITLE,
                            FIELD_CODE_IS_REVIEWED, FIELD_CODE_IS_COMPLETED,
                            FIELD_CODE_ASSIGNEE_ID, FIELD_CODE_ASSIGNEE_NAME, FIELD_CODE_ASSIGN_DATE,
                            FIELD_CODE_STATUS_NAME, FIELD_CODE_DELETE_PENDING,
                            FIELD_CODE_NOTES, FIELD_CODE_DEFINITIONS, FIELD_CODE_FOLDER,
                            FIELD_CODE_GEOGRAPHIES, FIELD_CODE_CURRENCY_TYPES,
                            FIELD_CODE_DOCUMENT_CLASS, FIELD_CODE_DOCUMENT_CLASS_PROB, FIELD_CODE_IS_CONTRACT}
FIELD_CODES_GENERIC = {FIELD_CODE_CLUSTER_ID, FIELD_CODE_PARTIES,
                       FIELD_CODE_LARGEST_CURRENCY, FIELD_CODE_EARLIEST_DATE, FIELD_CODE_LATEST_DATE,
                       FIELD_CODE_DOCUMENT_CLASS, FIELD_CODE_DOCUMENT_CLASS_PROB, FIELD_CODE_IS_CONTRACT}
FIELD_CODES_SHOW_BY_DEFAULT_NON_GENERIC = {
    FIELD_CODE_DOC_NAME, FIELD_CODE_ASSIGNEE_NAME, FIELD_CODE_STATUS_NAME
}
FIELD_CODES_SHOW_BY_DEFAULT_GENERIC = {
    FIELD_CODE_DOC_NAME, FIELD_CODE_CLUSTER_ID, FIELD_CODE_DOC_TITLE, FIELD_CODE_PARTIES, FIELD_CODE_EARLIEST_DATE,
    FIELD_CODE_LATEST_DATE, FIELD_CODE_LARGEST_CURRENCY, FIELD_CODE_IS_CONTRACT
}
FIELD_CODES_HIDE_BY_DEFAULT = {
    FIELD_CODE_ASSIGNEE_ID, FIELD_CODE_PROJECT_ID, FIELD_CODE_DELETE_PENDING,
    FIELD_CODE_GEOGRAPHIES, FIELD_CODE_CURRENCY_TYPES,
    FIELD_CODE_NOTES, FIELD_CODE_DEFINITIONS, FIELD_CODE_FOLDER
}
FIELD_CODES_RETURN_ALWAYS = {FIELD_CODE_DOC_ID, FIELD_CODE_DOC_NAME}
FIELD_CODES_HIDE_FROM_CONFIG_API = {
    FIELD_CODE_ASSIGNEE_ID, FIELD_CODE_ASSIGN_DATE,
    FIELD_CODE_DELETE_PENDING, FIELD_CODE_DOC_PROCESSED
}
FIELD_CODE_ANNOTATION_SUFFIX = '_ann'
INDEX_NAME_PREFIX = 'cx_'
DEFAULT_ORDER_BY = (FIELD_CODE_DOC_NAME, SortDirection.ASC)

# RawDB cache field name (like "document_name") -> document field code ("name")
CACHE_FIELD_TO_DOC_FIELD = {
    FIELD_CODE_DOC_NAME: DOCUMENT_FIELD_CODE_NAME,
    FIELD_CODE_DOC_TITLE: DOCUMENT_FIELD_CODE_TITLE,
    FIELD_CODE_DOC_LANGUAGE: DOCUMENT_FIELD_CODE_LANGUAGE,
    FIELD_CODE_DELETE_PENDING: DOCUMENT_FIELD_CODE_DELETE_PENDING,
    FIELD_CODE_FOLDER: DOCUMENT_FIELD_CODE_FOLDER,
    FIELD_CODE_PROJECT_ID: DOCUMENT_FIELD_CODE_PROJECT_ID,
    FIELD_CODE_PROJECT_NAME: DOCUMENT_FIELD_CODE_PROJECT_NAME,
    FIELD_CODE_STATUS_NAME: DOCUMENT_FIELD_CODE_STATUS_NAME,
    FIELD_CODE_ASSIGNEE_ID: DOCUMENT_FIELD_CODE_ASSIGNEE_ID,
    FIELD_CODE_ASSIGNEE_NAME: DOCUMENT_FIELD_CODE_ASSIGNEE_NAME,
    FIELD_CODE_ASSIGN_DATE: DOCUMENT_FIELD_CODE_ASSIGN_DATE,
    FIELD_CODE_CLUSTER_ID: DOCUMENT_FIELD_CODE_CLUSTER_ID,
    FIELD_CODE_DOC_PROCESSED: DOCUMENT_FIELD_CODE_PROCESSED
}

CACHE_FIELD_TO_DOC_FIELD_REVERSE = {i[1]: i[0] for i in CACHE_FIELD_TO_DOC_FIELD.items()}

# document field code (simple like "language" or complex like "assignee.name") -> RawDB cache field name
DOC_FIELD_TO_CACHE_FIELD = {}
for doc_field in ALL_DOCUMENT_FIELD_CODES:
    DOC_FIELD_TO_CACHE_FIELD[doc_field] = CACHE_FIELD_TO_DOC_FIELD_REVERSE.get(doc_field) or doc_field
