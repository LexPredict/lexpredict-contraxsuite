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

import pandas as pd
from typing import Optional, Dict, List, Tuple, Pattern
from apps.task.utils.text_segments import DocumentSection
import regex as re

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class MarkedUpTableCell:
    """
    A cell (<td> or <th>) inside MarkedUpTable. The class stores
    cell's start and and position within the source text (XHTML) and relative
    to resulting plain text as well ass flags like "rowspan=..."
    """
    def __init__(self, start: int, end: int, flags: str = ''):
        """
        :param start: cell's start in the source text
        :param end: cell's end in the source text
        :param flags: any possible flags like "rowspan=N"
        """
        self.start = start
        self.end = end
        self.flags = flags
        # start - end of the cell (cell's content) in the resulted plain text
        self.content_coords = None  # type: Optional[Tuple[int, int]]

    def __repr__(self):
        return f'<td>{self.start}, {self.end}</td>'


class MarkedUpTableRow:
    """
    A row (<tr>) inside MarkedUpTable. The class stores cells' collection,
    row's start and and position within the source text (XHTML) and relative
    to resulting plain text as well ass flags like "colspan=..."
    """
    def __init__(self, start: int, end: int, flags: str = ''):
        """
        :param start: row's start in the source text
        :param end: row's end in the source text
        :param flags: any possible flags like "head" if the row is in table's head tag
        """
        self.start = start
        self.end = end
        self.flags = flags
        self.cells = []  # type: List[MarkedUpTableCell]
        # start - end of the row (row's content) in the resulted plain text
        self.content_coords = None  # type: Optional[Tuple[int, int]]

    def __repr__(self):
        cells_s = ' '.join([str(c) for c in self.cells])
        return f'  <tr coords="{self.start, self.end}">\n    {cells_s}\n  </tr>'


class MarkedUpTable:
    """
    The class represents a table within a document. For the table it stores:
    - table coordinates relative to both source (XHTML) and resulting (plain) text
    - rows + cells inside with their coordinates and flags
    """
    def __init__(self, start: int, end: int):
        """
        :param start: table's start in the source text
        :param end: table's end in the source text
        """
        self.start = start
        self.end = end
        self.rows = []  # type: List[MarkedUpTableRow]
        # start - end of the table (table's content) in the resulted plain text
        self.content_coords = None  # type: Optional[Tuple[int, int]]

    def __repr__(self):
        return f'<table coords="{self.start, self.end}">\n' + '\n'.join([str(r) for r in self.rows]) + '\n</table>'

    def serialize_in_dataframe(self,
                               source_text: str) -> pd.DataFrame:
        """
        Save the table as Pandas dataframe - text only, w/o positioning information
        :param source_text: source text to extract table's text, because table itself doesn't store text - coords only
        :return: pandas dataframe
        """
        data = []
        for row in self.rows:
            rowdata = []
            for cell in row.cells:
                cell_text = '' if not cell.content_coords \
                    else source_text[cell.content_coords[0]:cell.content_coords[1]]
                rowdata.append(cell_text)
            data.append(rowdata)
        df = pd.DataFrame(data=data)
        return df

    def make_coord_list(self) -> List[Tuple[int, int]]:
        """
        Makes a plain list of coordinates of each cell. The method is used by code
        that "transforms" the text, trimming or stretching parts of the text.
        :return: cells' coordinates like [(start0, end0), (start1, end1) ...]
        """
        labels = []
        for row in self.rows:
            for cell in row.cells:
                if cell.content_coords:
                    labels.append(cell.content_coords)
        return labels

    def update_coords(self, coords: List[Tuple[int, int]]) -> None:
        """
        Applies "transformed" (trimmed, shifted or stretched) cells' coordinates to the cells themselves
        :param coords: cells' coordinates plain list like [(start0, end0), (start1, end1) ...]
        """
        if not coords:
            return
        index = 0
        for row in self.rows:
            for cell in row.cells:
                if index == len(coords):
                    return
                if not cell.content_coords:
                    continue
                cell.content_coords = coords[index]
                index += 1


