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

import os

from picklefield import PickledObjectField
from scipy.spatial.distance import _METRICS

# Django imports
from django.db import models
from django.db.models.deletion import CASCADE
from django.contrib.postgres.fields import JSONField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.dispatch import receiver
from django.utils.timezone import now

# App imports
from apps.common.file_storage import get_file_storage
from apps.document.models import Document, TextUnit
from apps.extract.models import Party
from apps.project.models import Project
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# --------------------------------------------------------------------------
# Transformer and classifier models are now in MLModel object
# --------------------------------------------------------------------------
class MLDocumentTransformerModelManager(models.Manager):
    use_in_migrations = True

    def get_queryset(self):
        return super().get_queryset().filter(apply_to='document', target_entity='transformer')


class MLTextUnitTransformerModelManager(models.Manager):
    use_in_migrations = True

    def get_queryset(self):
        return super().get_queryset().filter(apply_to='text_unit', target_entity='transformer')


class MLDocumentClassifierModelManager(models.Manager):
    use_in_migrations = True

    def get_queryset(self):
        return super().get_queryset().filter(apply_to='document', target_entity='classifier')


class MLTextUnitClassifierModelManager(models.Manager):
    use_in_migrations = True

    def get_queryset(self):
        return super().get_queryset().filter(apply_to='text_unit', target_entity='classifier')


class MLDocumentContractClassifierModelManager(models.Manager):
    use_in_migrations = True

    def get_queryset(self):
        return super().get_queryset().filter(apply_to='document', target_entity='contract_type_classifier')


class MLTextUnitContractClassifierModelManager(models.Manager):
    use_in_migrations = True

    def get_queryset(self):
        return super().get_queryset().filter(apply_to='text_unit', target_entity='contract_type_classifier')


class MLModel(models.Model):
    """
    This table stores only the path to the ML Model (pickled or even compressed)
    together with some flags.
    Document / text unit level classifiers, transformers and contract type detectors all
    use this class to access the model files.
    """
    DEFAULT_LANGUAGE = 'en'

    # Transformer / classifier name, also may contain description (model params)
    name = models.CharField(max_length=1024, db_index=True,
                            help_text='Model name, may include module parameters')

    # Transformer version, for version-tracked transformers
    version = models.CharField(max_length=1024, db_index=True,
                               help_text='Model version')

    # Name for <entity>Vector - matches <entity>UnitVector
    vector_name = models.CharField(max_length=1024, db_index=True, null=True, blank=True)

    # Serialized model object path in WebDAV
    model_path = models.CharField(max_length=1024, db_index=True, unique=True,
                                  help_text='Model path, relative to WebDAV root folder')

    # Active/valid model field used to invalidate or de-activate models
    is_active = models.BooleanField(default=True, db_index=True,
                                    help_text='Inactive models are ignored')

    # whether it's default or not
    default = models.BooleanField(default=False, db_index=True,
                                  help_text='The default model is used unless another model is deliberately selected')

    apply_to = models.CharField(
        max_length=26, db_index=True, blank=True, null=True,
        choices=[('document', 'Document'), ('text_unit', 'Text Unit')],
        help_text='Should the model be applied to documents or text units')

    target_entity = models.CharField(
        max_length=26, db_index=True, blank=True, null=True,
        choices=[('transformer', 'Transformer'),
                 ('classifier', 'Classifier'),
                 ('contract_type_classifier', 'Contract Type Classifier'),
                 ('is_contract', 'Contract / Generic Document Classifier')],
        help_text='The model class')

    # Serialized model object path in WebDAV
    language = models.CharField(max_length=12, db_index=True, blank=True, null=True,
                                help_text='Language (ISO 693-1) code, may be omitted')

    # optional project reference
    project = models.ForeignKey('project.Project', blank=True, null=True, on_delete=CASCADE, default=None,
                                help_text='Optional project reference')

    text_unit_type = models.CharField(
        max_length=26, db_index=True, blank=False, null=True,
        choices=[('sentence', 'sentence'), ('paragraph', 'paragraph')],
        help_text='Text unit type: sentence or paragraph',
        default='sentence')

    # this is the version of the CS codebase in which the model was trained
    codebase_version = models.CharField(max_length=64, db_index=True, null=True, blank=True,
                                        help_text='ContraxSuite version in which the model was created')

    # this flag is supposed to be set automatically
    # and if it's set CS won't try updating the model files
    user_modified = models.BooleanField(db_index=True, null=False, blank=False, default=False,
                                        help_text='User modified models are not automatically updated',)

    class Meta:
        unique_together = (('name', 'version', 'target_entity', 'apply_to', 'language', 'project'),)
        ordering = ('name', 'vector_name', 'target_entity', 'apply_to')

    objects = models.Manager()
    document_transformers = MLDocumentTransformerModelManager()
    textunit_transformers = MLTextUnitTransformerModelManager()
    document_classifiers = MLDocumentClassifierModelManager()
    textunit_classifiers = MLTextUnitClassifierModelManager()
    document_contract_classifiers = MLDocumentContractClassifierModelManager()
    textunit_contract_classifiers = MLTextUnitContractClassifierModelManager()

    def __str__(self):
        return f'{self.apply_to} {self.target_entity}, ' \
               f'lang="{self.language}", project={self.project}, name="{self.name}"'

    def __repr__(self):
        return self.__str__()

    def save_default(self):
        if self.default:
            self._meta.model.objects.filter(
                apply_to=self.apply_to, target_entity=self.target_entity).exclude(id=self.id).update(default=False)


