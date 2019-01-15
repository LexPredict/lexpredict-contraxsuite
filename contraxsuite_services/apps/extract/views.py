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
from collections import defaultdict
import datetime
import itertools
import json
from urllib.parse import quote as url_quote

# Third-party import
import icalendar

# Django imports
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from django.db.models import Count, F, Max, Min, Sum, Q, Value, IntegerField
from django.db.models.functions import TruncMonth
from django.http import Http404, HttpResponseForbidden, HttpResponse
from django.views.generic import DetailView, TemplateView

# Project imports
from apps.common.mixins import (
    AjaxResponseMixin, JqPaginatedListView, JSONResponseView, TypeaheadView)
from apps.document.models import Document
from apps.extract.models import (
    AmountUsage, CitationUsage, CopyrightUsage, CourtUsage, CurrencyUsage,
    DateDurationUsage, DateUsage, DefinitionUsage, DistanceUsage,
    GeoAliasUsage, GeoAlias, GeoEntity, GeoEntityUsage, Party, PartyUsage, PercentUsage,
    RatioUsage, RegulationUsage, TermUsage, TrademarkUsage, UrlUsage)

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.7/LICENSE"
__version__ = "1.1.7"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class BaseUsageListView(JqPaginatedListView):
    json_fields = ['text_unit__document__pk', 'text_unit__document__name',
                   'text_unit__document__description', 'text_unit__document__document_type__title',
                   'text_unit__text', 'text_unit__pk']
    limit_reviewers_qs_by_field = 'text_unit__document'
    field_types = dict(count=int)
    highlight_field = ''
    extra_item_map = dict()
    search_field = ''

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = reverse(
                'document:document-detail', args=[item['text_unit__document__pk']])
            item['detail_url'] = reverse(
                'document:text-unit-detail', args=[item['text_unit__pk']]) + \
                '?highlight=' + item.get(self.highlight_field, '')
            for field_name, field_lambda in self.extra_item_map.items():
                item[field_name] = field_lambda(item)
        return data

    def get_queryset(self):
        qs = super().get_queryset()
        if "document_pk" in self.request.GET:
            qs = qs.filter(text_unit__document__pk=self.request.GET['document_pk'])
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.search_field:
            ctx[self.search_field] = self.request.GET.get(self.search_field, "")
        return ctx


class BaseTopUsageListView(JqPaginatedListView):
    limit_reviewers_qs_by_field = 'text_unit__document'
    sort_by = None

    def get_template_names(self):
        return [super().get_template_names()[0].replace('extract/', 'extract/top_')]

    def get_json_data(self, **kwargs):
        data = super().get_json_data(**kwargs)
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
            qs = qs.filter(text_unit__document__pk=self.request.GET['document_pk'])
        return qs


class TermUsageListView(BaseUsageListView):
    sub_app = 'term'
    model = TermUsage
    extra_json_fields = ['term__term', 'count']
    highlight_field = 'term__term'
    search_field = 'term_search'

    def get_queryset(self):
        qs = super().get_queryset()
        term_search = self.request.GET.get("term_search", "")

        if term_search:
            # qs = self.filter(term_search, qs,
            #                  _or_lookup='term__term__exact',
            #                  _and_lookup='text_unit__text__icontains',
            #                  _not_lookup='text_unit__text__icontains')
            qs = qs.filter(term__term__icontains=term_search)
        # filter out duplicated Terms (equal terms, but diff. term sources)
        # qs = qs.order_by('term__term').distinct('term__term', 'text_unit__pk')
        return qs


class TopTermUsageListView(BaseTopUsageListView):
    sub_app = 'term'
    model = TermUsage
    parent_list_view = TermUsageListView

    def get_item_data(self, item, parent_data=None):
        item['url'] = reverse('extract:term-usage-list') + '?term_search=' + item['term__term']
        if "document_pk" in self.request.GET:
            item['term_data'] = [i for i in parent_data if i['term__term'] == item['term__term']]
        return item

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.values('term__term', 'term__source') \
            .annotate(count=Sum('count')) \
            .values('term__term', 'count') \
            .order_by('-count')
        qs = sorted([dict(j) for j in set([tuple(i.items()) for i in qs])],
                    key=lambda i: i['count'], reverse=True)
        return qs


