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

# Standard imports
import datetime
import itertools
import json
import operator
import re
from collections import defaultdict
from functools import reduce
from urllib.parse import quote as url_quote

# Third-party imports
import icalendar
from rest_framework import serializers, routers, viewsets
from rest_framework.generics import ListAPIView

# Django imports
from django.conf import settings
from django.conf.urls import url
from django.urls import reverse
from django.db.models import Q, Sum, F, Min, Max
from django.db.models.functions import TruncMonth
from django.http import JsonResponse, HttpResponse

# Project imports
from apps.document.models import Document
from apps.extract.models import *
import apps.common.mixins

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class BaseUsageSerializer(apps.common.mixins.SimpleRelationSerializer):
    class Meta:
        fields = []
        base_fields = ['pk',
                       'text_unit__pk',
                       'text_unit__location_start',
                       'text_unit__location_end']
        document_fields = ['text_unit__document__pk',
                           'text_unit__document__name',
                           'text_unit__document__description',
                           'text_unit__document__document_type']

    def __init__(self, instance=None, **kwargs):
        self.Meta.fields += self.Meta.base_fields
        try:
            _ = kwargs['context']['request'].GET.get('document_id') or \
                getattr(kwargs['context']['view'], 'document_id')
        except (AttributeError, KeyError):
            self.Meta.fields += self.Meta.document_fields
        super().__init__(instance, **kwargs)


class ViewSetDataMixin(object):

    @property
    def data(self):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return serializer.data


class BaseUsageListAPIView(apps.common.mixins.JqListAPIView, ViewSetDataMixin):

    filters = None

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(text_unit__unit_type='sentence')
        if self.filters:
            for field, key, _callable in self.filters:
                try:
                    value = self.request.GET.get(key)
                except Exception:
                    continue
                if value:
                    value = _callable(value)
                    qs = qs.filter(**{field: value})
        document_id = self.request.GET.get('document_id') or getattr(self, 'document_id', None)
        if document_id:
            qs = qs.filter(text_unit__document_id=document_id)
            return qs.select_related('text_unit')
        else:
            return qs.select_related('text_unit', 'text_unit__document')

    @staticmethod
    def filter(search_str, qs, _or_lookup,
               _and_lookup=None, _not_lookup=None):
        search_list = re.split(r'\s*,\s*', search_str.strip().strip(","))
        _not_search_list = [i[1:].strip() for i in search_list if i.startswith('-')]
        _and_search_list = [i[1:].strip() for i in search_list if i.startswith('&')]
        _or_search_list = [i for i in search_list if i[0] not in ['-', '&']]

        if _or_search_list:
            query = reduce(
                operator.or_,
                (Q(**{_or_lookup: i}) for i in _or_search_list))
            qs = qs.filter(query)
        if _and_search_list:
            query = reduce(
                operator.and_,
                (Q(**{_and_lookup or _or_lookup: i}) for i in _and_search_list))
            qs = qs.filter(query)
        if _not_search_list:
            query = reduce(
                operator.or_,
                (Q(**{_not_lookup or _or_lookup: i}) for i in _not_search_list))
            qs = qs.exclude(query)
        return qs


class BaseTopUsageSerializer(object):

    def __init__(self, queryset, *args, **kwargs):
        self.view = kwargs['context']['view']
        self.queryset = self.view.queryset
        self.data_view = self.view.data_view
        self.grouping_item = self.view.grouping_item
        self.url_args = self.view.url_args
        self.update_item = self.view.update_item
        self.request = kwargs.get('context', {}).get('request')
        document_id = self.request.GET.get('document_id') or \
                      getattr(kwargs['context']['view'], 'document_id', None)
        if document_id and not self.request.GET.get('skip_details'):
            self.detail_data = self.data_view(
                request=self.request, format_kwarg=None, document_id=document_id)\
                .get(request=self.request).data
        else:
            self.detail_data = None

    def get_detail_data(self, item):
        return [i for i in self.detail_data if
                i[self.grouping_item] == item[self.grouping_item]]

    @property
    def data(self):
        for item in self.queryset:
            if callable(self.update_item):
                item = self.update_item(item)
            if self.url_args:
                item['url'] = '{}?{}={}'.format(
                    reverse(self.url_args[0]), self.url_args[1], str(item[self.url_args[2]]))
            if self.detail_data:
                item['data'] = self.get_detail_data(item)
        return list(self.queryset)


class BaseTopUsageListAPIView(BaseUsageListAPIView, ViewSetDataMixin):
    serializer_class = BaseTopUsageSerializer
    qs_values = []
    qs_order_by = ["-count"]
    url_args = None

    def get_queryset(self):
        self.queryset = self.model.objects.all()
        qs = super().get_queryset()
        qs = qs.values(*self.qs_values) \
            .annotate(count=Sum("count"), value=F(self.grouping_item)) \
            .order_by(*self.qs_order_by)
        self.queryset = qs
        return qs

    def update_item(self, item):
        return item


# --------------------------------------------------------
# Term Usage Views
# --------------------------------------------------------

class TermUsageSerializer(BaseUsageSerializer):
    class Meta(BaseUsageSerializer.Meta):
        model = TermUsage
        fields = ['term__term', 'count']


