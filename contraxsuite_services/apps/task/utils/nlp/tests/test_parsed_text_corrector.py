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

from lexnlp.nlp.en.segments.sentences import pre_process_document
from apps.task.utils.nlp.parsed_text_corrector import ParsedTextCorrector
from django.test import TestCase
from tests.testutils import load_resource_document

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestParsedTextCorrector(TestCase):
    def test_estimate_dense_text(self):
        text = load_resource_document('parsing/pdf_malformat_parsed_default.txt', 'utf-8')
        corrector = ParsedTextCorrector()
        corr = corrector.correct_line_breaks(text)
        self.assertLess(len(corr), len(text))

    def test_correct_if_corrupted(self):
        ok_text = """
While we pursued the horsemen of the north, He slily stole away and left his men:
Whereat the great Lord of Northumberland. Whose warlike ears could never brook retreat. Cheer'd up the drooping army; 
and himself, Lord Clifford and Lord Stafford, all abreast, Charged our main battle's front, and breaking in
were by the swords of common soldiers slain.


Lord Stafford's father, Duke of Buckingham, is either slain or wounded dangerously;
I cleft his beaver with a downright blow: that this is true, father, behold his blood."""
        corrector = ParsedTextCorrector()
        corr = corrector.correct_if_corrupted(ok_text)
        self.assertEqual(len(corr), len(ok_text))

        corr = corrector.correct_line_breaks(ok_text)
        self.assertLess(len(corr), len(ok_text))

    def test_estimate_fishy_header(self):
        text = """
Notwithstanding anything in this Section (B) of Article IV to the contrary, in the event any such disruption to Tenant's operations and use of the demised premises is attributable to Landlord's negligence, or that of its agents, contractors, servants or employees, or is attributable to a breach by Landlord of its obligations under this lease, and if such disruption shall materially impair Tenant's use of the demised premises for a period in excess of five (5) business days in duration, then a just proportion of the Rent, according to the nature and extent of the impairment to Tenant's operation and use of the demised premises shall abate for any such period of time from the date of disruption which is in excess of said five (5) business days in duration.



ARTICLE V


RENT"""
        text = pre_process_document(text)
        corrector = ParsedTextCorrector()
        corr = corrector.correct_line_breaks(text)
        self.assertLess(len(corr), len(text))

    def test_fix_money_line_breaks_dotted(self):
        text = 'Some \n 11.23 amount of  \n 98 money'
        corrector = ParsedTextCorrector()
        resulted = corrector.fix_money_line_breaks(text)
        self.assertEqual('Some 11.23 amount of  \n 98 money', resulted)

    def test_fix_money_line_breaks_money_sign(self):
        text = 'Some \n $11.2 amount of  \n $98 money'
        corrector = ParsedTextCorrector()
        resulted = corrector.fix_money_line_breaks(text)
        self.assertEqual('Some $11.2 amount of $98 money', resulted)

        text = 'Some \n $ 11.2 amount of  \n $ 98 money'
        resulted = corrector.fix_money_line_breaks(text)
        self.assertEqual('Some $ 11.2 amount of $ 98 money', resulted)

    def test_fix_money_line_breaks_space_separated(self):
        text = 'Some \n 11 345.23 '
        corrector = ParsedTextCorrector()
        resulted = corrector.fix_money_line_breaks(text)
        self.assertEqual('Some 11 345.23 ', resulted)

        resulted = corrector.fix_money_line_breaks('Some \n $ 11 345 ')
        self.assertEqual('Some $ 11 345 ', resulted)

        resulted = corrector.fix_money_line_breaks('Some \n 11 345 ')
        self.assertEqual('Some \n 11 345 ', resulted)

    def test_fix_money_line_breaks_ugly_text(self):
        text = """
            per
            
            Share:
            
            $0.023
            $
            ) (
            Total Number of Shares Granted:
            
            275,000
            ) (
            Total
        """
        corrector = ParsedTextCorrector()
        resulted = corrector.fix_money_line_breaks(text)
        self.assertLess(len(resulted), len(text))
        self.assertTrue('Share: $0.023' in resulted)

    def test_fix_pager_line_break(self):
        text = 'Some paragraph  \n[1/48]  \n stop'
        corrector = ParsedTextCorrector()
        resulted = corrector.fix_pager_line_breaks(text)
        self.assertEqual('Some paragraph [1/48]  \n stop', resulted)

        resulted = corrector.fix_pager_line_breaks('Some paragraph  \n[1/48].')
        self.assertEqual('Some paragraph [1/48].', resulted)

        resulted = corrector.fix_pager_line_breaks('Some paragraph  \n[I/48].')
        self.assertEqual('Some paragraph  \n[I/48].', resulted)
