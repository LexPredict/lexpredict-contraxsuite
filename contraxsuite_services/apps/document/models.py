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

# Standard imports
import datetime
import hashlib
import pickle
import re
import uuid
from enum import Enum
from io import StringIO
from typing import List, Union, Any, Tuple

import jiphy
import pandas as pd

# Django imports
from ckeditor.fields import RichTextField
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Count, F, Value, QuerySet, Index, Q
from django.db.models.deletion import CASCADE, SET_NULL
from django.db.models.functions import Concat
from django.dispatch import receiver
from django.utils.html import format_html
from django.utils.timezone import now
from djangoql.queryset import DjangoQLQuerySet
from guardian.shortcuts import assign_perm, get_content_type
from picklefield import PickledObjectField
from simple_history.models import HistoricalRecords

from apps.common.fields import StringUUIDField, CustomJSONField
from apps.common.managers import BulkSignalsManager
from apps.common.model_utils.improved_django_json_encoder import ImprovedDjangoJSONEncoder
from apps.common.models import get_default_status
from apps.document import constants
from apps.document.value_extraction_hints import ValueExtractionHint, ORDINAL_EXTRACTION_HINTS
from apps.users.models import User, CustomUserObjectPermission
from apps.users.permissions import remove_perm, document_type_manager_permissions

# WARNING: Do not import from field_types.py here to avoid cyclic dependencies and unpredictable behavior.
# When RawdbFieldHandler of a field is required - use RawdbFieldHandler.of() in the client code.

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def all_reviewers():
    return {'role': 'reviewer'}


EXTRACTION_HINT_CHOICES = tuple((hint.name, hint.name) for hint in ValueExtractionHint)


class TimeStampedModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_date = models.DateTimeField(auto_now=True, db_index=True)
    created_by = models.ForeignKey(
        User, related_name="created_%(class)s_set", null=True, blank=True, db_index=True, on_delete=CASCADE)
    modified_by = models.ForeignKey(
        User, related_name="modified_%(class)s_set", null=True, blank=True, db_index=True, on_delete=CASCADE)

    class Meta:
        abstract = True

    @staticmethod
    def save_timestamp(sender, instance, created, func):
        if getattr(instance, 'request_user', None):
            models.signals.post_save.disconnect(func, sender=sender)
            if created:
                instance.created_by = instance.request_user
            instance.modified_by = instance.request_user
            instance.save()
            models.signals.post_save.connect(func, sender=sender)


class DocumentFieldCategory(models.Model):
    document_type = models.ForeignKey('document.DocumentType', null=True, blank=False,
                                      related_name='categories', on_delete=CASCADE)

    name = models.CharField(max_length=100, db_index=True)

    order = models.IntegerField(default=0)

    export_key = StringUUIDField(default=uuid.uuid4, editable=True, unique=True, null=False)

    class Meta:
        verbose_name_plural = 'Document Field Categories'
        ordering = ('order', 'name')

    def __str__(self):
        return "{}: type={} (#{})".format(self.name,
                                          self.document_type.code if self.document_type else None,
                                          self.pk)

    def __repr__(self):
        return self.__str__()


class DocumentFieldFamily(models.Model):
    code = models.CharField(max_length=100, blank=True, null=True, db_index=True)

    title = models.CharField(max_length=100, db_index=True)

    class Meta:
        verbose_name_plural = 'Document Field Families'
        ordering = ('title',)

    def __str__(self):
        return self.title

    def __repr__(self):
        return "{1} (#{0})".format(self.pk, self.title)

    @classmethod
    def make_unique_code(cls, source):
        code = re.sub(r'\W+', '_', source.lower()).strip('_')
        if cls.objects.filter(code=code).exists():
            similar_codes = cls.objects.filter(code__iregex=re.sub(r'(.+?)\d+$', r'\1\\d+', code))
            latest_index = max([int(re.sub(r'.+?(\d+)?$', r'\1', i) or 0)
                                for i in similar_codes.values_list('code', flat=True)])
            code_base = re.sub(r'_?\d+$', '', code)
            code = f'{code_base}_{latest_index + 1}'
        return code

    def save(self, **kwargs):
        if not self.code:
            self.code = self.make_unique_code(self.title)
        elif self.pk and DocumentFieldFamily.objects.exclude(pk=self.pk).filter(code=self.code).exists():
            self.code = self.make_unique_code(self.code)
        elif self.pk is None:
            self.code = self.make_unique_code(self.code)
        return super().save()


class DocumentFieldManager(models.Manager):
    def set_dirty_for_value(self, field_id: int, doc_type_id: str):
        field = self.get(pk=field_id, document_type_id=doc_type_id)
        field.dirty = True
        field.save()

    def _get_dirty_fields_filter(self):
        user_delay = DocumentFieldManager.get_user_delay()
        return self.filter(dirty=True,
                           value_detection_strategy__in=DocumentField.VALUE_DETECTION_AUTO_TRAINABLE,
                           training_finished=False,
                           modified_date__lt=user_delay)

    def has_dirty_fields(self):
        return self._get_dirty_fields_filter().exists()

    def get_dirty_fields(self):
        return self._get_dirty_fields_filter().prefetch_related('document_type').all()

    def assigned_fields(self):
        return self.filter(document_type__isnull=False)

    @staticmethod
    def get_user_delay():
        return now() - datetime.timedelta(seconds=settings.RETRAINING_DELAY_IN_SEC)


