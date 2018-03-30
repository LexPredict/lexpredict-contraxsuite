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
import os
import pickle
import re
import uuid
from typing import Union, List, Dict, Any

# Django imports
from ckeditor.fields import RichTextField
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.dispatch import receiver
from django.utils.timezone import now
from simple_history.models import HistoricalRecords

# Project imports
from apps.document.field_types import FIELD_TYPES_REGISTRY, FIELD_TYPES_CHOICE, ValueExtractionHint
from apps.document.parsing.extractors import remove_num_separators
from apps.document.parsing.machine_learning import SkLearnClassifierModel
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.8/LICENSE"
__version__ = "1.0.8"
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
    DOCUMENT_FIELD_TYPES = ((i, i) for i in sorted(FIELD_TYPES_REGISTRY))

    KIND_REQUIRED_FOR_CALCULATIONS = 'required_for_calculations'
    KIND_CALCULATED = 'calculated'

    # Make pk field unique
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Short name for field.
    code = models.CharField(max_length=50, db_index=True)

    # Verbose name for field.
    title = models.CharField(max_length=100, db_index=True)

    # Type of the field.
    type = models.CharField(max_length=30, choices=DOCUMENT_FIELD_TYPES,
                            default='string', db_index=True)

    formula = models.TextField(null=True, blank=True)

    depends_on_fields = models.ManyToManyField('self', blank=True, related_name='affects_fields')

    def is_calculated(self):
        return self.formula and self.formula.strip()

    @staticmethod
    def calc_formula(field_type_code: str, formula: str, depends_on_field_to_value: Dict) -> Any:
        if not formula or not formula.strip():
            return None

        if '__' in formula:
            raise SyntaxError('Formula contains "__" string. This may be unsafe for python eval.')
        eval_locals = dict()
        eval_locals.update(settings.CALCULATED_FIELDS_EVAL_LOCALS)

        for field, value in depends_on_field_to_value.items():
            field_type = FIELD_TYPES_REGISTRY[field.type]
            eval_locals[field.code] = field_type.json_value_to_python(value)

        eval_locals.update(depends_on_field_to_value)
        value = eval(formula, {'__builtins__': {}}, eval_locals)
        return FIELD_TYPES_REGISTRY[field_type_code].python_value_to_json(value)

    def calculate(self, depends_on_field_to_value: Dict) -> Any:
        return self.calc_formula(self.type, self.formula, depends_on_field_to_value)

    def get_field_type(self):
        return FIELD_TYPES_REGISTRY[self.type]

    # In case the type of the field requires selecting one of pre-defined values -
    # they should be stored \n-separated in the "choices" property
    choices = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (('code', 'modified_by', 'modified_date'),)
        ordering = ('code', 'modified_by', 'modified_date')

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
        return [choice.strip() for choice in self.choices.strip().split('\n')]


