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
import os
import pickle
import re
import uuid
from enum import Enum
from typing import List, Optional, Tuple
import jiphy

# Django imports
from ckeditor.fields import RichTextField
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Count, F, Value
from django.db.models.functions import Concat
from django.dispatch import receiver
from django.utils.timezone import now
from lexnlp.extract.en.definitions import get_definitions_in_sentence, get_definitions
from simple_history.models import HistoricalRecords

# Project imports
from apps.common.fields import StringUUIDField, CustomJSONField
from apps.common.managers import AdvancedManager
from apps.common.utils import CustomDjangoJSONEncoder
from apps.common.models import get_default_status
from apps.document import constants
from apps.document.field_types import FieldType, FIELD_TYPES_REGISTRY, FIELD_TYPES_CHOICE, ValueExtractionHint, \
    ORDINAL_EXTRACTION_HINTS, RelatedInfoField
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.8/LICENSE"
__version__ = "1.1.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def all_reviewers():
    return {'role': 'reviewer'}


EXTRACTION_HINT_CHOICES = tuple((hint.name, hint.name) for hint in ValueExtractionHint)


class TimeStampedModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_date = models.DateTimeField(auto_now=True, db_index=True)
    created_by = models.ForeignKey(
        User, related_name="created_%(class)s_set", null=True, blank=True, db_index=True)
    modified_by = models.ForeignKey(
        User, related_name="modified_%(class)s_set", null=True, blank=True, db_index=True)

    class Meta:
        abstract = True

    @staticmethod
    def save_timestamp(sender, instance, created, func):
        if hasattr(instance, 'request_user'):
            models.signals.post_save.disconnect(func, sender=sender)
            if created:
                instance.created_by = instance.request_user
            instance.modified_by = instance.request_user
            instance.save()
            models.signals.post_save.connect(func, sender=sender)


