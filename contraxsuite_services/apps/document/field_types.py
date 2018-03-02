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
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.5/LICENSE"
__version__ = "1.0.6"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

from enum import Enum, unique
from typing import List, Union
from datetime import datetime, date

import geocoder
from lexnlp.extract.en.dates import get_dates_list
from lexnlp.extract.en.durations import get_durations
from lexnlp.extract.en.amounts import get_amounts
from lexnlp.extract.en.entities.nltk_maxent import get_companies, get_persons

from apps.document import models
from apps.document.parsing import extractors


@unique
class ValueExtractionHint(Enum):
    TAKE_FIRST = "first"
    TAKE_SECOND = "second"
    TAKE_LAST = "last"

    @staticmethod
    def get_value(l: List, hint):
        if not l:
            return None

        if hint == ValueExtractionHint.TAKE_LAST:
            return l[-1]
        elif hint == ValueExtractionHint.TAKE_SECOND and len(l) > 1:
            return l[1]
        else:
            return l[0]


class FieldType:
    code = ''
    title = ''
    multi_value = False
    value_aware = False

    def extraction_function(self, field, possible_value, text):
        return possible_value

    def save_value(self,
                   document,
                   field,
                   location_start: int,
                   location_end: int,
                   location_text: str,
                   value=None,
                   user=None,
                   allow_overwriting_user_data=True):
        """
        Saves a new value to the field. Depending on the field type it should either
        rewrite existing DocumentFieldValues or add new ones.
        """
        field_values = list(
            models.DocumentFieldValue.objects.filter(document=document, field=field))

        if self.multi_value:
            value = self.extraction_function(field, value, location_text)

            for field_value in field_values:
                if field_value.value == value \
                        and field_value.location_start == location_start \
                        and field_value.location_end == location_end:
                    return field_value
            field_value = models.DocumentFieldValue()
            return self.update(field_value, document, field, location_start, location_end,
                               location_text,
                               value, user)
        else:
            # For single-value fields - either update the existing value or create a new one
            field_value = field_values[0] if len(field_values) > 0 else models.DocumentFieldValue()

            # Just ensure we don't have some mistakenly added multiple values
            for fv in field_values[1:]:
                fv.delete()

            # This will work only for existing field values having filled created_by or modified_by.
            if not allow_overwriting_user_data \
                    and (field_value.created_by is not None
                         or field_value.modified_by is not None):
                return field_value
            else:
                return self.update(field_value, document, field, location_start, location_end,
                                   location_text,
                                   value, user)

    def update(self, field_value, document, field,
               location_start: int, location_end: int, location_text: str, value=None, user=None):
        """
        Updates existing field value with the new data.
        """
        value = self.extraction_function(field, value, location_text)

        field_value.document = document
        field_value.field = field
        field_value.location_start = location_start
        field_value.location_end = location_end
        field_value.location_text = location_text
        field_value.value = value
        field_value.created_by = field_value.created_by or user
        field_value.modified_by = user
        field_value.created_date = field_value.created_date or datetime.now()
        field_value.modified_date = field_value.modified_date or datetime.now()
        field_value.save()
        return field_value

    def get_value(self, field_value):
        return field_value.value

    def delete(self, field_value, **kwargs):
        field_value.delete()

    def value_to_string(self, field_value):
        return str(field_value.value)


class StringField(FieldType):
    code = 'str'
    title = 'String'
    value_aware = True


class ChoiceField(FieldType):
    code = 'choice'
    title = 'Choice'
    value_aware = True

    def extraction_function(self, field, possible_value, text):
        if possible_value is not None and possible_value in field.get_choice_values():
            return possible_value
        else:
            return None


class MultiChoiceField(ChoiceField):
    code = 'multi_choice'
    title = 'Multi Choice'
    multi_value = True
    value_aware = True


class DateField(FieldType):
    code = 'date'
    title = 'String'
    value_aware = True

    def extraction_function(self, field, possible_value, text):
        if isinstance(possible_value, datetime) or isinstance(possible_value, date):
            return possible_value

        if not possible_value and not text:
            return None

        possible_value = str(possible_value) if possible_value else text

        dates = get_dates_list(possible_value)
        return ValueExtractionHint.get_value(dates, field.item_number) if dates else None


