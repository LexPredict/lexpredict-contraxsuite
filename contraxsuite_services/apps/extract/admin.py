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
from collections import Set
from typing import List, Tuple, Dict, Any

from django.contrib import admin
from django.db.models import F, Q, QuerySet

# Project imports
from django.utils.html import escape
from django.utils.safestring import mark_safe

from apps.common.querysets import CustomCountQuerySet, stringify_queryset
from apps.common.utils import full_reverse
from apps.document.models import TextUnit
from apps.extract.models import (
    AmountUsage, CitationUsage, CopyrightUsage, Court, CourtUsage, CurrencyUsage,
    DateDurationUsage, DateUsage, DefinitionUsage, DistanceUsage,
    GeoAlias, GeoAliasUsage, GeoEntity, GeoEntityUsage, GeoRelation,
    Party, PartyUsage, PercentUsage, RatioUsage, RegulationUsage,
    Term, TermUsage, TrademarkUsage, UrlUsage, DocumentTermUsage, DocumentDefinitionUsage)

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TextUnitUsageAdminBase(admin.ModelAdmin):
    raw_id_fields = ('text_unit',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('text_unit', 'text_unit__document', 'text_unit__textunittext')


class CourtAdmin(admin.ModelAdmin):
    list_display = ('type', 'name', 'alias')
    search_fields = ('name', 'alias')


class CourtUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'court', 'count')
    search_fields = ('text_unit__textunittext__text', 'court__name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('court')


class CitationUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'citation_str', 'count')
    search_fields = ('text_unit__textunittext__text', 'citation_str')


class CopyrightUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'copyright_str', 'count')
    search_fields = ('text_unit__textunittext__text', 'copyright_str')


class CurrencyUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'usage_type', 'currency', 'amount')
    search_fields = ('currency',)


class DateDurationUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'amount', 'amount_str', 'count')
    search_fields = ('amount', 'amount_str')


class DateUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'date', 'format', 'count')
    search_fields = ('date', 'format')


class AmountUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'amount', 'amount_str', 'count')
    search_fields = ('amount', 'amount_str')


class DistanceUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'distance_type', 'amount', 'count')
    search_fields = ('definition',)


class PercentUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'amount', 'unit_type', 'count')
    search_fields = ('amount', 'unit_type')


class RatioUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'amount', 'amount2', 'count')
    search_fields = ('amount', 'amount2')


class DefinitionUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'definition', 'count')
    search_fields = ('definition',)


class DocumentDefinitionUsageAdmin(admin.ModelAdmin):
    list_display = ('document', 'definition', 'count')
    search_fields = ('definition', 'document')

    def get_queryset(self, request):
        qs = admin.ModelAdmin.get_queryset(self, request)
        qs = qs.only('id', 'document_id', 'count', 'definition')
        return qs


class RegulationUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'regulation_name', 'regulation_type', 'count')
    search_fields = ('regulation_name',)


class GeoAliasAdmin(admin.ModelAdmin):
    list_display = ('alias', 'type')
    search_fields = ('alias', 'type')


class GeoAliasUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'alias', 'count')
    search_fields = ('text_unit__textunittext__text', 'alias__alias')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('alias', 'alias__entity')


class GeoEntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name', 'category')


class GeoEntityUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'entity', 'count')
    search_fields = ('text_unit__textunittext__text', 'entity__name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('entity')


class GeoRelationAdmin(admin.ModelAdmin):
    list_display = ('entity_a', 'entity_b', 'relation_type')
    search_fields = ('entity_a__name', 'entity_b__name', 'relation_type')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('entity_a', 'entity_b')


class TermAdmin(admin.ModelAdmin):
    list_display = ('term', 'source', 'definition_url')
    search_fields = ('term', 'source', 'definition_url')


class TermUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('term_data', 'document_ref', 'unit_type', 'count',)
    search_fields = ('term', 'count',)
    last_request = None
    LIMIT_QUERY = 100000

    def get_queryset(self, request):
        self.last_request = request
        # qs = admin.ModelAdmin.get_queryset(self, request)
        qs = TermUsage.objects.all()
        if 'q' in request.GET:
            # searching by count?
            request.GET = request.GET.copy()
            query_text = request.GET.pop('q')
            query_text = query_text[0] if query_text else ''
            if query_text:
                queries = Q(term__term__icontains=query_text) | \
                          Q(document__name__icontains=query_text) | \
                          Q(document__project__name__icontains=query_text)
                if query_text.isdigit():
                    queries |= (Q(count__gt=int(query_text) - 1))
                qs = qs.filter(queries)
        qs = qs.only('id', 'text_unit_id', 'count', 'term')
        qs = self.filter_count_predicate(qs)
        return qs

    def filter_count_predicate(self, qs: QuerySet) -> CustomCountQuerySet:
        inner_query = stringify_queryset(qs)
        qs = CustomCountQuerySet.wrap(qs)  # type: CustomCountQuerySet
        full_query = f'SELECT COUNT(text_unit_id) FROM ({inner_query} LIMIT {self.LIMIT_QUERY}) AS temp;'
        qs.set_optional_count_query(full_query)
        return qs

    def term_data(self, obj):
        term = obj.term
        url = self.full_reverse('extract:term-usage-list') + '?term_search=' + term.term
        return mark_safe(f'<a href="{url}"><i class="fa fa-external-link"></i>{escape(term.term)}</a>')

    term_data.short_description = 'Term'
    term_data.admin_order_field = 'term__term'

    def document_ref(self, obj):
        document = obj.document
        url = self.full_reverse('document:document-detail', args=[document.pk])
        return mark_safe(f'<a href="{url}"><i class="fa fa-external-link"></i>{escape(document.name)}</a>')

    document_ref.short_description = 'Document'
    document_ref.admin_order_field = 'document__name'

    def unit_type(self, obj):
        unit = obj.text_unit  # type: TextUnit
        unit_text = unit.text or ''
        if len(unit_text) > 60:
            unit_text = unit_text[:57] + '...'
        url = self.full_reverse('document:text-unit-detail', args=[unit.pk])
        return mark_safe(f'<a href="{url}"><i class="fa fa-external-link"></i>{escape(unit_text)}</a>')

    unit_type.short_description = 'Unit'
    unit_type.admin_order_field = 'text_unit__unit_type'

    def full_reverse(self, *args, **kwargs):
        return full_reverse(*args, **kwargs, request=self.last_request)


class DocumentTermUsageAdmin(admin.ModelAdmin):
    list_display = ('term', 'document', 'count')
    search_fields = ('term', 'document')

    def get_queryset(self, request):
        qs = admin.ModelAdmin.get_queryset(self, request)
        qs = qs.only('id', 'document_id', 'count', 'term').select_related('term')
        return qs


class TrademarkUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'trademark', 'count')
    search_fields = ('text_unit__textunittext__text', 'trademark')


class UrlUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'source_url', 'count')
    search_fields = ('text_unit__textunittext__text', 'source_url')


class PartyUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'party_name', 'count')
    search_fields = ('text_unit__textunittext__text', 'party__name')

    @staticmethod
    def party_name(obj):
        return obj.party_name

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(party_name=F('party__name'))
        return qs.select_related('party')


admin.site.register(AmountUsage, AmountUsageAdmin)
admin.site.register(CitationUsage, CitationUsageAdmin)
admin.site.register(CopyrightUsage, CopyrightUsageAdmin)
admin.site.register(Court, CourtAdmin)
admin.site.register(CourtUsage, CourtUsageAdmin)
admin.site.register(CurrencyUsage, CurrencyUsageAdmin)
admin.site.register(DateDurationUsage, DateDurationUsageAdmin)
admin.site.register(DateUsage, DateUsageAdmin)
admin.site.register(DefinitionUsage, DefinitionUsageAdmin)
admin.site.register(DocumentDefinitionUsage, DocumentDefinitionUsageAdmin)
admin.site.register(DistanceUsage, DistanceUsageAdmin)
admin.site.register(GeoAlias, GeoAliasAdmin)
admin.site.register(GeoAliasUsage, GeoAliasUsageAdmin)
admin.site.register(GeoEntity, GeoEntityAdmin)
admin.site.register(GeoEntityUsage, GeoEntityUsageAdmin)
admin.site.register(GeoRelation, GeoRelationAdmin)
admin.site.register(Party)
admin.site.register(PartyUsage, PartyUsageAdmin)
admin.site.register(PercentUsage, PercentUsageAdmin)
admin.site.register(RatioUsage, RatioUsageAdmin)
admin.site.register(RegulationUsage, RegulationUsageAdmin)
admin.site.register(Term, TermAdmin)
admin.site.register(TermUsage, TermUsageAdmin)
admin.site.register(DocumentTermUsage, DocumentTermUsageAdmin)
admin.site.register(TrademarkUsage, TrademarkUsageAdmin)
admin.site.register(UrlUsage, UrlUsageAdmin)
