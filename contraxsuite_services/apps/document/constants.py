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
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.3.0/LICENSE"
__version__ = "1.3.0"
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

    def specified_in(self, field_spec: FieldSpec):
        return field_spec is True or field_spec and self.value in field_spec


DOC_NUMBER_PER_SUB_TASK = 20
DOC_NUMBER_PER_MAIN_TASK = 100
