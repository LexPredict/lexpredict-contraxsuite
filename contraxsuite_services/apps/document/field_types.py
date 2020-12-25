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

import decimal
import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from random import randint, random
from typing import List, Tuple, Optional, Any, Callable, Set

import dateparser
import pyap
from lexnlp.extract.en.addresses.addresses import get_addresses
from lexnlp.extract.en.amounts import get_amounts
from lexnlp.extract.en.dates import get_dates_list
from lexnlp.extract.en.durations import get_durations
from lexnlp.extract.en.entities.nltk_maxent import get_persons
from lexnlp.extract.en.geoentities import get_geoentities
from lexnlp.extract.en.money import get_money
from lexnlp.extract.en.percents import get_percents
from lexnlp.extract.en.ratios import get_ratios
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from sklearn.pipeline import FeatureUnion, Pipeline

from apps.companies_extractor import CompaniesExtractor
from apps.document.field_processing import vectorizers
from apps.document.models import DocumentField, Document
from apps.document.value_extraction_hints import ValueExtractionHint

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def to_decimal(v, decimal_places=6) -> Optional[float]:
    """
    Take care about proper rounding for floats:
    round(float('123.5555555'), 6)
    123.555555
    vs
    to_decimal('123.5555555', 6)
    123.555556
    """
    if v is None:
        return None

    # This method is used in two kinds of operations:
    #
    # 1. Converting floating point values coming from UI to Python values.
    # JSON decoder for the API endpoint brings such values in form of Python "float".
    # We convert them to Decimal via str() to avoid non-visible precision digits from appearing.
    # This makes sense because such values were already represented as float/double
    # values on the frontend side and the UI form fields do not allow entering more
    # than 6 digits after dot.
    #
    # 2. Converting floating point values coming from DB to Python values.
    # To avoid loosing anything we decided to store Decimal values as strings in the DB.
    # Strings are converted to Decimals as is.
    if not isinstance(v, Decimal):
        v = Decimal(str(v))
    if isinstance(decimal_places, int):
        v = round(v, decimal_places).normalize()
    return v


def to_int(v) -> Optional[int]:
    return int(v) if v is not None else None


ATTR_TYPED_FIELD = '__typed_field__'


