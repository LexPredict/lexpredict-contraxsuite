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
import regex as re
from django.test import TestCase
from apps.task.utils.marked_up_text import MarkedUpText

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestMarkedUpTest(TestCase):
    def test_apply_transform(self):
        text = 'a123456789b123456789c123456789d123456789e123456789'
        markup = MarkedUpText(text, labels={'p': [(7, 12), (22, 28)]})
        trans = [((0, 9), (0, 1))]
        markup.apply_transformations(trans)
        self.assertEqual((0, 4), markup.labels['p'][0])
        self.assertEqual((14, 20), markup.labels['p'][1])

    def test_replace_by_regex_none(self):
        text = 'A text   with extra   spaces.'
        markup = MarkedUpText(text)
        reg = re.compile(r'AbC')
        markup.replace_by_regex(reg, ' ')
        self.assertEqual(text, markup.text)

    def test_replace_by_regex_extra(self):
        text = 'A text   with extra   spaces.'
        markup = MarkedUpText(text,
                              labels={'p': [(7, 12), (22, 28)]})
        reg = re.compile(r'\s+')
        markup.replace_by_regex(reg, ' ')

        self.assertEqual('A text with extra spaces.', markup.text)
        labels = markup.labels['p']
        self.assertEqual((6, 10), labels[0])
        self.assertEqual((18, 24), labels[1])

    def test_replace_by_regex_limited(self):
        text = """
        <p>Here (Improve  text segmentation   (section / page / paragraph / sentence), section 1.1 Use 
        markup from document parser) I described Tika’s   output in XHTML. In short:
        </p>
        """
        labels = {'p': [(7, 12), (22, 28)]}
        reg = re.compile(r'\s+')

        markup1 = MarkedUpText(text, labels={l: list(labels[l]) for l in labels})
        markup1.replace_by_regex(reg, ' ')

        markup2 = MarkedUpText(text, labels={l: list(labels[l]) for l in labels})
        markup2.replace_by_regex(reg, ' ', 0, len(text))
        self.assertEqual(markup1.text, markup2.text)

        markup2 = MarkedUpText(text, labels={l: list(labels[l]) for l in labels})
        markup2.replace_by_regex(reg, ' ', 0, len(text) >> 1)
        self.assertNotEqual(markup1.text, markup2.text)

    def test_replace_by_regex_extra_end(self):
        text = 'A text   with extra   spaces.   '
        markup = MarkedUpText(text,
                              labels={'p': [(7, 12), (22, 29)]})
        reg = re.compile(r'\s+')
        markup.replace_by_regex(reg, ' ')

        self.assertEqual('A text with extra spaces. ', markup.text)
        labels = markup.labels['p']
        self.assertEqual((6, 10), labels[0])
        self.assertEqual((18, 25), labels[1])

    def test_replace_by_regex_extra_longer(self):
        text = 'A text   with extra   spaces, and   more spaces'
        markup = MarkedUpText(text,
                              labels={'p': [(7, 12), (22, 32), (41, 46)]})
        reg = re.compile(r'\s+')
        markup.replace_by_regex(reg, ' ')

        self.assertEqual('A text with extra spaces, and more spaces', markup.text)
        labels = markup.labels['p']
        self.assertEqual((6, 10), labels[0])
        self.assertEqual((18, 28), labels[1])
        self.assertEqual((35, 40), labels[2])

    def test_replace_by_text_extra(self):
        text = 'A text   with extra   spaces.   '
        markup = MarkedUpText(text,
                              labels={'p': [(7, 12), (22, 28)]})
        markup.replace_by_string('   ', ' ')

        self.assertEqual('A text with extra spaces. ', markup.text)
        labels = markup.labels['p']
        self.assertEqual((6, 10), labels[0])
        self.assertEqual((18, 24), labels[1])

    def test_apply_transformations_(self):
        text = 'A text   with extra   spaces.'
        markup = MarkedUpText(text,
                              labels={'p': [(7, 12), (22, 28)]})
        markup.apply_transformations([((6, 9), (6, 7)), ((19, 22), (19, 20))])
        labels = markup.labels['p']
        self.assertEqual((6, 10), labels[0])
        self.assertEqual((18, 24), labels[1])