class DocumentField(TimeStampedModel):
    """DocumentField object model

    DocumentField describes manually created custom field for a document.
    """

    # WARNING: Do not add proxy methods to RawdbFieldHandler into the model class to avoid cyclic references and
    # unpredictable behavior.
    # When RawdbFieldHandler of a field is required - use RawdbFieldHandler.of() in the client code.
    # Let the model class be lightweight and the handlers of additional logic such as field_types.py/RawdbFieldHandler
    # or field handlers in rawdb plugged in as external components without straightforward referencing from the model.

    UNIT_TYPES = ((i, i) for i in ('sentence', 'paragraph', 'section'))
    CONFIDENCE = ('High', 'Medium', 'Low')
    CONFIDENCE_CHOICES = ((i, i) for i in CONFIDENCE)

    # Make pk field unique
    uid = StringUUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    document_type = models.ForeignKey('document.DocumentType', null=True, blank=False,
                                      related_name='fields', on_delete=CASCADE)

    # Short name for field.
    code = models.CharField(max_length=constants.DOCUMENT_FIELD_CODE_MAX_LEN,
                            db_index=True, unique=False, help_text='''Field codes must be lowercase, should start with 
a Latin letter, and contain only Latin letters, digits, underscores. Field codes must be unique to every Document Type.''')

    # Calculated field. Only for usage in __str__ function
    long_code = models.CharField(max_length=150, null=False, unique=True, default=None)

    # Verbose name for field.
    title = models.CharField(max_length=100, db_index=True)

    # Verbose description - information which does not fit into title
    description = models.TextField(null=True, blank=True)

    category = models.ForeignKey(DocumentFieldCategory, blank=True, null=True, db_index=True, on_delete=SET_NULL)

    family = models.ForeignKey(DocumentFieldFamily, blank=True, null=True, db_index=True, on_delete=SET_NULL)

    # Type of the field.
    # Choices are lazy-set on app init. See field_type_registry.py
    type = models.CharField(max_length=30, default='string', db_index=True)

    # Type of the text unit to parse.
    text_unit_type = models.CharField(max_length=10, choices=UNIT_TYPES, default='sentence')

    DETECT_LIMIT_NONE = 'NONE'
    DETECT_LIMIT_UNIT = 'UNIT'

    DETECT_LIMIT_OPTIONS = [(DETECT_LIMIT_NONE, 'No Limit'),
                            (DETECT_LIMIT_UNIT, 'Limit to N "text unit type" units')]

    # see detect_limit_count
    detect_limit_unit = models.CharField(max_length=10,
                                         choices=DETECT_LIMIT_OPTIONS,
                                         default=DETECT_LIMIT_NONE,
                                         help_text='''Choose to add an upward limit to the amount of document text 
                                         ContraxSuite will search for this Document Field. For example, you can choose 
                                         to only search the first 10 paragraphs of text for the value required (this 
                                         often works best for values like “Company,” “Execution Date,” or “Parties,”
                                         all of which typically appear in the first few paragraphs of a contract).''')

    # while detecting field value restrict to N units (see detect_limit_unit)
    # 0 means no limit
    detect_limit_count = models.IntegerField(null=False, default=0, db_index=True, help_text='''Specify the maximum 
range for a bounded search. Field detection begins at the top of the document and continues until this Nth 
"Detect limit unit" element.''')

    DEFAULT_UNSURE_THRESHOLD = 0.9

    VD_DISABLED = 'disabled'

    VD_USE_REGEXPS_ONLY = 'use_regexps_only'

    VD_REGEXP_TABLE = 'regexp_table'

    VD_USE_FORMULA_ONLY = 'use_formula_only'

    VD_REGEXPS_AND_TEXT_BASED_ML = 'regexps_and_text_based_ml'

    VD_TEXT_BASED_ML_ONLY = 'text_based_ml_only'

    VD_FORMULA_AND_FIELD_BASED_ML = 'formula_and_fields_based_ml'

    VD_FIELD_BASED_ML_ONLY = 'fields_based_ml_only'

    VD_FIELD_BASED_WITH_UNSURE_ML_ONLY = 'fields_based_prob_ml_only'

    VD_PYTHON_CODED_FIELD = 'python_coded_field'

    VD_FIELD_BASED_REGEXPS = 'field_based_regexps'

    VD_MLFLOW_MODEL = 'mlflow_model'

    VALUE_DETECTION_AUTO_TRAINABLE = {
        VD_REGEXPS_AND_TEXT_BASED_ML,
        VD_FORMULA_AND_FIELD_BASED_ML,
    }

    VALUE_DETECTION_STRATEGY_CHOICES = [(VD_DISABLED, 'Field detection disabled'),
                                        (VD_USE_REGEXPS_ONLY,
                                         'No ML. Use regexp field detectors.'),
                                        (VD_REGEXP_TABLE,
                                         'Use regexp pattern: value collection.'),
                                        (VD_USE_FORMULA_ONLY,
                                         'No ML. Use formula only.'),
                                        (VD_REGEXPS_AND_TEXT_BASED_ML,
                                         'Start with regexps, switch to text-based ML when possible.'),
                                        (VD_TEXT_BASED_ML_ONLY,
                                         'Use pre-trained text-based ML only.'),
                                        (VD_FORMULA_AND_FIELD_BASED_ML,
                                         'Start with formula, switch to fields-based ML when possible.'),
                                        (VD_FIELD_BASED_ML_ONLY, 'Use pre-trained field-based ML only.'),
                                        (VD_FIELD_BASED_WITH_UNSURE_ML_ONLY,
                                         'Use pre-trained field-based ML with "Unsure" category.'),
                                        (VD_PYTHON_CODED_FIELD, 'Use python class for value detection.'),
                                        (VD_FIELD_BASED_REGEXPS, 'Apply regexp field detectors to '
                                                                 'depends-on field values'),
                                        (VD_MLFLOW_MODEL, 'Use pre-trained mlflow model to find matching text units.')]

    value_detection_strategy = models.CharField(max_length=50,
                                                choices=VALUE_DETECTION_STRATEGY_CHOICES,
                                                default=VD_USE_REGEXPS_ONLY)

    vectorizer_stop_words = models.TextField(null=True, blank=True, help_text='''Stop words for vectorizers 
    user in field-based ML field detection. These stop words are excluded from going into the feature vector part 
    build based on this field. In addition to these words the standard sklearn "english" word list is used. 
    Format: each word on new line''')

    unsure_choice_value = models.CharField(max_length=256, blank=True, null=True,
                                           help_text='''Makes sense for machine learning 
    strategies with "Unsure" category. The strategy will return this value if probabilities of all other categories 
    appear lower than the specified threshold.''')

    unsure_thresholds_by_value = JSONField(encoder=ImprovedDjangoJSONEncoder, null=True, blank=True,
                                           help_text='''Makes sense for machine learning 
    strategies with "Unsure" category. The strategy will return concrete result (one of choice values) only if 
    the probability of the detected value is greater than this threshold. Otherwise the strategy returns None 
    or the choice value specified in "Unsure choice value" field. Format: { "value1": 0.9, "value2": 0.5, ...}.
     Default: ''' + str(DEFAULT_UNSURE_THRESHOLD))

    python_coded_field = models.CharField(max_length=100, null=True, blank=True)

    mlflow_model_uri = models.CharField(max_length=1024, null=True, blank=True, help_text='''MLFlow model URI 
    understandable by the MLFlow artifact downloading routines.''')

    mlflow_detect_on_document_level = models.BooleanField(null=False, blank=False, default=False,
                                                          help_text='''If true - whole 
    document text will be sent to the MLFlow model and the field value will be returned for the whole text with no
    annotations. If false - each text unit will be sent separately.''')

    classifier_init_script = models.TextField(null=True, blank=True)

    formula = models.TextField(null=True, blank=True)

    convert_decimals_to_floats_in_formula_args = models.BooleanField(null=False, blank=False, default=False,
                                                                     help_text='''Floating point field values 
    are represented in Python Decimal type to avoid rounding problems in machine numbers representations. 
    Use this checkbox for converting them to Python float type before calculating the formula. 
    Float: 0.1 + 0.2 = 0.30000000000000004. Decimal: 0.1 + 0.2 = 0.3.''')

    value_regexp = models.TextField(null=True, blank=True, help_text='''This regular expression is run on the sentence 
    found by a Field Detector and extracts a specific string value from a Text Unit. The first matching group is used if
     the regular expression returns multiple matching groups. This is only applicable to string fields.''')

    depends_on_fields = models.ManyToManyField('self', blank=True, related_name='affects_fields', symmetrical=False)

    confidence = models.CharField(max_length=100, choices=CONFIDENCE_CHOICES, default=None,
                                  blank=True, null=True)

    requires_text_annotations = models.BooleanField(default=True, null=False, blank=False)

    read_only = models.BooleanField(default=False, null=False, blank=False)

    default_value = JSONField(blank=True, null=True, encoder=ImprovedDjangoJSONEncoder, help_text='''When populated, this 
    default value is displayed in the user interface’s annotator sidebar for the associated field. If not populated, the
     Field Value remains empty by default. Please wrap entries with quotes, example: “landlord”. This is only applicable
      to Choice and Multichoice fields.''')

    # In case the type of the field requires selecting one of pre-defined values -
    # they should be stored \n-separated in the "choices" property
    choices = models.TextField(blank=True, null=True,
                               help_text='''Newline-separated choices. A choice cannot contain a comma.''')

    def admin_unit_details(self):  # Button for admin to get to API
        return format_html(u'<a href="#" onclick="return false;" class="button" '
                           u'id="id_admin_unit_selected">Unit Details</a>')

    admin_unit_details.allow_tags = True
    admin_unit_details.short_description = "Unit Details"

    allow_values_not_specified_in_choices = models.BooleanField(blank=False, null=False, default=False)

    # Used for quickly detecting a value if one of these regexps is matched.
    # Format:
    # { "regexp": "choice_value", "regexp": "choice_value", ..... }
    # For field-based field detecting (formulas/ML/field detectors):
    #   - strategies try to find any of these regexps
    stop_words = JSONField(blank=True, null=True, encoder=ImprovedDjangoJSONEncoder)

    metadata = CustomJSONField(blank=True, null=True, encoder=ImprovedDjangoJSONEncoder)

    training_finished = models.BooleanField(default=False)

    dirty = models.BooleanField(default=False)

    order = models.PositiveSmallIntegerField(default=0)

    trained_after_documents_number = models.PositiveIntegerField(default=settings.TRAINED_AFTER_DOCUMENTS_NUMBER,
                                                                 null=False, validators=[MinValueValidator(1)])

    hidden_always = models.BooleanField(default=False, null=False, blank=False)

    hide_until_python = models.TextField(null=True, blank=True)

    hide_until_js = models.TextField(null=True, blank=True)

    display_yes_no = models.BooleanField(default=False, null=False, blank=False, help_text='''Checking this box will 
    display “Yes” if Related Info text is found, and display “No” if no text is found.''')

    modified_date = models.DateTimeField(auto_now=True)

    created_date = models.DateTimeField(auto_now_add=True)

    objects = DocumentFieldManager()

    def make_unique_code(self, source=None):
        source = source or self.title
        code = re.sub(r'\W+', '_', source.lower()).strip('_')
        if DocumentField.objects.filter(code=code, document_type=self.document_type).exists():
            similar_codes = DocumentField.objects.filter(code__iregex=re.sub(r'(.+?)\d+$', r'\1\\d+', code), document_type=self.document_type)
            latest_index = max([int(re.sub(r'.+?(\d+)?$', r'\1', i) or 0)
                                for i in similar_codes.values_list('code', flat=True)])
            code_base = re.sub(r'_?\d+$', '', code)
            code = f'{code_base}_{latest_index + 1}'
        return code

    def is_detectable(self):
        return self.value_detection_strategy and self.value_detection_strategy != self.VD_DISABLED

    def get_depends_on_uids(self) -> QuerySet:
        return self.depends_on_fields.all().values_list('pk', flat=True)

    def get_depends_on_codes(self) -> QuerySet:
        return self.depends_on_fields.all().values_list('code', flat=True)

    class Meta:
        unique_together = (('code', 'document_type'), ('code', 'document_type', 'modified_by', 'modified_date'),)
        ordering = ('long_code',)
        indexes = [
            Index(fields=['dirty']),
            Index(fields=['training_finished']),
            Index(fields=['modified_date']),
            Index(fields=['text_unit_type']),
            Index(fields=['confidence']),
            Index(fields=['python_coded_field'])]
        permissions = (
            ('view_documentfield_stats', 'View document field stats'),
            ('clone_documentfield', 'Clone document field'),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._compiled_value_regexp = None

    def __str__(self):
        return self.long_code or self.code

    def __repr__(self):
        return "{1} (#{0})".format(self.pk, self.code)

    @classmethod
    def parse_choice_values(cls, choices: str) -> List[str]:
        if not choices:
            return list()
        return [choice.strip() for choice in choices.strip().splitlines()]

    def get_vectorizer_stop_words(self) -> List[str]:
        if not self.vectorizer_stop_words:
            return list()
        return [w.strip() for w in self.vectorizer_stop_words.strip().splitlines()]

    def get_choice_values(self) -> List[str]:
        return self.parse_choice_values(self.choices)

    def is_choice_value(self, possible_value):
        # update get_invalid_choice_values function if this logic will be changed
        return self.allow_values_not_specified_in_choices or possible_value in self.get_choice_values()

    def get_invalid_choice_annotations(self) -> 'Union[QuerySet, List[FieldAnnotation]]':
        if not self.allow_values_not_specified_in_choices:
            return FieldAnnotation.objects \
                .filter(field=self) \
                .exclude(value__in=self.get_choice_values())
        return FieldAnnotation.objects.none()

    def set_choice_values(self, choices: List[str]):
        self.choices = '\n'.join(choices) if choices else None

    def store_choice_value_if_not_present(self, new_choice: str):
        choices = set(self.get_choice_values())
        if new_choice not in choices:
            choices.add(new_choice)
            self.set_choice_values(sorted(choices))
            self.save()

    def can_retrain(self):
        return self.dirty \
               and not self.training_finished \
               and self.modified_date < DocumentFieldManager.get_user_delay()

    def save(self, *args, **kwargs):
        self.hide_until_python = self.hide_until_python.strip() if self.hide_until_python else ''
        self.hide_until_js = jiphy.to.javascript(self.hide_until_python) if self.hide_until_python else ''
        with transaction.atomic():
            for values in DocumentField.objects.filter(pk=self.pk).values('document_type__pk', 'type'):
                if values['document_type__pk'] != self.document_type.pk or values['type'] != self.type:
                    # DocumentFieldValue.objects.filter(field=self).delete()
                    FieldAnnotation.objects.filter(field=self).delete()
                    break
            document_type = None
            if self.document_type is not None:
                document_type = DocumentType.objects.get(pk=self.document_type.pk)
            self.long_code = self.get_long_code(self, document_type)
            super().save(*args, **kwargs)

    @classmethod
    def get_long_code(cls, field, document_type=None):
        document_type = field.document_type if document_type is None else document_type
        return '{0}: {1}'.format(document_type.code, field.code) if document_type is not None else field.code

    @classmethod
    def compile_value_regexp(cls, value_regexp: str):
        return re.compile(value_regexp)

    def get_compiled_value_regexp(self):
        if not self._compiled_value_regexp and self.value_regexp and self.value_regexp.strip():
            try:
                self._compiled_value_regexp = self.compile_value_regexp(self.value_regexp)
            except Exception as exc:
                msg = 'Unable to compile value regexp for field {0}. Regexp:\n{1}\nReason: {2}'
                raise SyntaxError(msg.format(self.code, self.value_regexp, exc))
        return self._compiled_value_regexp


@receiver(models.signals.pre_delete, sender=DocumentField)
def remove_document_field_perms(sender, instance, **kwargs):
    ctype = get_content_type(DocumentField)
    CustomUserObjectPermission.objects.filter(content_type=ctype, object_pk=instance.pk).delete()


@receiver(models.signals.post_save, sender=DocumentField)
def save_document_field(sender, instance, created, **kwargs):
    sender.save_timestamp(sender, instance, created, save_document_field)
    if created and instance.created_by is not None:
        # grant_document_field_perms
        for perm_name in document_type_manager_permissions['document_field']:
            assign_perm(perm_name, instance.created_by, instance)


class DocumentType(TimeStampedModel):
    """
    DocumentType describes custom document type.
    """

    DOCUMENT_EDITOR_CHOICES = ['save_by_field', 'save_all_fields_at_once', 'no_text']
    DOCUMENT_EDITOR_CHOICES = [(i, i) for i in DOCUMENT_EDITOR_CHOICES]
    GENERIC_TYPE_CODE = constants.DOCUMENT_TYPE_CODE_GENERIC_DOCUMENT

    # Make pk field unique
    uid = StringUUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Short name for field.
    code = models.CharField(max_length=50, db_index=True, unique=True,
                            help_text='''Field codes must be lowercase, should start with a Latin letter, and contain 
only Latin letters, digits, and underscores.''')

    # Verbose name for field.
    title = models.CharField(max_length=100, db_index=True)

    # Aliases of field codes for document import purposes.
    # Json format: { "alias1": "field_code1", "alias2": "field_code2", ...}
    field_code_aliases = JSONField(blank=True, null=True, encoder=ImprovedDjangoJSONEncoder)

    # lesser set of fields to filter/sort on Document list page
    search_fields = models.ManyToManyField(
        DocumentField, related_name='search_field_document_type', blank=True)

    editor_type = models.CharField(max_length=100, blank=True, null=True, choices=DOCUMENT_EDITOR_CHOICES)

    metadata = CustomJSONField(blank=True, null=True, encoder=ImprovedDjangoJSONEncoder)

    managers = models.ManyToManyField(User, related_name='document_type_managers', blank=True)

    class Meta:
        unique_together = (('code', 'modified_by', 'modified_date'),)
        ordering = ('code', 'modified_by', 'modified_date')
        permissions = (
            ('view_documenttype_stats', 'View document type stats'),
            ('clone_documenttype', 'Clone document type'),
            ('import_documenttype', 'Import document type'),
            ('export_documenttype', 'Export document type'),
        )

    def __str__(self):
        return self.code

    def __repr__(self):
        return "{1} (#{0})".format(self.pk, self.code)

    @classmethod
    def generic(cls):
        obj, _ = cls.objects.get_or_create(
            uid=constants.DOCUMENT_TYPE_PK_GENERIC_DOCUMENT,
            defaults={
                'uid': constants.DOCUMENT_TYPE_PK_GENERIC_DOCUMENT,
                'code': DocumentType.GENERIC_TYPE_CODE,
                'title': 'Generic Document'})
        # UID for generic doc type is hardcoded here to prevent problems if
        # uploading full config dump from one host where it has one uid to another host
        # where generic doc type possibly has another uid.
        return obj

    @classmethod
    def generic_pk(cls):
        return constants.DOCUMENT_TYPE_PK_GENERIC_DOCUMENT

    def is_generic(self):
        return self.code == DocumentType.GENERIC_TYPE_CODE

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            DocumentField.objects \
                .filter(document_type=self) \
                .update(long_code=Concat(Value(self.code + ': '), F('code')))


@receiver(models.signals.post_save, sender=DocumentType)
def save_document_type(sender, instance, created, **kwargs):
    sender.save_timestamp(sender, instance, created, save_document_type)


@receiver(models.signals.m2m_changed, sender=DocumentType.managers.through)
def grant_manager_perms(instance, action, pk_set, **kwargs):
    if action in ['post_add', 'post_remove']:
        users = User.objects.filter(pk__in=pk_set)
        method = assign_perm if action == 'post_add' else remove_perm
        with transaction.atomic():
            for perm_name in document_type_manager_permissions['document_type']:
                method(perm_name, users, instance)
            for field in instance.fields.only('pk'):
                for perm_name in document_type_manager_permissions['document_field']:
                    method(perm_name, users, field)


@receiver(models.signals.pre_delete, sender=DocumentType)
def remove_document_type_perms(sender, instance, **kwargs):
    ctype = get_content_type(DocumentField)
    field_ids = list(instance.fields.values_list('pk', flat=True))
    CustomUserObjectPermission.objects.filter(content_type=ctype, object_pk__in=field_ids).delete()
    ctype = get_content_type(DocumentType)
    CustomUserObjectPermission.objects.filter(content_type=ctype, object_pk=instance.pk).delete()


class DocumentQuerySet(models.QuerySet):

    def update(self, **kwargs):
        from apps.document.signals import documents_pre_update
        documents_pre_update.send(sender=self.model, queryset=self, **kwargs)
        return super().update(**kwargs)


class DocumentManager(models.Manager):
    use_in_migrations = True

    def get_queryset(self):
        qs = super(DocumentManager, self).get_queryset().filter(delete_pending=False)
        qs.use_in_migrations = True
        return qs

    def active(self):
        return self.filter(status__is_active=True, delete_pending=False)


class DocumentObjectsManager(DocumentManager.from_queryset(DocumentQuerySet)):
    pass


class DocumentAllObjectsManager(models.Manager.from_queryset(DocumentQuerySet)):
    pass


class Document(models.Model):
    """Document object model

    Document is the root class for the `document` app model.  Each :model:`document.Document`
    can contain zero or more :model:`document.TextUnit`, as well as its own set of fixed and
    flexible metadata about the document per se.
    """
    LOG_FIELD_DOC_ID = 'log_document_id'
    LOG_FIELD_DOC_NAME = 'log_document_name'

    class DocumentMetadataKey:
        KEY_SECTIONS = 'sections'
        KEY_DEFINITIONS = 'definitions'
        KEY_TABLES = 'tables'
        KEY_UPLOAD_STATUS = 'upload_status'
        KEY_PARSING_STATISTICS = 'parsing_statistics'

    # Name of document, as presented in most views and exports.
    name = models.CharField(max_length=1024, db_index=True, null=True)

    # Document description, as provided by metadata or user-entered.
    description = models.TextField(null=True, db_index=True)

    # Language,  as detected upon ingestion and stored via ISO code
    language = models.CharField(max_length=3, blank=True, null=True, db_index=True)

    # Document source name, e.g., Acme File System or Acme Google Mail
    source = models.CharField(max_length=1024, db_index=True, null=True)

    # Document source type, e.g., File System, Email, Salesforce
    source_type = models.CharField(max_length=100, db_index=True, blank=True, null=True)

    # If relevant, URI/path within document source
    source_path = models.CharField(max_length=1024, db_index=True, null=True)

    # If relevant, URI/path within alternative document source
    alt_source_path = models.CharField(max_length=1024, db_index=True, null=True)

    # source file size, bytes
    file_size = models.PositiveIntegerField(default=0, null=False)

    # Pre-calculated length statistics for paragraph and sentence
    paragraphs = models.PositiveIntegerField(default=0, null=False)
    sentences = models.PositiveIntegerField(default=0, null=False)

    # Document title
    title = models.CharField(max_length=1024, db_index=True, blank=True, null=True)

    # Document history
    history = HistoricalRecords()

    # selected for Delete admin task
    delete_pending = models.BooleanField(default=False, null=False)

    # Document's original path in end user filesystem
    folder = models.CharField(max_length=1024, db_index=True, blank=True, null=True)

    # apply custom objects manager
    objects = DocumentObjectsManager()

    ql_objects = DocumentAllObjectsManager()

    all_objects = models.Manager.from_queryset(DocumentQuerySet)()

    document_type = models.ForeignKey(DocumentType, blank=True, null=True, db_index=True, on_delete=CASCADE)

    project = models.ForeignKey('project.Project', blank=True, null=True, db_index=True, on_delete=CASCADE)

    status = models.ForeignKey('common.ReviewStatus', default=get_default_status,
                               blank=True, null=True, on_delete=CASCADE)

    assignee = models.ForeignKey(User, blank=True, null=True, db_index=True, on_delete=CASCADE)

    assign_date = models.DateTimeField(blank=True, null=True)

    upload_session = models.ForeignKey('project.UploadSession', blank=True, null=True,
                                       db_index=True, on_delete=CASCADE)

    processed = models.BooleanField(default=False, null=False)

    document_class = models.CharField(max_length=256, db_index=True, blank=True, null=True)

    fields_dirty = models.DateTimeField(db_index=True, null=True)

    ocr_rating = models.FloatField(blank=True, db_index=True, null=True)

    class Meta:
        ordering = ('name',)
        # commented out it as it doesn't allow to upload
        # the same documents (having the same source) into two different projects
        # unique_together = ('name', 'source',)
        permissions = (
            ('change_document_field_values', 'Change document field values'),
            ('change_status', 'Change document status'),
        )

    def __str__(self):
        return self.name

    def __repr__(self):
        return "{1} ({0})" \
            .format(self.document_type.title, self.name)

    @property
    def full_text(self):
        """
        Just an alias
        """
        try:
            return self.documenttext.full_text
        except DocumentText.DoesNotExist:
            pass

    @property
    def text(self):
        """
        Just an alias
        """
        return self.full_text

    @property
    def metadata(self):
        """
        Just an alias
        """
        try:
            return self.documentmetadata.metadata
        except DocumentMetadata.DoesNotExist:
            pass

    @property
    def available_assignees(self):
        return self.project.available_assignees

    def set_language_from_text_units(self):
        langs = self.textunit_set \
            .filter(unit_type='paragraph') \
            .values('language') \
            .order_by() \
            .annotate(count=Count('pk'))
        if langs:
            lang = sorted(langs, key=lambda i: -i['count'])[0]['language']
            self.language = lang
            self.save()

    def is_completed(self):
        return not self.status.is_active

    def is_reviewed(self):
        return not self.status.group.is_active

    def cluster_id(self):
        if not self.document_type.is_generic():
            return None
        return self.documentcluster_set.order_by('-pk').values_list('pk', flat=True).first()

    def get_field_by_code(self, field_code: str) -> Any:
        """
        Get document's attribute (like name, assignee etc) by name or
        get document's attribute attribute by name as "attr_parent.attr_child.attr_grandchild..."
        See possible codes in constants.py, like DOCUMENT_FIELD_CODE_NAME
        :param field_code: code like "status.name"
        :return: field value (status name for this example)
        """
        fval, f_exists = self.try_get_field_by_code(field_code)
        if not f_exists:
            raise RuntimeError(f'get_field_by_code("{field_code}") - attribute "{field_code}" was not found')
        return fval

    def try_get_field_by_code(self, field_code: str) -> Tuple[Any, bool]:
        """
        Get document's attribute (like name, assignee etc) by name or
        get document's attribute attribute by name as "attr_parent.attr_child.attr_grandchild..."
        See possible codes in constants.py, like DOCUMENT_FIELD_CODE_NAME
        :param field_code: code like "status.name"
        :return: (field value (status name for this example); flag indicating such field exists)
        """
        fields = field_code.split('.')
        val = self
        for field in fields:
            if not hasattr(val, field):
                return None, False
            val = getattr(val, field)
            if callable(val):
                val = val()
            if val is None:
                break
        return val, True

    @classmethod
    def reset_status_from_annotations(cls, ann_status, project=None, document_ids=None):
        """
        Reset Document's status if all its annotations are accepted or rejected
        OR if a Document status is Awaiting_QA but some annotation is unset from accepted or rejected
        :param ann_status: ReviewStatus instance
        :param project: Project instance
        :param document_ids: Document ids
        :return:
        """
        from apps.common.models import ReviewStatus
        from apps.rawdb.field_value_tables import cache_document_fields, ProcessLogger

        documents_to_update_pks = []
        # TODO: do not hardcode status code
        awaiting_qa_status = ReviewStatus.objects.get(code='awaiting_qa')
        completed_status = ReviewStatus.objects.get(code='completed')

        document_qs = Document.objects
        if project is not None:
            document_qs = document_qs.filter(project=project)
        elif document_ids is not None:
            document_qs = document_qs.filter(id__in=document_ids)
        else:
            raise NotImplementedError('Provide either project or document.')

        # If all clauses reviewed, set document status to "Awaiting QA"
        if ann_status.is_accepted or ann_status.is_rejected:
            documents_to_update = document_qs \
                .exclude(status__in=[awaiting_qa_status, completed_status]) \
                .exclude(Q(annotations_matches__status__is_accepted=False) &
                         Q(annotations_matches__status__is_rejected=False)) \
                .distinct()
            documents_to_update_pks += list(documents_to_update.values_list('pk', flat=True))
            documents_to_update.update(status=awaiting_qa_status)

        # If some clauses are unset from reviewed, set document status to "In Review"
        else:
            in_review_status = ReviewStatus.objects.get(code='in_review')
            documents_to_update = document_qs \
                .filter(status=awaiting_qa_status) \
                .filter(Q(annotations_matches__status__is_accepted=False) &
                        Q(annotations_matches__status__is_rejected=False)) \
                .distinct()
            documents_to_update_pks += list(documents_to_update.values_list('pk', flat=True))
            documents_to_update.update(status=in_review_status)

        for document in Document.objects.filter(pk__in=documents_to_update_pks):
            cache_document_fields(ProcessLogger(),
                                  document,
                                  cache_system_fields=['status'],
                                  cache_generic_fields=False,
                                  cache_user_fields=False)


@receiver(models.signals.post_delete, sender=Document)
def full_delete(sender, instance, **kwargs):
    # automatically removes Document, TextUnits, ThingUsages
    from apps.document.utils import cleanup_document_relations
    # remove Document perms in cleanup_document_relations as well
    cleanup_document_relations(instance)


@receiver(models.signals.pre_save, sender=Document)
def update_pernissions(sender, instance, **kwargs):
    # change perms for assignees
    if instance.pk:
        db_instance = Document.objects.get(pk=instance.pk)
        if instance.assignee_id != db_instance.assignee_id:
            from apps.users.permissions import document_permissions, remove_perm
            if db_instance.assignee is not None:
                for perm_name in document_permissions:
                    remove_perm(perm_name, db_instance.assignee, instance)
            if instance.assignee is not None:
                for perm_name in document_permissions:
                    assign_perm(perm_name, instance.assignee, instance)


class DocumentText(models.Model):
    """DocumentText object model"""

    # Document FK
    document = models.OneToOneField(Document, db_index=True, on_delete=CASCADE)

    # Full document text
    full_text = models.TextField(null=True)

    @property
    def text(self):
        """
        Just an alias
        """
        return self.full_text


class DocumentMetadata(models.Model):
    # Document FK
    document = models.OneToOneField(Document, db_index=True, on_delete=CASCADE)

    # Document metadata from original file
    metadata = JSONField(blank=True, encoder=ImprovedDjangoJSONEncoder)


class DocumentTag(models.Model):
    """DocumentTag object model

    DocumentTag is a flexible class for applying labels or tags to a :model:`document.Document`.
    Each Document can have zero or more DocumentTag records, which can be subsequently used for
    unsupervised task accuracy assessment, semi-supervised tasks, and supervised tasks, as well
    as reporting.
    """

    document = models.ForeignKey(Document, db_index=True, on_delete=CASCADE)
    tag = models.CharField(max_length=1024, db_index=True)
    timestamp = models.DateTimeField(default=now, db_index=True)
    user = models.ForeignKey(User, db_index=True, null=True, on_delete=CASCADE)

    class Meta:
        unique_together = (("document", "tag"),)
        ordering = ('document', 'tag', 'timestamp')

    def __str__(self):
        return "DocumentTag (document={0}, tag={1})" \
            .format(self.document.id, self.tag)

    def __repr__(self):
        return "DocumentTag (id={0})".format(self.id)


class DocumentProperty(TimeStampedModel):
    """DocumentProperty object model

    DocumentProperty is a flexible class for creating key-value properties for a
    :model:`document.Document`.  Each Document can have zero or more DocumentProperty records,
    which may be used either at document ingestion to store metadata or subsequently to store
    any information that may be relevant.

    Unlike DocumentTag and DocumentClassification objects, DocumentProperty objects are not
    used in user-trained algorithm development.

    DocumentProperty objects can be used to cluster documents.
    """

    # Document
    document = models.ForeignKey(Document, db_index=True, on_delete=CASCADE)

    # Key - string with maximum length 1024
    key = models.CharField(max_length=1024, db_index=True)

    # Value - string with maximum length 1024
    value = models.TextField()

    class Meta:
        ordering = ('document', 'key')
        verbose_name_plural = 'Document Properties'
        indexes = [Index(fields=['document', 'key'])]

    def __str__(self):
        return "DocumentProperty (document={0}, key={1}, value={2})" \
            .format(self.document, self.key, self.value)

    def __repr__(self):
        return "DocumentProperty (document={0}, key={1})" \
            .format(self.document.id, self.key)


class DocumentPage(models.Model):
    document = models.ForeignKey(Document, db_index=True, on_delete=CASCADE)

    number = models.IntegerField(null=False, blank=False)

    location_start = models.IntegerField(null=False, blank=False)

    location_end = models.IntegerField(null=False, blank=False)

    class Meta:
        ordering = ('document', 'number')
        verbose_name_plural = 'Document Page'
        indexes = [Index(fields=['document', 'number'])]

    def __repr__(self):
        return f'Page #{self.number} (document={self.document_id}, location={self.location_start})'

    def __str__(self):
        return f'Page #{self.number}, {self.location_start}: {self.location_end})'


@receiver(models.signals.post_save, sender=DocumentProperty)
def save_document_property(sender, instance, created, **kwargs):
    sender.save_timestamp(sender, instance, created, save_document_property)


class DocumentRelation(models.Model):
    """DocumentRelation object model

    DocumentRelation is a flexible class for linking two :model:`document.Document` objects.
    These records can be used to define a many-to-many network or graph, where each relationship
    or "edge" can have a specific `relation_type`.

    For example, Documents A and B might have relation "amendment" while Documents A
    and C might have relation "previous_negotiated_copy" or "executed".
    """

    # "Left" or "source" document
    document_a = models.ForeignKey(Document, db_index=True, related_name="document_a_set", on_delete=CASCADE)

    # "Right" or "target" document
    document_b = models.ForeignKey(Document, db_index=True, related_name="document_b_set", on_delete=CASCADE)

    # Relation type, e.g., amendment or negotiated_copy
    relation_type = models.CharField(max_length=128)

    def __str__(self):
        return "DocumentRelation (document_a={0}, document_b={1}, relation_type={2})" \
            .format(self.document_a, self.document_b, self.relation_type)

    def __repr__(self):
        return "DocumentRelation (document_a={0}, document_b={1}, relation_type={2})" \
            .format(self.document_a.id, self.document_b.id, self.relation_type)


class DocumentNote(models.Model):
    """DocumentNote object model

    DocumentNote is a class that allows users to store rich text notes, much like Word
    or HTML documents.  Each Document can contain zero or more of these notes, which are
    tracked to user and timestamp.

    Since each DocumentNote is versioned, DocumentNote objects have a `HistoricalRecords`
    manager embedded.
    """

    # Document
    document = models.ForeignKey(Document, db_index=True, on_delete=CASCADE)

    # Document Field Value
    # TODO: FieldValue or FieldValueAnnotation ?
    field_value = models.ForeignKey('document.FieldValue', blank=True,
                                    null=True, db_index=True, on_delete=CASCADE)

    # Document Field Value
    field = models.ForeignKey('document.DocumentField', blank=True, null=True, db_index=True, on_delete=CASCADE)

    user = models.ForeignKey(User, db_index=True, null=True, on_delete=SET_NULL, default=None)

    username = models.CharField(db_index=False, null=True, max_length=200, default=None)

    # Document timestamp
    timestamp = models.DateTimeField(default=now, db_index=True)

    # Note body
    note = RichTextField()

    location_start = models.IntegerField(null=True, blank=True)

    location_end = models.IntegerField(null=True, blank=True)

    # Note history
    history = HistoricalRecords()

    class Meta:
        ordering = ('document__name', 'timestamp')

    def __str__(self):
        return "DocumentNote (document={0}, note={1}, timestamp={2})" \
            .format(self.document, len(self.note), self.timestamp)

    def __repr__(self):
        return "DocumentNote (document={0}, note={1})" \
            .format(self.document.id, self.id)

    def update_document_cache(self):
        user = getattr(self, 'request_user', self.history.last().history_user if self.history.exists() else None)
        from apps.document.tasks import plan_process_document_changed
        from apps.document.constants import DocumentSystemField

        plan_process_document_changed(doc_id=self.document.pk,
                                      system_fields_changed=[DocumentSystemField.notes.value],
                                      generic_fields_changed=False,
                                      user_fields_changed=False,
                                      changed_by_user_id=user.pk if user else None
                                      )


@receiver(models.signals.post_save, sender=DocumentNote)
def save_document_note(sender, instance, **kwargs):
    # update document cache
    instance.update_document_cache()


@receiver(models.signals.post_delete, sender=DocumentNote)
def delete_document_note(sender, instance, **kwargs):
    # delete history
    instance.history.all().delete()
    # update document cache
    instance.update_document_cache()


class TextUnit(models.Model):
    """TextUnit object model

    TextUnit is the primary container of actual text.  Each Document, upon ingestion, is
    parsed and segmented into zero or more TextUnit records.  Depending on segmentation
    and use case, TextUnits may represent sentences, paragraphs, or some larger unit
    of text.
    """
    UNIT_TYPE_SENTENCE = 'sentence'

    UNIT_TYPE_PARAGRAPH = 'paragraph'

    # Document
    document = models.ForeignKey(Document, db_index=True, on_delete=CASCADE)

    # Project reference for better SQL performance
    project = models.ForeignKey('project.Project', blank=True,
                                null=True, db_index=True, on_delete=CASCADE)

    # Text unit type, e.g., sentence, paragraph, section
    unit_type = models.CharField(max_length=128)

    # Language,  as detected upon ingestion and stored via ISO code
    language = models.CharField(max_length=3)

    location_start = models.IntegerField(null=True, blank=True)

    location_end = models.IntegerField(null=True, blank=True)

    # Cryptographic hash of raw text for identical de-duplication
    text_hash = models.CharField(max_length=1024, null=True)

    objects = models.Manager()

    ql_objects = DjangoQLQuerySet.as_manager()

    class Meta:
        indexes = [Index(fields=['text_hash']),
                   Index(fields=['unit_type']),
                   Index(fields=['document', 'unit_type']),
                   Index(fields=['language'])]

    def __str__(self):
        return "TextUnit (id={4}, document={0}, unit_type={1}, language={2}, len(text)={3})" \
            .format(self.document, self.unit_type, self.language, len(self.text), self.id, )

    def __repr__(self):
        return "TextUnit (id={0})".format(self.id)

    def is_sentence(self) -> bool:
        return self.unit_type == 'sentence'

    @property
    def text(self):
        """
        Just an alias
        """
        try:
            return self.textunittext.text
        except TextUnitText.DoesNotExist:
            pass


class TextUnitText(models.Model):
    """TextUnitText object model"""

    # enable full-text-search for "text" column in "contains" and "icontains" queries
    full_text_search_fields = ['text']

    text_unit = models.OneToOneField(TextUnit, db_index=True, on_delete=CASCADE)

    text = models.TextField(max_length=16384, null=True)

    text_tsvector = SearchVectorField(null=True)

    def __str__(self):
        return "TextUnitText (id={}, text_unit={})".format(self.pk, str(self.text_unit))

    class Meta:
        indexes = [GinIndex(fields=['text'],
                            name='idx_dtut_text_gin',
                            opclasses=['gin_trgm_ops']),
                   GinIndex(fields=['text_tsvector'],
                            name='idx_dtut_text_tsvector_gin')]


class TextUnitTag(models.Model):
    """TextUnitTag object model

    TextUnitTag is a flexible class for applying labels or tags to a :model:`document.TextUnit`.
    Each TextUnit can have zero or more TextUnitTag records, which can be subsequently used for
    unsupervised task accuracy assessment, semi-supervised tasks, and supervised tasks, as well
    as reporting.
    """

    # Text unit
    text_unit = models.ForeignKey(TextUnit, db_index=True, on_delete=CASCADE)

    # Tag
    tag = models.CharField(max_length=1024, db_index=True)

    # Timestamp
    timestamp = models.DateTimeField(default=now, db_index=True)

    # User
    user = models.ForeignKey(User, db_index=True, null=True, on_delete=CASCADE)

    class Meta:
        unique_together = (("text_unit", "tag"),)
        ordering = ('text_unit', 'tag', 'timestamp')

    def __str__(self):
        return "TextUnitTag (text_unit={0}, tag={1})" \
            .format(self.text_unit, self.tag)

    def __repr__(self):
        return "TextUnitTag (id={0})".format(self.id)


class TextUnitProperty(TimeStampedModel):
    """TextUnitProperty object model

    TextUnitProperty is a flexible class for creating key-value properties for a
    :model:`document.TextUnit`.  Each TextUnit can have zero or more TextUnitProperty records,
    which may be used either at document ingestion to store metadata, such as Track Changes or
    annotations, or subsequently to store relevant information.
    """
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, related_name="created_%(class)s_set", null=True, blank=True, db_index=False, on_delete=CASCADE)
    modified_by = models.ForeignKey(
        User, related_name="modified_%(class)s_set", null=True, blank=True, db_index=False, on_delete=CASCADE)

    # Text unit
    text_unit = models.ForeignKey(TextUnit, db_index=True, on_delete=CASCADE)

    # Key - string with maximum length 1024
    key = models.CharField(max_length=1024, db_index=True)

    # Value - string with maximum length 1024
    value = models.CharField(max_length=1024, db_index=True)

    class Meta:
        ordering = ('text_unit', 'key', 'value')
        verbose_name_plural = 'Text Unit Properties'
        indexes = [Index(fields=['text_unit', 'key', 'value'])]

    def __str__(self):
        return "TextUnitProperty (text_unit_pk={0}, key={1}, value={2})" \
            .format(self.text_unit.pk, self.key, self.value)

    def __repr__(self):
        return "TextUnitProperty (id={0})".format(self.id)


