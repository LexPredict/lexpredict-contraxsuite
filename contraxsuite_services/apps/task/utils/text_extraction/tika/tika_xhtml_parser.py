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

import math
from enum import Enum
from typing import Optional, List, Tuple, Pattern, Callable, Any
import regex as re
from html import _charref, _replace_charref

from apps.task.utils.marked_up_text import MarkedUpText, MarkedUpTable, MarkedUpTableRow, MarkedUpTableCell

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class OcrTextStoreSettings(Enum):
    # describes the way parser treats images' parsed text got from Tika
    NEVER_STORE = 'never_store'  # ignores the text (because the text can be a mess)
    STORE_IF_NO_OTHER_TEXT = 'store_no_other'  # stores the text if there's no other text than that got from images
    STORE_IF_MORE_TEXT = 'store_if_more'  # stores the images' text if it's longer than the rest of the text obtained
    STORE_ALWAYS = 'story_always'  # always stores text got from images


class XhtmlParsingSettings:
    def __init__(self,
                 remove_extra_newlines: bool = True,
                 store_url_refs: bool = True,
                 store_img_refs: bool = True,
                 ocr_sets: OcrTextStoreSettings = OcrTextStoreSettings.STORE_IF_NO_OTHER_TEXT,
                 ocr_vector_text_min_length: int = 100):
        """
        :param remove_extra_newlines: try to "smart" remove newlines in the middle of a phrase
        :param store_url_refs: add comments next to hyperlinks with the URL inside {}
        :param store_img_refs: add comments next to image tags with image URL /
        :param ocr_sets: what to do with the text obtained from image inclusions, see OcrTextStoreSettings
        :param ocr_vector_text_min_length: pairs with ocr_sets, OcrTextStoreSettings.STORE_IF_NO_OTHER_TEXT
        """
        self.remove_extra_newlines = remove_extra_newlines
        self.store_url_refs = store_url_refs
        self.store_img_refs = store_img_refs
        self.ocr_sets = ocr_sets
        self.ocr_vector_text_min_length = ocr_vector_text_min_length


class XhtmlParsingStatistics:
    def __init__(self,
                 parsed_text_len: int = 0,
                 parsed_ocr_text_len: int = 0):
        """
        :param parsed_text_len: total characters of a plain text extracted from XHTML tags, not including whitespace-s
        :param parsed_ocr_text_len: the share of text got from images (OCR)
        """
        self.parsed_text_len = parsed_text_len
        self.parsed_ocr_text_len = parsed_ocr_text_len