class GeoEntityListView(JqPaginatedListView):
    model = GeoEntity

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['alias'] = ', '.join(
                GeoAlias.objects.filter(entity_id=item['pk']).values_list('alias', flat=True))
        return data


class GeoEntityPriorityUpdateView(JSONResponseView):

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
    extra_json_fields = ['entity__name', 'entity__category', 'count']
    highlight_field = 'entity__name'
    search_field = 'entity_search'

    def get_json_data(self, **kwargs):
        entity_data = super().get_json_data()['data']
        alias_data = GeoAliasUsageListView(request=self.request).get_json_data()['data']
        collapse_aliases = json.loads(self.request.GET.get('collapse_aliases', 'true'))

        if collapse_aliases:
            for alias in alias_data:
                added = False
                for entity in entity_data:
                    if entity['text_unit__pk'] == alias['text_unit__pk'] and \
                                    entity['entity__name'] == alias['alias__entity__name']:
                        entity['count'] += alias['count']
                        added = True
                if not added:
                    alias['entity__name'] = alias['alias__entity__name']
                    alias['entity__category'] = alias['alias__entity__category']
                    alias['url'] = reverse('document:document-detail',
                                           args=[alias['text_unit__document__pk']])
                    alias['detail_url'] = reverse('document:text-unit-detail',
                                                  args=[alias['text_unit__pk']]) + \
                                          '?highlight=' + alias['alias__alias']
                    entity_data.append(alias)
        else:
            for alias in alias_data:
                alias['entity__name'] = alias['alias__entity__name']
                alias['entity__category'] = alias['alias__entity__category']
            entity_data.extend(alias_data)

        return {'data': entity_data,
                'total_records': len(entity_data),
                'collapse_aliases': collapse_aliases}

    def get_queryset(self):
        qs = super().get_queryset()
        entity_search = self.request.GET.get("entity_search")
        if entity_search:
            entity_search_list = entity_search.split(",")
            qs = qs.filter(entity__name__in=entity_search_list)
        if "party_pk" in self.request.GET:
            qs = qs.filter(
                text_unit__document__textunit__partyusage__party__pk=self.request.GET['party_pk']) \
                .distinct()
        return qs


class TopGeoEntityUsageListView(GeoEntityUsageListView):
    sub_app = 'geoentity'
    template_name = "extract/top_geo_entity_usage_list.html"

    def get_json_data(self, **kwargs):
        document_id = self.request.GET.get("document_pk")
        party_id = self.request.GET.get("party_pk")

        entities = {i['name']: i for i in GeoEntity.objects.values('name', 'category').annotate(
            count=Value(0, output_field=IntegerField()))}
        entites_filter_opts = dict(geoentityusage__isnull=False)
        aliases_filter_opts = dict(geoalias__geoaliasusage__isnull=False)

        if document_id:
            entites_filter_opts['geoentityusage__text_unit__document_id'] = document_id
            aliases_filter_opts['geoalias__geoaliasusage__text_unit__document_id'] = document_id
        elif party_id:
            entites_filter_opts[
                'geoentityusage__text_unit__document__textunit__partyusage__party__pk'] = party_id
            aliases_filter_opts[
                'geoalias__geoaliasusage__text_unit__document__textunit__partyusage__party__pk'] = party_id

        entities_data = list(GeoEntity.objects
                             .filter(**entites_filter_opts)
                             .values('name', 'category')
                             .annotate(count=Sum('geoentityusage__count', distinct=True)))
        aliases_data = list(GeoEntity.objects
                            .filter(**aliases_filter_opts)
                            .values('name', 'category')
                            .annotate(count=Sum('geoalias__geoaliasusage__count')))
        for i in entities_data:
            entities[i['name']]['count'] += i['count']
        for i in aliases_data:
            entities[i['name']]['count'] += i['count']

        if document_id or party_id:
            entities_data = super().get_json_data()['data']
            for entity in entities_data:
                entity_data = entities[entity['entity__name']].get('entity_data', [])
                entity_data.append(entity)
                entities[entity['entity__name']]['entity_data'] = entity_data

        entities = sorted([i for i in entities.values() if i['count']], key=lambda i: -i['count'])
        for i in entities:
            i['url'] = reverse('extract:geo-entity-usage-list') + \
                       '?entity_search=' + i['name']

        return {'data': entities, 'total_records': len(entities)}


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
                text_unit__document__textunit__partyusage__party__pk=self.request.GET['party_pk']) \
                .distinct()
        return qs


