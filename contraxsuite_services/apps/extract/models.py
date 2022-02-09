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

import hashlib
import pickle
from collections import Iterable
from typing import Dict, Optional

from django.db import models
from django.db.models.deletion import CASCADE, DO_NOTHING
from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from lexnlp.config.en.company_types import CompanyDescriptor

from lexnlp.extract.common.entities.entity_banlist import EntityBanListItem

from apps.common import redis

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class Usage(models.Model):
    """
    Base usage model
    """
    text_unit = models.ForeignKey('document.TextUnit', db_index=True, on_delete=CASCADE)
    document = models.ForeignKey('document.Document', null=True, blank=True, db_index=True, on_delete=CASCADE)
    # document_name = models.CharField(max_length=1024, db_index=True, null=True)
    project = models.ForeignKey('project.Project', null=True, blank=True, db_index=True, on_delete=CASCADE)
    # project_name = models.CharField(max_length=100, db_index=True, null=True)
    count = models.IntegerField(null=False, default=0, db_index=True)

    class Meta:
        abstract = True


class ProjectUsage(models.Model):
    project = models.ForeignKey('project.Project', db_index=True, on_delete=DO_NOTHING)
    count = models.IntegerField(null=False, default=0, db_index=True)

    class Meta:
        abstract = True
        managed = False


class DocumentUsage(models.Model):
    """
    Base usage model on document level
    """
    document = models.ForeignKey('document.Document', db_index=True, on_delete=CASCADE)
    count = models.IntegerField(null=False, default=0, db_index=True)

    class Meta:
        abstract = True


class TermManager(models.Manager):
    def bulk_create(self, objs, **kwargs):
        # to update global cached terms if they are loaded via fixtures
        super().bulk_create(objs, **kwargs)
        invalidate_terms_cache()


class Term(models.Model):
    """
    Legal term/dictionary entry
    """
    term = models.CharField(max_length=1024, db_index=True)
    source = models.CharField(max_length=1024, db_index=True, null=True)
    definition_url = models.CharField(max_length=1024, null=True, verbose_name='Locale')
    tags = models.ManyToManyField(to='extract.TermTag', blank=True, db_index=True)
    objects = TermManager()

    class Meta:
        ordering = ('term', 'source')

    def __str__(self):
        return f'Term (term={self.term}, source={self.source})'


class TermTag(models.Model):
    DEFAULT_TAG = 'default'

    name = models.CharField(max_length=100, db_index=True,
                            default=DEFAULT_TAG, unique=True, blank=False)

    def __str__(self):
        return f'{self.name} #{self.pk}'

    def delete(self, **kwargs):
        if self.name == TermTag.DEFAULT_TAG:
            raise RuntimeError(f'Deleting default tag (name="{TermTag.DEFAULT_TAG}") is not allowed.')
        super().delete(**kwargs)


class CompanyTypeManager(models.Manager):
    def bulk_create(self, objs, **kwargs):
        super().bulk_create(objs, **kwargs)
        invalidate_company_type_cache()


class CompanyType(models.Model):
    """
    Legal term/dictionary entry
    """
    alias = models.CharField(max_length=512, db_index=True, unique=True)
    abbreviation = models.CharField(max_length=128, db_index=True, null=True)
    label = models.CharField(max_length=512, db_index=True, null=True)
    tags = models.ManyToManyField(to='extract.CompanyTypeTag', blank=True, db_index=True)
    objects = CompanyTypeManager()

    class Meta:
        ordering = ('alias', 'abbreviation')

    def __str__(self):
        return f'"{self.abbreviation}" "{self.alias}"'

    @classmethod
    def to_company_descriptors(cls, comp_types: 'Iterable[CompanyType]') -> Dict[str, CompanyDescriptor]:
        dct: Dict[str, CompanyDescriptor] = {}
        for c in comp_types:
            dct[c.alias] = CompanyDescriptor(c.alias, c.abbreviation, c.label)
        return dct

    @classmethod
    def get_comp_types_hash(cls, comp_types: 'Optional[Iterable[CompanyType]]') -> str:
        s = ''
        if comp_types:
            for c in comp_types:
                s += f'{c.alias}, {c.label}, {c.abbreviation};'
        return hash(s) if s else ''