class TypedField:
    type_code = ''
    title = ''

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

    is_choice_field = False

    default_hint = ValueExtractionHint.TAKE_FIRST.name

    def __init__(self, field: DocumentField) -> None:
        super().__init__()
        self.field = field

    def is_there_annotation_matching_field_value(self, field_value: Any, annotation_values: List) -> bool:
        if field_value is None:
            return True
        return not self.field.requires_text_annotations or any([av == field_value for av in annotation_values])

    def annotation_value_matches_field_value(self, field_value: Any, annotation_value: Any) -> bool:
        return field_value == annotation_value

    def is_json_field_value_ok(self, val: Any):
        raise NotImplementedError()

    def is_python_field_value_ok(self, val: Any):
        return self.is_json_field_value_ok(val)

    def is_python_annotation_value_ok(self, val: Any) -> bool:
        return self.is_json_annotation_value_ok(val)

    def is_json_annotation_value_ok(self, val: Any):
        return self.is_json_field_value_ok(val)

    def field_value_python_to_json(self, python_value: Any) -> Any:
        return python_value

    def field_value_json_to_python(self, json_value: Any) -> Any:
        return json_value

    def annotation_value_python_to_json(self, python_value: Any) -> Any:
        return self.field_value_python_to_json(python_value)

    def annotation_value_json_to_python(self, json_value: Any) -> Any:
        return self.field_value_json_to_python(json_value)

    def _extract_variants_from_text(self, text: str,
                                    doc: Document) -> Optional[List]:
        return None

    def extract_from_possible_value(self, possible_value):
        return possible_value

    def extract_from_possible_value_text(self, possible_value_or_text,
                                         doc: Document):
        """
        Check if possible_value_or_text is also containing the value in this field type's data type.
        If not parse the possible_value_text var for extracting the first suitable value of this type.
        This method does not try to pick value hint or anything similar assuming that there is no
        source text available but only the value which is possibly in text form.
        :param doc: Document in which we are detecting. May be used for getting context info such as language.
        :param text_unit_if_avail: Text unit in which we are detecting (if available). May be used for getting context
                                    info such as pre-located usage entities.
        :param possible_value_or_text:
        :return:
        """
        try:
            maybe_value = self.extract_from_possible_value(possible_value_or_text)
        except Exception as e:
            raise RuntimeError(
                f'Incorrect value ("{possible_value_or_text}") for field "{self.field.code}" ({self.type_code})') from e
        if maybe_value:
            return maybe_value
        variants = self._extract_variants_from_text(possible_value_or_text,
                                                    doc=doc)
        if variants:
            return variants[0]
        return None

    def pick_hint_by_searching_for_value_among_extracted(self,
                                                         text: str,
                                                         value,
                                                         doc: Document) \
            -> Optional[str]:
        if not self.value_extracting:
            return None

        if value is None or not text:
            return self.default_hint

        extracted = self._extract_variants_from_text(text, doc=doc)

        if not extracted:
            return self.default_hint

        for hint in ValueExtractionHint:
            if value == ValueExtractionHint.get_value(extracted, hint):
                return hint.name

        return self.default_hint

    def get_or_extract_value(self,
                             document: Document,
                             possible_value,
                             possible_hint: Optional[str],
                             text: Optional[str]) \
            -> Tuple[Any, Optional[str]]:
        if possible_value is None and not text:
            return None, None

        # If we have some value provided, then try using it and picking hint for it
        # by simply finding this value in all values extracted from this text
        if possible_value is not None:
            value = self.extract_from_possible_value(possible_value)

            if value is not None:
                if self.value_extracting:
                    hint = possible_hint or self \
                        .pick_hint_by_searching_for_value_among_extracted(text,
                                                                          value,
                                                                          doc=document)
                else:
                    hint = None
                return value, hint

        # If we were unsuccessful in using the provided possible value, then try to extract it from
        # string representation of the provided possible value or from the full provided text

        if not self.value_extracting:
            return None, None

        text = str(possible_value) if possible_value else text

        extracted = self._extract_variants_from_text(text=text, doc=document)

        if not extracted:
            return None, None

        value = ValueExtractionHint.get_value(extracted, possible_hint)
        if value is not None:
            return value, possible_hint
        else:
            return ValueExtractionHint.get_value(extracted, self.default_hint), self.default_hint

    def suggest_value(self,
                      document,
                      location_text: str):
        value, hint = self.get_or_extract_value(document, location_text,
                                                self.default_hint, location_text)
        return value

    def example_python_value(self):
        return None

    @classmethod
    def _wrap_get_feature_names(cls, vectorizer_step):
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

    def _build_stop_words(self) -> Set[str]:
        additional_stop_words = self.field.get_vectorizer_stop_words()
        if additional_stop_words:
            stop_words = set(ENGLISH_STOP_WORDS)
            stop_words.update(additional_stop_words)
            return stop_words
        else:
            return ENGLISH_STOP_WORDS

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
                               stop_words=self._build_stop_words())
        return [('clean', vectorizers.ReplaceNoneTransformer('')),
                ('vect', vect),
                ('tfidf', TfidfTransformer())], self._wrap_get_feature_names(vect)

    @staticmethod
    def by(field: DocumentField) -> 'TypedField':
        from apps.document.field_type_registry import FIELD_TYPE_REGISTRY
        code = field.type if isinstance(field, DocumentField) else str(field)

        try:
            res = getattr(field, ATTR_TYPED_FIELD)  # type: Optional[TypedField]
        except AttributeError:
            res = None
        if res is None or res.type_code != code:
            res = FIELD_TYPE_REGISTRY[code](field)
            setattr(field, ATTR_TYPED_FIELD, res)
        return res

    @classmethod
    def replace_decimals_with_floats_in_python_value_of_any_type(cls, v):
        """
        Convert python field value of any kind of TypedField to using float instead of Decimal.
        This method is intended for using in the formula calculation when the operations with Decimals are not
        supported.

        This method should support all TypedFields - it is quite easy because they all return simple value types
        or dicts.

        More strictly would be to implement a separate method per TypedField sub-class but it will
        require a lot of changes in the codebase which uses it. Creating this single method works because
        we know that all TypedFields work with quite simple python values and we can take all their kinds
        into accounts in this method.
        """
        if v is None:
            return None
        if isinstance(v, Decimal):
            return float(v)
        if isinstance(v, dict):
            return {k: cls.replace_decimals_with_floats_in_python_value_of_any_type(v) for k, v in v.items()}
        if isinstance(v, set):
            return {cls.replace_decimals_with_floats_in_python_value_of_any_type(i) for i in v}
        if isinstance(v, list):
            return [cls.replace_decimals_with_floats_in_python_value_of_any_type(i) for i in v]
        if isinstance(v, tuple):
            return (cls.replace_decimals_with_floats_in_python_value_of_any_type(i) for i in v)
        return v


class MultiValueField(TypedField):

    def build_json_field_value_from_json_ant_values(self, ant_values: List) -> Any:
        raise NotImplementedError()

    def update_field_value_by_changing_annotations(self,
                                                   current_ant_values: List,
                                                   old_field_value: Any,
                                                   added_ant_value: Any,
                                                   removed_ant_value: Any):
        raise NotImplementedError()


