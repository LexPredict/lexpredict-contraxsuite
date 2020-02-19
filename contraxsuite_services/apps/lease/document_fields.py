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

from lexnlp.extract.en.dates import get_dates
from lexnlp.extract.en.durations import get_durations

from apps.document.models import Document
from apps.fields.document_fields import FieldConfig, FieldType, FieldDetector
from apps.fields.parsing.extractors import NUMBERS_RE_STR, find_numbers, remove_num_separators, \
    find_addresses_str, cleanup_sentence
from apps.lease.models import LeaseDocument

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class AddressFieldConfig(FieldConfig):
    ADDRESSES_EXCLUDE_SENTENCES_RE = [
        re.compile(r'by\s+and\s+between', re.DOTALL | re.IGNORECASE),
        re.compile(r'address.+(?:tenant|landlord|lessee|lessor)', re.DOTALL | re.IGNORECASE),
        re.compile(r'address.+(?:notice|mail)', re.DOTALL | re.IGNORECASE),
        re.compile(r'(?:notice|mail).+address', re.DOTALL | re.IGNORECASE),
        re.compile(r'to\s+(?:lessor|lessee)', re.DOTALL | re.IGNORECASE)
    ]

    def __init__(self, field: str, name: str) -> None:
        super().__init__(LeaseDocument, field, name, FieldType.FIELD_TYPE_CONCRETE_STRING, [
            FieldDetector(select=r'(?:premises|property)\s+located\s+in(.*)',
                          process_selected=lambda sentence, match: find_addresses_str(match),
                          fill_fields=lambda sentence, addresses: {'address': addresses[0]},
                          exclude=AddressFieldConfig.ADDRESSES_EXCLUDE_SENTENCES_RE),

        ])

    def set_value_from_selection(self, doc: Document, value: str):
        doc.address = value
        return doc.address


