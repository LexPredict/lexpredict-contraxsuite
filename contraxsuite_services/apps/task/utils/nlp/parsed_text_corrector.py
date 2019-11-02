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
import itertools

from typing import Pattern

from apps.task.utils.nlp.line_processor import LineOrPhrase
from apps.task.utils.nlp.parsed_text_quality_estimator import ParsedTextQualityEstimator

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.3.0/LICENSE"
__version__ = "1.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class ParsedTextCorrector:

    PATTERN_MONEY_BREAK = r"""
    ([\n\s]+(?=[\d\s]+\.\d{{2,2}}(\D|$))) |
    ([\n\s]+(?=({symbols})\s*\d))
    """

    REGEX_MONEY_BREAK = None  # type:Pattern

    PATTERN_PAGER_BREAK = r"""
    [\n\s]+(?=\[\d+/\d+\])
    """

    REGEX_PAGER_BREAK = re.compile(PATTERN_PAGER_BREAK,
                                   re.IGNORECASE | re.DOTALL | re.MULTILINE | re.VERBOSE)

    @staticmethod
    def setup_parser():
        from lexnlp.extract.en.amounts import CURRENCY_SYMBOL_MAP
        symbols = '|'.join([k for k in CURRENCY_SYMBOL_MAP]).replace('$', r'\$')
        ParsedTextCorrector.PATTERN_MONEY_BREAK = ParsedTextCorrector.PATTERN_MONEY_BREAK.format(symbols=symbols)
        ParsedTextCorrector.REGEX_MONEY_BREAK = re.compile(
            ParsedTextCorrector.PATTERN_MONEY_BREAK,
            re.IGNORECASE | re.DOTALL | re.MULTILINE | re.VERBOSE | re.UNICODE)

    def check_and_correct(self, text: str) -> str:
        text = self.fix_money_line_breaks(text)
        text = self.fix_pager_line_breaks(text)
        text = self.correct_if_corrupted(text)
        return text

    # check the text and correct if corrupted
    def correct_if_corrupted(self, text: str) -> str:
        estimator = ParsedTextQualityEstimator()
        estim = estimator.estimate_text(text)
        if estim.corrupted_prob < 50:
            return text
        if estim.extra_line_breaks_prob > 50:
            text = self.correct_line_breaks(text, estimator)
        return text

    # remove all double (triple ...) line breaks
    def correct_line_breaks(self, text: str,
                            estimator: ParsedTextQualityEstimator = None) -> str:
        if estimator is None:
            estimator = ParsedTextQualityEstimator()
            estimator.split_text_on_lines(text)

        resulted = ''
        lines = estimator.lines

        for indx in range(0, len(lines)):
            line = lines[indx]
            if estimator.check_line_followed_by_unnecessary_break(indx):
                self.normalize_line_ending(line)
            resulted += line.text
            resulted += line.ending
        return resulted

    def normalize_line_ending(self, line: LineOrPhrase):
        line.ending = ''.join(ch for ch, _ in itertools.groupby(line.ending))

    def fix_money_line_breaks(self, text: str) -> str:
        """
        removes extra line breaks that appear between money string and the preceding text
        """
        text = self.REGEX_MONEY_BREAK.sub(' ', text)
        return text

    def fix_pager_line_breaks(self, text: str) -> str:
        """
        removes extra line breaks that appear between [1/48] etc.
        """
        text = self.REGEX_PAGER_BREAK.sub(' ', text)
        return text


ParsedTextCorrector.setup_parser()
