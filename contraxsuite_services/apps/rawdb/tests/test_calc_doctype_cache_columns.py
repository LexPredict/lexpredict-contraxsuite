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


from tests.django_test_case import *
from typing import List, Iterable
from apps.document.field_type_registry import init_field_type_registry
from apps.document.models import DocumentType, DocumentField
from apps.rawdb.field_value_tables import calculate_doctype_cache_columns


class TestCalcDoctypeCacheColumns(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        init_field_type_registry()

    def manual_test_columns(self):
        user_fields = [
            DocumentField(),
            DocumentField()
        ]
        user_fields[0].code = 'k_one'
        user_fields[0].type = 'int'
        user_fields[1].code = 'k_ten'
        user_fields[1].type = 'multi_choice'

        repo = DocumentFieldRepositoryMock()
        repo.fields = user_fields

        doc_type = DocumentType.objects.get(code='k_fields_depend')
        f_count = calculate_doctype_cache_columns(doc_type, [], repo)
        self.assertEqual(35, f_count)

        # old type was 'bigint'
        f_new = DocumentField()
        f_new.code = 'k_ten'
        f_new.type = 'linked_documents'

        f_count = calculate_doctype_cache_columns(doc_type, [f_new], repo)
        self.assertEqual(36, f_count)


class DocumentFieldRepositoryMock:
    def __init__(self):
        super().__init__()
        self.fields = []  # type: List[DocumentField]

    def get_user_document_fields(self,
                                 document_type: DocumentType,
                                 include_user_fields: bool,
                                 exclude_hidden_always_fields: bool) -> Iterable[DocumentField]:
        return self.fields
