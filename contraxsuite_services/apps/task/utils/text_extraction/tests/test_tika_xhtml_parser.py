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
from apps.task.utils.text_extraction.tika.tika_xhtml_parser import TikaXhtmlParser
from django.test import TestCase

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from tests.testutils import load_resource_document


class TestTikaXhtmlParser(TestCase):
    def test_process_inner_tags(self):
        text = """
<p>The pen employed in finishing her story, and making it what you now see
it to be, has had no little difficulty to put it into a dress fit to be
seen, and to make it speak language fit to be read. When a woman
debauched from her youth, nay, even being the offspring of debauchery
and vice, comes to give an account of all her vicious practices, and
even to descend to the particular occasions and circumstances by which
she ran through in threescore years, an author must be hard put to it
wrap it up so clean as not to give room, especially for vicious
readers, to turn it to his disadvantage. <a href="#">This page{{##PGPG##}}
ends with semibold text</a>.
It is suggested there cannot be the same life, the same brightness and</p>
<p>
beauty, in relating the penitent part as is in the criminal part. If
there is any truth in that suggestion, I must be allowed to say ’tis
because there is not the same taste and relish in the reading, and
indeed it is too true that the difference lies not in the real worth of
the subject so much as in the gust and palate of the reader.</p>
        """
        parser = TikaXhtmlParser()
        markup = parser.parse_text(text)
        markup.convert_markers_to_labels()
        proc_text = markup.text
        self.assertEqual(-1, proc_text.find('##'))

        pages = markup.labels['pages']
        self.assertEqual(1, len(pages))
        last_page_text = proc_text[pages[0][0] - 30: pages[0][0]].strip()
        self.assertTrue(last_page_text.endswith('This page'))

        paragraphs = markup.labels['paragraphs']
        p_text = proc_text[paragraphs[0][0]: paragraphs[0][1]].strip()
        self.assertTrue(p_text.endswith('the same brightness and'))

    def test_complex_mixed_pdf(self):
        full_text = load_resource_document('parsing/parsed_mixed_pdf.xhtml', encoding='utf-8')
        parser = TikaXhtmlParser()
        markup = parser.parse_text(full_text)
        markup.convert_markers_to_labels()

        proc_text = markup.text
        self.assertEqual(-1, proc_text.find('##'))
        pages = markup.labels['pages']
        self.assertGreater(len(pages), 100)

        pages_texts = []
        for _start, end in pages:
            in_end = min(end, len(markup.text))
            in_start = max(in_end - 50, 0)
            ending = markup.text[in_start:in_end]
            pages_texts.append(ending)

        self.assertTrue(pages_texts[0].strip().find('See “RATINGS” herein.') > 0)
        self.assertTrue(pages_texts[1].find(
            'optional redemption date of November 15, 2027.') > 0)
        self.assertTrue(pages_texts[54].strip().endswith('by the IRS.'))
