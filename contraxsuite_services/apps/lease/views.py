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

import urllib

import pycountry
from django.urls import reverse
from django.db import models
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.views.generic import TemplateView

import apps.common.mixins
from apps.document.views import DocumentDetailView
from apps.document.views import TextUnitListView
from apps.extract.models import (
    PartyUsage)
from apps.extract.models import TermUsage
from apps.lease.forms import ProcessLeaseDocumentsForm
from apps.lease.models import LeaseDocument
from apps.task.views import BaseAjaxTaskView

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.3.0/LICENSE"
__version__ = "1.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def search(request):
    """
    Search dispatcher.
    :param request:
    :return:
    """
    view_name = 'lease:lease-document-list'

    return redirect('{}?{}'.format(reverse(view_name), request.GET.urlencode()))


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


class LeaseMapDataView(apps.common.mixins.JSONResponseView):
    def get_json_data(self, request, *args, **kwargs):
        country = kwargs.get('country')
        province = kwargs.get('province')
        lessor = kwargs.get('lessor_name')

        if not country:
            q = LeaseDocument.objects \
                .values('address_country') \
                .annotate(
                leases_number=models.Count('address_country') if not lessor else models.Count(
                    models.Case(models.When(lessor=lessor, then=1)))) \
                .order_by('-leases_number', 'address_country')

            return [{'address_country': row['address_country'],
                     'address_country_code': _country_short(row['address_country']),
                     'leases_number': row['leases_number']}
                    for row in q if row['address_country']]
        elif not province:
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

            return [{'address_country': row['address_country'],
                     'address_country_code': _country_short(row['address_country']),
                     'address_state_province': row['address_state_province'],
                     'leases_number': row['leases_number']}
                    for row in rows if row['address_country']]
        else:
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

            return list(q.filter(f).annotate() if f else q)


class LeaseDashboardView(TemplateView):
    template_name = 'lease/lease_dashboard.html'


class LessorListView(apps.common.mixins.JSONResponseView):
    def get_json_data(self, request, *args, **kwargs):
        q = LeaseDocument.objects \
            .values('lessor') \
            .annotate(leases_number=models.Count('lessor')) \
            .order_by('-leases_number', 'lessor')
        data = [{'lessor': row['lessor'],
                 'leases_number': row['leases_number'],
                 'url': reverse('lease:lessor-details', args=[row['lessor']])
                 } for row in q if row['lessor']]
        return {'total_records': len(data), 'data': data}


class LessorDetailsView(DetailView):
    template_name = 'lease/lessor_details.html'

    def get_context_object_name(self, obj):
        return 'lessor'

    def get_object(self, queryset=None):
        lessor_name = self.kwargs.get('lessor_name')
        q = LeaseDocument.objects \
            .filter(lessor=lessor_name) \
            .values('lessor') \
            .annotate(leases_number=models.Count('lessor')) \
            .order_by('-leases_number', 'lessor')

        lessor = q[0]

        return {
            'name': lessor['lessor'],
            'leases_number': lessor['leases_number']
        }


class LeaseDocumentListView(apps.common.mixins.JqPaginatedListView):
    model = LeaseDocument

    json_fields = ['name', 'property_type', 'area_size_sq_ft', 'address', 'lessor', 'lessee',
                   'commencement_date',
                   'expiration_date', 'lease_type', 'total_rent_amount', 'rent_due_frequency',
                   'mean_rent_per_month',
                   'security_deposit']
    limit_reviewers_qs_by_field = ''
    field_types = {
        'pk': int,
        'name': str,
        'property_type': str,
        'area_size_sq_ft': float,
        'address': str,
        'lessor': str,
        'lessor_url': str,
        'lessee': str,
        'commencement_date': 'date',
        'expiration_date': 'date',
        'lease_type': str,
        'total_rent_amount': float,
        'rent_due_frequency': str,
        'mean_rent_per_month': float,
        'security_deposit': float,
        'url': str
    }

    def get_queryset(self):
        qs = super().get_queryset()

        lessor_name = self.kwargs.get('lessor_name')
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

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        if 'party_pk' in self.request.GET:
            tu_list_view = TextUnitListView(request=self.request)
            tu_data = tu_list_view.get_json_data()['data']
        for item in data['data']:
            item['url'] = reverse('lease:lease-document-detail', args=[item['pk']])
            item['lessor_url'] = reverse('lease:lessor-details', args=[item['lessor']])
            if 'party_pk' in self.request.GET:
                item['text_unit_data'] = [i for i in tu_data
                                          if i['document__pk'] == item['pk']]
        return data

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()
        params = dict(urllib.parse.parse_qsl(self.request.GET.urlencode()))
        ctx.update(params)
        return ctx


class LeaseDocumentDetailView(DocumentDetailView):
    model = LeaseDocument
    template_name = 'lease/lease_document.html'

    def get_context_data(self, **kwargs):
        document = self.object
        paragraph_list = document.textunit_set \
            .filter(unit_type='paragraph') \
            .order_by('id') \
            .prefetch_related(
            models.Prefetch(
                'termusage_set',
                queryset=TermUsage.objects.order_by('term__term').select_related('term'),
                to_attr='ltu'))
        ctx = {'document': document,
               'party_list': list(PartyUsage.objects.filter(
                   text_unit__document=document).values_list('party__name', flat=True)),
               'highlight': self.request.GET.get('highlight', ''),
               'paragraph_list': paragraph_list}
        return ctx


class ProcessLeaseDocumentsTaskView(BaseAjaxTaskView):
    task_name = 'Process Lease Documents'
    form_class = ProcessLeaseDocumentsForm
    html_form_class = 'popup-form process-lease-documents-form'
    metadata = dict(
        result_links=[{'name': 'View Lease Documents', 'link': 'lease:lease-dashboard'}])