class TypeaheadTermTerm(TypeaheadView):

    def get_json_data(self, request, *args, **kwargs):
        qs = TermUsage.objects.all()
        if "q" in request.GET:
            qs = qs.filter(term__term__icontains=request.GET.get("q")) \
                .values('term__term').annotate(s=Sum('count')).order_by('-s')
        results = []
        for t in qs:
            results.append({"value": t['term__term']})
            results.append({"value": '-%s' % t['term__term']})
        return results


class TypeaheadGeoEntityName(TypeaheadView):

    def get_json_data(self, request, *args, **kwargs):
        qs = GeoEntityUsage.objects.all()
        if "q" in request.GET:
            qs = qs.filter(entity__name__icontains=request.GET.get("q")) \
                .values('entity__name').annotate(s=Sum('count')).order_by('-s')
        return [{"value": i['entity__name']} for i in qs]


class TypeaheadPartyName(TypeaheadView):

    def get_json_data(self, request, *args, **kwargs):
        qs = PartyUsage.objects.all()
        if "q" in request.GET:
            qs = qs.filter(party__name__icontains=request.GET.get("q")) \
                .values('party__name').annotate(s=Sum('count')).order_by('-s')
        return [{"value": i['party__name']} for i in qs]


class PartyUsageListView(BaseUsageListView):
    sub_app = 'party'
    model = PartyUsage
    extra_json_fields = ['party__name', 'party__type_abbr', 'party__pk', 'count']
    highlight_field = 'party__name'
    extra_item_map = dict(
        party_summary_url=lambda x: reverse('extract:party-summary', args=[x['party__pk']]))
    search_field = 'party_search'

    def get_queryset(self):
        qs = super().get_queryset()
        party_search = self.request.GET.get("party_search", "")
        if party_search:
            party_search_list = party_search.split(",")
            qs = qs.filter(party__name__in=party_search_list)
        party_search_iexact = self.request.GET.get("party_search_iexact", "")
        if party_search_iexact:
            qs = qs.filter(party__name__iexact=party_search_iexact)
        qs = qs.select_related('party', 'text_unit', 'text_unit__document')
        return qs


class TopPartyUsageListView(BaseTopUsageListView):
    sub_app = 'party'
    model = PartyUsage
    parent_list_view = PartyUsageListView

    def get_item_data(self, item, parent_data):
        item['url'] = reverse('extract:party-usage-list') + '?party_search=' + item['party__name']
        item['party_summary_url'] = reverse('extract:party-summary', args=[item['party__pk']])
        if "document_pk" in self.request.GET:
            item['party_data'] = [i for i in parent_data if i['party__name'] == item['party__name']]
        return item

    def get_queryset(self):
        qs = super().get_queryset()
        if "party_pk" in self.request.GET:
            qs = qs.filter(party__pk=self.request.GET['party_pk'])
        qs = qs.values("party__name", "party__type_abbr", "party__pk") \
            .annotate(count=Sum("count")) \
            .order_by("-count")
        return qs


