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
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.0/LICENSE"
__version__ = "1.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

from datetime import datetime, date
from enum import Enum, unique
from random import randint, random
from typing import List, Tuple, Optional, Any, Callable, Dict

import dateparser
import pyap
from django.db import models as django_models
from django.db import transaction
from django.db.models import Q
from lexnlp.extract.en.addresses.addresses import get_addresses
from lexnlp.extract.en.amounts import get_amounts
from lexnlp.extract.en.dates import get_dates_list
from lexnlp.extract.en.durations import get_durations
from lexnlp.extract.en.entities.nltk_maxent import get_companies, get_persons
from lexnlp.extract.en.geoentities import get_geoentities
from lexnlp.extract.en.money import get_money
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import FeatureUnion
from sklearn.pipeline import Pipeline

from apps.common.fields import RoundedFloatField
from apps.document import models
from apps.document.fields_detection import vectorizers
from apps.extract import models as extract_models

ORDINAL_EXTRACTION_HINTS = ['TAKE_MIN', 'TAKE_MAX']


@unique
class ValueExtractionHint(Enum):
    TAKE_FIRST = "TAKE_FIRST"
    TAKE_SECOND = "TAKE_SECOND"
    TAKE_LAST = "TAKE_LAST"
    TAKE_MIN = "TAKE_MIN"
    TAKE_MAX = "TAKE_MAX"

    @staticmethod
    def _is_money(v) -> bool:
        return type(v) is dict and 'amount' in v and 'currency' in v

    @staticmethod
    def get_value(l: Optional[List], hint: str):
        if not l:
            return None

        if str(hint) == ValueExtractionHint.TAKE_LAST.name:
            return l[-1]
        elif str(hint) == ValueExtractionHint.TAKE_SECOND.name and len(l) > 1:
            return l[1]
        elif str(hint) == ValueExtractionHint.TAKE_FIRST.name and len(l) > 0:
            return l[0]
        elif str(hint) == ValueExtractionHint.TAKE_MIN.name:
            return min(l, key=lambda dd: dd['amount']) if ValueExtractionHint._is_money(l[0]) else min(l)
        elif str(hint) == ValueExtractionHint.TAKE_MAX.name:
            return max(l, key=lambda dd: dd['amount']) if ValueExtractionHint._is_money(l[0]) else max(l)
        else:
            return None


def to_float(v) -> Optional[float]:
    try:
        return float(v) if v is not None else None
    except ValueError:
        return None


def to_int(v) -> Optional[int]:
    try:
        return int(v) if v is not None else None
    except ValueError:
        return None


