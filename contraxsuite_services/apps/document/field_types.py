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
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.3/LICENSE"
__version__ = "1.1.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

import pickle
import re
from datetime import datetime, date
from enum import Enum, unique
from random import randint, random
from typing import List, Union, Tuple

import dateparser
import geocoder
import pyap
import redis
from lexnlp.extract.en.addresses.addresses import get_addresses
from lexnlp.extract.en.amounts import get_amounts
from lexnlp.extract.en.dates import get_dates_list
from lexnlp.extract.en.durations import get_durations
from lexnlp.extract.en.entities.nltk_maxent import get_companies, get_persons
from lexnlp.extract.en.money import get_money
from lexnlp.extract.en.geoentities import get_geoentities

from django.conf import settings
from django.db import transaction

from apps.document import models
from apps.document.parsing.machine_learning import ModelCategory
from apps.extract import models as extract_models

_redis = redis.Redis.from_url(url=settings.CELERY_CACHE_REDIS_URL)


@unique
class ValueExtractionHint(Enum):
    TAKE_FIRST = "TAKE_FIRST"
    TAKE_SECOND = "TAKE_SECOND"
    TAKE_LAST = "TAKE_LAST"
    TAKE_MIN = "TAKE_MIN"
    TAKE_MAX = "TAKE_MAX"

    ORDINAL_EXTRACTION_HINTS = ['TAKE_MIN', 'TAKE_MAX']

    @staticmethod
    def get_value(l: Union[None, List], hint):
        if not l:
            return None

        if str(hint) == ValueExtractionHint.TAKE_LAST.name:
            return l[-1]
        elif str(hint) == ValueExtractionHint.TAKE_SECOND.name and len(l) > 1:
            return l[1]
        elif str(hint) == ValueExtractionHint.TAKE_FIRST.name and len(l) > 0:
            return l[0]
        # WARNING: currently doesn't check if min/max are possible.
        # ...That is checked exclusively by model.clean_fields() in ./models.py
        elif str(hint) == ValueExtractionHint.TAKE_MIN.name:
            if type(l[0]) is dict \
                    and (l[0]).get('currency') \
                    and (l[0]).get('amount') is not None:
                amount_list = [x.get('amount') for x in l]
                result = [e for e in l if e['amount'] == min(amount_list)]
                return result
            else:
                # Return min of list of amounts
                return min(l)
        # WARNING: currently doesn't check if min/max are possible.
        # ...That is checked exclusively by model.clean_fields() in ./models.py
        elif str(hint) == ValueExtractionHint.TAKE_MAX.name:
            if type(l[0]) is dict \
                    and (l[0]).get('currency') \
                    and (l[0]).get('amount') is not None:
                amount_list = [x.get('amount') for x in l]
                result = [e for e in l if e['amount'] == max(amount_list)]
                return result
            else:
                # Return max of list of amounts
                return max(l)
        else:
            return None


