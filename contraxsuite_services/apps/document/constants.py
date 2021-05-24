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
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import enum
from typing import Union, List, Optional

"""
Constants related to document app.
Main goal of having this file is resolving cyclic dependencies between other modules.

"""
DOCUMENT_TYPE_PK_GENERIC_DOCUMENT = '68f992f1-dba3-4dc0-a815-4d868b23c5b4'
DOCUMENT_TYPE_CODE_GENERIC_DOCUMENT = 'document.GenericDocument'
DOCUMENT_FIELD_CODE_MAX_LEN = 50

FieldSpec = Optional[Union[bool, List[str]]]


class DocumentGenericField(enum.Enum):
    cluster_id = 'cluster_id'

    def specified_in(self, field_spec: FieldSpec):
        return field_spec is True or field_spec and self.value in field_spec


class DocumentSystemField(enum.Enum):
    assignee = 'assignee'
    status = 'status'
    project = 'project'
    delete_pending = 'delete_pending'
    notes = 'notes'
    folder = 'folder'
    processed = 'document_processed'

    def specified_in(self, field_spec: FieldSpec):
        return field_spec is True or field_spec and self.value in field_spec


DOC_NUMBER_PER_SUB_TASK = 20
DOC_NUMBER_PER_MAIN_TASK = 100


DOCUMENT_FIELD_CODE_ID = 'id'
DOCUMENT_FIELD_CODE_NAME = 'name'
DOCUMENT_FIELD_CODE_DESCRIPTION = 'description'
DOCUMENT_FIELD_CODE_LANGUAGE = 'language'
DOCUMENT_FIELD_CODE_SOURCE = 'source'
DOCUMENT_FIELD_CODE_SOURCE_TYPE = 'source_type'
DOCUMENT_FIELD_CODE_SOURCE_PATH = 'source_path'
DOCUMENT_FIELD_CODE_FILE_SIZE = 'file_size'
DOCUMENT_FIELD_CODE_PARAGRAPHS = 'paragraphs'
DOCUMENT_FIELD_CODE_SENTENCES = 'sentences'
DOCUMENT_FIELD_CODE_TITLE = 'title'
DOCUMENT_FIELD_CODE_HISTORY = 'history'
DOCUMENT_FIELD_CODE_DELETE_PENDING = 'delete_pending'
DOCUMENT_FIELD_CODE_FOLDER = 'folder'
DOCUMENT_FIELD_CODE_DOCUMENT_TYPE = 'document_type'
DOCUMENT_FIELD_CODE_PROJECT = 'project'
DOCUMENT_FIELD_CODE_PROJECT_ID = 'project_id'
DOCUMENT_FIELD_CODE_PROJECT_NAME = 'project.name'
DOCUMENT_FIELD_CODE_STATUS = 'status'
DOCUMENT_FIELD_CODE_STATUS_ID = 'status_id'
DOCUMENT_FIELD_CODE_STATUS_NAME = 'status.name'
DOCUMENT_FIELD_CODE_ASSIGNEE = 'assignee'
DOCUMENT_FIELD_CODE_ASSIGNEE_ID = 'assignee_id'
DOCUMENT_FIELD_CODE_ASSIGNEE_NAME = 'assignee.get_full_name'
DOCUMENT_FIELD_CODE_ASSIGN_DATE = 'assign_date'
DOCUMENT_FIELD_CODE_UPLOAD_SESSION = 'upload_session'
DOCUMENT_FIELD_CODE_PROCESSED = 'processed'
DOCUMENT_FIELD_CODE_CLUSTER_ID = 'cluster_id'
DOCUMENT_FIELD_CODE_CLASS = 'document_class'
DOCUMENT_FIELD_CODE_CONTRACT_TYPE = 'document_contract_class'
DOCUMENT_FIELD_CODE_OCR_GRADE = 'ocr_rating'

ALL_DOCUMENT_FIELD_CODES = {
    DOCUMENT_FIELD_CODE_NAME,
    DOCUMENT_FIELD_CODE_DESCRIPTION,
    DOCUMENT_FIELD_CODE_LANGUAGE,
    DOCUMENT_FIELD_CODE_SOURCE,
    DOCUMENT_FIELD_CODE_SOURCE_TYPE,
    DOCUMENT_FIELD_CODE_SOURCE_PATH,
    DOCUMENT_FIELD_CODE_FILE_SIZE,
    DOCUMENT_FIELD_CODE_PARAGRAPHS,
    DOCUMENT_FIELD_CODE_SENTENCES,
    DOCUMENT_FIELD_CODE_TITLE,
    DOCUMENT_FIELD_CODE_HISTORY,
    DOCUMENT_FIELD_CODE_DELETE_PENDING,
    DOCUMENT_FIELD_CODE_FOLDER,
    DOCUMENT_FIELD_CODE_DOCUMENT_TYPE,
    DOCUMENT_FIELD_CODE_PROJECT,
    DOCUMENT_FIELD_CODE_PROJECT_ID,
    DOCUMENT_FIELD_CODE_PROJECT_NAME,
    DOCUMENT_FIELD_CODE_STATUS,
    DOCUMENT_FIELD_CODE_STATUS_NAME,
    DOCUMENT_FIELD_CODE_ASSIGNEE,
    DOCUMENT_FIELD_CODE_ASSIGNEE_ID,
    DOCUMENT_FIELD_CODE_ASSIGNEE_NAME,
    DOCUMENT_FIELD_CODE_ASSIGN_DATE,
    DOCUMENT_FIELD_CODE_UPLOAD_SESSION,
    DOCUMENT_FIELD_CODE_PROCESSED,
    DOCUMENT_FIELD_CODE_CLUSTER_ID,
    DOCUMENT_FIELD_CODE_CLASS,
    DOCUMENT_FIELD_CODE_CONTRACT_TYPE,
    DOCUMENT_FIELD_CODE_OCR_GRADE}

# Document.metadata keys
DOC_METADATA_DOCUMENT_CLASS_PROB = 'document_class_probability'
DOC_METADATA_DOCUMENT_CONTRACT_CLASS_VECTOR = 'document_contract_type_vector'

# Field Annotation Filter names
FA_COMMON_FILTER = 'common_filter'
FA_USER_FILTER = 'user_filter'