class DocumentFieldCategory(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Document Field Categories'
        ordering = ('order', 'name')

    def __str__(self):
        return self.name

    def __repr__(self):
        return "{1} (#{0})".format(self.pk, self.name)


class DocumentFieldManager(models.Manager):
    def set_dirty_for_value(self, value):
        field = self.get(pk=value.field_id, document_type_id=value.document.document_type_id)
        field.dirty = True
        field.save()

    def _get_dirty_fields_filter(self):
        user_delay = DocumentFieldManager.get_user_delay()
        return self.filter(dirty=True,
                           value_detection_strategy__in=DocumentField.VALUE_DETECTION_TRAINABLE,
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
    DOCUMENT_FIELD_TYPES = ((i, FIELD_TYPES_REGISTRY[i].title or i) for i in sorted(FIELD_TYPES_REGISTRY))
    UNIT_TYPES = ((i, i) for i in ('sentence', 'paragraph', 'section'))
    CONFIDENCE = ('High', 'Medium', 'Low')
    CONFIDENCE_CHOICES = ((i, i) for i in CONFIDENCE)

    # Make pk field unique
    uid = StringUUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    document_type = models.ForeignKey('document.DocumentType', null=True, blank=False, related_name='fields')

    # Short name for field.
    code = models.CharField(max_length=50, db_index=True, unique=False)

    # Calculated field. Only for usage in __str__ function
    long_code = models.CharField(max_length=150, null=False, unique=True, default=None)

    # Verbose name for field.
    title = models.CharField(max_length=100, db_index=True)

    # Verbose description - information which does not fit into title
    description = models.TextField(null=True, blank=True)

    # Type of the field.
    type = models.CharField(max_length=30, choices=DOCUMENT_FIELD_TYPES,
                            default='string', db_index=True)

    # Type of the text unit to parse.
    text_unit_type = models.CharField(max_length=10, choices=UNIT_TYPES, default='sentence', db_index=True)

    VD_DISABLED = 'disabled'

    VD_USE_REGEXPS_ONLY = 'use_regexps_only'

    VD_USE_FORMULA_ONLY = 'use_formula_only'

    VD_REGEXPS_AND_TEXT_BASED_ML = 'regexps_and_text_based_ml'

    VD_TEXT_BASED_ML_ONLY = 'text_based_ml_only'

    VD_FORMULA_AND_FIELD_BASED_ML = 'formula_and_fields_based_ml'

    VD_FIELD_BASED_ML_ONLY = 'fields_based_ml_only'

    VD_PYTHON_CODED_FIELD = 'python_coded_field'

    VD_FIELD_BASED_REGEXPS = 'field_based_regexps'

    VALUE_DETECTION_TRAINABLE = {
        VD_REGEXPS_AND_TEXT_BASED_ML,
        VD_TEXT_BASED_ML_ONLY,
        VD_FORMULA_AND_FIELD_BASED_ML,
        VD_PYTHON_CODED_FIELD,
        VD_FIELD_BASED_ML_ONLY
    }

    VALUE_DETECTION_STRATEGY_CHOICES = [(VD_DISABLED, 'Field detection disabled'),
                                        (VD_USE_REGEXPS_ONLY,
                                         'No ML. Use regexp field detectors.'),
                                        (VD_USE_FORMULA_ONLY,
                                         'No ML. Use formula only.'),
                                        (VD_REGEXPS_AND_TEXT_BASED_ML,
                                         'Start with regexps, switch to text-based ML when possible.'),
                                        (VD_TEXT_BASED_ML_ONLY,
                                         'Use pre-trained text-based ML only.'),
                                        (VD_FORMULA_AND_FIELD_BASED_ML,
                                         'Start with formula, switch to fields-based ML when possible.'),
                                        (VD_FIELD_BASED_ML_ONLY, 'Use pre-trained field-based ML only.'),
                                        (VD_PYTHON_CODED_FIELD, 'Use python class for value detection.'),
                                        (VD_FIELD_BASED_REGEXPS, 'Apply regexp field detectors to '
                                                                 'depends-on field values')]

    value_detection_strategy = models.CharField(max_length=50,
                                                choices=VALUE_DETECTION_STRATEGY_CHOICES,
                                                default=VD_USE_REGEXPS_ONLY)

    python_coded_field = models.CharField(max_length=100, db_index=True, null=True, blank=True)

    classifier_init_script = models.TextField(null=True, blank=True)

    formula = models.TextField(null=True, blank=True)

    value_regexp = models.TextField(null=True, blank=True)

    depends_on_fields = models.ManyToManyField('self', blank=True, related_name='affects_fields', symmetrical=False)

    confidence = models.CharField(max_length=100, choices=CONFIDENCE_CHOICES, default=None,
                                  blank=True, null=True, db_index=True)

    requires_text_annotations = models.BooleanField(default=True, null=False, blank=False)

    read_only = models.BooleanField(default=False, null=False, blank=False)

    category = models.ForeignKey(DocumentFieldCategory, blank=True, null=True, db_index=True)

    default_value = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder, help_text='''Default value used 
    for showing in frontend instead of None/null (empty) value. Currently makes sense only for choice / multi-choice
    fields. Should be defined in JSON format - strings should be quoted, null means empty value. Example: "landlord"''')

    # In case the type of the field requires selecting one of pre-defined values -
    # they should be stored \n-separated in the "choices" property
    choices = models.TextField(blank=True, null=True)

    allow_values_not_specified_in_choices = models.BooleanField(blank=False, null=False, default=False)

    # Used for quickly detecting a value if one of these regexps is matched.
    # Format:
    # { "regexp": "choice_value", "regexp": "choice_value", ..... }
    # For field-based field detecting (formulas/ML/field detectors):
    #   - strategies try to find any of these regexps
    stop_words = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)

    metadata = CustomJSONField(blank=True, null=True, encoder=DjangoJSONEncoder)

    training_finished = models.BooleanField(default=False)

    dirty = models.BooleanField(default=False)

    order = models.PositiveSmallIntegerField(default=0)

    trained_after_documents_number = models.PositiveIntegerField(default=settings.TRAINED_AFTER_DOCUMENTS_NUMBER,
                                                                 null=False, validators=[MinValueValidator(1)])

    hidden_always = models.BooleanField(default=False, null=False, blank=False)

    hide_until_python = models.TextField(null=True, blank=True)

    hide_until_js = models.TextField(null=True, blank=True)

    display_yes_no = models.BooleanField(default=False, null=False, blank=False)

    modified_date = models.DateTimeField(auto_now=True)

    created_date = models.DateTimeField(auto_now_add=True)

    objects = DocumentFieldManager()

    def is_detectable(self):
        return self.value_detection_strategy and self.value_detection_strategy != self.VD_DISABLED

    def get_field_type(self) -> FieldType:
        return FIELD_TYPES_REGISTRY[self.type]

    def is_value_aware(self):
        return self.get_field_type().requires_value

    def get_depends_on_uids(self):
        depends_on_fields = self.depends_on_fields.all()
        return {f.uid for f in depends_on_fields} if depends_on_fields else None

    def get_depends_on_codes(self):
        depends_on_fields = self.depends_on_fields.all()
        return {f.code for f in depends_on_fields} if depends_on_fields else None

    class Meta:
        unique_together = (('code', 'document_type'), ('code', 'document_type', 'modified_by', 'modified_date'),)
        indexes = [
            models.Index(fields=['dirty']),
            models.Index(fields=['training_finished']),
            models.Index(fields=['modified_date']),
        ]
        ordering = ('long_code',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._compiled_value_regexp = None

    def __str__(self):
        return self.long_code

    def __repr__(self):
        return "{1} (#{0})".format(self.pk, self.code)

    def is_choice_field(self):
        return self.type in FIELD_TYPES_CHOICE

    def is_related_info_field(self):
        return self.type == RelatedInfoField.code

    def is_value_extracting_field(self):
        return self.type and FIELD_TYPES_REGISTRY[self.type].value_extracting

    def get_choice_values(self) -> List[str]:
        if not self.choices:
            return list()
        return [choice.strip() for choice in self.choices.strip().splitlines()]

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
            document_type = None
            if self.document_type is not None:
                document_type = DocumentType.objects.get(pk=self.document_type.pk)
            self.long_code = self.get_long_code(self, document_type)
            super().save(*args, **kwargs)

    @classmethod
    def get_long_code(cls, field, document_type=None):
        document_type = field.document_type if document_type is None else document_type
        return '{0}: {1}'.format(document_type.code, field.code) if document_type is not None else field.code

    def test_value_regexp(self):
        self._compile_value_regexp()

    def _compile_value_regexp(self):
        return re.compile(self.value_regexp)

    def get_compiled_value_regexp(self):
        if not self._compiled_value_regexp and self.value_regexp and self.value_regexp.strip():
            try:
                self._compiled_value_regexp = self._compile_value_regexp()
            except Exception as exc:
                raise SyntaxError(
                    'Unable to compile value regexp for field {0}. Regexp:\n{1}\n'
                    'Reason: {2}'
                        .format(self.code, self.value_regexp, exc))
        return self._compiled_value_regexp


class DocumentType(TimeStampedModel):
    """
    DocumentType describes custom document type.
    """

    DOCUMENT_EDITOR_CHOICES = ['save_by_field', 'save_all_fields_at_once', 'no_text']
    DOCUMENT_EDITOR_CHOICES = [(i, i) for i in DOCUMENT_EDITOR_CHOICES]
    GENERIC_TYPE_CODE = 'document.GenericDocument'

    # Make pk field unique
    uid = StringUUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Short name for field.
    code = models.CharField(max_length=50, db_index=True, unique=True)

    # Verbose name for field.
    title = models.CharField(max_length=100, db_index=True)

    # Aliases of field codes for document import purposes.
    # Json format: { "alias1": "field_code1", "alias2": "field_code2", ...}
    field_code_aliases = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)

    # lesser set of fields to filter/sort on Document list page
    search_fields = models.ManyToManyField(
        DocumentField, related_name='search_field_document_type', blank=True)

    editor_type = models.CharField(max_length=100, blank=True, null=True, choices=DOCUMENT_EDITOR_CHOICES)

    metadata = CustomJSONField(blank=True, null=True, encoder=DjangoJSONEncoder)

    class Meta:
        unique_together = (('code', 'modified_by', 'modified_date'),)
        ordering = ('code', 'modified_by', 'modified_date')

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


