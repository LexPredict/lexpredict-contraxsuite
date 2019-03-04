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

import pyap

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.9/LICENSE"
__version__ = "1.1.9"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

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