@receiver(models.signals.post_save, sender=TextUnitProperty)
def save_text_unit_property(sender, instance, created, **kwargs):
    sender.save_timestamp(sender, instance, created, save_text_unit_property)


class TextUnitRelation(models.Model):
    """DocumentRelation object model

    DocumentRelation is a flexible class for linking two :model:`document.Document` objects.
    These records can be used to define a many-to-many network or graph, where each relationship
    or "edge" can have a specific `relation_type`.

    For example, Documents A and B might have relation "amendment" while Documents A
    and C might have relation "previous_negotiated_copy" or "executed".
    """

    # Left or "source" text unit
    text_unit_a = models.ForeignKey(TextUnit, db_index=True,
                                    related_name="text_unit_a_set", on_delete=CASCADE)

    # Right or "target" text unit
    text_unit_b = models.ForeignKey(TextUnit, db_index=True,
                                    related_name="text_unit_b_set", on_delete=CASCADE)

    # Relation type
    relation_type = models.CharField(max_length=128)

    def __str__(self):
        return "TextUnitRelation (text_unit_a={0}, text_unit_b={1}, relation_type={2})" \
            .format(self.document_a, self.document_b, self.relation_type)

    def __repr__(self):
        return "TextUnitRelation (text_unit_a={0}, text_unit_b={1}, relation_type={2})" \
            .format(self.text_unit_a.id, self.text_unit_b.id, self.relation_type)


