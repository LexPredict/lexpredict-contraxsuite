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

from typing import List

from apps.task.utils.text_extraction.xml_wordx.xml_wordx_numbering import XmlWordxNumbering

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DocLine:
    PAD_BY_INDENT = {}

    def __init__(self,
                 line: str,
                 indent: int = 0):
        self.line = line
        self.indent = indent

    def __repr__(self):
        return DocLine.PAD_BY_INDENT[self.indent] + self.line

    @staticmethod
    def init_pad_by_indent():
        for i in range(200):
            DocLine.PAD_BY_INDENT[i] = ' ' * i


DocLine.init_pad_by_indent()


class WordxSerializationSettings:
    def __init__(self,
                 table_col_st: str = '\t',
                 table_indent: int = 4,
                 url_format: str = '{0} ({1})'):
        self.table_col_st = table_col_st
        self.table_indent = table_indent
        self.url_format = url_format


class SerializationContext:
    def __init__(self,
                 lines: List[DocLine],
                 settings: WordxSerializationSettings,
                 numbering: XmlWordxNumbering,
                 indent: int = 0):
        self.lines = lines
        self.settings = settings
        self.numbering = numbering
        self.indent = indent

    def get_shallow_copy(self):
        return SerializationContext(self.lines,
                                    self.settings,
                                    self.numbering,
                                    self.indent)
