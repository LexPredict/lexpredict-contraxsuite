import re
from typing import Optional, List, Dict, Tuple
from apps.document.field_types import ValueExtractionHint
from lexnlp.nlp.en.segments.sentences import get_sentence_span_list

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
