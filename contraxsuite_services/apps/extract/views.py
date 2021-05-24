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

# Future imports
from __future__ import absolute_import, unicode_literals

# Standard imports
import datetime
import itertools
import json
from collections import defaultdict
from typing import Dict, Any, Set, List, Tuple
from urllib.parse import quote as url_quote

# Third-party import
import icalendar

# Django imports
from django.contrib.auth import authenticate
from django.db.models import Count, F, Max, Min, Sum, Q, Value, Subquery, QuerySet
from django.db.models.functions import TruncMonth, TruncYear, Left, Concat
from django.http import Http404, HttpResponseForbidden, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import DetailView, TemplateView

# Project imports
import apps.common.mixins
from apps.common.querysets import CustomCountQuerySet, stringify_queryset
from apps.document.models import Document, TextUnit
from apps.extract.models import (
    AmountUsage, CitationUsage, CopyrightUsage, CourtUsage, CurrencyUsage,
    DateDurationUsage, DateUsage, DefinitionUsage, DistanceUsage,
    GeoAliasUsage, GeoAlias, GeoEntity, GeoEntityUsage, Party, PartyUsage, PercentUsage,
    RatioUsage, RegulationUsage, TermUsage, TrademarkUsage,
    UrlUsage, DocumentTermUsage, Term,
    ProjectTermUsage, ProjectPartyUsage, ProjectGeoEntityUsage, ProjectDefinitionUsage)

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class BaseUsageListView(apps.common.mixins.JqPaginatedListView):
    json_fields = ['document_id',
                   'project__name',
                   'document__name',
                   'document__document_type__title',
                   'text_unit__textunittext__text',
                   'text_unit_id']
    document_lookup = 'document'
    field_types = dict(count=int)
    highlight_field = ''
    extra_item_map = {}
    search_field = ''
    annotate_after_filter = dict(
        text_unit__textunittext__text=Left('text_unit__textunittext__text', 300)
    )

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = self.full_reverse(
                'document:document-detail', args=[item['document_id']])
            item['detail_url'] = self.full_reverse(
                'document:text-unit-detail', args=[item['text_unit_id']]) + \
                                 '?highlight=' + (item.get(self.highlight_field) or '')
            for field_name, field_lambda in self.extra_item_map.items():
                item[field_name] = field_lambda(item)
            self.get_item_data(item)
        return data

    def get_queryset(self):
        qs = super().get_queryset()

        if "document_pk" in self.request.GET:
            qs = qs.filter(document_id=self.request.GET['document_pk'])
        else:
            qs = qs.filter(project_id__in=list(
                self.request.user.userprojectssavedfilter.projects.values_list('pk', flat=True)))

        return qs.select_related('text_unit', 'text_unit__textunittext')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.search_field:
            ctx[self.search_field] = self.request.GET.get(self.search_field, "")
        return ctx

    def get_item_data(self, item):
        pass


class BaseDocUsageListView(apps.common.mixins.JqPaginatedListView):
    json_fields = ['document__pk',
                   'document__project__name',
                   'document__name',
                   'document__description', 'document__document_type__title']
    document_lookup = 'document'
    field_types = dict(count=int)
    highlight_field = ''
    extra_item_map = {}
    search_field = ''

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = self.full_reverse(
                'document:document-detail', args=[item['document__pk']])
            item['detail_url'] = item['url']
            for field_name, field_lambda in self.extra_item_map.items():
                item[field_name] = field_lambda(item)
        return data

    def get_queryset(self):
        qs = super().get_queryset()

        if "document_pk" in self.request.GET:
            qs = qs.filter(document_id=self.request.GET['document_pk'])
        else:
            qs = qs.filter(
                document__project_id__in=list(
                    self.request.user.userprojectssavedfilter.projects.values_list('pk', flat=True)))

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.search_field:
            ctx[self.search_field] = self.request.GET.get(self.search_field, "")
        return ctx


class BaseTopUsageListView(apps.common.mixins.JqPaginatedListView):
    deep_processing = False
    document_lookup = 'document'
    sort_by = None
    document_filter_key = 'document_id'
    project_filter_key = 'project_id__in'
    extra_data = {}  # type: Dict[str, Any]

    def get_json_data(self, **kwargs):
        data = super().get_json_data(**kwargs)
        data.update(self.extra_data)
        parent_data = None
        if "document_pk" in self.request.GET:
            parent_list_view = self.parent_list_view(request=self.request)
            parent_data = parent_list_view.get_json_data()['data']
        for item in data['data']:
            self.get_item_data(item, parent_data)
        if self.sort_by:
            data['data'] = sorted(data['data'], key=self.sort_by)
        return data

    def get_queryset(self):
        qs = super().get_queryset()

        if "document_pk" in self.request.GET:
            qs = qs.filter(**{self.document_filter_key: self.request.GET['document_pk']})
        else:
            project_ids = list(self.request.user.userprojectssavedfilter.projects.values_list(
                'pk', flat=True))
            qs = qs.filter(**{self.project_filter_key: project_ids})
        return qs


class TermUsageListView(BaseDocUsageListView):
    sub_app = 'term'
    model = DocumentTermUsage  # TermUsage
    extra_json_fields = ['term__term', 'count']
    highlight_field = 'term__term'
    search_field = 'term_search'
    template_name = 'extract/term_usage_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        term_search = self.request.GET.get("term_search", "")

        if term_search:
            for term in term_search.split(','):
                if term.startswith('-'):
                    qs = qs.exclude(term__term=term.lstrip('-'))
                else:
                    qs = qs.filter(term__term__icontains=term)
        return qs


class TopTermUsageListView(BaseTopUsageListView):
    sub_app = 'term'
    parent_list_view = DocumentTermUsage
    template_name = 'extract/top_term_usage_list.html'
    document_filter_key = 'document_id'
    project_filter_key = 'project_id__in'

    def get_item_data(self, item, parent_data=None):
        item['url'] = self.full_reverse('extract:term-usage-list') + '?term_search=' + item['term__term']
        if "document_pk" in self.request.GET:
            item['term_data'] = [i for i in parent_data if i['term__term'] == item['term__term']]
        return item

    def get_queryset(self):
        self.extra_data = {}

        if 'document_id' in self.request.GET:
            qs = super().get_queryset()
            qs = qs.values('term__term', 'count').order_by('-count')
        else:
            qs = ProjectTermUsage.objects \
                .filter(project_id__in=self.request.user.userprojectssavedfilter.projects.all()) \
                .values('term__term', 'count').order_by('-count')
        return qs


