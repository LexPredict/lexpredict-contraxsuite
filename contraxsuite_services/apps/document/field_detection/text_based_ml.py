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

import re
from typing import Optional, List, Dict, Tuple

from lexnlp.nlp.en.segments.sentences import get_sentence_span_list

from apps.document.value_extraction_hints import ValueExtractionHint

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.3.0/LICENSE"
__version__ = "1.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


_TOKEN_PATTERN = re.compile(r'(?u)\b\w\w+\b')
_TOKEN_POSITIONS_SPLIT = 5


def word_position_tokenizer(sentence: str):
    token_list = list(_TOKEN_PATTERN.findall(sentence))
    size = len(token_list)

    # size = 3, position_split = 10
    # |   |   |   |
    #
    # position = 2
    #
    # 2 of 3
    # x of 10
    #
    # x = (2 * 10) / 3 = 6.67
    #
    # size = 20, position_split = 10, position = 5
    #
    # 5 of 20
    # x of 10
    # x = (5*10)/20 = 2.5
    return [token + ':' + str(round((position * _TOKEN_POSITIONS_SPLIT) / size))
            for position, token in enumerate(token_list)]


def encode_category(field_uid, choice_value, extraction_hint) -> str:
    if not field_uid:
        return SkLearnClassifierModel.EMPTY_CAT_NAME
    return ':::'.join([str(field_uid) if field_uid else '',
                       str(choice_value) if choice_value else '',
                       str(extraction_hint) if extraction_hint else ValueExtractionHint.TAKE_FIRST.name])


def parse_category(category: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    if category == SkLearnClassifierModel.EMPTY_CAT_NAME:
        return None, None, None

    ar = category.split(':::')
    field_uid = ar[0] or None
    choice_value = ar[1] or None
    extractiion_hint = ar[2] or None
    return field_uid, choice_value, extractiion_hint


class ModelCategory:
    def __init__(self, document_field_uid, choice_or_hint) -> None:
        self.document_field_uid = str(document_field_uid) if document_field_uid else None
        self.choice_or_hint = choice_or_hint

    def name(self):
        if not self.document_field_uid:
            return SkLearnClassifierModel.EMPTY_CAT_NAME

        return str(self.document_field_uid) + (
            ':::' + str(self.choice_or_hint) if self.choice_or_hint is not None else '')

    @staticmethod
    def from_name(name: str):
        if SkLearnClassifierModel.EMPTY_CAT_NAME == name:
            return ModelCategory(None, None)
        ar = name.split(':::')
        if not ar:
            return None
        field_uid = ar[0]
        choice_or_hint = ar[1] if len(ar) > 1 else None
        return ModelCategory(field_uid, choice_or_hint)


class SkLearnClassifierModel:
    EMPTY_CAT_NAME = '-'

    def __init__(self, sklearn_model, target_names) -> None:
        self.sklearn_model = sklearn_model
        self.target_names = target_names

    def detect_category_names_for_sentence(self, sentence: str) -> List[str]:
        predicted = self.sklearn_model.predict([sentence])  # [0]

        res = set()
        for target_index, value in enumerate(predicted):
            if not value:
                continue
            target_name = self.target_names[target_index]
            if target_name == SkLearnClassifierModel.EMPTY_CAT_NAME:
                continue

            res.add(target_name)
        return list(res)

    def detect_category_names_to_spans(self, text: str, field: str = None) \
            -> Dict[str, List[Tuple[int, int, str]]]:
        if self.sklearn_model is None:
            return {}

        sentence_spans = get_sentence_span_list(text)

        res = {}

        for span in sentence_spans:
            sentence = text[span[0]:span[1]]
            category_names = self.detect_category_names_for_sentence(sentence)

            for target_name in category_names:
                if (not field and target_name) or (field and field == target_name):
                    spans_of_category = res.get(target_name)
                    if not spans_of_category:
                        spans_of_category = [(span[0], span[1], sentence)]
                        res[target_name] = spans_of_category
                    else:
                        spans_of_category.append((span[0], span[1], sentence))

        return res