class DocumentManager(models.Manager):
    def active(self):
        return self.filter(status__is_active=True)


class Document(models.Model):
    """Document object model

    Document is the root class for the `document` app model.  Each :model:`document.Document`
    can contain zero or more :model:`document.TextUnit`, as well as its own set of fixed and
    flexible metadata about the document per se.
    """

    # Name of document, as presented in most views and exports.
    name = models.CharField(max_length=1024, db_index=True, null=True)

    # Document description, as provided by metadata or user-entered.
    description = models.TextField(null=True, db_index=True)

    # Language,  as detected upon ingestion and stored via ISO code
    language = models.CharField(max_length=3, blank=True, null=True, db_index=True)

    # Document source name, e.g., Acme File System or Acme Google Mail
    source = models.CharField(max_length=1024, db_index=True, null=True)

    # Document source type, e.g., File System, Email, Salesforce
    source_type = models.CharField(max_length=100, db_index=True, null=True)

    # If relevant, URI/path within document source
    source_path = models.CharField(max_length=1024, db_index=True, null=True)

    # source file size, bytes
    file_size = models.PositiveIntegerField(default=0, null=False)

    # full document text
    full_text = models.TextField(null=True)

    # Pre-calculated length statistics for paragraph and sentence
    paragraphs = models.PositiveIntegerField(default=0, null=False)
    sentences = models.PositiveIntegerField(default=0, null=False)

    # Document metadata from original file
    metadata = JSONField(blank=True, encoder=CustomDjangoJSONEncoder)

    # Cache of document field values for document in the format of dict: { field_uid: field_value }
    # For calculated fields this dict additionally contains: { field_uid_suggested: calculated_field_value }
    field_values = JSONField(blank=True, null=True, encoder=CustomDjangoJSONEncoder)

    # Cache of generic document values like: max_currency_amount, cluster id e.t.c. for showing in batch project grids
    generic_data = JSONField(blank=True, null=True, encoder=CustomDjangoJSONEncoder)

    # Document title
    title = models.CharField(max_length=1024, db_index=True, null=True)

    # Document history
    history = HistoricalRecords(excluded_fields=['full_text'])

    # apply custom objects manager
    objects = DocumentManager()

    document_type = models.ForeignKey(DocumentType, blank=True, null=True, db_index=True)

    project = models.ForeignKey('project.Project', blank=True, null=True, db_index=True)

    status = models.ForeignKey('common.ReviewStatus', default=get_default_status,
                               blank=True, null=True)

    assignee = models.ForeignKey(User, blank=True, null=True, db_index=True)

    upload_session = models.ForeignKey('project.UploadSession', blank=True, null=True,
                                       db_index=True)

    class Meta:
        ordering = ('name',)
        # commented out it as it doesn't allow to upload
        # the same documents (having the same source) into two different projects
        # unique_together = ('name', 'source',)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "{1} ({0})" \
            .format(self.document_type.title, self.name)

    @property
    def text(self):
        """
        Just an alias
        """
        return self.full_text

    @property
    def available_assignees(self):
        return self.project.owners.all().union(self.project.reviewers.all()).distinct()

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

    @staticmethod
    def get_suggested_field_uid(field_uid: str):
        return field_uid + '_suggested'

    def is_completed(self):
        return self.status.is_active

    def is_reviewed(self):
        return not self.status.group.is_active

    def cluster_id(self):
        if not self.document_type.is_generic():
            return None
        return self.documentcluster_set.order_by('-pk').values_list('pk', flat=True).first()


