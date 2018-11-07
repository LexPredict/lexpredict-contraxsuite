import re

import pyap
import json
import os

_TOKEN_PATTERN = re.compile(r'(?u)\b\w\w+\b')
_TOKEN_POSITIONS_SPLIT = 5

NUMBERS_RE_STR = r'[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?'
NUMBERS_RE = re.compile(NUMBERS_RE_STR)
REMOVE_NUMERIC_SEPARATORS_RE = re.compile(r'(\d),(\d)')
REMOVE_NUMERIC_SEPARATORS_WITH_SPACES_RE = [re.compile(r'(\d),\s*(\d)'),
                                            re.compile(r'(\d\.)\s*(\d)')]

RE_MULTI_SPACES = re.compile(r'[\s\n]+', re.IGNORECASE | re.DOTALL | re.MULTILINE)


def cleanup_sentence(s: str):
    if not s:
        return None
    res = RE_MULTI_SPACES.sub(' ', s)
    return res


def remove_num_separators(sentence):
    res = sentence
    for r in REMOVE_NUMERIC_SEPARATORS_WITH_SPACES_RE:
        res = r.sub(r'\1\2', res)
    return res


def find_numbers(text: str):
    text = REMOVE_NUMERIC_SEPARATORS_RE.sub(r'\1\2', text)
    for ns in NUMBERS_RE.findall(text):
        yield float(ns)


def find_addresses_str(text):
    res = pyap.parse(text, country='US')
    return None if not res else [str(a) for a in res]


def inject_field_into_json_files(src_dir: str, field_name: str, field_value, dst_dir: str):
    for fn in os.listdir(src_dir):
        dst_fn = os.path.join(dst_dir, fn)
        src_fn = os.path.join(src_dir, fn)
        with open(src_fn, encoding='UTF-8') as f:
            d = json.load(f)
            d[field_name] = field_value
            with open(dst_fn, 'w', encoding="UTF-8") as df:
                json.dump(d, df, indent=2)