class TermUsageListAPIView(BaseUsageListAPIView):
    """
    Term Usage List
    """
    queryset = TermUsage.objects.all()
    serializer_class = TermUsageSerializer
    sub_app = 'term'

    def get_queryset(self):
        qs = super().get_queryset()
        term_search = self.request.GET.get('term_search')
        if term_search:
            qs = self.filter(term_search, qs,
                             _or_lookup='term__term__exact',
                             _and_lookup='text_unit__text__icontains',
                             _not_lookup='text_unit__text__icontains')
        # filter out duplicated Terms (equal terms, but diff. term sources)
        # qs = qs.order_by('term__term').distinct('term__term', 'text_unit__pk')
        return qs.select_related('term')


class TopTermUsageListAPIView(BaseTopUsageListAPIView):
    """
    Top Term Usage List
    """
    sub_app = 'term'
    model = TermUsage
    grouping_item = 'term__term'
    data_view = TermUsageListAPIView
    qs_values = ['term__term', 'term__source']
    qs_order_by = ['-count', 'term__term']
    url_args = ('v1:term-usage', 'term_search', 'term__term')


# --------------------------------------------------------
# Geo Entity Views
# --------------------------------------------------------

class GeoEntityListSerializer(serializers.ModelSerializer):
    alias = serializers.SerializerMethodField()

    class Meta:
        model = GeoEntity
        fields = ['pk', 'entity_id', 'name', 'priority', 'category', 'alias']

    def get_alias(self, obj):
        return ', '.join(
            GeoAlias.objects.filter(entity_id=obj.pk).values_list('alias', flat=True))


class GeoEntityUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeoEntity
        fields = ['pk', 'priority']