class TextUnitNote(models.Model):
    """TextUnitNote object model

    TextUnitNote is a class that allows users to store rich text notes, much like Word
    or HTML documents.  Each TextUnit can contain zero or more of these notes, which are
    tracked to user and timestamp.

    Since each TextUnit is versioned, TextUnit objects have a `HistoricalRecords`
    manager embedded.
    """
    # Text unit
    text_unit = models.ForeignKey(TextUnit, db_index=True, on_delete=CASCADE)

    # Timestamp
    timestamp = models.DateTimeField(default=now, db_index=True)

    user = models.ForeignKey(User, db_index=True, null=True, on_delete=SET_NULL, default=None)

    username = models.CharField(db_index=False, null=True, max_length=200, default=None)

    # Note
    note = RichTextField()

    # Historical manager
    history = HistoricalRecords()

    class Meta:
        ordering = ('text_unit', 'timestamp')

    def __str__(self):
        return "TextUnitNote (text_unit={0}, note={1}, timestamp={2})" \
            .format(self.text_unit, len(self.note), self.timestamp)

    def __repr__(self):
        return "TextUnitNote (id={0})".format(self.id)


@receiver(models.signals.post_delete, sender=TextUnitNote)
def delete_text_unit_note(sender, instance, **kwargs):
    # delete history
    instance.history.all().delete()