class DocumentTopTermUsageListView(apps.common.mixins.JqPaginatedListView):

    def get_queryset(self):
        return TermUsage.objects.filter(text_unit__unit_type='sentence').order_by('term_id')

    def get_json_data(self, *args, **kwargs):
        document_id = self.request.GET.get('document_pk')
        term_id = self.request.GET.get('term_pk')

        qs = self.get_queryset()
        if document_id:
            qs = qs.filter(document_id=document_id)

        if term_id:
            qs = qs.filter(term_id=term_id)
            res = list(
                qs.values('term__term', 'text_unit__textunittext__text', 'text_unit_id', 'count').order_by('-count'))
            for item in res:
                text_unit_id = item.pop('text_unit_id')
                item['detail_url'] = self.full_reverse(
                    'document:text-unit-detail', args=[text_unit_id]) + \
                                     '?highlight=' + item['term__term']
        else:
            top = qs \
                .values('term_id', 'term__term') \
                .annotate(count=Sum('count')) \
                .order_by('-count')
            res = list(top)

        return {'data': res, 'total_records': len(res)}


class BaseTextUnitUsageListView(apps.common.mixins.JqPaginatedListView):
    model = TextUnit
    template_name = 'document/text_unit_ref_usage_list.html'
    json_fields = ['document_id',
                   'textunittext__text',
                   'unit_type',
                   'language',
                   'pk']
    highlight_field = ''
    extra_item_map = {}
    search_field = ''

    filter_field_name = ''  # should be derived in descendant
    filter_field_id = ''  # should be derived in descendant
    search_prompt = ''  # should be derived in descendant
    units_column_title = ''  # should be derived in descendant
    filter_join_operator = 0  # join sub-filters by AND (1 for "OR")

    def get(self, request, *args, **kwargs):
        self.get_args = args
        self.get_kwargs = kwargs
        if self.filter_field_name in request.GET:
            self.get_kwargs[self.filter_field_name] = request.GET[self.filter_field_name]
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_prompt'] = self.search_prompt
        ctx['filter_field_name'] = self.filter_field_name
        ctx['filter_field_id'] = self.filter_field_id
        ctx['units_column_title'] = self.units_column_title

        ctx[self.filter_field_name] = ''
        if self.filter_field_name in self.get_kwargs:
            ctx['filter_value'] = self.get_kwargs[self.filter_field_name]
        elif self.filter_field_id in self.get_kwargs:
            self.set_filter_value_by_ref_id(ctx)
        return ctx

    def set_filter_value_by_ref_id(self, ctx: Dict[str, Any]):
        raise NotImplementedError()

    def sort(self, qs):
        sortfield = self.request.GET.get('sortdatafield')
        if sortfield == 'unit_type':
            # if we're sorting by "unit_type" - that performs bad
            # let's split the query on two and union
            sortorder = self.request.GET.get('sortorder', 'asc')
            qs_s = qs.filter(unit_type='sentence')
            qs_p = qs.filter(unit_type='paragraph')
            qs_filtered = qs_p if sortorder.lower() == 'asc' else qs_s
            if qs_filtered.count() > 0:
                return qs_filtered
            return qs
        return super().sort(qs)


class TextUnitTermUsageListView(BaseTextUnitUsageListView):
    sub_app = 'term'
    filter_field_name = 'term_name'
    filter_field_id = 'term_id'
    search_prompt = 'Search for term:'
    units_column_title = 'Terms'

    field_name_transform_map = {'unit_refs': 'term__term'}
    LIMIT_QUERY = 100000

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['document__name'] = Document.all_objects.filter(
                pk=item['document_id']).values_list('name', flat=True)[0]
            item['url'] = self.full_reverse(
                'document:document-detail', args=[item['document_id']])
            item['detail_url'] = self.full_reverse(
                'document:text-unit-detail', args=[item['pk']]) + \
                                 '?highlight=' + (item.get(self.highlight_field) or '')
            item_terms = TermUsage.objects.filter(
                text_unit_id=item['pk']).order_by('term__term').distinct().values_list('term__term', flat=True)
            item['unit_refs'] = ', '.join(item_terms)
            for field_name, field_lambda in self.extra_item_map.items():
                item[field_name] = field_lambda(item)
        return data

    def get_queryset(self, term_id=None):
        term_usages = TermUsage.objects.all()

        self.read_request_filters()
        if hasattr(self, 'term_filter'):
            filter_val = self.term_filter[0]['value']
            term_usages = TermUsage.objects.filter(term__term__startswith=filter_val)
        term_usages = term_usages.order_by()

        qs = TextUnit.objects.only('pk', 'document_id', 'unit_type', 'language',
                                   'location_start', 'location_end').filter(
            pk__in=Subquery(term_usages.values('text_unit_id'))).order_by('document_id')
        filtered_projects = list(self.request.user.userprojectssavedfilter.projects.values_list('pk', flat=True))
        qs = qs.filter(document__project_id__in=filtered_projects or [])
        return qs

    def set_filter_value_by_ref_id(self, ctx: Dict[str, Any]):
        terms = list(Term.objects.filter(pk=self.get_kwargs[self.filter_field_id]))
        if terms:
            ctx['filter_value'] = terms[0].term

    def read_request_filters(self) -> Dict[str, Any]:
        filters = super().read_request_filters()
        if 'term__term' in filters:
            self.term_filter = filters['term__term']
            del filters['term__term']
        return filters

    def filter_count_predicate(self, qs: QuerySet) -> CustomCountQuerySet:
        # possible filters: document_name, term_name, term_id
        # text_unit_text?
        qs = CustomCountQuerySet.wrap(qs)  # type: CustomCountQuerySet
        filters = self.read_request_filters()
        if not filters:
            inner_query = stringify_queryset(qs)
            full_query = f'SELECT COUNT(*) FROM ({inner_query} LIMIT {self.LIMIT_QUERY}) AS temp;'
            qs.set_optional_count_query(full_query)
            return qs

        # base query looks like
        # SELECT COUNT(text_unit_id) FROM (SELECT DISTINCT text_unit_id FROM extract_termusage LIMIT 1000) AS temp;
        inner_query = 'SELECT DISTINCT tu.text_unit_id FROM extract_termusage tu'

        joins = set()  # type: Set[str]
        wheres = []  # type: List[Tuple[str, str]]  # table, operator
        operator_by_num = {0: 'AND', 1: 'OR'}

        for filter in filters:
            op = filters[filter][0]['operator']
            filters[filter][0]['operator'] = operator_by_num[op]

        if 'document__name' in filters:
            filter_val = filters['document__name'][0]['value'].replace("'", "''")
            joins.add('document_textunit t on tu.text_unit_id = t.id')
            joins.add('document_document d on t.document_id = d.id')
            wheres.append((f"d.name LIKE '{filter_val}%'", filters['document__name'][0]['operator'],))
            """
            SELECT COUNT(text_unit_id) FROM (SELECT DISTINCT text_unit_id FROM extract_termusage tu
            join document_textunit t on tu.text_unit_id = t.id join document_document d on t.document_id = d.id
            WHERE d.name LIKE '12%' LIMIT 1000) AS temp;
            """

        if 'language' in filters:
            filter_val = filters['language'][0]['value'].replace("'", "''")
            joins.add('document_textunit t on tu.text_unit_id = t.id')
            wheres.append((f"t.language LIKE '{filter_val}%'", filters['language'][0]['operator'],))

        if 'unit_type' in filters:
            filter_val = filters['unit_type'][0]['value'].replace("'", "''")
            joins.add('document_textunit t on tu.text_unit_id = t.id')
            wheres.append((f"t.unit_type LIKE '{filter_val}%'", filters['unit_type'][0]['operator'],))

        if 'textunit__text' in filters:
            filter_val = filters['textunit__text'][0]['value'].replace("'", "''")
            joins.add('document_textunittext tt on tu.text_unit_id = tt.id')
            wheres.append((f"tt.text LIKE '{filter_val}%'", filters['textunit__text'][0]['operator'],))

        if hasattr(self, 'term_filter'):
            filter_val = self.term_filter[0]['value'].replace("'", "''")
            joins.add('extract_term tr on tu.term_id = tr.id')
            op = self.term_filter[0]['operator']
            wheres.append((f"tr.term LIKE '{filter_val}%'", operator_by_num[op],))

        if joins:
            inner_query = inner_query + ' JOIN ' + ' JOIN '.join(joins)

        if wheres:
            inner_query = inner_query + ' WHERE'
            for i, where in enumerate(wheres):
                if i > 0:
                    inner_query += f' {where[1]}'  # AND, OR
                inner_query += f' {where[0]}'

        full_query = f'SELECT COUNT(text_unit_id) FROM ({inner_query} LIMIT 1000) AS temp;'
        qs.set_optional_count_query(full_query)
        return qs


