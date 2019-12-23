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

from typing import Any, List

import regex as re

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class XmlPreprocessor:
    reg_namespace = re.compile(r"\{[^\}]+\}")

    @staticmethod
    def get_clear_attributes(node: Any):
        cl_atrs = {}
        if not hasattr(node, 'attrib'):
            return cl_atrs
        for atr in node.attrib:
            atr_clear = XmlPreprocessor.remove_namespace(atr)
            cl_atrs[atr_clear] = node.attrib[atr]
        return cl_atrs

    @staticmethod
    def get_clear_attribute_val(node, atr_name) -> str:
        attrs = XmlPreprocessor.get_clear_attributes(node)
        return attrs.get(atr_name)

    @staticmethod
    def get_clear_tag(node: Any) -> str:
        return XmlPreprocessor.remove_namespace(node.tag)

    @staticmethod
    def remove_namespace(text: str) -> str:
        text = XmlPreprocessor.reg_namespace.sub('', text)
        text = text.strip(' \t')
        return text

    @staticmethod
    def find_children_by_tag(node: Any,
                             tag: str,
                             lookup_all_levels=False,
                             first_only=False) -> List[Any]:
        items = []
        XmlPreprocessor.fill_children_by_tag(node, tag, items,
                                             lookup_all_levels, first_only)
        return items

    @staticmethod
    def fill_children_by_tag(node: Any,
                             tag: str,
                             found_items: List[Any],
                             lookup_all_levels=False,
                             first_only=False) -> None:
        go_deeper = True
        for child in node:
            clear_tag = XmlPreprocessor.get_clear_tag(child)
            if clear_tag == tag:
                found_items.append(child)
                if first_only:
                    return
                go_deeper = lookup_all_levels
        if not go_deeper:
            return
        for child in node:
            XmlPreprocessor.fill_children_by_tag(child, tag, found_items,
                                                 lookup_all_levels, first_only)


class NumberConverter:
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syb = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    syb_lower = [
        "m", "cm", "d", "cd",
        "c", "xc", "l", "xl",
        "x", "ix", "v", "iv",
        "i"
    ]

    chars_count = ord('z') - ord('a')

    @staticmethod
    def int_to_roman(num: int, uppercase: bool = True) -> str:
        val = NumberConverter.val
        syb = NumberConverter.syb if uppercase else NumberConverter.syb_lower

        roman_num = ''
        i = 0
        while num > 0:
            for _ in range(num // val[i]):
                roman_num += syb[i]
                num -= val[i]
            i += 1
        return roman_num

    @staticmethod
    def int_to_letter(num: int, uppercase: bool = True) -> str:
        num -= 1
        start = 'A' if uppercase else 'a'
        if num < NumberConverter.chars_count:
            return chr(ord(start) + num)
        a = num // NumberConverter.chars_count
        b = num % NumberConverter.chars_count
        return chr(ord(start) + a - 1) + chr(ord(start) + b)