@receiver(models.signals.post_delete, sender=Document)
def full_delete(sender, instance, **kwargs):
    # automatically removes Document, TextUnits, ThingUsages

    # delete file
    file_path = os.path.join(
        settings.MEDIA_ROOT,
        settings.FILEBROWSER_DIRECTORY,
        instance.source_path)
    try:
        os.remove(file_path)
    except OSError:
        pass

    from apps.document.utils import cleanup_document_relations
    cleanup_document_relations(instance)


class DocumentTag(models.Model):
    """DocumentTag object model

    DocumentTag is a flexible class for applying labels or tags to a :model:`document.Document`.
    Each Document can have zero or more DocumentTag records, which can be subsequently used for
    unsupervised task accuracy assessment, semi-supervised tasks, and supervised tasks, as well
    as reporting.
    """

    document = models.ForeignKey(Document, db_index=True)
    tag = models.CharField(max_length=1024, db_index=True)
    timestamp = models.DateTimeField(default=now, db_index=True)
    user = models.ForeignKey(User, db_index=True, null=True)

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
    document = models.ForeignKey(Document, db_index=True)

    # Key - string with maximum length 1024
    key = models.CharField(max_length=1024, db_index=True)

    # Value - string with maximum length 1024
    value = models.TextField()

    class Meta:
        ordering = ('document__name', 'key', 'value')
        verbose_name_plural = 'Document Properties'

    def __str__(self):
        return "DocumentProperty (document={0}, key={1}, value={2})" \
            .format(self.document, self.key, self.value)

    def __repr__(self):
        return "DocumentProperty (document={0}, key={1})" \
            .format(self.document.id, self.key)


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
    document_a = models.ForeignKey(Document, db_index=True, related_name="document_a_set")

    # "Right" or "target" document
    document_b = models.ForeignKey(Document, db_index=True, related_name="document_b_set")

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
    document = models.ForeignKey(Document, db_index=True)

    # Document Field Value
    field_value = models.ForeignKey('document.DocumentFieldValue', blank=True, null=True, db_index=True)

    # Document Field Value
    field = models.ForeignKey('document.DocumentField', blank=True, null=True, db_index=True)

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


