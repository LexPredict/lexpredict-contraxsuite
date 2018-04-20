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
from django.db import models

from apps.document.models import TextUnit

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.8/LICENSE"
__version__ = "1.0.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class Usage(models.Model):
    """
    Base usage model
    """
    text_unit = models.ForeignKey(TextUnit, db_index=True)
    count = models.IntegerField(null=False, default=0)

    class Meta:
        abstract = True


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


class TermUsage(Usage):
    """
    Legal term/dictionary usage
    """
    term = models.ForeignKey(Term, db_index=True)

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
    priority = models.IntegerField(null=True, blank=True)
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


class GeoEntityUsage(Usage):
    """
    Geo Entity usage
    """
    entity = models.ForeignKey(GeoEntity, db_index=True)

    class Meta:
        unique_together = (("text_unit", "entity"),)
        ordering = ('text_unit', '-count', 'entity')

    def __str__(self):
        return "GeoEntityUsage (entity={0}, text_unit={1}, count={2})" \
            .format(self.entity, self.text_unit, self.count)


class GeoAliasUsage(Usage):
    """
    Geo Alias usage
    """
    alias = models.ForeignKey(GeoAlias, db_index=True)

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
    type = models.CharField(max_length=1024, blank=True, null=True, db_index=True)
    type_abbr = models.CharField(max_length=30, blank=True, null=True, db_index=True)
    type_label = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    type_description = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    description = models.TextField(null=True)

    class Meta:
        unique_together = (("name", "type_abbr"),)
        verbose_name_plural = 'Parties'
        ordering = ('name', 'type')

    def __str__(self):
        return "Party (name={0}, type={1}, description={2}" \
            .format(self.name, self.type, self.description)


class PartyUsage(Usage):
    """
    Party usage
    """
    party = models.ForeignKey(Party, db_index=True)
    role = models.CharField(max_length=1024, db_index=True, blank=True, null=True)

    class Meta:
        unique_together = (("text_unit", "party"),)
        ordering = ('text_unit', '-count', 'party')

    def __str__(self):
        return "PartyUsage (party={0}, role={1}, text_unit={2})" \
            .format(self.party, self.role, self.text_unit)


class DateUsage(Usage):
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

    date = models.DateField(db_index=True)
    date_str = models.CharField(max_length=128, blank=True, null=True)
    format = models.CharField(max_length=30, choices=FORMAT_CHOICES, default=ED, db_index=True)

    class Meta:
        unique_together = (("text_unit", "date"),)
        ordering = ('text_unit', 'date', '-count')

    def __str__(self):
        return "DateUsage (date={0}, text_unit={1})" \
            .format(self.date, self.text_unit)


class DefinitionUsage(Usage):
    """
    Definition usage
    """
    definition = models.CharField(max_length=128, db_index=True)
    definition_str = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        unique_together = (("text_unit", "definition"),)
        ordering = ('text_unit', '-count', 'definition')

    def __str__(self):
        return "DefinitionUsage (definition={0}, text_unit={1})" \
            .format(self.definition, self.text_unit)