@receiver(models.signals.post_save, sender=MLModel)
def save_default(sender, instance, created, **kwargs):
    instance.save_default()


# --------------------------------------------------------------------------
# Vector models
# --------------------------------------------------------------------------

class BaseVector(models.Model):
    """
    BaseVector abstract model - parent class fro DocumentVector and TextUnitVector
    # TODO: Discuss stronger "typing" of TextUnitVectors (e.g., as CHOICE field or further normalization)
    # TODO: Discuss whether we should pre-calculate TermUsage term-frequency vectors and update on TermSet update.
    """

    # Class value/label value
    vector_name = models.CharField(max_length=100, blank=True, null=True)

    # Class value/label value
    vector_value = PickledObjectField(compress=True)

    # Timestamp
    timestamp = models.DateTimeField(default=now, db_index=True)

    class Meta:
        abstract = True


class TextUnitVector(BaseVector):
    """
    TextUnitVector object model
    TextUnitVector is a class used to record the calculation of a TextUnitTransformer. This calculation
    can be set via Jupyter notebook or calculated through manual or scheduled task executing TextUnitTransformer.
    """
    # Transformer
    transformer = models.ForeignKey(MLModel, db_index=True, on_delete=CASCADE)

    # Text unit
    text_unit = models.ForeignKey(TextUnit, db_index=True, on_delete=CASCADE)

    # Text unit type, e.g., sentence, paragraph, section
    unit_type = models.CharField(max_length=128, db_index=True, blank=False, null=False)

    # Document
    document = models.ForeignKey(Document, db_index=True, on_delete=CASCADE)

    class Meta(BaseVector.Meta):
        ordering = ('text_unit', 'vector_name', 'timestamp')

    def __str__(self):
        return f'TextUnitVector (doc id={self.document_id}, t.unit={self.text_unit}, ' +\
               f'name={self.vector_name}, timestamp={self.timestamp}'


class DocumentVector(BaseVector):
    """
    DocumentVector object model
    DocumentVector is a class used to record the calculation of a MLModel.  This calculation
    can be set via Jupyter notebook or calculated through manual or scheduled task executing MLModel.
    """
    # Transformer
    transformer = models.ForeignKey(MLModel, db_index=True, on_delete=CASCADE)

    # Document FK
    document = models.ForeignKey(Document, db_index=True, on_delete=CASCADE)

    class Meta(BaseVector.Meta):
        ordering = ('document', 'vector_name', 'timestamp')

    def __str__(self):
        return "DocumentVector (document={}, vector_name={}, timestamp={}" \
            .format(self.document, self.vector_name, self.timestamp)


# --------------------------------------------------------------------------
# Classifier models
# --------------------------------------------------------------------------


class BaseClassification(models.Model):
    """
    BaseClassification object model
    Base model for TextUnitClassification and DocumentClassification models
    """
    # Class name/label name
    class_name = models.CharField(max_length=1024, db_index=True)

    # Class value/label value
    class_value = models.CharField(max_length=1024, db_index=True)

    # Timestamp
    timestamp = models.DateTimeField(default=now, db_index=True)

    # User
    user = models.ForeignKey(User, db_index=True, null=True, on_delete=CASCADE)

    class Meta:
        abstract = True


