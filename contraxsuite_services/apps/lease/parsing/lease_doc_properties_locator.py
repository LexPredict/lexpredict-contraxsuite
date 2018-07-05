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
from typing import List, Tuple, Dict, Any, Callable, Union, Pattern, Generator

import pyap
from lexnlp.extract.en.dates import get_dates
from lexnlp.extract.en.durations import get_durations
from lexnlp.extract.en.entities.nltk_maxent import get_companies

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.1/LICENSE"
__version__ = "1.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

_LANDLORD_SYNONYMS = ['landlord', 'lessor', 'owner', 'sub-lessor', 'sub-landlord', 'sublessor',
                      'sublandlord']
_TENANT_SYNONYMS = ['tenant', 'lessee', 'sub-lessee', 'sub-tenant', 'sublessee', 'subtenant']


def min_index_of_word(text: str, words: List[str]) -> int:
    min_index = None
    for word in words:
        i = text.find(word)
        if i >= 0 and (min_index is None or i < min_index):
            min_index = i
    return -1 if min_index is None else min_index


def find_landlord_tenant(text: str):
    # landlord, tenant = find_landlord_tenant_re(text)

    # if landlord or tenant:
    #    return landlord, tenant

    companies = list(get_companies(text, detail_type=True, name_upper=True, strict=True))

    text = text.lower()

    min_index_landlord = min_index_of_word(text, _LANDLORD_SYNONYMS)
    min_index_tenant = min_index_of_word(text, _TENANT_SYNONYMS)

    if min_index_landlord < min_index_tenant:
        landlord = companies[0] if len(companies) > 0 else None
        tenant = companies[1] if len(companies) > 1 else None
    else:
        tenant = companies[0] if len(companies) > 0 else None
        landlord = companies[1] if len(companies) > 1 else None

    if landlord is not None and landlord[0] is not None:
        landlord = '{0}{1}'.format(landlord[0].upper(),
                                   (' ' + landlord[1].upper()) if landlord[1] is not None else '')

    if tenant is not None and tenant[0] is not None:
        tenant = '{0}{1}'.format(tenant[0].upper(),
                                 (' ' + tenant[1].upper()) if tenant[1] is not None else '')

    return landlord, tenant


RE_BAD_FOR_PARTIES = re.compile(r'([^\s\w\.\,-]|_|\n)+')


def _filter_name(s: str):
    if not s:
        return None
    res = RE_BAD_FOR_PARTIES.sub('', s).strip().upper()
    res = RE_MULTISPACES.sub(' ', res)
    return res


RE_MULTISPACES = re.compile(r'[\s\n]+', re.IGNORECASE | re.DOTALL | re.MULTILINE)


def _cleanup_sentence(s: str):
    if not s:
        return None
    res = RE_MULTISPACES.sub(' ', s)
    return res


LANDLORD_TENANT_REGEXPS = [
    re.compile(
        r'(?:lessor|landlord|sub-lessor|sub-landlord|sublessor|sublandlord).*:\W*(?P<landlord>.*)'
        r'(?:lessee|tenant|sub-lessee|sub-tenant|sublessee|subtenant).*:\W*(?P<tenant>.*)\n\n',
        re.DOTALL),

    re.compile(r'(?:lessee|tenant|sub-lessee|sub-tenant|sublessee|subtenant).*:\W*(?P<tenant>.*)'
               r'(?:lessor|landlord|sub-lessor|sub-landlord|sublessor|sublandlord).*:\W*(?P<landlord>.*)\n\n',
               re.DOTALL),

    re.compile(r'between\W*'
               r'(?P<tenant>.*)\W*\(.*(?:lessee|tenant|sub-lessee|sub-tenant|sublessee|subtenant).*\)'
               r'\W*and\W*'
               r'(?P<landlord>.*)\W*\(.*(?:lessor|landlord|sub-lessor|sub-landlord|sublessor|sublandlord).*\)',
               re.DOTALL),
    re.compile(r'between\W*'
               r'(?P<landlord>.*)\W*\(.*(?:lessor|landlord|sub-lessor|sub-landlord|sublessor|sublandlord).*\)'
               r'\W*and\W*'
               r'(?P<tenant>.*)\W*\(.*(?:lessee|tenant|sub-lessee|sub-tenant|sublessee|subtenant).*\)',
               re.DOTALL)
]


