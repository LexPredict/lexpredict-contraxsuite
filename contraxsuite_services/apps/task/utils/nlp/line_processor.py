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
import re

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class LineOrPhrase:
    def __init__(self, text='', start=0):
        self.text = text
        self.start = start
        self.ending = ''

    def get_end(self):
        return self.start + len(self.text)

    def __repr__(self):
        return self.text + '->' + self.ending


class SingleWord:
    def __init__(self, text='', start=0, is_separator=False):
        self.text = text
        self.start = start
        self.is_separator = is_separator

    def get_end(self):
        return self.start + len(self.text)


class LineSplitParams:
    def __init__(self):
        # line breaks are newline characters
        # but also they can be '.' or ';' to break the line on phrases
        self.line_breaks = set()
        self.line_breaks.add('\n')

        # abbreviations endin up with '.' (like "Nr.")
        # should not break line on phrases
        self.abbreviations = []

        self.abbr_ignore_case = True


WordList = List[SingleWord]
StringList = List[str]


# splits text by phrases
# finds an ending for each phrase and clues the phrases
#  back by their endings
class LineProcessor:
    default_length = 95
    max_possible_length = 200
    min_possible_length = 50
    line_tail_percent = 60
    word_separator_pattern = re.compile(r"[\w]+[\w-]*")
    default_split_params = LineSplitParams()

    def __init__(self, allow_breaks_in_phrase: bool = True):
        self.line_length = LineProcessor.default_length
        self.tail_length = int(self.line_length * LineProcessor.line_tail_percent / 100)
        self.allow_breaks_in_phrase = allow_breaks_in_phrase

    # does the same as remove_blanks_from_phrases but doesn't
    #  use nltk for splitting the text into phrases
    def remove_double_breaks_lang_agnostic(self, text: str) -> str:
        if len(text) < LineProcessor.default_length:
            return text
        self.determine_line_length(text)

        # split text into [[line, break], [...]]
        lines = self.split_text_on_line_with_endings(text)

        # remove double line breaks
        for line in lines:
            # one or no line break
            if len(line[1]) < 2:
                continue
            breaks_count = 2 if len(line[0]) < self.tail_length else 1
            line[1] = line[1][:breaks_count]

        # merge lines
        text = ''
        for line in lines:
            text += line[0]
            text += line[1]

        return text

    # determine line length inside the document
    # enormously large parts of text are considered as fluctuations
    def determine_line_length(self, text: str) -> int:
        lens = []  # line length percentiles' array
        ln = 0
        ws_tail = 0
        for ch in text:
            if ch == '\n':
                if ln > 1:
                    lens.append(ln)
                    ln = 0
                    ws_tail = 0
                    continue
            if ch == '' or ch == '\t':
                ws_tail += 1
                continue
            ln += ws_tail
            ws_tail = 0
            ln += 1

        if ln > 1:
            lens.append(ln)

        if len(lens) == 0:
            self.line_length = LineProcessor.default_length
        else:
            lens.sort(reverse=True)
            max_100 = min(LineProcessor.max_possible_length, lens[0])

            # compare max_100 with the 95th percentile
            index_95 = int((100 - 95) * len(lens) / 100)
            max_95 = min(LineProcessor.max_possible_length, lens[index_95])
            max_len = max_95 if max_100 > int(1.5 * max_95) else max_100
            self.line_length = max(max_len, LineProcessor.min_possible_length)
        self.tail_length = int(LineProcessor.line_tail_percent * self.line_length / 100)

    # split text on lines or phrases (LineOrPhrase),
    # returning iterator
    def split_text_on_line_with_endings(self, text: str, ptrs: LineSplitParams = None) -> LineOrPhrase:
        if ptrs is None:
            ptrs = LineProcessor.default_split_params

        line = None
        text_ended = False
        i = -1

        for ch in text:
            i += 1
            if ch in ptrs.line_breaks:
                if line is not None:
                    # is this "line break" a part of abbreviation?
                    # e.g. Abs. or Nr. ?
                    if self.line_ended_with_abbreviation(line.text + ch, ptrs):
                        line.text += ch
                        continue

                    text_ended = True
                    line.ending += ch
                continue

            if line is None:
                line = LineOrPhrase(ch, i)
                continue

            if text_ended:
                new_line = LineOrPhrase(ch, i)
                yield line
                line = new_line
                text_ended = False
            else:
                line.text += ch

        if line is not None:
            if len(line.text) > 0:
                yield line

    def line_ended_with_abbreviation(self, line: str, ptrs: LineSplitParams) -> bool:
        if len(ptrs.abbreviations) == 0:
            return False
        if ptrs.abbr_ignore_case:
            line = line.lower()
        for abbr in ptrs.abbreviations:
            if line.endswith(abbr):
                return True
        return False

    # split text on words and separators, both are SingleWord instances
    def split_text_on_words(self, text: str) -> WordList:
        words = []
        last_end = 0
        for m in re.finditer(LineProcessor.word_separator_pattern, text):
            pos = m.start()
            if pos > last_end:
                words.append(SingleWord(text[last_end:pos], last_end, True))

            words.append(SingleWord(m.group(), pos, False))
            last_end = pos + len(words[-1].text)

        if last_end < len(text):
            words.append(SingleWord(text[last_end:-1], last_end, True))

        return words

    def words_to_lowercase(words: WordList):
        for word in words:
            if not word.is_separator:
                word.text = word.text.lower()

    # src_phrase is a list of SingleWord (either words or separators)
    # check_start - position from which the src_phrase is being tested
    # checking_phrases - something like [ 'jede', 'ein', [ 'im', 'sinne'], 'der' ... ]
    def check_phrase_starts_with_phrase(self, src_phrase: WordList, check_start: int,
                                        checking_phrases) -> bool:
        if src_phrase[check_start].is_separator:
            return False
        wrd = src_phrase[check_start].text
        for check_phrase in checking_phrases:

            # check for a single word,
            # e.g. ('sämtliche Anteile von der REIT-Aktiengesellschaft', 1, ['von'])) -> True
            if isinstance(check_phrase, str):
                if wrd == check_phrase:
                    return True
                continue

            # check for a sub-phrase,
            # e.g. ('sämtliche Anteile Im Sinne der REIT-Aktiengesellschaft', 1, [['im', 'sinne']])) -> True
            pattern_index = 0
            for i in range(check_start, len(src_phrase)):
                if src_phrase[i].is_separator:
                    continue
                if src_phrase[i].text == check_phrase[pattern_index]:
                    if pattern_index == len(check_phrase) - 1:
                        return True
                    pattern_index += 1
                    continue
                break
        return False
