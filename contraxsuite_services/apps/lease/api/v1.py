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

import pycountry
from django.db import models
from django.http import JsonResponse
from rest_framework import routers, serializers, viewsets
from rest_framework.decorators import detail_route, list_route

from apps.lease.models import LeaseDocument


class LeaseDocumentShortSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LeaseDocument
        fields = ['pk', 'name', 'property_type', 'address',
                  'lessee', 'lessor',
                  'lease_type',
                  'commencement_date', 'expiration_date',
                  'area_size_sq_ft', 'rent_due_frequency',
                  'mean_rent_per_month',
                  'security_deposit'
                  ]


class LeaseDocumentFullSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LeaseDocument
        fields = ['pk', 'name', 'property_type', 'address',
                  'lessee', 'lessor',
                  'lease_type',
                  'commencement_date', 'expiration_date',
                  'area_size_sq_ft', 'rent_due_frequency',
                  'mean_rent_per_month',
                  'security_deposit',
                  'full_text'
                  ]


class LeaseDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LeaseDocument.objects.all()
    serializer_class = LeaseDocumentShortSerializer

    def list(self, request, *args, **kwargs):
        """
        lessor_name -- Filter by lessor - 'equals'. (query param).

        description_search -- Filter by document description - 'contains' (query param).

        name_search -- Filter by document name - 'contains' (query param).
        """
        return super(LeaseDocumentViewSet, self).list(args, kwargs)

    def get_queryset(self):
        qs = super().get_queryset()

        lessor_name = self.request.GET.get('lessor_name')
        if lessor_name:
            qs = qs.filter(lessor=lessor_name)

        description_search = self.request.GET.get('description_search')
        if description_search:
            qs = qs.filter(description__icontains=description_search)

        name_search = self.request.GET.get('name_search')
        if name_search:
            qs = qs.filter(name__icontains=name_search)

        if 'party_pk' in self.request.GET:
            qs = qs.filter(textunit__partyusage__party__pk=self.request.GET['party_pk'])

        return qs

    @detail_route(['get'], url_path='full')
    def full(self, request, *args, **kwargs):
        doc = self.get_object()
        serializer = LeaseDocumentFullSerializer(doc)
        return JsonResponse(serializer.data, safe=False)


class LeaseMapViewSet(viewsets.ViewSet):
    def _country_short(country_long):
        if country_long == 'Russia':
            country_long = 'Russian Federation'

        try:
            return pycountry.countries.get(name=country_long).alpha_2
        except:
            try:
                return pycountry.countries.get(official_name=country_long).alpha_2
            except:
                try:
                    return pycountry.countries.get(common_name=country_long).alpha_2
                except:
                    return country_long

    @list_route(['get'], url_path='document-numbers-by-country')
    def lease_doc_number_by_country(self, request):
        """
        lessor -- Filter by lessor name
        """
        lessor = request.query_params.get('lessor', None)
        q = LeaseDocument.objects \
            .values('address_country') \
            .annotate(
            leases_number=models.Count('address_country') if not lessor else models.Count(
                models.Case(models.When(lessor=lessor, then=1)))) \
            .order_by('-leases_number', 'address_country')

        data = {'rows': [{'address_country': row['address_country'],
                          'address_country_code': LeaseMapViewSet._country_short(
                              row['address_country']),
                          'leases_number': row['leases_number']}
                         for row in q if row['address_country']]}
        return JsonResponse(data)

    @list_route(['get'], url_path=r'document-numbers-by-province/(?P<country>[^/$]+)')
    def lease_doc_number_by_province(self, request, country: str = None):
        """
        lessor -- Filter by lessor name (query param)
        """
        lessor = request.query_params.get('lessor', None)
        q = LeaseDocument.objects \
            .values('address_country', 'address_state_province') \
            .annotate(
            leases_number_country=models.Count(
                'address_country') if not lessor else models.Count(
                models.Case(models.When(lessor=lessor, then=1)))) \
            .annotate(
            leases_number=models.Count(
                'address_state_province') if not lessor else models.Count(
                models.Case(models.When(lessor=lessor, then=1)))) \
            .order_by('-leases_number', 'address_state_province')

        if country != 'all':
            q = q.filter(address_country=country)

        rows = list(q)

        data = {'rows': [{'address_country': row['address_country'],
                          'address_country_code': LeaseMapViewSet._country_short(
                              row['address_country']),
                          'address_state_province': row['address_state_province'],
                          'leases_number': row['leases_number']}
                         for row in rows if row['address_country']]}
        return JsonResponse(data)

    @list_route(['get'],
                url_path=r'document-addresses/(?P<country>[^/$]+)/(?P<province>[^/$]+)')
    def lease_doc_adresses(self, request, country: str = None, province: str = None):
        """
        lessor -- Filter by lessor name (query param)

        country: Country name as returned from document-numbers-by-country or
                        'all' to return addresses for all countries.

        province: State/province name as returned from document-numbers-by-province or
                        'all' to return addresses for all states/provinces.
        """
        lessor = request.query_params.get('lessor', None)
        q = LeaseDocument.objects.values('pk', 'name', 'address_longitude', 'address_latitude',
                                         'address',
                                         'address_country', 'address_state_province',
                                         'lessor', 'lessee')
        if lessor:
            q = q.filter(lessor=lessor)

        fl = []
        if country != 'all':
            fl.append(models.Q(address_country=country))
        if province != 'all':
            fl.append(models.Q(address_state_province=province))
        if lessor:
            fl.append(models.Q(lessor=lessor))

        f = None
        for item in fl:
            f = f & item if f else item

        data = {'rows': list(q.filter(f).annotate() if f else q)}
        return JsonResponse(data)


class LessorViewSet(viewsets.ViewSet):
    def list(self, request):
        q = LeaseDocument.objects \
            .values('lessor') \
            .annotate(leases_number=models.Count('lessor')) \
            .order_by('-leases_number', 'lessor')
        data = [{'lessor': row['lessor'],
                 'leases_number': row['leases_number']
                 } for row in q if row['lessor']]
        return JsonResponse({'total_records': len(data), 'data': data})

    def retrieve(self, request, pk):
        """
        id -- lessor name
        """
        lessor_name = pk
        q = LeaseDocument.objects \
            .filter(lessor=lessor_name) \
            .values('lessor') \
            .annotate(leases_number=models.Count('lessor')) \
            .order_by('-leases_number', 'lessor')

        lessor = q[0]

        return JsonResponse({
            'name': lessor['lessor'],
            'leases_number': lessor['leases_number']
        })


router = routers.DefaultRouter()
router.register(r'documents', LeaseDocumentViewSet, 'documents')
router.register(r'map-data', LeaseMapViewSet, 'map-data')
router.register(r'lessors', LessorViewSet, 'lessors')