def find_landlord_tenant_re(text: str):
    text = text.lower()

    tenant = None
    landlord = None

    for p in LANDLORD_TENANT_REGEXPS:
        for m in p.finditer(text):
            landlord = m.group('landlord')
            tenant = m.group('tenant')
            if tenant is not None and landlord is not None:
                break
            print('Landlord: {0}; Tenant: {1}'.format(landlord, tenant))
    return _filter_name(landlord), _filter_name(tenant)


def _find_addresses_str(text):
    res = pyap.parse(text, country='US')
    return None if not res else [str(a) for a in res]


ADDRESSES_EXCLUDE_SENTENCES_RE = [
    re.compile(r'by\s+and\s+between', re.DOTALL | re.IGNORECASE),
    re.compile(r'address.+(?:tenant|landlord|lessee|lessor)', re.DOTALL | re.IGNORECASE),
    re.compile(r'address.+(?:notice|mail)', re.DOTALL | re.IGNORECASE),
    re.compile(r'(?:notice|mail).+address', re.DOTALL | re.IGNORECASE),
    re.compile(r'to\s+(?:lessor|lessee)', re.DOTALL | re.IGNORECASE)
]

NUMBERS_RE_STR = r'[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?'
NUMBERS_RE = re.compile(NUMBERS_RE_STR)
REMOVE_NUMERIC_SEPARATORS_RE = re.compile(r'(\d),(\d)')
REMOVE_NUMERIC_SEPARATORS_WITH_SPACES_RE = [re.compile(r'(\d),\s*(\d)'),
                                            re.compile(r'(\d\.)\s*(\d)')]


def _remove_num_separators(sentence):
    res = sentence
    for r in REMOVE_NUMERIC_SEPARATORS_WITH_SPACES_RE:
        res = r.sub(r'\1\2', res)
    return res


def find_numbers(text: str):
    text = REMOVE_NUMERIC_SEPARATORS_RE.sub(r'\1\2', text)
    for ns in NUMBERS_RE.findall(text):
        yield float(ns)


def _matches_any(patterns: List, text: str) -> bool:
    if not text or not patterns:
        return False
    for p in patterns:
        if re.match(p, text):
            return True
    return False


class FieldDetector:
    DEF_RE_FLAGS = re.DOTALL | re.IGNORECASE

    @staticmethod
    def prepare_matcher(
            matcher: Union[str, Pattern, Callable[[str], str], List]) \
            -> Callable[[str], Generator[str, None, None]]:

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