class MarkedUpText:
    """
    Plain text + labels + tables + metadata
    - labels is a dictionary where a key may be "paragraphs" or "heading_1" ...
      and values are a list of (start: end) numbers

    - tables is a collection of MarkedUpTable records

    - metadata is a key-value dictionary of string: string records
    """
    DEFAULT_HEADINGS = {'heading_1': 1, 'heading_2': 2, 'heading_3': 3, 'heading_4': 4}
    REG_SPACE = re.compile(r'\s|(\r\n|\r|\n)')

    def __init__(self, text: str,
                 labels: Optional[Dict[str, List[Tuple[int, int]]]] = None,
                 tables: Optional[List[MarkedUpTable]] = None,
                 meta: Optional[Dict[str, str]] = None):
        self.text = text
        self.labels = labels or {}
        self.tables = tables or []
        self.meta = meta or {}

    def __repr__(self) -> str:
        text_short = self.text or ''
        text_short = text_short if len(text_short) < 128 else text_short[:126] + '...'

        labels = ', '.join([f'{l}: {len(self.labels[l])}' for l in self.labels])
        return f'{text_short}, labels: {labels}'

    def sort_labels(self):
        """
        a method to be called after adding a number of labels to .labels mmember
        to sort each labels list by (start, _) (first) value
        """
        if not self.labels:
            return
        for key in self.labels:
            self.labels[key].sort()

    def replace_by_string(self, source_text: str, replacement: str) -> None:
        """
        Replace "source_text" with "replacement", adjusting
        labels' coordinates
        """
        if not self.text:
            return
        if not self.labels:
            self.text = self.text.replace(source_text, replacement)
            return

        repl_len = len(replacement)
        new_text = ''
        last_index = 0
        transformations = []

        while True:
            match_start = self.text.find(source_text, last_index)
            if match_start < 0:
                break
            match_end = match_start + len(source_text)
            new_text += self.text[last_index: match_start]
            new_text += replacement
            last_index = match_end
            delta = repl_len - match_end + match_start
            if delta != 0:
                transformations.append(((match_start, match_end), (match_start, match_end + delta)))

        new_text += self.text[last_index:len(self.text)]
        self.text = new_text
        self.apply_transformations(transformations)

    def replace_by_regex(self, reg: Pattern, replacement: str,
                         start: Optional[int] = None,
                         end: Optional[int] = None) -> None:
        """
        Replace phrases matching "reg" with "replacement", adjusting
        labels' coordinates
        """
        if not self.text:
            return
        if not self.labels:
            self.text = reg.sub(replacement, self.text)
            return

        repl_len = len(replacement)
        new_text = ''
        last_index = 0
        transformations = []

        text_to_check = self.text if start is None else self.text[start: end]
        start = start or 0
        for match in reg.finditer(text_to_check):
            match_start = match.start() + start
            match_end = match.end() + start
            new_text += self.text[last_index: match_start]
            new_text += replacement
            last_index = match_end
            delta = repl_len - match_end + match_start
            if delta != 0:
                transformations.append(((match_start, match_end), (match_start, match_end + delta)))

        new_text += self.text[last_index:len(self.text)]
        self.text = new_text
        self.apply_transformations(transformations)

    def apply_transformations(self, transformations: List[Tuple[Tuple[int, int], Tuple[int, int]]]) -> None:
        """
        Text might have been changed: some parts are cut or replaced by other parts.
        In this case some labels' coordinates should also be changed.
        :param transformations: [ ((source_start, source_end), (result_start, result_end)), ... ]
        """
        if not transformations or not self.labels:
            return

        label_keys = [l for l in self.labels]
        for i in range(len(self.tables)):
            self.labels[f'table#{i}'] = self.tables[i].make_coord_list()

        for key in label_keys:
            labels = self.labels[key]  # type: List[Tuple[int, int]]
            # {index: (shift_start, shift_end)}
            label_transforms = {}  # type:Dict[int, Tuple[int, int]]

            for src, rst in transformations:
                src_s, src_e = src
                rst_s, rst_e = rst

                if src_e - src_s == rst_e - rst_s:
                    continue

                delta = rst_e - rst_s - (src_e - src_s)
                new_e = src_e + delta

                for i in range(len(labels)):
                    label_s, label_e = labels[i]
                    if label_e <= src_s:
                        continue
                    old_trans = label_transforms.get(i) or (0, 0)
                    if label_s >= src_e:
                        label_transforms[i] = (old_trans[0] + delta, old_trans[1] + delta)
                        continue
                    if label_e <= new_e:
                        continue
                    if delta > 0:
                        if label_e > src_e:
                            label_transforms[i] = (old_trans[0], old_trans[1] + delta)
                        continue
                    if label_s >= new_e:
                        if label_e <= src_e:
                            label_transforms[i] = None  # label should be deleted
                            continue
                        new_len = label_e + delta - new_e
                        if new_len <= 0:
                            label_transforms[i] = None  # label should be deleted
                            continue
                        new_label_start = new_e - 1
                        new_label_end = new_e + new_len
                        label_transforms[i] = (old_trans[0] + new_label_start - label_s,
                                               old_trans[1] + new_label_end - label_e)
                        continue
                    label_transforms[i] = (old_trans[0], old_trans[1] + delta)

            for index in label_transforms:  # type: int
                transform = label_transforms[index]
                if transform is None:
                    labels[index] = None
                    continue
                labels[index] = (labels[index][0] + transform[0],
                                 labels[index][1] + transform[1])

        for i in range(len(self.tables)):
            table_key = f'table#{i}'
            self.tables[i].update_coords(self.labels[table_key])
            del self.labels[table_key]

        for key in label_keys:
            labels = self.labels.get(key)
            if not labels:
                continue
            labels = [l for l in labels if l is not None]
            self.labels[key] = labels

    def find_sections(self,
                      heading_titles: Optional[Dict[str, int]] = None) -> List[DocumentSection]:
        """
        Find fragments starting from heading_N (see labels). The heading itself with
        the following fragment is considered a "section".
        :param heading_titles: optional keys to lookup in "labels" member, if not provided looks up for "heading_1..4"
        :return: a list of DocumentSections
        """
        sections = []  # type:List[DocumentSection]

        # start, end, level
        all_headings = []  # type: List[Tuple[int, int, int]]
        heading_titles = heading_titles or self.DEFAULT_HEADINGS
        for label_key in self.labels:
            heading_level = heading_titles.get(label_key)
            if not heading_level:
                continue
            for label_s, label_e in self.labels[label_key]:
                all_headings.append((label_s, label_e, heading_level))

        all_headings.sort(key=lambda h: h[0])
        for i in range(len(all_headings)):
            heading_s, heading_e, heading_l = all_headings[i]
            title = self.text[heading_s: heading_e]
            end = all_headings[i + 1][1] if i < len(all_headings) - 1 else len(self.text)
            section = DocumentSection(heading_s, end, title, heading_s, heading_e, heading_l)
            sections.append(section)
        return sections

    def count_non_space_chars(self,
                              start: Optional[int] = None,
                              end: Optional[int] = None) -> int:
        """
        This method calculates a number of non-whitespaces characters within the
        pointed section of the text
        :param start: section's start or None (0) to start from the beginning
        :param end: section's end or None to count characters in the whole text
        :return: non-whitespace characters' count
        """
        if start is not None:
            return len(self.REG_SPACE.sub('', self.text[start:end]))
        return len(self.REG_SPACE.sub('', self.text))