class GeoEntityViewSet(apps.common.mixins.JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: Geo Entity List
    retrieve: Retrieve Geo Entity
    update: Update Geo Entity
    """
    queryset = GeoEntity.objects.all()
    http_method_names = ['get', 'put']

    def get_serializer_class(self):
        if self.action == 'update':
            return GeoEntityUpdateSerializer
        return GeoEntityListSerializer


# --------------------------------------------------------
# Geo Entity Usage Views
# --------------------------------------------------------

# TODO: merge entity data with alias data

class GeoEntityUsageSerializer(BaseUsageSerializer):
    class Meta(BaseUsageSerializer.Meta):
        model = GeoEntityUsage
        fields = ['entity__name', 'entity__category', 'count']


class GeoEntityUsageListAPIView(BaseUsageListAPIView):
    """
    Geo Entity Usage List
    """
    queryset = GeoEntityUsage.objects.all()
    serializer_class = GeoEntityUsageSerializer
    sub_app = 'geoentity'

    def get_queryset(self):
        qs = super().get_queryset()
        entity_search = self.request.GET.get("entity_search")
        if entity_search:
            entity_search_list = entity_search.split(",")
            qs = qs.filter(entity__name__in=entity_search_list)
        party_id = self.request.GET.get("party_id")
        if party_id:
            qs = qs.filter(
                text_unit__document__textunit__partyusage__party_id=party_id) \
                .distinct()
        return qs.select_related('entity')


class TopGeoEntityUsageListAPIView(BaseTopUsageListAPIView):
    """
    Top Geo Entity Usage List
    """
    sub_app = 'geoentity'
    model = GeoEntityUsage
    grouping_item = 'entity__name'
    data_view = GeoEntityUsageListAPIView
    qs_values = ['entity__name']
    qs_order_by = ['-count', 'entity__name']
    url_args = ('v1:geo-entity-usage', 'entity_search', 'entity__name')


class GeoAliasUsageSerializer(BaseUsageSerializer):
    class Meta(BaseUsageSerializer.Meta):
        model = GeoAliasUsage
        fields = ['alias__alias', 'alias__locale', 'alias__type', 'count',
                  'alias__entity__name', 'alias__entity__category']


class GeoAliasUsageListAPIView(BaseUsageListAPIView):
    """
    Geo Alias Usage List
    """
    sub_app = 'geoentity'
    queryset = GeoAliasUsage.objects.all()
    serializer_class = GeoAliasUsageSerializer
    filters = [('alias__name', 'alias_name', str)]

    def get_queryset(self):
        qs = super().get_queryset()
        entity_search = self.request.GET.get("entity_name")
        if entity_search:
            entity_search_list = entity_search.split(",")
            qs = qs.filter(alias__entity__name__in=entity_search_list)
        party_id = self.request.GET.get("party_id")
        if party_id:
            qs = qs.filter(
                text_unit__document__textunit__partyusage__party_id=party_id) \
                .distinct()
        return qs.select_related('alias')


class TopGeoAliasUsageListAPIView(BaseTopUsageListAPIView):
    """
    Top Geo Alias Usage List
    """
    sub_app = 'geoentity'
    model = GeoAliasUsage
    grouping_item = 'alias__alias'
    data_view = GeoAliasUsageListAPIView
    qs_values = ['alias__alias']
    qs_order_by = ['-count', 'alias__alias']
    url_args = ('v1:geo-alias-usage', 'alias_search', 'alias__alias')


# --------------------------------------------------------
# Typeahead Views
# --------------------------------------------------------

class TypeaheadUsageApiView(ListAPIView):
    """
    Base ThingUsage Typeahead view\n
    GET params:
      - q: str
    """
    model = None
    use_negative_value = False

    def get(self, request, *args, **kwargs):
        qs = self.model.objects.all()
        field_name = kwargs.get('field_name')
        if "q" in request.GET:
            search_key = '%s__icontains' % field_name
            qs = qs.filter(**{search_key: request.GET.get("q")})\
                .values(field_name).annotate(s=Sum('count')).order_by('-s')
        else:
            qs = qs.values(field_name).distinct().order_by(field_name)
        results = [{"value": i[field_name]} for i in qs]
        if self.use_negative_value:
            _results = []
            for t in results:
                _results.append(t)
                _results.append({"value": '-%s' % t['value']})
            results = _results
        return JsonResponse(results, safe=False)


class TypeaheadTermUsage(TypeaheadUsageApiView):
    """
    Typeahead Term Usage\n
        Kwargs: field_name: [term__term]
        GET params:
          - q: str
    """
    model = TermUsage
    use_negative_value = True


class TypeaheadGeoEntityUsage(TypeaheadUsageApiView):
    """
    Typeahead Geo Entity Usage\n
        Kwargs: field_name: [entity__name]
        GET params:
          - q: str
    """
    model = GeoEntityUsage


class TypeaheadPartyUsage(TypeaheadUsageApiView):
    """
    Typeahead Party Usage\n
        Kwargs: field_name: [party__name]
        GET params:
          - q: str
    """
    model = PartyUsage


# --------------------------------------------------------
# Party Usage Views
# --------------------------------------------------------

class PartyUsageSerializer(BaseUsageSerializer):
    class Meta(BaseUsageSerializer.Meta):
        model = PartyUsage
        fields = ['party__name', 'party__type_abbr', 'party__pk', 'count']


class PartyUsageListAPIView(BaseUsageListAPIView):
    """
    Party Usage List\n
    GET params:
      - document_id: int
      - text_unit_id: int
      - party_search: str
      - party_search_iexact: str
      - role: str
      - role_contains: str
    """
    queryset = PartyUsage.objects.all()
    serializer_class = PartyUsageSerializer
    sub_app = 'party'

    def get_queryset(self):
        qs = super().get_queryset()
        party_search = self.request.GET.get("party_search", "")
        if party_search:
            party_search_list = party_search.split(",")
            query = reduce(
                operator.or_,
                (Q(party__name__icontains=i) for i in party_search_list))
            qs = qs.filter(query)
        party_search_iexact = self.request.GET.get("party_search_iexact", "")
        if party_search_iexact:
            qs = qs.filter(party__name__iexact=party_search_iexact)
        document_id = self.request.GET.get('document_id') or getattr(self, 'document_id', None)
        if document_id:
            qs = qs.select_related('party', 'text_unit')
        else:
            qs = qs.select_related('party', 'text_unit', 'text_unit__document')
        return qs


class TopPartyUsageListAPIView(BaseTopUsageListAPIView):
    """
    Top Party Usage List\n
    GET params:
      - document_id: int
      - party_id: int
    """
    sub_app = 'party'
    model = PartyUsage
    grouping_item = 'party__name'
    data_view = PartyUsageListAPIView
    filters = [('party_id', 'party_id', str)]
    qs_values = ['party__name']
    url_args = ('v1:party-usage', 'party_search', 'party__name')

    # def update_item(self, item):
    #     item['party_summary_url'] = reverse('extract:party-summary', args=[item['party__pk']])
    #     return item


class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ['pk', 'name', 'type', 'type_abbr', 'type_label',
                  'type_description', 'description']


class PartyViewSet(apps.common.mixins.JqListAPIMixin, viewsets.ReadOnlyModelViewSet):
    """
    list: Party List
    retrieve: Retrieve Party
    """
    queryset = Party.objects.all()
    serializer_class = PartySerializer


class PartyNetworkChartView(PartyUsageListAPIView):
    """
    Party Network Chart\n
    GET params:
        - party_name_iexact: str
    """
    sub_app = 'party'

    def get_queryset(self):
        return PartyUsage.objects.all()

    def get_parties(self):
        parties = defaultdict(list)
        for result in self.get_queryset()\
                .values('party__name', 'text_unit__document_id') \
                .order_by('party__name', 'text_unit__document_id'):
            parties[result['text_unit__document_id']].append(result['party__name'].upper())
        parties = [i for sub in parties.values() for i in sub if len(set(sub)) > 1]
        return {'parties': sorted(set(parties))}

    def get(self, request, *args, **kwargs):
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
                members1 = {i["source"] for i in chart_links
                            if i["target"] in members and i["source"] not in members}
                members2 = {i["target"] for i in chart_links
                            if i["source"] in members and i["target"] not in members}
                if not members1 and not members2:
                    break
                members = members | members1 | members2

            chart_nodes = [i for i in chart_nodes if i['id'] in members]
            chart_links = [i for i in chart_links if i['source'] in members or i['target'] in members]

        ret = {"nodes": chart_nodes, "links": chart_links, "parties": self.get_parties()}
        return JsonResponse(ret, safe=False)


# --------------------------------------------------------
# Date Usage Views
# --------------------------------------------------------

class DateUsageSerializer(BaseUsageSerializer):
    class Meta(BaseUsageSerializer.Meta):
        model = DateUsage
        fields = ['date', 'count']


class DateUsageListAPIView(BaseUsageListAPIView):
    """
    Date Usage List\n
    GET params:
      - document_id: int
      - date_search: str
      - month_search: str ('%Y-%m-%d')
    """
    queryset = DateUsage.objects.all()
    serializer_class = DateUsageSerializer
    sub_app = 'date'

    def get_queryset(self):
        qs = super().get_queryset()
        if 'date_search' in self.request.GET:
            qs = qs.filter(date=self.request.GET["date_search"])
        elif 'month_search' in self.request.GET:
            adate = datetime.datetime.strptime(self.request.GET["month_search"], '%Y-%m-%d')
            qs = qs.filter(date__year=adate.year, date__month=adate.month)
        return qs


class TopDateUsageListAPIView(BaseTopUsageListAPIView):
    """
    Top Date Usage List\n
    GET params:
      - document_id: int
    """
    sub_app = 'date'
    model = DateUsage
    grouping_item = 'date'
    data_view = DateUsageListAPIView
    qs_values = ['date']
    qs_order_by = ['-date', '-count']

    def update_item(self, item):
        item['url'] = reverse('v1:date-usage') + '?date_search=' + item['date'].isoformat()
        item['date'] = item['date'].isoformat()
        return item


class DateUsageTimelineView(ListAPIView):
    """
    Date Usage Timeline Chart\n
    GET params:
        - document_id: int
        - per_month: bool
    """
    sub_app = 'date'

    def get_queryset(self):
        qs = DateUsage.objects.all()
        if "document_pk" in self.request.GET:
            qs = qs.filter(text_unit__document__pk=self.request.GET['document_pk'])
        return qs

    def get(self, request, *args, **kwargs):
        per_month = json.loads(self.request.GET.get('per_month', 'false'))

        qs = self.get_queryset()

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
            date_list_view = DateUsageListAPIView(request=self.request, format_kwarg={})
            date_data = date_list_view.list(request=self.request).data
            visible_interval = 180

        max_value = qs.aggregate(m=Max('count'))['m']
        min_value = qs.aggregate(m=Min('count'))['m']
        range_value = max_value - min_value

        for item in data:
            item['weight'] = (item['count'] - min_value) / range_value
            if per_month:
                item['url'] = '{}?month_search={}'.format(
                    reverse('extract:date-usage-list'), item['start'].isoformat())
                item['content'] = '{}, {}: {}'.format(item['start'].strftime('%B'),
                                                      item['start'].year, item['count'])
            else:
                item['url'] = '{}?date_search={}'.format(
                    reverse('extract:date-usage-list'), item['start'].isoformat())
                item['content'] = '{}: {}'.format(item['start'].isoformat(), item['count'])
                item['date_data'] = [i for i in date_data if i['date'] == item['start']]

        initial_start_date = datetime.date.today() - datetime.timedelta(days=visible_interval)
        initial_end_date = datetime.date.today() + datetime.timedelta(days=visible_interval)
        ret = {'data': data,
               'per_month': per_month,
               'initial_start_date': initial_start_date,
               'initial_end_date': initial_end_date}
        return JsonResponse(ret)


class DateUsageCalendarView(ListAPIView):
    """
    Date Usage Calendar Chart\n
    GET params:
        - document_id: int
    """
    sub_app = 'date'

    def get_queryset(self):
        qs = DateUsage.objects.all()
        qs = qs.filter(date__lte=datetime.date.today() + datetime.timedelta(365 * 100))

        if self.request.GET.get("document_id"):
            qs = qs.filter(text_unit__document_id=self.request.GET['document_id'])

        qs = qs.order_by('date') \
            .values('date') \
            .annotate(count=Sum('count'))

        return qs

    def get_context(self):
        documents = Document.objects.all()
        if self.request.user.is_reviewer:
            documents = documents.filter(
                taskqueue__user_id=self.request.user.pk,
                textunit__dateusage__isnull=False).distinct()
        return {'documents': {i.pk: i.name for i in documents}}

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        data = list(qs)

        max_value = qs.aggregate(m=Max('count'))['m']

        min_date = qs.aggregate(m=Min('date'))['m']
        max_date = qs.aggregate(m=Max('date'))['m']

        for item in data:
            item['weight'] = item['count'] / max_value
            # TODO: update url
            item['url'] = '{}?date_search={}'.format(
                reverse('extract:date-usage-list'), item['date'].isoformat())

        ret = {'data': data,
               'min_year': min_date.year,
               'max_year': max_date.year,
               'context': self.get_context()}

        return JsonResponse(ret)


class DateUsageToICalView(DateUsageListAPIView):
    """
    Load Date Usage as iCal\n
    GET params:
        - document_id: int (required)
    """
    sub_app = 'date'

    def get(self, request, *args, **kwargs):
        document_id = request.GET.get('document_id')
        if not document_id:
            return JsonResponse({'error': "Document id is not defined."})

        sample_length = 100
        # Create calendar
        cal = icalendar.Calendar()
        cal.add('prodid', 'ContraxSuite (https://contraxsuite.com)')
        cal.add('version', settings.VERSION_NUMBER)

        # Filter to text unit
        for du in self.get_queryset():
            event = icalendar.Event()
            event.add("summary", "Calendar reminder for document {0}, text unit {1}:\n{2}"
                      .format(du.text_unit.document.name, du.text_unit_id,
                              du.text_unit.text[:sample_length]))
            event.add("dtstart", du.date)
            event.add("dtend", du.date)
            event.add("dtstamp", du.date)
            cal.add_component(event)

        filename = "document-{0}.ics".format(document_id)

        response = HttpResponse(cal.to_ical(), content_type='text/calendar; charset=utf8')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        return response


# --------------------------------------------------------
# Date Duration Usage Views
# --------------------------------------------------------

class DateDurationUsageSerializer(BaseUsageSerializer):
    class Meta(BaseUsageSerializer.Meta):
        model = DateDurationUsage
        fields = ['amount', 'amount_str', 'duration_type', 'duration_days', 'count']


class DateDurationUsageListAPIView(BaseUsageListAPIView):
    """
    Date Duration Usage List\n
    GET params:
      - document_id: int
      - text_unit_id: int
      - duration_days_str: str/float
    """
    sub_app = 'duration'
    queryset = DateDurationUsage.objects.all()
    serializer_class = DateDurationUsageSerializer
    filters = [('duration_days', 'duration_days_str', float)]


class TopDateDurationUsageListAPIView(BaseTopUsageListAPIView):
    """
    Top Date Duration Usage List\n
    GET params:
      - document_id: int
    """
    sub_app = 'duration'
    model = DateDurationUsage
    grouping_item = 'duration_days'
    data_view = DateDurationUsageListAPIView
    qs_values = ['duration_days']
    qs_order_by = ['-duration_days', '-count']
    url_args = ('v1:date-duration-usage', 'duration_search', 'duration_days')


# --------------------------------------------------------
# Definition Usage Views
# --------------------------------------------------------

class DefinitionUsageSerializer(BaseUsageSerializer):
    class Meta(BaseUsageSerializer.Meta):
        model = DefinitionUsage
        fields = ['definition', 'count']


class DefinitionUsageListAPIView(BaseUsageListAPIView):
    """
    Definition Usage List\n
    GET params:
      - document_id: int
      - definition: str
    """
    queryset = DefinitionUsage.objects.all()
    serializer_class = DefinitionUsageSerializer
    sub_app = 'definition'
    # filters = [('definition', 'definition_search', str)]


class TopDefinitionUsageListAPIView(BaseTopUsageListAPIView):
    """
    Top Definition Usage List\n
    GET params:
      - document_id: int
    """
    sub_app = 'definition'
    model = DefinitionUsage
    grouping_item = 'definition'
    data_view = DefinitionUsageListAPIView
    qs_values = ["definition"]
    url_args = ('v1:definition-usage', 'definition_search', 'definition')


# --------------------------------------------------------
# Court Usage Views
# --------------------------------------------------------

class CourtUsageSerializer(BaseUsageSerializer):
    class Meta(BaseUsageSerializer.Meta):
        model = CourtUsage
        fields = ['court__name', 'court__alias', 'count']


class CourtUsageListAPIView(BaseUsageListAPIView):
    """
    Court Usage List\n
    GET params:
      - document_id: int
      - text_unit_id: int
      - court_name: str
      - court_alias: str
    """
    sub_app = 'court'
    queryset = CourtUsage.objects.all()
    serializer_class = CourtUsageSerializer
    filters = [('court__name', 'court_name', str),
               ('court__alias', 'court_alias', str)]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related('court')


class TopCourtUsageListAPIView(BaseTopUsageListAPIView):
    """
    Top Court Usage List\n
    GET params:
      - document_id: int
    """
    sub_app = 'court'
    model = CourtUsage
    grouping_item = 'court__name'
    data_view = CourtUsageListAPIView
    qs_values = ["court__name", "court__alias"]
    url_args = ('v1:court-usage', 'court_search', 'court__name')


# --------------------------------------------------------
# Currency Usage Views
# --------------------------------------------------------

class CurrencyUsageSerializer(BaseUsageSerializer):
    class Meta(BaseUsageSerializer.Meta):
        model = CurrencyUsage
        fields = ['usage_type', 'currency', 'amount', 'amount_str']


class CurrencyUsageListAPIView(BaseUsageListAPIView):
    """
    Currency Usage List\n
    GET params:
      - document_id: int
      - amount_search: str
      - currency: str
    """
    sub_app = 'court'
    queryset = CurrencyUsage.objects.all()
    serializer_class = CurrencyUsageSerializer
    filters = [('amount', 'amount_search', float)]


class TopCurrencyUsageListAPIView(BaseTopUsageListAPIView):
    """
    Top Currency Usage List\n
    GET params:
      - document_id: int
    """
    sub_app = 'currency'
    model = CurrencyUsage
    grouping_item = 'amount'
    data_view = CurrencyUsageListAPIView
    qs_values = ['amount', 'currency']
    qs_order_by = ['-amount', '-count']
    url_args = ('v1:currency-usage', 'currency_search', 'currency')


# --------------------------------------------------------
# Regulation Usage Views
# --------------------------------------------------------

class RegulationUsageSerializer(BaseUsageSerializer):
    class Meta(BaseUsageSerializer.Meta):
        model = RegulationUsage
        fields = ['regulation_type', 'regulation_name', 'entity__name', 'count']


class RegulationUsageListAPIView(BaseUsageListAPIView):
    """
    Regulation Usage List\n
    GET params:
      - document_id: int
      - text_unit_id: int
      - regulation_type: str
      - regulation_name: str
    """
    sub_app = 'regulation'
    queryset = RegulationUsage.objects.all()
    serializer_class = RegulationUsageSerializer
    # filters = [('regulation_name', 'regulation_search', str)]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related('entity')


class TopRegulationUsageListAPIView(BaseTopUsageListAPIView):
    """
    Top Regulation Usage List\n
    GET params:
      - document_id: int
    """
    sub_app = 'regulation'
    model = RegulationUsage
    grouping_item = 'regulation_name'
    data_view = RegulationUsageListAPIView
    qs_values = ["regulation_name", "regulation_type"]
    url_args = ('v1:regulation-usage', 'regulation_search', 'regulation_name')


# --------------------------------------------------------
# Amount Usage Views
# --------------------------------------------------------

class AmountUsageSerializer(BaseUsageSerializer):
    class Meta(BaseUsageSerializer.Meta):
        model = AmountUsage
        fields = ['amount', 'amount_str', 'count']


class AmountUsageListAPIView(BaseUsageListAPIView):
    """
    Amount Usage List\n
    GET params:
      - document_id: int
      - text_unit_id: int
      - amount_search: float
      - amount_str: str
    """
    sub_app = 'amount'
    queryset = AmountUsage.objects.all()
    serializer_class = AmountUsageSerializer
    filters = [('amount', 'amount_search', float)]


class TopAmountUsageListAPIView(BaseTopUsageListAPIView):
    """
    Top Amount Usage List\n
    GET params:
      - document_id: int
    """
    sub_app = 'amount'
    model = AmountUsage
    grouping_item = 'amount'
    data_view = AmountUsageListAPIView
    qs_values = ['amount']
    qs_order_by = ['-amount', '-count']
    url_args = ('v1:amount-usage', 'amount_search', 'amount')


# --------------------------------------------------------
# Distance Usage Views
# --------------------------------------------------------

class DistanceUsageSerializer(BaseUsageSerializer):
    class Meta(BaseUsageSerializer.Meta):
        model = DistanceUsage
        fields = ['amount', 'distance_type', 'count']


class DistanceUsageListAPIView(BaseUsageListAPIView):
    """
    Distance Usage List\n
    GET params:
      - document_id: int
      - distance_type: str
      - amount_search: float
    """
    sub_app = 'distance'
    queryset = DistanceUsage.objects.all()
    serializer_class = DistanceUsageSerializer
    filters = [('amount', 'amount_search', float)]


class TopDistanceUsageListAPIView(BaseTopUsageListAPIView):
    """
    Top Distance Usage List\n
    GET params:
      - document_id: int
    """
    sub_app = 'distance'
    model = DistanceUsage
    grouping_item = 'amount'
    data_view = DistanceUsageListAPIView
    qs_values = ['amount', 'distance_type']
    qs_order_by = ['-amount', '-count']

    def get_detail_data(self, item):
        return [i for i in self.detail_data if
                i['distance_type'] == item['distance_type'] and i['amount'] == item['amount']]

    def update_item(self, item):
        item['url'] = '{}?distance_type_search={}&distance_amount_search={}'.format(
            reverse('v1:distance-usage'), item['distance_type'], item['amount'])
        return item


# --------------------------------------------------------
# Percent Usage Views
# --------------------------------------------------------

class PercentUsageSerializer(BaseUsageSerializer):
    class Meta(BaseUsageSerializer.Meta):
        model = PercentUsage
        fields = ['amount', 'unit_type', 'total', 'count']


class PercentUsageListAPIView(BaseUsageListAPIView):
    """
    Percent Usage List\n
    GET params:
      - document_id: int
      - unit_type: str
      - amount_search: float
    """
    sub_app = 'percent'
    queryset = PercentUsage.objects.all()
    serializer_class = PercentUsageSerializer
    filters = [('amount', 'amount_search', float)]


class TopPercentUsageListAPIView(BaseTopUsageListAPIView):
    """
    Top Percent Usage List\n
    GET params:
      - document_id: int
    """
    sub_app = 'percent'
    model = PercentUsage
    grouping_item = 'amount'
    data_view = PercentUsageListAPIView
    qs_values = ['amount', 'unit_type']
    qs_order_by = ['-amount', '-count']

    def get_detail_data(self, item):
        return [i for i in self.detail_data if
                i['unit_type'] == item['unit_type'] and i['amount'] == item['amount']]

    def update_item(self, item):
        item['url'] = '{}?percent_type_search={}&percent_amount_search={}'.format(
            reverse('v1:percent-usage'), item['unit_type'], item['amount'])
        return item


# --------------------------------------------------------
# Ratio Usage Views
# --------------------------------------------------------

class RatioUsageSerializer(BaseUsageSerializer):
    class Meta(BaseUsageSerializer.Meta):
        model = RatioUsage
        fields = ['amount', 'amount2', 'total', 'count']


class RatioUsageListAPIView(BaseUsageListAPIView):
    """
    Ratio Usage List\n
    GET params:
      - document_id: int
      - text_unit_id: int
      - amount_search: float
      - amount_search2: float
    """
    sub_app = 'ratio'
    queryset = RatioUsage.objects.all()
    serializer_class = RatioUsageSerializer
    filters = [('amount', 'amount_search', float),
               ('amount2', 'amount_search2', float)]


class TopRatioUsageListAPIView(BaseTopUsageListAPIView):
    """
    Top Ratio Usage List\n
    GET params:
      - document_id: int
    """
    sub_app = 'ratio'
    model = RatioUsage
    grouping_item = 'amount'
    data_view = RatioUsageListAPIView
    qs_values = ['amount', 'amount2']
    qs_order_by = ['-amount', '-count']

    def get_detail_data(self, item):
        return [i for i in self.detail_data if
                i['amount'] == item['amount'] and i['amount2'] == item['amount2']]

    def update_item(self, item):
        item['url'] = '{}?ratio_amount_search={}&ratio_amount2_search={}'.format(
            reverse('v1:ratio-usage'), item['amount'], item['amount2'])
        return item


# --------------------------------------------------------
# Citation Usage Views
# --------------------------------------------------------

class CitationUsageSerializer(BaseUsageSerializer):
    class Meta(BaseUsageSerializer.Meta):
        model = CitationUsage
        fields = ['volume', 'reporter', 'reporter_full_name', 'page', 'page2',
                  'court', 'year', 'citation_str', 'count']


class CitationUsageListAPIView(BaseUsageListAPIView):
    """
    Citation Usage List\n
    GET params:
      - document_id: int
      - text_unit_id: int
      - citation_str: str
      - citation_str_contains: str
      - year_str: str
      - reporter: str
      - court: str
    """
    sub_app = 'citation'
    queryset = CitationUsage.objects.all()
    serializer_class = CitationUsageSerializer
    filters = [('year', 'year_str', int)]


class TopCitationUsageListAPIView(BaseTopUsageListAPIView):
    """
    Top Citation Usage List\n
    GET params:
      - document_id: int
    """
    sub_app = 'citation'
    model = CitationUsage
    data_view = CitationUsageListAPIView
    grouping_item = 'citation_str'
    qs_values = ["citation_str"]
    url_args = ('v1:citation-usage', 'citation_search', 'citation_str')


# --------------------------------------------------------
# Copyright Usage Views
# --------------------------------------------------------

class CopyrightUsageSerializer(BaseUsageSerializer):
    class Meta(BaseUsageSerializer.Meta):
        model = CopyrightUsage
        fields = ['copyright_str', 'count']


class CopyrightUsageListAPIView(BaseUsageListAPIView):
    """
    Copyright Usage List\n
    GET params:
      - document_id: int
      - text_unit_id: int
      - copyright: str
      - copyright_contains: str
    """
    sub_app = 'copyright'
    queryset = CopyrightUsage.objects.all()
    serializer_class = CopyrightUsageSerializer
    filters = [('copyright_str', 'copyright', url_quote)]


class TopCopyrightUsageListAPIView(BaseTopUsageListAPIView):
    """
    Top Copyright Usage List\n
    GET params:
      - document_id: int
    """
    sub_app = 'copyright'
    model = CopyrightUsage
    data_view = CopyrightUsageListAPIView
    grouping_item = 'copyright_str'
    qs_values = ["copyright_str"]
    url_args = ('v1:copyright-usage', 'copyright_search', 'copyright_str')


# --------------------------------------------------------
# Trademark Usage Views
# --------------------------------------------------------

class TrademarkUsageSerializer(BaseUsageSerializer):
    class Meta(BaseUsageSerializer.Meta):
        model = TrademarkUsage
        fields = ['trademark', 'count']


class TrademarkUsageListAPIView(BaseUsageListAPIView):
    """
    Trademark Usage List\n
    GET params:
      - document_id: int
      - text_unit_id: int
      - trademark: str
    """
    sub_app = 'trademark'
    queryset = TrademarkUsage.objects.all()
    serializer_class = TrademarkUsageSerializer
    # filters = [('trademark', 'trademark_search', url_quote)]


class TopTrademarkUsageListAPIView(BaseTopUsageListAPIView):
    """
    Top Trademark Usage List\n
    GET params:
      - document_id: int
    """
    sub_app = 'trademark'
    model = TrademarkUsage
    data_view = TrademarkUsageListAPIView
    grouping_item = 'trademark'
    qs_values = ['trademark']
    url_args = ('v1:trademark-usage', 'trademark_search', 'trademark')


# --------------------------------------------------------
# Url Usage Views
# --------------------------------------------------------

class UrlUsageSerializer(BaseUsageSerializer):
    class Meta(BaseUsageSerializer.Meta):
        model = UrlUsage
        fields = ['source_url', 'count']


class UrlUsageListAPIView(BaseUsageListAPIView):
    """
    Url Usage List\n
    GET params:
      - document_id: int
      - text_unit_id: int
      - source_url: str
    """
    sub_app = 'url'
    queryset = UrlUsage.objects.all()
    serializer_class = UrlUsageSerializer
    # filters = [('source_url', 'url_search', str)]


class TopUrlUsageListAPIView(BaseTopUsageListAPIView):
    """
    Top Url Usage List\n
    GET params:
      - document_id: int
    """
    sub_app = 'url'
    model = UrlUsage
    data_view = UrlUsageListAPIView
    grouping_item = 'source_url'
    qs_values = ['source_url']
    url_args = ('v1:url-usage', 'url_search', 'source_url')

    def update_item(self, item):
        item['goto_url'] = item['source_url'] if item['source_url'].lower().startswith('http') \
            else 'http://' + item['source_url']
        return item


router = routers.DefaultRouter()
router.register(r'geo-entities', GeoEntityViewSet, 'geo-entity')
router.register(r'parties', PartyViewSet, 'party')


urlpatterns = [
    url(r'^term-usage/$', TermUsageListAPIView.as_view(),
        name='term-usage'),
    url(r'^term-usage/top/$', TopTermUsageListAPIView.as_view(),
        name='top-term-usage'),

    url(r'^geo-entity-usage/$', GeoEntityUsageListAPIView.as_view(),
        name='geo-entity-usage'),
    url(r'^geo-entity-usage/top/$', TopGeoEntityUsageListAPIView.as_view(),
        name='top-geo-entity-usage'),

    url(r'^geo-alias-usage/$', GeoAliasUsageListAPIView.as_view(),
        name='geo-alias-usage'),
    url(r'^geo-alias-usage/top/$', TopGeoAliasUsageListAPIView.as_view(),
        name='top-geo-alias-usage'),

    url(r'^typeahead/term-usage/(?P<field_name>[a-z_]+)/$', TypeaheadTermUsage.as_view(),
        name='typeahead-term-usage'),
    url(r'^typeahead/geo-entity-usage/(?P<field_name>[a-z_]+)/$', TypeaheadGeoEntityUsage.as_view(),
        name='typeahead-geo-entity-usage'),
    url(r'^typeahead/party-usage/(?P<field_name>[a-z_]+)/$', TypeaheadPartyUsage.as_view(),
        name='typeahead-party-usage'),

    url(r'^party-usage/$', PartyUsageListAPIView.as_view(),
        name='party-usage'),
    url(r'^party-usage/top/$', TopPartyUsageListAPIView.as_view(),
        name='top-party-usage'),
    url(r'^party/network-chart/$', PartyNetworkChartView.as_view(),
        name='party-network-chart'),

    url(r'^date-usage/$', DateUsageListAPIView.as_view(),
        name='date-usage'),
    url(r'^date-usage/top/$', TopDateUsageListAPIView.as_view(),
        name='top-date-usage'),
    url(r'^date-usage/timeline-chart/$', DateUsageTimelineView.as_view(),
        name='date-usage-timeline-chart'),
    url(r'^date-usage/calendar-chart/$', DateUsageCalendarView.as_view(),
        name='date-usage-calendar-chart'),
    url(r'^date-usage/to-ical/$', DateUsageToICalView.as_view(),
        name='date-usage-to-ical'),

    url(r'^date-duration-usage/$', DateDurationUsageListAPIView.as_view(),
        name='date-duration-usage'),
    url(r'^date-duration-usage/top/$', TopDateDurationUsageListAPIView.as_view(),
        name='top-date-duration-usage'),

    url(r'^definition-usage/$', DefinitionUsageListAPIView.as_view(),
        name='definition-usage'),
    url(r'^definition-usage/top/$', TopDefinitionUsageListAPIView.as_view(),
        name='top-definition-usage'),

    url(r'^court-usage/$', CourtUsageListAPIView.as_view(),
        name='court-usage'),
    url(r'^court-usage/top/$', TopCourtUsageListAPIView.as_view(),
        name='top-court-usage'),

    url(r'^currency-usage/$', CurrencyUsageListAPIView.as_view(),
        name='currency-usage'),
    url(r'^currency-usage/top/$', TopCurrencyUsageListAPIView.as_view(),
        name='top-currency-usage'),

    url(r'^regulation-usage/$', RegulationUsageListAPIView.as_view(),
        name='regulation-usage'),
    url(r'^regulation-usage/top/$', TopRegulationUsageListAPIView.as_view(),
        name='top-regulation-usage'),

    url(r'^amount-usage/$', AmountUsageListAPIView.as_view(),
        name='amount-usage'),
    url(r'^amount-usage/top/$', TopAmountUsageListAPIView.as_view(),
        name='top-amount-usage'),

    url(r'^distance-usage/$', DistanceUsageListAPIView.as_view(),
        name='distance-usage'),
    url(r'^distance-usage/top/$', TopDistanceUsageListAPIView.as_view(),
        name='top-distance-usage'),

    url(r'^percent-usage/$', PercentUsageListAPIView.as_view(),
        name='percent-usage'),
    url(r'^percent-usage/top/$', TopPercentUsageListAPIView.as_view(),
        name='top-percent-usage'),

    url(r'^ratio-usage/$', RatioUsageListAPIView.as_view(),
        name='ratio-usage'),
    url(r'^ratio-usage/top/$', TopRatioUsageListAPIView.as_view(),
        name='top-ratio-usage'),

    url(r'^citation-usage/$', CitationUsageListAPIView.as_view(),
        name='citation-usage'),
    url(r'^citation-usage/top/$', TopCitationUsageListAPIView.as_view(),
        name='top-citation-usage'),

    url(r'^copyright-usage/$', CopyrightUsageListAPIView.as_view(),
        name='copyright-usage'),
    url(r'^copyright-usage/top/$', TopCopyrightUsageListAPIView.as_view(),
        name='top-copyright-usage'),

    url(r'^trademark-usage/$', TrademarkUsageListAPIView.as_view(),
        name='trademark-usage'),
    url(r'^trademark-usage/top/$', TopTrademarkUsageListAPIView.as_view(),
        name='top-trademark-usage'),

    url(r'^url-usage/$', UrlUsageListAPIView.as_view(),
        name='url-usage'),
    url(r'^url-usage/top/$', TopUrlUsageListAPIView.as_view(),
        name='top-url-usage'),
]
