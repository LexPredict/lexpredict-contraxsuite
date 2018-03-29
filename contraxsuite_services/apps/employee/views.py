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

# Django imports
from django.core.urlresolvers import reverse
from django.db.models import Count, F
from django.views.generic import DetailView

# Project imports
from apps.employee.tasks import *     # noqa - append tasks.py in sys.modules
from apps.employee.models import (
    Employee, Employer, Provision)
from apps.employee.forms import LocateEmployeesForm
from apps.task.views import BaseAjaxTaskView
from apps.common.mixins import (
    JSONResponseView, JqPaginatedListView, PermissionRequiredMixin)


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.5/LICENSE"
__version__ = "1.0.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class EmployeeListView(JqPaginatedListView):
    model = Employee
    json_fields = ['document__pk', 'document__name', 'document__description',
                   'document__document_type', 'name', 'annual_salary',
                   'salary_currency', 'effective_date', 'employer__name',
                   'employer__pk', 'has_noncompete', 'has_termination',
                   'has_severance', 'vacation_yearly', 'governing_geo']
    field_types = dict(count=int)

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['detail_url'] = reverse('employee:employee-detail', args=[item['pk']])
            item['employer_url'] = reverse('employee:employer-detail', args=[item['employer__pk']]) \
                if item['employer__pk'] else None
            item['url'] = reverse('document:document-detail', args=[item['document__pk']])
        return data

    def get_queryset(self):
        qs = super().get_queryset()

        if "employer_pk" in self.request.GET:
            qs = qs.filter(employer__pk=self.request.GET['employer_pk'])

        term_search = self.request.GET.get("employee_search", "")

        if term_search:
            qs = qs.filter(name__icontains=term_search)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['employee_search'] = self.request.GET.get("employee_search", "")
        return ctx


class ProvisionListView(JqPaginatedListView):
    model = Provision
    template_name = "employee/provision_list.html"
    json_fields = ['text_unit__text', 'text_unit__pk', 'similarity', 'type',
                   'employee__name', 'employee__pk', 'document__pk', 'document__name']
    field_types = dict(count=int)

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['detail_url'] = reverse('document:text-unit-detail', args=[item['text_unit__pk']])
        return data

    def get_queryset(self):
        qs = super().get_queryset()
        if "employee__pk" in self.request.GET:
            qs = qs.filter(employee__pk=self.request.GET['employee__pk'])
        if "type" in self.request.GET:
            qs = qs.filter(type= self.request.GET['type'])
        return qs


class EmployerListView(JqPaginatedListView):
    model = Employer
    template_name = "employee/employer_list.html"
    json_fields = ['name']
    annotate = {'count': Count('employee')}

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] = reverse('employee:employer-detail', args=[item['pk']])
        return data


class EmployeeDetailView(PermissionRequiredMixin, DetailView):
    model = Employee
    template_name = "employee/employee_detail.html"
    raise_exception = True

    def has_permission(self):
        return self.request.user.can_view_document(self.get_object().document)


class EmployerDetailView(PermissionRequiredMixin, DetailView):
    model = Employer
    template_name = "employee/employer_detail.html"
    raise_exception = True

    def has_permission(self):
        return True

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_contracts'] = self.object.employee_set.count()
        ctx['total_employees'] = self.object.employee_set.values('name').annotate(Count('name')).count()
        return ctx


class EmployeeGeoChartView(JSONResponseView):

    def get_json_data(self, request, *args, **kwargs):
        qs = Employee.objects.all()
        if 'employer_pk' in request.GET:
            qs = qs.filter(employer__pk=request.GET['employer_pk'])
        location_list = list(qs.order_by('name', '-effective_date').distinct('name').values_list('governing_geo', flat=True))
        data = [['location', 'count']] + [[i, location_list.count(i)] for i in set(location_list)
                                          if i is not None]
        return data


class EmployeeTimelineChartView(JSONResponseView):

    def get_json_data(self, request, *args, **kwargs):

        qs = Employee.objects.filter(effective_date__isnull=False)
        if "employer_pk" in self.request.GET:
            qs = qs.filter(employer__pk=self.request.GET['employer_pk'])

        qs = qs.order_by('effective_date') \
            .values('pk', 'name', start=F('effective_date'))
        data = list(qs)
        visible_interval = 180

        for item in data:
            item['url'] = reverse('employee:employee-detail', args=[item['pk']])

        focus_date = data[-1]['start'] if data else datetime.date.today()
        initial_start_date = focus_date - datetime.timedelta(days=visible_interval)
        initial_end_date = focus_date + datetime.timedelta(days=visible_interval)
        return {'data': data,
                'initial_start_date': initial_start_date,
                'initial_end_date': initial_end_date}


class LocateEmployeesView(BaseAjaxTaskView):
    task_name = 'Locate Employees'
    form_class = LocateEmployeesForm
    metadata = dict(
        result_links=[{'name': 'View Employee List', 'link': 'employee:employee-list'},
                      {'name': 'View Employer List', 'link': 'employee:employer-list'}])