class MultiValueSetField(MultiValueField):

    def is_there_annotation_matching_field_value(self, field_value: List, annotation_values: List) -> bool:
        if not field_value:
            return True
        if not self.field.requires_text_annotations:
            return True
        if not annotation_values:
            return False
        ants = set(annotation_values)
        return all(fv in ants for fv in field_value)

    def annotation_value_matches_field_value(self, field_value: List, annotation_value: Any) -> bool:
        if not field_value:
            return False
        return any(fv == annotation_value for fv in field_value)

    def update_field_value_by_changing_annotations(self,
                                                   current_ant_values: List,
                                                   old_field_value: List,
                                                   added_ant_value: Any,
                                                   removed_ant_value: Any):

        # New field value consists of:
        # - values introduced by current annotations;
        # - values existed in the original field value not introduced by any annotation.
        #
        # If we removed an annotation value then we leave it in the field value
        # only if there is another annotation with this value.

        ant_values_set = set()

        if current_ant_values:
            ant_values_set.update(current_ant_values)

        if old_field_value and not self.field.requires_text_annotations:
            # Adding all previous field values to the new collection excepting the removed one.
            # But if the removed one was introduced by some other annotation - it will stay in the new field value.
            for old_fv_item in old_field_value:
                if old_fv_item != removed_ant_value:
                    ant_values_set.add(old_fv_item)

        return sorted(ant_values_set) if ant_values_set else None

    def build_json_field_value_from_json_ant_values(self, ant_values: List) -> Any:
        if not ant_values:
            return None
        return sorted(set(ant_values))

    def field_value_python_to_json(self, python_value: Set) -> Any:
        return sorted(python_value) if python_value else None

    def field_value_json_to_python(self, json_value: Any) -> Any:
        return set(json_value) if json_value else None

    def annotation_value_python_to_json(self, python_value: Any) -> Any:
        return python_value

    def annotation_value_json_to_python(self, json_value: Any) -> Any:
        return json_value


class StringField(TypedField):
    type_code = 'string'
    title = 'String (vectorizer uses words as tokens)'
    requires_value = True
    allows_value = True
    value_extracting = True

    def is_json_field_value_ok(self, val: Any):
        return val is None or isinstance(val, str)

    def example_python_value(self):
        return "example_string"

    def _extract_variants_from_text(self, text: str,
                                    doc: Document) -> Optional[List]:
        regexp = self.field.get_compiled_value_regexp()
        extracted = None
        if regexp:
            extracted = regexp.findall(text)
            for index, value in enumerate(extracted):
                if isinstance(value, tuple):
                    value = str(value[0])
                extracted[index] = value.strip()

        return extracted or None


class StringFieldWholeValueAsAToken(StringField):
    type_code = 'string_no_word_wrap'
    title = 'String (vectorizer uses whole value as a token)'
    requires_value = True
    allows_value = True
    value_extracting = True

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = CountVectorizer(strip_accents='unicode', analyzer='word',
                               stop_words=self._build_stop_words(),
                               tokenizer=vectorizers.whole_value_as_token)
        return [('clean', vectorizers.ReplaceNoneTransformer('')),
                ('vect', vect),
                ('tfidf', TfidfTransformer())], self._wrap_get_feature_names(vect)


class LongTextField(TypedField):
    type_code = 'text'
    title = 'Long Text'
    requires_value = True
    allows_value = True
    value_extracting = True

    def is_json_field_value_ok(self, val: Any):
        return val is None or isinstance(val, str)

    def example_python_value(self):
        return "example\nmulti-line\ntext"

    def _extract_variants_from_text(self, text: str,
                                    doc: Document) -> Optional[List]:
        regexp = self.field.get_compiled_value_regexp()
        extracted = None
        if regexp:
            extracted = regexp.findall(text)
            for index, value in enumerate(extracted):
                if isinstance(value, tuple):
                    value = str(value[0])
                extracted[index] = value.strip()

        return extracted or None


class ChoiceField(TypedField):
    type_code = 'choice'
    title = 'Choice'
    requires_value = True
    allows_value = True
    value_extracting = False
    is_choice_field = True

    def is_json_field_value_ok(self, val: Any):
        if val is None:
            return True
        if not isinstance(val, str):
            return False
        if self.field.allow_values_not_specified_in_choices:
            return True
        return val in self.field.get_choice_values()

    def extract_from_possible_value(self, possible_value):
        if self.field.is_choice_value(possible_value):
            return possible_value
        else:
            return None

    def _extract_variants_from_text(self, text: str,
                                    doc: Document) -> Optional[List]:
        return None

    def example_python_value(self):
        choice_values = self.field.get_choice_values()
        return choice_values[randint(0, len(choice_values) - 1)] if choice_values else None

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = CountVectorizer(strip_accents='unicode', analyzer='word',
                               stop_words=self._build_stop_words(),
                               tokenizer=vectorizers.whole_value_as_token)
        return [('clean', vectorizers.ReplaceNoneTransformer('')),
                ('vect', vect),
                ('tfidf', TfidfTransformer())], self._wrap_get_feature_names(vect)

    @classmethod
    def check_choice_values_list(
            cls,
            choice_values: List[str]
    ) -> List[str]:
        opt_num: int = 0
        errors: List[str] = []
        unique_opts: Set[str] = set()
        for opt in choice_values:
            opt_num += 1
            if not opt:
                errors.append(f'Option {opt_num} is empty.')
                continue
            if ',' in opt:
                errors.append(f'Option {opt_num} ({opt}) contains a comma.')
                continue
            if opt in unique_opts:
                errors.append(f'Option {opt_num} ({opt}) appeared multiple times.')
                continue
            unique_opts.add(opt)
        return errors


