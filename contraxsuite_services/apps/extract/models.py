from django.contrib.postgres.fields import JSONField
from django.db import models

from apps.document.models import TextUnit

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.1/LICENSE"
__version__ = "1.0.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class Term(models.Model):
    """
    Legal term/dictionary entry
    """
    term = models.CharField(max_length=1024, db_index=True)
    source = models.CharField(max_length=128, db_index=True, null=True)
    definition_url = models.CharField(max_length=1024, null=True)

    class Meta:
        ordering = ('term', 'source')

    def __str__(self):
        return "Term (term={0}, source={1})" \
            .format(self.term, self.source)


class TermUsage(models.Model):
    """
    Legal term/dictionary usage
    """
    text_unit = models.ForeignKey(TextUnit, db_index=True)
    term = models.ForeignKey(Term, db_index=True)
    count = models.IntegerField(null=False)

    class Meta:
        unique_together = (("text_unit", "term"),)
        ordering = ['-count', 'term__term']

    def __str__(self):
        return "TermUsage (term={0}, text_unit={1}, count={2})" \
            .format(self.term, self.text_unit, self.count)


class GeoEntity(models.Model):
    """
    Entity, e.g., geographic or political
    """
    entity_id = models.PositiveSmallIntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=1024, db_index=True)
    category = models.CharField(max_length=1024, db_index=True)
    description = models.TextField(null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    class Meta:
        unique_together = (("name", "category"),)
        verbose_name_plural = 'Geo Entities'
        ordering = ('name', 'entity_id', 'category')

    def __str__(self):
        return "GeoEntity (id={0}, name={1}, category={2}" \
            .format(self.entity_id, self.name, self.category)


class GeoRelation(models.Model):
    """
    GeoPolitical Entity relation
    """
    entity_a = models.ForeignKey(GeoEntity, db_index=True, related_name="entity_a_set")
    entity_b = models.ForeignKey(GeoEntity, db_index=True, related_name="entity_b_set")
    relation_type = models.CharField(max_length=128, db_index=True)

    def __str__(self):
        return "GeoRelation (entity_a={0}, entity_b={1}, type={2}" \
            .format(self.entity_a, self.entity_b, self.relation_type)


class GeoAlias(models.Model):
    """
    GeoPolitical aliases
    """
    entity = models.ForeignKey(GeoEntity, db_index=True)
    locale = models.CharField(max_length=10, default='en-us', db_index=True)
    alias = models.CharField(max_length=1024, db_index=True)
    type = models.CharField(max_length=20, default='abbreviation', db_index=True)

    def __str__(self):
        return "GeoAlias (alias={0}, type={1}, entity={2}" \
            .format(self.alias, self.type, self.entity)


class GeoEntityUsage(models.Model):
    """
    Geo Entity usage
    """
    text_unit = models.ForeignKey(TextUnit, db_index=True)
    entity = models.ForeignKey(GeoEntity, db_index=True)
    count = models.IntegerField(null=False)

    class Meta:
        unique_together = (("text_unit", "entity"),)
        ordering = ('text_unit', '-count', 'entity')

    def __str__(self):
        return "GeoEntityUsage (entity={0}, text_unit={1}, count={2})" \
            .format(self.entity, self.text_unit, self.count)


class GeoAliasUsage(models.Model):
    """
    Geo Alias usage
    """
    text_unit = models.ForeignKey(TextUnit, db_index=True)
    alias = models.ForeignKey(GeoAlias, db_index=True)
    count = models.IntegerField(null=False)

    class Meta:
        unique_together = (("text_unit", "alias"),)
        ordering = ('text_unit', '-count', 'alias')

    def __str__(self):
        return "GeoAliasUsage (alias={0}, text_unit={1}, count={2})" \
            .format(self.alias, self.text_unit, self.count)


class Party(models.Model):
    """
    Party, e.g., person or company
    """
    name = models.CharField(max_length=1024, db_index=True)
    type = models.CharField(max_length=1024, db_index=True)
    description = models.TextField(null=True)

    class Meta:
        unique_together = (("name", "type"),)
        verbose_name_plural = 'Parties'
        ordering = ('name', 'type')

    def __str__(self):
        return "Party (name={0}, type={1}, description={2}" \
            .format(self.name, self.type, self.description)


class PartyUsage(models.Model):
    """
    Party usage
    """
    text_unit = models.ForeignKey(TextUnit, db_index=True)
    party = models.ForeignKey(Party, db_index=True)
    role = models.CharField(max_length=1024, db_index=True, blank=True, null=True)
    count = models.IntegerField(null=False, default=0)

    class Meta:
        unique_together = (("text_unit", "party"),)
        ordering = ('text_unit', '-count', 'party')

    def __str__(self):
        return "PartyUsage (party={0}, role={1}, text_unit={2})" \
            .format(self.party, self.role, self.text_unit)


class DateUsage(models.Model):
    """
    Date usage
    """
    ED = 'exact_date'
    WD = 'without_day'
    WY = 'without_year'
    FORMAT_CHOICES = (
        (ED, ED),
        (WD, WD),
        (WY, WY)
    )

    text_unit = models.ForeignKey(TextUnit, db_index=True)
    date = models.DateField(db_index=True)
    format = models.CharField(max_length=30, choices=FORMAT_CHOICES, default=ED, db_index=True)
    count = models.IntegerField(null=False, default=0)

    class Meta:
        unique_together = (("text_unit", "date"),)
        ordering = ('text_unit', 'date', '-count')

    def __str__(self):
        return "DateUsage (date={0}, text_unit={1})" \
            .format(self.date, self.text_unit)


class DateDurationUsage(models.Model):
    """
    Date Duration usage
    """
    text_unit = models.ForeignKey(TextUnit, db_index=True)
    duration = models.DurationField(db_index=True)
    duration_str = models.CharField(max_length=20, db_index=True)
    count = models.IntegerField(null=False, default=0)

    class Meta:
        unique_together = (("text_unit", "duration_str"),)
        ordering = ('text_unit', 'duration', '-count')

    def __str__(self):
        return "DateDurationUsage (duration={0}, text_unit={1})" \
            .format(self.duration, self.text_unit)


class DefinitionUsage(models.Model):
    """
    Definition usage
    """
    text_unit = models.ForeignKey(TextUnit, db_index=True)
    definition = models.CharField(max_length=128, db_index=True)
    count = models.IntegerField(null=False, default=0)

    class Meta:
        unique_together = (("text_unit", "definition"),)
        ordering = ('text_unit', '-count', 'definition')

    def __str__(self):
        return "DefinitionUsage (definition={0}, text_unit={1})" \
            .format(self.definition, self.text_unit)


class Court(models.Model):
    """
    Courts
    """
    court_id = models.IntegerField(default=0)
    type = models.CharField(max_length=30, db_index=True)
    name = models.CharField(max_length=1024, db_index=True)
    abbreviation = models.CharField(max_length=100, db_index=True, blank=True)

    class Meta:
        ordering = ('court_id',)

    def __str__(self):
        return "Court (id={0}, name={1}, type={2}, abbr={3})" \
            .format(self.court_id, self.name, self.type, self.abbreviation)


class CourtUsage(models.Model):
    """
    Court usage
    """
    text_unit = models.ForeignKey(TextUnit, db_index=True)
    court = models.ForeignKey(Court, db_index=True)
    count = models.IntegerField(null=False, default=0)

    class Meta:
        unique_together = (("text_unit", "court"),)
        ordering = ('text_unit', '-count', 'court')

    def __str__(self):
        return "CourtUsage (court={0}, text_unit={1})" \
            .format(self.court.name, self.text_unit)


class RegulationUsage(models.Model):
    """
    Regulation usage
    """
    text_unit = models.ForeignKey(TextUnit, db_index=True)
    entity = models.ForeignKey(GeoEntity, db_index=True)
    regulation_type = models.CharField(max_length=128, db_index=True)
    regulation_name = models.CharField(max_length=1024, db_index=True)
    count = models.IntegerField(null=False, default=0)

    class Meta:
        unique_together = (("text_unit", "entity", "regulation_type"),)
        ordering = ('text_unit', '-count', 'regulation_type', 'entity')

    def __str__(self):
        return "RegulationUsage (regulation={0}, text_unit={1})" \
            .format(self.regulation, self.text_unit)


class CurrencyUsage(models.Model):
    """
    Currency usage
    """
    text_unit = models.ForeignKey(TextUnit, db_index=True)
    usage_type = models.CharField(max_length=20, db_index=True)
    currency = models.CharField(max_length=20, db_index=True)
    amount = JSONField(blank=True, null=True)

    class Meta:
        ordering = ('text_unit', 'usage_type', 'currency', '-amount')

    def __str__(self):
        return "CurrencyUsage (usage_type={0}, currency={1}, amount={2})" \
            .format(self.usage_type, self.currency, self.amount)
