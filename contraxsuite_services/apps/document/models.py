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
from typing import List

# Django imports
from ckeditor.fields import RichTextField
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Count
from django.dispatch import receiver
from django.utils.timezone import now
from lexnlp.extract.en.definitions import get_definitions_in_sentence
from simple_history.models import HistoricalRecords

# Project imports
from apps.common.fields import StringUUIDField, CustomJSONField
from apps.common.managers import AdvancedManager
from apps.common.models import get_default_status
from apps.document import constants
from apps.document.field_types import FieldType, FIELD_TYPES_REGISTRY, FIELD_TYPES_CHOICE, ValueExtractionHint, \
    ORDINAL_EXTRACTION_HINTS
from apps.document.fields_detection.utils import remove_num_separators
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.5a/LICENSE"
__version__ = "1.1.5a"
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


class DocumentField(TimeStampedModel):
    """DocumentField object model

    DocumentField describes manually created custom field for a document.
    """
    DOCUMENT_FIELD_TYPES = ((i, FIELD_TYPES_REGISTRY[i].title or i) for i in sorted(FIELD_TYPES_REGISTRY))
    UNIT_TYPES = ((i, i) for i in ('sentence', 'paragraph', 'section'))
    CONFIDENCE = ('High', 'Medium', 'Low')
    CONFIDENCE_CHOICES = ((i, i) for i in CONFIDENCE)

    KIND_REQUIRED_FOR_CALCULATIONS = 'required_for_calculations'
    KIND_CALCULATED = 'calculated'

    # Make pk field unique
    uid = StringUUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Short name for field.
    code = models.CharField(max_length=50, db_index=True, unique=True)

    # Verbose name for field.
    title = models.CharField(max_length=100, db_index=True)

    # Verbose description - information which does not fit into title
    description = models.TextField(null=True, blank=True)

    # Type of the field.
    type = models.CharField(max_length=30, choices=DOCUMENT_FIELD_TYPES,
                            default='string', db_index=True)

    # Type of the text unit to parse.
    text_unit_type = models.CharField(max_length=10, choices=UNIT_TYPES,
                                      default='sentence', db_index=True)

    VD_DISABLED = 'disabled'

    VD_USE_REGEXPS_ONLY = 'use_regexps_only'

    VD_USE_FORMULA_ONLY = 'use_formula_only'

    VD_REGEXPS_AND_TEXT_BASED_ML = 'regexps_and_text_based_ml'

    VD_TEXT_BASED_ML_ONLY = 'text_based_ml_only'

    VD_FORMULA_AND_FIELD_BASED_ML = 'formula_and_fields_based_ml'

    VD_FIELD_BASED_ML_ONLY = 'fields_based_ml_only'

    VD_PYTHON_CODED_FIELD = 'python_coded_field'

    VD_FIELD_BASED_REGEXPS = 'field_based_regexps'

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

    formula = models.TextField(null=True, blank=True)

    value_regexp = models.TextField(null=True, blank=True)

    depends_on_fields = models.ManyToManyField('self', blank=True, related_name='affects_fields', symmetrical=False)

    confidence = models.CharField(max_length=100, choices=CONFIDENCE_CHOICES, default=None,
                                  blank=True, null=True, db_index=True)

    requires_text_annotations = models.BooleanField(default=True, null=False, blank=False)

    read_only = models.BooleanField(default=False, null=False, blank=False)

    metadata = CustomJSONField(blank=True, null=True, encoder=DjangoJSONEncoder)

    def is_detectable(self):
        return self.value_detection_strategy and self.value_detection_strategy != self.VD_DISABLED

    def get_field_type(self) -> FieldType:
        return FIELD_TYPES_REGISTRY[self.type]

    def is_value_aware(self):
        return self.get_field_type().value_aware

    def get_depends_on_uids(self):
        depends_on_fields = self.depends_on_fields.all()
        return {f.uid for f in depends_on_fields} if depends_on_fields else None

    def get_depends_on_codes(self):
        depends_on_fields = self.depends_on_fields.all()
        return {f.code for f in depends_on_fields} if depends_on_fields else None

    # In case the type of the field requires selecting one of pre-defined values -
    # they should be stored \n-separated in the "choices" property
    choices = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (('code', 'modified_by', 'modified_date'),)
        ordering = ('code',)

    def __str__(self):
        return "{0}".format(self.code)

    def __repr__(self):
        return "{1} (#{0})".format(self.pk, self.code)

    def is_choice_field(self):
        return self.type in FIELD_TYPES_CHOICE

    def is_value_extracting_field(self):
        return self.type and FIELD_TYPES_REGISTRY[self.type].value_extracting

    def get_choice_values(self) -> List[str]:
        if not self.choices:
            return []
        return [choice.strip() for choice in self.choices.strip().splitlines()]


