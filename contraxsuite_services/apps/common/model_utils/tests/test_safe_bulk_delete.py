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

from unittest import TestCase

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from apps.common.model_utils.safe_bulk_create import SafeBulkCreate


class TestObject:
    def __init__(self, text_unit_id: int = 0, party: str = ''):
        self.text_unit_id = text_unit_id
        self.party = party


class TestSafeBulkDelete(TestCase):
    def test_build_handler(self):
        # from apps.extract.models import PartyUsage
        msg = '''
        insert or update on table "extract_partyusage" violates foreign key constraint
        "extract_partyusage_text_unit_id_2b4758b0_fk_document_"
        DETAIL:  Key (text_unit_id)=(2614539) is not present in table "document_textunit".
        '''
        handler = SafeBulkCreate.build_entity_filter(msg)
        self.assertIsNotNone(handler)

        usages = [TestObject(1000), TestObject(2614539)]
        self.assertFalse(handler(usages[0]))
        self.assertTrue(handler(usages[1]))

    def test_build_2vals_handler(self):
        msg = '''
                insert or update on table "extract_partyusage" violates foreign key constraint
                "extract_partyusage_text_unit_id_2b4758b0_fk_document_"
                DETAIL:  Key (text_unit_id,party)=(2614539,contoso) is not present in table "document_textunit".
                '''
        handler = SafeBulkCreate.build_entity_filter(msg)
        self.assertIsNotNone(handler)

        usages = [TestObject(2614539), TestObject(2614539, 'contoso')]
        self.assertFalse(handler(usages[0]))
        self.assertTrue(handler(usages[1]))