class CopyrightUsage(Usage):
    """
    Copyright usage
    """
    year = models.CharField(max_length=10, null=True, blank=True, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    copyright_str = models.CharField(max_length=200)

    class Meta:
        unique_together = (("text_unit", "name", "year"),)
        ordering = ('text_unit', '-count', 'name')

    def __str__(self):
        return "CopyrightUsage (copyright={0}, text_unit={1})" \
            .format(self.copyright_str, self.text_unit)


class TrademarkUsage(Usage):
    """
    Trademark usage
    """
    trademark = models.CharField(max_length=200, db_index=True)

    class Meta:
        unique_together = (("text_unit", "trademark"),)
        ordering = ('text_unit', '-count', 'trademark')

    def __str__(self):
        return "TrademarkUsage (trademark={0}, text_unit={1})" \
            .format(self.trademark, self.text_unit)


class UrlUsage(Usage):
    """
    Url usage
    """
    source_url = models.CharField(max_length=1000, db_index=True)

    class Meta:
        unique_together = (("text_unit", "source_url"),)
        ordering = ('text_unit', '-count', 'source_url')

    def __str__(self):
        return "UrlUsage (source_url={0}, text_unit={1})" \
            .format(self.source_url, self.text_unit)


class Court(models.Model):
    """
    Courts
    """
    court_id = models.IntegerField(default=0)
    type = models.CharField(max_length=30, db_index=True)
    name = models.CharField(max_length=1024, db_index=True)
    level = models.CharField(max_length=30, db_index=True, blank=True)
    jurisdiction = models.CharField(max_length=30, db_index=True, blank=True)
    alias = models.CharField(max_length=100, db_index=True, blank=True)

    class Meta:
        ordering = ('court_id',)

    def __str__(self):
        return "Court (id={0}, name={1}, type={2}, alias={3})" \
            .format(self.court_id, self.name, self.type, self.alias)


class CourtUsage(Usage):
    """
    Court usage
    """
    court = models.ForeignKey(Court, db_index=True)

    class Meta:
        unique_together = (("text_unit", "court"),)
        ordering = ('text_unit', '-count', 'court')

    def __str__(self):
        return "CourtUsage (court={0}, text_unit={1})" \
            .format(self.court.name, self.text_unit)


class RegulationUsage(Usage):
    """
    Regulation usage
    """
    entity = models.ForeignKey(GeoEntity, null=True, blank=True, db_index=True)
    regulation_type = models.CharField(max_length=128, db_index=True)
    regulation_name = models.CharField(max_length=1024, db_index=True)

    class Meta:
        unique_together = (("text_unit", "entity", "regulation_type"),)
        ordering = ('text_unit', '-count', 'regulation_type', 'entity')

    def __str__(self):
        return "RegulationUsage (regulation_name={0}, text_unit={1})" \
            .format(self.regulation_name, self.text_unit)


class BaseAmountUsage(Usage):
    """
    Base Amount usage model
    """
    amount = models.FloatField(blank=True, null=True)
    amount_str = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ('text_unit', '-amount', 'count')

    def save(self, *args, **kwargs):
        if self.amount_str:
            self.amount_str = self.amount_str[:300]
        super().save(*args, **kwargs)


class AmountUsage(BaseAmountUsage):
    """
    Amount usage
    """
    def __str__(self):
        return "AmountUsage (amount={})" \
            .format(self.amount)


class CurrencyUsage(BaseAmountUsage):
    """
    Currency usage
    """
    usage_type = models.CharField(max_length=20, db_index=True)
    currency = models.CharField(max_length=20, db_index=True)

    class Meta:
        ordering = ('text_unit', 'usage_type', 'currency', '-amount')

    def __str__(self):
        return "CurrencyUsage (usage_type={0}, currency={1}), amount={2})" \
            .format(self.usage_type, self.currency, self.amount)


class DistanceUsage(BaseAmountUsage):
    """
    Distance usage
    """
    distance_type = models.CharField(max_length=20, db_index=True)

    class Meta:
        ordering = ('text_unit', 'distance_type', '-amount')

    def __str__(self):
        return "DistanceUsage (distance_type={0}, amount={1})" \
            .format(self.distance_type, self.amount)


class RatioUsage(BaseAmountUsage):
    """
    Ratio usage
    """
    amount2 = models.FloatField(blank=True, null=True)
    total = models.FloatField(blank=True, null=True)

    class Meta:
        ordering = ('text_unit', '-amount', '-amount2')

    def __str__(self):
        return "RatioUsage ({0} : {1})" \
            .format(self.amount, self.amount2)


class PercentUsage(BaseAmountUsage):
    """
    Percent usage
    """
    unit_type = models.CharField(max_length=20, db_index=True)
    total = models.FloatField(blank=True, null=True)

    class Meta:
        ordering = ('text_unit', 'unit_type', '-amount')

    def __str__(self):
        return "PercentUsage (unit_type={0}, amount={1})" \
            .format(self.unit_type, self.amount)


class DateDurationUsage(BaseAmountUsage):
    """
    Date Duration usage
    """
    duration_type = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    duration_days = models.FloatField(blank=True, null=True)

    class Meta:
        unique_together = (("text_unit", "amount_str"),)
        ordering = ('text_unit', 'amount', '-count')

    def __str__(self):
        return "DateDurationUsage (amount_str={0}, text_unit={1})" \
            .format(self.amount_str, self.text_unit)


class CitationUsage(Usage):
    """
    Citation usage
    """
    volume = models.PositiveSmallIntegerField()
    reporter = models.CharField(max_length=20, db_index=True)
    reporter_full_name = models.CharField(max_length=200, blank=True, null=True, db_index=True)
    page = models.PositiveSmallIntegerField()
    page2 = models.CharField(max_length=10, blank=True, null=True)
    court = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    year = models.PositiveSmallIntegerField(blank=True, null=True, db_index=True)
    citation_str = models.CharField(max_length=100)

    class Meta:
        ordering = ('text_unit', 'reporter', '-count')

    def __str__(self):
        return "CitationUsage (citation_str={0}, text_unit={1})" \
            .format(self.citation_str, self.text_unit)
