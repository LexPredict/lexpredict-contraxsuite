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

import os
import zipfile
from typing import Callable, Any, List, Tuple
import xml.etree.ElementTree as ET

from pandas import DataFrame

from apps.task.utils.text_extraction.xml_wordx.xml_wordx_items import \
    DocParagraph, DocTable, DocItem, DocTableRow, DocText, DocHyperlink
from apps.task.utils.text_extraction.xml_wordx.xml_wordx_styles import XmlNumberingSetsSection
from apps.task.utils.text_extraction.xml_wordx.xml_wordx_utils import XmlPreprocessor
from apps.task.utils.text_extraction.xml_wordx.xml_wordx_numbering import XmlWordxNumbering
from apps.task.utils.text_extraction.xml_wordx.xml_wordx_serialization import \
    WordxSerializationSettings, SerializationContext
from apps.task.utils.text_extraction.xml_wordx.xml_wordx_relationships import \
    XmlWordxRelationship

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class XmlWordxExtractor:
    extensions = {'docx'}

    def __init__(self,
                 log_func: Callable = None):
        self.log_func = log_func
        self.file_name = ''
        self.tree = None  # type: ET.ElementTree
        self.items = []  # type:List[DocItem]
        self.serialize_sets = WordxSerializationSettings()
        self.numbering = XmlWordxNumbering()
        self.relationship = XmlWordxRelationship()
        self.styles = XmlNumberingSetsSection()
        self.tables = []  # type:List[DataFrame]
        self.doc_tables = []  # type:List[DocTable]

    # these methods can be overriden to return derived classes
    @classmethod
    def make_paragraph_instance(cls) -> DocParagraph:
        return DocParagraph()

    @classmethod
    def make_table_instance(cls) -> DocTable:
        return DocTable()

    @classmethod
    def make_hyperlink_instance(cls) -> DocHyperlink:
        return DocHyperlink()

    def can_process_file(self, file_name: str) -> bool:
        _, file_extension = os.path.splitext(file_name)
        file_extension = file_extension.strip('.')
        return file_extension in self.extensions

    def parse_file(self, file_name: str) -> str:
        self.file_name = file_name
        doc_xml, numb_xml, rel_xml, styles_xml = self.get_plain_xml()
        if not doc_xml:
            return None
        try:
            self.tree = ET.ElementTree(ET.fromstring(doc_xml))
        except Exception as ex:
            self.log_msg(f'Error parsing DOCX XML: {ex}')
            return None

        try:
            if numb_xml:
                self.numbering.read_from_xml(numb_xml)
        except Exception as ex:
            self.log_msg(f'Error parsing numbering XML: {ex}')

        try:
            if rel_xml:
                self.relationship.read_from_xml(rel_xml)
        except Exception as ex:
            self.log_msg(f'Error parsing relationship XML: {ex}')

        try:
            if styles_xml:
                self.styles.read_from_xml(styles_xml)
        except Exception as ex:
            self.log_msg(f'Error parsing styles XML: {ex}')

        self.traverse_doc_tree(self.tree.getroot(), self.items)

        text = self.serialize_items()
        return text

    def serialize_items(self) -> str:
        context = SerializationContext([],
                                       self.serialize_sets,
                                       self.numbering)
        for item in self.items:
            item.serialize(context)
        self.serialize_tables(context)
        return '\n'.join([str(l) for l in context.lines])

    def serialize_tables(self, context: SerializationContext) -> None:
        for table in self.doc_tables:
            df = table.serialize_in_dataframe(context)
            self.tables.append(df)

    def traverse_doc_tree(self, node: Any, items_container: List[DocItem]):
        # fill "Items"
        for elt in node:
            tag = XmlPreprocessor.get_clear_tag(elt)
            if tag == 'p':
                self.add_paragraph(elt, items_container)
            elif tag == 'tbl':
                self.add_table(elt, items_container)
            else:
                self.traverse_doc_tree(elt, items_container)

    def add_paragraph(self, node: Any, items_container: List[Any]):
        pr = self.make_paragraph_instance()
        self.explore_paragraph(pr, node)
        items_container.append(pr)

    def explore_paragraph(self, pr: DocParagraph, node: Any):
        for child in node:
            tag = XmlPreprocessor.get_clear_tag(child)
            if tag == 'pPr':
                self.explore_paragraph_properties(pr, child)
            elif tag == 'hyperlink':
                self.add_hyperlink(child, pr.text_items)
            elif tag == 'tab':
                pr.text_items.append(DocText('\t'))
            elif tag == 't':
                if child.text:
                    pr.text_items.append(DocText(child.text))
            elif tag == 'r':
                self.explore_paragraph(pr, child)
            else:
                self.explore_paragraph(pr, child)

    def add_hyperlink(self, node: Any, container: List[DocItem]) -> None:
        text_child = XmlPreprocessor.find_children_by_tag(node,
                                                          't',
                                                          first_only=True)
        if not text_child or not text_child[0].text:
            return
        link = self.make_hyperlink_instance()
        link.text = text_child[0].text
        # get link's reference
        # r:id="rId4" -> self.relationship
        rel_id = XmlPreprocessor.get_clear_attribute_val(node, 'id')
        if rel_id:
            rel_link = self.relationship.rel_by_id.get(rel_id) or ''
            link.link = rel_link
        container.append(link)

    def explore_paragraph_properties(self, pr: DocParagraph, node: Any):
        for elt in node:
            tag = XmlPreprocessor.get_clear_tag(elt)
            if tag == 'pStyle':
                style_val = XmlPreprocessor.get_clear_attributes(elt).get('val')
                if style_val:
                    self.apply_paragraph_style(pr, style_val)
            elif tag == 'numPr':
                self.explore_paragraph_numpr(pr, elt)
            else:
                self.explore_paragraph_properties(pr, elt)

    def apply_paragraph_style(self, pr: DocParagraph, style_id: str):
        pr.style = style_id
        style = self.styles.find_style(style_id)
        if style.numId:
            pr.list_number = style.numId
            pr.list_level = style.ilvl

    def explore_paragraph_numpr(self, pr: DocParagraph, node: Any):
        for elt in node:
            tag = XmlPreprocessor.get_clear_tag(elt)
            if tag == 'ilvl':
                style_val = XmlPreprocessor.get_clear_attributes(elt).get('val')
                if style_val:
                    pr.list_level = int(style_val)
            elif tag == 'numId':
                style_val = XmlPreprocessor.get_clear_attributes(elt).get('val')
                if style_val:
                    pr.list_number = int(style_val)

    def add_table(self, node: Any, items_container: List[Any]):
        t = self.make_table_instance()
        items_container.append(t)
        self.fill_table_rows(t, node)
        self.doc_tables.append(t)

    def fill_table_rows(self, tbl: DocTable, node: Any):
        go_deeper = True
        for elt in node:
            tag = XmlPreprocessor.get_clear_tag(elt)
            if tag == 'tr':
                go_deeper = False
                self.fill_table_row(tbl, elt)

        if not go_deeper:
            return

        for elt in node:
            self.fill_table_rows(tbl, elt)

    def fill_table_row(self, tbl: DocTable, node: Any):
        row = DocTableRow()
        tbl.rows.append(row)

        go_deeper = True
        for elt in node:
            tag = XmlPreprocessor.get_clear_tag(elt)
            if tag == 'tc':
                go_deeper = False
                self.fill_table_cell(row, elt)

        if not go_deeper:
            return

        for elt in node:
            self.fill_table_row(tbl, elt)

    def fill_table_cell(self, row: DocTableRow, node: Any):
        cell = []
        row.cells.append(cell)
        self.traverse_doc_tree(node, cell)

    def get_plain_xml(self) -> Tuple[str, str, str, str]:
        """
        :return: document.xml, numbering.xml, relationship.xml (all in decoded strings)
        """
        try:
            with open(self.file_name, 'rb') as f:
                zip = zipfile.ZipFile(f)
                main_ctx = self.get_document_content(zip)
                numb_ctx = self.get_document_numbering(zip)
                rel_xml = self.get_document_relationship(zip)
                styles_xml = self.get_document_styles(zip)
            return main_ctx, numb_ctx, rel_xml, styles_xml
        except Exception as ex:
            self.log_msg(f'Error reading DOCX XML: {ex}')
            return None, None, None, None

    @staticmethod
    def get_document_content(zip: zipfile.ZipFile) -> str:
        xml_content = zip.read('word/document.xml')
        # TODO: derive decoding from doc
        xml_content = xml_content.decode("utf-8")
        return xml_content

    @staticmethod
    def get_document_numbering(zip: zipfile.ZipFile) -> str:
        try:
            xml_content = zip.read('word/numbering.xml')
            # TODO: derive decoding from doc
            xml_content = xml_content.decode("utf-8")
            return xml_content
        except:
            return ''

    @staticmethod
    def get_document_relationship(zip: zipfile.ZipFile) -> str:
        try:
            xml_content = zip.read('word/_rels/document.xml.rels')
            # TODO: derive decoding from doc
            xml_content = xml_content.decode("utf-8")
            return xml_content
        except:
            return ''

    @staticmethod
    def get_document_styles(zip: zipfile.ZipFile) -> str:
        try:
            xml_content = zip.read('word/styles.xml')
            # TODO: derive decoding from doc
            xml_content = xml_content.decode("utf-8")
            return xml_content
        except:
            return ''

    def log_msg(self, msg: str) -> None:
        if self.log_func:
            self.log_func(msg)