class DateUsageListView(BaseUsageListView):
    sub_app = 'date'
    model = DateUsage
    extra_json_fields = ['date', 'count']

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

    def get_item_data(self, item, parent_data):
        item['url'] = reverse('extract:date-usage-list') + '?date_search=' + item['date'].isoformat()
        if "document_pk" in self.request.GET:
            item['date_data'] = [i for i in parent_data if i['date'] == item['date']]
        return item

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.values("date") \
            .annotate(count=Sum("count")) \
            .order_by("-count")
        return qs


class DateUsageTimelineView(JqPaginatedListView):
    sub_app = 'date'
    model = DateUsage
    template_name = "extract/date_usage_timeline.html"
    limit_reviewers_qs_by_field = 'text_unit__document'

    def get_json_data(self, **kwargs):
        per_month = json.loads(self.request.GET.get('per_month', 'false'))

        qs = super().get_queryset()
        if "document_pk" in self.request.GET:
            qs = qs.filter(text_unit__document__pk=self.request.GET['document_pk'])

        if per_month:
            qs = qs.order_by('date') \
                .annotate(start=TruncMonth('date')) \
                .values('start') \
                .annotate(count=Sum('count')).order_by()
            data = list(qs)
            visible_interval = 360
        else:
            qs = qs.order_by('date') \
                .values(start=F('date')) \
                .annotate(count=Sum('count'))
            data = list(qs)
            date_list_view = DateUsageListView(request=self.request)
            date_data = date_list_view.get_json_data()['data']
            visible_interval = 180

        max_value = qs.aggregate(m=Max('count'))['m']
        min_value = qs.aggregate(m=Min('count'))['m']
        range_value = max_value - min_value

        for item in data:
            item['weight'] = (item['count'] - min_value) / range_value
            if per_month:
                item['url'] = reverse('extract:date-usage-list') + \
                              '?month_search=' + item['start'].isoformat()
                item['content'] = '{}, {}: {}'.format(item['start'].strftime('%B'),
                                                      item['start'].year, item['count'])
            else:
                item['url'] = reverse('extract:date-usage-list') + \
                              '?date_search=' + item['start'].isoformat()
                item['content'] = '{}: {}'.format(item['start'].isoformat(), item['count'])
                item['date_data'] = [i for i in date_data if i['date'] == item['start']]

        initial_start_date = datetime.date.today() - datetime.timedelta(days=visible_interval)
        initial_end_date = datetime.date.today() + datetime.timedelta(days=visible_interval)
        return {'data': data,
                'per_month': per_month,
                'initial_start_date': initial_start_date,
                'initial_end_date': initial_end_date}


class DateUsageCalendarView(JqPaginatedListView):
    sub_app = 'date'
    model = DateUsage
    template_name = "extract/date_usage_calendar.html"
    limit_reviewers_qs_by_field = 'text_unit__document'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        documents = Document.objects.all()
        if self.request.user.is_reviewer:
            documents = documents.filter(
                taskqueue__user_id=self.request.user.pk,
                textunit__dateusage__isnull=False).distinct()
        ctx['documents'] = documents
        return ctx

    def get_json_data(self, **kwargs):
        qs = super().get_queryset()
        qs = qs.filter(date__lte=datetime.date.today() + datetime.timedelta(365*100))

        if self.request.GET.get("document_id"):
            qs = qs.filter(text_unit__document__pk=self.request.GET['document_id'])

        qs = qs.order_by('date') \
            .values('date') \
            .annotate(count=Sum('count'))
        data = list(qs)

        max_value = qs.aggregate(m=Max('count'))['m']

        min_date = qs.aggregate(m=Min('date'))['m']
        max_date = qs.aggregate(m=Max('date'))['m']

        for item in data:
            item['weight'] = item['count'] / max_value
            item['url'] = reverse('extract:date-usage-list') + \
                          '?date_search=' + item['date'].isoformat()

        return {'data': data,
                'min_year': min_date.year,
                'max_year': max_date.year}