class FloatField(FieldType):
    code = 'float'
    title = 'Floating Point Number'
    value_aware = True

    def extraction_function(self, field, possible_value, text):
        if possible_value is None and not text:
            return None
        try:
            return float(possible_value)
        except:
            possible_value = str(possible_value) if possible_value else text
            floats = list(extractors.find_numbers(possible_value))
            return ValueExtractionHint.get_value(floats, field.item_number) if floats else None


class IntField(FieldType):
    code = 'int'
    title = 'Integer Number'
    value_aware = True

    def extraction_function(self, field, possible_value, text):
        if possible_value is None and not text:
            return None
        try:
            return int(possible_value)
        except:
            possible_value = str(possible_value) if possible_value else text
            floats = list(extractors.find_numbers(possible_value))
            return ValueExtractionHint.get_value(floats, field.item_number) if floats else None


class AddressField(FieldType):
    code = 'address'
    title = 'Address'
    value_aware = True

    def extraction_function(self, field, possible_value, text):
        if possible_value is None and not text:
            return None

        if possible_value and type(possible_value) is dict:
            address = possible_value.get('address')
        elif possible_value and type(possible_value) is str:
            address = possible_value
        else:
            address = text

        g = geocoder.google(address)
        if g.ok:
            return {
                'address': g.address,
                'latitude': g.lat,
                'longitude': g.lng,
                'country': g.country_long,
                'province': g.province_long,
                'city': g.city_long
            }
        else:
            # Google does not know such address - probably we detected it wrong.
            return {
                'address': address,
                'latitude': None,
                'longitude': None,
                'country': None,
                'province': None,
                'city': None
            }

    def value_to_string(self, field_value):
        if not field_value:
            return None
        return field_value.value['address']


class CompanyField(FieldType):
    code = 'company'
    title = 'Company'
    value_aware = True

    def extraction_function(self, field, possible_value, text):
        if possible_value:
            return possible_value

        if possible_value is None and not text:
            return None

        companies = list(
            get_companies(text, detail_type=True, name_upper=True, strict=True))

        company = ValueExtractionHint.get_value(companies, field.item_number)

        if company:
            return '{0}{1}'.format(company[0].upper(),
                                   (' ' + company[1].upper()) if company[1] is not None else '')
        else:
            return None


class DurationField(FieldType):
    code = 'duration'
    title = 'Duration'
    value_aware = True

    def extraction_function(self, field, possible_value, text):
        if possible_value is None and not text:
            return None

        if possible_value and type(possible_value) is tuple and len(possible_value) == 3:
            return possible_value

        possible_value = str(possible_value) if possible_value else text
        durations = list(get_durations(possible_value))
        duration = ValueExtractionHint.get_value(durations, field.item_number)
        return duration


class RelatedInfoField(FieldType):
    code = 'related_info'
    title = 'Related Info'
    multi_value = True
    value_aware = False


class PersonField(FieldType):
    code = 'person'
    title = 'Person'
    value_aware = True

    def extraction_function(self, field, possible_value, text):
        if possible_value:
            return possible_value

        persons = list(get_persons(text, return_source=False))

        person = ValueExtractionHint.get_value(persons, field.item_number)

        return person


class AmountField(FieldType):
    code = 'amount'
    title = 'Amount'
    value_aware = True

    def extraction_function(self, field, possible_value, text):
        if possible_value is None and not text:
            return None
        try:
            return float(possible_value)
        except:
            possible_value = str(possible_value) if possible_value else text
            floats = list(get_amounts(possible_value, return_sources=False))
            return ValueExtractionHint.get_value(floats, field.item_number) if floats else None


_FIELD_TYPE_CHOICE = 'choice'
_FIELD_TYPE_MULTI_CHOICE = 'multi_choice'

FIELD_TYPES_CHOICE = {_FIELD_TYPE_CHOICE, _FIELD_TYPE_MULTI_CHOICE}

FIELD_TYPES_REGISTRY = {
    'string': StringField(),
    'int': IntField(),
    'float': FloatField(),
    'date': DateField(),
    'company': CompanyField(),
    'duration': DurationField(),
    'address': AddressField(),
    'related_info': RelatedInfoField(),
    _FIELD_TYPE_CHOICE: ChoiceField(),
    _FIELD_TYPE_MULTI_CHOICE: MultiChoiceField(),
    'person': PersonField(),
    'amount': AmountField()
}