class BooleanField(TypedField):
    type_code = 'boolean'
    title = 'Boolean'
    requires_value = True
    allows_value = True
    value_extracting = False

    def is_json_field_value_ok(self, val: Any):
        return val is None or isinstance(val, bool) or val in {0, 1}

    def extract_from_possible_value(self, possible_value):
        if not possible_value:
            return False
        if type(possible_value) is bool:
            return bool(possible_value)
        elif type(possible_value) is str:
            return str(possible_value).lower() in {'yes', 'on', 'true'}
        else:
            return bool(possible_value)

    def _extract_variants_from_text(self, text: str,
                                    doc: Document) -> Optional[List]:
        return None

    def example_python_value(self):
        return False

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = vectorizers.NumberVectorizer()
        return [('vect', vect)], self._wrap_get_feature_names(vect)


class MultiChoiceField(ChoiceField, MultiValueSetField):
    type_code = 'multi_choice'
    title = 'Multi Choice'
    multi_value = True
    requires_value = True
    allows_value = True
    value_extracting = False
    is_choice_field = True

    def is_json_annotation_value_ok(self, val: Any):
        if val is None:
            return False
        if not isinstance(val, str):
            return False

        return self.field.is_choice_value(val)

    def is_json_field_value_ok(self, val: Any):
        if val is None:
            return True
        if not isinstance(val, list):
            return False
        if self.field.allow_values_not_specified_in_choices:
            return all([isinstance(v, str) for v in val])

        choices = self.field.get_choice_values()
        choices = set(choices) if choices is not None else set()

        return all([v in choices for v in val])

    def is_python_field_value_ok(self, val: Any):
        if val is None:
            return True
        if not isinstance(val, list) and not isinstance(val, set):
            return False
        if self.field.allow_values_not_specified_in_choices:
            return all([isinstance(v, str) for v in val])

        choices = self.field.get_choice_values()
        choices = set(choices) if choices is not None else set()

        return all([v in choices for v in val])

    def example_python_value(self):
        choice_values = self.field.get_choice_values()
        if not choice_values:
            return None
        res = set()
        for i in range(randint(0, len(choice_values))):
            res.add(choice_values[randint(0, len(choice_values) - 1)])
        return res

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        count_vectorizer = CountVectorizer(strip_accents='unicode', analyzer='word',
                                           stop_words=self._build_stop_words(),
                                           preprocessor=vectorizers.set_items_as_tokens_preprocessor,
                                           tokenizer=vectorizers.set_items_as_tokens)
        return [('clean', vectorizers.ReplaceNoneTransformer('')),
                ('vect', count_vectorizer),
                ('tfidf', TfidfTransformer())], self._wrap_get_feature_names(count_vectorizer)


class LinkedDocumentsField(MultiValueSetField):
    type_code = 'linked_documents'
    title = 'Linked Documents'
    multi_value = True
    requires_value = True
    allows_value = True
    value_extracting = True

    def is_json_field_value_ok(self, val: Any):
        if val is None:
            return True
        if not isinstance(val, list):
            return False
        if not all(isinstance(v, int) for v in val):
            return False

        from apps.document.models import Document
        return Document.objects.filter(pk__in=val).count() == len(val)

    def is_json_annotation_value_ok(self, val: Any):
        if not isinstance(val, int):
            return False
        from apps.document.models import Document
        return Document.objects.filter(pk=val).exists()

    def is_python_field_value_ok(self, val: Any):
        if val is None:
            return True
        if not isinstance(val, list) and not isinstance(val, set):
            return False
        if not all(isinstance(v, int) for v in val):
            return False

        from apps.document.models import Document
        return Document.objects.filter(pk__in=val).count() == len(val)

    def extract_from_possible_value(self, possible_value):
        if not isinstance(possible_value, int) and not isinstance(possible_value, str):
            return None

        if isinstance(possible_value, str):
            try:
                possible_value = int(possible_value)
            except ValueError:
                return None

        from apps.document.models import Document
        if not Document.objects.filter(pk=possible_value).exists():
            return None

        return possible_value

    def _extract_variants_from_text(self, text: str,
                                    doc: Document) -> Optional[List]:
        return None

    def example_python_value(self):
        res = set()
        for i in range(randint(0, 10)):
            res.add(randint(0, 12345))
        return res

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        count_vectorizer = CountVectorizer(strip_accents='unicode', analyzer='word',
                                           stop_words=self._build_stop_words(),
                                           preprocessor=vectorizers.set_items_as_tokens_preprocessor,
                                           tokenizer=vectorizers.set_items_as_tokens)
        return [('clean', vectorizers.ReplaceNoneTransformer('')),
                ('vect', count_vectorizer),
                ('tfidf', TfidfTransformer())], self._wrap_get_feature_names(count_vectorizer)