class ExternalFieldValue(TimeStampedModel):
    """ExternalFieldValue  object model

    ExternalFieldValue contains external field values to train classifier.
    Transfer container for Training Data For Document Field Values.
    """

    # DocumentField uid
    field_id = models.CharField(max_length=36)

    # Datastore for extracted value
    value = JSONField(blank=True, null=True, encoder=ImprovedDjangoJSONEncoder)

    # source text
    text_unit_text = models.TextField()

    # Extraction hint detected at the moment of storing - used for further model training
    extraction_hint = models.CharField(max_length=30, choices=EXTRACTION_HINT_CHOICES,
                                       default=EXTRACTION_HINT_CHOICES[0][0], db_index=True,
                                       blank=True, null=True)

    def __str__(self):
        return "{0}.{1} = {2}" \
            .format(self.type_id, self.field_id, str(self.value)[:40])

    def __repr__(self):
        return "{0}.{1} = {2} (#{3})" \
            .format(self.type_id, self.field_id, str(self.value)[:40], self.id)


class TextParts(Enum):
    FULL = "FULL"
    BEFORE_REGEXP = "BEFORE_REGEXP"
    AFTER_REGEXP = "AFTER_REGEXP"
    INSIDE_REGEXP = "INSIDE_REGEXP"


class DocumentFieldDetector(models.Model):
    DEF_RE_FLAGS = re.DOTALL

    TEXT_PARTS = (
        (TextParts.FULL.value, 'Whole text'),
        (TextParts.BEFORE_REGEXP.value, 'Before matching substring'),
        (TextParts.AFTER_REGEXP.value, 'After matching substring'),
        (TextParts.INSIDE_REGEXP.value, 'Inside matching substring'),
    )

    uid = StringUUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    field = models.ForeignKey(DocumentField, blank=False, null=False,
                              related_name='field_detectors', on_delete=CASCADE)

    CAT_SIMPLE_CONFIG = 'simple_config'

    CATEGORY_CHOICES = [(CAT_SIMPLE_CONFIG, 'Simple field detectors loaded and managed via '
                                            '"Documents: Import CSV Field Detection Config" admin task.')]

    # Field detector category which can be used for finding some special field detectors
    # from the set of all available.
    category = models.CharField(max_length=64, db_index=True, blank=True, null=True, choices=CATEGORY_CHOICES,
                                help_text='''Field detector category used for technical needs e.g. for determining 
which field detectors were created automatically during import process.''')

    exclude_regexps = models.TextField(blank=True, null=True,
                                       help_text='''Enter regular expressions, each on a new line, for text patterns 
you want EXCLUDED. The Field Detector will attempt to skip any Text Unit that contains any of the patterns written 
here, and will move on to the next Text Unit. Avoid using “.*” and similar unlimited multipliers, as they can crash 
or slow ContraxSuite. Use bounded multipliers for variable length matching, like “.{0,100}” or similar. Note that 
Exclude regexps are checked before Definition words and Include regexps. If a Field Detector has Exclude regexps, but 
no Definition words or Include regexps, it will not extract any data.''')

    definition_words = models.TextField(blank=True, null=True,
                                        help_text='''Enter words or phrases, each on a new line, that must be present 
in the Text Unit. These words must be in the Definitions List. If ContraxSuite fails to recognize these words as 
definitions, then the Field Detector skips and moves to the next Text Unit. If there are Include regexps, then the 
Field Detector checks against those requirements. The Field Detector marks the entire Text Unit as a match. Note that 
the Field Detector checks for definition words after filtering using the Exclude regexps.''')

    include_regexps = models.TextField(blank=True, null=True, help_text='''Enter regular expressions, each on a new 
line, for text patterns you want INCLUDED. The Field Detector will attempt to match each of these regular expressions 
within a given Text Unit. Avoid using “.*” and similar unlimited multipliers, as they can crash or slow ContraxSuite. 
Use bounded multipliers for variable length matching, like “.{0,100}” or similar. Note that Include regexps are checked 
after both Exclude regexps and Definition words.''')

    regexps_pre_process_lower = models.BooleanField(
        blank=False, null=False, default=True,
        verbose_name='Make search case-insensitive',
        help_text='''Set 'ignore case' flag for both 'Include regexps' and 'Exclude regexps' options.''')

    # For choice fields - the value which should be set if a sentence matches this detector
    detected_value = models.CharField(max_length=256, blank=True, null=True, help_text='''The string value written here 
will be assigned to the field if the Field Detector positively matches a Text Unit. This is only applicable to Choice, 
Multichoice, and String fields, as their respective Field Detectors do not extract and display values from the source 
text.''')

    # Number of value to extract in case of multiple values
    extraction_hint = models.CharField(max_length=30, choices=EXTRACTION_HINT_CHOICES,
                                       default=EXTRACTION_HINT_CHOICES[0][0], db_index=True,
                                       blank=True, null=True, help_text='''Provide additional instruction on which 
specific values should be prioritized for extraction, when multiple values of the same type 
(e.g., Company, Person, Geography) are found within the relevant detected Text Unit.''')

    text_part = models.CharField(max_length=30, choices=TEXT_PARTS, default=TEXT_PARTS[0][0], db_index=True,
                                 blank=False, null=False, help_text='''Defines which part of the matched Text Unit 
should be passed to the extraction function. Example: In the string "2019-01-23 is the start date and 2019-01-24 is the 
end date," if text part = "Before matching substring" and Include regexp is "is.{0,100}start" then "2019-01-23" will be 
parsed correctly as the start date.''')

    @property
    def include_matchers(self):
        return self._include_matchers

    @property
    def exclude_matchers(self):
        return self._exclude_matchers

    @property
    def detector_definition_words(self):
        return self._definition_words

    # Validator. If field is not of an ordinal type and TAKE_MIN/MAX are selected, throw error
    def clean_fields(self, exclude=('uid', 'field', 'document_type', 'exclude_regexps',
                                    'include_regexps', 'regexps_pre_process_lower',
                                    'detected_value')):
        # TODO: Put this validation to the proper place (forms?)
        from apps.document.field_types import TypedField
        try:
            typed_field = TypedField.by(self.field)
        except:
            raise ValidationError('field')

        if not typed_field.ordinal \
                and self.extraction_hint in ORDINAL_EXTRACTION_HINTS:
            raise ValidationError({'field': ['Cannot take min or max of <Field> because its type is not '
                                             'amount, money, int, float, date, or duration. Please select '
                                             'TAKE_FIRST, TAKE_SECOND, or TAKE_THIRD, or change the field '
                                             'type.']})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._include_matchers = None
        self._exclude_matchers = None
        self._definition_words = None

    def compile_regexps_string(self, regexps: str) -> list:
        matchers = []
        if regexps:
            for r in regexps.split('\n'):
                r = r.strip()
                if r:
                    flags = self.DEF_RE_FLAGS
                    if self.regexps_pre_process_lower:
                        flags |= re.IGNORECASE
                    matchers.append(re.compile(r, flags))
        return matchers

    def compile_regexps(self):

        if self.definition_words:
            dw = []
            for w in self.definition_words.split('\n'):
                w = w.strip()
                if w:
                    dw.append(self._clean_def_words(w))
            self._definition_words = dw or None

        try:
            self._include_matchers = self.compile_regexps_string(self.include_regexps)
        except Exception as exc:
            raise SyntaxError('Unable to compile include regexp for field detector #{1} and field {2}. Regexp:\n{0}\n'
                              'Reason: {3}'
                              .format(self.include_regexps, self.pk, self.field.code, exc))

        try:
            self._exclude_matchers = self.compile_regexps_string(self.exclude_regexps)
        except Exception as exc:
            raise SyntaxError('Unable to compile exclude regexp for field detector #{1} and field {2}. Regexp:\n{0}\n'
                              'Reason: {3}'
                              .format(self.exclude_regexps, self.pk, self.field.code, exc))

    def _matches_exclude_regexp(self, sentence: str) -> bool:
        if self._exclude_matchers:
            for matcher_re in self._exclude_matchers:
                for _m in matcher_re.finditer(sentence):
                    return True
        return False

    def _clean_def_words(self, s: str):
        res = ''.join(filter(lambda ss: ss.isalpha() or ss.isnumeric() or ss.isspace(), s))
        return ' '.join(res.split()).lower()

    class Meta:
        ordering = ('uid',)

    def __str__(self):
        return "{0}: {1}".format(self.field, self.include_regexps)[:50] \
               + " (#{0})".format(self.uid)

    def __repr__(self):
        return "{0}: {1}".format(self.field, self.include_regexps)[:50] \
               + " (#{0})".format(self.uid)

    def check_model(self) -> List[Tuple[str, Any]]:
        errors = []  # type: List[Tuple[str, Any]]
        try:
            self.compile_regexps_string(self.exclude_regexps)
        except Exception as exc:
            errors.append(('exclude_regexps', exc,))

        try:
            self.compile_regexps_string(self.include_regexps)
        except Exception as exc:
            errors.append(('include_regexps', exc,))

        try:
            from apps.document.field_detection.detector_field_matcher import DetectorFieldMatcher
            DetectorFieldMatcher.validate_detected_value(
                self.field.type, self.detected_value)
        except Exception as exc:
            errors.append(('detected_value', exc,))
        return errors


