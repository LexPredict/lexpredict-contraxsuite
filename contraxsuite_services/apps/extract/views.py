# -*- coding: utf-8 -*-

# Future imports
from __future__ import absolute_import, unicode_literals

# Standard imports
import datetime
import json
import geocoder

# Django imports
from django.core.urlresolvers import reverse
from django.db.models import Count, F, Max, Min, Sum, Q
from django.db.models.functions import TruncMonth
from django.views.generic import DetailView, TemplateView

# Project imports
from apps.common.mixins import (
    AjaxListView, AjaxResponseMixin, JqPaginatedListView, TypeaheadView)
from apps.document.models import Document
from apps.extract.models import (
    CourtUsage, CurrencyUsage,
    DateDurationUsage, DateUsage, DefinitionUsage,
    GeoAliasUsage, GeoEntity, GeoEntityUsage,
    Term, TermUsage, Party, PartyUsage)

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.1/LICENSE"
__version__ = "1.0.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TermUsageListView(JqPaginatedListView):
    model = TermUsage
    json_fields = ['text_unit__document__pk', 'text_unit__document__name',
                   'text_unit__document__description', 'text_unit__document__document_type',
                   'term__term', 'count', 'text_unit__text', 'text_unit__pk']
    limit_reviewers_qs_by_field = 'text_unit__document'
    field_types = dict(count=int)

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = reverse('document:document-detail',
                                  args=[item['text_unit__document__pk']])
            item['detail_url'] = reverse('document:text-unit-detail',
                                         args=[item['text_unit__pk']]) + \
                                 '?highlight=' + item['term__term']
        return data

    def get_queryset(self):
        qs = super().get_queryset()
        term_search = self.request.GET.get("term_search", "")

        if term_search:
            qs = self.filter(term_search, qs,
                             _or_lookup='term__term__exact',
                             _and_lookup='text_unit__text__icontains',
                             _not_lookup='text_unit__text__icontains')

        if "document_pk" in self.request.GET:
            qs = qs.filter(text_unit__document__pk=self.request.GET['document_pk'])

        # filter out duplicated Terms (equal terms, but diff. term sources)
        qs = qs.order_by('term__term').distinct('term__term', 'text_unit__pk')
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['term_search'] = self.request.GET.get("term_search", "")
        return ctx


class TopTermUsageListView(JqPaginatedListView):
    model = TermUsage
    template_name = "extract/top_term_usage_list.html"
    limit_reviewers_qs_by_field = 'text_unit__document'

    def get_json_data(self, **kwargs):
        data = list(self.get_queryset())
        if "document_pk" in self.request.GET:
            term_list_view = TermUsageListView(request=self.request)
            term_data = term_list_view.get_json_data()['data']
        for item in data:
            item['url'] = reverse('extract:term-usage-list') + \
                          '?term_search=' + item['term__term']
            if "document_pk" in self.request.GET:
                item['term_data'] = [i for i in term_data
                                     if i['term__term'] == item['term__term']]
        return {'data': data, 'total_records': len(data)}

    def get_queryset(self):
        qs = super().get_queryset()

        if "document_pk" in self.request.GET:
            qs = qs.filter(text_unit__document__pk=self.request.GET['document_pk'])

        qs = qs.values('term__term', 'term__source') \
            .annotate(count=Sum('count')) \
            .values('term__term', 'count') \
            .order_by('-count')
        qs = sorted([dict(j) for j in set([tuple(i.items()) for i in qs])],
                    key=lambda i: i['count'], reverse=True)
        return qs


class GeoEntityUsageListView(AjaxListView):
    model = GeoEntityUsage
    json_fields = ['text_unit__document__pk', 'text_unit__document__name',
                   'text_unit__document__description', 'text_unit__document__document_type',
                   'entity__name', 'entity__category', 'count',
                   'text_unit__pk', 'text_unit__text']
    limit_reviewers_qs_by_field = 'text_unit__document'

    def get_json_data(self, **kwargs):
        entity_data = super().get_json_data()
        alias_data = GeoAliasUsageListView(request=self.request).get_json_data()
        collapse_aliases = json.loads(self.request.GET.get('collapse_aliases', 'true'))

        for entity in entity_data:
            entity['url'] = reverse('document:document-detail',
                                    args=[entity['text_unit__document__pk']])
            entity['detail_url'] = reverse('document:text-unit-detail',
                                           args=[entity['text_unit__pk']]) + \
                                   '?highlight=' + entity['entity__name']
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

        if "document_pk" in self.request.GET:
            qs = qs.filter(text_unit__document__pk=self.request.GET['document_pk'])
        if "party_pk" in self.request.GET:
            qs = qs.filter(
                text_unit__document__textunit__partyusage__party__pk=self.request.GET['party_pk']) \
                .distinct()
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['entity_search'] = self.request.GET.get("entity_search", "")
        return ctx