class DateDurationUsageListView(BaseUsageListView):
    sub_app = 'duration'
    model = DateDurationUsage
    extra_json_fields = ['amount', 'amount_str', 'duration_type', 'duration_days', 'count']
    highlight_field = 'amount_str'

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
    # template_name = "extract/top_date_duration_usage_list.html"
    parent_list_view = DateDurationUsageListView

    @staticmethod
    def sort_by(i):
        return -i['duration_days']

    def get_item_data(self, item, parent_data):
        item['url'] = reverse('extract:date-duration-usage-list') + \
                      '?duration_search=' + str(item['duration_days'])
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

    def get_queryset(self):
        qs = super().get_queryset()
        definition_search = self.request.GET.get("definition_search")
        if definition_search:
            qs = qs.filter(definition=definition_search)
        return qs


class TopDefinitionUsageListView(BaseTopUsageListView):
    sub_app = 'definition'
    model = DefinitionUsage
    parent_list_view = DefinitionUsageListView

    def get_item_data(self, item, parent_data):
        item['url'] = reverse('extract:definition-usage-list') + \
                      '?definition_search=' + item['definition']
        if "document_pk" in self.request.GET:
            item['definition_data'] = [i for i in parent_data
                                       if i['definition'] == item['definition']]
        return item

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.values("definition") \
            .annotate(count=Sum("count")) \
            .order_by("-count")
        return qs


class CourtUsageListView(BaseUsageListView):
    sub_app = 'court'
    model = CourtUsage
    extra_json_fields = ['court__name', 'court__alias', 'count']
    highlight_field = 'court__name'

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

    def get_item_data(self, item, parent_data):
        item['url'] = reverse('extract:court-usage-list') + \
                      '?court_search=' + item['court__name']
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
    extra_json_fields = ['usage_type', 'currency', 'amount', 'amount_str']
    highlight_field = 'amount_str'

    def get_queryset(self):
        qs = super().get_queryset()
        if "currency_search" in self.request.GET:
            qs = qs.filter(currency=self.request.GET['currency_search'])
        return qs


class TopCurrencyUsageListView(BaseTopUsageListView):
    sub_app = 'currency'
    model = CurrencyUsage
    parent_list_view = CurrencyUsageListView

    def get_item_data(self, item, parent_data):
        item['url'] = reverse('extract:currency-usage-list') + '?currency_search=' + item['currency']
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

    def get_item_data(self, item, parent_data):
        item['url'] = reverse('extract:regulation-usage-list') + \
                      '?regulation_search=' + item['regulation_name']
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

    def get_item_data(self, item, parent_data):
        item['url'] = reverse('extract:amount-usage-list') + \
                      '?amount_search={}'.format(item['amount'])
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

    def get_item_data(self, item, parent_data):
        item['url'] = reverse('extract:distance-usage-list') + \
                      '?distance_type_search={}&distance_amount_search={}'.format(
                          item['distance_type'], item['amount'])
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

    def get_item_data(self, item, parent_data):
        item['url'] = reverse('extract:percent-usage-list') + \
                      '?percent_type_search={}&percent_amount_search={}'.format(
                          item['unit_type'], item['amount'])
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

    def get_item_data(self, item, parent_data):
        item['url'] = reverse('extract:ratio-usage-list') + \
                      '?ratio_amount_search={}&ratio_amount2_search={}'.format(
                          item['amount'], item['amount2'])
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

    def get_item_data(self, item, parent_data):
        item['url'] = reverse('extract:citation-usage-list') + \
                      '?citation_search={}'.format(item['citation_str'])
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

    def get_item_data(self, item, parent_data):
        item['url'] = reverse('extract:copyright-usage-list') + \
                      '?copyright_search={}'.format(url_quote(item['copyright_str']))
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

    def get_item_data(self, item, parent_data):
        item['url'] = reverse('extract:trademark-usage-list') + \
                      '?trademark_search={}'.format(url_quote(item['trademark']))
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

    def get_item_data(self, item, parent_data):
        item['goto_url'] = item['source_url'] if item['source_url'].lower().startswith('http')\
            else 'http://' + item['source_url']
        item['url'] = reverse('extract:url-usage-list') + \
                      '?url_search={}'.format(url_quote(item['source_url']))
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

        sample_length = 100
        # Create calendar
        cal = icalendar.Calendar()
        cal.add('prodid', 'ContraxSuite (https://contraxsuite.com)')
        cal.add('version', '1.0.3')

        # Filter to text unit
        for du in self.get_json_data()['data']:
            event = icalendar.Event()
            event.add("summary", "Calendar reminder for document {0}, text unit {1}:\n{2}"
                      .format(du['text_unit__document__name'], du['text_unit__pk'],
                              du['text_unit__text'][:sample_length]))
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
        parties = defaultdict(list)
        for result in self.get_queryset() \
                .values('party__name', 'text_unit__document_id') \
                .order_by('party__name', 'text_unit__document_id'):
            parties[result['text_unit__document_id']].append(result['party__name'].upper())
        parties = [i for sub in parties.values() for i in sub if len(set(sub)) > 1]
        ctx['parties'] = sorted(set(parties))
        return ctx

    def get_json_data(self):
        parties = defaultdict(list)
        for result in self.get_queryset()\
                .values('party__name', 'text_unit__document_id')\
                .order_by('party__name', 'text_unit__document_id'):
            parties[result['text_unit__document_id']].append(result['party__name'].upper())
        party_doc_edge = [list(itertools.combinations(set(i), 2))
                          for i in parties.values() if len(set(i)) > 1]
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

        if 'party_name_iexact' in self.request.GET:
            party_name = self.request.GET.get('party_name_iexact', chart_nodes[0]['id'])
            members = {party_name}
            while 1:
                members1 = {i["source"] for i in chart_links if i["target"] in members
                           and i["source"] not in members}
                members2 = {i["target"] for i in chart_links if i["source"] in members
                           and i["target"] not in members}
                if not members1 and not members2:
                    break
                members = members | members1 | members2

            chart_nodes = [i for i in chart_nodes if i['id'] in members]
            chart_links = [i for i in chart_links if i['source'] in members or i['target'] in members]
        return {"nodes": chart_nodes, "links": chart_links}