# Order makes sense - less accurate regexps should go first and more detailed should follow them.
FIELD_DETECTORS_FOR_SENTENCES = {
    'mean_rent_per_month': [
        FieldDetector(select=[r'total.*amount.*month.*\$\s*(' + NUMBERS_RE_STR + ')',
                              r'rent.*\$\s*(' + NUMBERS_RE_STR + ').*per\s+month',
                              r'pay.*amount.*\$\s*(' + NUMBERS_RE_STR + ').*per\s+month',
                              r'rent.*(?:paid|payable).*monthly.*\$\s*(' + NUMBERS_RE_STR + ')',
                              ],
                      pre_process_before_select=_remove_num_separators,
                      process_selected=lambda sentence, match: find_numbers(match),
                      fill_fields=lambda sentence, amounts: {
                          'mean_rent_per_month__set': amounts[0]}),

    ],
    'rent_due_frequency': [
        FieldDetector(
            pre_process_before_select=lambda sentence: sentence.lower(),
            exclude=[lambda sentence: all([(word in sentence) for word in ['monthly']])],
            select=[lambda sentence: all(
                [(word in sentence) for word in ['pay', 'rent', 'advance', 'term', 'lease']])],
            fill_fields={'rent_due_frequency': 'total amount'}),
        FieldDetector(pre_process_before_select=lambda sentence: sentence.lower(),
                      select=[lambda sentence: all(
                          [(word in sentence) for word in ['pay', 'rent', 'monthly']]),
                              lambda sentence: all(
                                  [(word in sentence) for word in ['paid', 'rent', 'monthly']]),
                              lambda sentence: all(
                                  [(word in sentence) for word in ['payments', 'rent', 'monthly']]),
                              lambda sentence: all(
                                  [(word in sentence) for word in ['pay', 'per', 'month']]),
                              lambda sentence: all(
                                  [(word in sentence) for word in ['payable', 'per', 'month']]),
                              lambda sentence: all(
                                  [(word in sentence) for word in ['payable', 'monthly']])
                              ],
                      fill_fields={'rent_due_frequency': 'monthly'})
    ],
    'renew_non_renew_notice': [
        FieldDetector(select=r'(?:lessor|tenant).+intends\s+to.+lease.+(?:notice|notify)',
                      process_selected=lambda sentence, match: get_durations(sentence),
                      fill_fields=lambda sentence, durations: {'auto_renew': False,
                                                               'renew_non_renew_notice': durations[
                                                                   0]}),
        FieldDetector(select=r'given.+option.+to\s+(?:renew|extend)',
                      fill_fields=lambda sentence, durations: {'auto_renew': False}),
        FieldDetector(select=r'to\s+(?:renew|extend).+(?:shall|must).+notice',
                      fill_fields=lambda sentence, durations: {'auto_renew': False}),
        FieldDetector(select=r'shall\s+automatically\s+(?:extend|renew)',
                      fill_fields=lambda sentence, durations: {'auto_renew': True}),
        FieldDetector(select=r'notice.+to.+(?:extend|renew)',
                      exclude=[r'agree'],
                      process_selected=lambda sentence, match: get_durations(sentence),
                      fill_fields=lambda sentence, durations: {
                          'renew_non_renew_notice': durations[0]}),
        FieldDetector(select=r'right\s+to\s+(?:renew|extend)',
                      fill_fields=lambda sentence, match: {'auto_renew': False}),
        FieldDetector(select=r'(?:shall|must).+(?:provide|deliver|give).+notice',
                      process_selected=lambda sentence, match: get_durations(sentence),
                      fill_fields=lambda sentence, durations: {
                          'renew_non_renew_notice': durations[0]}),
        FieldDetector(select=r'lease.*(?:shall|may)\s+be\s+terminated(.*)',
                      process_selected=lambda sentence, match: get_durations(match),
                      fill_fields=lambda sentence, durations: {
                          'renew_non_renew_notice': durations[0],
                          'auto_renew': True}),
        FieldDetector(select=r'notice.+to\s+(?:renew|extend|exercise)',
                      fill_fields=lambda sentence, durations: {'auto_renew': False}),
        FieldDetector(select=r'notice.+not\s+to\s+(?:renew|extend|exercise)',
                      fill_fields=lambda sentence, durations: {'auto_renew': True}),
        FieldDetector(select=r'elect\s+to\s+extend.+notice',
                      process_selected=lambda sentence, match: get_durations(sentence),
                      fill_fields=lambda sentence, durations: {
                          'renew_non_renew_notice': durations[0],
                          'auto_renew': False}),
    ],
    'security_deposit': [
        FieldDetector(select=[r'\$\s*(' + NUMBERS_RE_STR + ').*(?:tenant|lessee).*deposit',
                              r'\$\s*(' + NUMBERS_RE_STR + ').*deposit.*(?:tenant|lessee)',
                              r'(?:tenant|lessee).*\$\s*(' + NUMBERS_RE_STR + ').*deposit',
                              r'(?:tenant|lessee).*deposit.*\$\s*(' + NUMBERS_RE_STR + ')',
                              r'security\s+deposit\s*:\s*\$\s*(' + NUMBERS_RE_STR + ')'],
                      exclude=[r'SECURITY\s+DEPOSIT\s*:\s*N\/A'],
                      pre_process_before_select=_remove_num_separators,
                      process_selected=lambda sentence, match: find_numbers(match),
                      fill_fields=lambda sentence, amounts: {'security_deposit__set': amounts[0]}),
    ],
    'alterations_allowed': [
        FieldDetector(select=r'.*(?:alteration|improvement).*',
                      fill_fields=lambda sentence, _nothing: {
                          'alterations_allowed__list': sentence}),
    ],
    'area_square_feet': [
        FieldDetector(select=r'(?:premises|property)(.*?)\s+square\s+(?:foot|feet)',
                      process_selected=lambda sentence, match: find_numbers(match),
                      fill_fields=lambda sentence, numbers: {
                          'area_square_feet__list': list(numbers)[-1]}),
        FieldDetector(select=r'(?:premises|property)(.*?)\s+acres?',
                      process_selected=lambda sentence, match: find_numbers(match),
                      fill_fields=lambda sentence, numbers: {
                          'area_square_feet__list': 43560 * list(numbers)[-1]}),
        FieldDetector(select=r'(.*?)\s+square\s+(?:foot|feet).+(?:premises|property)',
                      process_selected=lambda sentence, match: find_numbers(match),
                      fill_fields=lambda sentence, numbers: {
                          'area_square_feet__list': list(numbers)[-1]}),
        FieldDetector(select=r'(.*?)\s+acres?.+(?:premises|property)',
                      process_selected=lambda sentence, match: find_numbers(match),
                      fill_fields=lambda sentence, numbers: {
                          'area_square_feet__list': 43560 * list(numbers)[-1]}),
    ],
    'address': [
        FieldDetector(select=r'(?:premises|property)\s+located\s+in(.*)',
                      process_selected=lambda sentence, match: _find_addresses_str(match),
                      fill_fields=lambda sentence, addresses: {'address': addresses[0]},
                      exclude=ADDRESSES_EXCLUDE_SENTENCES_RE),

    ],

    'prohibited_use': [
        FieldDetector(select=r'(?:property|premises)\s+(?:shall|may)\s+not\s+be\s+used',
                      fill_fields=lambda sentence, match: {
                          'prohibited_use__list': _cleanup_sentence(sentence).strip()}),

        FieldDetector(select=r'(?:tenant|lessee)\s+(?:shall|may)\s+not.+(?:property|premises)',
                      fill_fields=lambda sentence, match: {
                          'prohibited_use__list': _cleanup_sentence(sentence).strip()},
                      exclude=[r'\srent\s']),

        FieldDetector(select=r'Restrition\s+[Oo]n\s+Use.*[:.]\s+.',
                      fill_fields=lambda sentence, match: {
                          'permitted_use__list': _cleanup_sentence(sentence).strip()})
    ],
    'permitted_use': [

        FieldDetector(select=r'(?:property|premises)\s+shall\s+be\s+used(.*)',
                      fill_fields=lambda sentence, match: {
                          'permitted_use': _cleanup_sentence(match).strip()}),
        FieldDetector(select=r'(?:tenant|lessee)\s+(?:may|shall)\s+use.*(?:property|premises)(.*)',
                      fill_fields=lambda sentence, match: {
                          'permitted_use': _cleanup_sentence(match).strip()}),
        FieldDetector(select=re.compile(r'Use.*[:.]\s+(.*)', re.DOTALL),
                      fill_fields=lambda sentence, match: {
                          'permitted_use': _cleanup_sentence(match).strip()}),
        FieldDetector(select=re.compile(r'Permitted\s+[Uu]se.*[:.]\s+(.*)', re.DOTALL),
                      fill_fields=lambda sentence, match: {
                          'permitted_use': _cleanup_sentence(match).strip()})
    ],

    'start_end_term': [

        FieldDetector(select=r'shall\s+(?:commence|start).*\d.*',
                      process_selected=lambda sentence, match: get_dates(match),
                      fill_fields=lambda sentence, dates: {'commencement_date': dates[0]}),
        FieldDetector(select=r'shall\s+(?:end).*\d.*',
                      process_selected=lambda sentence, match: get_dates(match),
                      fill_fields=lambda sentence, dates: {'expiration_date': dates[0]}),
        FieldDetector(select=r'from.*\d.*',
                      process_selected=lambda sentence, match: get_dates(match),
                      fill_fields=lambda sentence, dates: {'commencement_date': dates[0]}),
        FieldDetector(select=r'commencement\s+date.*\d.*',
                      process_selected=lambda sentence, match: get_dates(match),
                      fill_fields=lambda sentence, dates: {'commencement_date': dates[0]}),
        FieldDetector(select=r'expiration\s+date.*\d.*',
                      process_selected=lambda sentence, match: get_dates(match),
                      fill_fields=lambda sentence, dates: {'expiration_date': dates[0]}),
        FieldDetector(select=r'term\W.*\d.*',
                      process_selected=lambda sentence, match: get_durations(match),
                      fill_fields=lambda sentence, durations: {'term': durations[0]}),
        FieldDetector(
            select=r'(?:beginning|commencing|commence)\s+.*\d.*(?:expiring|ending|end)\s+.*\d+.*',
            process_selected=lambda sentence, match: get_dates(match),
            fill_fields=lambda sentence, dates: {'commencement_date': dates[0],
                                                 'expiration_date': dates[1]}),
        FieldDetector(select=r'commencement\s+date.*expiration\s+date.*',
                      process_selected=lambda sentence, match: get_dates(match),
                      fill_fields=lambda sentence, dates: {'commencement_date': dates[0],
                                                           'expiration_date': dates[1]})
    ],

    'lease_type': [
        FieldDetector(select=r'(?:tenant|lessee).+pay.+taxes',
                      fill_fields={'pay_taxes': True}),
        FieldDetector(select=r'(?:tenant|lessee).+pay.+insurance',
                      fill_fields={'pay_insurance': True}),
        FieldDetector(select=r'(?:tenant|lessee).+pay.+(?:costs|maintenance)',
                      fill_fields={'pay_costs': True}),
        FieldDetector(select=r'triple\s*-?\s*net',
                      fill_fields={'pay_taxes': True, 'pay_costs': True, 'pay_insurance': True}),
        FieldDetector(select=r'NNN',
                      fill_fields={'pay_taxes': True, 'pay_costs': True, 'pay_insurance': True})
    ],

    'property_type': [

        FieldDetector(select=r'.*(?:tenant|lessee|premises|property|agreed).+use.+storage.*',
                      fill_fields={'property_types__set': 'storage'}),

        FieldDetector(select=r'.*(?:tenant|lessee|premises|property|agreed).+use.+farming.*',
                      fill_fields={'property_types__set': 'farming'}),
        FieldDetector(
            select=r'.*(?:tenant|lessee|premises|property|agreed).+use.+office.*',
            fill_fields={'property_types__set': 'office'}),
        FieldDetector(
            select=r'.*(?:tenant|lessee|premises|property|agreed).+use.+(?:sale|retail).*',
            fill_fields={'property_types__set': 'retail'}),

        FieldDetector(select=r'.*storage.+lease.*',
                      fill_fields={'property_types__set': 'storage'}),
        FieldDetector(select=r'.*office.+lease.*',
                      fill_fields={'property_types__set': 'office'}),
        FieldDetector(select=r'.*land.+lease.*',
                      fill_fields={'property_types__set': 'land'}),
        FieldDetector(select=r'.*(?:property|premises).+\d+\s+acre.*',
                      fill_fields={'property_types__set': 'land'})
    ]

}