class TextUnitClassification(BaseClassification):
    """
    TextUnitClassification object model
    TextUnitClassification is a class used to record the assignment of one or more labels
    to one or more text units.  This assignment can be done by a human manually, through the
    "approval" of a TextUnitClassifierSuggestion, through Jupyter notebooks, or through the API.
    This object supports names and values up to 1024 characters, and includes user and
    timestamp auditing.
    """
    text_unit = models.ForeignKey(TextUnit, db_index=True, on_delete=CASCADE)

    class Meta(BaseClassification.Meta):
        ordering = ('text_unit', 'class_name', 'timestamp')

    def __str__(self):
        return "TextUnitClassification (text_unit={0}, class_name={1}, class_value={2}" \
            .format(self.text_unit, self.class_name, self.class_value)


class DocumentClassification(BaseClassification):
    """
    DocumentClassification object model
    DocumentClassification is a class used to record the assignment of one or more labels
    to one or more documents.  This assignment can be done by a human manually, through the
    "approval" of a DocumentClassifierSuggestion, through Jupyter notebooks, or through the API.
    This object supports names and values up to 1024 characters, and includes user and
    timestamp auditing.
    """
    document = models.ForeignKey(Document, db_index=True, on_delete=CASCADE)

    class Meta(BaseClassification.Meta):
        ordering = ('document', 'class_name', 'timestamp')

    def __str__(self):
        return "DocumentClassification (document={0}, class_name={1}, class_value={2}" \
            .format(self.document, self.class_name, self.class_value)


class BaseClassifier(models.Model):
    """
    Base class for TextUnitClassifier and DocumentClassifier object model
    Classifier is a class used to store a trained classifier.  Classifiers may be trained
    through the UI, through Jupyter notebooks, or through the API.
    # TODO: Mainline filesystem storage of very large models.
    # TODO: Mainline calibration/post-processing, e.g., isotonic/sigmoid.
    """
    # Classifier name
    name = models.CharField(max_length=1024, db_index=True)

    # Classifier version, for version-tracked classifiers
    version = models.CharField(max_length=1024, db_index=True)

    # Class name for classifier - matches TextUnitClassification and TextUnitClassifierSuggestion
    class_name = models.CharField(max_length=1024, db_index=True)

    # Serialized model object
    model_object = models.BinaryField()

    # Active/valid model field used to invalidate or de-activate models
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        unique_together = (("name", "version"),)
        ordering = ('name', 'class_name')
        abstract = True

    def __str__(self):
        return self.name


class TextUnitClassifier(BaseClassifier):
    """
    TextUnitClassifier object model
    """


class DocumentClassifier(BaseClassifier):
    """
    DocumentClassifier object model
    """


class BaseClassifierSuggestion(models.Model):
    """
    BaseClassifierSuggestion object model
    Base for TextUnitClassifierSuggestion and DocumentClassifierSuggestion models
    """
    # Run timestamp
    classifier_run = models.DateTimeField(default=now, db_index=True)

    # Classifier confidence/score/probability, depending on model and calibration
    classifier_confidence = models.FloatField(default=0.0)

    # Class name
    class_name = models.CharField(max_length=1024, db_index=True)

    # Class value
    class_value = models.CharField(max_length=1024, db_index=True)

    class Meta:
        abstract = True

    @property
    def classifier_confidence_format(self):
        return "{0:2d}%".format(int(100 * self.classifier_confidence))


class TextUnitClassifierSuggestion(BaseClassifierSuggestion):
    """
    TextUnitClassifierSuggestion object model
    TextUnitClassifierSuggestion is a class used to record the suggested classifications
    produced by a trained TextUnitClassifier.  These suggestions can be "approved" either
    automatically through workflows or with human review.
    TODO: Mainline OvR/OvO assessment.
    """
    # Classifier object
    classifier = models.ForeignKey(TextUnitClassifier, db_index=True, on_delete=CASCADE)

    # Text unit
    text_unit = models.ForeignKey(TextUnit, db_index=True, on_delete=CASCADE)

    def __str__(self):
        return "TextUnitClassifierSuggestion (classifier={0}, classifier_run={1}, text_unit={2}" \
            .format(self.classifier, self.classifier_run, self.text_unit)


class DocumentClassifierSuggestion(BaseClassifierSuggestion):
    """
    DocumentClassifierSuggestion object model
    DocumentClassifierSuggestion is a class used to record the suggested classifications
    produced by a trained DocumentClassifier.  These suggestions can be "approved" either
    automatically through workflows or with human review.
    TODO: Mainline OvR/OvO assessment.
    """
    # Classifier object
    classifier = models.ForeignKey(DocumentClassifier, db_index=True, on_delete=CASCADE)

    # Text unit
    document = models.ForeignKey(Document, db_index=True, on_delete=CASCADE)

    def __str__(self):
        return "DocumentClassifierSuggestion (classifier={0}, classifier_run={1}, document={2}" \
            .format(self.classifier, self.classifier_run, self.document)


