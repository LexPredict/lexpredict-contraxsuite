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

from apps.task.utils.text_extraction.xml_wordx.xml_wordx_utils import NumberConverter, XmlPreprocessor
from unittest import TestCase

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestWordxUtils(TestCase):
    def test_roman_number(self):
        self.assertEqual('I', NumberConverter.int_to_roman(1, True))
        self.assertEqual('II', NumberConverter.int_to_roman(2, True))
        self.assertEqual('XIV', NumberConverter.int_to_roman(14, True))
        self.assertEqual('CCXXXVIII'.lower(),
                         NumberConverter.int_to_roman(238, False))

    def test_num_to_letter(self):
        self.assertEqual('A', NumberConverter.int_to_letter(1, True))
        self.assertEqual('B', NumberConverter.int_to_letter(2, True))
        self.assertEqual('b', NumberConverter.int_to_letter(2, False))
        self.assertEqual('aa', NumberConverter.int_to_letter(26, False))
        self.assertEqual('AB', NumberConverter.int_to_letter(27, True))

    def test_remove_namespace(self):
        text = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main"}val'
        self.assertEqual('val', XmlPreprocessor.remove_namespace(text))
        self.assertEqual('val', XmlPreprocessor.remove_namespace('val'))
