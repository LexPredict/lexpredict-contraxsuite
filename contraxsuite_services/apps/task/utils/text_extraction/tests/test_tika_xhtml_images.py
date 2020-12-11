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

from tests.testutils import load_resource_document
from apps.task.utils.text_extraction.tika.tika_xhtml_parser import TikaXhtmlParser, XhtmlParsingSettings, \
    OcrTextStoreSettings

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestTikaXhtmlImages(TestCase):
    def test_ocr_if_less(self):
        text = load_resource_document('parsing/xhtml_ocr_mixed.xhtml', encoding='utf-8')
        parser = TikaXhtmlParser(pars_settings=XhtmlParsingSettings(
            ocr_sets=OcrTextStoreSettings.STORE_ALWAYS,
            ocr_vector_text_min_length=100))
        rst = parser.parse_text(text)
        rst.convert_markers_to_labels()
        self.assertGreater(len(rst.text), 100)
        """
        there'll be 4 images:
        - 2 for <img> tag
        - 2 for <div class="ocr"> tag
        """
        self.assertEqual(4, len(rst.labels['images']))

        text = load_resource_document('parsing/xhtml_ocr_mixed.xhtml', encoding='utf-8')
        parser = TikaXhtmlParser(pars_settings=XhtmlParsingSettings(
            ocr_sets=OcrTextStoreSettings.STORE_IF_NO_OTHER_TEXT,
            ocr_vector_text_min_length=100))
        rst = parser.parse_text(text)
        self.assertGreater(len(rst.text), 100)
        self.assertTrue('images' not in rst.labels or len(rst.labels['images']) == 0)

        parser = TikaXhtmlParser(pars_settings=XhtmlParsingSettings(
            ocr_sets=OcrTextStoreSettings.NEVER_STORE,
            ocr_vector_text_min_length=100))
        rst = parser.parse_text(text)
        self.assertTrue('images' not in rst.labels or len(rst.labels['images']) == 0)

    def test_ocr_little_text_scanned_negative(self):
        text = load_resource_document('parsing/xhtml_ocr_mixed_long.xhtml', encoding='utf-8')
        parser = TikaXhtmlParser(pars_settings=XhtmlParsingSettings(
            ocr_sets=OcrTextStoreSettings.STORE_IF_MORE_TEXT,
            ocr_vector_text_min_length=100))
        rst = parser.parse_text(text)
        rst.convert_markers_to_labels()
        self.assertGreater(len(rst.text), 100)
        self.assertEqual(4, len(rst.labels['images']))
        self.assertTrue('Refactor' in rst.text)

    def test_ocr_little_text_scanned_positive(self):
        text = load_resource_document('parsing/xhtml_ocr_mixed_short.xhtml', encoding='utf-8')
        parser = TikaXhtmlParser(pars_settings=XhtmlParsingSettings(
            ocr_sets=OcrTextStoreSettings.STORE_IF_MORE_TEXT,
            ocr_vector_text_min_length=100))
        rst = parser.parse_text(text)
        rst.convert_markers_to_labels()
        self.assertFalse('navigate' in rst.text)
        self.assertTrue('aforementioned' in rst.text)

    def test_ocr_empty_images(self):
        text = load_resource_document('parsing/xhtml_ocr_emptyimages.xhtml', encoding='utf-8')
        parser = TikaXhtmlParser(pars_settings=XhtmlParsingSettings(
            ocr_sets=OcrTextStoreSettings.STORE_IF_MORE_TEXT,
            ocr_vector_text_min_length=100))
        rst = parser.parse_text(text)
        self.assertEqual(len(rst.text),  rst.markers_extra_text_length)

    def test_remove_images_from_text(self):
        text = """
        {{##PF

PF##}}{{##PFThat’s all.

PF##}}{{##IM

i
=

jocument ) ft parsers





IM##}}{{##PF
Aus diesem Gedankenkreise entnahm er wesentliche Teile und vereinigte sie zu seinen letzten Werken, besonders zum Antichrist, der in den letzten Monaten vor seiner Erkrankung entstanden ist und in einem erregten Ton geschrieben ist, der sich von der Stilart der Niederschriften völlig unterscheidet.

PF##}}
        """
        parser = TikaXhtmlParser(pars_settings=XhtmlParsingSettings(
            ocr_sets=OcrTextStoreSettings.STORE_IF_MORE_TEXT,
            ocr_vector_text_min_length=100))
        text = parser.remove_text_in_images(text)
        self.assertFalse('ft parsers' in text)
        self.assertTrue('That’s all.' in text)
