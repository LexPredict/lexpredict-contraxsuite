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
from unittest import TestCase

from tests.testutils import load_resource_document
from apps.task.utils.text_extraction.tika.tika_xhtml_parser import TikaXhtmlParser

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestTikaXhtmlWrapper(TestCase):
    def test_parse_vector_pdf(self):
        text = load_resource_document('parsing/xhtml_pdf.xhtml', encoding='utf-8')
        parser = TikaXhtmlParser()
        rst = parser.parse_text(text)
        self.assertGreater(len(rst.text), 100)
        self.assertGreater(len(rst.labels['pages']), 1)
        self.assertGreater(len(rst.labels['paragraphs']), 5)

    def test_parse_headings(self):
        raw = """
        <?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml">
        <head>
        <meta name="date" content="2019-08-08T15:35:00Z"/>
        <title/>
        </head>
        <body><h1>1. Heading One</h1>
        <p class="list_Paragraph"/>
        <p class="list_Paragraph">Contrary to popular belief, Lorem Ipsum is not simply random text. 
        It has roots in a piece of classical Latin literature from &gt; 45 BC, making it over 2000 years old. 
        This book is a treatise on the theory of ethics, very popular during the Renaissance. 
        The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", <a href="en.wikipedia.org/%20s%20s">comes from a line</a> in section 1.10.32.</p>
        <p class="list_Paragraph"/>
        <p class="list_Paragraph">The standard chunk of Lorem Ipsum used since the 1500s is reproduced below for</p>
        <p class="list_Paragraph"/>
        <h2>1.1 Heading One One</h2>
        <p class="list_Paragraph">Sections 1.10.32 and 1.10.33 from "de Finibus Bonorum &amp; et Malorum" by Cicero are also</p>
        <p class="list_Paragraph"/>
        <h2>1.2 Heading one two</h2>
        <h1>2. <a name="_GoBack"/>Heading 2</h1>
        </body></html>
        """
        parser = TikaXhtmlParser()
        rst = parser.parse_text(raw)
        self.assertGreater(len(rst.text), 100)
        self.assertGreater(len(rst.labels['paragraphs']), 1)

        self.assertGreater(len(rst.labels['heading_1']), 1)
        self.assertGreater(len(rst.labels['heading_2']), 1)
        headings = [rst.text[h_s: h_e] for h_s, h_e in rst.labels['heading_1']]
        self.assertEqual('1. Heading One', headings[0])
        self.assertEqual('2. {_GoBack} Heading 2', headings[1])

        self.assertGreater(len(rst.labels['a']), 0)

        sections = rst.find_sections()
        self.assertGreater(len(sections), 1)

        self.assertTrue("de Finibus Bonorum & et Malorum" in rst.text)

    def test_parse_table(self):
        raw = """        
        <?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml">
        <head>
        <meta name="dc:publisher" content=""/>
        <title/>
        </head>
        <body><p>What is Lorem Ipsum?</p>
        <p><b>Lorem Ipsum</b> is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry.</p>
        <p/>
        <table><tbody><tr>	<td><p>Row 1, column 1</p>
        </td>	<td><p>Row 1, column 2</p>
        </td>	<td><p>Row 1, column 3</p>
        </td></tr>
        <tr>	<td><p>Row 2, column 1</p>
        </td>	<td><p>Row 2, column 2</p>
        </td>	<td><p>Row 2, column 3</p>
        </td></tr>
        <tr>	<td><p>Row 3, column 1</p>
        </td>	<td><p>Row 3, column 2</p>
        </td>	<td><p>Row 3, column 3</p>
        </td></tr>
        <tr>	<td><p>Row 4, column 1</p>
        </td>	<td><p>Row 4, column 2</p>
        </td>	<td><p>Row 4, column 3</p>
        </td></tr>
        </tbody></table>
        <p/>
        <h2>Where does it come from?</h2>
        <p class="normal_(Web)">Contrary to popular belief, Lorem Ipsum is not simply random text.</p>
        <p/>
        <table><tbody><tr>	<td><p>r1c1: Contrary to popular belief, Lorem Ipsum is not simply random text.</p>
        </td>	<td><p/>
        </td>	<td><p/>
        </td></tr>
        <tr>	<td><p/>
        </td>	<td><p/>
        </td>	<td><p class="normal_(Web)"><a name="_GoBack"/>r2c3: The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", comes from a line in section 1.10.32.</p>
        </td></tr>
        </tbody></table>
        <p/>
        </body></html>
        """
        parser = TikaXhtmlParser()
        rst = parser.parse_text(raw, detect_tables=True)
        self.assertGreater(len(rst.text), 100)
        self.assertGreater(len(rst.labels['paragraphs']), 1)

        self.assertEqual(2, len(rst.tables))
        table_df = rst.tables[0].serialize_in_dataframe(rst.text)

        for i_row, row in table_df.iterrows():
            for i_cell in range(len(row)):
                target_str = f'Row {i_row + 1}, column {i_cell + 1}'
                self.assertEqual(target_str, row[i_cell])

        table_df = rst.tables[1].serialize_in_dataframe(rst.text)
        cell_text = table_df.loc[1, 2]
        self.assertEqual('{_GoBack} r2c3: The first line of Lorem Ipsum, "Lorem ' +
                         'ipsum dolor sit amet..", comes from a line in section 1.10.32.\n\n', cell_text)

    def test_list_parsing(self):
        raw = """
        <?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml">
        <head>
        <meta name="pdf:PDFVersion" content="1.4"/>
        <title>Sample Docx with Image.docx</title>
        </head>
        <body><div class="page"><p/>
        <p>Explore XHTML Tika’s output
        </p>
        <p>JIRA ticket: https://lexpredict.atlassian.net/browse/CS-3966
        </p>
        <p>Here (Improve text segmentation (section / page / paragraph / sentence), section 1.1 Use 
        markup from document parser) I described Tika’s output in XHTML. In short:
        </p>
        <p>● Tika uses PdfBox for “vector” files, MS Word and OpenOffice files 
        ● and Tesseract for scanned files
        ● in both cases Tika returns valid XHTML
        ● XHTML contains almost all information on document’s structure that Tika can get
        </p>
        <p>see the aforementioned document, section 1.2 Verdict on using Tika markup for segmenting 
        text.
        </p>
        <p>I’ve implemented a parser that reads Tika’s output in XHTML and extracts:
        1. plain text with or without extra line breaks inside paragraphs, with hyperlinks 
        </p>
        <p>
        This paragraph contains text with extra line breaks that should have been deleted 
        because the text is not formatted as a list. This paragraph contains text with extra 
        line breaks that should have been deleted because the text is not formatted as a list.
        This paragraph contains text with extra line breaks that should have been deleted because
        the text is not formatted as a list. This paragraph contains text with extra line breaks
        that should have been deleted because the text is not formatted as a list.
        </p>
        <p>formatted
        2. paragraphs’ coordinates
        3. pages’ coordinates
        4. headings
        5. tables as Pandas dataframes + anchors to the source text
        </p>
        </div>
        </body></html>
        """
        parser = TikaXhtmlParser()
        rst = parser.parse_text(raw, detect_tables=True)
        self.assertGreater(len(rst.text), 100)
        self.assertGreater(len(rst.labels['paragraphs']), 1)
