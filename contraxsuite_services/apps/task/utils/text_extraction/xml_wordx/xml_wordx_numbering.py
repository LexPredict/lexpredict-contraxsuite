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
from typing import Dict, List, Callable, Any
import xml.etree.ElementTree as ET

from apps.task.utils.text_extraction.xml_wordx.xml_wordx_utils import NumberConverter, \
    XmlPreprocessor

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class NumberingSets:
    reg_format_space_clear = re.compile(r'(?<=%)\s(?=\d+)')
    reg_format_str = re.compile(r'%\d+')
    default_bullet = '•'

    def __init__(self):
        self.set_id = 0
        self.level = 0
        self.start = 1
        self.num_fmt = 'bullet'  # or lowerRoman or decimal
        self.lvl_text = '#'
        self.lvl_jc = ''  # left, right ...

        self.format_string = None  # type:str
        self.parent_section = None

    def initialize(self):
        self.parse_format_sets()

    def format_number(self,
                      all_sections: List[Any],  # List[NumberingSets]
                      counter_by_level: List[int],
                      level: int) -> str:
        if self.num_fmt == 'bullet':
            return self.lvl_text

        counters = []
        for i in range(level + 1):
            cur_counter = counter_by_level.get(i) or 0
            cur_section = all_sections[level]
            counters.append(cur_section.get_formatted_level_counter(cur_counter))

        num_str = self.format_string.format(*counters)
        return num_str

    def get_formatted_level_counter(self, counter: int) -> str:
        if self.num_fmt == 'bullet':
            return self.lvl_text
        counter += self.start

        number_str = str(counter)
        if self.num_fmt != 'decimal':
            upper_case = self.num_fmt.startswith('upper')
            if self.num_fmt.endswith('Roman'):
                number_str = NumberConverter.int_to_roman(counter, upper_case)
            elif self.num_fmt.endswith('Letter'):
                number_str = NumberConverter.int_to_letter(counter, upper_case)
        return number_str

    def parse_format_sets(self):
        # "Sub %1-% 2-%3. "
        fmt_str = self.reg_format_space_clear.sub('', self.lvl_text)
        # "Sub %1-%2-%3. "
        for lvl in range(1, 10):
            rep = f'%{lvl}'
            nval = f'{{{lvl-1}}}'
            fmt_str = fmt_str.replace(rep, nval)
        # "Sub {0}-{1}-{2}. "
        self.format_string = fmt_str


class NumberingSetsSection:
    def __init__(self):
        self.sets = []  # type: List[NumberingSets]
        self.restart_after_break = False
        self.list_counter_by_level = {}  # type: Dict[int, int]

    def initialize(self):
        self.sets.sort(key=lambda s: s.level)
        for st in self.sets:
            st.parent_section = self
            st.initialize()