class TopGeoEntityUsageListView(GeoEntityUsageListView):
    template_name = "extract/top_geo_entity_usage_list.html"

    def get_json_data(self, **kwargs):
        entities_data = super().get_json_data()['data']
        top_data = {}
        for entity in entities_data:
            if entity['entity__name'] in top_data:
                top_data[entity['entity__name']]['count'] += entity['count']
                if "document_pk" in self.request.GET or "party_pk" in self.request.GET:
                    top_data[entity['entity__name']]['entity_data'].append(entity)
            else:
                top_data[entity['entity__name']] = {k: v for k, v in entity.items()
                                                    if k in ['entity__name', 'entity__category',
                                                             'count']}
                top_data[entity['entity__name']]['url'] = \
                    reverse('extract:geo-entity-usage-list') + \
                    '?entity_search=' + entity['entity__name']
                if "document_pk" in self.request.GET or "party_pk" in self.request.GET:
                    top_data[entity['entity__name']]['entity_data'] = [entity]
        ret = sorted(top_data.values(), key=lambda i: -i['count'])
        return {'data': ret, 'total_records': len(ret)}


class GeoAliasUsageListView(AjaxListView):
    model = GeoAliasUsage
    json_fields = ['text_unit__document__pk', 'text_unit__document__name',
                   'text_unit__document__description', 'text_unit__document__document_type',
                   'alias__alias', 'alias__locale', 'alias__type', 'count',
                   'alias__entity__name', 'alias__entity__category',
                   'text_unit__pk', 'text_unit__text']
    limit_reviewers_qs_by_field = 'text_unit__document'

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data:
            item['url'] = reverse('document:document-detail',
                                  args=[item['text_unit__document__pk']])
            item['detail_url'] = reverse('document:text-unit-detail',
                                         args=[item['text_unit__pk']]) + \
                                 '?highlight=' + item['alias__alias']
        return data

    def get_queryset(self):
        qs = super().get_queryset()
        entity_search = self.request.GET.get("entity_search", "")
        if entity_search:
            entity_search_list = entity_search.split(",")
            qs = qs.filter(alias__entity__name__in=entity_search_list)

        if "document_pk" in self.request.GET:
            qs = qs.filter(text_unit__document__pk=self.request.GET['document_pk'])

        if "party_pk" in self.request.GET:
            qs = qs.filter(
                text_unit__document__textunit__partyusage__party__pk=self.request.GET['party_pk']) \
                .distinct()
        return qs


class GeoEntityUsageGoogleMapView(AjaxResponseMixin, TemplateView):
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
        for entity in entities:
            if not entity['latitude']:
                g = geocoder.google(entity['entity__name'])
                if not g.latlng and ',' in entity['entity__name']:
                    g = geocoder.google(entity['entity__name'].split(',')[0])
                try:
                    entity['latitude'], entity['longitude'] = g.latlng
                except ValueError:
                    pass
        return entities


class GeoEntityUsageGoogleChartView(GeoEntityUsageGoogleMapView):
    template_name = "extract/geo_entity_usage_chart.html"

    def get_json_data(self):
        entities = self.get_entities()
        data = [['country', 'count']] + [[e['entity__name'], e['count']] for e in entities]
        return data


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