class DocumentFieldMultilineRegexDetector(models.Model):
    document_field = models.OneToOneField(
        DocumentField, db_index=True, primary_key=True, blank=False, null=False, on_delete=CASCADE)

    csv_content = models.TextField(blank=True, null=True, help_text='''CSV structure where:
    - the first column is the detected value,
    - the second column is the regular expression,
    - separators are semicolon, other semicolon are escaped with \\''')

    csv_checksum = models.CharField(blank=True, db_index=True, max_length=100, null=True,
                                    help_text='''The field is used for caching regular expressions between
                                     parsing tasks. Should be rewritten upon changing csv_content.''')

    # Number of value to extract in case of multiple values
    extraction_hint = models.CharField(max_length=30, choices=EXTRACTION_HINT_CHOICES,
                                       default=EXTRACTION_HINT_CHOICES[0][0], db_index=True,
                                       blank=True, null=True, help_text='''Provide additional instruction on which 
    specific values should be prioritized for extraction, when multiple values of the same type 
    (e.g., Company, Person, Geography) are found within the relevant detected Text Unit.''')

    text_part = models.CharField(max_length=30,
                                 choices=DocumentFieldDetector.TEXT_PARTS,
                                 default=DocumentFieldDetector.TEXT_PARTS[0][0], db_index=True,
                                 blank=False, null=False, help_text='''Defines which part of the matched Text Unit 
    should be passed to the extraction function. Example: In the string "2019-01-23 is the start date and 2019-01-24 is the 
    end date," if text part = "Before matching substring" and Include regexp is "is.{0,100}start" then "2019-01-23" will be 
    parsed correctly as the start date.''')

    regexps_pre_process_lower = models.BooleanField(
        blank=False, null=False, default=True,
        verbose_name='Make search case-insensitive',
        help_text='''Set 'ignore case' flag for both 'Include regexps' and 'Exclude regexps' options.''')

    def __repr__(self):
        short_text = self.csv_content or ''
        short_text = short_text if len(short_text) < 512 else short_text[512] + ' ...'
        field_code = self.document_field.code if self.document_field else '-'
        return f'field: {field_code}\n{short_text}'

    def update_checksum(self):
        if not self.csv_content:
            self.csv_checksum = None
            return
        m = hashlib.md5()
        m.update(self.csv_content.encode('utf-8'))
        self.csv_checksum = m.hexdigest()

    def get_as_pandas_df(self):
        return self.get_csv_as_pandas_df(self.csv_content)

    @classmethod
    def get_csv_as_pandas_df(cls, csv_data):
        if not csv_data:
            return None
        with StringIO(csv_data) as cs_stream:
            df = pd.read_csv(cs_stream,
                             usecols=[1, 2],
                             header=None,
                             skiprows=1,
                             names=['value', 'pattern'],
                             dtype={'value': str, 'pattern': str})
            if df.shape[0] > 0:
                if df.iloc[0]['value'] == 'value' and df.iloc[0]['pattern'] == 'pattern':
                    df.drop(0, axis=0, inplace=True)
            return df

    def combine_with_dataframe(self, df: pd.DataFrame) -> None:
        """
        "Append" another DF (value, pattern) to own data and update csv_content
        Remove duplicates by value or pattern
        :param df: dataframe (value, pattern) to append
        """
        own_df = self.get_as_pandas_df()
        if own_df is None:
            self.csv_content = df.to_csv()
            self.update_checksum()
            return
        own_df = own_df.append(df, ignore_index=True)
        own_df.drop_duplicates(subset='pattern',
                               inplace=True,
                               keep='last')
        self.csv_content = own_df.to_csv()
        self.update_checksum()