class FieldType:
    code = ''
    title = ''

    # If true: When detecting field values try to extract values in every sentence without their pre-selection
    #          regex field detectors or machine learning models. If extractor returns no value - then proceed
    #          to the next sentence.
    search_in_every_sentence = False

    # Does this field support storing multiple DocumentFieldValue objects per document+field
    multi_value = False

    # Should this field store some value or only mark piece of text as related to this field
    requires_value = False

    # Should this field allow storing some value even if it is not required
    allows_value = False

    # Does this field support extracting concrete value from sentence
    # or it only allows pre-assigned values.
    # (for value requiring fields)
    value_extracting = False

    ordinal = False

    default_hint = ValueExtractionHint.TAKE_FIRST.name

    def merge_multi_python_values(self, previous_merge_result, value_to_merge_in):
        """
        Merges a single value into the combined value.
        Annotated field values are stored in DocumentFieldValue models.
        For multi-value fields there can be multiple DocumentFieldValue per document+field but they
        need to be combined into a single value to cache in Document.field_values.

        Different field types can support different variants of combining multiple DocumentFieldValues.
        For example for related_info fields we store the number of entries in Document.field_values.

        But for most cases it will be enough to only combine the values into a set.
        :param previous_merge_result:
        :param value_to_merge_in:
        :return:
        """
        if self.multi_value:
            if not previous_merge_result:
                return {value_to_merge_in} if value_to_merge_in is not None else None
            else:
                if value_to_merge_in is not None:
                    previous_merge_result.add(value_to_merge_in)
                return previous_merge_result
        else:
            return value_to_merge_in

    def merged_python_value_to_db(self, merged_python_value):
        """
        Convert python value of the field into a DB-aware sortable form to save to Document.field_values.

        That's what it needed for:
            There are simple atomic field types like float, string, date e.t.c.
            But there are also structured fields - like Money (currency + amount) and maybe others.
            Use the code of the Money type as a reference.

            For all kinds of fields we need to solve two main problems:

            1. Good JSON-ready representation of their values suitable for python backend and JS frontend needs.
            Python backend should be able to calculate user-entered Python formulas based on the field values.
            Python backend should be able to store the field values in JSON in DB.
            Frontend should not know any implementation details but only have simple and understandable
            structure for displaying for example Money editor consisting of:
            (1) currency selector and (2) amount text field.
                ===> Document editing support with text annotating.

            2. Ability to query documents with sorting and filtering by concrete field values, with pagination
            support. And the querying should work on the database side.
                ===> Document Grid Support


            Field values are stored in DB in two forms:
            - detailed annotated form: DocumentFieldValue (contains text annotation per each value),
                there can be multiple DocumentFieldValues per field+document if the field type is multi-value;
            - short cached variant for querying and sorting: Document.field_values
            The engine maintains these two forms in the consistent state.

            DocumentFieldValue contains the original full json structure (e.g. { "currency": "USD", "amount": 5 }
            Document.field_values is a jsonb field of uids -> pre-formatted sortable values (e.g. "USD|0000000005.0000")

            This way we can query DB from Django with any sorting/pagination or >=< filtering by
            writing queries which access components of the Document.field_values jsonb field.

            Next to return to the frontend the original simple structure we should decode the sortable format
            back to the original JSON-ready form.

            This looks complicated but at the moment we don't have better solution. We need both text annotated
            detailed DocumentFieldValues for text-based machine learning and short sortable Document.field_values
            for easy DB querying.

            To allow the above we use the set of methods per each FieldType:
            - encode from normal Python structure to sortable DB-aware format;
            - decode back to the Python structure;
            - Django field type (TextField, FloatField and so on);

        Examples:
            For strings - it will be just the string because it is sortable and everything is fine.
            For money (currency + amount) - it should be something like "USD:000012345.67" allowing the currency
            to participate in the sorting.
            For dates - it should be something like sortable ISO format '2018-10-23T03:17'.
        Output format of this method should be restorable to the original python value.
        :param merged_python_value:
        :return:
        """
        return str(merged_python_value) if merged_python_value else None

    def merged_db_value_to_python(self, db_value):
        """
        Decode value created by merged_python_value_to_db() back to python value.
        See explanation in merged_python_value_to_db().
        :param db_value:
        :return:
        """
        return db_value

    def single_python_value_to_db(self, python_single_value):
        """
        Used for storing values in DB format in DocumentFieldValue models.
        Otherwise for example it looses date/datetime type on loading from DB.
        :param python_single_value:
        :return:
        """
        return self.merged_python_value_to_db(python_single_value)

    def single_db_value_to_python(self, db_value):
        return self.merged_db_value_to_python(db_value)

    def get_postgres_transform_map(self):
        """
        Return django DB field type suitable for this field type.

        Used in querying/sorting components of Document.field_value with django DB routines.
        :return:
        """
        return django_models.TextField

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        return None

    def _extract_from_possible_value(self, field, possible_value):
        return possible_value

    def extract_from_possible_value_text(self, field, possible_value_or_text):
        """
        Check if possible_value_or_text is also containing the value in this field type's data type.
        If not parse the possible_value_text var for extracting the first suitable value of this type.
        This method does not try to pick value hint or anything similar assuming that there is no
        source text available but only the value which is possibly in text form.
        :param field:
        :param possible_value_or_text:
        :return:
        """
        maybe_value = self._extract_from_possible_value(field, possible_value_or_text)
        if maybe_value:
            return maybe_value
        variants = self._extract_variants_from_text(field, possible_value_or_text)
        if variants:
            return variants[0]
        return None

    def _pick_hint_by_searching_for_value_among_extracted(self, field, text: str, value, **kwargs) -> Optional[str]:
        if not self.value_extracting:
            return None

        if value is None or not text:
            return self.default_hint

        extracted = self._extract_variants_from_text(field, text, **kwargs)

        if not extracted:
            return self.default_hint

        for hint in ValueExtractionHint:
            if value == ValueExtractionHint.get_value(extracted, hint):
                return hint.name

        return self.default_hint

    def get_or_extract_value(self, document, field, possible_value, possible_hint: str, text) \
            -> Tuple[Any, Optional[str]]:
        if possible_value is None and not text:
            return None, None

        # If we have some value provided, then try using it and picking hint for it
        # by simply finding this value in all values extracted from this text
        if possible_value is not None:
            value = self._extract_from_possible_value(field, possible_value)

            if value is not None:
                if self.value_extracting:
                    hint = possible_hint or self \
                        ._pick_hint_by_searching_for_value_among_extracted(field, text, value, document=document)
                else:
                    hint = None
                return value, hint

        # If we were unsuccessful in using the provided possible value, then try to extract it from
        # string representation of the provided possible value or from the full provided text

        if not self.value_extracting:
            return None, None

        text = str(possible_value) if possible_value else text

        extracted = self._extract_variants_from_text(field, text, document=document)

        if not extracted:
            return None, None

        value = ValueExtractionHint.get_value(extracted, possible_hint)
        if value is not None:
            return value, possible_hint
        else:
            return ValueExtractionHint.get_value(extracted, self.default_hint), self.default_hint

    def suggest_value(self,
                      document,
                      field,
                      location_text: str):
        value, hint = self.get_or_extract_value(document, field, location_text,
                                                self.default_hint, location_text)
        return value

    def _get_value_to_save(self, document, field, location_start: int, location_end: int, value):
        if self.multi_value:
            q = models.DocumentFieldValue.objects.filter(document=document,
                                                         field=field,
                                                         location_start=location_start,
                                                         location_end=location_end)
            q = q.filter(value__isnull=True) if value is None else q.filter(value=value)

            return q.first()
        else:
            return models.DocumentFieldValue.objects.filter(document=document, field=field).first()

    def save_value(self,
                   document,
                   field,
                   location_start: Optional[int],
                   location_end: Optional[int],
                   location_text: Optional[str],
                   text_unit,
                   value=None,
                   user=None,
                   allow_overwriting_user_data=True,
                   extraction_hint=None):
        """
        Saves a new value to the field. Depending on the field type it should either
        rewrite existing DocumentFieldValues or add new ones.
        """
        field_value = self._get_value_to_save(document, field,
                                              location_start, location_end, value)  # type: 'DocumentFieldValue'
        if self.requires_value and value is None:
            if field_value and (allow_overwriting_user_data or not field_value.is_user_value()):
                field_value.delete()
            return value

        if self.multi_value:
            if field_value:
                if field_value.removed_by_user:
                    if allow_overwriting_user_data:
                        field_value.removed_by_user = False
                        field_value.save()
                return field_value

            field_value = models.DocumentFieldValue()
            return self._update(field_value, document, field, location_start, location_end,
                                location_text,
                                text_unit,
                                value,
                                extraction_hint,
                                user)
        else:
            if field_value:
                qr = models.DocumentFieldValue.objects.filter(document=document, field=field).exclude(pk=field_value.pk)
                if not allow_overwriting_user_data:
                    qr = qr.exclude(Q(created_by__isnull=False) | Q(modified_by__isnull=False))
                qr.filter(location_start__isnull=True, location_end__isnull=True).delete()
                qr.exclude(location_start__isnull=True, location_end__isnull=True).update(removed_by_user=True)

                if (field_value.location_start is not None or field_value.location_end is not None) \
                        and location_start is None and location_end is None:
                    if field_value.removed_by_user:
                        field_value = models.DocumentFieldValue()
                    elif allow_overwriting_user_data:
                        models.DocumentFieldValue.objects.filter(pk=field_value.pk).update(removed_by_user=True)
                        field_value = models.DocumentFieldValue()
                    else:
                        return field_value
            else:
                field_value = models.DocumentFieldValue()

            # This will work only for existing field values having filled created_by or modified_by.
            if not allow_overwriting_user_data and field_value.is_user_value():
                return field_value
            else:
                return self._update(field_value, document, field, location_start, location_end,
                                    location_text, text_unit,
                                    value, extraction_hint, user)

    def _update(self, field_value, document, field,
                location_start: int, location_end: int, location_text: str, text_unit,
                value=None, hint=None,
                user=None):
        """
        Updates existing field value with the new data.
        """
        if field_value.id \
                and field_value.location_start == location_start \
                and field_value.location_end == location_end \
                and field_value.python_value == value \
                and field_value.extraction_hint == hint \
                and not field_value.removed_by_user:
            return field_value

        field_value.document = document
        field_value.field = field
        field_value.location_start = location_start
        field_value.location_end = location_end
        field_value.location_text = location_text
        field_value.text_unit = text_unit
        field_value.python_value = value
        field_value.extraction_hint = hint
        field_value.created_by = field_value.created_by or user
        field_value.modified_by = user
        field_value.created_date = field_value.created_date or datetime.now()
        field_value.modified_date = field_value.modified_date or datetime.now()
        field_value.removed_by_user = False

        with transaction.atomic():
            field_value.save()
            if user:
                models.DocumentField.objects.set_dirty_for_value(field_value)

        return field_value

    def get_value(self, field_value):
        return field_value.value

    def example_python_value(self, field):
        return None

    @staticmethod
    def _wrap_get_feature_names(vectorizer_step):
        """
        Return the function which retrieves the feature names from the vectorizer stored in its scope.
        For some vectorizers the feature names depend on the train data passed to them into the fit() function.
        Some field types return composite vectorizers in which only one / some of elements produce the features.
        This wrapper may be used by field type implementations to store the link to the vectorizer which does produce
        the features and use it to get the feature names in future after it is trained.
        :param vectorizer_step:
        :return:
        """
        return lambda: vectorizer_step.get_feature_names()

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        """
        Build SKLearn vectorization pipeline for this field.
        This is used in field-based machine learning when we calculate value of one field based on the
        values of other fields of this document.

        We are able to detect only choice fields this way at the moment.

        To reach this we need to build a feature vector of all dependencies of the field being detected.
        This feature vector is built as a union of feature vectors of each dependency.

        See how the whole pipeline is built in FieldBasedMLOnlyFieldDetectionStrategy.build_pipeline(..)

        :return: Tuple of: 1. List of vectorization steps - to be added to a Pipeline()
                           2. List of str feature names or a function returning list of str feature names.
        """
        vect = CountVectorizer(strip_accents='unicode', analyzer='word',
                               stop_words='english')
        return [('clean', vectorizers.ReplaceNoneTransformer('')),
                ('vect', vect),
                ('tfidf', TfidfTransformer())], self._wrap_get_feature_names(vect)


