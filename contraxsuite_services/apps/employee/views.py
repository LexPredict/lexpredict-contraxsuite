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
    AjaxListView, AjaxResponseMixin, JqPaginatedListView, TypeaheadView)
from apps.document.models import Document
from apps.employee.models import (
    Employee, Employer)
from apps.task.views import BaseAjaxTaskView, LocateTaskView
from apps.task.models import Task
from apps.task.tasks import call_task, clean_tasks, purge_task

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.1/LICENSE"
__version__ = "1.0.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class EmployeeListView(JqPaginatedListView):
    model = Employee
    json_fields = ['document__pk', 'document__name', 'document__description',
                   'document__document_type', 'name', 'salary', 'title', 'effective_date',
                   'employer__name']
    field_types = dict(count=int)

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['employee_url'] = '#'
            item['url'] = reverse('document:document-detail',
                                  args=[item['document__pk']])
        return data

    def get_queryset(self):
        qs = super().get_queryset()
        term_search = self.request.GET.get("employee_search", "")

        if term_search:
            qs = qs.filter(name__icontains=term_search)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['employee_search'] = self.request.GET.get("employee_search", "")
        return ctx


class EmployerListView(JqPaginatedListView):
    model = Employee
    json_fields = ['name']
    field_types = dict(count=int)

    def get_json_data(self, **kwargs):
        data = super().get_json_data()
        for item in data['data']:
            item['url'] =  '#'
        return data

    def get_queryset(self):
        qs = super().get_queryset()
        term_search = self.request.GET.get("employer_search", "")

        if term_search:
            qs = self.filter(term_search, qs,
                             _or_lookup='employer__employer__exact')

        # filter out duplicated Terms (equal terms, but diff. term sources)
        # qs = qs.order_by('term__term').distinct('term__term', 'text_unit__pk')
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['employer_search'] = self.request.GET.get("employer_search", "")
        return ctx