@receiver(models.signals.post_delete, sender=DocumentNote)
def delete_note(sender, instance, **kwargs):
    # delete history
    instance.history.all().delete()


class TextUnit(models.Model):
    """TextUnit object model

    TextUnit is the primary container of actual text.  Each Document, upon ingestion, is
    parsed and segmented into zero or more TextUnit records.  Depending on segmentation
    and use case, TextUnits may represent sentences, paragraphs, or some larger unit
    of text.
    """

    # Document
    document = models.ForeignKey(Document, db_index=True)

    # Text unit type, e.g., sentence, paragraph, section
    unit_type = models.CharField(max_length=128, db_index=True)

    # Language,  as detected upon ingestion and stored via ISO code
    language = models.CharField(max_length=3, db_index=True)

    # Raw text
    text = models.TextField(max_length=16384)

    location_start = models.IntegerField(null=True, blank=True)

    location_end = models.IntegerField(null=True, blank=True)

    # Cryptographic hash of raw text for identical de-duplication
    text_hash = models.CharField(max_length=1024, db_index=True, null=True)

    metadata = CustomJSONField(blank=True, null=True, encoder=DjangoJSONEncoder)

    class Meta:
        ordering = ('document__name', 'unit_type')

    def __str__(self):
        return "TextUnit (id={4}, document={0}, unit_type={1}, language={2}, len(text)={3})" \
            .format(self.document, self.unit_type, self.language, len(self.text), self.id, )

    def __repr__(self):
        return "TextUnit (id={0})".format(self.id)

    def is_sentence(self) -> bool:
        return self.unit_type == 'sentence'


class TextUnitTag(models.Model):
    """TextUnitTag object model

    TextUnitTag is a flexible class for applying labels or tags to a :model:`document.TextUnit`.
    Each TextUnit can have zero or more TextUnitTag records, which can be subsequently used for
    unsupervised task accuracy assessment, semi-supervised tasks, and supervised tasks, as well
    as reporting.
    """

    # Text unit
    text_unit = models.ForeignKey(TextUnit, db_index=True)

    # Tag
    tag = models.CharField(max_length=1024, db_index=True)

    # Timestamp
    timestamp = models.DateTimeField(default=now, db_index=True)

    # User
    user = models.ForeignKey(User, db_index=True, null=True)

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
    # Text unit
    text_unit = models.ForeignKey(TextUnit, db_index=True)

    # Key - string with maximum length 1024
    key = models.CharField(max_length=1024, db_index=True)

    # Value - string with maximum length 1024
    value = models.CharField(max_length=1024, db_index=True)

    class Meta:
        ordering = ('text_unit__document__name', 'key', 'value')
        verbose_name_plural = 'Text Unit Properties'

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
    text_unit_a = models.ForeignKey(TextUnit, db_index=True, related_name="text_unit_a_set")

    # Right or "target" text unit
    text_unit_b = models.ForeignKey(TextUnit, db_index=True, related_name="text_unit_b_set")

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
    text_unit = models.ForeignKey(TextUnit, db_index=True)

    # Timestamp
    timestamp = models.DateTimeField(default=now, db_index=True)

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
def delete_note(sender, instance, **kwargs):
    # delete history
    instance.history.all().delete()