class StringField(FieldType):
    code = 'string'
    title = 'String (vectorizer uses words as tokens)'
    requires_value = True
    allows_value = True
    value_extracting = True

    def get_postgres_transform_map(self):
        return django_models.TextField

    def example_python_value(self, field):
        return "example_string"

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        regexp = field.get_compiled_value_regexp()
        extracted = None
        if regexp:
            extracted = regexp.findall(text)
            for index, value in enumerate(extracted):
                extracted[index] = value.strip()

        return extracted or None


class StringFieldWholeValueAsAToken(FieldType):
    code = 'string_no_word_wrap'
    title = 'String (vectorizer uses whole value as a token)'

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = CountVectorizer(strip_accents='unicode', analyzer='word',
                               stop_words='english',
                               tokenizer=vectorizers.whole_value_as_token)
        return [('clean', vectorizers.ReplaceNoneTransformer('')),
                ('vect', vect),
                ('tfidf', TfidfTransformer())], self._wrap_get_feature_names(vect)


class LongTextField(FieldType):
    code = 'text'
    title = 'Long Text'
    requires_value = True
    allows_value = True
    value_extracting = True

    def get_postgres_transform_map(self):
        return django_models.TextField

    def example_python_value(self, field):
        return "example\nmulti-line\ntext"

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        regexp = field.get_compiled_value_regexp()
        extracted = None
        if regexp:
            extracted = regexp.findall(text)
            for index, value in enumerate(extracted):
                extracted[index] = value.strip()

        return extracted or None


