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

import re
import time
import types
from enum import Enum, unique
from typing import Type, Callable, Union, Pattern, List, Generator, Dict, Any, Tuple

import dateparser
from lexnlp.extract.en.dates import get_dates
from lexnlp.nlp.en.segments.sentences import get_sentence_span_list

from apps.document.models import Document
from apps.fields.parsing import extractors

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.1/LICENSE"
__version__ = "1.2.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


@unique
class FieldType(Enum):
    FIELD_TYPE_CONCRETE_STRING = "string"
    FIELD_TYPE_CONCRETE_DATE = "date"
    FIELD_TYPE_CONCRETE_FLOAT = "float"
    FIELD_TYPE_CONCRETE_BOOLEAN = "boolean"
    FIELD_TYPE_CONCRETE_INTEGER = "int"
    FIELD_TYPE_CONCRETE_CHOICE = "choice"
    FIELD_TYPE_RELATED_INFO = "related_info"


class FieldDetector:
    DEF_RE_FLAGS = re.DOTALL | re.IGNORECASE

    @staticmethod
    def prepare_matcher(
            matcher: Union[str, Pattern, Callable[[str], str], List]) \
            -> Union[None, Callable[[str], Generator[str, None, None]]]:

        if type(matcher) is list:
            matchers = [FieldDetector.prepare_matcher(m) for m in list(matcher)]

            def matcher_func(text):
                for m in matchers:
                    if m is not None:
                        yield from m(text)

            return matcher_func

        elif callable(matcher):
            def matcher_func(text):
                res = matcher(text)
                if type(res) is list:
                    for e in list(res):
                        yield e
                elif isinstance(res, types.GeneratorType):
                    yield from res
                else:
                    yield res

            return matcher_func
        elif isinstance(matcher, str):
            matcher_re = re.compile(matcher, FieldDetector.DEF_RE_FLAGS)

            def matcher_func(str):
                for m in matcher_re.findall(str):
                    yield m

            return matcher_func
        elif isinstance(matcher, re._pattern_type):
            def matcher_func(str):
                for m in matcher.findall(str):
                    yield m

            return matcher_func
        else:
            return None

    def __init__(self, select,
                 fill_fields: Union[Callable, Dict[str, Any]],
                 pre_process_before_select: Callable[[str, ], str] = None,
                 process_selected: Callable = None,
                 exclude: List = None):
        self.select = FieldDetector.prepare_matcher(select)
        self.exclude = FieldDetector.prepare_matcher(exclude) if exclude else None
        self.pre_process = pre_process_before_select
        self.process_selected = process_selected
        self.fill_fields = fill_fields

    @staticmethod
    def _update(dst: Dict[str, Any], patch):
        # print('Fields updated with: {0}'.format(patch))
        # time_start = time.time()
        for key, value in patch.items():
            is_set = key.endswith('__set')
            is_list = key.endswith('__list')
            if is_set or is_list:
                v = dst.get(key)
                if not v:
                    v = list() if is_list else set()
                    dst[key] = v
                elif (is_set and type(v) != set) or (is_list and type(v) != list):
                    v = [v] if is_list else {v}
                    dst[key] = v

                if is_list:
                    v.append(value)
                else:
                    v.add(value)
            else:
                dst[key] = value
                # print('Update Time: {0:.2f}'.format(1000 * (time.time() - time_start)))

    def sentence_matches(self, sentence: str):
        if self.exclude:
            for m in self.exclude(sentence):
                if m:
                    return
        # print('Regexp: {0}'.format(self.select_re))

        if self.pre_process:
            sentence = self.pre_process(sentence)

        for match in self.select(sentence):
            if match:
                return True

    def process(self, sentence: str, fields_dst: Dict[str, Any]):
        time_start = time.time()
        if self.exclude:
            for m in self.exclude(sentence):
                if m:
                    return
        # print('Regexp: {0}'.format(self.select_re))

        if self.pre_process:
            sentence = self.pre_process(sentence)

        for match in self.select(sentence):
            try:
                values = self.process_selected(sentence, match) if self.process_selected else match
                if not values:
                    continue
                if isinstance(values, types.GeneratorType):
                    values = list(values)

                if isinstance(self.fill_fields, types.FunctionType):
                    FieldDetector._update(fields_dst, self.fill_fields(sentence, values))
                elif type(self.fill_fields) is dict:
                    FieldDetector._update(fields_dst, self.fill_fields)
            except Exception:
                continue
                # print('Processing Time: {0:.2f}'.format(1000 * (time.time() - time_start)))


class FieldConfig:
    def __init__(self, document_class: Type[Document], field: str, name: str,
                 field_type: FieldType = None,
                 field_detectors: List[FieldDetector] = None
                 ) -> None:
        super().__init__()
        self.document_class = document_class
        try:
            self.document_class_code = document_class.class_code
        except AttributeError:
            self.document_class_code = document_class.__name__
        self.field = field
        self.field_code = self.document_class_code + "__" + field
        self.name = name
        self.field_type = field_type
        self.field_detectors = field_detectors

    def set_value_from_selection(self, doc: Document, value: str):
        if self.field_type == FieldType.FIELD_TYPE_CONCRETE_STRING:
            doc.__setattr__(self.field, value)

        elif self.field_type == FieldType.FIELD_TYPE_CONCRETE_FLOAT:
            try:
                doc.__setattr__(self.field, float(value))
            except ValueError:
                nums = list(extractors.find_numbers(value)) if value else None
                doc.__setattr__(self.field, nums[0] if nums else None)

        elif self.field_type == FieldType.FIELD_TYPE_CONCRETE_INTEGER:
            try:
                doc.__setattr__(self.field, int(value))
            except ValueError:
                nums = list(extractors.find_numbers(value)) if value else None
                doc.__setattr__(self.field, nums[0] if nums else None)

        elif self.field_type == FieldType.FIELD_TYPE_CONCRETE_DATE:
            d = dateparser.parse(value) if value else None
            if d:
                doc.__setattr__(self.field, d)
            else:
                dates = list(get_dates(value)) if value else None
                doc.__setattr__(self.field, dates[0] if dates else None)

        return doc.__getattribute__(self.field)

    def get_value(self, doc: Document):
        return doc.__getattribute__(self.field)

    def sentence_matches_field_detectors(self, sentence: str):
        if self.field_detectors:
            for fd in self.field_detectors:
                if fd.sentence_matches(sentence):
                    return True
        return False

    def _sentence_matches_annotations(self,
                                      sentence_span: Tuple[int, int],
                                      annotations: List[Tuple[int, int]]):
        #
        # a:  25        30
        # s:       28       33
        #
        #
        if annotations:
            for a in annotations:
                if a[0] <= sentence_span[1] and sentence_span[0] <= a[1]:
                    return True
        else:
            return False

    def _create_annotator_model(self,
                                documents_gen: Generator[Document, Any, None],
                                annotations_by_doc: Callable[
                                    [Document], Generator[Tuple[int, int], Any, None]] = None):
        positive = []
        negative = []
        for doc in documents_gen:
            text = doc.full_text
            annotations = list(annotations_by_doc(doc))
            sentence_spans = get_sentence_span_list(text)
            for span in sentence_spans:
                sentence = text[span[0]:span[1]]
                if self._sentence_matches_field_detectors(sentence) \
                        or self._sentence_matches_annotations(span, annotations):
                    positive.append(sentence)
                else:
                    negative.append(sentence)
