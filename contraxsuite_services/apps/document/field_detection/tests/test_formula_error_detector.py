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

from tests.django_test_case import *
from django.test import TestCase
from apps.document.admin import DocumentFieldAdmin
from apps.document.models import DocumentField

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestFormulaErrorDetector(TestCase):
    def non_test_formula_ok(self):
        from apps.document.field_type_registry import init_field_type_registry
        init_field_type_registry()

        document_field = DocumentField.objects.get(code='ws_accept_reject_sender_based')
        formula = "'accept' if ('Glee' in (ws_email_subject or '') or 'R&B' in (ws_email_subject or '')) " + \
                  "and (ws_lit_client or ws_lit_contact or ws_lit_subsidiary) else ('unsure' or some_var)"
        fields_to_values = {
            'ws_email_subject': 'No Subject'
        }
        r = DocumentFieldAdmin.calculate_formula_result_on_values(
            check_return_value=True, document_field=document_field,
            fields_to_values=fields_to_values, formula=formula)
        self.assertEqual(1, len(r.warnings))