class GeoEntityListView(apps.common.mixins.JqPaginatedListView):
    template_name = 'extract/geo_entity_list.html'
    model = GeoEntity

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['alias'] = ', '.join(
                GeoAlias.objects.filter(entity_id=item['pk']).values_list('alias', flat=True))
        return data


class GeoEntityPriorityUpdateView(apps.common.mixins.JSONResponseView):

    def get_json_data(self, request, *args, **kwargs):
        pk = request.GET.get('pk')
        priority = request.GET.get('priority')
        obj = GeoEntity.objects.get(pk=pk)
        obj.priority = priority
        obj.save()
        return {'status': 'success', 'message': 'Updated'}


class GeoEntityUsageListView(BaseUsageListView):
    sub_app = 'geoentity'
    model = GeoEntityUsage

    old_json_fields = ['document_id',
                       'project__name',
                       'document__name',
                       'document__document_type__title',
                       'text_unit__textunittext__text',
                       'text_unit_id']
    json_fields = ['text_unit_id',
                   'entity_id',
                   'count']

    highlight_field = 'entity__name'
    search_field = 'entity_search'
    template_name = 'extract/geo_entity_usage_list.html'

    def get_json_data(self, **kwargs):
        data = apps.common.mixins.JqPaginatedListView.get_json_data(self, **kwargs)

        unit_ids = [i['text_unit_id'] for i in data['data']]
        enty_ids = [i['entity_id'] for i in data['data']]

        unit_detail = {v[0]: v for v in TextUnit.objects.filter(pk__in=unit_ids).values_list(
                    'pk', 'textunittext__text', 'document_id',
                    'document__name', 'document__document_type__title', 'document__project__name')}
        enty_detail = {v[0]: v for v in GeoEntity.objects.filter(
            pk__in=enty_ids).values_list('pk', 'name', 'category')}

        for item in data['data']:
            _, ent_name, ent_cat = enty_detail[item['entity_id']]
            item['entity__name'] = ent_name
            item['entity__category'] = ent_cat

            unit_pk, unit_text, unit_document_pk, unit_document_name, unit_document_type_title, unit_project = \
                unit_detail[item['text_unit_id']]
            item['text_unit_id'] = unit_pk
            item['text_unit__textunittext__text'] = unit_text
            item['document_id'] = unit_document_pk
            item['document__name'] = unit_document_name
            item['document__document_type__title'] = unit_document_type_title
            item['project__name'] = unit_project

            item['url'] = self.full_reverse(
                'document:document-detail', args=[item['document_id']])
            item['detail_url'] = self.full_reverse(
                'document:text-unit-detail', args=[item['text_unit_id']]) + \
                                 '?highlight=' + (item.get(self.highlight_field) or '')
            for field_name, field_lambda in self.extra_item_map.items():
                item[field_name] = field_lambda(item)
            self.get_item_data(item)

        return data

    def get_queryset(self):
        qs = apps.common.mixins.JqPaginatedListView.get_queryset(self)
        qs = qs.filter(
            project_id__in=list(self.request.user.userprojectssavedfilter.projects.values_list('pk', flat=True)))

        if "document_pk" in self.request.GET:
            qs = qs.filter(document_id=self.request.GET['document_pk'])

        entity_search = self.request.GET.get("entity_search")
        document_id = self.request.GET.get("document_pk")
        party_id = self.request.GET.get("party_pk")
        entity_id = self.request.GET.get("entity_pk")

        if document_id:
            qs = qs.filter(document_id=document_id)
        if entity_search:
            entity_search_list = entity_search.split(",")
            qs = qs.filter(entity__name__in=entity_search_list)
        if party_id:
            doc_ids = Document.objects.filter(textunit__partyusage__party_id=party_id) \
                .values_list('pk', flat=True).distinct()
            qs = qs.filter(document_id__in=doc_ids)
        if entity_id:
            qs = qs.filter(entity_id=entity_id)
        return qs


class TopGeoEntityUsageListView(BaseTopUsageListView):
    sub_app = 'geoentity'
    parent_list_view = GeoEntityUsageListView
    template_name = "extract/top_geo_entity_usage_list.html"

    def get_item_data(self, item, parent_data):
        item['url'] = '{}?entity_search={}'.format(
            self.full_reverse('extract:geo-entity-usage-list'), item['entity__name'])
        if "document_pk" in self.request.GET:
            item['entity_data'] = [i for i in parent_data if i['entity__name'] == item['entity__name']]
        return item

    def get_queryset(self):
        document_id = self.request.GET.get("document_pk")
        party_id = self.request.GET.get("party_pk")
        entity_id = self.request.GET.get("entity_pk")

        if document_id or party_id or entity_id:
            self.model = GeoEntityUsage
            qs = super().get_queryset().filter(text_unit__unit_type='sentence')

            if document_id:
                qs = qs.filter(document_id=document_id)
            if party_id:
                doc_ids = Document.objects.filter(textunit__partyusage__party_id=party_id)\
                    .values_list('pk', flat=True).distinct()
                qs = qs.filter(document_id__in=doc_ids)
            if entity_id:
                qs = qs.filter(entity_id=entity_id)
        else:
            self.model = ProjectGeoEntityUsage
            qs = super().get_queryset()

        qs = qs.values('entity_id', 'entity__name', 'entity__category') \
            .annotate(count=Sum("count")) \
            .order_by("-count")
        return qs


