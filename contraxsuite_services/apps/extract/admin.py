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

# Django imports
from django.contrib import admin

# Project imports
from apps.extract.models import (
    AmountUsage, CitationUsage, CopyrightUsage, Court, CourtUsage, CurrencyUsage,
    DateDurationUsage, DateUsage, DefinitionUsage, DistanceUsage,
    GeoAlias, GeoAliasUsage, GeoEntity, GeoEntityUsage, GeoRelation,
    Party, PartyUsage, PercentUsage, RatioUsage, RegulationUsage,
    Term, TermUsage, TrademarkUsage, UrlUsage)

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.8/LICENSE"
__version__ = "1.1.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class CourtAdmin(admin.ModelAdmin):
    list_display = ('type', 'name', 'alias')
    search_fields = ('name', 'alias')


class CourtUsageAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'court', 'count')
    search_fields = ('text_unit__text', 'court__name')


class CitationUsageAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'citation_str', 'count')
    search_fields = ('text_unit__text', 'citation_str')


class CopyrightUsageAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'copyright_str', 'count')
    search_fields = ('text_unit__text', 'copyright_str')


class CurrencyUsageAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'usage_type', 'currency', 'amount')
    search_fields = ('currency',)


class DateDurationUsageAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'amount', 'amount_str', 'count')
    search_fields = ('amount', 'amount_str')


class DateUsageAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'date', 'format', 'count')
    search_fields = ('date', 'format')


class AmountUsageAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'amount', 'amount_str', 'count')
    search_fields = ('amount', 'amount_str')


class DistanceUsageAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'distance_type', 'amount', 'count')
    search_fields = ('definition',)


class PercentUsageAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'amount', 'unit_type', 'count')
    search_fields = ('amount', 'unit_type')


class RatioUsageAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'amount', 'amount2', 'count')
    search_fields = ('amount', 'amount2')


class DefinitionUsageAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'definition', 'count')
    search_fields = ('definition',)


class RegulationUsageAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'regulation_name', 'regulation_type', 'count')
    search_fields = ('regulation_name',)


class GeoAliasAdmin(admin.ModelAdmin):
    list_display = ('alias', 'type')
    search_fields = ('alias', 'type')


class GeoAliasUsageAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'alias', 'count')
    search_fields = ('text_unit__text', 'alias__alias')


class GeoEntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name', 'category')


class GeoEntityUsageAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'entity', 'count')
    search_fields = ('text_unit__text', 'entity__name')


class GeoRelationAdmin(admin.ModelAdmin):
    list_display = ('entity_a', 'entity_b', 'relation_type')
    search_fields = ('entity_a__name', 'entity_b__name', 'relation_type')


class TermAdmin(admin.ModelAdmin):
    list_display = ('term', 'source', 'definition_url')
    search_fields = ('term', 'source', 'definition_url')


class TermUsageAdmin(admin.ModelAdmin):
    list_display = ('term', 'count')
    search_fields = ('term', 'count')


class TrademarkUsageAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'trademark', 'count')
    search_fields = ('text_unit__text', 'trademark')


class UrlUsageAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'source_url', 'count')
    search_fields = ('text_unit__text', 'source_url')


admin.site.register(AmountUsage, AmountUsageAdmin)
admin.site.register(CitationUsage, CitationUsageAdmin)
admin.site.register(CopyrightUsage, CopyrightUsageAdmin)
admin.site.register(Court, CourtAdmin)
admin.site.register(CourtUsage, CourtUsageAdmin)
admin.site.register(CurrencyUsage, CurrencyUsageAdmin)
admin.site.register(DateDurationUsage, DateDurationUsageAdmin)
admin.site.register(DateUsage, DateUsageAdmin)
admin.site.register(DefinitionUsage, DefinitionUsageAdmin)
admin.site.register(DistanceUsage, DistanceUsageAdmin)
admin.site.register(GeoAlias, GeoAliasAdmin)
admin.site.register(GeoAliasUsage, GeoAliasUsageAdmin)
admin.site.register(GeoEntity, GeoEntityAdmin)
admin.site.register(GeoEntityUsage, GeoEntityUsageAdmin)
admin.site.register(GeoRelation, GeoRelationAdmin)
admin.site.register(Party)
admin.site.register(PartyUsage)
admin.site.register(PercentUsage, PercentUsageAdmin)
admin.site.register(RatioUsage, RatioUsageAdmin)
admin.site.register(RegulationUsage, RegulationUsageAdmin)
admin.site.register(Term, TermAdmin)
admin.site.register(TermUsage, TermUsageAdmin)
admin.site.register(TrademarkUsage, TrademarkUsageAdmin)
admin.site.register(UrlUsage, UrlUsageAdmin)