RE_DATE_TIME_ISO = re.compile(
    r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$')

RE_DATE_ISO = re.compile(
    r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])')


class DateTimeField(TypedField):
    type_code = 'datetime'
    title = 'DateTime: Non-recurring Events'
    requires_value = True
    allows_value = True
    value_extracting = True
    ordinal = True

    def is_json_field_value_ok(self, val: Any):
        if val is None:
            return True

        if not isinstance(val, str):
            return False

        return RE_DATE_TIME_ISO.fullmatch(val) is not None

    def is_python_field_value_ok(self, val: Any):
        return val is None or isinstance(val, datetime)

    def field_value_python_to_json(self, python_value: Any) -> Any:
        return python_value.isoformat() if python_value else None

    def field_value_json_to_python(self, json_value: Any) -> Any:
        if json_value is None:
            return None
        return dateparser.parse(json_value)

    def extract_from_possible_value(self, possible_value):
        if isinstance(possible_value, datetime) or isinstance(possible_value, date):
            return possible_value
        else:
            try:
                return dateparser.parse(str(possible_value))
            except:
                return None

    def _extract_variants_from_text(self, text: str,
                                    doc: Document) -> Optional[List]:
        dates = get_dates_list(text) or []
        dates = [d if isinstance(d, datetime) else datetime(d.year, d.month, d.day)
                 for d in dates if d.year < 3000]
        return dates or None

    def example_python_value(self):
        return datetime.now()

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = vectorizers.SerialDateVectorizer()
        return [('vect', vect)], lambda: vect.get_feature_names()


class DateField(TypedField):
    type_code = 'date'
    title = 'Date: Non-recurring Events'
    requires_value = True
    allows_value = True
    value_extracting = True
    ordinal = True

    def is_json_field_value_ok(self, val: Any):
        if val is None:
            return True

        if not isinstance(val, str):
            return False

        return RE_DATE_TIME_ISO.fullmatch(val) is not None or RE_DATE_ISO.fullmatch(val) is not None

    def is_python_annotation_value_ok(self, val: Any):
        return val is None or isinstance(val, datetime) or isinstance(val, date)

    def is_python_field_value_ok(self, val: Any):
        return val is None or isinstance(val, datetime) or isinstance(val, date)

    def field_value_python_to_json(self, python_value: Any) -> Any:
        if not python_value:
            return None
        if isinstance(python_value, datetime):
            return python_value.date().isoformat()
        return python_value.isoformat()

    def field_value_json_to_python(self, json_value: Any) -> Any:
        if json_value is None:
            return None
        if isinstance(json_value, date):
            return json_value
        if isinstance(json_value, str) and not json_value:
            return None
        return dateparser.parse(json_value).date()

    def extract_from_possible_value(self, possible_value):
        if isinstance(possible_value, datetime):
            return possible_value.date()
        elif isinstance(possible_value, date):
            return possible_value
        else:
            try:
                return dateparser.parse(str(possible_value)).date()
            except:
                return None

    def _extract_variants_from_text(self, text: str,
                                    doc: Document) -> Optional[List]:
        dates = get_dates_list(text) or []
        dates = [d.date() if isinstance(d, datetime) else d
                 for d in dates if d.year < 3000]
        return dates or None

    def example_python_value(self):
        return datetime.now()

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = vectorizers.SerialDateVectorizer()
        return [('vect', vect)], lambda: vect.get_feature_names()


class RecurringDateField(DateField):
    type_code = 'date_recurring'
    title = 'Date: Recurring Events'

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = vectorizers.RecurringDateVectorizer()
        return [('vect', vect)], lambda: vect.get_feature_names()


class FloatField(TypedField):
    type_code = 'float'
    title = 'Floating Point Number'
    requires_value = True
    allows_value = True
    value_extracting = True
    ordinal = True

    def is_json_field_value_ok(self, val: Any):
        return val is None or isinstance(val, (float, int, Decimal, str))

    def field_value_python_to_json(self, python_value: Any) -> Any:
        return to_decimal(python_value)

    def field_value_json_to_python(self, json_value: Any) -> Any:
        return to_decimal(json_value)

    def extract_from_possible_value(self, possible_value):
        return to_decimal(possible_value)

    def _extract_variants_from_text(self, text: str,
                                    doc: Document) -> Optional[List]:
        amounts = get_amounts(text, return_sources=False)
        return list(amounts) if amounts else None

    def example_python_value(self):
        return decimal.Decimal(random() * 1000)

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = vectorizers.NumberVectorizer()
        return [('vect', vect)], self._wrap_get_feature_names(vect)


