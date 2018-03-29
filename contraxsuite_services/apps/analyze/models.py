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
# Django imports
from django.db import models
from django.utils.timezone import now

# App imports
from apps.document.models import Document, TextUnit
from apps.extract.models import Party
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.5/LICENSE"
__version__ = "1.0.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TextUnitClassification(models.Model):
    """TextUnitClassification object model

    TextUnitClassification is a class used to record the assignment of one or more labels
    to one or more text units.  This assignment can be done by a human manually, through the
    "approval" of a TextUnitClassifierSuggestion, through Jupyter notebooks, or through the API.
    This object supports names and values up to 1024 characters, and includes user and
    timestamp auditing.
    """
    # Text unit
    text_unit = models.ForeignKey(TextUnit, db_index=True)

    # Class name/label name
    class_name = models.CharField(max_length=1024, db_index=True)

    # Class value/label value
    class_value = models.CharField(max_length=1024, db_index=True)

    # Timestamp
    timestamp = models.DateTimeField(default=now, db_index=True)

    # User
    user = models.ForeignKey(User, db_index=True, null=True)

    class Meta:
        ordering = ('text_unit', 'class_name', 'timestamp')

    def __str__(self):
        return "TextUnitClassification (text_unit={0}, class_name={1}, class_value={2}" \
            .format(self.text_unit, self.class_name, self.class_value)


class TextUnitClassifier(models.Model):
    """TextUnitClassifier object model

    TextUnitClassifier is a class used to store a trained classifier.  Classifiers may be trained
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

    def __str__(self):
        return "TextUnitClassifier (name={0}, version={1}, class_name={2}" \
            .format(self.name, self.version, self.class_name)


class TextUnitClassifierSuggestion(models.Model):
    """TextUnitClassifierSuggestion object model

    TextUnitClassifierSuggestion is a class used to record the suggested classifications
    produced by a trained TextUnitClassifier.  These suggestions can be "approved" either
    automatically through workflows or with human review.

    #TODO: Mainline OvR/OvO assessment.
    """
    # Classifier object
    classifier = models.ForeignKey(TextUnitClassifier, db_index=True)

    # Run timestamp
    classifier_run = models.DateTimeField(default=now, db_index=True)

    # Classifier confidence/score/probability, depending on model and calibration
    classifier_confidence = models.FloatField(default=0.0)

    # Text unit
    text_unit = models.ForeignKey(TextUnit, db_index=True)

    # Class name
    class_name = models.CharField(max_length=1024, db_index=True)

    # Class value
    class_value = models.CharField(max_length=1024, db_index=True)

    def __str__(self):
        return "TextUnitClassifierSuggestion (classifier={0}, classifier_run={1}, text_unit={2}" \
            .format(self.classifier, self.classifier_run, self.text_unit)

    @property
    def classifier_confidence_format(self):
        return "{0:2d}%".format(int(100 * self.classifier_confidence))


class BaseCluster(models.Model):
    """BaseCluster object model

    BaseCluster is the abstract or template cluster class.  All cluster types,
    including DocumentCluster and TextUnitCluster, "inherit" from this type.
    """

    # Cluster ID
    cluster_id = models.IntegerField(default=0)

    # Cluster name
    name = models.CharField(max_length=100, db_index=True)

    # Automatically generated name, e.g., from topic models or top terms
    self_name = models.CharField(max_length=100, db_index=True)

    # Cluster description
    description = models.CharField(max_length=200, db_index=True)

    # Cluster dimension(s)
    cluster_by = models.CharField(max_length=100, db_index=True)

    # Cluster data
    using = models.CharField(max_length=20, db_index=True)

    # Create date
    created_date = models.DateTimeField(default=now, db_index=True)

    class Meta:
        abstract = True
        ordering = ('cluster_by', 'using', 'cluster_id')


class DocumentCluster(BaseCluster):
    """DocumentCluster object model

    DocumentCluster extends BaseCluster for the Document type.
    """
    # Many-to-many Document set
    documents = models.ManyToManyField(Document, blank=True)

    def __str__(self):
        return '%s: %s' % (self.name, self.self_name)


class TextUnitCluster(BaseCluster):
    """TextUnitCluster object model

    TextUnitCluster extends BaseCluster for the TextUnit type.
    """
    # Many-to-many TextUnit set
    text_units = models.ManyToManyField(TextUnit, blank=True)

    def __str__(self):
        return '%s: %s' % (self.name, self.self_name)


class DocumentSimilarity(models.Model):
    """DocumentSimilarity object model

    DocumentSimilarity records similarity between two documents.
    These similarities can be calculated along any dimension.
    """

    # Left or source document
    document_a = models.ForeignKey(Document, db_index=True,
                                   related_name="document_a_similarity_set")

    # Right or target document
    document_b = models.ForeignKey(Document, db_index=True,
                                   related_name="document_b_similarity_set")

    # Similarity
    similarity = models.DecimalField(max_digits=5, decimal_places=2)

    # Create date
    created_date = models.DateTimeField(default=now, db_index=True)

    class Meta:
        ordering = ('document_a__pk', '-similarity', 'document_b__pk')
        verbose_name_plural = 'Document Similarities'

    def __str__(self):
        return '{}-{}: {}'.format(str(self.document_a), str(self.document_b), self.similarity)


class TextUnitSimilarity(models.Model):
    """TextUnitSimilarity object model

    TextUnitSimilarity records similarity between two text units.
    These similarities can be calculated along any dimension.
    """
    # Left or source text unit
    text_unit_a = models.ForeignKey(TextUnit, db_index=True, related_name="similar_text_unit_a_set")

    # Right or target text unit
    text_unit_b = models.ForeignKey(TextUnit, db_index=True, related_name="similar_text_unit_b_set")

    # Similarity score
    similarity = models.DecimalField(max_digits=5, decimal_places=2)

    # Create date
    created_date = models.DateTimeField(default=now, db_index=True)

    class Meta:
        ordering = ('text_unit_a__pk', '-similarity', 'text_unit_b__pk')
        verbose_name_plural = 'Text Unit Similarities'

    def __str__(self):
        return '{}-{}: {}'.format(str(self.text_unit_a), str(self.text_unit_b), self.similarity)


class PartySimilarity(models.Model):
    """PartySimilarity object model

    PartySimilarity is a class used to record similar party relationships,
    e.g., as assessed through semantic similarity, known subsidiary relationships,
    or other metadata.
    """
    # "Left" or "source" party
    party_a = models.ForeignKey(Party, db_index=True,
                                related_name="party_a_similarity_set")

    # "Right" or "target" party
    party_b = models.ForeignKey(Party, db_index=True,
                                related_name="party_b_similarity_set")

    # Similarity score
    similarity = models.DecimalField(max_digits=5, decimal_places=2)

    # Create date
    created_date = models.DateTimeField(default=now, db_index=True)

    class Meta:
        ordering = ('party_a__pk', '-similarity', 'party_b__pk')
        verbose_name_plural = 'Party Similarities'

    def __str__(self):
        return '{}-{}: {}'.format(str(self.party_a), str(self.party_b), self.similarity)
