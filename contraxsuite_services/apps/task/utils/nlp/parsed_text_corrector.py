import itertools
from apps.task.utils.nlp.line_processor import LineProcessor, LineOrPhrase
from apps.task.utils.nlp.parsed_text_quality_estimator import ParsedTextQualityEstimator


class ParsedTextCorrector:
    def __init__(self):
        pass

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