class XmlWordxNumbering:
    simplify_bullet_symbols = True
    enabled_bullet_symbols = ['•', '♦', '○']

    def __init__(self,
                 log_func: Callable = None):
        self.list_num_to_section_id = {}  # type: Dict[int, int]
        self.collections = {}  # type: Dict[int: NumberingSetsSection]
        self.log_func = log_func
        # last serialized list_level by list_number, used for continue or
        # break number sequence for lists / headings
        self.level_by_list = {}  # type: Dict[int, int]

    def get_bullet(self, item: Any) -> str:
        """
        :param context: serialization context, provides current settings
        :param item: item being serialized
        :return: bullet symbol or formatted number
        """
        if not hasattr(item, 'list_level'):
            return ''
        list_id = item.list_number
        level = item.list_level
        prev_level = self.level_by_list.get(list_id)
        self.level_by_list[list_id] = level

        sect_id = self.list_num_to_section_id.get(list_id)
        if sect_id is None:
            return NumberingSets.default_bullet
        num_set_lst = self.collections.get(sect_id)
        if not num_set_lst:
            return NumberingSets.default_bullet
        if level < 0 or level >= len(num_set_lst.sets):
            return NumberingSets.default_bullet
        num_set = num_set_lst.sets[level]

        # determine list counter (zero started)
        counter = 0
        ct = num_set_lst.list_counter_by_level.get(level)
        continue_numbering = True if ct is not None else False
        if continue_numbering and num_set_lst.restart_after_break:
            # check prev serialized item has the same sect_num and level
            if prev_level is None:
                continue_numbering = False
            elif prev_level < level:
                continue_numbering = False

        if continue_numbering:
            counter = ct + 1
        num_set_lst.list_counter_by_level[level] = counter
        # finally, get text - "1)" or simply "-"
        return num_set.format_number(
            num_set_lst.sets,
            num_set_lst.list_counter_by_level, level)

    def read_from_xml(self, xml: str) -> None:
        if not xml:
            return
        try:
            tree = ET.ElementTree(ET.fromstring(xml))
        except Exception as ex:
            self.log_msg(f'Error parsing DOCX numbering.xml: {ex}')
            return
        try:
            self.traverse_tree(tree.getroot())
        except Exception as ex:
            self.log_msg(f'Error exploring DOCX numbering.xml: {ex}')
            return
        if self.simplify_bullet_symbols:
            self.assign_simple_bullet_symbols()

    def traverse_tree(self, node: Any) -> None:
        # looking for "<w:abstractNum w:abstractNumId="1" restartNumberingAfterBreak="0">"
        get_section = False
        get_num_map = False
        for child in node:
            tag = XmlPreprocessor.get_clear_tag(child)
            if tag == 'abstractNum':
                self.read_section(child)
                get_section = True
            elif tag == 'num':
                get_num_map = True
                self.read_num_map(child)

        if get_section and get_num_map:
            return
        for child in node:
            self.traverse_tree(child)

    def read_num_map(self, node: Any) -> None:
        """
        <w:num w:numId="1">
            <w:abstractNumId w:val="1" />
        </w:num>
        """
        num_id_str = XmlPreprocessor.get_clear_attribute_val(node, 'numId')
        if not num_id_str:
            return
        num_id = int(num_id_str)  # list number
        for child in node:
            tag = XmlPreprocessor.get_clear_tag(child)
            if tag != 'abstractNumId':
                continue
            val_str = XmlPreprocessor.get_clear_attribute_val(child, 'val')
            if not val_str:
                break
            sect_id = int(val_str)
            self.list_num_to_section_id[num_id] = sect_id
            return

    def read_section(self, node: Any) -> None:
        attrs = XmlPreprocessor.get_clear_attributes(node)
        num_str = attrs.get('abstractNumId')
        if not num_str:
            return
        sect_index = int(num_str)
        sect = NumberingSetsSection()
        restart_num_str = attrs.get('restartNumberingAfterBreak') or ''
        sect.restart_after_break = restart_num_str != '0'

        self.collections[sect_index] = sect
        go_deeper = True

        for child in node:
            tag = XmlPreprocessor.get_clear_tag(child)
            # find "<w:lvl w:ilvl="0">"
            if tag == 'lvl':
                self.read_numbering_sets(child, sect)
                go_deeper = False

        try:
            if not go_deeper:
                return
            for child in node:
                self.read_section(child)
        finally:
            sect.initialize()

    def read_numbering_sets(self, node: Any, sect: NumberingSetsSection):
        nm_set = NumberingSets()
        lvl = XmlPreprocessor.get_clear_attribute_val(node, 'ilvl')
        nm_set.level = int(lvl)

        for child in node:
            tag = XmlPreprocessor.get_clear_tag(child)
            if tag == 'start':
                nm_set.start = int(
                    XmlPreprocessor.get_clear_attribute_val(child, 'val') or '0')
                continue
            if tag == 'numFmt':
                nm_set.num_fmt = \
                    XmlPreprocessor.get_clear_attribute_val(child, 'val') or 'bullet'
                continue
            if tag == 'lvlText':
                nm_set.lvl_text = \
                    XmlPreprocessor.get_clear_attribute_val(child, 'val') or '*'
                continue
            if tag == 'lvlJc':
                nm_set.lvl_jc = \
                    XmlPreprocessor.get_clear_attribute_val(child, 'val') or 'left'
                continue
        sect.sets.append(nm_set)

    def log_msg(self, msg: str) -> None:
        if self.log_func:
            self.log_func(msg)

    def assign_simple_bullet_symbols(self):
        bullet_symbols = self.enabled_bullet_symbols
        bullet_index = 0
        bullet_map = {}  # type: Dict[str, str]

        for col_id in self.collections:
            section = self.collections[col_id]
            for num_set in section.sets:
                if num_set.num_fmt != 'bullet':
                    continue
                if num_set.lvl_text in bullet_symbols:
                    continue

                bul_smb = bullet_map.get(num_set.lvl_text)
                if not bul_smb:
                    bul_smb = bullet_symbols[bullet_index]
                    bullet_map[num_set.lvl_text] = bul_smb
                    bullet_index += 1
                    bullet_index = bullet_index \
                        if bullet_index < len(bullet_symbols) else 0
                num_set.lvl_text = bul_smb
