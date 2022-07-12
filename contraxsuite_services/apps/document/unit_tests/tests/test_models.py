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
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import regex as re
from typing import Dict, Any, List

from mock import patch

from tests.django_test_case import *
from tests.django_db_mock import MockQuerySet
from apps.document.models import DocumentField, DocumentType


class TestDocumentModels(TestCase):
    def test_doc_field_make_unique_code(self):
        doc_type = DocumentType()
        doc_type.pl = 'a'
        other_names = ['martial_law_1', 'marsian_law', 'Martial_law',
                       'martial__law', 'martial_law_12', 'martial_law']
        other_fields = [DocumentField() for _ in range(6)]
        for i, code in enumerate(other_names):
            other_fields[i].code = code
            other_fields[i].document_type = doc_type

        field = DocumentField()
        field.title = 'Martial Law'
        field.document_type = doc_type

        def filter_fields(fields: List[Any], filters: Dict[str, Any]):
            if 'code' in filters:
                return [f for f in fields if f.code == filters['code']]
            if 'code__iregex' in filters:
                reg = re.compile(filters['code__iregex'])
                return [f for f in fields if reg.fullmatch(f.code)]
            return fields

        with patch('apps.document.models.DocumentField') as mocked_field:
            mocked_field.objects = MockQuerySet(other_fields[:4])
            mocked_field.objects.custom_filter = filter_fields
            code = field.make_unique_code()
            self.assertEqual('martial_law', code)

            mocked_field.objects = MockQuerySet(other_fields)
            code = field.make_unique_code()
            self.assertEqual('martial_law_13', code)
