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

from apps.common.collection_utils import leave_unique_values
from apps.task.utils.text_segments import DocumentSection
import regex as re

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
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
                rowdata.append(cell_text or '')
            data.append(rowdata or '')
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
    BLOCK_MARKERS = {
        'paragraphs': ('{{##PF', 'PF##}}',),
        'images': ('{{##IM', 'IM##}}',),
        'a': ('{{##AN', 'AN##}}',),
        'pages': ('{{##PG', 'PG##}}',),
        'heading_1': ('{{##H1', 'H1##}}',),
        'heading_2': ('{{##H2', 'H2##}}',),
        'heading_3': ('{{##H3', 'H3##}}',),
        'heading_4': ('{{##H4', 'H4##}}',),
        'heading_5': ('{{##H5', 'H5##}}',),
        'heading_6': ('{{##H6', 'H6##}}',),
        'heading_7': ('{{##H7', 'H7##}}',),
        'heading_8': ('{{##H8', 'H8##}}',),
        'heading_9': ('{{##H9', 'H9##}}',),
        'table': ('{{##TB', 'TB##}}',),
        'tr': ('{{##TR', 'TR##}}',),
        'td': ('{{##TD', 'TD##}}',),
    }
    MARKER_TEXT_LEN = len('<<##PF')

    def __init__(self, text: str,
                 labels: Optional[Dict[str, List[Tuple[int, int]]]] = None,
                 tables: Optional[List[MarkedUpTable]] = None,
                 meta: Optional[Dict[str, str]] = None):
        self.text = text
        self.markers_extra_text_length = 0
        self.labels = labels or {}
        self.tables = tables or []
        self.meta = meta or {}

    def __repr__(self) -> str:
        text_short = self.text or ''
        text_short = text_short if len(text_short) < 128 else text_short[:126] + '...'

        labels = ', '.join([f'{l}: {len(self.labels[l])}' for l in self.labels])
        return f'{text_short}, labels: {labels}'

    @property
    def pure_text_length(self) -> int:
        return len(self.text or '') - self.markers_extra_text_length

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

    def add_marker(self, label: str, is_open: bool, position=-1):
        marker_text = self.get_marker(label, is_open)
        if position < 0 or position == len(self.text):
            self.text += marker_text
        else:
            self.text = self.text[:position] + marker_text + self.text[:position]
        self.markers_extra_text_length += len(marker_text)

    @classmethod
    def get_marker(cls, label: str, is_open: bool):
        marker = cls.BLOCK_MARKERS[label]
        return marker[0] if is_open else marker[1]

    def convert_markers_to_labels(self):
        # label - is opening - position - original position
        marker_coords = []  # type: List[Tuple[str, bool, int, int]]

        # add ' ' to empty table cell so as the cells won't collapse
        empty_cell_text = ''.join(self.BLOCK_MARKERS['td'])
        empty_cell_text_replace = ' '.join(self.BLOCK_MARKERS['td'])
        self.text = self.text.replace(empty_cell_text, empty_cell_text_replace)

        # find coords for all markers
        for label in self.BLOCK_MARKERS:
            for i in range(len(self.BLOCK_MARKERS[label])):
                marker = self.BLOCK_MARKERS[label][i]
                is_opening = i == 0

                start = 0
                while True:
                    marker_start = self.text.find(marker, start)
                    if marker_start < 0:
                        break
                    start = marker_start + len(marker)
                    marker_coords.append((label, is_opening, marker_start, marker_start,))

        # sort markers by position
        marker_coords.sort(key=lambda m: m[2])

        # cut markers from text, shifting the following markers left
        for i in range(len(marker_coords)):
            _label, _is_op, pos, orig_pos = marker_coords[i]
            self.text = self.text[:pos] + self.text[pos + self.MARKER_TEXT_LEN:]
            # shift other markers
            for j in range(i + 1, len(marker_coords)):
                marker_coords[j] = (marker_coords[j][0],
                                    marker_coords[j][1],
                                    marker_coords[j][2] - self.MARKER_TEXT_LEN,
                                    marker_coords[j][3],)

        # make unpaired labels from marker_coords
        for label, is_op, position, orig_pos in marker_coords:
            lst = self.labels.get(label)
            if not lst:
                lst = []
                self.labels[label] = lst
            lst.append((position, is_op, orig_pos, ))

        # make label pairs (opening / closing) from unpaired labels
        for label in self.labels:
            lst = self.labels[label]
            lst.sort(key=lambda p: p[0] * 100 + p[2] * 10 + (1 if p[1] else 0))
            paired_list = []
            tag_stack = []  # type: List[int]
            for position, is_open, _ in lst:
                if is_open:
                    tag_stack.append(position)
                    continue
                if not tag_stack:
                    continue
                paired_list.append((tag_stack[-1], position))
                tag_stack = tag_stack[:-1]
            self.labels[label] = paired_list
        self.untangle_self_closing_tags()
        self.detect_tables()

    def untangle_self_closing_tags(self):
        # self-closing tags looks like
        # [(0, 0), (901, 901), (1460, 1460)]
        # instead, we should transform to
        # [(0, 901), (901, 1460), (1460, text_length)]
        self_clos_tags = ['pages']
        for label in self_clos_tags:
            lst = self.labels.get(label)
            if not lst:
                continue

            untangled = []
            last_index = len(lst) - 1
            for i in range(len(lst)):
                next_pos = lst[i + 1][0] if i < last_index else len(self.text)
                untangled.append((lst[i][0], next_pos,))
            self.labels[label] = untangled

    def detect_tables(self) -> None:
        """
        a "private" method called while parsing the source markup to
        detect tables and store them as MarkedUpTable records. Each MarkedUpTable
        stores start /end positions (relative to resulting text) of each row, cell
        and the table itself.
        Should be called after postprocessing text and transforming marks into labels

        :param text: MarkedUpText text to find tables in
        """
        if 'table' not in self.labels or 'tr' not in self.labels or 'td' not in self.labels:
            return
        table_labels, row_labels, cell_labels = \
            self.labels['table'], self.labels['tr'], self.labels['td']

        for t_start, t_end in table_labels:
            table = MarkedUpTable(t_start, t_end)
            self.tables.append(table)

            table_row_labels = [l for l in row_labels if table.start <= l[0] <= table.end
                                and table.start <= l[1] <= table.end]
            # skip rows in embedded tables
            em_tables = self.get_embedded_table_bounds(t_start, t_end, table_labels)
            table_row_labels = leave_unique_values(
                [l for l in table_row_labels
                 if not self.is_cell_in_table(l[0], l[1], em_tables)])

            for row_start, row_end in table_row_labels:
                row = MarkedUpTableRow(row_start, row_end)
                table.rows.append(row)
                row_cell_labels = [l for l in cell_labels if row_start <= l[0] < row_end and
                                   row_start <= l[1] <= row_end]
                row_cell_labels = leave_unique_values(
                    [l for l in row_cell_labels
                     if not self.is_cell_in_table(l[0], l[1], em_tables)])

                for cell_start, cell_end in row_cell_labels:
                    cell = MarkedUpTableCell(cell_start, cell_end)
                    cell.content_coords = (cell_start, cell_end,)
                    row.cells.append(cell)

    def get_embedded_table_bounds(self, start: int, end: int,
                                  table_labels: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        em_tabs = []  # type: List[Tuple[int, int]]
        for t_start, t_end in table_labels:
            if (t_start > start and t_end <= end) or \
               (t_start >= start and t_end < end):
                em_tabs.append((t_start, t_end,))
        return em_tabs

    @classmethod
    def is_cell_in_table(cls, start: int, end: int, tables: List[Tuple[int, int]]):
        for t_start, t_end in tables:
            if t_start <= start <= t_end and t_start <= end <= t_end:
                if t_start != start or t_end != end:
                    return True
        return False