class GeoAliasUsageListView(BaseUsageListView):
    sub_app = 'geoentity'
    model = GeoAliasUsage
    extra_json_fields = ['alias__alias', 'alias__locale', 'alias__type', 'count',
                         'alias__entity__name', 'alias__entity__category']
    highlight_field = 'alias__alias'

    def get_queryset(self):
        qs = super().get_queryset()
        entity_search = self.request.GET.get("entity_search", "")
        if entity_search:
            entity_search_list = entity_search.split(",")
            qs = qs.filter(alias__entity__name__in=entity_search_list)
        if "party_pk" in self.request.GET:
            qs = qs.filter(
                document__textunit__partyusage__party_id=self.request.GET['party_pk']) \
                .distinct()
        if 'entity_pk' in self.request.GET:
            qs = qs.filter(alias__entity_id=self.request.GET['entity_pk'])
        return qs


class TypeaheadTermTerm(apps.common.mixins.TypeaheadView):

    def get_json_data(self, request, *args, **kwargs):
        qs = ProjectTermUsage.objects.all()
        qs = qs.filter(
            project_id__in=list(
                self.request.user.userprojectssavedfilter.projects.values_list('pk', flat=True)))

        if "q" in request.GET:
            qs = qs.filter(term__term__icontains=request.GET.get("q")).values('term__term').distinct()
        qs = qs.order_by('-count')[:self.DEFAULT_LIMIT]
        results = []
        for t in qs:
            results.append({"value": t['term__term']})
            results.append({"value": '-%s' % t['term__term']})
        return results


class TypeaheadGeoEntityName(apps.common.mixins.TypeaheadView):

    def get_json_data(self, request, *args, **kwargs):
        qs = ProjectGeoEntityUsage.objects.all()
        qs = qs.filter(
            project_id__in=list(
                self.request.user.userprojectssavedfilter.projects.values_list('pk', flat=True)))
        if "q" in request.GET:
            qs = qs.filter(entity__name__icontains=request.GET.get("q")).order_by('entity__name').values('entity__name').distinct()
        qs = qs.order_by('-count')[:self.DEFAULT_LIMIT]
        return [{"value": i['entity__name']} for i in qs]


class TypeaheadPartyName(apps.common.mixins.TypeaheadView):

    def get_json_data(self, request, *args, **kwargs):
        qs = ProjectPartyUsage.objects.all()
        qs = qs.filter(project_id__in=list(
            self.request.user.userprojectssavedfilter.projects.values_list('pk', flat=True)))

        if "q" in request.GET:
            qs = qs.filter(party__name__icontains=request.GET.get("q")).values('party__name').distinct()
        qs = qs.order_by('-count')[:self.DEFAULT_LIMIT]
        return [{"value": i['party__name']} for i in qs]


class PartyUsageListView(BaseUsageListView):
    sub_app = 'party'
    model = PartyUsage
    extra_json_fields = ['party__name', 'party__type_abbr', 'party_id', 'count']
    highlight_field = 'party__name'
    search_field = 'party_search'
    template_name = 'extract/party_usage_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        party_search = self.request.GET.get("party_search", "")
        if party_search:
            party_search_list = party_search.split(",")
            qs = qs.filter(party__name__in=party_search_list)
        party_search_iexact = self.request.GET.get("party_search_iexact", "")
        if party_search_iexact:
            qs = qs.filter(party__name__iexact=party_search_iexact)
        qs = qs.select_related('party', 'text_unit', 'document')
        return qs

    def get_item_data(self, item):
        item['party_summary_url'] = self.full_reverse('extract:party-summary', args=[item['party_id']])
        return item


class TopPartyUsageListView(BaseTopUsageListView):
    sub_app = 'party'
    parent_list_view = PartyUsageListView
    template_name = 'extract/top_party_usage_list.html'

    def get_item_data(self, item, parent_data):
        item['url'] = self.full_reverse('extract:party-usage-list') + '?party_search=' + item['party__name']
        item['party_summary_url'] = self.full_reverse('extract:party-summary', args=[item['party_id']])
        if 'document_pk' in self.request.GET:
            item['party_data'] = [i for i in parent_data if i['party__name'] == item['party__name']]
        return item

    def get_queryset(self):
        self.model = PartyUsage if 'document_pk' in self.request.GET else ProjectPartyUsage
        qs = None

        if qs is None:
            qs = super().get_queryset()
            if 'party_pk' in self.request.GET:
                qs = qs.filter(party_id=self.request.GET['party_pk'])
            qs = qs.values('party__name', 'party__type_abbr', 'party_id') \
                .annotate(count=Sum("count")) \
                .order_by('-count')
        return qs


class DateUsageListView(BaseUsageListView):
    sub_app = 'date'
    model = DateUsage
    extra_json_fields = ['date', 'count']
    template_name = 'extract/date_usage_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        if 'date_search' in self.request.GET:
            qs = qs.filter(date=self.request.GET["date_search"])
        elif 'month_search' in self.request.GET:
            adate = datetime.datetime.strptime(self.request.GET["month_search"], '%Y-%m-%d')
            qs = qs.filter(date__year=adate.year, date__month=adate.month)
        return qs


class TopDateUsageListView(BaseTopUsageListView):
    sub_app = 'date'
    model = DateUsage
    parent_list_view = DateUsageListView
    template_name = 'extract/top_date_usage_list.html'

    def get_item_data(self, item, parent_data):
        item['url'] = self.full_reverse('extract:date-usage-list') + '?date_search=' + item['date'].isoformat()
        if "document_pk" in self.request.GET:
            item['date_data'] = [i for i in parent_data if i['date'] == item['date']]
        return item

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.values("date") \
            .annotate(count=Sum("count")) \
            .order_by("-count")
        return qs