class IntField(TypedField):
    type_code = 'int'
    title = 'Integer Number'
    requires_value = True
    allows_value = True
    value_extracting = True
    ordinal = True

    def is_json_field_value_ok(self, val: Any):
        return val is None or isinstance(val, int)

    def field_value_python_to_json(self, python_value: Any) -> Any:
        return to_int(python_value)

    def field_value_json_to_python(self, json_value: Any) -> Any:
        return to_int(json_value)

    def extract_from_possible_value(self, possible_value):
        return to_int(possible_value)

    def _extract_variants_from_text(self, text: str,
                                    doc: Document) -> Optional[List]:
        amounts = get_amounts(text, return_sources=False)
        if not amounts:
            return None
        amounts = [int(i) if int(i) == i else i for i in amounts
                   if isinstance(i, (float, int, Decimal))]
        return amounts or None

    def example_python_value(self):
        return randint(0, 1000)

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = vectorizers.NumberVectorizer()
        return [('vect', vect)], self._wrap_get_feature_names(vect)


class AddressField(TypedField):
    type_code = 'address'
    title = 'Address'
    requires_value = True
    allows_value = True
    value_extracting = True

    def is_json_field_value_ok(self, val: Any):
        if val is None:
            return True
        if not isinstance(val, dict):
            return False
        addr = val.get('address')
        return addr is None or isinstance(addr, str)

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

    def extract_from_possible_value(self, possible_value):
        if possible_value is None:
            return None

        if type(possible_value) is dict:
            return possible_value
        else:
            return {'address': str(possible_value)}

    def _extract_variants_from_text(self, text: str,
                                    doc: Document) -> Optional[List]:
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

    def example_python_value(self):
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
                               stop_words=self._build_stop_words())
        return [('item_select', vectorizers.DictItemSelector('address')),
                ('clean', vectorizers.ReplaceNoneTransformer('')),
                ('vect', vect),
                ('tfidf', TfidfTransformer())], self._wrap_get_feature_names(vect)


class CompanyField(TypedField):
    type_code = 'company'
    title = 'Company'
    requires_value = True
    allows_value = True
    value_extracting = True

    def is_json_field_value_ok(self, val: Any):
        return val is None or isinstance(val, str)

    def extract_from_possible_value(self, possible_value):
        if possible_value is not None:
            return str(possible_value)
        else:
            return None

    def _extract_variants_from_text(self, text: str,
                                    doc: Document) -> Optional[List]:
        companies = list(CompaniesExtractor.get_companies(
            text, detail_type=True, name_upper=True, strict=True))
        if not companies:
            return None
        return ['{0}{1}'.format(company[0].upper(),
                                (' ' + company[1].upper()) if company[1] is not None else '')
                for company in companies]

    def example_python_value(self):
        return 'SOME COMPANY LLC'

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = CountVectorizer(strip_accents='unicode', analyzer='word',
                               stop_words=self._build_stop_words(), tokenizer=vectorizers.whole_value_as_token)
        return [('clean', vectorizers.ReplaceNoneTransformer('')),
                ('vect', vect),
                ('tfidf', TfidfTransformer())], self._wrap_get_feature_names(vect)


class DurationField(TypedField):
    type_code = 'duration'
    title = 'Duration'
    requires_value = True
    allows_value = True
    value_extracting = True
    ordinal = True
    MAX_DURATION = 5000 * 365

    def is_json_field_value_ok(self, val: Any):
        return val is None or isinstance(val, (float, int, Decimal, str))

    def field_value_python_to_json(self, python_value: Any) -> Any:
        return to_decimal(python_value)

    def field_value_json_to_python(self, json_value: Any) -> Any:
        return to_decimal(json_value)

    def extract_from_possible_value(self, possible_value):
        return to_decimal(possible_value)

    def _extract_variants_from_text(self, text: str,
                                    doc: Document) -> Optional[List]:
        durations = get_durations(text)
        if not durations:
            return None
        return [duration[2] for duration in durations if duration[2] < self.MAX_DURATION]

    def example_python_value(self):
        return decimal.Decimal(random() * 365 * 5)

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = vectorizers.NumberVectorizer(to_float_converter=lambda d: d.total_seconds() if d else 0 if d else 0)
        return [('vect', vect)], self._wrap_get_feature_names(vect)


class PercentField(TypedField):
    type_code = 'percent'
    title = 'Percent'
    requires_value = True
    allows_value = True
    value_extracting = True
    ordinal = True
    MAX_PERCENT = 1

    def is_json_field_value_ok(self, val: Any):
        return val is None or isinstance(val, (float, int, Decimal, str))

    def field_value_python_to_json(self, python_value: Any) -> Any:
        return to_decimal(python_value)

    def field_value_json_to_python(self, json_value: Any) -> Any:
        return to_decimal(json_value)

    def extract_from_possible_value(self, possible_value):
        return to_decimal(possible_value, decimal_places=6)

    def _extract_variants_from_text(self, text: str,
                                    doc: Document) -> Optional[List]:
        percents = list(get_percents(text, float_digits=8))
        if not percents:
            return None
        return [percent[2] * 100 for percent in percents]
        # return [percent[2] for percent in percents if percent[2] < self.MAX_PERCENT]

    def example_python_value(self):
        return decimal.Decimal(round(random(), 6))

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = vectorizers.NumberVectorizer()
        return [('vect', vect)], self._wrap_get_feature_names(vect)