ADD_BEFORE_SENTENCES = [
    re.compile(r'\W*permitted\s+use\W+$', re.DOTALL | re.IGNORECASE),
    re.compile(r'\W*prohibited\s+use\W+$', re.DOTALL | re.IGNORECASE),
    re.compile(r'\W*(?:use|usage)\s+restrictions\W+$', re.DOTALL | re.IGNORECASE),
]


def detect_fields(sentences: List[str],
                  groups: Tuple[str] = None) \
        -> Dict[str, Any]:
    res = {}
    _detect_fields_in_blocks(sentences,
                             FIELD_DETECTORS_FOR_SENTENCES,
                             ADD_BEFORE_SENTENCES,
                             dst_fields_dict=res,
                             groups=groups)
    return res


def _detect_fields_in_blocks(blocks: List[str],
                             field_detectors: Dict[str, List[FieldDetector]],
                             add_before_block_re,
                             dst_fields_dict: Dict[str, Any] = None,
                             groups: Tuple[str] = None) \
        -> Dict[str, Any]:
    res = dst_fields_dict if dst_fields_dict is not None else {}

    if not blocks:
        return res

    add_before = []

    for block in blocks:
        if _matches_any(add_before_block_re, block):
            add_before.append(block)
            continue
        elif len(add_before) > 0:
            add_before.append(block)
            block = ' '.join(add_before)
            add_before = []

        # print('Sentence: {0}'.format(block))
        if field_detectors:
            detectors = field_detectors if not groups else {group: ar for group, ar in
                                                            field_detectors.items()
                                                            if group in groups}
            if detectors:
                for ar in detectors.values():
                    for field_detector in ar:
                        field_detector.process(block, res)
    return res


def detect_address_default(text: str, blocks: List[str]):
    # 1. Try to detect addresses in the text as a whole.
    # Results may differ from detecting addresses from each sentence.
    addresses = _find_addresses_str(text) or []

    # 2. Now try to detect addresses in each sentence separately
    for sentence in blocks:
        sentence_addresses = _find_addresses_str(sentence)
        if not sentence_addresses:
            continue
        excluded = False

        for r in ADDRESSES_EXCLUDE_SENTENCES_RE:
            if r.search(sentence):
                excluded = True
                break

        # If this sentence matches one of exclude regexps - remove this sentence's addresses from the doc address list.
        if excluded:
            addresses = [a for a in addresses if a not in sentence_addresses]
        # Otherwise - add addresses of this sentence to the doc address list (those which do not present there already)
        else:
            for a in sentence_addresses:
                if a not in addresses:
                    addresses.append(a)

    # Return the first found address - there is a chance that premises address goes first
    # and party addresses are in the end
    return addresses[0] if addresses else None