class ClassifierModel(models.Model):
    document_field = models.ForeignKey(DocumentField, db_index=True, null=False,
                                       blank=True, default=None, on_delete=CASCADE)

    trained_model = models.BinaryField(null=True, blank=True)

    field_detection_accuracy = models.FloatField(null=True, blank=True)

    classifier_accuracy_report_in_sample = models.CharField(max_length=1024, null=True, blank=True)

    classifier_accuracy_report_out_of_sample = models.CharField(max_length=1024, null=True, blank=True)

    store_suggestion = models.BooleanField(default=False)

    def get_trained_model_obj(self):
        if not self.trained_model:
            return None
        return pickle.loads(self.trained_model)

    def set_trained_model_obj(self, obj):
        self.trained_model = pickle.dumps(obj)

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return "ClassifierModel (document_type={0})" \
            .format(self.document_field)

    def __repr__(self):
        return "ClassifierModel (id={0})".format(self.pk)


class FieldValue(models.Model):
    modified_date = models.DateTimeField(auto_now=True, db_index=True)
    modified_by = models.ForeignKey(User, null=True, blank=True, db_index=True, on_delete=CASCADE)

    document = models.ForeignKey(Document, db_index=True, on_delete=CASCADE, related_name='field_values')

    field = models.ForeignKey(DocumentField, db_index=True, on_delete=CASCADE)

    value = JSONField(blank=True, null=True, encoder=ImprovedDjangoJSONEncoder)

    history = HistoricalRecords()

    objects = BulkSignalsManager(use_in_migrations=True)

    def is_user_value(self):
        return self.modified_by is not None

    class Meta:
        unique_together = ['document', 'field']

    def __repr__(self):
        doc_name = self.document.name if self.document and hasattr(self.document, 'name') else ''
        field_code = self.field.code if self.field and hasattr(self.field, 'code') else ''

        value = str(self.value) if self.value else ''
        if len(value) > 255:
            value = value[:252] + '...'
        return f'doc: "{doc_name}", field: "{field_code}", value: "{value}"'

    @property
    def python_value(self):
        from apps.document.field_types import TypedField
        try:
            typed_field = TypedField.by(self.field)
            return typed_field.field_value_json_to_python(self.value)
        except:
            pass