class ChoiceField(FieldType):
    code = 'choice'
    title = 'Choice'
    requires_value = True
    allows_value = True
    value_extracting = False

    def merged_python_value_to_db(self, merged_python_value):
        return str(merged_python_value) if merged_python_value else None

    def merged_db_value_to_python(self, db_value):
        return str(db_value) if db_value else None

    def get_postgres_transform_map(self):
        return django_models.TextField

    def _extract_from_possible_value(self, field, possible_value):
        if field.is_choice_value(possible_value):
            return possible_value
        else:
            return None

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        return None

    def example_python_value(self, field):
        choice_values = field.get_choice_values()
        return choice_values[randint(0, len(choice_values) - 1)] if choice_values else None

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = CountVectorizer(strip_accents='unicode', analyzer='word',
                               stop_words='english',
                               tokenizer=vectorizers.whole_value_as_token)
        return [('clean', vectorizers.ReplaceNoneTransformer('')),
                ('vect', vect),
                ('tfidf', TfidfTransformer())], self._wrap_get_feature_names(vect)


class BooleanField(FieldType):
    code = 'boolean'
    title = 'Boolean'
    requires_value = True
    allows_value = True
    value_extracting = False

    def merged_python_value_to_db(self, merged_python_value):
        return bool(merged_python_value)

    def merged_db_value_to_python(self, db_value):
        return bool(db_value)

    def get_postgres_transform_map(self):
        return django_models.BooleanField

    def _extract_from_possible_value(self, field, possible_value):
        if not possible_value:
            return False
        if type(possible_value) is bool:
            return bool(possible_value)
        elif type(possible_value) is str:
            return str(possible_value).lower() in {'yes', 'on', 'true'}
        else:
            return bool(possible_value)

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        return None

    def example_python_value(self, field):
        return False

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = vectorizers.NumberVectorizer()
        return [('vect', vect)], self._wrap_get_feature_names(vect)