class DateUsageTimelineView(apps.common.mixins.JqPaginatedListView):
    sub_app = 'date'
    model = DateUsage
    template_name = "extract/date_usage_timeline.html"
    document_lookup = 'document'

    def get_json_data(self, **kwargs):
        per_month = json.loads(self.request.GET.get('per_month', 'false'))
        show_documents = json.loads(self.request.GET.get('show_documents', 'false'))
        show_text_unit_text = json.loads(self.request.GET.get('show_text_unit_text', 'false'))
        truncate_text_unit_text = json.loads(self.request.GET.get('truncate_text_unit_text', 'false'))

        qs = super().get_queryset()
        if "document_pk" in self.request.GET:
            qs = qs.filter(document_id=self.request.GET['document_pk'])

        if per_month:
            qs = qs.order_by('date') \
                .annotate(start=TruncMonth('date')) \
                .values('start') \
                .annotate(count=Sum('count')).order_by()
            visible_interval = 360
        else:
            qs = qs.order_by('date') \
                .values(start=F('date')) \
                .annotate(count=Sum('count'))
            date_data = {}
            if show_documents:
                annotations = dict(document=F('document__name'))
                values = ['date', 'document']
                if show_text_unit_text:
                    values.append('text')
                    if truncate_text_unit_text:
                        annotations.update(dict(text=Concat(Left('text_unit__textunittext__text', 100), Value('...'))))
                    else:
                        annotations.update(dict(text=F('text_unit__textunittext__text')))
                date_list_view = DateUsageListView(request=self.request)
                date_data = date_list_view.get_queryset() \
                    .annotate(**annotations) \
                    .values(*values) \
                    .distinct()
                values.remove('date')
                date_data = {k: [{kj: kv for kj, kv in j.items() if kj in values}
                                 for j in v]
                             for k, v in itertools.groupby(date_data, lambda i: i['date'])}
            visible_interval = 180

        max_value = qs.aggregate(m=Max('count'))['m']
        min_value = qs.aggregate(m=Min('count'))['m']
        range_value = max_value - min_value

        data = list(qs)
        for item in data:
            item['weight'] = (item['count'] - min_value) / range_value if range_value else 0
            if per_month:
                item['url'] = '{}?month_search={}'.format(
                    reverse('extract:date-usage-list'), item['start'].isoformat())
                item['content'] = '{}, {}: {}'.format(item['start'].strftime('%B'),
                                                      item['start'].year, item['count'])
            else:
                item['url'] = '{}?date_search={}'.format(
                    reverse('extract:date-usage-list'), item['start'].isoformat())
                item['content'] = '{}: {}'.format(item['start'].isoformat(), item['count'])
                item['date_data'] = date_data.get(item['start'])

        initial_start_date = datetime.date.today() - datetime.timedelta(days=visible_interval)
        initial_end_date = datetime.date.today() + datetime.timedelta(days=visible_interval)
        return {'data': data,
                'per_month': per_month,
                'initial_start_date': initial_start_date,
                'initial_end_date': initial_end_date}


class DateUsageCalendarView(apps.common.mixins.JqPaginatedListView):
    sub_app = 'date'
    model = DateUsage
    template_name = "extract/date_usage_calendar.html"
    document_lookup = 'document'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        documents = self.request.user.user_documents
        documents = documents.filter(
            taskqueue__user_id=self.request.user.pk,
            textunit__dateusage__isnull=False).distinct()
        ctx['documents'] = documents.values('pk', 'name').iterator()

        periods_qs = DateUsage.objects

        # got rid of probably false-pos
        periods_qs = periods_qs.filter(date__gte=datetime.date.today() - datetime.timedelta(365 * 300),
                                       date__lte=datetime.date.today() + datetime.timedelta(365 * 100))

        periods_qs = periods_qs \
            .annotate(year=TruncYear('date')).values('year') \
            .annotate(count=Count('date', distinct=True)).order_by('year')
        periods = []
        start = end = count = years_count = 0
        limit = 1000
        years_count_limit = 10
        flag = False
        current_year = datetime.date.today().year

        # get periods to truncate data by periods otherwise d3 hangs on large datasets
        for q in periods_qs:
            if not start:
                start = q['year']
            if count + q['count'] > limit or years_count > years_count_limit:
                periods.append({'start': start.year, 'end': end.year, 'count': count,
                                'checked': start.year <= current_year <= end.year})
                count = q['count']
                start = q['year']
                years_count = 0
                flag = True
            else:
                count += q['count']
                years_count += 1
                flag = False
            end = q['year']
        if not flag and count:
            periods.append({'start': start.year, 'end': end.year, 'count': count,
                            'checked': start.year <= current_year <= end.year})
        ctx['periods'] = periods

        return ctx

    def get_json_data(self, **kwargs):
        qs = super().get_queryset()

        # got rid of probably false-pos
        qs = qs.filter(date__gte=datetime.date.today() - datetime.timedelta(365 * 300),
                       date__lte=datetime.date.today() + datetime.timedelta(365 * 100))

        if self.request.GET.get("document_id"):
            qs = qs.filter(document_id=self.request.GET['document_id'])

        elif self.request.GET.get("period"):
            start, end = self.request.GET["period"].split('-')
            qs = qs.filter(date__year__gte=start, date__year__lte=end)

        qs = qs.order_by('date') \
            .values('date') \
            .annotate(count=Sum('count'))
        data = list(qs)

        if not data:
            return

        max_value = qs.aggregate(m=Max('count'))['m']

        for item in data:
            item['weight'] = item['count'] / max_value
            item['url'] = '{}?date_search={}'.format(
                reverse('extract:date-usage-list'), item['date'].isoformat())

        return {'data': data,
                'years': sorted({i['date'].year for i in data})}


class DateDurationUsageListView(BaseUsageListView):
    sub_app = 'duration'
    model = DateDurationUsage
    extra_json_fields = ['amount', 'amount_str', 'duration_type', 'duration_days', 'count']
    highlight_field = 'amount_str'
    template_name = 'extract/date_duration_usage_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        if 'duration_search' in self.request.GET:
            try:
                duration_days = float(self.request.GET["duration_search"])
                qs = qs.filter(duration_days=duration_days)
            except ValueError:
                pass
        return qs


class TopDateDurationUsageListView(BaseTopUsageListView):
    sub_app = 'duration'
    model = DateDurationUsage
    parent_list_view = DateDurationUsageListView
    template_name = 'extract/top_date_duration_usage_list.html'

    @staticmethod
    def sort_by(i):
        return -i['duration_days']

    def get_item_data(self, item, parent_data):
        item['url'] = '{}?duration_search={}'.format(
            self.full_reverse('extract:date-duration-usage-list'), str(item['duration_days']))
        if "document_pk" in self.request.GET:
            item['duration_data'] = [i for i in parent_data
                                     if i['duration_days'] == item['duration_days']]
        return item

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.values("amount", "duration_type", "duration_days") \
            .annotate(count=Sum("count")) \
            .order_by("-count")
        return qs


class DefinitionUsageListView(BaseUsageListView):
    sub_app = 'definition'
    model = DefinitionUsage
    extra_json_fields = ['definition', 'count']
    highlight_field = 'definition'
    template_name = 'extract/definition_usage_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        definition_search = self.request.GET.get("definition_search")
        if definition_search:
            qs = qs.filter(definition__iexact=definition_search)
        return qs


class TopDefinitionUsageListView(BaseTopUsageListView):
    sub_app = 'definition'
    parent_list_view = DefinitionUsageListView
    template_name = 'extract/top_definition_usage_list.html'

    def get_item_data(self, item, parent_data):
        item['url'] = '{}?definition_search={}'.format(
            self.full_reverse('extract:definition-usage-list'), item['definition'])
        if "document_pk" in self.request.GET:
            item['definition_data'] = [i for i in parent_data
                                       if i['definition'] == item['definition']]
        return item

    def get_queryset(self):
        self.model = DefinitionUsage if "document_pk" in self.request.GET else ProjectDefinitionUsage
        qs = None
        if qs is None:
            qs = super().get_queryset() \
                .values("definition") \
                .annotate(count=Sum("count")) \
                .order_by("-count")
        return qs


