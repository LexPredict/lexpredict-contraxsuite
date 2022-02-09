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

import csv
import math
from typing import List, Dict, Any  # OrderedDict as OrderedDictType
from collections import OrderedDict

# Django imports
import pandas as pd
from django.contrib import admin
from django.db.models import F, Q, QuerySet, Count
from django.forms import Select
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import path, reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe

# Project imports
from apps.common.querysets import CustomCountQuerySet, stringify_queryset
from apps.common.utils import full_reverse, GroupConcat
from apps.common.model_utils.improved_django_json_encoder import ImprovedDjangoJSONEncoder
from apps.document.models import TextUnit
from apps.extract.models import AmountUsage, CitationUsage, CopyrightUsage, Court, CourtUsage, CurrencyUsage, \
    DateDurationUsage, DateUsage, DefinitionUsage, DistanceUsage, GeoAlias, GeoAliasUsage, GeoEntity, GeoEntityUsage, \
    GeoRelation, Party, PartyUsage, PercentUsage, RatioUsage, RegulationUsage, Term, TermUsage, TrademarkUsage, \
    UrlUsage, DocumentTermUsage, DocumentDefinitionUsage, BanListRecord, TermTag, CompanyType, CompanyTypeTag
from apps.task.forms import LoadTermsForm, LoadCompanyTypesForm

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TextUnitUsageAdminBase(admin.ModelAdmin):
    raw_id_fields = ('text_unit',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('text_unit', 'text_unit__document')


class CourtAdmin(admin.ModelAdmin):
    list_display = ('type', 'name', 'alias')
    search_fields = ('name', 'alias')


class CourtUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'court', 'count')
    search_fields = ('text_unit__text', 'court__name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('court')


class CitationUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'citation_str', 'count')
    search_fields = ('text_unit__text', 'citation_str')


class CopyrightUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'copyright_str', 'count')
    search_fields = ('text_unit__text', 'copyright_str')


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
    search_fields = ('text_unit__text', 'alias__alias')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('alias', 'alias__entity')


class GeoEntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name', 'category')


class GeoEntityUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'entity', 'count')
    search_fields = ('text_unit__text', 'entity__name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('entity')


class GeoRelationAdmin(admin.ModelAdmin):
    list_display = ('entity_a', 'entity_b', 'relation_type')
    search_fields = ('entity_a__name', 'entity_b__name', 'relation_type')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('entity_a', 'entity_b')


class TagManagerAdmin:
    @classmethod
    def init_obj_relations(
            cls,
            new_obj: Any,
            data: Dict[str, Any],
            tag_by_name: Dict[str, Any],
            tag_class,
            tag_column_name: str = 'Tags') -> None:
        tag_list_str = data[tag_column_name] or ''
        if not isinstance(tag_list_str, str):
            tag_list_str = ''  # for numpy / pandas "nan" value
        tag_names = [t.strip() for t in tag_list_str.split(',')]
        tag_names = [t for t in tag_names if t]
        # new object needs to be saved to add a tag to it (relation)
        # otherwise this line fails
        if new_obj.tags is not None:
            extra_tags = [t for t in new_obj.tags.all() if t.name not in tag_names]
            for tag in extra_tags:
                new_obj.tags.remove(tag)
        for tag_name in tag_names:
            if tag_name not in tag_by_name:
                new_tag = tag_class()
                new_tag.name = tag_name
                new_tag.save()
                tag_by_name[tag_name] = new_tag
            new_obj.tags.add(tag_by_name[tag_name])

    @classmethod
    def _export_as_csv(cls,
                       model_name: str,
                       field_aliases: OrderedDict,
                       queryset):
        queryset = queryset.annotate(tag_list=GroupConcat('tags__name'))

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={model_name}.csv'
        writer = csv.writer(response)
        writer.writerow([title for _, title in field_aliases.items()])
        for obj in queryset:
            tag_list_items = (obj.tag_list or '').split(', ')
            obj.tag_list = ', '.join(sorted(tag_list_items))
            writer.writerow([getattr(obj, field) for field in field_aliases])

        return response


class TermAdmin(admin.ModelAdmin, TagManagerAdmin):
    list_display = ('term', 'source', 'definition_url', 'term_tags')
    search_fields = ('term', 'source', 'definition_url', '_term_tags')
    actions = ['export_as_csv']

    COLUMN_FIELD_MAPPING = {
        'Term': 'term',
        'Source': 'source',
        'Locale': 'definition_url',
        'Tags': 'tag_list',
        # for backward compatibility
        'Term Locale': 'definition_url',
        'Term Category': 'source',
    }

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _term_tags=GroupConcat('tags__name'))
        return queryset

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def term_tags(self, obj: Term):
        return obj._term_tags

    term_tags.short_description = 'Tags'
    term_tags.admin_order_field = '_term_tags'

    def json_response(self, data, **kwargs):
        return JsonResponse(data, encoder=ImprovedDjangoJSONEncoder, safe=False, **kwargs)

    def upload_csv_file(self, request):
        # TODO: move into task.views/forms/urls

        if request.method == 'GET':
            form = LoadTermsForm()
            data = dict(form_data=form.as_p())
            return self.json_response(data)

        form = LoadTermsForm(files=request.FILES)
        if not form.is_valid():
            return self.json_response(form.errors, status=400)

        file_data = request.FILES['source_file']
        try:
            df = pd.read_csv(file_data.file)
        except:
            return JsonResponse(data={'status': 'error', 'message': 'File can\'t be parsed as CSV'})

        # we expect the following columns here:
        # 'term', 'source', 'definition_url', 'tag_list'
        # New terms will be added, the existing terms will be updated.
        try:
            self.import_or_update_terms(df)
        except Exception as e:
            return JsonResponse(data={'status': 'error', 'message': str(e)})
        return HttpResponseRedirect(reverse('admin:extract_term_changelist'))

    def import_or_update_terms(self, df: pd.DataFrame):
        old_term_list = Term.objects.annotate(tag_list=GroupConcat('tags__name'))
        for term in old_term_list:
            tag_list_items = (term.tag_list or '').split(', ')
            term.tag_list = ', '.join(sorted(tag_list_items))
        old_terms = {t.term: t for t in old_term_list}

        new_terms: List[Dict[str, any]] = []
        updated_terms: List[Dict[str, any]] = []

        for _, row in df.iterrows():
            if len(row) == 0:
                continue
            data = row.to_dict()
            data = {d: data[d] if not
                    (isinstance(data[d], float) and math.isnan(data[d])) else '' for d in data}
            if data['Term'] not in old_terms:
                new_terms.append(data)
                continue
            # did item change?
            is_updated = False
            old_term = old_terms[data['Term']]
            for key in data:
                term_attr = self.COLUMN_FIELD_MAPPING[key]
                if not hasattr(old_term, term_attr):
                    # for columns like 'Case Sensitive'
                    continue
                if data[key] != getattr(old_term, term_attr):
                    is_updated = True
                    break
            if is_updated:
                updated_terms.append(data)

        tag_by_name = {t.name: t for t in TermTag.objects.all()}

        # insert new terms. Then update updated terms
        for data in new_terms:
            term = Term()
            # term object needs to be saved to add a tag to it (relation), see self.init_new_term
            self.init_new_term(term, data, tag_by_name)

        # update existing terms
        for data in updated_terms:
            term = old_terms[data['Term']]
            self.init_new_term(term, data, tag_by_name)

    @classmethod
    def init_new_term(cls, term: Term, data: Dict[str, Any], tag_by_name: Dict[str, TermTag]) -> None:
        term.term = data['Term']
        term.definition_url = data.get('Locale', data.get('Term Locale'))
        term.source = data.get('Source', data.get('Term Category'))
        # term object needs to be saved to add a tag to it (relation)
        term.save()
        cls.init_obj_relations(term, data, tag_by_name, TermTag)

    def export_as_csv(self, request, queryset):
        field_aliases = OrderedDict(
            term='Term', source='Source',
            definition_url='Locale', tag_list='Tags')
        return self._export_as_csv(self.model._meta, field_aliases, queryset)

    def export_all_as_csv(self, request):
        return self.export_as_csv(request, Term.objects.all())

    export_as_csv.short_description = 'Export Selected'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('upload_csv_file/', self.upload_csv_file),
            path('export_all_terms/', self.export_all_as_csv)
        ]
        return my_urls + urls


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
    search_fields = ('text_unit__text', 'trademark')


class UrlUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'source_url', 'count')
    search_fields = ('text_unit__text', 'source_url')


class PartyUsageAdmin(TextUnitUsageAdminBase):
    list_display = ('text_unit', 'party_name', 'count')
    search_fields = ('text_unit__text', 'party__name')

    @staticmethod
    def party_name(obj):
        return obj.party_name

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(party_name=F('party__name'))
        return qs.select_related('party')


class BanListRecordListFilter(admin.SimpleListFilter):
    title = 'Entity'
    parameter_name = 'entity_type'
    default_value = 'All'

    def lookups(self, request, model_admin):
        options = BanListRecord.TYPE_CHOICES
        return sorted(options, key=lambda c: c[0])

    def queryset(self, request, queryset):
        if not self.value() or self.value() == 'All':
            return queryset
        return queryset.filter(entity_type=self.value())


class BanListRecordAdmin(admin.ModelAdmin):
    list_display = ('record_ref', 'entity_type', 'pattern', 'ignore_case', 'is_regex', 'trim_phrase')
    list_editable = ('entity_type', 'pattern', 'ignore_case', 'is_regex', 'trim_phrase')
    search_fields = ('entity_type', 'pattern')
    list_filter = (BanListRecordListFilter,)

    @staticmethod
    def record_ref(obj):
        return f'{obj.pk} - {obj.pattern}'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['entity_type'].widget = Select(choices=(
            ('party', 'party'),
        ))
        return form


class TermTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'terms_count', 'projects_count')
    search_fields = ('pk', 'name')
    # filter_horizontal = ('terms',)

    @staticmethod
    def projects_count(obj):
        return obj.projects_count

    @staticmethod
    def terms_count(obj):
        return obj.terms_count

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(projects_count=Count('project'), terms_count=Count('term'))
        return qs


class CompanyTypeAdmin(admin.ModelAdmin, TagManagerAdmin):
    list_display = ('alias', 'abbreviation', 'label', 'companytype_tags')
    search_fields = ('alias', 'abbreviation', 'label')
    actions = ['export_as_csv', 'export_all_as_csv']

    COLUMN_FIELD_MAPPING = {
        'Alias': 'alias',
        'Abbreviation': 'abbreviation',
        'Label': 'label',
        'Tags': 'tag_list',
    }

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _companytype_tags=GroupConcat('tags__name'))
        return queryset

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def companytype_tags(self, obj: CompanyType):
        return obj._companytype_tags

    companytype_tags.short_description = 'Tags'
    companytype_tags.admin_order_field = '_companytype_tags'

    def json_response(self, data, **kwargs):
        return JsonResponse(data, encoder=ImprovedDjangoJSONEncoder, safe=False, **kwargs)

    def upload_csv_file(self, request):
        if request.method == 'GET':
            form = LoadCompanyTypesForm()
            data = dict(form_data=form.as_p())
            return self.json_response(data)

        form = LoadCompanyTypesForm(files=request.FILES)
        if not form.is_valid():
            return self.json_response(form.errors, status=400)

        file_data = request.FILES['source_file']
        df = pd.read_csv(file_data.file)
        # we expect the following columns here:
        # 'alias', 'abbreviation', 'label', 'tag_list'
        # New company types will be added, the existing ones will be updated.
        self.import_or_update_types(df)
        return HttpResponseRedirect(reverse('admin:extract_companytype_changelist'))

    def import_or_update_types(self, df: pd.DataFrame):
        old_comp_list = CompanyType.objects.annotate(tag_list=GroupConcat('tags__name'))
        for cm in old_comp_list:
            tag_list_items = (cm.tag_list or '').split(', ')
            cm.tag_list = ', '.join(sorted(tag_list_items))
        old_comps = {t.alias: t for t in old_comp_list}

        new_comps: List[Dict[str, any]] = []
        updated_comps: List[Dict[str, any]] = []

        for _, row in df.iterrows():
            if len(row) == 0:
                continue
            data = row.to_dict()
            if data['Alias'] not in old_comps:
                new_comps.append(data)
                continue
            # did item change?
            is_updated = False
            old_comp = old_comps[data['Alias']]
            for key in data:
                term_attr = self.COLUMN_FIELD_MAPPING[key]
                if data[key] != getattr(old_comp, term_attr):
                    is_updated = True
                    break
            if is_updated:
                updated_comps.append(data)

        tag_by_name = {t.name: t for t in CompanyTypeTag.objects.all()}

        # insert new terms. Then update updated terms
        for data in new_comps:
            comp = CompanyType()
            # CompanyType object needs to be saved to add a tag to it (relation), see self.init_new_term
            self.init_new_comp(comp, data, tag_by_name)

        # update existing company types
        for data in updated_comps:
            comp = old_comps[data['Alias']]
            self.init_new_comp(comp, data, tag_by_name)

    @classmethod
    def init_new_comp(cls, comp: CompanyType, data: Dict[str, Any], tag_by_name: Dict[str, TermTag]) -> None:
        comp.alias = data['Alias']
        comp.abbreviation = data['Abbreviation']
        comp.label = data['Label']
        # CompanyType object needs to be saved to add a tag to it (relation)
        comp.save()
        cls.init_obj_relations(comp, data, tag_by_name, CompanyTypeTag)

    def export_as_csv(self, request, queryset):
        field_aliases = OrderedDict(
            alias='Alias', abbreviation='Abbreviation',
            label='Label', tag_list='Tags')
        return self._export_as_csv(self.model._meta, field_aliases, queryset)

    def export_all_as_csv(self, request, queryset):
        return self.export_as_csv(request, CompanyType.objects.all())

    export_as_csv.short_description = 'Export Selected'

    export_all_as_csv.short_description = 'Export All'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('upload_csv_file/', self.upload_csv_file),
        ]
        return my_urls + urls


class CompanyTypeTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'companytypes_count', 'projects_count')
    search_fields = ('pk', 'name')

    @staticmethod
    def projects_count(obj):
        return obj.projects_count

    @staticmethod
    def companytypes_count(obj):
        return obj.companytypes_count

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(projects_count=Count('project'), companytypes_count=Count('companytype'))
        return qs


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
admin.site.register(BanListRecord, BanListRecordAdmin)
admin.site.register(TermTag, TermTagAdmin)
admin.site.register(CompanyType, CompanyTypeAdmin)
admin.site.register(CompanyTypeTag, CompanyTypeTagAdmin)