class MultiChoiceField(ChoiceField):
    code = 'multi_choice'
    title = 'Multi Choice'
    multi_value = True
    requires_value = True
    allows_value = True
    value_extracting = False

    def merged_python_value_to_db(self, merged_python_value):
        if merged_python_value is None or type(merged_python_value) is not set:
            return None

        value_set = set(merged_python_value)
        return ', '.join(sorted([str(v) for v in value_set]))

    def merged_db_value_to_python(self, db_value: str):
        if not db_value:
            return None
        return {p.strip() for p in str(db_value).split(',')}

    def single_python_value_to_db(self, python_single_value):
        return str(python_single_value)

    def single_db_value_to_python(self, db_value):
        if not isinstance(db_value, str):
            raise RuntimeError('Non-string value found for a multi-choice field. Please run cleanup.')
        return db_value

    def get_postgres_transform_map(self):
        return django_models.TextField

    def example_python_value(self, field):
        choice_values = field.get_choice_values()
        if not choice_values:
            return None
        res = set()
        for i in range(randint(0, len(choice_values))):
            res.add(choice_values[randint(0, len(choice_values) - 1)])
        return res

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        count_vectorizer = CountVectorizer(strip_accents='unicode', analyzer='word',
                                           stop_words='english',
                                           tokenizer=vectorizers.list_items_as_tokens)
        return [('clean', vectorizers.ReplaceNoneTransformer('')),
                ('vect', count_vectorizer),
                ('tfidf', TfidfTransformer())], self._wrap_get_feature_names(count_vectorizer)


class DateTimeField(FieldType):
    code = 'datetime'
    title = 'DateTime: Non-recurring Events'
    requires_value = True
    allows_value = True
    value_extracting = True
    ordinal = True

    def merged_python_value_to_db(self, merged_python_value):
        if not merged_python_value:
            return None

        if type(merged_python_value) is date or type(merged_python_value) is datetime:
            return merged_python_value.isoformat()

        if type(merged_python_value) is str:
            return merged_python_value

        return None

    def merged_db_value_to_python(self, db_value):
        if not db_value:
            return None

        return dateparser.parse(str(db_value))

    def get_postgres_transform_map(self):
        return django_models.DateTimeField

    def _extract_from_possible_value(self, field, possible_value):
        if isinstance(possible_value, datetime) or isinstance(possible_value, date):
            return possible_value
        else:
            try:
                return dateparser.parse(str(possible_value))
            except:
                return None

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        dates = get_dates_list(text) or []
        dates = [d.date() if isinstance(d, datetime) else d
                 for d in dates if d.year < 3000]
        return dates or None

    def example_python_value(self, field):
        return datetime.now()

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = vectorizers.SerialDateVectorizer()
        return [('vect', vect)], lambda: vect.get_feature_names()


class DateField(FieldType):
    code = 'date'
    title = 'Date: Non-recurring Events'
    requires_value = True
    allows_value = True
    value_extracting = True
    ordinal = True

    def merged_python_value_to_db(self, merged_python_value):
        if not merged_python_value:
            return None

        if type(merged_python_value) is date:
            return merged_python_value.isoformat()

        if type(merged_python_value) is datetime:
            return merged_python_value.date().isoformat()

        if type(merged_python_value) is str:
            return merged_python_value

        return None

    def merged_db_value_to_python(self, db_value):
        if not db_value:
            return None

        return dateparser.parse(str(db_value)).date()

    def get_postgres_transform_map(self):
        return django_models.DateField

    def _extract_from_possible_value(self, field, possible_value):
        if isinstance(possible_value, datetime):
            return possible_value.date()
        elif isinstance(possible_value, date):
            return possible_value
        else:
            try:
                return dateparser.parse(str(possible_value)).date()
            except:
                return None

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        dates = get_dates_list(text) or []
        dates = [d.date() if isinstance(d, datetime) else d
                 for d in dates if d.year < 3000]
        return dates or None

    def example_python_value(self, field):
        return datetime.now()

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = vectorizers.SerialDateVectorizer()
        return [('vect', vect)], lambda: vect.get_feature_names()


