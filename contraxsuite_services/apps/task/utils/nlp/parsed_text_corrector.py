import regex as re
import itertools

from typing import Pattern

from apps.task.utils.nlp.line_processor import LineProcessor, LineOrPhrase
from apps.task.utils.nlp.parsed_text_quality_estimator import ParsedTextQualityEstimator


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
