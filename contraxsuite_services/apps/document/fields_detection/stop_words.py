import re
from typing import Dict, Any, Tuple, Optional, List

from apps.document.field_types import FieldType
from apps.document.fields_detection.fields_detection_abstractions import DetectedFieldValue
from apps.document.models import DocumentField


def compile_stop_words(stop_words_dict: Dict[str, Any]) -> Optional[Dict]:
    """
    Pre-compile patterns in a stop-words JSON dict
    :param stop_words_dict: Dictionary of { "regexp_str": value_of_any_type, ...}
    :return: Dictionary of compiled regexps to values.
    """
    if not stop_words_dict:
        return None

    return {re.compile(pattern): value for pattern, value in stop_words_dict.items()}


FORMAT_PREFIX = 'format:'


def detect_value_with_stop_words(stop_words_compiled: Dict, text: str) -> Tuple[bool, Any]:
    """
    Try detecting a field value in the provided text using the stop-words dict with compiled regexps.
    If nothing detected it returns (False, None).
    If a regexp match is found in the text and the value starts with 'format:' then the groupdict()
    is applied as named format parameters to the format string provided in the value.

    Example:
        stop_words_compiled: { re.compile(r'(?P<name>\\w+)'): 'format:Hello, {name}!' }
        text: '   TheName   '
        Result: (True, 'Hello, TheName!')

    Example:
        stop_words_compiled: { re.compile(r'\\d+'): True }
        text: 'Here goes a number: 12345!'
        Result: (True, True)

    Example:
        stop_words_compiled: { re.compile(r'\\d+'): None }
        text: 'Here goes a number: 12345!'
        Result: (True, None)

    Example:
        stop_words_compiled: { re.compile(r'\\d+'): True }
        text: 'No number'
        Result: (False, None)

    :param stop_words_compiled: Dict of { compiled_matcher: value_of_any_type, ...}
    :param text: Text to search in.
    :return: Tuple of ( detected_flag, detected_value )
    """
    if not text or not stop_words_compiled:
        return False, None
    s = text.lower().replace('\n', ' ').replace('\t', ' ')
    for matcher_re, value in stop_words_compiled.items():
        for m in matcher_re.finditer(s):
            if value and type(value) is str and value.startswith(FORMAT_PREFIX):
                return True, value[len(FORMAT_PREFIX):].format(**m.groupdict())
            else:
                return True, value
    return False, None


def detect_with_stop_words_by_field_and_full_text(field: DocumentField, full_text: str) -> Tuple[bool, Optional[List]]:
    if field.requires_text_annotations:
        return False, None
    stop_words = compile_stop_words(field.stop_words)
    if not stop_words:
        return False, None
    field_type_adapter = field.get_field_type()  # type: FieldType
    detected, possible_value = detect_value_with_stop_words(stop_words, full_text)
    if not detected:
        return False, None
    if possible_value is None:
        return True, None
    else:
        possible_value = field_type_adapter.extract_from_possible_value_text(field, possible_value)
        return True, [DetectedFieldValue(field, possible_value)]
