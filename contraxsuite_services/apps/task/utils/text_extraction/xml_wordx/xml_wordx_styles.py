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

import regex as re
from typing import Dict, Callable, Any, Set
import xml.etree.ElementTree as ET

from apps.task.utils.text_extraction.xml_wordx.xml_wordx_utils import XmlPreprocessor

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


"""
Reads /word/styles.xml
Looks for "<w:style w:type="paragraph" w:styleId="Heading2">" sections
"""


class StyleSets:

    reg_format_space_clear = re.compile(r'(?<=%)\s(?=\d+)')
    reg_format_str = re.compile(r'%\d+')
    default_bullet = '•'

    def __init__(self):
        self.styleId = ''  # Heading2
        self.type = ''  # paragraph
        self.aliases = set()  # type:Set[str]  # { '1.1', '2nd', 'B Sub' }
        self.numId = 0
        self.ilvl = 0


class XmlNumberingSetsSection:
    def __init__(self,
                 log_func: Callable = None):
        self.sets = {}  # type: Dict[str, StyleSets]
        self.log_func = log_func

    def read_from_xml(self, xml: str) -> None:
        if not xml:
            return
        try:
            tree = ET.ElementTree(ET.fromstring(xml))
        except Exception as ex:
            self.log_msg(f'Error parsing DOCX styles.xml: {ex}')
            return
        try:
            self.traverse_tree(tree.getroot())
        except Exception as ex:
            self.log_msg(f'Error exploring DOCX styles.xml: {ex}')
            return

    def find_style(self, style_id: str) -> StyleSets:
        style = self.sets.get(style_id)
        if style:
            return style
        for key in self.sets:
            style = self.sets[key]
            if style_id in style.aliases:
                return style
        return None

    def traverse_tree(self, node: Any) -> None:
        # looking for "<w:style w:type="paragraph" w:styleId="Heading2">"
        get_section = False
        for child in node:
            tag = XmlPreprocessor.get_clear_tag(child)
            if tag == 'style':
                self.read_section(child)
                get_section = True

        if get_section:
            return
        for child in node:
            self.traverse_tree(child)

    def read_section(self, node: Any) -> None:
        """
        <w:style w:type="paragraph" w:styleId="Heading2">
            <w:aliases w:val="1.1,2nd,B Sub/Bold,B Sub/Bold1,B Sub/Bold11,B Sub/Bold12,B Sub/Bold13" />
            <w:pPr>
                <w:keepNext />
                <w:numPr>
                    <w:ilvl w:val="1" />
                    <w:numId w:val="19" />
                </w:numPr>
            </w:pPr>
        </w:num>
        """
        style_id = XmlPreprocessor.get_clear_attribute_val(node, 'styleId')
        if not style_id:
            return
        style_set = StyleSets()
        style_set.styleId = style_id
        self.sets[style_id] = style_set
        try:
            self.explore_section(node, style_set)
        except:
            del self.sets[style_id]

    def explore_section(self, node: Any, style_set: StyleSets):
        for child in node:
            tag = XmlPreprocessor.get_clear_tag(child)
            if tag == 'aliases':
                val = XmlPreprocessor.get_clear_attribute_val(child, 'val')
                aliases = set((val or '').split(','))
                style_set.aliases = aliases
                continue
            if tag == 'ilvl':
                val = XmlPreprocessor.get_clear_attribute_val(child, 'val')
                style_set.ilvl = int(val)
                continue
            if tag == 'numId':
                val = XmlPreprocessor.get_clear_attribute_val(child, 'val')
                style_set.numId = int(val)
                continue
            self.explore_section(child, style_set)

    def log_msg(self, msg: str) -> None:
        if self.log_func:
            self.log_func(msg)