class BaseClassifierAssessment(models.Model):
    """
    BaseClassifierAssessment object model
    Base model for TextUnitClassifierAssessment and DocumentClassifierAssessment models
    """
    # Assessment name/label
    assessment_name = models.CharField(max_length=1024, db_index=True)

    # Score/assessment value
    assessment_value = models.FloatField(default=0.0, db_index=True)

    # Assessment timestamp
    assessment_run = models.DateTimeField(default=now, db_index=True)

    class Meta:
        abstract = True

    def __str__(self):
        return "{} (classifier={}, assessment={}, value={}" \
            .format(self.__class__.__name__, self.classifier,
                    self.assessment_name, self.assessment_value)


class TextUnitClassifierAssessment(BaseClassifierAssessment):
    """
    TextUnitClassifierAssessment object model
    TextUnitClassifierAssessment is a class used to store an assessment of a trained classifier,
    for example, an F1-score or precision metric.
    TODO: Decide if we create full replication support through TextUnit FK table; expensive on TU delete.
    """
    # Classifier object
    classifier = models.ForeignKey(TextUnitClassifier, db_index=True, on_delete=CASCADE)


class DocumentClassifierAssessment(BaseClassifierAssessment):
    """
    DocumentClassifierAssessment object model
    DocumentClassifierAssessment is a class used to store an assessment of a trained classifier,
    for example, an F1-score or precision metric.
    """
    # Classifier object
    classifier = models.ForeignKey(DocumentClassifier, db_index=True, on_delete=CASCADE)


# --------------------------------------------------------------------------
# Cluster models
# --------------------------------------------------------------------------

