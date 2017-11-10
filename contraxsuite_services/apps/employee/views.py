# -*- coding: utf-8 -*-

# Future imports
from __future__ import absolute_import, unicode_literals

# Standard imports
from collections import defaultdict
import datetime
import itertools
import json
import geocoder

# Third-party import
import icalendar

# Django imports
from django.core.urlresolvers import reverse
from django.db.models import Count, F, Max, Min, Sum, Q
from django.db.models.functions import TruncMonth
from django.http import Http404
from django.http.response import HttpResponse
from django.views.generic import DetailView, TemplateView

# Project imports
from apps.common.mixins import (
    JSONResponseView, AjaxListView, AjaxResponseMixin, JqPaginatedListView, TypeaheadView)
from apps.document.models import Document
from apps.employee.models import (
    Employee, Employer, EmployerUsage, Provision)
from apps.task.views import BaseAjaxTaskView, LocateTaskView
from apps.task.models import Task
from apps.task.tasks import call_task, clean_tasks, purge_task
from apps.common.mixins import (
    AjaxListView, CustomUpdateView, CustomCreateView, CustomDeleteView,
    JqPaginatedListView, PermissionRequiredMixin, SubmitView, TypeaheadView)

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.1/LICENSE"
__version__ = "1.0.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class EmployeeListView(JqPaginatedListView):
    model = Employee
    json_fields = ['document__pk', 'document__name', 'document__description',
                   'document__document_type', 'name', 'annual_salary', 'salary_currency', 'effective_date',
                   'employer__name', 'employer__pk', 'has_noncompete', 'has_termination', 'vacation_yearly',
                   'governing_geo']
    field_types = dict(count=int)

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['detail_url'] = reverse('employee:employee-detail', args=[item['pk']])
            item['employer_url'] = reverse('employee:employer-detail', args=[item['employer__pk']]) if item['employer__pk'] else None
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
    template_name="employee/provision_list.html"
    json_fields = [ 'text_unit__text', 'text_unit__pk','similarity', 'type','employee__name', 'employee__pk',
                    'document__pk', 'document__name']
    field_types = dict(count=int)

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['detail_url'] = reverse('document:text-unit-detail', args=[item['text_unit__pk']])
        return data

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx

    def get_queryset(self):
        qs = super().get_queryset()
        if "employee__pk" in self.request.GET:
            qs = qs.filter(employee__pk =self.request.GET['employee__pk'])
        if "type" in self.request.GET:
            qs=qs.filter(type= self.request.GET['type'])
        return qs


class EmployerListView(JqPaginatedListView):
    model = Employer
    template_name="employee/employer_list.html"
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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx


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


class EmployerGeoChartView(JSONResponseView):

    def get_json_data(self, request):
        qs = Employee.objects.all()
        if 'employer_pk' in request.GET:
            qs = qs.filter(employer__pk=request.GET['employer_pk'])
        location_list = list(qs.order_by('name', '-effective_date').distinct('name').values_list('governing_geo', flat=True))
        data = [['location', 'count']] + [[i, location_list.count(i)] for i in set(location_list) if i != None]
        return data