class DocumentFieldValue(TimeStampedModel):
    """DocumentFieldValue  object model

    DocumentFieldValue contains value for custom document field.
    """
    # related Document.
    document = models.ForeignKey(Document, db_index=True)

    # related DocumentField
    field = models.ForeignKey(DocumentField, db_index=True)

    # Datastore for extracted value
    # Value should be stored in sortable DB-aware format. See field_types.py
    value = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)

    # source text start position
    location_start = models.PositiveIntegerField(null=True, blank=True)

    # source text end position
    location_end = models.PositiveIntegerField(null=True, blank=True)

    # source text
    location_text = models.TextField(null=True, blank=True)

    # sentence in which this value is located
    # Used as cache for training models.
    # For user entered values - fields location_start, location_end, location_text
    # can contain more detailed position inside sentences - while we train models on sentence level.
    text_unit = models.ForeignKey(TextUnit, blank=True, null=True,
                                  related_name='related_field_values')

    # Extraction hint detected at the moment of storing - used for further model training
    extraction_hint = models.CharField(max_length=30, choices=EXTRACTION_HINT_CHOICES,
                                       default=EXTRACTION_HINT_CHOICES[0][0], db_index=True,
                                       blank=True, null=True)

    removed_by_user = models.BooleanField(default=False)

    # change history
    history = HistoricalRecords()

    objects = AdvancedManager()

    class Meta:
        ordering = ('document_id', 'field__code')

    def __str__(self):
        return "{0}.{1} = {2}" \
            .format(self.document.name, self.field.code, str(self.value)[:40])

    def __repr__(self):
        return "{0}.{1} = {2} (#{3})" \
            .format(self.document_id, self.field_id, str(self.value)[:40], self.id)

    @property
    def python_value(self):
        field_type = self.field.get_field_type()  # type: FieldType
        return field_type.single_db_value_to_python(self.value if not self.field.is_related_info_field()
                                                    else self.location_text)

    @python_value.setter
    def python_value(self, pv):
        if self.field.is_related_info_field():
            return
        field_type = self.field.get_field_type()  # type: FieldType
        self.value = field_type.single_python_value_to_db(pv)

    def is_user_value(self):
        return self.created_by is not None or self.modified_by is not None or self.removed_by_user


class ExternalFieldValue(TimeStampedModel):
    """ExternalFieldValue  object model

    ExternalFieldValue contains external field values to train classifier.
    Transfer container for Training Data For Document Field Values.
    """

    # DocumentField uid
    field_id = models.CharField(max_length=36)

    # Datastore for extracted value
    value = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)

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