class RecurringDateField(DateField):
    code = 'date_recurring'
    title = 'Date: Recurring Events'

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = vectorizers.RecurringDateVectorizer()
        return [('vect', vect)], lambda: vect.get_feature_names()


class FloatField(FieldType):
    code = 'float'
    title = 'Floating Point Number'
    requires_value = True
    allows_value = True
    value_extracting = True
    ordinal = True

    def merged_python_value_to_db(self, merged_python_value):
        return to_float(merged_python_value)

    def merged_db_value_to_python(self, db_value):
        return to_float(db_value)

    def get_postgres_transform_map(self):
        return RoundedFloatField

    def _extract_from_possible_value(self, field, possible_value):
        return to_float(possible_value)

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        amounts = get_amounts(text, return_sources=False)
        return list(amounts) if amounts else None

    def example_python_value(self, field):
        return random() * 1000

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = vectorizers.NumberVectorizer()
        return [('vect', vect)], self._wrap_get_feature_names(vect)


class IntField(FieldType):
    code = 'int'
    title = 'Integer Number'
    requires_value = True
    allows_value = True
    value_extracting = True
    ordinal = True

    def merged_python_value_to_db(self, merged_python_value):
        return to_int(merged_python_value)

    def merged_db_value_to_python(self, db_value):
        return to_int(db_value)

    def get_postgres_transform_map(self):
        return django_models.IntegerField

    def _extract_from_possible_value(self, field, possible_value):
        return to_int(possible_value)

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        amounts = get_amounts(text, return_sources=False)
        if not amounts:
            return None
        amounts = [int(i) if int(i) == i else i for i in amounts
                   if isinstance(i, (float, int))]
        return amounts or None

    def example_python_value(self, field):
        return randint(0, 1000)

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = vectorizers.NumberVectorizer()
        return [('vect', vect)], self._wrap_get_feature_names(vect)


class AddressField(FieldType):
    code = 'address'
    title = 'Address'
    requires_value = True
    allows_value = True
    value_extracting = True

    def merged_python_value_to_db(self, merged_python_value):
        if merged_python_value is None:
            return None
        return merged_python_value.get('address') if type(merged_python_value) is dict else str(merged_python_value)

    def merged_db_value_to_python(self, db_value):
        return {'address': db_value}

    def get_postgres_transform_map(self):
        return django_models.TextField

    @staticmethod
    def _get_from_geocode(address: str):
        # geocoding is removed as google api is not free now !!
        return {
            'address': str(address),
            'latitude': None,
            'longitude': None,
            'country': None,
            'province': None,
            'city': None
        }

    def _extract_from_possible_value(self, field, possible_value):
        if possible_value is None:
            return None

        if type(possible_value) is dict:
            return possible_value
        else:
            return {'address': str(possible_value)}

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        addresses = list(pyap.parse(text, country='US'))
        result = []

        if not addresses:
            addresses = list(get_addresses(text))

        resolved_addresses = {}
        while addresses:
            address = addresses.pop(0)
            resolved_address = resolved_addresses.get(address)
            if resolved_address is None:
                resolved_address = AddressField._get_from_geocode(address)
                resolved_addresses[address] = resolved_address
            result.append(resolved_address)
        return result

    def example_python_value(self, field):
        return {
            'address': 'Some address',
            'latitude': None,
            'longitude': None,
            'country': None,
            'province': None,
            'city': None
        }

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = CountVectorizer(strip_accents='unicode', analyzer='word',
                               stop_words='english')
        return [('item_select', vectorizers.DictItemSelector('address')),
                ('clean', vectorizers.ReplaceNoneTransformer('')),
                ('vect', vect),
                ('tfidf', TfidfTransformer())], self._wrap_get_feature_names(vect)