class DocumentType(TimeStampedModel):
    """
    DocumentType describes custom document type.
    """

    DOCUMENT_EDITOR_CHOICES = ['save_by_field', 'save_all_fields_at_once', 'no_text']
    DOCUMENT_EDITOR_CHOICES = [(i, i) for i in DOCUMENT_EDITOR_CHOICES]

    # Make pk field unique
    uid = StringUUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Short name for field.
    code = models.CharField(max_length=50, db_index=True)

    # Verbose name for field.
    title = models.CharField(max_length=100, db_index=True)

    # full set of fields to annotate on Document detail page
    fields = models.ManyToManyField(
        DocumentField, related_name='field_document_type', blank=True, through='DocumentTypeField')

    # Aliases of field codes for document import purposes.
    # Json format: { "alias1": "field_code1", "alias2": "field_code2", ...}
    field_code_aliases = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)

    # lesser set of fields to filter/sort on Document list page
    search_fields = models.ManyToManyField(
        DocumentField, related_name='search_field_document_type', blank=True)

    editor_type = models.CharField(max_length=100, blank=True, null=True, choices=DOCUMENT_EDITOR_CHOICES)

    metadata = CustomJSONField(blank=True, null=True, encoder=DjangoJSONEncoder)

    def get_classifier(self):
        classifiers = self.classifiers.iterator()
        if classifiers:
            classifier = next(classifiers, None)
            if classifier:
                return classifier.get_trained_model_obj()
        return None

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
            code='document.GenericDocument',
            title='Generic Document')
        # UID for generic doc type is hardcoded here to prevent problems if
        # uploading full config dump from one host where it has one uid to another host
        # where generic doc type possibly has another uid.
        return obj

    @classmethod
    def generic_pk(cls):
        return cls.generic().pk

    def is_generic(self):
        return self == DocumentType.generic()


class DocumentTypeFieldManager(models.Manager):
    def set_dirty_for_value(self, value):
        document_type_field = self.get(document_field_id=value.field_id,
                                       document_type_id=value.document.document_type_id)
        document_type_field.dirty = True
        document_type_field.save()

    def _get_dirty_fields_filter(self):
        user_delay = DocumentTypeFieldManager.get_user_delay()
        return self.filter(dirty=True,
                           training_finished=False,
                           modified_date__lt=user_delay)

    def has_dirty_fields(self):
        return self._get_dirty_fields_filter().exists()

    def get_dirty_fields(self):
        return self._get_dirty_fields_filter().prefetch_related('document_type', 'document_field').all()

    @staticmethod
    def get_user_delay():
        return now() - datetime.timedelta(seconds=settings.RETRAINING_DELAY_IN_SEC)

    def get_document_type_field(self, document_type_uid, field_uid):
        return self.get(document_type__pk=document_type_uid, document_field__pk=field_uid)


class DocumentTypeFieldCategory(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    #
    # type_fields = models.ManyToManyField(DocumentTypeField, db_index=True, related_name='category')

    order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Document Type Field Categories'
        ordering = ('order', 'name')

    def __str__(self):
        return self.name

    def __repr__(self):
        return "{1} (#{0})".format(self.pk, self.name)


class DocumentTypeField(models.Model):
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE,
                                      db_column='documenttype_id')

    document_field = models.ForeignKey(DocumentField, on_delete=models.CASCADE,
                                       db_column='documentfield_id')

    category = models.ForeignKey(DocumentTypeFieldCategory, blank=True, null=True, db_index=True)

    training_finished = models.BooleanField(default=False)

    dirty = models.BooleanField(default=False)

    order = models.PositiveSmallIntegerField(default=0)

    trained_after_documents_number = models.PositiveIntegerField(default=settings.TRAINED_AFTER_DOCUMENTS_NUMBER,
                                                                 null=False, validators=[MinValueValidator(1)])
    modified_date = models.DateTimeField(auto_now=True)

    created_date = models.DateTimeField(auto_now_add=True)

    objects = DocumentTypeFieldManager()

    class Meta:
        unique_together = ('document_type', 'document_field',)
        indexes = [
            models.Index(fields=['dirty']),
            models.Index(fields=['training_finished']),
            models.Index(fields=['modified_date']),
        ]

    def __str__(self):
        return 'DocumentTypeField type:{} field:{}'.format(self.document_type.code, self.document_field.code)

    def can_retrain(self):
        return self.dirty \
               and not self.training_finished \
               and self.modified_date < DocumentTypeFieldManager.get_user_delay()


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
    description = models.TextField(null=True)

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
    metadata = JSONField(blank=True, encoder=DjangoJSONEncoder)

    # Cache of document field values for document in the format of dict: { field_uid: field_value }
    # For calculated fields this dict additionally contains: { field_uid_suggested: calculated_field_value }
    field_values = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)

    # Cache of generic document values like: max_currency_amount, cluster id e.t.c. for showing in batch project grids
    generic_data = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)

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

    # Document timestamp
    timestamp = models.DateTimeField(default=now, db_index=True)

    # Note body
    note = RichTextField()

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
            .format(self.document.name, self.field.code, str(self.value)[:40], self.id)

    @property
    def python_value(self):
        field_type = self.field.get_field_type()  # type: FieldType
        return field_type.single_db_value_to_python(self.value)

    @python_value.setter
    def python_value(self, pv):
        field_type = self.field.get_field_type()  # type: FieldType
        self.value = field_type.single_python_value_to_db(pv)