class FieldAnnotationStatus(models.Model):
    """
    FieldAnnotationStatus object model
    """
    # Status verbose name
    name = models.CharField(unique=True, max_length=100, db_index=True)

    # Status code
    code = models.CharField(unique=True, max_length=100, db_index=True, blank=True, null=True)

    # Status order number
    order = models.PositiveSmallIntegerField()

    # flag to detect f.e. whether we should recalculate fields for a document
    is_active = models.BooleanField(default=True, db_index=True)

    # flag - to set it automatically if a document has "completed" status
    is_accepted = models.BooleanField(default=False, db_index=True)

    # flag - to transform annotation into FalseMatch
    is_rejected = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['order', 'name', 'code']
        verbose_name_plural = 'Field Annotation Statuses'

    def __str__(self):
        return "FieldAnnotationStatus (pk={}, name={})".format(self.pk, self.name)

    @property
    def is_final_status(self):
        return self.is_accepted or self.is_rejected

    @classmethod
    def initial_status(cls):
        return cls.objects.first()

    @classmethod
    def initial_status_pk(cls):
        status = cls.initial_status()
        return status.pk if status else None

    @classmethod
    def accepted_status(cls):
        return cls.objects.filter(is_accepted=True).first()

    @classmethod
    def accepted_status_pk(cls):
        status = cls.accepted_status()
        return status.pk if status else None

    @classmethod
    def rejected_status(cls):
        return cls.objects.filter(is_rejected=True).first()

    @classmethod
    def rejected_status_pk(cls):
        status = cls.rejected_status()
        return status.pk if status else None


class FieldAnnotation(models.Model):
    # INFO: added to make unique field among FieldAnnotation and FieldAnnotationFalseMatch
    # as we use combined clauses views
    # TODO: make it primary_key? - had issues with updating pk for history objects
    uid = StringUUIDField(default=uuid.uuid4, editable=False)

    modified_date = models.DateTimeField(auto_now=True, db_index=True)
    modified_by = models.ForeignKey(User, null=True, blank=True, db_index=True, on_delete=CASCADE)

    document = models.ForeignKey(Document, db_index=True, on_delete=CASCADE, related_name='annotations_matches')

    field = models.ForeignKey(DocumentField, db_index=True, on_delete=CASCADE, related_name='annotations_matches')

    value = JSONField(blank=True, null=True, encoder=ImprovedDjangoJSONEncoder)

    location_start = models.PositiveIntegerField(null=True, blank=True)

    location_end = models.PositiveIntegerField(null=True, blank=True)

    location_text = models.TextField(null=True, blank=True)

    text_unit = models.ForeignKey(TextUnit, blank=True, null=True,
                                  on_delete=CASCADE, related_name='annotations_matches')

    extraction_hint = models.CharField(max_length=30, choices=EXTRACTION_HINT_CHOICES,
                                       default=EXTRACTION_HINT_CHOICES[0][0],
                                       blank=True, null=True)

    assignee = models.ForeignKey(User, blank=True, null=True, db_index=True, on_delete=SET_NULL,
                                 related_name='field_annotations')

    assign_date = models.DateTimeField(blank=True, null=True)

    status = models.ForeignKey(FieldAnnotationStatus, default=FieldAnnotationStatus.initial_status_pk,
                               blank=True, null=True, db_index=True, on_delete=SET_NULL)

    history = HistoricalRecords()

    objects = BulkSignalsManager()

    class Meta:
        unique_together = ['document', 'field', 'value', 'location_start', 'location_end']
        indexes = [
            Index(fields=['extraction_hint'])]

    @property
    def available_assignees(self):
        return self.document.project.available_assignees

    @property
    def is_user_value(self):
        return self.modified_by is not None

    def __repr__(self):
        doc_name = self.document.name if self.document and hasattr(self.document, 'name') else ''
        field_code = self.field.code if self.field and hasattr(self.field, 'code') else ''

        value = str(self.value) if self.value else ''
        if len(value) > 255:
            value = value[:252] + '...'
        coords = f'({self.location_start}, {self.location_end})'
        return f'doc: "{doc_name}", field: "{field_code}", value: "{value}", ' + \
               f'coords: {coords}'

    @property
    def python_value(self):
        from apps.document.field_types import TypedField
        try:
            typed_field = TypedField.by(self.field)
            return typed_field.field_value_json_to_python(self.value)
        except:
            pass


class FieldAnnotationFalseMatch(models.Model):
    # INFO: added to make unique field among FieldAnnotation and FieldAnnotationFalseMatch
    # as we use combined clauses views
    # TODO: make it primary_key? - had issues with updating pk for history objects
    uid = StringUUIDField(default=uuid.uuid4, editable=False)

    document = models.ForeignKey(Document, db_index=True, on_delete=CASCADE, related_name='annotation_false_matches')

    field = models.ForeignKey(DocumentField, db_index=True, on_delete=CASCADE, related_name='annotation_false_matches')

    value = JSONField(blank=True, null=True, encoder=ImprovedDjangoJSONEncoder)

    location_start = models.PositiveIntegerField(null=True, blank=True)

    location_end = models.PositiveIntegerField(null=True, blank=True)

    location_text = models.TextField(null=True, blank=True)

    text_unit = models.ForeignKey(TextUnit, blank=True, null=True,
                                  on_delete=CASCADE,
                                  related_name='annotation_false_matches')

    assignee = models.ForeignKey(User, blank=True, null=True, db_index=True, on_delete=SET_NULL,
                                 related_name='annotation_false_matches')

    assign_date = models.DateTimeField(blank=True, null=True)

    history = HistoricalRecords()

    class Meta:
        unique_together = ['document', 'field', 'value', 'location_start', 'location_end']

    @staticmethod
    def make_from_annotation(ant: FieldAnnotation) -> 'FieldAnnotationFalseMatch':
        fa = FieldAnnotationFalseMatch()
        fa.document = ant.document
        fa.field = ant.field
        fa.value = ant.value
        fa.location_start = ant.location_start
        fa.location_end = ant.location_end
        fa.location_text = ant.location_text
        fa.text_unit = ant.text_unit
        fa.assignee = ant.assignee
        fa.uid = ant.uid
        return fa


class FieldAnnotationSavedFilter(models.Model):
    FILTER_TYPE_CHOICES = [
        (constants.FA_COMMON_FILTER, 'Common Filter'),
        (constants.FA_USER_FILTER, 'User Project Annotations Grid Config')
    ]

    filter_type = models.CharField(max_length=50, blank=False, null=False,
                                   default=constants.FA_COMMON_FILTER, choices=FILTER_TYPE_CHOICES)

    title = models.CharField(max_length=256, blank=True, null=True)

    display_order = models.PositiveSmallIntegerField(default=0)

    project = models.ForeignKey('project.Project', null=True, blank=True, db_index=True, on_delete=CASCADE)

    document_type = models.ForeignKey(DocumentType, null=False, blank=False, db_index=True, on_delete=CASCADE)

    user = models.ForeignKey(User, blank=True, null=True, db_index=True, on_delete=CASCADE)

    columns = JSONField(blank=True, null=True, encoder=ImprovedDjangoJSONEncoder)

    column_filters = JSONField(blank=True, null=True, encoder=ImprovedDjangoJSONEncoder)

    order_by = JSONField(blank=True, null=True, encoder=ImprovedDjangoJSONEncoder)

    class Meta:
        ordering = ['filter_type', 'user__username', 'project_id']
        verbose_name_plural = 'Field Annotation Saved Filters'

    def __str__(self):
        return "FieldAnnotationSavedFilter (pk={}, user={}, project={})".format(
            self.pk, self.user.username, self.project_id)


class DocumentTable(models.Model):
    document = models.ForeignKey(Document, db_index=True, on_delete=CASCADE)

    table = PickledObjectField(compress=True)

    def __repr__(self):
        return ''