class DocumentType(TimeStampedModel):
    """DocumentType  object model

    DocumentType describes custom document type.
    """
    # Make pk field unique
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Short name for field.
    code = models.CharField(max_length=50, db_index=True)

    # Verbose name for field.
    title = models.CharField(max_length=100, db_index=True)

    # set of DocumentFields allowed for this DocumentType
    fields = models.ManyToManyField(DocumentField, related_name='field_document_type')

    # set of DocumentFields to show in search/browse API
    search_fields = models.ManyToManyField(
        DocumentField, related_name='search_field_document_type', blank=True)

    def get_classifier(self):
        classifiers = self.classifiers.all()
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

    # Document source name, e.g., Acme File System or Acme Google Mail
    source = models.CharField(max_length=1024, db_index=True, null=True)

    # Document source type, e.g., File System, Email, Salesforce
    source_type = models.CharField(max_length=100, db_index=True, null=True)

    # If relevant, URI/path within document source
    source_path = models.CharField(max_length=1024, db_index=True, null=True)

    full_text = models.TextField(null=True)

    # Pre-calculated length statistics for paragraph and sentence
    paragraphs = models.PositiveIntegerField(default=0, null=False)
    sentences = models.PositiveIntegerField(default=0, null=False)

    # Document metadata from original file
    metadata = JSONField(blank=True)

    # Document title
    title = models.CharField(max_length=1024, db_index=True, null=True)

    # Document history
    history = HistoricalRecords()

    document_type = models.ForeignKey(DocumentType, blank=True, null=True, db_index=True)

    project = models.ForeignKey('project.Project', blank=True, null=True, db_index=True)

    upload_session = models.ForeignKey('project.UploadSession', blank=True, null=True,
                                       db_index=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "{1} ({0})" \
            .format(self.document_type, self.name)

    @property
    def text(self):
        return '\n'.join(self.textunit_set.values_list('text', flat=True))


@receiver(models.signals.post_delete, sender=Document)
def delete_document_file(sender, instance, **kwargs):
    file_path = os.path.join(
        settings.MEDIA_ROOT,
        settings.FILEBROWSER_DIRECTORY,
        instance.source_path)
    try:
        os.remove(file_path)
    except OSError:
        pass


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
    value = models.CharField(max_length=1024)

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
    value = models.CharField(max_length=1024)

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


class DocumentFieldValue(TimeStampedModel):
    """DocumentFieldValue  object model

    DocumentFieldValue contains value for custom document field.
    """
    # related Document.
    document = models.ForeignKey(Document, db_index=True)

    # related DocumentField
    field = models.ForeignKey(DocumentField, db_index=True)

    # Datastore for extracted value
    value = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)

    # source text start position
    location_start = models.PositiveIntegerField()

    # source text end position
    location_end = models.PositiveIntegerField()

    # source text
    location_text = models.TextField(null=True, blank=True)

    # sentence in which this value is located
    # Used as cache for training models.
    # For user entered values - fields location_start, location_end, location_text
    # can contain more detailed position inside sentences - while we train models on sentence level.
    sentence = models.ForeignKey(TextUnit, blank=True, null=True,
                                 related_name='related_field_values')

    # Extraction hint detected at the moment of storing - used for further model training
    extraction_hint = models.CharField(max_length=30, choices=EXTRACTION_HINT_CHOICES,
                                       default=EXTRACTION_HINT_CHOICES[0][0], db_index=True,
                                       blank=True, null=True)

    # change history
    history = HistoricalRecords()

    class Meta:
        ordering = ('document_id', 'field__code')

    def __str__(self):
        return "{0}.{1} = {2}" \
            .format(self.document.name, self.field.code, str(self.value)[:40])

    def __repr__(self):
        return "{0}.{1} = {2} (#{3})" \
            .format(self.document.name, self.field.code, str(self.value)[:40], self.id)


class DocumentFieldDetector(models.Model):
    DEF_RE_FLAGS = re.DOTALL | re.IGNORECASE

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    field = models.ForeignKey(DocumentField, blank=False, null=False,
                              related_name='field_detectors')

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._include_matchers = None
        self._exclude_matchers = None

    def compile_regexps(self):
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

        if self._exclude_matchers:
            for matcher_re in self._exclude_matchers:
                for m in matcher_re.findall(sentence):
                    return False
        if self._include_matchers:
            for matcher_re in self._include_matchers:
                for m in matcher_re.findall(sentence):
                    return True

    class Meta:
        ordering = ('uid',)

    def __str__(self):
        return "{0}: {1}".format(self.field, self.include_regexps)[:50] \
               + " (#{0})".format(self.uid)

    def __repr__(self):
        return "{0}: {1}".format(self.field, self.include_regexps)[:50] \
               + " (#{0})".format(self.uid)


class ClassifierModel(models.Model):
    document_type = models.ForeignKey(DocumentType, db_index=True, related_name='classifiers')

    document_field = models.ForeignKey(DocumentField, db_index=True, null=True, blank=True)

    trained_model = models.BinaryField(null=True, blank=True)

    def get_trained_model_obj(self) -> Union[SkLearnClassifierModel, None]:
        if not self.trained_model:
            return None
        return pickle.loads(self.trained_model)

    def set_trained_model_obj(self, obj: SkLearnClassifierModel):
        self.trained_model = pickle.dumps(obj)

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return "ClassifierModel (document_type={0})" \
            .format(self.document_type)

    def __repr__(self):
        return "ClassifierModel (id={0})".format(self.id)
