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
import operator
import re
from functools import reduce

# Third-party imports
from rest_framework import routers, serializers, viewsets, mixins
from rest_framework.generics import (
    ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView)

# Django imports
from django.conf import settings
from django.conf.urls import include, url
from django.core.urlresolvers import reverse
from django.db.models import Q, Sum
from django.http import JsonResponse

# Project imports
from apps.extract.models import *
from apps.common.mixins import (
    SimpleRelationSerializer, JqListAPIView, TypeaheadAPIView)


class BaseUsageSerializer(SimpleRelationSerializer):
    document_url = serializers.SerializerMethodField()
    text_unit_url = serializers.SerializerMethodField()

    class Meta:
        fields = []
        base_fields = ['pk', 'text_unit__document__pk', 'text_unit__document__name',
                       'text_unit__document__description', 'text_unit__document__document_type',
                       'text_unit__text', 'text_unit__pk']

    def __init__(self, instance=None, **kwargs):
        self.Meta.fields += self.Meta.base_fields
        super().__init__(instance, **kwargs)

    def get_document_url(self, obj):
        return reverse('v1:document-detail', args=[obj.text_unit.document.pk])

    def get_text_unit_url(self, obj):
        return reverse('v1:text-unit-detail', args=[obj.text_unit.pk])


class BaseUsageListAPIView(JqListAPIView):

    def get_queryset(self):
        qs = super().get_queryset()
        document_pk = self.request.GET.get('document_pk')
        if document_pk:
            qs = qs.filter(text_unit__document__pk=document_pk)
        return qs

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
    data_view = None
    grouping_item = None

    def __init__(self, queryset, *args, **kwargs):
        self.queryset = queryset
        self.request = kwargs.get('context', {}).get('request')
        if self.request and self.request.GET.get('document_pk'):
            self.detail_data = self.data_view(
                request=self.request, format_kwarg=None).get(request=self.request).data

    def get_detail_data(self, item):
        return [i for i in self.detail_data if
                i[self.grouping_item] == item[self.grouping_item]]

    @property
    def data(self):
        for item in self.queryset:
            item = self.update_item(item)
            if "document_pk" in self.request.GET:
                item['data'] = self.get_detail_data(item)
        return list(self.queryset)

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
    Term Usage List\n
    GET params:
      - document_pk: int
      - term_search: str
    """
    queryset = TermUsage.objects.all()
    serializer_class = TermUsageSerializer
    sub_app = 'term'

    def get_queryset(self):
        qs = super().get_queryset()
        term_search = self.request.GET.get("term_search", "")
        if term_search:
            qs = self.filter(term_search, qs,
                             _or_lookup='term__term__exact',
                             _and_lookup='text_unit__text__icontains',
                             _not_lookup='text_unit__text__icontains')
        # filter out duplicated Terms (equal terms, but diff. term sources)
        # qs = qs.order_by('term__term').distinct('term__term', 'text_unit__pk')
        return qs


class TopTermUsageSerializer(BaseTopUsageSerializer):
    data_view = TermUsageListAPIView
    grouping_item = 'term__term'

    def update_item(self, item):
        item['url'] = reverse('v1:term-usage') + '?term_search=' + item['term__term']
        return item


class TopTermUsageListAPIView(BaseUsageListAPIView):
    """
    Term Usage List\n
    GET params:
      - document_pk: int
    """
    queryset = TermUsage.objects.all()
    serializer_class = TopTermUsageSerializer
    sub_app = 'term'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.values('term__term', 'term__source') \
            .annotate(count=Sum('count')) \
            .values('term__term', 'count') \
            .order_by('-count', 'term__term')
        return qs


# --------------------------------------------------------
# Geo Entity Views
# --------------------------------------------------------

class GeoEntityListSerializer(serializers.ModelSerializer):
    alias = serializers.SerializerMethodField()

    class Meta:
        model = GeoEntity
        fields = ['pk', 'entity_id', 'name', 'priority', 'category',
                  'alias']

    def get_alias(self, obj):
        return ', '.join(
                GeoAlias.objects.filter(entity_id=obj.pk).values_list('alias', flat=True))


class GeoEntityListAPIView(ListAPIView):
    """
    GeoEntity List\n
    """
    queryset = GeoEntity.objects.all()
    serializer_class = GeoEntityListSerializer


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
    GeoEntity Usage List\n
    GET params:
      - document_pk: int
      - party_pk: int
      - entity_search: str
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
        party_pk = self.request.GET.get("party_pk")
        if party_pk:
            qs = qs.filter(
                text_unit__document__textunit__partyusage__party__pk=party_pk) \
                .distinct()
        return qs


class TopGeoEntityUsageSerializer(BaseTopUsageSerializer):
    data_view = GeoEntityUsageListAPIView
    grouping_item = 'entity__name'

    def update_item(self, item):
        item['url'] = reverse('v1:geo-entity-usage') + '?entity_search=' + item['entity__name']
        return item


class TopGeoEntityUsageListAPIView(BaseUsageListAPIView):
    """
    GeoEntity Usage List\n
    GET params:
      - document_pk: int
    """
    queryset = GeoEntityUsage.objects.all()
    serializer_class = TopGeoEntityUsageSerializer
    sub_app = 'geoentity'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.values('entity__name') \
            .annotate(count=Sum('count')) \
            .values('entity__name', 'count') \
            .order_by('-count', 'entity__name')
        return qs


urlpatterns = [
    url(r'^term-usage/$', TermUsageListAPIView.as_view(),
        name='term-usage'),
    url(r'^term-usage/top/$', TopTermUsageListAPIView.as_view(),
        name='top-term-usage'),

    url(r'^geo-entity/list/$', GeoEntityListAPIView.as_view(),
        name='geo-entity-list'),

    url(r'^geo-entity-usage/$', GeoEntityUsageListAPIView.as_view(),
        name='geo-entity-usage'),
    url(r'^geo-entity-usage/top/$', TopGeoEntityUsageListAPIView.as_view(),
        name='top-geo-entity-usage'),
]