class RatioField(TypedField):
    type_code = 'ratio'
    title = 'Ratio'
    requires_value = True
    allows_value = True
    value_extracting = True
    ordinal = True

    def is_json_field_value_ok(self, val: Any):
        if val is None:
            return True
        if not isinstance(val, dict):
            return False
        n = val.get('numerator')
        if n is not None and not isinstance(n, int):
            return False
        c = val.get('denominator')
        if c is not None and not isinstance(c, int):
            return False
        return True

    def field_value_python_to_json(self, python_value: Any) -> Any:
        if python_value is None:
            return None
        d = dict(python_value)
        d['numerator'] = to_int(d.get('numerator'))
        d['denominator'] = to_int(d.get('denominator'))
        return d

    def field_value_json_to_python(self, json_value: Any) -> Any:
        if json_value is None:
            return None
        d = dict(json_value)
        d['numerator'] = to_int(d.get('numerator'))
        d['denominator'] = to_int(d.get('denominator'))
        return d

    def _extract_variants_from_text(self, text: str,
                                    doc: Document) -> Optional[List]:
        ratios = list(get_ratios(text))
        if not ratios:
            return None
        return [{'numerator': i[0],
                 'denominator': i[1]} for i in ratios]

    def example_python_value(self):
        return {'numerator': randint(1, 10), 'denominator': randint(1, 10)}

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect_numerator = vectorizers.NumberVectorizer()
        vect_denominator = vectorizers.NumberVectorizer()

        def get_feature_names_(vect_numerator, vect_denominator):
            def res():
                return ['numerator_' + str(c) for c in vect_numerator.get_feature_names()] \
                       + ['denominator_' + str(c) for c in vect_denominator.get_feature_names()]

            return res

        return [
                   ('vect', FeatureUnion(transformer_list=[
                       ('numerator', Pipeline([
                           ('selector', vectorizers.DictItemSelector(item='numerator')),
                           ('vect', vect_numerator),
                       ])),
                       ('denominator', Pipeline([
                           ('selector', vectorizers.DictItemSelector(item='denominator')),
                           ('vect', vect_denominator),
                       ]))
                   ]))
               ], get_feature_names_(vect_numerator, vect_denominator)


class RelatedInfoField(MultiValueField):
    type_code = 'related_info'
    title = 'Related Info'
    multi_value = True
    requires_value = False
    allows_value = True
    value_extracting = False

    def is_there_annotation_matching_field_value(self, field_value: Any, annotation_values: List) -> bool:
        if not field_value or not self.field.requires_text_annotations:
            return True
        return bool(annotation_values)

    def annotation_value_matches_field_value(self, field_value: Any, annotation_value: Any) -> bool:
        if not field_value:
            return False
        return True

    def is_json_field_value_ok(self, val: Any):
        return val is None or isinstance(val, bool) or val in {0, 1}

    def build_json_field_value_from_json_ant_values(self, ant_values: List) -> Any:
        return bool(ant_values)

    def update_field_value_by_changing_annotations(self,
                                                   current_ant_values: List,
                                                   old_field_value: List,
                                                   added_ant_value: Any,
                                                   removed_ant_value: Any):
        return self.build_json_field_value_from_json_ant_values(current_ant_values)

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = vectorizers.NumberVectorizer(to_float_converter=lambda merged: len(merged) if merged else 0)
        return [('vect', vect)], self._wrap_get_feature_names(vect)

    def example_python_value(self):
        return 1

    def _extract_variants_from_text(self, text: str,
                                    doc: Document) -> Optional[List]:
        return [True]


class PersonField(TypedField):
    type_code = 'person'
    title = 'Person'
    requires_value = True
    allows_value = True
    value_extracting = True

    def is_json_field_value_ok(self, val: Any):
        return val is None or isinstance(val, str)

    def extract_from_possible_value(self, possible_value):
        if possible_value is not None:
            return str(possible_value)
        return None

    def _extract_variants_from_text(self, text: str,
                                    doc: Document) -> Optional[List]:
        persons = get_persons(text, return_source=False)
        return list(persons) if persons else None

    def example_python_value(self):
        return 'John Doe'

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = CountVectorizer(strip_accents='unicode', analyzer='word',
                               stop_words=self._build_stop_words(), tokenizer=vectorizers.whole_value_as_token)
        return [('clean', vectorizers.ReplaceNoneTransformer('')),
                ('vect', vect),
                ('tfidf', TfidfTransformer())], self._wrap_get_feature_names(vect)