DOCUMENT_FIELDS = [
    FieldConfig(LeaseDocument, 'property_type', 'Property Type',
                FieldType.FIELD_TYPE_CONCRETE_STRING, [

                    FieldDetector(
                        select=r'.*(?:tenant|lessee|premises|property|agreed).+use.+storage.*',
                        fill_fields={'property_types__set': 'storage'}),

                    FieldDetector(
                        select=r'.*(?:tenant|lessee|premises|property|agreed).+use.+farming.*',
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
                ]),
    AddressFieldConfig('address', 'Address'),
    FieldConfig(LeaseDocument, 'lessor', 'Lessor', FieldType.FIELD_TYPE_CONCRETE_STRING),
    FieldConfig(LeaseDocument, 'lessee', 'Lessee', FieldType.FIELD_TYPE_CONCRETE_STRING),
    FieldConfig(LeaseDocument, 'lease_type', 'Lease Type', FieldType.FIELD_TYPE_CONCRETE_STRING, [
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
    ]),
    FieldConfig(LeaseDocument, 'commencement_date', 'Commencement Date',
                FieldType.FIELD_TYPE_CONCRETE_DATE, [

                    FieldDetector(select=r'shall\s+(?:commence|start).*\d.*',
                                  process_selected=lambda sentence, match: get_dates(match),
                                  fill_fields=lambda sentence, dates: {
                                      'commencement_date': dates[0]}),
                    FieldDetector(select=r'from.*\d.*',
                                  process_selected=lambda sentence, match: get_dates(match),
                                  fill_fields=lambda sentence, dates: {
                                      'commencement_date': dates[0]}),
                    FieldDetector(select=r'commencement\s+date.*\d.*',
                                  process_selected=lambda sentence, match: get_dates(match),
                                  fill_fields=lambda sentence, dates: {
                                      'commencement_date': dates[0]}),
                ]),
    FieldConfig(LeaseDocument, 'expiration_date', 'Expiration Date',
                FieldType.FIELD_TYPE_CONCRETE_DATE, [

                    FieldDetector(select=r'shall\s+(?:end).*\d.*',
                                  process_selected=lambda sentence, match: get_dates(match),
                                  fill_fields=lambda sentence, dates: {
                                      'expiration_date': dates[0]}),
                    FieldDetector(select=r'expiration\s+date.*\d.*',
                                  process_selected=lambda sentence, match: get_dates(match),
                                  fill_fields=lambda sentence, dates: {
                                      'expiration_date': dates[0]}),
                ]),
    FieldConfig(LeaseDocument, 'area_size_sq_ft', 'Area Size (sq. ft.)',
                FieldType.FIELD_TYPE_CONCRETE_FLOAT, [
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
                ]),
    FieldConfig(LeaseDocument, 'rent_due_frequency', 'Rent Due Frequency',
                FieldType.FIELD_TYPE_CONCRETE_STRING, [
                    FieldDetector(
                        pre_process_before_select=lambda sentence: sentence.lower(),
                        exclude=[
                            lambda sentence: all([(word in sentence) for word in ['monthly']])],
                        select=[lambda sentence: all(
                            [(word in sentence) for word in
                             ['pay', 'rent', 'advance', 'term', 'lease']])],
                        fill_fields={'rent_due_frequency': 'total amount'}),
                    FieldDetector(pre_process_before_select=lambda sentence: sentence.lower(),
                                  select=[lambda sentence: all(
                                      [(word in sentence) for word in ['pay', 'rent', 'monthly']]),
                                          lambda sentence: all(
                                              [(word in sentence) for word in
                                               ['paid', 'rent', 'monthly']]),
                                          lambda sentence: all(
                                              [(word in sentence) for word in
                                               ['payments', 'rent', 'monthly']]),
                                          lambda sentence: all(
                                              [(word in sentence) for word in
                                               ['pay', 'per', 'month']]),
                                          lambda sentence: all(
                                              [(word in sentence) for word in
                                               ['payable', 'per', 'month']]),
                                          lambda sentence: all(
                                              [(word in sentence) for word in
                                               ['payable', 'monthly']])
                                          ],
                                  fill_fields={'rent_due_frequency': 'monthly'})
                ]),
    FieldConfig(LeaseDocument, 'mean_rent_per_month', 'Mean Rent Per Month',
                FieldType.FIELD_TYPE_CONCRETE_FLOAT, [
                    FieldDetector(select=[r'total.*amount.*month.*\$\s*(' + NUMBERS_RE_STR + ')',
                                          r'rent.*\$\s*(' + NUMBERS_RE_STR + ').*per\s+month',
                                          r'pay.*amount.*\$\s*(' + NUMBERS_RE_STR + ').*per\s+month',
                                          r'rent.*(?:paid|payable).*monthly.*\$\s*(' + NUMBERS_RE_STR + ')',
                                          ],
                                  pre_process_before_select=remove_num_separators,
                                  process_selected=lambda sentence, match: find_numbers(match),
                                  fill_fields=lambda sentence, amounts: {
                                      'mean_rent_per_month__set': amounts[0]}),

                ]),
    FieldConfig(LeaseDocument, 'security_deposit', 'Security Deposit',
                FieldType.FIELD_TYPE_CONCRETE_FLOAT, [
                    FieldDetector(
                        select=[r'\$\s*(' + NUMBERS_RE_STR + ').*(?:tenant|lessee).*deposit',
                                r'\$\s*(' + NUMBERS_RE_STR + ').*deposit.*(?:tenant|lessee)',
                                r'(?:tenant|lessee).*\$\s*(' + NUMBERS_RE_STR + ').*deposit',
                                r'(?:tenant|lessee).*deposit.*\$\s*(' + NUMBERS_RE_STR + ')',
                                r'security\s+deposit\s*:\s*\$\s*(' + NUMBERS_RE_STR + ')'],
                        exclude=[r'SECURITY\s+DEPOSIT\s*:\s*N\/A'],
                        pre_process_before_select=remove_num_separators,
                        process_selected=lambda sentence, match: find_numbers(match),
                        fill_fields=lambda sentence, amounts: {
                            'security_deposit__set': amounts[0]}),
                ]),

    FieldConfig(LeaseDocument, 'permitted_uses', 'Permitted Uses',
                FieldType.FIELD_TYPE_RELATED_INFO, [

                    FieldDetector(select=r'(?:property|premises)\s+shall\s+be\s+used(.*)',
                                  fill_fields=lambda sentence, match: {
                                      'permitted_use': cleanup_sentence(match).strip()}),
                    FieldDetector(
                        select=r'(?:tenant|lessee)\s+(?:may|shall)\s+use.*(?:property|premises)(.*)',
                        fill_fields=lambda sentence, match: {
                            'permitted_use': cleanup_sentence(match).strip()}),
                    FieldDetector(select=re.compile(r'Use.*[:.]\s+(.*)', re.DOTALL),
                                  fill_fields=lambda sentence, match: {
                                      'permitted_use': cleanup_sentence(match).strip()}),
                    FieldDetector(select=re.compile(r'Permitted\s+[Uu]se.*[:.]\s+(.*)', re.DOTALL),
                                  fill_fields=lambda sentence, match: {
                                      'permitted_use': cleanup_sentence(match).strip()})
                ]),
    FieldConfig(LeaseDocument, 'prohibited_uses', 'Prohibited Uses',
                FieldType.FIELD_TYPE_RELATED_INFO, [
                    FieldDetector(select=r'(?:property|premises)\s+(?:shall|may)\s+not\s+be\s+used',
                                  fill_fields=lambda sentence, match: {
                                      'prohibited_use__list': cleanup_sentence(sentence).strip()}),

                    FieldDetector(
                        select=r'(?:tenant|lessee)\s+(?:shall|may)\s+not.+(?:property|premises)',
                        fill_fields=lambda sentence, match: {
                            'prohibited_use__list': cleanup_sentence(sentence).strip()},
                        exclude=[r'\srent\s']),

                    FieldDetector(select=r'Restrition\s+[Oo]n\s+Use.*[:.]\s+.',
                                  fill_fields=lambda sentence, match: {
                                      'permitted_use__list': cleanup_sentence(sentence).strip()})
                ]),
    FieldConfig(LeaseDocument, 'renew_non_renew_notice_duration', 'Renew/Non-renew Notice Duration',
                FieldType.FIELD_TYPE_RELATED_INFO, [
                    FieldDetector(
                        select=r'(?:lessor|tenant).+intends\s+to.+lease.+(?:notice|notify)',
                        process_selected=lambda sentence, match: get_durations(sentence),
                        fill_fields=lambda sentence, durations: {'auto_renew': False,
                                                                 'renew_non_renew_notice':
                                                                     durations[
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
                ]),
    FieldConfig(LeaseDocument, 'auto_renew', 'Auto Renew', FieldType.FIELD_TYPE_RELATED_INFO),
    FieldConfig(LeaseDocument, 'alterations_allowed', 'Alternations Allowed',
                FieldType.FIELD_TYPE_RELATED_INFO, [
                    FieldDetector(select=r'.*(?:alteration|improvement).*',
                                  fill_fields=lambda sentence, _nothing: {
                                      'alterations_allowed__list': sentence}),
                ]),
    FieldConfig(LeaseDocument, 'total_rent_amount', 'Total Rent Amount',
                FieldType.FIELD_TYPE_CONCRETE_FLOAT),
    FieldConfig(LeaseDocument, 'period_rent_amount', 'Period Rent Amount',
                FieldType.FIELD_TYPE_CONCRETE_FLOAT),
    FieldConfig(LeaseDocument, 'construction_allowance', 'Construction Allowance',
                FieldType.FIELD_TYPE_RELATED_INFO),
    FieldConfig(LeaseDocument, 'construction_allowance_type', 'Construction Allowance Type',
                FieldType.FIELD_TYPE_RELATED_INFO),
]