class CompanyTypeTag(models.Model):
    DEFAULT_TAG = 'default'

    name = models.CharField(max_length=100, db_index=True,
                            default='', unique=True, blank=False)

    def __str__(self):
        return f'{self.name} #{self.pk}'

    def delete(self, **kwargs):
        if self.name == CompanyTypeTag.DEFAULT_TAG:
            raise RuntimeError(f'Deleting default tag (name="{CompanyTypeTag.DEFAULT_TAG}") is not allowed.')
        super().delete(**kwargs)


class TermUsage(Usage):
    """
    Legal term/dictionary usage
    """
    term = models.ForeignKey(Term, db_index=True, on_delete=CASCADE)

    class Meta:
        unique_together = (("text_unit", "term"),)
        # Warning: ordering on non-indexed fields or on multiple fields in joined tables
        # catastrophically slows down queries on large tables
        ordering = ['-count']

    def __str__(self):
        return "DocumentTermUsage (term={0}, text_unit={1}, count={2})" \
            .format(self.term, self.text_unit, self.count)


class DocumentTermUsage(DocumentUsage):
    """
    Legal term/dictionary usage
    """
    term = models.ForeignKey(Term, db_index=True, on_delete=CASCADE)

    class Meta:
        unique_together = (("document", "term"),)
        # Warning: ordering on non-indexed fields or on multiple fields in joined tables
        # catastrophically slows down queries on large tables
        ordering = ['-count']

    def __str__(self):
        return "TermUsage (term={0}, document={1}, count={2})" \
            .format(self.term, self.document, self.count)


class ProjectTermUsage(ProjectUsage):
    # to be filled with a trigger
    MATERIALIZED_PROJECT_VIEW = 'extract_projecttermusage'

    term = models.OneToOneField(Term, db_index=True, on_delete=DO_NOTHING, primary_key=True)


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
    entity_a = models.ForeignKey(GeoEntity, db_index=True, related_name="entity_a_set", on_delete=CASCADE)
    entity_b = models.ForeignKey(GeoEntity, db_index=True, related_name="entity_b_set", on_delete=CASCADE)
    relation_type = models.CharField(max_length=128, db_index=True)

    def __str__(self):
        return "GeoRelation (entity_a={0}, entity_b={1}, type={2}" \
            .format(self.entity_a, self.entity_b, self.relation_type)


class GeoAlias(models.Model):
    """
    GeoPolitical aliases
    """
    entity = models.ForeignKey(GeoEntity, db_index=True, on_delete=CASCADE)
    locale = models.CharField(max_length=10, default='en-us', db_index=True)
    alias = models.CharField(max_length=1024, db_index=True)
    type = models.CharField(max_length=1024, default='abbreviation', db_index=True)

    def __str__(self):
        return "GeoAlias (alias={0}, type={1}, entity={2}" \
            .format(self.alias, self.type, self.entity)


class GeoEntityUsage(Usage):
    """
    Geo Entity usage
    """
    entity = models.ForeignKey(GeoEntity, db_index=True, on_delete=CASCADE)

    class Meta:
        unique_together = (("text_unit", "entity"),)
        # Warning: ordering on non-indexed fields or on multiple fields in joined tables
        # catastrophically slows down queries on large tables
        ordering = ('-count',)

    def __str__(self):
        return "GeoEntityUsage (entity={0}, text_unit={1}, count={2})" \
            .format(self.entity, self.text_unit, self.count)


class ProjectGeoEntityUsage(ProjectUsage):
    # to be filled with a trigger
    MATERIALIZED_PROJECT_VIEW = 'extract_projectgeoentityusage'

    entity = models.OneToOneField(GeoEntity, db_index=True, on_delete=DO_NOTHING, primary_key=True)