class DocumentFieldDetector(models.Model):
    DEF_RE_FLAGS = re.DOTALL

    TEXT_PARTS = tuple((text_part.value, text_part.value) for text_part in TextParts)

    uid = StringUUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    field = models.ForeignKey(DocumentField, blank=False, null=False,
                              related_name='field_detectors')

    CAT_SIMPLE_CONFIG = 'simple_config'

    CATEGORY_CHOICES = [(CAT_SIMPLE_CONFIG, 'Simple field detectors loaded and managed via '
                                            '"Documents: Import Simple Field Detection Config" admin task.')]

    # Field detector category which can be used for finding some special field detectors
    # from the set of all available.
    category = models.CharField(max_length=64, db_index=True, blank=True, null=True, choices=CATEGORY_CHOICES,
                                help_text='''Field detector category used for technical needs e.g. for determining 
which field detectors were created automatically during import process.''')

    exclude_regexps = models.TextField(blank=True, null=True,
                                       help_text='''\\n-separated regexps excluding sentences from possible match. 
Exclude regexps are checked before include regexps or definition words. If one of exclude regexps matches text of a 
text unit then the field detector exits and skips this text unit. Whole text unit does not need to match an 
exclude regexp. The regexps are searched in the text unit.''')

    definition_words = models.TextField(blank=True, null=True,
                                        help_text='''\\n-separated list of definition words (in lowercase) expected 
to be in the text unit. Definition words are checked after the exclude regexps. If definition words are assigned 
to the field detector then get_definitions() function is executed on the text unit. If it finds nothing then skip the
text unit. If the text unit contains one of the definitions from this field then: If there are no include regexps 
then the whole text unit matches the field detector. If there are include regexps then check against them.''')

    include_regexps = models.TextField(blank=True, null=True, help_text='''\\n-separated list of regexps to which 
should be found in the text unit for it to match the field detector. Include regexps are checked after the definition 
words and include regexps. An include regexp does not need to match the whole sentence but it only should be found in 
the sentence. Example: "house" - will match any sentence containing this word. Please avoid using ".*" and similar 
unlimited multipliers. They can cause catastrophic backtracking and slowdown or crash the whole system. 
Use ".{0,100}" or similar instead.''')

    regexps_pre_process_lower = models.BooleanField(blank=False, null=False, default=False,
                                                    help_text='Bring sentence/paragraph to lower case before processing'
                                                              ' with this field detector.')

    # For choice fields - the value which should be set if a sentence matches this detector
    detected_value = models.CharField(max_length=256, blank=True, null=True, help_text='''Assigns this string value to 
the field if this field detector matches. Makes sense for choice/multi-choice/string fields only which don't have 
an extraction function which will be applied to the matching text.''')

    # Number of value to extract in case of multiple values
    extraction_hint = models.CharField(max_length=30, choices=EXTRACTION_HINT_CHOICES,
                                       default=EXTRACTION_HINT_CHOICES[0][0], db_index=True,
                                       blank=True, null=True, help_text='''Hint for selection one of multiple possible
values found by an extraction function of the corresponding field type. Example: Date field finds 5 dates and the last
of them should be taken.''')

    text_part = models.CharField(max_length=30, choices=TEXT_PARTS, default=TEXT_PARTS[0][0], db_index=True,
                                 blank=False, null=False, help_text='''Defines which part of the matching 
sentence / paragraph should be passed to the extraction function of the corresponding field type. 
Example: "2019-01-23 is the Start date and 2019-01-24 is the end date." If include regexp is "is.{0,100}Start" and 
text part = BEFORE_REGEXP then "2019-01-23 " will be passed to get_dates().''')

    # Validator. If field is not of an ordinal type and TAKE_MIN/MAX are selected, throw error
    def clean_fields(self, exclude=('uid', 'field', 'document_type', 'exclude_regexps',
                                    'include_regexps', 'regexps_pre_process_lower',
                                    'detected_value')):
        field_type = FIELD_TYPES_REGISTRY[self.field.type]

        if not field_type.ordinal \
                and self.extraction_hint in ORDINAL_EXTRACTION_HINTS:
            raise ValidationError(('Cannot take min or max of <Field> because its type is not '
                                   'amount, money, int, float, date, or duration. Please select '
                                   'TAKE_FIRST, TAKE_SECOND, or TAKE_THIRD, or change the field '
                                   'type.'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._include_matchers = None
        self._exclude_matchers = None
        self._definition_words = None

    def _compile_include_regexps(self):
        include_matchers = []

        if self.include_regexps:
            for r in self.include_regexps.split('\n'):
                r = r.strip()
                if r:
                    include_matchers.append(re.compile(r, self.DEF_RE_FLAGS))
        return include_matchers

    def _compile_exclude_regexp(self):
        exclude_matchers = []

        if self.exclude_regexps:
            for r in self.exclude_regexps.split('\n'):
                r = r.strip()
                if r:
                    exclude_matchers.append(re.compile(r, self.DEF_RE_FLAGS))
        return exclude_matchers

    def test_include_regexps(self):
        self._compile_include_regexps()

    def test_exclude_regexps(self):
        self._compile_exclude_regexp()

    def compile_regexps(self):

        if self.definition_words:
            dw = []
            for w in self.definition_words.split('\n'):
                w = w.strip()
                if w:
                    dw.append(self._clean_def_words(w))
            self._definition_words = dw or None

        try:
            self._include_matchers = self._compile_include_regexps()
        except Exception as exc:
            raise SyntaxError('Unable to compile include regexp for field detector #{1} and field {2}. Regexp:\n{0}\n'
                              'Reason: {3}'
                              .format(self.include_regexps, self.pk, self.field.code, exc))

        try:
            self._exclude_matchers = self._compile_exclude_regexp()
        except Exception as exc:
            raise SyntaxError('Unable to compile exclude regexp for field detector #{1} and field {2}. Regexp:\n{0}\n'
                              'Reason: {3}'
                              .format(self.exclude_regexps, self.pk, self.field.code, exc))

    def _matches_exclude_regexp(self, sentence: str) -> bool:
        if self._exclude_matchers:
            for matcher_re in self._exclude_matchers:
                for m in matcher_re.finditer(sentence):
                    return True
        return False

    def _match_include_regexp_or_none(self, sentence: str, sentence_before_lower: str) -> Optional[
        Tuple[str, int, int]]:
        if self._include_matchers:
            for matcher_re in self._include_matchers:
                for match in matcher_re.finditer(sentence):
                    return sentence_before_lower, match.start(), match.end()
        return None

    def _clean_def_words(self, s: str):
        res = ''.join(filter(lambda ss: ss.isalpha() or ss.isnumeric() or ss.isspace(), s))
        return ' '.join(res.split()).lower()

    def _matches_definition_words(self, text: str, text_is_sentence: bool) -> bool:
        if self._definition_words:
            terms = get_definitions_in_sentence(text) if text_is_sentence else get_definitions(text)
            if not terms:
                return False
            terms = set([self._clean_def_words(t) for t in terms])

            for w in self._definition_words:
                if w in terms:
                    return True
        return False

    def matches(self, text: str, text_is_sentence: bool = True) -> Optional[Tuple[str, int, int]]:
        if self._include_matchers is None or self._exclude_matchers is None:
            self.compile_regexps()

        if not text:
            return None

        text = text.replace('\n', ' ').replace('\t', ' ')

        sentence_without_lower = text
        if self.regexps_pre_process_lower:
            text = text.lower()

        if self._matches_exclude_regexp(text):
            return None
        else:
            if self._definition_words:
                if not self._matches_definition_words(text, text_is_sentence):
                    return None
                elif not self._include_matchers:
                    return sentence_without_lower, 0, len(sentence_without_lower)
                else:
                    return self._match_include_regexp_or_none(text, sentence_without_lower)
            else:
                return self._match_include_regexp_or_none(text, sentence_without_lower)

    def matching_string(self, text: str, text_is_sentence: bool = True) -> Optional[str]:
        match = self.matches(text, text_is_sentence)
        if match:
            matching_string, begin, end = match
            if self.text_part == TextParts.BEFORE_REGEXP.value:
                return matching_string[:begin]
            elif self.text_part == TextParts.AFTER_REGEXP.value:
                return matching_string[end:]
            else:
                return text
        return None

    class Meta:
        ordering = ('uid',)

    def __str__(self):
        return "{0}: {1}".format(self.field, self.include_regexps)[:50] \
               + " (#{0})".format(self.uid)

    def __repr__(self):
        return "{0}: {1}".format(self.field, self.include_regexps)[:50] \
               + " (#{0})".format(self.uid)


class DocumentFieldDetectingConfig(models.Model):
    pass


class ClassifierModel(models.Model):
    document_field = models.ForeignKey(DocumentField, db_index=True, null=False, blank=True, default=None)

    trained_model = models.BinaryField(null=True, blank=True)

    field_detection_accuracy = models.FloatField(null=True, blank=True)

    classifier_accuracy_report_in_sample = models.CharField(max_length=1024, null=True, blank=True)

    classifier_accuracy_report_out_of_sample = models.CharField(max_length=1024, null=True, blank=True)

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
        return "ClassifierModel (id={0})".format(self.id)