class CourtUsageListView(BaseUsageListView):
    sub_app = 'court'
    model = CourtUsage
    extra_json_fields = ['court__name', 'court__alias', 'count']
    highlight_field = 'court__name'
    template_name = 'extract/court_usage_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        court_search = self.request.GET.get("court_search")
        if court_search:
            qs = qs.filter(court__name=court_search)
        return qs


class TopCourtUsageListView(BaseTopUsageListView):
    sub_app = 'court'
    model = CourtUsage
    parent_list_view = CourtUsageListView
    template_name = 'extract/top_court_usage_list.html'

    def get_item_data(self, item, parent_data):
        item['url'] = '{}?court_search={}'.format(
            self.full_reverse('extract:court-usage-list'), item['court__name'])
        if "document_pk" in self.request.GET:
            item['court_data'] = [i for i in parent_data
                                  if i['court__name'] == item['court__name']]
        return item

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.values("court__name", "court__alias") \
            .annotate(count=Sum("count")) \
            .order_by("-count")
        return qs


class CurrencyUsageListView(BaseUsageListView):
    sub_app = 'currency'
    model = CurrencyUsage
    extra_json_fields = ['currency', 'amount', 'amount_str']
    highlight_field = 'amount_str'
    template_name = 'extract/currency_usage_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        if "currency_search" in self.request.GET:
            qs = qs.filter(currency=self.request.GET['currency_search'])
        return qs


class TopCurrencyUsageListView(BaseTopUsageListView):
    sub_app = 'currency'
    model = CurrencyUsage
    parent_list_view = CurrencyUsageListView
    template_name = 'extract/top_currency_usage_list.html'

    def get_item_data(self, item, parent_data):
        item['url'] = self.full_reverse('extract:currency-usage-list') + '?currency_search=' + item['currency']
        if "document_pk" in self.request.GET:
            item['currency_data'] = [i for i in parent_data if i['currency'] == item['currency']]
        return item

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.values("currency", "usage_type") \
            .annotate(count=Count("pk")) \
            .order_by("-count")
        return qs


class RegulationUsageListView(BaseUsageListView):
    sub_app = 'regulation'
    model = RegulationUsage
    extra_json_fields = ['regulation_type', 'regulation_name', 'entity__name', 'count']
    template_name = 'extract/regulation_usage_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        regulation_search = self.request.GET.get("regulation_search")
        if regulation_search:
            qs = qs.filter(regulation_name=regulation_search)
        return qs


class TopRegulationUsageListView(BaseTopUsageListView):
    sub_app = 'regulation'
    model = RegulationUsage
    parent_list_view = RegulationUsageListView
    template_name = 'extract/top_regulation_usage_list.html'

    def get_item_data(self, item, parent_data):
        item['url'] = '{}?regulation_search={}'.format(
            self.full_reverse('extract:regulation-usage-list'), item['regulation_name'])
        if "document_pk" in self.request.GET:
            item['regulation_data'] = [i for i in parent_data
                                       if i['regulation_name'] == item['regulation_name']]
        return item

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.values("regulation_name", "regulation_type") \
            .annotate(count=Sum("count")) \
            .order_by("-count")
        return qs


class AmountUsageListView(BaseUsageListView):
    sub_app = 'amount'
    model = AmountUsage
    extra_json_fields = ['amount', 'amount_str', 'count']
    highlight_field = 'amount_str'
    template_name = 'extract/amount_usage_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        amount_search = self.request.GET.get("amount_search")
        if amount_search:
            qs = qs.filter(amount=float(amount_search))
        return qs


class TopAmountUsageListView(BaseTopUsageListView):
    sub_app = 'amount'
    model = AmountUsage
    parent_list_view = AmountUsageListView
    template_name = 'extract/top_amount_usage_list.html'

    def get_item_data(self, item, parent_data):
        item['url'] = '{}?amount_search={}'.format(
            self.full_reverse('extract:amount-usage-list'), item['amount'])
        if "document_pk" in self.request.GET:
            item['amount_data'] = [i for i in parent_data if i['amount'] == item['amount']]
        return item

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.values("amount") \
            .annotate(count=Sum("count")) \
            .order_by("-count")
        return qs


class DistanceUsageListView(BaseUsageListView):
    sub_app = 'distance'
    model = DistanceUsage
    extra_json_fields = ['amount', 'distance_type', 'count']
    template_name = 'extract/distance_usage_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        distance_type_search = self.request.GET.get("distance_type_search")
        distance_amount_search = self.request.GET.get("distance_amount_search")
        if distance_type_search and distance_amount_search:
            qs = qs.filter(distance_type=distance_type_search, amount=float(distance_amount_search))
        return qs


class TopDistanceUsageListView(BaseTopUsageListView):
    sub_app = 'distance'
    model = DistanceUsage
    parent_list_view = DistanceUsageListView
    template_name = 'extract/top_distance_usage_list.html'

    def get_item_data(self, item, parent_data):
        item['url'] = '{}?distance_type_search={}&distance_amount_search={}'.format(
            self.full_reverse('extract:distance-usage-list'), item['distance_type'], item['amount'])
        if "document_pk" in self.request.GET:
            item['distance_data'] = [i for i in parent_data
                                     if i['distance_type'] == item['distance_type']
                                     and i['amount'] == item['amount']]
        return item

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.values("distance_type", "amount") \
            .annotate(count=Sum("count")) \
            .order_by("-count")
        return qs


class PercentUsageListView(BaseUsageListView):
    sub_app = 'percent'
    model = PercentUsage
    extra_json_fields = ['amount', 'unit_type', 'total', 'count']
    template_name = 'extract/percent_usage_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        percent_type_search = self.request.GET.get("percent_type_search")
        percent_amount_search = self.request.GET.get("percent_amount_search")
        if percent_type_search and percent_amount_search:
            qs = qs.filter(unit_type=percent_type_search, amount=float(percent_amount_search))
        return qs


class TopPercentUsageListView(BaseTopUsageListView):
    sub_app = 'percent'
    model = PercentUsage
    parent_list_view = PercentUsageListView
    template_name = 'extract/top_percent_usage_list.html'

    def get_item_data(self, item, parent_data):
        item['url'] = '{}?percent_type_search={}&percent_amount_search={}'.format(
            self.full_reverse('extract:percent-usage-list'), item['unit_type'], item['amount'])
        if "document_pk" in self.request.GET:
            item['percent_data'] = [i for i in parent_data
                                    if i['unit_type'] == item['unit_type']
                                    and i['amount'] == item['amount']]
        return item

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.values("unit_type", "amount") \
            .annotate(count=Sum("count")) \
            .order_by("-count")
        return qs