class FieldType:
    code = ''
    title = ''

    # Does this field support storing multiple DocumentFieldValue objects per document+field
    multi_value = False

    # Should this field store some value or only mark piece of text as related to this field
    value_aware = False

    # Does this field support extracting concrete value from sentence
    # or it only allows pre-assigned values.
    # (for value_aware fields)
    value_extracting = False

    ordinal = False

    default_hint = ValueExtractionHint.TAKE_FIRST.name

    def json_value_to_python(self, json_value):
        return json_value

    def python_value_to_json(self, python_value):
        return python_value

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        return None

    def _extract_from_possible_value(self, field, possible_value):
        return possible_value

    def _pick_hint_for_text_using_matching_extractors(self, document, field, text: str):
        if not self.value_extracting:
            return None

        classifier = document.document_type.get_classifier()

        # Try detecting hint with trained model.
        # Detect all category names of this sentence,
        # find the first category related to this field and use its hint.
        if classifier:
            category_names = classifier.detect_category_names_for_sentence(text)
            for category_name in category_names:
                category = ModelCategory.from_name(category_name)
                if str(field.uid) == category.document_field_uid:
                    return category.choice_or_hint

        # If there is no classifier or classifier didn't detect this field for this sentence
        # then try detecting with regexp field detectors (if any).
        detectors = field.field_detectors.all()
        if not detectors:
            return self.default_hint

        for detector in detectors:
            if detector.matches(text):
                return detector.extraction_hint

        return self.default_hint

    def _pick_hint_by_searching_for_value_among_extracted(self, field, text: str, value, **kwargs):
        if not self.value_extracting:
            return None

        if value is None:
            return self.default_hint

        extracted = self._extract_variants_from_text(field, text, **kwargs)

        if not extracted:
            return self.default_hint

        for hint in ValueExtractionHint:
            if value == ValueExtractionHint.get_value(extracted, hint):
                return hint.name

        return self.default_hint

    def get_or_extract_value(self, document, field, possible_value, possible_hint, text) -> Tuple:
        if possible_value is None and not text:
            return None, None

        # If we have some value provided, then try using it and picking hint for it
        # by simply finding this value in all values extracted from this text
        if possible_value is not None:
            value = self._extract_from_possible_value(field, possible_value)

            if value is not None:
                if self.value_extracting:
                    hint = possible_hint or self \
                        ._pick_hint_by_searching_for_value_among_extracted(
                        field,
                        text,
                        value,
                        document=document)
                else:
                    hint = None
                return value, hint

        # If we were unsuccessful in using the provided possible value, then try to extract it from
        # string representation of the provided possible value or from the full provided text

        text = str(possible_value) if possible_value else text

        extracted = self._extract_variants_from_text(field, text, document=document)

        if not extracted:
            return None, None

        # We need to figure out which one of the extracted values to use.
        # For this we pick hint by finding it via trained model or field value extractors.
        if self.value_extracting:
            hint = possible_hint or self._pick_hint_for_text_using_matching_extractors(
                document,
                field,
                text)
        else:
            hint = None

        return ValueExtractionHint.get_value(extracted, hint), hint

    def suggest_value(self,
                      document,
                      field,
                      location_text: str):
        if field.is_calculated():
            return None

        value, hint = self.get_or_extract_value(document, field, location_text,
                                                ValueExtractionHint.TAKE_FIRST.name, location_text)
        return value

    def save_value(self,
                   document,
                   field,
                   location_start: int,
                   location_end: int,
                   location_text: str,
                   sentence_text_unit,
                   value=None,
                   user=None,
                   removed_by_user=None,
                   allow_overwriting_user_data=True,
                   extraction_hint=None):
        """
        Saves a new value to the field. Depending on the field type it should either
        rewrite existing DocumentFieldValues or add new ones.
        """
        if field.is_calculated():
            return None

        if self.multi_value:
            value, hint = self.get_or_extract_value(document, field, value, extraction_hint,
                                                    location_text)

            q = models.DocumentFieldValue.objects.filter(document=document,
                                                         field=field,
                                                         location_start=location_start,
                                                         location_end=location_end)
            q = q.filter(value__isnull=True) if value is None else q.filter(value=value)

            field_value = q.first()

            if field_value:
                if field_value.removed_by_user:
                    field_value.removed_by_user = False
                    field_value.save()
                return field_value

            field_value = models.DocumentFieldValue()
            return self._update(field_value, document, field, location_start, location_end,
                                location_text, sentence_text_unit,
                                value,
                                hint,
                                user, removed_by_user)
        else:
            q = models.DocumentFieldValue.objects.filter(document=document,
                                                         field=field)
            field_value = q.first()

            if field_value:
                models.DocumentFieldValue.objects \
                    .filter(document=document, field=field) \
                    .exclude(pk=field_value.pk) \
                    .delete()
            else:
                field_value = models.DocumentFieldValue()

            # This will work only for existing field values having filled created_by or modified_by.
            if not allow_overwriting_user_data \
                    and (field_value.created_by is not None
                         or field_value.modified_by is not None):
                return field_value
            else:
                value, hint = self.get_or_extract_value(document, field, value, extraction_hint,
                                                        location_text)
                return self._update(field_value, document, field, location_start, location_end,
                                    location_text, sentence_text_unit,
                                    value, hint, user, removed_by_user)

    def _update(self, field_value, document, field,
                location_start: int, location_end: int, location_text: str, sentence_text_unit,
                value=None, hint=None,
                user=None, removed_by_user=None):
        """
        Updates existing field value with the new data.
        """
        field_value.document = document
        field_value.field = field
        field_value.location_start = location_start
        field_value.location_end = location_end
        field_value.location_text = location_text
        field_value.sentence = sentence_text_unit
        field_value.value = value
        field_value.extraction_hint = hint
        field_value.created_by = field_value.created_by or user
        field_value.modified_by = user
        field_value.created_date = field_value.created_date or datetime.now()
        field_value.modified_date = field_value.modified_date or datetime.now()

        if removed_by_user is not None:
            field_value.removed_by_user = removed_by_user

        with transaction.atomic():
            field_value.save()
            if user:
                models.DocumentTypeField.objects.set_dirty_for_value(field_value)

        return field_value

    def get_value(self, field_value):
        return field_value.value

    def delete(self, field_value, **kwargs):
        field_value.delete()

    def mark_removed_by_user(self, field_value):
        field_value.removed_by_user = True
        field_value.save()

    def value_to_string(self, field_value):
        return str(field_value.value)

    def example_json_value(self, field):
        return None


