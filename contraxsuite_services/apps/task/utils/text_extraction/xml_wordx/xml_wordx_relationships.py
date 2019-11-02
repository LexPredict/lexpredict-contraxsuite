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

from typing import Dict, Callable
import xml.etree.ElementTree as ET

from apps.task.utils.text_extraction.xml_wordx.xml_wordx_utils import XmlPreprocessor

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.3.0/LICENSE"
__version__ = "1.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class XmlWordxRelation:
    def __init__(self,
                 id: str,
                 type: str = '',
                 target: str = '',
                 target_mode: str = ''):
        self.id = id
        self.type = type
        self.target = target
        self.target_mode = target_mode


class XmlWordxRelationship:
    def __init__(self,
                 log_func: Callable = None):
        self.rel_by_id = {}  # type: Dict[str, XmlWordxRelation]
        self.log_func = log_func

    def read_from_xml(self, xml: str) -> None:
        if not xml:
            return
        try:
            tree = ET.ElementTree(ET.fromstring(xml))
        except Exception as ex:
            self.log_msg(f'Error parsing DOCX relationship.xml: {ex}')
            return
        try:
            self.traverse_tree(tree.getroot())
        except Exception as ex:
            self.log_msg(f'Error exploring DOCX relationship.xml: {ex}')
            return

    def traverse_tree(self, node) -> None:
        go_deeper = True
        for child in node:
            tag = XmlPreprocessor.get_clear_tag(child)
            if tag == 'Relationship':
                self.parse_relationship(child)
                go_deeper = False

        if go_deeper:
            for child in node:
                self.traverse_tree(child)

    def parse_relationship(self, node) -> None:
        id = node.attrib.get('Id')
        if not id:
            return
        rel = XmlWordxRelation(id=id,
                               type=node.attrib.get('Type') or '',
                               target=node.attrib.get('Target') or '',
                               target_mode=node.attrib.get('TargetMode') or '')
        self.rel_by_id[rel.id] = rel

    def log_msg(self, msg: str) -> None:
        if self.log_func:
            self.log_func(msg)