class CompanyField(FieldType):
    code = 'company'
    title = 'Company'
    requires_value = True
    allows_value = True
    value_extracting = True

    def merged_python_value_to_db(self, merged_python_value):
        return str(merged_python_value) if merged_python_value else None

    def merged_db_value_to_python(self, db_value):
        return db_value

    def get_postgres_transform_map(self):
        return django_models.TextField

    def _extract_from_possible_value(self, field, possible_value):
        if possible_value is not None:
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

    def example_python_value(self, field):
        return 'SOME COMPANY LLC'

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = CountVectorizer(strip_accents='unicode', analyzer='word',
                               stop_words='english', tokenizer=vectorizers.whole_value_as_token)
        return [('clean', vectorizers.ReplaceNoneTransformer('')),
                ('vect', vect),
                ('tfidf', TfidfTransformer())], self._wrap_get_feature_names(vect)


class DurationField(FieldType):
    code = 'duration'
    title = 'Duration'
    requires_value = True
    allows_value = True
    value_extracting = True
    ordinal = True
    MAX_DURATION = 5000 * 365

    def merged_python_value_to_db(self, merged_python_value):
        return to_float(merged_python_value)

    def merged_db_value_to_python(self, db_value):
        return to_float(db_value)

    def get_postgres_transform_map(self):
        return RoundedFloatField

    def _extract_from_possible_value(self, field, possible_value):
        return to_float(possible_value)

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        durations = get_durations(text)
        if not durations:
            return None
        return [duration[2] for duration in durations if duration[2] < DurationField.MAX_DURATION]

    def example_python_value(self, field):
        return random() * 365 * 5

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = vectorizers.NumberVectorizer(to_float_converter=lambda d: d.total_seconds() if d else 0 if d else 0)
        return [('vect', vect)], self._wrap_get_feature_names(vect)


class RelatedInfoField(FieldType):
    code = 'related_info'
    title = 'Related Info'
    multi_value = True
    requires_value = False
    allows_value = True
    value_extracting = False

    def merged_python_value_to_db(self, merged_python_value):
        return merged_python_value

    def merged_db_value_to_python(self, db_value):
        return db_value

    def single_python_value_to_db(self, python_single_value):
        return python_single_value

    def single_db_value_to_python(self, db_value):
        return db_value

    def get_postgres_transform_map(self):
        return django_models.IntegerField

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = vectorizers.NumberVectorizer(to_float_converter=lambda merged: len(merged) if merged else 0)
        return [('vect', vect)], self._wrap_get_feature_names(vect)

    def example_python_value(self, field):
        return 1

    def merge_multi_python_values(self, previous_merge_result, value_to_merge_in):
        return super().merge_multi_python_values(previous_merge_result, value_to_merge_in or '')


class PersonField(FieldType):
    code = 'person'
    title = 'Person'
    requires_value = True
    allows_value = True
    value_extracting = True

    def merged_python_value_to_db(self, merged_python_value):
        return merged_python_value

    def merged_db_value_to_python(self, db_value):
        return db_value

    def get_postgres_transform_map(self):
        return django_models.TextField

    def _extract_from_possible_value(self, field, possible_value):
        if possible_value is not None:
            return str(possible_value)
        else:
            return None

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        persons = get_persons(text, return_source=False)
        return list(persons) if persons else None

    def example_python_value(self, field):
        return 'John Doe'

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = CountVectorizer(strip_accents='unicode', analyzer='word',
                               stop_words='english', tokenizer=vectorizers.whole_value_as_token)
        return [('clean', vectorizers.ReplaceNoneTransformer('')),
                ('vect', vect),
                ('tfidf', TfidfTransformer())], self._wrap_get_feature_names(vect)


class AmountField(FloatField):
    code = 'amount'
    title = 'Amount'
    requires_value = True
    allows_value = True
    value_extracting = True
    ordinal = True

    def merged_python_value_to_db(self, merged_python_value):
        return to_float(merged_python_value)

    def merged_db_value_to_python(self, db_value):
        return to_float(db_value)

    def get_postgres_transform_map(self):
        return RoundedFloatField

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        amounts = get_amounts(text, return_sources=False)
        return list(amounts) if amounts else None

    def example_python_value(self, field):
        return 25000.50

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = vectorizers.NumberVectorizer()
        return [('vect', vect)], self._wrap_get_feature_names(vect)