class TermSearchView(JSONResponseView):

    def get(self, request, *args, **kwargs):
        return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseForbidden()
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            return HttpResponse('Wrong username or password.',
                                content_type="application/json",
                                status=401)
        request.user = user
        return super().post(request, *args, **kwargs)

    def get_json_data(self, request, *args, **kwargs):
        request.GET = request.POST
        data = TermUsageListView(request=request).get_json_data()
        if request.POST.get('as_dict') in [None, 'false']:
            ret = [dict(
                    document_id=item['text_unit__document__pk'],
                    term=item['term__term'],
                    count=item['count'],
                    text_unit_id=item['text_unit__pk']) for item in data['data']]
        else:
            ret = [(item['text_unit__document__pk'],
                    item['count'],
                    item['term__term'],
                    item['text_unit__pk']) for item in data['data']]
            ret = [('Document ID', 'Term', 'Count', 'Text Unit ID')] + ret
        return ret


class GeoEntityUsageGoogleMapView(AjaxResponseMixin, TemplateView):
    sub_app = 'geoentity'
    template_name = "extract/geo_entity_usage_map.html"

    def get_entities(self):
        if self.request.GET.get('usa_only') == 'true':
            entities = list(GeoEntityUsage.objects.
                            filter(Q(entity__category='Countries',
                                     entity__name='United States') |
                                   Q(entity__category='US States')).
                            values('entity__name',
                                   latitude=F('entity__latitude'),
                                   longitude=F('entity__longitude')).
                            annotate(count=Sum('count')).
                            order_by())
        else:
            country_entities = list(GeoEntityUsage.objects.
                                    filter(entity__category='Countries').
                                    values('entity__name',
                                           latitude=F('entity__latitude'),
                                           longitude=F('entity__longitude')).
                                    annotate(count=Sum('count')).
                                    order_by())
            country_entities = {i['entity__name']: i for i in country_entities}
            other_entities = GeoEntityUsage.objects. \
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
