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

# Third-party imports
from rest_framework import serializers, routers, viewsets
import rest_framework.views

# Django imports
from django.conf.urls import url
from django.http import JsonResponse
from django.db.models import Count, F
from django.urls import reverse

# Project imports
import apps.common.mixins
from apps.employee.models import *
from apps.employee.views import LocateEmployeesView

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.2/LICENSE"
__version__ = "1.2.2"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# --------------------------------------------------------
# Employee Views
# --------------------------------------------------------

class EmployeeSerializer(apps.common.mixins.SimpleRelationSerializer):
    class Meta:
        model = Employee
        fields = ['pk', 'document__pk', 'document__name', 'document__description',
                  'document__document_type', 'name', 'annual_salary',
                  'salary_currency', 'effective_date', 'employer__name',
                  'employer__pk', 'has_noncompete', 'has_termination',
                  'has_severance', 'vacation_yearly', 'governing_geo']


class EmployeeViewSet(apps.common.mixins.JqListAPIMixin, viewsets.ReadOnlyModelViewSet):
    """
    list: Employee List\n
        GET params:
          - name: str
          - name_contains: str
          - employer_id: int
          - document_id: int
          - governing_geo: str
          - governing_geo_contains: str
    retrieve: Retrieve Employees
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


# --------------------------------------------------------
# Employer Views
# --------------------------------------------------------

class EmployerSerializer(apps.common.mixins.SimpleRelationSerializer):
    total_contracts = serializers.SerializerMethodField()
    total_employees = serializers.SerializerMethodField()

    class Meta:
        model = Employer
        fields = ['pk', 'name', 'total_contracts', 'total_employees']

    def get_total_contracts(self, obj):
        return obj.employee_set.count()

    def get_total_employees(self, obj):
        return obj.employee_set.values('name').annotate(Count('name')).count()


class EmployerViewSet(apps.common.mixins.JqListAPIMixin, viewsets.ReadOnlyModelViewSet):
    """
    list: Employer List\n
        GET params:
          - name: str
          - name_contains: str
    retrieve: Retrieve Employers
    """
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer


# --------------------------------------------------------
# Provision Views
# --------------------------------------------------------

class ProvisionSerializer(apps.common.mixins.SimpleRelationSerializer):
    class Meta:
        model = Provision
        fields = ['pk', 'text_unit__text', 'text_unit__pk', 'similarity', 'type',
                  'employee__name', 'employee__pk', 'document__pk', 'document__name']


class ProvisionListAPIView(apps.common.mixins.JqListAPIView):
    """
    Provision List\n
    GET params:
      - document_id: int
      - employee_id: int
      - type: str
    """
    queryset = Provision.objects.all()
    serializer_class = ProvisionSerializer


class EmployeeGeoChartView(rest_framework.views.APIView):
    """
    Employee Geo Chart List\n
    GET params:
      - employer_id: int
    """
    def get(self, request, *args, **kwargs):
        qs = Employee.objects.all()
        if 'employer_id' in request.GET:
            qs = qs.filter(employer__pk=request.GET['employer_id'])
        location_list = list(qs.order_by('name', '-effective_date').distinct('name').values_list('governing_geo', flat=True))
        data = [['location', 'count']] + [[i, location_list.count(i)] for i in set(location_list)
                                          if i is not None]
        return JsonResponse(data, safe=False)


class EmployeeTimelineChartView(rest_framework.views.APIView):
    """
    Employee Timeline Chart List\n
    GET params:
      - employer_id: int
    """
    def get(self, request, *args, **kwargs):

        qs = Employee.objects.filter(effective_date__isnull=False)
        if "employer_id" in self.request.GET:
            qs = qs.filter(employer__pk=self.request.GET['employer_id'])

        qs = qs.order_by('effective_date') \
            .values('pk', 'name', start=F('effective_date'))
        data = list(qs)
        visible_interval = 180

        for item in data:
            item['url'] = reverse('v1:employee-detail', args=[item['pk']])

        focus_date = data[-1]['start'] if data else datetime.date.today()
        initial_start_date = focus_date - datetime.timedelta(days=visible_interval)
        initial_end_date = focus_date + datetime.timedelta(days=visible_interval)
        ret = {'data': data,
               'initial_start_date': initial_start_date,
               'initial_end_date': initial_end_date}
        return JsonResponse(ret)


class LocateEmployeesAPIView(rest_framework.views.APIView, LocateEmployeesView):
    """
    "Locate Employees" admin task\n
    POST params:
        - no_detect: bool
        - document_type: str[]
        - delete: bool
    """
    http_method_names = ["get", "post"]


router = routers.DefaultRouter()
router.register(r'employees', EmployeeViewSet, 'employee')
router.register(r'employers', EmployerViewSet, 'employer')


urlpatterns = [
    url(r'^provisions/$', ProvisionListAPIView.as_view(), name='provision'),

    url(r'^employee-geo-chart/$', EmployeeGeoChartView.as_view(),
        name='employee-geo-chart'),
    url(r'^employee-timeline-chart/$', EmployeeTimelineChartView.as_view(),
        name='employee-timeline-chart'),

    url(r'^locate-employees/$', LocateEmployeesAPIView.as_view(),
        name='locate-employees'),
]