class PartyUsageListView(JqPaginatedListView):
    model = PartyUsage
    json_fields = ['text_unit__document__pk', 'text_unit__document__name',
                   'text_unit__document__description', 'text_unit__document__document_type',
                   'party__name', 'party__type', 'party__pk',
                   'count', 'text_unit__pk', 'text_unit__text']
    limit_reviewers_qs_by_field = 'text_unit__document'

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = reverse('document:document-detail',
                                  args=[item['text_unit__document__pk']])
            item['detail_url'] = reverse('document:text-unit-detail',
                                         args=[item['text_unit__pk']]) + \
                                 '?highlight=' + item['party__name']
            item['party_summary_url'] = \
                reverse('extract:party-summary', args=[item['party__pk']])
        return data

    def get_queryset(self):
        qs = super().get_queryset()

        if "document_pk" in self.request.GET:
            qs = qs.filter(text_unit__document__pk=self.request.GET['document_pk'])

        party_search = self.request.GET.get("party_search", "")
        if party_search:
            party_search_list = party_search.split(",")
            qs = qs.filter(party__name__in=party_search_list)
        qs = qs.select_related('party', 'text_unit', 'text_unit__document')
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['party_search'] = self.request.GET.get("party_search", "")
        return ctx


class TopPartyUsageListView(JqPaginatedListView):
    model = PartyUsage
    template_name = "extract/top_party_usage_list.html"
    limit_reviewers_qs_by_field = 'text_unit__document'

    def get_json_data(self, **kwargs):
        data = list(self.get_queryset())
        if "document_pk" in self.request.GET:
            party_list_view = PartyUsageListView(request=self.request)
            party_data = party_list_view.get_json_data()['data']
        for item in data:
            item['url'] = reverse('extract:party-usage-list') + \
                          '?party_search=' + item['party__name']
            item['party_summary_url'] = \
                reverse('extract:party-summary', args=[item['party__pk']])
            if "document_pk" in self.request.GET:
                item['party_data'] = [i for i in party_data
                                      if i['party__name'] == item['party__name']]
        return {'data': data, 'total_records': len(data)}

    def get_queryset(self):
        qs = super().get_queryset()

        if "document_pk" in self.request.GET:
            qs = qs.filter(text_unit__document__pk=self.request.GET['document_pk'])

        if "party_pk" in self.request.GET:
            qs = qs.filter(party__pk=self.request.GET['party_pk'])

        qs = qs.values("party__name", "party__type", "party__pk") \
            .annotate(count=Sum("count")) \
            .order_by("-count")
        return qs


class DateUsageListView(JqPaginatedListView):
    model = DateUsage
    json_fields = ['text_unit__document__pk', 'text_unit__document__name',
                   'text_unit__document__description', 'text_unit__document__document_type',
                   'date', 'count', 'text_unit__pk', 'text_unit__text']
    limit_reviewers_qs_by_field = 'text_unit__document'

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = reverse('document:document-detail',
                                  args=[item['text_unit__document__pk']])
            item['detail_url'] = reverse('document:text-unit-detail',
                                         args=[item['text_unit__pk']])
        return data

    def get_queryset(self):
        qs = super().get_queryset()
        if "document_pk" in self.request.GET:
            qs = qs.filter(text_unit__document__pk=self.request.GET['document_pk'])
        if 'date_search' in self.request.GET:
            qs = qs.filter(date=self.request.GET["date_search"])
        elif 'month_search' in self.request.GET:
            adate = datetime.datetime.strptime(self.request.GET["month_search"], '%Y-%m-%d')
            qs = qs.filter(date__year=adate.year, date__month=adate.month)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['date_search'] = self.request.GET.get("date_search", "")
        return ctx


class TopDateUsageListView(JqPaginatedListView):
    model = DateUsage
    template_name = "extract/top_date_usage_list.html"
    limit_reviewers_qs_by_field = 'text_unit__document'

    def get_json_data(self, **kwargs):
        data = list(self.get_queryset())
        if "document_pk" in self.request.GET:
            date_list_view = DateUsageListView(request=self.request)
            date_data = date_list_view.get_json_data()['data']
        for item in data:
            item['url'] = reverse('extract:date-usage-list') + \
                          '?date_search=' + item['date'].isoformat()
            if "document_pk" in self.request.GET:
                item['date_data'] = [i for i in date_data
                                     if i['date'] == item['date']]
        return {'data': data, 'total_records': len(data)}

    def get_queryset(self):
        qs = super().get_queryset()

        if "document_pk" in self.request.GET:
            qs = qs.filter(text_unit__document__pk=self.request.GET['document_pk'])

        qs = qs.values("date") \
            .annotate(count=Sum("count")) \
            .order_by("-count")
        return qs


class DateUsageTimelineView(JqPaginatedListView):
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