class StringField(FieldType):
    code = 'str'
    title = 'String'
    value_aware = True
    value_extracting = True

    def example_json_value(self, field):
        return "example_string"

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        regexp = field.value_regexp
        extracted = None
        if regexp:
            extracted = re.findall(regexp, text)
            for index, value in enumerate(extracted):
                extracted[index] = value.strip()

        return extracted or None


class ChoiceField(FieldType):
    code = 'choice'
    title = 'Choice'
    value_aware = True
    value_extracting = False

    def _extract_from_possible_value(self, field, possible_value):
        if possible_value in field.get_choice_values():
            return possible_value
        else:
            return None

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        return None

    def example_json_value(self, field):
        choice_values = field.get_choice_values()
        return choice_values[randint(0, len(choice_values) - 1)] if choice_values else None


class MultiChoiceField(ChoiceField):
    code = 'multi_choice'
    title = 'Multi Choice'
    multi_value = True
    value_aware = True
    value_extracting = False

    def example_json_value(self, field):
        choice_values = field.get_choice_values()
        if not choice_values:
            return None
        res = set()
        for i in range(randint(0, len(choice_values))):
            res.add(choice_values[randint(0, len(choice_values) - 1)])
        return res


class DateField(FieldType):
    code = 'date'
    title = 'Date'
    value_aware = True
    value_extracting = True
    ordinal = True

    def _extract_from_possible_value(self, field, possible_value):
        if isinstance(possible_value, datetime):
            return possible_value.date()
        elif isinstance(possible_value, date):
            return possible_value
        else:
            try:
                return dateparser.parse(possible_value)
            except:
                return None

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        dates = get_dates_list(text) or []
        dates = [d for d in dates if d.year < 3000]
        return dates or None

    def example_json_value(self, field):
        return self.python_value_to_json(datetime.now())

    def json_value_to_python(self, json_value):
        if not json_value:
            return None

        return dateparser.parse(json_value)

    def python_value_to_json(self, python_value: datetime):
        if not python_value:
            return None
        return python_value.isoformat()


class FloatField(FieldType):
    code = 'float'
    title = 'Floating Point Number'
    value_aware = True
    value_extracting = True
    ordinal = True

    def _extract_from_possible_value(self, field, possible_value):
        try:
            return float(possible_value)
        except ValueError:
            return None

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        amounts = get_amounts(text, return_sources=False)
        return list(amounts) if amounts else None

    def example_json_value(self, field):
        return random() * 1000


class IntField(FieldType):
    code = 'int'
    title = 'Integer Number'
    value_aware = True
    value_extracting = True
    ordinal = True

    def _extract_from_possible_value(self, field, possible_value):
        try:
            return int(possible_value)
        except ValueError:
            return None

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        amounts = get_amounts(text, return_sources=False)
        if not amounts:
            return None
        amounts = [int(i) if int(i) == i else i for i in amounts
                   if isinstance(i, (float, int))]
        return amounts or None

    def example_json_value(self, field):
        return randint(0, 1000)


class AddressField(FieldType):
    code = 'address'
    title = 'Address'
    value_aware = True
    value_extracting = True

    @staticmethod
    def _get_from_geocode(address: str):
        g = geocoder.google(address)
        if g.ok:
            return {
                'address': str(g.address),
                'latitude': g.lat,
                'longitude': g.lng,
                'country': g.country_long,
                'province': g.province_long,
                'city': g.city_long
            }
        else:
            # Google does not know such address - probably we detected it wrong.
            return {
                'address': str(address),
                'latitude': None,
                'longitude': None,
                'country': None,
                'province': None,
                'city': None
            }

    def _extract_from_possible_value(self, field, possible_value):
        if not possible_value:
            return None

        if type(possible_value) is dict:
            address = possible_value.get('address')
        else:
            addresses = list(pyap.parse(str(possible_value), country='US'))

            if not addresses:
                addresses = list(get_addresses(str(possible_value)))

            address = addresses[0] if addresses else str(possible_value)

        return AddressField._get_from_geocode(address)

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        addresses = list(pyap.parse(text, country='US'))

        if not addresses:
            addresses = list(get_addresses(text))

        return [AddressField._get_from_geocode(address) for address in addresses]

    def value_to_string(self, field_value):
        if not field_value:
            return None
        return str(field_value.value['address'])

    def example_json_value(self, field):
        return {
            'address': 'Some address',
            'latitude': None,
            'longitude': None,
            'country': None,
            'province': None,
            'city': None
        }


