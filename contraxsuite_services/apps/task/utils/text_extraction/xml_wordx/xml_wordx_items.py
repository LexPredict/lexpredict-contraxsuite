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

from typing import List, Any

from pandas import DataFrame

from apps.task.utils.text_extraction.xml_wordx.xml_wordx_serialization import SerializationContext, DocLine


# either DocText, DocHyperlink, DocParagraph or DocTable

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DocItem:
    def is_plain(self):
        return True

    def serialize(self, context: SerializationContext):
        raise NotImplementedError()

    def serialize_inline(self, context: SerializationContext) -> str:
        raise NotImplementedError()


# inline text, usually is embedded into paragraph
class DocText(DocItem):
    def __init__(self, text: str):
        self.text = text

    def is_plain(self):
        return True

    def __repr__(self):
        return self.text

    def serialize(self, context: SerializationContext):
        context.lines.append(DocLine(self.text))
        # context.prev_item = self

    def serialize_inline(self,
                         context: SerializationContext) -> str:
        # context.prev_item = self
        return self.text


# hyperlink, usually is embedded into paragraph
class DocHyperlink(DocItem):
    def __init__(self, text: str = '', link: Any = ''):
        self.text = text
        self.link = link  # XmlWordxRelation

    def is_plain(self):
        return True

    def __repr__(self):
        return f'{self.text} ({self.link})'

    def serialize(self, context: SerializationContext):
        line = self.serialize_inline(context)
        context.lines.append(DocLine(line))
        # context.prev_item = self

    def serialize_inline(self,
                         context: SerializationContext) -> str:
        if not self.link:
            return self.text

        if not self.text:
            return self.link.target if self.link else ''

        # context.prev_item = self
        return context.settings.url_format.format(self.text, self.link.target)


# paragraph that can include a number of DocText or Hyperlink records
class DocParagraph(DocItem):
    def __init__(self,
                 text_items: List[DocItem] = None,
                 style: str = ''):
        self.text_items = text_items or []
        self.style = style
        self.list_level = 0
        self.list_number = None  # type: int

    def is_plain(self):
        return True

    def __repr__(self):
        return ' '.join([str(i) for i in self.text_items])

    def serialize(self, context: SerializationContext):
        line = ''.join([i.serialize_inline(context) for i in self.text_items])
        list_marker = self.get_list_marker(context)
        line = list_marker + line
        # TODO: override and extra formatting here
        is_header = self.style and self.style.lower().startswith('heading')
        context.lines.append(DocLine(line,
                                     indent=context.indent))
        if not self.is_list_paragraph() and not is_header and line:
            context.lines.append(DocLine(''))

    def serialize_inline(self,
                         context: SerializationContext) -> str:
        line = ''.join([i.serialize_inline(context) for i in self.text_items])
        return line

    def get_list_marker(self, context: SerializationContext) -> str:
        if self.list_number is None:
            return ''
        blt = context.numbering.get_bullet(self) + ' '
        return blt

    def is_list_paragraph(self) -> bool:
        return self.style == 'ListParagraph'


class DocTableRow:
    def __init__(self):
        self.cells = []  # type: List[List[DocItem]]

    def __repr__(self):
        return '\t'.join([str(c) for c in self.cells])


class DocTable(DocItem):
    def __init__(self):
        self.rows = []  # type: List[DocTableRow]

    def is_plain(self):
        return False

    def __repr__(self):
        return '\n'.join([str(r) for r in self.rows])

    def is_content_plain(self):
        for r in self.rows:
            for c in r.cells:
                if len(c) > 1:
                    return False
                for item in c:
                    if not item.is_plain:
                        return False
        return True

    def serialize_in_dataframe(self,
                               context: SerializationContext) -> DataFrame:
        data = []
        for row in self.rows:
            rowdata = []
            for cell in row.cells:
                cell_text = ' '.join(
                    [item.serialize_inline(context) for item in cell])
                rowdata.append(cell_text)
            data.append(rowdata)
        df = DataFrame(data=data)
        return df

    def serialize(self,
                  context: SerializationContext):
        if self.is_content_plain():
            self.serialize_plain_table(context)
        else:
            self.serialize_hierarchical_table(context)

    def serialize_inline(self,
                         context: SerializationContext) -> str:
        subcontext = context.get_shallow_copy()
        subcontext.lines = []
        self.serialize(subcontext)
        return '\n'.join([l.line for l in subcontext.lines])

    def serialize_plain_table(self,
                              context: SerializationContext):
        for row in self.rows:
            row_line = []
            for cell in row.cells:
                cell_line = ' '.join([item.serialize_inline(context)
                                      for item in cell])
                row_line.append(cell_line)
            line = context.settings.table_col_st.join(row_line)
            context.lines.append(DocLine(line, context.indent))

    def serialize_hierarchical_table(self,
                                     context: SerializationContext):
        # serialize table as a list of lists
        for row in self.rows:
            for cell in row.cells:
                for item in cell:
                    ctx = context.get_shallow_copy()
                    ctx.indent += context.settings.table_indent
                    item.serialize(ctx)
