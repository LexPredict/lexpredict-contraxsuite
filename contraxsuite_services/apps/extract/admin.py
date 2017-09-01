# -*- coding: utf-8 -*-

# Django imports
from django.contrib import admin

# Project imports
from apps.extract.models import (
    Court, CourtUsage, CurrencyUsage,
    DateDurationUsage, DateUsage, DefinitionUsage,
    GeoAlias, GeoAliasUsage, GeoEntity, GeoEntityUsage, GeoRelation,
    Term, TermUsage, Party, PartyUsage)

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.1/LICENSE"
__version__ = "1.0.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class CourtAdmin(admin.ModelAdmin):
    list_display = ('type', 'name', 'abbreviation')
    search_fields = ('name', 'abbreviation')


class CourtUsageAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'court', 'count')
    search_fields = ('text_unit__text', 'court__name')


class CurrencyUsageAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'usage_type', 'currency', 'amount')
    search_fields = ('currency',)


class DateDurationUsageAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'duration', 'duration_str', 'count')
    search_fields = ('duration', 'duration_str')


class DateUsageAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'date', 'format', 'count')
    search_fields = ('date', 'format')


class DefinitionUsageAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'definition', 'count')
    search_fields = ('definition',)


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


admin.site.register(Court, CourtAdmin)
admin.site.register(CourtUsage, CourtUsageAdmin)
admin.site.register(CurrencyUsage, CurrencyUsageAdmin)
admin.site.register(DateDurationUsage, DateDurationUsageAdmin)
admin.site.register(DateUsage, DateUsageAdmin)
admin.site.register(DefinitionUsage, DefinitionUsageAdmin)
admin.site.register(GeoAlias, GeoAliasAdmin)
admin.site.register(GeoAliasUsage, GeoAliasUsageAdmin)
admin.site.register(GeoEntity, GeoEntityAdmin)
admin.site.register(GeoEntityUsage, GeoEntityUsageAdmin)
admin.site.register(GeoRelation, GeoRelationAdmin)
admin.site.register(Term, TermAdmin)
admin.site.register(TermUsage, TermUsageAdmin)
admin.site.register(Party)
admin.site.register(PartyUsage)