class CompanyField(FieldType):
    code = 'company'
    title = 'Company'
    value_aware = True
    value_extracting = True

    def _extract_from_possible_value(self, field, possible_value):
        if possible_value:
            return str(possible_value)
        else:
            return None

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        companies = list(get_companies(text, detail_type=True, name_upper=True, strict=True))
        if not companies:
            return None
        return ['{0}{1}'.format(company[0].upper(),
                                (' ' + company[1].upper()) if company[1] is not None else '')
                for company in companies]

    def example_json_value(self, field):
        return 'SOME COMPANY LLC'


class DurationField(FieldType):
    code = 'duration'
    title = 'Duration'
    value_aware = True
    value_extracting = True
    ordinal = True
    MAX_DURATION = 5000 * 365

    def _extract_from_possible_value(self, field, possible_value):
        try:
            return float(possible_value)
        except ValueError:
            return None

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        durations = get_durations(text)
        if not durations:
            return None
        return [duration[2] for duration in durations if duration[2] < DurationField.MAX_DURATION]

    def example_json_value(self, field):
        return random() * 365 * 5


class RelatedInfoField(FieldType):
    code = 'related_info'
    title = 'Related Info'
    multi_value = True
    value_aware = False
    value_extracting = False


class PersonField(FieldType):
    code = 'person'
    title = 'Person'
    value_aware = True
    value_extracting = True

    def _extract_from_possible_value(self, field, possible_value):
        if possible_value:
            return str(possible_value)
        else:
            return None

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        persons = get_persons(text, return_source=False)
        return list(persons) if persons else None

    def example_json_value(self, field):
        return 'John Doe'


class AmountField(FloatField):
    code = 'amount'
    title = 'Amount'
    value_aware = True
    value_extracting = True
    ordinal = True

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        amounts = get_amounts(text, return_sources=False)
        return list(amounts) if amounts else None

    def example_json_value(self, field):
        return 25000.50


class MoneyField(FloatField):
    code = 'money'
    title = 'Money'
    value_aware = True
    value_extracting = True
    ordinal = True

    def _extract_from_possible_value(self, field, possible_value):
        if not possible_value:
            return None

        if type(possible_value) is dict \
                and possible_value.get('currency') \
                and possible_value.get('amount') is not None:
            return {
                'currency': possible_value.get('currency'),
                'amount': possible_value.get('amount')
            }

        try:
            amount = float(str(possible_value))
            return {
                'currency': 'USD',
                'amount': amount
            }
        except ValueError:
            return None

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        money = get_money(text, return_sources=False)
        if not money:
            return None
        return [{'currency': m[1],
                 'amount': m[0]} for m in money]

    def value_to_string(self, field_value):
        if not field_value:
            return None
        return '{amount} {currency}'.format(amount=field_value.get('amount'),
                                            currency=field_value.get('currency'))

    def example_json_value(self, field):
        return {
            'currency': 'USD',
            'amount': random() * 10000000,
        }


class GeographyField(FieldType):
    code = 'geography'
    title = 'Geography'
    value_aware = True
    value_extracting = True

    def _extract_from_possible_value(self, field, possible_value):
        if possible_value:
            return str(possible_value)
        else:
            return None

    def _extract_variants_from_text(self, field, text: str, **kwargs):

        geo_entities = None
        document = kwargs.get('document')
        if document is not None:
            # try to extract from GeoEntityUsage
            # pros: faster extraction
            # cons: we may extract extra entities
            geo_entities = extract_models.GeoEntityUsage.objects.filter(
                text_unit__document=document,
                text_unit__unit_type='sentence',
                text_unit__text__contains=text).values('entity_id', 'entity__name')

        if not geo_entities:
            # try to get geo config from cache
            geo_config = _redis.get('geo_config')
            if geo_config:
                geo_config = pickle.loads(geo_config)
            else:
                try:
                    geo_config_locate_storage_key = _redis.keys('*_locate')[0]
                    geo_config_locate_storage = pickle.loads(
                        _redis.get(geo_config_locate_storage_key))
                    geo_config = geo_config_locate_storage['geoentity']['geo_config']
                except (KeyError, IndexError):
                    from apps.task.tasks import Locate
                    geo_config = Locate.load_geo_config()
                _redis.set('geo_config', pickle.dumps(geo_config))

            text_languages = None
            if document:
                text_languages = models.TextUnit.objects.filter(
                    document=document,
                    text__contains=text).values_list('language', flat=True)
                if document.language and not text_languages:
                    text_languages = [document.language]

            geo_entities = [{'entity_id': i[0][0], 'entity__name': i[0][1]} for i in
                            get_geoentities(text,
                                            geo_config_list=geo_config,
                                            text_languages=text_languages,
                                            priority=True)]

        return list(geo_entities) or None

    def example_json_value(self, field):
        return [{'entity_id': 12, 'entity__name': 'New York'}]


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
    'amount': AmountField(),
    'money': MoneyField(),
    'geography': GeographyField(),
}