class DateDurationUsageListView(JqPaginatedListView):
    model = DateDurationUsage
    json_fields = ['text_unit__document__pk', 'text_unit__document__name',
                   'text_unit__document__description', 'text_unit__document__document_type',
                   'duration', 'duration_str', 'count', 'text_unit__pk', 'text_unit__text']
    limit_reviewers_qs_by_field = 'text_unit__document'

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['duration'] = item['duration'].days
            item['url'] = reverse('document:document-detail',
                                  args=[item['text_unit__document__pk']])
            item['detail_url'] = reverse('document:text-unit-detail',
                                         args=[item['text_unit__pk']])
        return data

    def get_queryset(self):
        qs = super().get_queryset()
        if "document_pk" in self.request.GET:
            qs = qs.filter(text_unit__document__pk=self.request.GET['document_pk'])
        if 'duration_search' in self.request.GET:
            qs = qs.filter(duration_str=self.request.GET["duration_search"])
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['duration_search'] = self.request.GET.get("duration_search", "")
        return ctx


class TopDateDurationUsageListView(JqPaginatedListView):
    model = DateDurationUsage
    template_name = "extract/top_date_duration_usage_list.html"
    limit_reviewers_qs_by_field = 'text_unit__document'

    def get_json_data(self, **kwargs):
        data = list(self.get_queryset())
        if "document_pk" in self.request.GET:
            list_view = DateDurationUsageListView(request=self.request)
            duration_data = list_view.get_json_data()['data']
        for item in data:
            duration = item['duration'].days
            item['duration'] = duration
            item['url'] = reverse('extract:date-duration-usage-list') + \
                          '?duration_search=' + item['duration_str']
            if "document_pk" in self.request.GET:
                item['duration_data'] = [i for i in duration_data
                                         if i['duration'] == item['duration']]
        data = sorted(data, key=lambda i: -i['duration'])
        return {'data': data, 'total_records': len(data)}

    def get_queryset(self):
        qs = super().get_queryset()

        if "document_pk" in self.request.GET:
            qs = qs.filter(text_unit__document__pk=self.request.GET['document_pk'])

        qs = qs.values("duration", "duration_str") \
            .annotate(count=Sum("count")) \
            .order_by("-count")
        return qs


class DefinitionUsageListView(JqPaginatedListView):
    model = DefinitionUsage
    json_fields = ['text_unit__document__pk', 'text_unit__document__name',
                   'text_unit__document__description', 'text_unit__document__document_type',
                   'definition', 'count', 'text_unit__pk', 'text_unit__text']
    limit_reviewers_qs_by_field = 'text_unit__document'

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = reverse('document:document-detail',
                                  args=[item['text_unit__document__pk']])
            item['detail_url'] = reverse('document:text-unit-detail',
                                         args=[item['text_unit__pk']]) + \
                                 '?highlight=' + item['definition']

        return data

    def get_queryset(self):
        qs = super().get_queryset()

        if "document_pk" in self.request.GET:
            qs = qs.filter(text_unit__document__pk=self.request.GET['document_pk'])

        definition_search = self.request.GET.get("definition_search")
        if definition_search:
            qs = qs.filter(definition=definition_search)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['definition_search'] = self.request.GET.get("definition_search", "")
        return ctx


class TopDefinitionUsageListView(JqPaginatedListView):
    model = DefinitionUsage
    template_name = "extract/top_definition_usage_list.html"
    limit_reviewers_qs_by_field = 'text_unit__document'

    def get_json_data(self, **kwargs):
        data = list(self.get_queryset())
        if "document_pk" in self.request.GET:
            definition_list_view = DefinitionUsageListView(request=self.request)
            definition_data = definition_list_view.get_json_data()['data']
        for item in data:
            item['url'] = reverse('extract:definition-usage-list') + \
                          '?definition_search=' + item['definition']
            if "document_pk" in self.request.GET:
                item['definition_data'] = [i for i in definition_data
                                           if i['definition'] == item['definition']]
        return {'data': data, 'total_records': len(data)}

    def get_queryset(self):
        qs = super().get_queryset()

        if "document_pk" in self.request.GET:
            qs = qs.filter(text_unit__document__pk=self.request.GET['document_pk'])

        qs = qs.values("definition") \
            .annotate(count=Sum("count")) \
            .order_by("-count")
        return qs


