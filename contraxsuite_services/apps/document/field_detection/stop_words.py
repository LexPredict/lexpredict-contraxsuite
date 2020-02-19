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
from typing import Dict, Any, Tuple, Optional

from apps.document.field_types import TypedField
from apps.document.models import DocumentField

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


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


def detect_with_stop_words_by_field_and_full_text(field: DocumentField, full_text: str) -> Tuple[bool, Any]:
    if field.requires_text_annotations:
        return False, None
    stop_words = compile_stop_words(field.stop_words)
    if not stop_words:
        return False, None
    typed_field = TypedField.by(field)  # type: TypedField
    detected, possible_value = detect_value_with_stop_words(stop_words, full_text)
    if not detected:
        return False, None
    if possible_value is None:
        return True, None
    else:
        possible_value = typed_field.extract_from_possible_value_text(possible_value)
        return True, possible_value