class TikaXhtmlParser:
    """
    TikaXhtmlParser parses XHTML string obtained from Tika into plain text
    while trying to preserve some of the source text's formatting and to store
    extra information (paragraphs, pages, tables) into designated fields of MarkedUpText.
    """
    class BlockProps:
        # describes the tag being processed
        def __init__(self,
                     start: int,
                     block_type: str,
                     label_name: str = '',
                     is_inline: bool = False):
            """
            :param start: current plain text length w/o the text within the current block
            :param block_type: "paragraph" or "heading" or "image"
            :param label_name: a label (start, end) to store in result.labels dictionary
            :param is_inline: is it an inline tag like "<a>"
            """
            self.start = start
            self.label_name = label_name
            self.is_inline = is_inline
            self.block_type = block_type

    re_tag = re.compile('<[^>]+>')
    re_tagname = re.compile('[a-zA-Z0-9_]+')
    re_name_attr = re.compile('(?<=name=")[^"]+')
    re_content_attr = re.compile('(?<=content=")[^"]+')
    re_tag_content = re.compile(r'(?<=>)[^<]+(?=</)')

    re_tag_h = re.compile(r'^h\d{1,1}$', re.IGNORECASE)

    re_tag_a = re.compile(r'(<a\s+[^>]+>.+</a>)|(<a\s+[^>]+/>)', re.IGNORECASE)
    re_tag_a_href = re.compile(r'(?<=href=")[^"]+(?=")')
    re_tag_a_name = re.compile(r'(?<=name=")[^"]+(?=")')

    re_tag_img = re.compile(r'(<img\s+[^>]+>.+</img>)|(<img\s+[^>]+/>)', re.IGNORECASE)
    re_tag_img_src = re.compile(r'(?<=src=")[^"]+(?=")')
    re_tag_img_alt = re.compile(r'(?<=alt=")[^"]+(?=")')

    re_multi_space_single_newline = re.compile(r'\s{2,}\n(?=[^\n])')
    re_single_newline = re.compile(r'(?<=[^\n])\n\s*(?=[^\n])')

    re_tag_table = re.compile(r'<table[^>]*>(.*?)</table>', re.DOTALL)
    re_tag_row = re.compile('<tr[^>]*>(.*?)</tr>', re.DOTALL)
    re_tag_cell = re.compile('(<td[^>]*>(.*?)</td>)|(<th[^>]*>(.*?)</th>)', re.DOTALL)

    re_list_start = re.compile(r'(^\s*\S[\.\s)]{1,5})|(^\d{1,3}[\.\s)]{1,5})|(^[ivxlcdm]{1,10}[\.\s)]{1,5})', re.IGNORECASE)

    str_spaces = {' ', '\t', '\n'}
    str_phrase_separators = {' ', '\t', '\n', '.', ',', '!', '?'}

    DEFAULT_PARSING_SETS = XhtmlParsingSettings()

    def __init__(self,
                 pars_settings: XhtmlParsingSettings = None):
        self.settings = pars_settings or self.DEFAULT_PARSING_SETS
        self.parse_stat = XhtmlParsingStatistics()

    def parse_text(self,
                   markup: str,
                   detect_tables: bool = True) -> MarkedUpText:
        """
        The only method to call by external code. Transforms "markup" (XHTML string)
        into plain text with some formatting and extra information stored into MarkedUpText structure.
        :param markup: string containing XHTML
        :param detect_tables: whether or not to parse and store tables (MarkedUpTable) markup information
        :return: MarkedUpText - resulted text, paragraphs, pages, headings and tables markup information
        """
        result = MarkedUpText('', {'pages': [], 'paragraphs': []})
        if detect_tables:
            result.tables = self.detect_tables(markup)

        cur_block = None  # type: Optional[TikaXhtmlParser.BlockProps]
        for tg in self.re_tag.finditer(markup):
            tag_text = tg.group(0)
            tag_name = self.get_tag_name(tag_text)
            tag_start, tag_end = (tg.start(), tg.end())
            if not tag_name:
                continue

            if tag_name == 'meta':
                self.process_meta(tag_text, result)
                continue

            tag_type = self.get_tag_type(tag_text)

            if tag_name == 'div' and 'class="page"' in tag_text:
                result.labels['pages'].append((len(result.text), 0))
                continue

            block_type = 'image' if tag_name == 'div' and 'class="ocr"' in tag_text \
                else 'paragraph' if tag_name == 'p' \
                else 'heading' if self.re_tag_h.match(tag_name) else tag_name
            is_text_block = block_type == 'paragraph' or block_type == 'heading' or block_type == 'image'

            if is_text_block and tag_type == 'o':
                if block_type == 'image' and self.settings.ocr_sets == OcrTextStoreSettings.NEVER_STORE:
                    continue
                cur_block = TikaXhtmlParser.BlockProps(tg.end(), block_type)
                if block_type == 'paragraph':
                    cur_block.label_name = 'paragraphs'
                elif block_type == 'heading':
                    cur_block.label_name = 'heading_' + tag_name[1:]
                elif block_type == 'image':
                    cur_block.label_name = 'images'
                continue

            if (is_text_block or block_type == 'div') and tag_type == 'c' and cur_block:
                end = tag_start
                line = markup[cur_block.start:end]
                p_start = len(result.text)
                p_end = p_start + len(line)
                result.text += line
                if not cur_block.is_inline:
                    result.text += '\n\n'
                if cur_block.label_name:
                    if cur_block.label_name not in result.labels:
                        result.labels[cur_block.label_name] = []
                    result.labels[cur_block.label_name].append((p_start, p_end))

                # check if the block belongs to a table
                self.update_tables_content(result.tables, tag_start, tag_end,
                                           p_start, p_end)

                cur_block = None
                continue

        l_pages = result.labels['pages']
        if l_pages:
            pages = []
            for i in range(len(l_pages) - 1):
                pages.append((l_pages[i][0], l_pages[i + 1][0]))
            pages.append((l_pages[-1][0], len(result.text)))

        self.process_inner_tags(result)
        self.post_process(result)
        self.parse_stat.parsed_text_len = result.count_non_space_chars()
        self.check_ocr_text(result)
        self.update_tables_outer_bounds(result.tables)

        return result

    def update_tables_outer_bounds(self, tables_to_process: List[MarkedUpTable]) -> None:
        """
        a "private" method to find a table by its start / end positions
        then "stretch" table's row's bounds (start / end) and table itself
        after including a new cell into that table
        :param tables_to_process: all tables detected on the step before
        """
        for table in tables_to_process:
            for row in table.rows:
                for cell in row.cells:
                    if cell.content_coords:
                        row.content_coords = cell.content_coords if not row.content_coords \
                            else (row.content_coords[0], cell.content_coords[1])
                        table.content_coords = cell.content_coords if not table.content_coords \
                            else (table.content_coords[0], cell.content_coords[1])

    def update_tables_content(self,
                              tables_to_process: List[MarkedUpTable],
                              tag_start: int,
                              tag_end: int,
                              cont_start: int,
                              cont_end: int) -> None:
        """
        a "private" method finding a table (by its bounds) and including current
        tag with its source (relative to source XHTML) and resulting (relative
        to resulting plain text)
        :param tables_to_process: list of MarkedUpTable those start / end positions are already detected
        :param tag_start: current tag's (<td> or <th> probably) start position relative to the source XHTML
        :param tag_end: current tag's end position relative to the source XHTML
        :param cont_start: current tag's start position relative to the resulting plain text
        :param cont_end: current tag's end position relative to the resulting plain text
        """
        for table in tables_to_process:
            if table.end <= tag_start:
                continue
            if table.start >= tag_end:
                break
            # tables can be nested, so we may check several tables here
            for row in table.rows:
                if row.end <= tag_start:
                    continue
                if row.start >= tag_end:
                    break
                for cell in row.cells:
                    if cell.end <= tag_start:
                        continue
                    if cell.start >= tag_end:
                        break
                    cell.content_coords = (cont_start, cont_end) if not cell.content_coords \
                        else (cell.content_coords[0], cont_end)
                    break
                break

    def process_meta(self, tag_text: str, result: MarkedUpText) -> None:
        """
        a "private" method to get metadata from a tag like <meta name="pdf:PDFVersion" content="1.4"/>
        :param tag_text: <meta> tag's full text
        :param result: MarkedUpText variable to store tag's value in
        """
        meta_name = ''
        for match in self.re_name_attr.finditer(tag_text):
            meta_name = match.group(0)
            break
        if not meta_name:
            return

        meta_val = ''
        for match in self.re_content_attr.finditer(tag_text):
            meta_val = match.group(0)
            break
        result.meta[meta_name] = meta_val

    @staticmethod
    def get_tag_name(tag_text: str) -> str:
        """
        a "private" method to get tag's name from tag's markup
        :param tag_text: tag's markup
        :return: tag's name
        """
        matches = TikaXhtmlParser.re_tagname.finditer(tag_text)
        for match in matches:
            return match.group(0).lower()
        return ''

    @staticmethod
    def get_tag_type(tag_text: str) -> str:
        """
        a "private" method to get tag's type (opening or closing) from tag's markup
        :param tag_text: tag's markup
        :return: tag's type: "o" for opening tag, "c" for closing and "co" for self-closing tag like <img ... />
        """
        if '/' not in tag_text:
            return 'o'  # opening
        if tag_text.startswith('</'):
            return 'c'  # closing
        return 'co'  # self-closing

    def process_inner_tags(self, result: MarkedUpText) -> None:
        """
        a "private" method to find and process (transform into plain text)
        sub-tags of all known types within a tag, like <a>-s and <img>-s within <p>
        :param result: a MarkedUpText variable with plain text to process
        """
        regex_function = [(self.re_tag_a, self.extract_hyperlink),
                          (self.re_tag_img, self.extract_image)]
        for reg, get_text_func in regex_function:
            self.process_inner_tag(result, reg, get_text_func)

    def process_inner_tag(self,
                          result: MarkedUpText,
                          tag_regex: Pattern,
                          make_text_function: Callable[[Any], str]) -> None:
        """
        this "private" method finds tags inside text, given it's start and end positions
        and stores labels found in result
        :param result: a MarkedUpText variable with plain text to process
        :param tag_regex: tag to find
        :param make_text_function: method that processes the tag found transforming the tag into plain text
        """
        new_text = ''
        transformations = []  # type: List[Tuple[Tuple[int, int], Tuple[int, int]]]
        last_stop = 0
        new_labels = []

        for match in tag_regex.finditer(result.text):
            link_markup = make_text_function(match)
            src_s, src_e = (match.start(), match.end())
            # ensure spaces between text and link text
            starts_space = src_s == 0 or result.text[src_s - 1] in self.str_spaces
            ends_space = src_e == len(result.text) - 1 or result.text[src_e + 1] in self.str_phrase_separators
            if not starts_space:
                link_markup = ' ' + link_markup
            if not ends_space:
                link_markup += ' '

            end_e = src_s + len(link_markup)
            if end_e != src_e:
                transformations.append(((src_s, src_e), (src_s, end_e)))
            new_labels.append((src_s, end_e))

            new_text += result.text[last_stop: src_s]
            new_text += link_markup
            last_stop = src_e

        new_text += result.text[last_stop: len(result.text)]
        result.text = new_text
        if transformations:
            result.apply_transformations(transformations)
        if new_labels:
            if 'a' not in result.labels:
                result.labels['a'] = new_labels
            else:
                result.labels['a'] = result.labels['a'] + new_labels

    def extract_hyperlink(self, match) -> str:
        """
        this "private" method transforms <a ...> tag's regexp capture
        into plain text
        :param match: <a ...> tag's regexp capture (match)
        :return: hyperlink's plain text representation
        """
        tag = match.group()
        link_text = ''
        for link_text_match in self.re_tag_content.finditer(tag):
            link_text = link_text_match.group(0)
            break
        link_href = ''
        for link_href_match in self.re_tag_a_href.finditer(tag):
            link_href = link_href_match.group(0)
            break
        if not link_text and not link_href:
            link_name = ''
            for link_name_match in self.re_tag_a_name.finditer(tag):
                link_name = link_name_match.group(0)
                break
            link_text = f'{{{link_name}}}'
        link_markup = f'{link_text} [{link_href}]' \
            if self.settings.store_url_refs and link_href else link_text
        return link_markup

    def extract_image(self, match) -> str:
        """
        this "private" method transforms <img ...> tag's regexp capture
        into plain text
        :param match: <img ...> tag's regexp capture (match)
        :return: <img> tag's plain text representation
        """
        tag = match.group()
        image_text = ''
        for image_text_match in self.re_tag_content.finditer(tag):
            image_text = image_text_match.group(0)
            break
        img_src = ''
        for img_src_match in self.re_tag_img_src.finditer(tag):
            img_src = img_src_match.group(0)
            break
        if not image_text:
            img_alt = ''
            for img_alt_match in self.re_tag_img_alt.finditer(tag):
                img_alt = img_alt_match.group(0)
                break
            image_text = f' {{{img_alt}}}' if img_alt else ''
        image_markup = f'image:{image_text} [{img_src}]' \
            if self.settings.store_img_refs and img_src else f'image: [{image_text}]'
        return image_markup

    def post_process(self, result: MarkedUpText) -> None:
        """
        a "private" method to post-process plain text: remove
        extra newlines, unescape HTML codes like &gt; with corresponding symbols
        :param result: MarkedUpText with resulted plain text
        """
        # TODO: process hrefs, correct labels
        if not result.text:
            return
        if self.settings.remove_extra_newlines:
            # result.replace_by_regex(self.re_single_newline, ' ')
            self.remove_extra_linebreaks(result)
        self.unescape(result)

    def remove_extra_linebreaks(self, result: MarkedUpText) -> None:
        """
        Removes linebreaks in the middle of the sentence. Usually, single linebreaks
        within a paragraph should be deleted and replaced with one space character.
        But we preserve the linebreaks if the paragraph is a list or a table.
        Unfortunately, presently we can't recognize a paragraph as a table (if the
        source is a PDF file).
        :param result: MarkedUpText containing resulted plain text
        """
        paragraphs = result.labels.get('paragraphs') or [(0, len(result.text))]
        for par_start, par_end in paragraphs:
            # check the paragraph is not a list and, therefore, can be
            # cleared of extra line breaks
            par_text = result.text[par_start: par_end]
            par_lines = [l for l in par_text.split('\n') if l.strip()]
            if not par_lines:
                continue

            # if lines make a list then don't remove line breaks
            is_list = True
            list_lines = 0
            for line in par_lines:
                if self.re_list_start.match(line):
                    list_lines += 1
            max_breaks_allowed = math.ceil(len(par_lines) / 3)
            if len(par_lines) - list_lines > max_breaks_allowed:
                is_list = False

            if not is_list:
                result.replace_by_regex(self.re_single_newline, ' ', par_start, par_end)

    @staticmethod
    def unescape(result: MarkedUpText) -> None:
        """
        a "private" method to replace HTML codes like &gt; with corresponding symbols in
        the resulting plain text
        :param result: MarkedUpText containing resulting plain text
        """
        new_text = ''
        transformations = []  # type: List[Tuple[Tuple[int, int], Tuple[int, int]]]
        last_stop = 0

        for match in _charref.finditer(result.text):
            replacement = _replace_charref(match)
            src_s, src_e = (match.start(), match.end())
            end_e = src_s + len(replacement)
            if end_e != src_e:
                transformations.append(((src_s, src_e), (src_s, end_e)))
            new_text += result.text[last_stop: src_s]
            new_text += replacement
            last_stop = src_e

        new_text += result.text[last_stop: len(result.text)]
        result.text = new_text
        if transformations:
            result.apply_transformations(transformations)

    def detect_tables(self, text: str) -> List[MarkedUpTable]:
        """
        a "private" method called while parsing the source markup to
        detect tables and store them as MarkedUpTable records. Each MarkedUpTable
        stores start /end positions (relative to resulting text) of each row, cell
        and the table itself.
        :param text: plain text to find tables in
        :return: list of MarkedUpTable
        """
        tables = []  # type: List[MarkedUpTable]
        for match_table in self.re_tag_table.finditer(text):
            table = MarkedUpTable(match_table.start(), match_table.end())
            tables.append(table)
            table_text = text[table.start:table.end]
            for match_row in self.re_tag_row.finditer(table_text):
                row = MarkedUpTableRow(match_row.start() + table.start,
                                       match_row.end() + table.start)
                table.rows.append(row)
                row_text = table_text[match_row.start():match_row.end()]
                for match_cell in self.re_tag_cell.finditer(row_text):
                    cell = MarkedUpTableCell(match_cell.start() + row.start,
                                             match_cell.end() + row.start)
                    row.cells.append(cell)

        return tables

    def check_ocr_text(self, result: MarkedUpText) -> None:
        """
        a "private" method that checks text obtained from embedded images
        The method decides whether to leave or to delete these pieces of text
        :param result: MarkedUpText, containing resulting plain text
        """
        if not result.text or 'images' not in result.labels:
            return

        # remove some of OCR-d text fragments or remove all of them or just quit
        if self.settings.ocr_sets == OcrTextStoreSettings.NEVER_STORE:
            return

        images = result.labels['images']
        self.parse_stat.parsed_ocr_text_len = sum([result.count_non_space_chars(l_s, l_e)
                                                   for l_s, l_e in images])
        self.parse_stat.parsed_text_len -= self.parse_stat.parsed_ocr_text_len
        if self.settings.ocr_sets == OcrTextStoreSettings.STORE_ALWAYS:
            return

        remove_ocrs = False
        if self.settings.ocr_sets == OcrTextStoreSettings.STORE_IF_NO_OTHER_TEXT and \
                self.parse_stat.parsed_text_len >= self.settings.ocr_vector_text_min_length:
            remove_ocrs = True

        if self.settings.ocr_sets == OcrTextStoreSettings.STORE_IF_MORE_TEXT and \
                self.parse_stat.parsed_text_len > self.parse_stat.parsed_ocr_text_len:
            remove_ocrs = True

        if not remove_ocrs:
            return

        transformations = [(l, (l[0], l[0])) for l in images]
        result.apply_transformations(transformations)