class RatioUsageListView(BaseUsageListView):
    sub_app = 'ratio'
    model = RatioUsage
    extra_json_fields = ['amount', 'amount2', 'total', 'count']
    template_name = 'extract/ratio_usage_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        ratio_amount_search = self.request.GET.get("ratio_amount_search")
        ratio_amount2_search = self.request.GET.get("ratio_amount2_search")
        if ratio_amount_search and ratio_amount2_search:
            qs = qs.filter(amount=float(ratio_amount_search),
                           amount2=float(ratio_amount2_search))
        return qs


class TopRatioUsageListView(BaseTopUsageListView):
    sub_app = 'ratio'
    model = RatioUsage
    parent_list_view = RatioUsageListView
    template_name = 'extract/top_ratio_usage_list.html'

    def get_item_data(self, item, parent_data):
        item['url'] = '{}?ratio_amount_search={}&ratio_amount2_search={}'.format(
            self.full_reverse('extract:ratio-usage-list'), item['amount'], item['amount2'])
        if "document_pk" in self.request.GET:
            item['ratio_data'] = [i for i in parent_data
                                  if i['amount'] == item['amount']
                                  and i['amount2'] == item['amount2']]
        return item

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.values("amount", "amount2") \
            .annotate(count=Sum("count")) \
            .order_by("-count")
        return qs


class CitationUsageListView(BaseUsageListView):
    sub_app = 'citation'
    model = CitationUsage
    extra_json_fields = ['volume', 'reporter', 'reporter_full_name', 'page', 'page2',
                         'court', 'year', 'citation_str', 'count']
    highlight_field = 'citation_str'
    template_name = 'extract/citation_usage_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        citation_search = self.request.GET.get("citation_search")
        if citation_search:
            qs = qs.filter(citation_str=citation_search)
        return qs


class TopCitationUsageListView(BaseTopUsageListView):
    sub_app = 'citation'
    model = CitationUsage
    parent_list_view = CitationUsageListView
    template_name = 'extract/top_citation_usage_list.html'

    def get_item_data(self, item, parent_data):
        item['url'] = '{}?citation_search={}'.format(
            self.full_reverse('extract:citation-usage-list'), item['citation_str'])
        if "document_pk" in self.request.GET:
            item['citation_data'] = [i for i in parent_data
                                     if i['citation_str'] == item['citation_str']]
        return item

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.values("citation_str") \
            .annotate(count=Sum("count")) \
            .order_by("-count")
        return qs


class CopyrightUsageListView(BaseUsageListView):
    sub_app = 'copyright'
    model = CopyrightUsage
    extra_json_fields = ['copyright_str', 'count']
    highlight_field = 'copyright_str'
    template_name = 'extract/copyright_usage_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        copyright_search = self.request.GET.get("copyright_search")
        if copyright_search:
            qs = qs.filter(copyright_str=copyright_search)
        return qs


class TopCopyrightUsageListView(BaseTopUsageListView):
    sub_app = 'copyright'
    model = CopyrightUsage
    parent_list_view = CopyrightUsageListView
    template_name = 'extract/top_copyright_usage_list.html'

    def get_item_data(self, item, parent_data):
        item['url'] = '{}?copyright_search={}'.format(
            self.full_reverse('extract:copyright-usage-list'), url_quote(item['copyright_str']))
        if "document_pk" in self.request.GET:
            item['copyright_data'] = [i for i in parent_data
                                      if i['copyright_str'] == item['copyright_str']]
        return item

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.values("copyright_str") \
            .annotate(count=Sum("count")) \
            .order_by("-count")
        return qs


class TrademarkUsageListView(BaseUsageListView):
    sub_app = 'trademark'
    model = TrademarkUsage
    extra_json_fields = ['trademark', 'count']
    highlight_field = 'trademark'
    template_name = 'extract/trademark_usage_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        trademark_search = self.request.GET.get("trademark_search")
        if trademark_search:
            qs = qs.filter(trademark=trademark_search)
        return qs


class TopTrademarkUsageListView(BaseTopUsageListView):
    sub_app = 'trademark'
    model = TrademarkUsage
    parent_list_view = TrademarkUsageListView
    template_name = 'extract/top_trademark_usage_list.html'

    def get_item_data(self, item, parent_data):
        item['url'] = '{}?trademark_search={}'.format(
            self.full_reverse('extract:trademark-usage-list'), url_quote(item['trademark']))
        if "document_pk" in self.request.GET:
            item['trademark_data'] = [i for i in parent_data
                                      if i['trademark'] == item['trademark']]
        return item

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.values("trademark") \
            .annotate(count=Sum("count")) \
            .order_by("-count")
        return qs


class UrlUsageListView(BaseUsageListView):
    sub_app = 'url'
    model = UrlUsage
    extra_json_fields = ['source_url', 'count']
    highlight_field = 'source_url'
    extra_item_map = dict(
        goto_url=lambda i: i['source_url'] if i['source_url'].lower().startswith('http')
        else 'http://' + i['source_url']
    )
    template_name = 'extract/url_usage_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        url_search = self.request.GET.get("url_search")
        if url_search:
            qs = qs.filter(source_url=url_search)
        return qs


class TopUrlUsageListView(BaseTopUsageListView):
    sub_app = 'url'
    model = UrlUsage
    parent_list_view = UrlUsageListView
    template_name = 'extract/top_url_usage_list.html'

    def get_item_data(self, item, parent_data):
        item['goto_url'] = item['source_url'] if item['source_url'].lower().startswith('http') \
            else 'http://' + item['source_url']
        item['url'] = '{}?url_search={}'.format(
            self.full_reverse('extract:url-usage-list'), url_quote(item['source_url']))
        if "document_pk" in self.request.GET:
            item['url_data'] = [i for i in parent_data if i['source_url'] == item['source_url']]
        return item

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.values("source_url") \
            .annotate(count=Sum("count")) \
            .order_by("-count")
        return qs


class DateUsageToICalView(DateUsageListView):
    sub_app = 'date'

    def get(self, request, *args, **kwargs):
        document_pk = request.GET.get('document_pk')
        if not document_pk:
            return Http404("Document pk is not defined.")
        if not request.user.can_view_document(Document.objects.get(pk=document_pk)):
            response = HttpResponseForbidden()
            msg = 'You do not have access to this document.'
            response.content = render(request, '403.html', context={'message': msg})
            return response

        sample_length = 100
        # Create calendar
        cal = icalendar.Calendar()
        cal.add('prodid', 'ContraxSuite (https://contraxsuite.com)')
        cal.add('version', '1.0.3')

        # Filter to text unit
        for du in self.get_json_data()['data']:
            event = icalendar.Event()
            event.add("summary", "Calendar reminder for document {0}, text unit {1}:\n{2}"
                      .format(du['document__name'], du['text_unit_id'],
                              du['text_unit__textunittext__text'][:sample_length]))
            event.add("dtstart", du['date'])
            event.add("dtend", du['date'])
            event.add("dtstamp", du['date'])
            cal.add_component(event)

        filename = "document-{0}.ics".format(document_pk)

        response = HttpResponse(cal.to_ical(), content_type='text/calendar; charset=utf8')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        return response