class GeoAliasUsage(Usage):
    """
    Geo Alias usage
    """
    alias = models.ForeignKey(GeoAlias, db_index=True, on_delete=CASCADE)

    class Meta:
        unique_together = (("text_unit", "alias"),)
        # Warning: ordering on non-indexed fields or on multiple fields in joined tables
        # catastrophically slows down queries on large tables
        ordering = ('-count',)

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
    party = models.ForeignKey(Party, db_index=True, on_delete=CASCADE)
    role = models.CharField(max_length=1024, db_index=True, blank=True, null=True)

    class Meta:
        unique_together = (("text_unit", "party"),)
        # Warning: ordering on non-indexed fields or on multiple fields in joined tables
        # catastrophically slows down queries on large tables
        ordering = ('-count',)

    def __str__(self):
        return "PartyUsage (party={0}, role={1}, text_unit={2})" \
            .format(self.party, self.role, self.text_unit)


class ProjectPartyUsage(ProjectUsage):
    # to be filled with a trigger
    MATERIALIZED_PROJECT_VIEW = 'extract_projectpartyusage'

    party = models.OneToOneField(Party, db_index=True, on_delete=DO_NOTHING, primary_key=True)


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
    date_str = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    format = models.CharField(max_length=30, choices=FORMAT_CHOICES, default=ED, db_index=True)

    class Meta:
        unique_together = (("text_unit", "date"),)
        # Warning: ordering on non-indexed fields or on multiple fields in joined tables
        # catastrophically slows down queries on large tables
        ordering = ('-count',)

    def __str__(self):
        return "DateUsage (date={0}, text_unit={1})" \
            .format(self.date, self.text_unit)


class DefinitionUsage(Usage):
    """
    Definition usage
    """
    definition = models.TextField(db_index=True)
    definition_str = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (("text_unit", "definition"),)
        # Warning: ordering on non-indexed fields or on multiple fields in joined tables
        # catastrophically slows down queries on large tables
        ordering = ('-count',)

    def __str__(self):
        return "DefinitionUsage (definition={0}, text_unit={1})" \
            .format(self.definition, self.text_unit)


class DocumentDefinitionUsage(DocumentUsage):
    """
    Definition usage
    """
    definition = models.TextField(db_index=True)

    class Meta:
        unique_together = (("document", "definition"),)
        # Warning: ordering on non-indexed fields or on multiple fields in joined tables
        # catastrophically slows down queries on large tables
        ordering = ('-count',)

    def __str__(self):
        return "DefinitionUsage (definition={0}, document={1})" \
            .format(self.definition, self.document)


class ProjectDefinitionUsage(ProjectUsage):
    # to be filled with a trigger
    MATERIALIZED_PROJECT_VIEW = 'extract_projectdefinitionusage'
    definition = models.TextField(db_index=True, unique=True, primary_key=True)