class CourtUsageListView(JqPaginatedListView):
    model = CourtUsage
    json_fields = ['text_unit__document__pk', 'text_unit__document__name',
                   'text_unit__document__description', 'text_unit__document__document_type',
                   'court__name', 'court__abbreviation', 'count',
                   'text_unit__pk', 'text_unit__text']
    limit_reviewers_qs_by_field = 'text_unit__document'

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = reverse('document:document-detail',
                                  args=[item['text_unit__document__pk']])
            item['detail_url'] = reverse('document:text-unit-detail',
                                         args=[item['text_unit__pk']]) + \
                                 '?highlight=' + item['court__name']
        return data

    def get_queryset(self):
        qs = super().get_queryset()

        if "document_pk" in self.request.GET:
            qs = qs.filter(text_unit__document__pk=self.request.GET['document_pk'])

        court_search = self.request.GET.get("court_search")
        if court_search:
            qs = qs.filter(court__name=court_search)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['court_search'] = self.request.GET.get("court_search", "")
        return ctx


class TopCourtUsageListView(JqPaginatedListView):
    model = CourtUsage
    template_name = "extract/top_court_usage_list.html"
    limit_reviewers_qs_by_field = 'text_unit__document'

    def get_json_data(self, **kwargs):
        data = list(self.get_queryset())
        if "document_pk" in self.request.GET:
            list_view = CourtUsageListView(request=self.request)
            court_data = list_view.get_json_data()['data']
        for item in data:
            item['url'] = reverse('extract:court-usage-list') + \
                          '?court_search=' + item['court__name']
            if "document_pk" in self.request.GET:
                item['court_data'] = [i for i in court_data
                                      if i['court__name'] == item['court__name']]
        return {'data': data, 'total_records': len(data)}

    def get_queryset(self):
        qs = super().get_queryset()

        if "document_pk" in self.request.GET:
            qs = qs.filter(text_unit__document__pk=self.request.GET['document_pk'])

        qs = qs.values("court__name", "court__abbreviation") \
            .annotate(count=Sum("count")) \
            .order_by("-count")
        return qs


class CurrencyUsageListView(JqPaginatedListView):
    model = CurrencyUsage
    json_fields = ['text_unit__document__pk', 'text_unit__document__name',
                   'text_unit__document__description', 'text_unit__document__document_type',
                   'usage_type', 'currency', 'amount',
                   'text_unit__pk', 'text_unit__text']
    limit_reviewers_qs_by_field = 'text_unit__document'

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['amount__value'] = item['amount']['value'] if item['amount'] else None
            item['amount__value_str'] = item['amount']['value_str'] if item['amount'] else None
            item['url'] = reverse('document:document-detail',
                                  args=[item['text_unit__document__pk']])
            item['detail_url'] = reverse('document:text-unit-detail',
                                         args=[item['text_unit__pk']])
        return data

    def get_queryset(self):
        qs = super().get_queryset()

        if "document_pk" in self.request.GET:
            qs = qs.filter(text_unit__document__pk=self.request.GET['document_pk'])

        if "currency_search" in self.request.GET:
            qs = qs.filter(currency=self.request.GET['currency_search'])
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['currency_search'] = self.request.GET.get("currency_search", "")
        return ctx


class TopCurrencyUsageListView(JqPaginatedListView):
    model = CurrencyUsage
    template_name = "extract/top_currency_usage_list.html"
    limit_reviewers_qs_by_field = 'text_unit__document'

    def get_json_data(self, **kwargs):
        data = list(self.get_queryset())
        if "document_pk" in self.request.GET:
            list_view = CurrencyUsageListView(request=self.request)
            currency_data = list_view.get_json_data()['data']
        for item in data:
            item['url'] = reverse('extract:currency-usage-list') + \
                          '?currency_search=' + item['currency']
            if "document_pk" in self.request.GET:
                item['currency_data'] = [i for i in currency_data
                                         if i['currency'] == item['currency']]
        return {'data': data, 'total_records': len(data)}

    def get_queryset(self):
        qs = super().get_queryset()

        if "document_pk" in self.request.GET:
            qs = qs.filter(text_unit__document__pk=self.request.GET['document_pk'])

        qs = qs.values("currency", "usage_type") \
            .annotate(count=Count("pk")) \
            .order_by("-count")
        return qs


class PartySummary(DetailView):
    model = Party
    template_name = 'extract/party_summary.html'