class PartySummary(DetailView):
    sub_app = 'party'
    model = Party
    template_name = 'extract/party_summary.html'


class PartyNetworkChartView(PartyUsageListView):
    sub_app = 'party'
    template_name = "extract/party_network_chart.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Var 1. - takes ~7sec on 650K rec
        # parties = defaultdict(list)
        # for result in self.get_queryset() \
        #         .values('party__name', 'text_unit__document_id') \
        #         .order_by('party__name', 'text_unit__document_id'):
        #     parties[result['text_unit__document_id']].append(result['party__name'].upper())
        # parties = [i for sub in parties.values() for i in sub if len(set(sub)) > 1]

        # Var 2. - takes ~25 sec on 650K rec
        # ids = PartyUsage.objects\
        #     .values('text_unit__document_id', 'party__name')\
        #     .distinct()\
        #     .values('text_unit__document_id')\
        #     .annotate(c=Count('party__name', distinct=True))\
        #     .filter(c__gt=1)\
        #     .values_list('text_unit__document_id', flat=True)
        # parties = PartyUsage.objects\
        #     .filter(text_unit__document_id__in=ids)\
        #     .values_list('party__name', flat=True)

        # Var 3. so simplify just to retrieve all party names - takes ~1sec on 7.8K rec
        ctx['parties'] = sorted(
            Party.objects.filter(partyusage__isnull=False).distinct().values_list('name', flat=True))
        return ctx

    def get_json_data(self):
        party_name = self.request.GET.get('party_name_iexact')
        qs = self.get_queryset() \
            .values('party__name', 'document_id') \
            .order_by('party__name', 'document_id')
        if party_name:
            doc_ids = Document.objects \
                .filter(textunit__partyusage__party__name=party_name) \
                .values_list('id', flat=True)
            qs = qs.filter(document_id__in=doc_ids)

        parties = defaultdict(set)
        for item in qs:
            parties[item['document_id']].add(item['party__name'])
        party_doc_edge = [list(itertools.combinations(i, 2))
                          for i in parties.values() if len(i) > 1]
        chart_nodes = []
        processed_nodes = []
        for group_num, parties in enumerate(party_doc_edge, start=1):
            to_process = {j for sub in parties for j in sub if j not in processed_nodes}
            chart_nodes += [{"id": i,
                             "group": group_num,
                             "url": reverse("extract:party-usage-list") + '?party_search_iexact=' + i}
                            for i in to_process]
            processed_nodes.extend(to_process)
        chart_links = [{"source": i, "target": j, "value": 2}
                       for g in party_doc_edge for i, j in g]

        members = {party_name}
        while 1:
            members1 = {i["source"] for i in chart_links
                        if i["target"] in members and i["source"] not in members}
            members2 = {i["target"] for i in chart_links
                        if i["source"] in members and i["target"] not in members}
            if not members1 and not members2:
                break
            members = members | members1 | members2

        chart_nodes = [i for i in chart_nodes if i['id'] in members]
        chart_links = [i for i in chart_links
                       if i['source'] in members or i['target'] in members]
        return {"nodes": chart_nodes, "links": chart_links}


class TermSearchView(apps.common.mixins.JSONResponseView):

    def get(self, request, *args, **kwargs):
        return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseForbidden()
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            return JsonResponse('Wrong username or password.', status=401)
        request.user = user
        return super().post(request, *args, **kwargs)

    def get_json_data(self, request, *args, **kwargs):
        request.GET = request.POST
        data = TermUsageListView(request=request).get_json_data()
        if request.POST.get('as_dict') in [None, 'false']:
            ret = [dict(
                document_id=item['document_id'],
                term=item['term__term'],
                count=item['count'],
                text_unit_id=item['text_unit_id']) for item in data['data']]
        else:
            ret = [(item['document_id'],
                    item['count'],
                    item['term__term'],
                    item['text_unit_id']) for item in data['data']]
            ret = [('Document ID', 'Term', 'Count', 'Text Unit ID')] + ret
        return ret


# TODO: seems it doesn't work no more
class GeoEntityUsageGoogleMapView(apps.common.mixins.AjaxResponseMixin, TemplateView):
    sub_app = 'geoentity'
    template_name = "extract/geo_entity_usage_map.html"

    def get_entities(self):
        qs = GeoEntityUsageListView(request=self.request).get_queryset()
        if self.request.GET.get('usa_only') == 'true':
            entities = list(qs.
                            filter(Q(entity__category='Countries',
                                     entity__name='United States') |
                                   Q(entity__category='US States')).
                            values('entity__name',
                                   latitude=F('entity__latitude'),
                                   longitude=F('entity__longitude')).
                            annotate(count=Sum('count')).
                            order_by())
        else:
            country_entities = list(qs.
                                    filter(entity__category='Countries').
                                    values('entity__name',
                                           latitude=F('entity__latitude'),
                                           longitude=F('entity__longitude')).
                                    annotate(count=Sum('count')).
                                    order_by())
            country_entities = {i['entity__name']: i for i in country_entities}
            other_entities = qs. \
                filter(entity__entity_a_set__relation_type="subdivision",
                       entity__entity_a_set__entity_b__category="Countries"). \
                values(entity__name=F('entity__entity_a_set__entity_b__name'),
                       latitude=F('entity__entity_a_set__entity_b__latitude'),
                       longitude=F('entity__entity_a_set__entity_b__longitude')). \
                annotate(count=Sum('count')). \
                order_by()
            other_entities = {i['entity__name']: i
                              for i in other_entities}
            for entity_name, info in other_entities.items():
                if entity_name in country_entities:
                    country_entities[entity_name]['count'] += info['count']
                else:
                    country_entities[entity_name] = info
            entities = list(country_entities.values())
        return entities

    def get_json_data(self):
        entities = self.get_entities()
        # for entity in entities:
        #     if not entity['latitude']:
        #         g = geocoder.google(entity['entity__name'])
        #         if not g.latlng and ',' in entity['entity__name']:
        #             g = geocoder.google(entity['entity__name'].split(',')[0])
        #         try:
        #             entity['latitude'], entity['longitude'] = g.latlng
        #         except ValueError:
        #             pass
        return entities


class GeoEntityUsageGoogleChartView(GeoEntityUsageGoogleMapView):
    sub_app = 'geoentity'
    template_name = "extract/geo_entity_usage_chart.html"

    def get_json_data(self):
        entities = self.get_entities()
        data = [['country', 'count']] + [[e['entity__name'], e['count']] for e in entities]
        return data
