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


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from logging import Logger
from apps.task.utils.logger import get_django_logger
from typing import Optional, Tuple
from lexnlp.extract.en.definitions \
    import get_definitions_in_sentence, get_definitions
from apps.document.models import DocumentFieldDetector, TextParts


class DetectorFieldMatcher:
    """
    class matches text units (sentences or paragraphs) against
    regular expressions, defined in DocumentFieldDetector
    """

    @property
    def extraction_hint(self) -> str:
        return self.detector.extraction_hint

    def __init__(self, detector: DocumentFieldDetector):
        self.detector = detector

    def _clean_def_words(self, s: str):
        res = ''.join(filter(lambda ss: ss.isalpha() or ss.isnumeric() or ss.isspace(), s))
        return ' '.join(res.split()).lower()

    def _matches_definition_words(self, text: str, text_is_sentence: bool) -> bool:
        if not self.detector.detector_definition_words:
            return False
        try:
            terms = get_definitions_in_sentence(text) \
                if text_is_sentence else get_definitions(text)
        except Exception as e:
            msg = f'{self.get_detector_code()}: error in ' + \
                  f'_matches_definition_words("{text}"), ' + \
                  'in get_definitions_in_sentence' if text_is_sentence \
                  else 'if get_definitions'
            e.detailed_error = msg
            raise
        if not terms:
            return False
        terms = set([self._clean_def_words(t) for t in terms])

        for w in self.detector.detector_definition_words:
            if w in terms:
                return True
        return False

    def matches(self, text: str, text_is_sentence: bool = True) -> \
            Optional[Tuple[str, int, int]]:
        if self.detector.include_matchers is None or self.detector.exclude_matchers is None:
            try:
                self.detector.compile_regexps()
            except Exception as e:
                e.detailed_error = f'{self.get_detector_code()}: ' +\
                                   'error compiling matching regexes.'
                raise

        if not text:
            return None

        text = text.replace('\n', ' ').replace('\t', ' ')
        if self.detector._matches_exclude_regexp(text):
            return None
        else:
            if self.detector.detector_definition_words:
                if not self._matches_definition_words(text, text_is_sentence):
                    return None
                if not self.detector.include_matchers:
                    return text, 0, len(text)
                else:
                    return self._match_include_regexp_or_none(text, text)
            else:
                return self._match_include_regexp_or_none(text, text)

    def matching_string(self, text: str, text_is_sentence: bool = True) -> Optional[Tuple[str, int, int]]:
        # returns: string, begin, end
        match = self.matches(text, text_is_sentence)
        if match:
            matching_string, begin, end = match
            if self.detector.text_part == TextParts.BEFORE_REGEXP.value:
                return matching_string[:begin], 0, begin
            elif self.detector.text_part == TextParts.AFTER_REGEXP.value:
                return matching_string[end:], end, len(text)
            elif self.detector.text_part == TextParts.INSIDE_REGEXP.value:
                return matching_string[begin:end], begin, end
            else:
                return text, 0, len(text)
        return None

    def _match_include_regexp_or_none(self,
                                      sentence: str,
                                      sentence_before_lower: str) -> Optional[Tuple[str, int, int]]:
        if self.detector.include_matchers:
            for matcher_re in self.detector.include_matchers:
                try:
                    for match in matcher_re.finditer(sentence):
                        return sentence_before_lower, match.start(), match.end()
                except Exception as e:
                    msg = self.get_detector_code() + \
                          ': error in DetectorFieldMatching. ' + \
                          f'_match_include_regexp_or_none("{sentence}"), ' + \
                          f'regex="{matcher_re}": {e}'
                    e.detailed_error = msg
                    raise
        return None

    @classmethod
    def validate_detected_value(cls, field_type: str, detected_value: str) -> None:
        from apps.document.field_types import FIELD_TYPES_ALLOWED_FOR_DETECTED_VALUE
        from apps.document.field_type_registry import FIELD_TYPE_REGISTRY

        if detected_value and field_type not in FIELD_TYPES_ALLOWED_FOR_DETECTED_VALUE:
            field_types = [FIELD_TYPE_REGISTRY[ft].title for ft in FIELD_TYPES_ALLOWED_FOR_DETECTED_VALUE]
            field_types_str = ', '.join(field_types)
            raise RuntimeError(
                f'Detected value "{detected_value}"'
                f'is allowed only for {field_types_str} fields, '
                f'and not for field type "{field_type}".'
            )

    def get_validated_detected_value(self, field=None) -> str:
        field = field or self.detector.field
        try:
            if self.detector.detected_value:
                self.validate_detected_value(field.type, self.detector.detected_value)
            return self.detector.detected_value
        except Exception as exc:
            msg = f'Field detector #{self.get_detector_code()} ' + \
                  f'has incorrect detected value. {exc}'
            logger = self.get_logger()
            logger.error(msg)
            raise RuntimeError(msg)

    def get_detector_code(self) -> str:
        if self.detector.field:
            doc_type = self.detector.field.document_type.code \
                if self.detector.field.document_type else ''
            return f'{self.detector.field.code}:{doc_type}'
        return f'field detector #{self.detector.uid}'

    @staticmethod
    def get_logger() -> Logger:
        return get_django_logger()