class MoneyField(FloatField):
    code = 'money'
    title = 'Money'
    requires_value = True
    allows_value = True
    value_extracting = True
    ordinal = True

    def merged_python_value_to_db(self, merged_python_value):
        if not merged_python_value:
            return None
        if isinstance(merged_python_value, list):
            merged_python_value = merged_python_value[0]
        amount = to_float(merged_python_value.get('amount')) or 0
        currency = merged_python_value.get('currency') or ''
        return '{}|{:020.4f}'.format(currency, amount)

    def merged_db_value_to_python(self, db_value):
        if db_value is None:
            return None
        if isinstance(db_value, dict):
            return {
                'currency': db_value.get('currency'),
                'amount': float(db_value.get('amount')) if 'amount' in db_value else None
            }

        ar = db_value.split('|')
        currency = ar[0]
        amount_str = ar[1]  # type: str
        return {
            'currency': currency,
            'amount': to_float(amount_str)
        }

    def get_postgres_transform_map(self):
        return django_models.TextField

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
            amount = to_float(str(possible_value))
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

    def example_python_value(self, field):
        return {
            'currency': 'USD',
            'amount': random() * 10000000,
        }

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect_cur = CountVectorizer(strip_accents='unicode', analyzer='word',
                                   stop_words='english', tokenizer=vectorizers.whole_value_as_token)
        vect_amount = vectorizers.NumberVectorizer()

        def get_feature_names_(vect_cur_, vect_amount_):
            def res():
                return ['currency_' + str(c) for c in vect_cur_.get_feature_names()] \
                       + ['amount_' + str(fn) for fn in vect_amount_.get_feature_names()]

            return res

        return [
                   ('vect', FeatureUnion(transformer_list=[
                       ('currency', Pipeline([
                           ('selector', vectorizers.DictItemSelector(item='currency')),
                           ('clean', vectorizers.ReplaceNoneTransformer('')),
                           ('vect', vect_cur),
                           ('tfidf', TfidfTransformer()),
                       ])),
                       ('amount', Pipeline([
                           ('selector', vectorizers.DictItemSelector(item='amount')),
                           ('vect', vect_amount),
                       ]))
                   ]))
               ], get_feature_names_(vect_cur, vect_amount)


class GeographyField(FieldType):
    code = 'geography'
    title = 'Geography'
    requires_value = True
    allows_value = True
    value_extracting = True

    def get_postgres_transform_map(self):
        return django_models.TextField

    def _extract_variants_from_text(self, field, text: str, **kwargs):
        geo_entities = None
        document = kwargs.get('document')
        if document is not None:
            # try to extract from GeoEntityUsage
            # pros: faster extraction
            # cons: we may extract extra entities
            geo_entities = extract_models.GeoEntityUsage.objects \
                .filter(text_unit__document=document,
                        text_unit__unit_type='sentence',
                        text_unit__text__contains=text) \
                .values_list('entity__name', flat=True)

        if not geo_entities:
            from apps.extract import dict_data_cache
            geo_config = dict_data_cache.get_geo_config()

            text_languages = None
            if document:
                text_languages = models.TextUnit.objects.filter(
                    document=document,
                    text__contains=text).values_list('language', flat=True)
                if document.language and not text_languages:
                    text_languages = [document.language]

            geo_entities = [i[0][1] for i in get_geoentities(text,
                                                             geo_config_list=geo_config,
                                                             text_languages=text_languages,
                                                             priority=True)]
        return list(geo_entities) or None

    def example_python_value(self, field):
        return 'New York'

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = CountVectorizer(strip_accents='unicode', analyzer='word',
                               stop_words='english', tokenizer=vectorizers.whole_value_as_token)
        return [('clean', vectorizers.ReplaceNoneTransformer('')),
                ('vect', vect),
                ('tfidf', TfidfTransformer())], self._wrap_get_feature_names(vect)


FIELD_TYPES_CHOICE = {ChoiceField.code, MultiChoiceField.code}

_FIELD_TYPES = (StringField,
                StringFieldWholeValueAsAToken,
                LongTextField,
                IntField,
                BooleanField,
                FloatField,
                DateTimeField,
                DateField,
                RecurringDateField,
                CompanyField,
                DurationField,
                AddressField,
                RelatedInfoField,
                ChoiceField,
                MultiChoiceField,
                PersonField,
                AmountField,
                MoneyField,
                GeographyField)

FIELD_TYPES_REGISTRY = {field_type.code: field_type() for field_type in _FIELD_TYPES}  # type: Dict[str, FieldType]
