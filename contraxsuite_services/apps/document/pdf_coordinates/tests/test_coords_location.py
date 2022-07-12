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

from apps.document.pdf_coordinates.text_coord_map import TextCoordMap
# -*- coding: utf-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestCoordsLocation(TestCase):

    def test_filter_sects_by_tables(self):
        from apps.document.models import DocumentTable
        from apps.document.pdf_coordinates.tests.pdf_test_common import load_sample_pdf_data
        pdf_data, _text = load_sample_pdf_data()
        metadata = {
            'sections': [{'start': 190, 'end': 2158, 'title': '1998 1997 1996 1995 1994',
                          'title_start': 191, 'title_end': 215, 'level': 2, 'abs_level': 7},
                         {'start': 55, 'end': 900, 'title': 'test',
                          'title_start': 55, 'title_end': 59, 'level': 2, 'abs_level': 7}]
        }
        tables = [
            DocumentTable(bounding_rect=[200, 260, 240, 110],
                          page=0),
            DocumentTable(bounding_rect=[120, 240, 440, 50],
                          page=1),
        ]

        from apps.document.tasks import filter_sections_inside_tables
        filter_sections_inside_tables(metadata, pdf_data, tables)
        self.assertEqual(1, len(metadata['sections']))

    def test_filter_sect_by_paragraphs(self):
        from apps.document.models import TextUnit
        metadata = {
            'sections': [{'start': 55, 'end': 900, 'title': 'test',
                          'title_start': 55, 'title_end': 59, 'level': 2, 'abs_level': 7},
                         {'start': 190, 'end': 2158, 'title': '1998 1997 1996 1995 1994',
                          'title_start': 191, 'title_end': 215, 'level': 2, 'abs_level': 7},
                         {'start': 2160, 'end': 2901, 'title': 'MCXIII',
                          'title_start': 2165, 'title_end': 2171, 'level': 2, 'abs_level': 7}]
        }
        paragraphs = [TextUnit(location_start=0, location_end=2150),
                      TextUnit(location_start=2150, location_end=3150)]
        from apps.document.tasks import filter_multiple_sections_inside_paragraph
        filter_multiple_sections_inside_paragraph(metadata, paragraphs)
        self.assertEqual(2, len(metadata['sections']))
