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

import json
from unittest import TestCase
from apps.task.utils.nlp.heading_heuristics import HeadingHeuristics
from tests.testutils import load_resource_document
from apps.task.tasks import LoadDocuments
from apps.document.models import TextUnit

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestHeadingHeuristics(TestCase):
    def test_too_short(self):
        self.assertEqual('Title B',
                         HeadingHeuristics.get_better_title('B', 'Title B'))
        self.assertEqual('A',
                         HeadingHeuristics.get_better_title('A', 'B2'))

    def test_too_long(self):
        long_text = 'Hea' + 'd' * 200 + 'ing'
        self.assertEqual('Title B',
                         HeadingHeuristics.get_better_title(long_text, 'Title B'))

    def test_new_better(self):
        self.assertEqual('II.IV Some other title',
                         HeadingHeuristics.get_better_title('Some title', 'II.IV Some other title'))

    def test_old_better(self):
        self.assertEqual('II.IV Some title',
                         HeadingHeuristics.get_better_title('II.IV Some title', 'II.IV Some other title'))

    def test_find_better_titles(self):
        full_text = load_resource_document('parsing/heading_document.txt')
        sections_txt = load_resource_document('parsing/heading_doc_sections.txt')
        sections = json.loads(sections_txt)
        section_titles = [s['title'] for s in sections]

        sentences_txt = load_resource_document('parsing/heading_doc_sentences.txt')
        sentence_coords = json.loads(sentences_txt)

        sentences = []
        for row in sentence_coords:
            sentence = TextUnit()
            sentence.location_start = int(row[0])
            sentence.location_end = int(row[1])
            sentences.append(sentence)

        LoadDocuments.find_section_titles(sections, sentences, full_text)
        new_section_titles = [s['title'] for s in sections]
        self.assertNotEqual(section_titles[16], new_section_titles[16])
