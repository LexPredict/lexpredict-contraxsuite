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

from apps.task.utils.text_extraction.xml_wordx.xml_wordx_extractor import XmlWordxExtractor
from unittest import TestCase
import regex as re
from tests.testutils import TEST_RESOURCE_DIRECTORY

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestWordxParseDocuments(TestCase):

    def test_tables_plain(self):
        file_path = self.get_file_path('tables_only.docx')
        xtractor = XmlWordxExtractor()
        self.assertTrue(xtractor.can_process_file(file_path))
        text = xtractor.parse_file(file_path)
        self.assertGreater(len(text), 100)

        regexp = re.compile(r'Row 1, column 1\s+Row 1, column 2\s+Row 1, column 3')
        self.assertTrue(regexp.search(text))

        self.assertTrue('r1c1: Contrary to popular belief' in text)

        regexp = re.compile(r'\s+r2c3: The first line of Lorem Ipsum')
        self.assertTrue(regexp.search(text))

    def test_hyperlink(self):
        file_path = self.get_file_path('hyperlink.docx')
        xtractor = XmlWordxExtractor()
        text = xtractor.parse_file(file_path)
        self.assertGreater(len(text), 50)
        self.assertTrue('https://epam-my.sharepoint.com/' in text)
        self.assertTrue('Soft Skill' in text)

    def test_lists(self):
        file_path = self.get_file_path('lists.docx')
        xtractor = XmlWordxExtractor()
        text = xtractor.parse_file(file_path)
        self.assertGreater(len(text), 50)

        regexp = re.compile(r'1\)\s+Refrigerator')
        self.assertTrue(regexp.search(text))

    def test_template_01(self):
        file_path = self.get_file_path('template_01.docx')
        xtractor = XmlWordxExtractor()
        text = xtractor.parse_file(file_path)
        self.assertGreater(len(text), 250)
        self.assertTrue('Describe your responsibilities and ' +
                        'achievements in terms of impact and results.' in text)

    def test_template_02(self):
        file_path = self.get_file_path('template_02.docx')
        xtractor = XmlWordxExtractor()
        text = xtractor.parse_file(file_path)
        self.assertGreater(len(text), 250)
        self.assertTrue('List your strengths relevant for the role ' +
                        'you’re applying for' in text)

    def test_numbered_headings(self):
        file_path = self.get_file_path('numbered_headings.docx')
        xtractor = XmlWordxExtractor()
        text = xtractor.parse_file(file_path)
        self.assertGreater(len(text), 250)

        regexp = re.compile(r'1.\s+Heading One')
        self.assertTrue(regexp.search(text))
        regexp = re.compile(r'1.1\s+Heading One One')
        self.assertTrue(regexp.search(text))
        regexp = re.compile(r'1.2\s+Heading one two')
        self.assertTrue(regexp.search(text))
        regexp = re.compile(r'2.\s+Heading 2')
        self.assertTrue(regexp.search(text))

    def test_table_with_columns(self):
        file_path = self.get_file_path('doc_table_01.docx')
        xtractor = XmlWordxExtractor()
        text = xtractor.parse_file(file_path)
        self.assertGreater(len(text), 250)
        self.assertEqual(1, len(xtractor.tables))
        table = xtractor.tables[0]
        self.assertEqual((4, 3), table.shape)

    def test_table_in_table(self):
        file_path = self.get_file_path('doc_table_02.docx')
        xtractor = XmlWordxExtractor()
        text = xtractor.parse_file(file_path)
        self.assertGreater(len(text), 250)
        self.assertEqual(2, len(xtractor.tables))

        table = xtractor.tables[0]
        self.assertEqual((2, 2), table.shape)

        table = xtractor.tables[1]
        self.assertEqual((4, 3), table.shape)

    @staticmethod
    def get_file_path(file_name: str) -> str:
        return os.path.join(TEST_RESOURCE_DIRECTORY,
                            'documents/ocr/wordx',
                            file_name)