class ExternalFieldValue(TimeStampedModel):
    """ExternalFieldValue  object model

    ExternalFieldValue contains external field values to train classifier.
    Transfer container for Training Data For Document Field Values.
    """

    # DocumentType uid
    type_id = models.CharField(max_length=36)

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


class DocumentFieldDetector(models.Model):
    DEF_RE_FLAGS = re.DOTALL

    uid = StringUUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    field = models.ForeignKey(DocumentField, blank=False, null=False,
                              related_name='field_detectors')

    # \n-separated list of words to search in the list of terms returned by get_definitions()
    # If set - this detector checks if the sentence if a definition of any term in this list.
    #          Include/exclude regexps are additionally checked next only if the definition matches.
    # If not set - apply include/exclude regexps to all sentences.
    definition_words = models.TextField(blank=True, null=True)

    # Field Detectors with no document type specified work for any document type
    document_type = models.ForeignKey(DocumentType, blank=True, null=True)

    # \n-separated regexps excluding sentences from possible match
    exclude_regexps = models.TextField(blank=True, null=True)

    # \n-separated regexps for detecting sentences containing field values
    # Process order: (1) exclude, (2) include
    include_regexps = models.TextField(blank=True, null=True)

    regexps_pre_process_lower = models.BooleanField(blank=False, null=False, default=False)

    regexps_pre_process_remove_numeric_separators = models.BooleanField(blank=False,
                                                                        null=False,
                                                                        default=False)

    # For choice fields - the value which should be set if a sentence matches this detector
    detected_value = models.CharField(max_length=256, blank=True, null=True)

    # Number of value to extract in case of multiple values
    extraction_hint = models.CharField(max_length=30, choices=EXTRACTION_HINT_CHOICES,
                                       default=EXTRACTION_HINT_CHOICES[0][0], db_index=True,
                                       blank=True, null=True)

    # Validator. If field is not of an ordinal type and TAKE_MIN/MAX are selected, throw error
    def clean_fields(self, exclude=('uid', 'field', 'document_type', 'exclude_regexps',
                                    'include_regexps', 'regexps_pre_process_lower',
                                    'regexps_pre_process_remove_numeric_separators',
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

    def compile_regexps(self):

        if self.definition_words:
            dw = []
            for w in self.definition_words.split('\n'):
                w = w.strip()
                if w:
                    dw.append(self._clean_def_words(w))
            self._definition_words = dw or None

        self._include_matchers = []

        if self.include_regexps:
            for r in self.include_regexps.split('\n'):
                r = r.strip()
                if r:
                    self._include_matchers.append(re.compile(r, self.DEF_RE_FLAGS))

        self._exclude_matchers = []

        if self.exclude_regexps:
            for r in self.exclude_regexps.split('\n'):
                r = r.strip()
                if r:
                    self._exclude_matchers.append(re.compile(r, self.DEF_RE_FLAGS))

    def _matches_exclude_regexp(self, sentence: str) -> bool:
        if self._exclude_matchers:
            for matcher_re in self._exclude_matchers:
                for m in matcher_re.finditer(sentence):
                    return True
        return False

    def _matches_include_regexp(self, sentence: str) -> bool:
        if self._include_matchers:
            for matcher_re in self._include_matchers:
                for m in matcher_re.finditer(sentence):
                    return True
        return False

    def _clean_def_words(self, s: str):
        res = ''.join(filter(lambda ss: ss.isalpha() or ss.isnumeric() or ss.isspace(), s))
        return ' '.join(res.split()).lower()

    def _matches_definition_words(self, sentence: str) -> bool:
        if self._definition_words:
            terms = get_definitions_in_sentence(sentence)
            if not terms:
                return False
            terms = set([self._clean_def_words(t) for t in terms])

            for w in self._definition_words:
                if w in terms:
                    return True
        return False

    def matches(self, sentence: str):
        if self._include_matchers is None or self._exclude_matchers is None:
            self.compile_regexps()

        if not sentence:
            return False

        sentence = sentence.replace('\n', ' ').replace('\t', ' ')

        if self.regexps_pre_process_lower:
            sentence = sentence.lower()
        if self.regexps_pre_process_remove_numeric_separators:
            sentence = remove_num_separators(sentence)

        if self._matches_exclude_regexp(sentence):
            return False

        if self._definition_words:
            if not self._matches_definition_words(sentence):
                return False

            return not self._include_matchers or self._matches_include_regexp(sentence)
        else:
            return self._matches_include_regexp(sentence)

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
    document_type = models.ForeignKey(DocumentType, db_index=True, related_name='classifiers')

    document_field = models.ForeignKey(DocumentField, db_index=True, null=True, blank=True)

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
            .format(self.document_type)

    def __repr__(self):
        return "ClassifierModel (id={0})".format(self.id)