class AmountField(FloatField):
    type_code = 'amount'
    title = 'Amount'
    requires_value = True
    allows_value = True
    value_extracting = True
    ordinal = True

    def field_value_python_to_json(self, python_value: Any) -> Any:
        return to_decimal(python_value)

    def field_value_json_to_python(self, json_value: Any) -> Any:
        return to_decimal(json_value)

    def is_json_field_value_ok(self, val: Any):
        return val is None or isinstance(val, (float, int, Decimal, str))

    def _extract_variants_from_text(self, text: str,
                                    doc: Document) -> Optional[List]:
        amounts = get_amounts(text, return_sources=False)
        return list(amounts) if amounts else None

    def example_python_value(self):
        return decimal.Decimal(25000.50)

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = vectorizers.NumberVectorizer()
        return [('vect', vect)], self._wrap_get_feature_names(vect)


class MoneyField(FloatField):
    type_code = 'money'
    title = 'Money'
    requires_value = True
    allows_value = True
    value_extracting = True
    ordinal = True

    def is_json_field_value_ok(self, val: Any):
        if val is None:
            return True
        if not isinstance(val, dict):
            return False
        c = val.get('currency')
        if c is not None and not isinstance(c, str):
            return False
        a = val.get('amount')
        if a is not None and not isinstance(a, (float, int, Decimal, str)):
            return False
        return True

    def field_value_python_to_json(self, python_value: Any) -> Any:
        if python_value is None:
            return None
        d = dict(python_value)
        d['amount'] = to_decimal(d.get('amount'))
        return d

    def field_value_json_to_python(self, json_value: Any) -> Any:
        if json_value is None:
            return None
        d = dict(json_value)
        d['amount'] = to_decimal(d.get('amount'))
        return d

    def extract_from_possible_value(self, possible_value):
        if not possible_value:
            return None

        if isinstance(possible_value, dict) \
                and possible_value.get('currency') \
                and possible_value.get('amount') is not None:
            return {
                'currency': possible_value.get('currency'),
                'amount': possible_value.get('amount')
            }

        try:
            amount = to_decimal(str(possible_value))
            return {
                'currency': 'USD',
                'amount': amount
            }
        except ValueError:
            return None
        except InvalidOperation:
            return None

    def _extract_variants_from_text(self, text: str,
                                    doc: Document) -> Optional[List]:
        money = get_money(text, return_sources=False, float_digits=6)
        if not money:
            return None
        return [{'currency': m[1],
                 'amount': m[0]} for m in money]

    def example_python_value(self):
        return {
            'currency': 'USD',
            'amount': decimal.Decimal(round(random(), 9) * 10000000),
        }

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect_cur = CountVectorizer(strip_accents='unicode', analyzer='word',
                                   stop_words=self._build_stop_words(), tokenizer=vectorizers.whole_value_as_token)
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


class GeographyField(TypedField):
    type_code = 'geography'
    title = 'Geography'
    requires_value = True
    allows_value = True
    value_extracting = True

    def is_json_field_value_ok(self, val: Any):
        return val is None or isinstance(val, str)

    def _extract_variants_from_text(self, text: str,
                                    doc: Document) -> Optional[List]:
        # We don't use the pre-located geo usages here to avoid
        # different behaviour in regexp field detecting strategy, value suggestion api and other
        # places where this code may be used.
        # Looks like the text unit (to find the geo usages) is available in the field detection only
        # and there are multiple places where only the document and some text is available.
        from apps.extract import dict_data_cache
        geo_config = dict_data_cache.get_geo_config()
        geos = get_geoentities(text=text,
                               geo_config_list=geo_config,
                               text_languages=[doc.language],
                               priority=True)
        return [g[0].name for g in geos] or None

    def example_python_value(self):
        return 'New York'

    def build_vectorization_pipeline(self) -> Tuple[List[Tuple[str, Any]], Callable[[], List[str]]]:
        vect = CountVectorizer(strip_accents='unicode', analyzer='word',
                               stop_words=self._build_stop_words(), tokenizer=vectorizers.whole_value_as_token)
        return [('clean', vectorizers.ReplaceNoneTransformer('')),
                ('vect', vect),
                ('tfidf', TfidfTransformer())], self._wrap_get_feature_names(vect)


FIELD_TYPES_ALLOWED_FOR_DETECTED_VALUE = {
    StringField.type_code,
    StringFieldWholeValueAsAToken.type_code,
    LongTextField.type_code,
    ChoiceField.type_code,
    MultiChoiceField.type_code,
}

FIELD_TYPES = (StringField,
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
               PercentField,
               RatioField,
               AddressField,
               RelatedInfoField,
               ChoiceField,
               MultiChoiceField,
               PersonField,
               AmountField,
               MoneyField,
               GeographyField,
               LinkedDocumentsField)