class CopyrightUsage(Usage):
    """
    Copyright usage
    """
    year = models.CharField(max_length=10, null=True, blank=True, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    copyright_str = models.CharField(max_length=200)

    class Meta:
        unique_together = (("text_unit", "name", "year"),)
        # Warning: ordering on non-indexed fields or on multiple fields in joined tables
        # catastrophically slows down queries on large tables
        ordering = ('-count',)

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
        # Warning: ordering on non-indexed fields or on multiple fields in joined tables
        # catastrophically slows down queries on large tables
        ordering = ('-count',)

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
        # Warning: ordering on non-indexed fields or on multiple fields in joined tables
        # catastrophically slows down queries on large tables
        ordering = ('-count',)

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
    alias = models.CharField(max_length=1024, db_index=True, blank=True)

    class Meta:
        ordering = ('court_id',)

    def __str__(self):
        return "Court (id={0}, name={1}, type={2}, alias={3})" \
            .format(self.court_id, self.name, self.type, self.alias)


class CourtUsage(Usage):
    """
    Court usage
    """
    court = models.ForeignKey(Court, db_index=True, on_delete=CASCADE)

    class Meta:
        unique_together = (("text_unit", "court"),)
        # Warning: ordering on non-indexed fields or on multiple fields in joined tables
        # catastrophically slows down queries on large tables
        ordering = ('-count',)

    def __str__(self):
        return "CourtUsage (court={0}, text_unit={1})" \
            .format(self.court.name, self.text_unit)


class RegulationUsage(Usage):
    """
    Regulation usage
    """
    entity = models.ForeignKey(GeoEntity, null=True, blank=True, db_index=True, on_delete=CASCADE)
    regulation_type = models.CharField(max_length=128, db_index=True)
    regulation_name = models.CharField(max_length=1024, db_index=True)

    class Meta:
        unique_together = (("text_unit", "entity", "regulation_type"),)
        # Warning: ordering on non-indexed fields or on multiple fields in joined tables
        # catastrophically slows down queries on large tables
        ordering = ('-count',)

    def __str__(self):
        return "RegulationUsage (regulation_name={0}, text_unit={1})" \
            .format(self.regulation_name, self.text_unit)


class BaseAmountUsage(Usage):
    """
    Base Amount usage model
    """
    amount = models.FloatField(blank=True, null=True, db_index=True)
    amount_str = models.CharField(max_length=300, blank=True, null=True, db_index=True)

    class Meta:
        abstract = True
        # Warning: ordering on non-indexed fields or on multiple fields in joined tables
        # catastrophically slows down queries on large tables
        ordering = ('-amount',)

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
    usage_type = models.CharField(max_length=1024, db_index=True)
    currency = models.CharField(max_length=1024, db_index=True)

    class Meta:
        # Warning: ordering on non-indexed fields or on multiple fields in joined tables
        # catastrophically slows down queries on large tables
        ordering = ('-amount',)

    def __str__(self):
        return "CurrencyUsage (usage_type={0}, currency={1}), amount={2})" \
            .format(self.usage_type, self.currency, self.amount)


class DistanceUsage(BaseAmountUsage):
    """
    Distance usage
    """
    distance_type = models.CharField(max_length=1024, db_index=True)

    class Meta:
        # Warning: ordering on non-indexed fields or on multiple fields in joined tables
        # catastrophically slows down queries on large tables
        ordering = ('-amount',)

    def __str__(self):
        return "DistanceUsage (distance_type={0}, amount={1})" \
            .format(self.distance_type, self.amount)


class RatioUsage(BaseAmountUsage):
    """
    Ratio usage
    """
    amount2 = models.FloatField(blank=True, null=True, db_index=True)
    total = models.FloatField(blank=True, null=True, db_index=True)

    class Meta:
        # Warning: ordering on non-indexed fields or on multiple fields in joined tables
        # catastrophically slows down queries on large tables
        ordering = ('-amount',)

    def __str__(self):
        return "RatioUsage ({0} : {1})" \
            .format(self.amount, self.amount2)


class PercentUsage(BaseAmountUsage):
    """
    Percent usage
    """
    unit_type = models.CharField(max_length=1024, db_index=True)
    total = models.FloatField(blank=True, null=True, db_index=True)

    class Meta:
        # Warning: ordering on non-indexed fields or on multiple fields in joined tables
        # catastrophically slows down queries on large tables
        ordering = ('-amount',)

    def __str__(self):
        return "PercentUsage (unit_type={0}, amount={1})" \
            .format(self.unit_type, self.amount)


class DateDurationUsage(BaseAmountUsage):
    """
    Date Duration usage
    """
    duration_type = models.CharField(max_length=1024, blank=True, null=True, db_index=True)
    duration_days = models.FloatField(blank=True, null=True, db_index=True)

    class Meta:
        unique_together = (("text_unit", "amount_str"),)
        # Warning: ordering on non-indexed fields or on multiple fields in joined tables
        # catastrophically slows down queries on large tables
        ordering = ('amount',)

    def __str__(self):
        return "DateDurationUsage (amount_str={0}, text_unit={1})" \
            .format(self.amount_str, self.text_unit)


class CitationUsage(Usage):
    """
    Citation usage
    """
    volume = models.PositiveIntegerField(db_index=True)
    reporter = models.CharField(max_length=1024, db_index=True)
    reporter_full_name = models.CharField(max_length=1024, blank=True, null=True, db_index=True)
    page = models.PositiveIntegerField(db_index=True)
    page2 = models.CharField(max_length=1024, blank=True, null=True, db_index=True)
    court = models.CharField(max_length=1024, blank=True, null=True, db_index=True)
    year = models.PositiveSmallIntegerField(blank=True, null=True, db_index=True)
    citation_str = models.CharField(max_length=1024, db_index=True)

    class Meta:
        # Warning: ordering on non-indexed fields or on multiple fields in joined tables
        # catastrophically slows down queries on large tables
        ordering = ('-count',)

    def __str__(self):
        return "CitationUsage (citation_str={0}, text_unit={1})" \
            .format(self.citation_str, self.text_unit)


class BanListRecord(models.Model):
    TYPE_PARTY = 'party'
    # TYPE_COMPANY = 'company'
    TYPE_CHOICES = (
        (TYPE_PARTY, 'party'),
        # (TYPE_COMPANY, 'company'),
    )

    CACHE_KEY = 'BanListRecordAdmin_cache'
    LAST_CACHED_HASH = ''
    CACHED_DATA = None

    """
    Items (company or geoentity or ..) that should be excluded
    from location / field detecting results.
    """
    entity_type = models.CharField(max_length=128,
                                   db_index=True,
                                   choices=TYPE_CHOICES,
                                   default=TYPE_PARTY)

    pattern = models.CharField(max_length=1024, db_index=True)

    ignore_case = models.BooleanField(default=True)

    is_regex = models.BooleanField(default=True)

    trim_phrase = models.BooleanField(default=True)

    def __repr__(self):
        flags = []
        if self.ignore_case:
            flags.append('I')
        if self.is_regex:
            flags.append('Re')
        if self.trim_phrase:
            flags.append('T')
        flags_s = ' ' + ','.join(flags) if flags else ''
        return f'"{self.pattern}"{flags_s}'

    def to_banlist_item(self):
        return EntityBanListItem(
            pattern=self.pattern,
            ignore_case=self.ignore_case,
            is_regex=self.is_regex,
            trim_phrase=self.trim_phrase)

    @classmethod
    def rewrite_cache(cls):
        records = list(BanListRecord.objects.all())
        records_str = pickle.dumps(records)
        m = hashlib.md5()
        m.update(records_str)
        records_checksum = m.hexdigest()
        redis.push(f'{cls.CACHE_KEY}_data', records_str, pickle_value=False)
        redis.push(f'{cls.CACHE_KEY}_hash', records_checksum, pickle_value=False)
        cls.LAST_CACHED_HASH = records_checksum
        return records

    @classmethod
    def get_cached(cls):
        cached_key = redis.pop(f'{cls.CACHE_KEY}_hash', unpickle_value=False)
        if cls.CACHED_DATA:
            if cached_key == cls.LAST_CACHED_HASH:
                return cls.CACHED_DATA
        cls.CACHED_DATA = redis.pop(f'{cls.CACHE_KEY}_data', unpickle_value=True)
        if cls.CACHED_DATA is None:
            return cls.rewrite_cache()
        cls.LAST_CACHED_HASH = cached_key
        return cls.CACHED_DATA

    def save(self, **kwargs):
        super().save(**kwargs)
        BanListRecord.rewrite_cache()

    def delete(self, **kwargs):
        super().delete(**kwargs)
        BanListRecord.rewrite_cache()


@receiver(pre_delete, sender=BanListRecord)
def on_banlist_record_delete(instance, **kwargs):
    BanListRecord.rewrite_cache()


@receiver(post_save, sender=Term)
def cache_term(instance, **kwargs):
    invalidate_terms_cache()


@receiver(post_delete, sender=Term)
def delete_cached_term(instance, **kwargs):
    invalidate_terms_cache()


def invalidate_terms_cache():
    from apps.extract.term_stems import TermStemsCache
    TermStemsCache.invalidate()


@receiver(post_save, sender=CompanyType)
def cache_company_types(instance, **kwargs):
    invalidate_company_type_cache()


@receiver(post_delete, sender=CompanyType)
def delete_cached_company_types(instance, **kwargs):
    invalidate_company_type_cache()


def invalidate_company_type_cache():
    from apps.extract.company_types import CompanyTypeCache
    CompanyTypeCache.invalidate()