class BaseCluster(models.Model):
    """
    BaseCluster object model
    BaseCluster is the abstract or template cluster class.  All cluster types,
    including DocumentCluster and TextUnitCluster, "inherit" from this type.
    """

    # Cluster ID
    cluster_id = models.IntegerField(default=0)

    # Cluster name
    name = models.CharField(max_length=300, db_index=True)

    # Automatically generated name, e.g., from topic models or top terms
    self_name = models.CharField(max_length=200, db_index=True)

    # Cluster description
    description = models.CharField(max_length=300, db_index=True)

    # Cluster dimension(s)
    cluster_by = models.CharField(max_length=100, db_index=True)

    # Cluster data
    using = models.CharField(max_length=20, db_index=True)

    # Create date
    created_date = models.DateTimeField(default=now, db_index=True)

    # store cluster centers, terms, etc
    metadata = JSONField(default=dict, blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ('cluster_by', 'using', 'cluster_id')


class DocumentCluster(BaseCluster):
    """
    DocumentCluster object model
    DocumentCluster extends BaseCluster for the Document type.
    """
    # Many-to-many Document set
    documents = models.ManyToManyField(Document, blank=True)

    def __str__(self):
        return '%s: %s' % (self.name, self.self_name)


class TextUnitCluster(BaseCluster):
    """
    TextUnitCluster object model
    TextUnitCluster extends BaseCluster for the TextUnit type.
    """
    # Many-to-many TextUnit set
    text_units = models.ManyToManyField(TextUnit, blank=True)

    def __str__(self):
        return '%s: %s' % (self.name, self.self_name)


# --------------------------------------------------------------------------
# Similarity models
# --------------------------------------------------------------------------


class SimilarityRun(models.Model):

    # Verbose name
    name = models.CharField(max_length=100, null=True, blank=True, db_index=True)

    project = models.ForeignKey(Project, null=True, blank=True, db_index=True, on_delete=CASCADE)

    # Create date - date of run, so should be equal for all objects from one run
    created_date = models.DateTimeField(default=now, db_index=True)

    created_by = models.ForeignKey(
        User, related_name="created_%(class)s_set", null=True, blank=True, db_index=True, on_delete=CASCADE)

    # source of features: term, date, ...., vector
    feature_source = models.CharField(max_length=50, null=True, blank=True, db_index=True)

    # threshold from 50 to 100
    similarity_threshold = models.PositiveSmallIntegerField(validators=[MinValueValidator(50), MaxValueValidator(100)],
                                                            default=75, null=True, blank=True, db_index=True)

    distance_type = models.CharField(max_length=20, choices=[(i, i) for i in _METRICS],
                                     blank=True, null=True, db_index=True)

    # param for similarity task
    use_tfidf = models.BooleanField(default=False, null=True, blank=True, db_index=True)

    # source for similarity: document, text_unit, etc
    # TODO: use FK(ContentType)?
    unit_source = models.CharField(max_length=50, null=True, blank=True, db_index=True)

    # unit type for text_unit, either other specific to item source info
    unit_type = models.CharField(max_length=50, null=True, blank=True, db_index=True)

    # item id if run was against specific item (text unit / document)
    unit_id = models.IntegerField(null=True, blank=True, db_index=True)

    class Meta:
        verbose_name_plural = 'Similarity Runs'

    def __str__(self):
        return f'{self.id}-{self.name}: {self.feature_source}: {self.created_date}'


class BaseSimilarity(models.Model):

    id = models.BigAutoField(primary_key=True)

    # Similarity value
    similarity = models.DecimalField(max_digits=5, decimal_places=2, db_index=True)

    # run id
    run = models.ForeignKey(SimilarityRun, null=True, blank=True, db_index=True, on_delete=CASCADE)

    class Meta:
        abstract = True


class DocumentSimilarity(BaseSimilarity):
    """
    DocumentSimilarity object model
    DocumentSimilarity records similarity between two documents.
    These similarities can be calculated along any dimension.
    """

    # Left or source document
    document_a = models.ForeignKey(Document, db_index=True,
                                   related_name="document_a_similarity_set", on_delete=CASCADE)

    # Right or target document
    document_b = models.ForeignKey(Document, db_index=True,
                                   related_name="document_b_similarity_set", on_delete=CASCADE)

    class Meta:
        ordering = ('document_a_id', '-similarity', 'document_b_id')
        verbose_name_plural = 'Document Similarities'

    def __str__(self):
        return f'{self.document_a_id}-{self.document_b_id} : {self.run.feature_source} : {self.similarity}'


class TextUnitSimilarity(BaseSimilarity):
    """
    TextUnitSimilarity object model
    TextUnitSimilarity records similarity between two text units.
    These similarities can be calculated along any dimension.
    """
    # Left or source text unit
    text_unit_a = models.ForeignKey(TextUnit, db_index=True,
                                    related_name="similar_text_unit_a_set",
                                    on_delete=CASCADE)

    # Right or target text unit
    text_unit_b = models.ForeignKey(TextUnit,
                                    db_index=True, related_name="similar_text_unit_b_set",
                                    on_delete=CASCADE)

    # These columns are added to avoid joining tables
    document_a = models.ForeignKey(
        Document, db_index=True, related_name="similar_document_a_set",
        on_delete=CASCADE)

    document_b = models.ForeignKey(
        Document, db_index=True, related_name="similar_document_b_set",
        on_delete=CASCADE)

    project_a = models.ForeignKey(
        Project, db_index=True, related_name="similar_project_a_set",
        on_delete=CASCADE)

    project_b = models.ForeignKey(
        Project, db_index=True, related_name="similar_project_b_set",
        on_delete=CASCADE)

    class Meta:
        ordering = ('text_unit_a_id', '-similarity', 'text_unit_b_id')
        verbose_name_plural = 'Text Unit Similarities'

    def __str__(self):
        feature_source = self.run.feature_source if self.run else 'Nothing'
        return f'{self.text_unit_a_id}-{self.text_unit_b_id} : {feature_source} : {self.similarity}'

    def save(self, **kwargs):
        if not self.document_a:
            self.document_a = self.text_unit_a.document
        if not self.project_a:
            self.project_a = self.document_a.project
        if not self.document_b:
            self.document_b = self.text_unit_b.document
        if not self.project_b:
            self.project_b = self.document_b.project
        super().save(**kwargs)


class PartySimilarity(BaseSimilarity):
    """
    PartySimilarity object model
    PartySimilarity is a class used to record similar party relationships,
    e.g., as assessed through semantic similarity, known subsidiary relationships,
    or other metadata.
    """
    # "Left" or "source" party
    party_a = models.ForeignKey(Party, db_index=True,
                                related_name="party_a_similarity_set", on_delete=CASCADE)

    # "Right" or "target" party
    party_b = models.ForeignKey(Party, db_index=True,
                                related_name="party_b_similarity_set", on_delete=CASCADE)

    class Meta:
        ordering = ('party_a_id', '-similarity', 'party_b_id')
        verbose_name_plural = 'Party Similarities'

    def __str__(self):
        return f'{self.party_a_id}-{self.party_b_id}: {self.feature_source}: {self.similarity}'
