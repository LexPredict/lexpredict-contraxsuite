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
import json
import operator
import os
import re
import traceback
from collections import OrderedDict
from functools import reduce
from types import GeneratorType

# Third-party imports
import pandas as pd
import rest_framework
import rest_framework.filters
import rest_framework.generics
import rest_framework.response
from typing import Tuple, Union, List, Any, Optional, Dict

# Django imports
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.core.exceptions import FieldError
from django.core.paginator import Paginator, EmptyPage
from django.db import connection
from django.db.models import Q, fields as django_fields, NOT_PROVIDED, QuerySet
from django.http import JsonResponse
from django.http.response import StreamingHttpResponse
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.base import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import MultipleObjectMixin
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.fields import empty as EMPTY
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin

# Project imports
from apps.common.model_utils.improved_django_json_encoder import ImprovedDjangoJSONEncoder
from apps.common.models import Action, CustomAPIRequestLog
from apps.common.querysets import QuerySetWoCache
from apps.common.streaming_utils import csv_gen_from_dicts
from apps.common.utils import cap_words, export_qs_to_file, download, full_reverse

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


base_success_msg = '%s "%s" was successfully %s.'


class AdminRequiredMixin(PermissionRequiredMixin):
    raise_exception = True

    def has_permission(self):
        return not self.request.user.is_reviewer


class TechAdminRequiredMixin(PermissionRequiredMixin):
    raise_exception = True

    def has_permission(self):
        return self.request.user.is_admin


class AppBlockMixin(PermissionRequiredMixin):
    raise_exception = True

    def has_permission(self):
        from apps.task.utils.task_utils import check_blocks

        return not check_blocks(raise_error=False)


def get_model(self):
    model = None
    try:
        model = self.model
    except AttributeError:
        pass
    if not model:
        try:
            model = self.get_form_class()._meta.model
        except AttributeError:
            pass
    if not model:
        try:
            model = self.get_queryset().model
        except AttributeError:
            pass
    return model


class AddModelNameMixin(LoginRequiredMixin):
    """
    Add extra variables related with model into context.
    """
    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        model = get_model(self)
        res['model_name'] = model._meta.verbose_name
        res['model_name_init'] = model._meta.model_name
        res['model_name_plural'] = model._meta.verbose_name_plural
        res['model_obj'] = model
        res['model_app'] = model._meta.app_label
        return res


class MessageMixin:
    """
    Pass custom success message in messages
    """
    def form_valid(self, form):
        response = super().form_valid(form)
        if hasattr(form, 'multiple_objects_created') and form.multiple_objects_created > 1:
            msg = '%d "%s" were created/updated successfully' % (
                form.multiple_objects_created,
                cap_words(self.object._meta.verbose_name_plural))
        else:
            msg = base_success_msg % (
                cap_words(self.object._meta.verbose_name),
                self.object.__str__(), self.success_message)
        messages.success(self.request, msg)
        return response


class TemplateNamesMixin:
    """
    Add "model_name_suffix.html" template name format (extra "_")
    """
    def get_template_names(self):
        if self.template_name is not None:
            return self.template_name
        names = super().get_template_names()
        model = get_model(self)
        app_label = model._meta.app_label
        template_name = '{}{}.html'.format(
            model._meta.verbose_name.replace(' ', '_'),
            self.template_name_suffix)
        names.append(os.path.join(app_label, template_name))
        names.append('{}{}.html'.format('base', self.template_name_suffix))
        return names


class SingleObjectMixin(MessageMixin, AddModelNameMixin, TemplateNamesMixin):
    pass


class CustomCreateView(AdminRequiredMixin, SingleObjectMixin, CreateView):
    success_message = 'created'

    def get_form_class(self):
        self.fields = self.get_fields()
        return super().get_form_class()

    def get_fields(self):
        return self.fields


class CustomUpdateView(CustomCreateView, UpdateView):
    success_message = 'updated'


class CustomDetailView(CustomUpdateView):
    """
    Detail view based on Update view to pass form in context
    and iterate over form fields with field names/labels
    """
    template_name_suffix = '_detail'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['fields'] = self.fields
        update_url = self.get_update_url()
        ctx['update_url'] = update_url
        # url = urllib.parse.urlparse(self.request.get_full_path())
        # ctx['edit_url'] = urllib.parse.urlunparse(
        #     (url.scheme, url.netloc, edit_url, url.params, url.query, url.fragment))
        return ctx

    def get_update_url(self):
        return reverse(
            '{}:{}-update'.format(
                self.model._meta.app_label,
                self.model._meta.verbose_name.replace(' ', '-')),
            args=[self.kwargs.get(self.slug_field, self.kwargs[self.pk_url_kwarg])])


class ReviewerQSMixin(MultipleObjectMixin):
    limit_reviewers_qs_by_field = None

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_reviewer and self.limit_reviewers_qs_by_field is not None:
            # limit qs for reviewers
            if isinstance(self.limit_reviewers_qs_by_field, (list, tuple)):
                lookup = {'%s__taskqueue__reviewers' % i: self.request.user for i in
                          self.limit_reviewers_qs_by_field}
            elif self.limit_reviewers_qs_by_field == "":
                lookup = {'taskqueue__reviewers': self.request.user}
            else:
                lookup = {
                    '%s__taskqueue__reviewers'
                    % self.limit_reviewers_qs_by_field: self.request.user}
            qs = qs.filter(**lookup)
        return qs


class BaseCustomListView(AddModelNameMixin, TemplateNamesMixin, ListView):
    paginate_by = 10
    export_params = dict(
        column_names=None,
        url_name=None,
        get_params=None
    )

    # handle "export" requests
    def get(self, request, *args, **kwargs):
        if 'export' in self.request.GET:
            return export_qs_to_file(
                request, qs=self.get_queryset(), **self.export_params)
        return super().get(request, *args, **kwargs)

    @staticmethod
    def filter(search_str, qs: QuerySet, _or_lookup,
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


class CustomListView(ReviewerQSMixin, BaseCustomListView):
    pass


class CustomDeleteView(AddModelNameMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'base_delete.html'
    raise_exception = True

    def handle_no_permission(self):
        if self.request.is_ajax():
            data = {'message': 'Permission denied.', 'level': 'error'}
            return JsonResponse(data, encoder=ImprovedDjangoJSONEncoder, safe=False)
        return super().handle_no_permission()

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            return JsonResponse(str(self.get_object()), encoder=ImprovedDjangoJSONEncoder, safe=False)
        return super().get(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        msg = base_success_msg % (
            cap_words(obj._meta.verbose_name),
            obj.__str__(), 'deleted')
        if request.is_ajax():
            obj.delete()
            data = {'message': msg, 'level': 'success'}
            return JsonResponse(data, encoder=ImprovedDjangoJSONEncoder, safe=False)
        messages.success(request, msg)
        return super().post(request, *args, **kwargs)


class AjaxResponseMixin:

    def render_to_response(self, *args, **kwargs):
        if self.request.is_ajax() or self.request.GET.get('to_json') == 'true':
            data = self.get_json_data(**kwargs)
            return JsonResponse(data, encoder=ImprovedDjangoJSONEncoder, safe=False)
        return super().render_to_response(*args, **kwargs)


class JSONResponseView(View):

    def response(self, request, *args, **kwargs):
        try:
            data = self.get_json_data(request, *args, **kwargs)
        except Exception as e:
            return JsonResponse(str(e), encoder=ImprovedDjangoJSONEncoder, safe=False, status=400)
        return JsonResponse(data, encoder=ImprovedDjangoJSONEncoder, safe=False)

    def get(self, request, *args, **kwargs):
        return self.response(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.response(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.response(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.response(request, *args, **kwargs)

    def get_json_data(self, request, *args, **kwargs):
        return []


class TypeaheadView(ReviewerQSMixin, JSONResponseView):

    DEFAULT_LIMIT = 30

    def get_json_data(self, request, *args, **kwargs):
        qs = self.model.objects.all()
        if "q" in request.GET:
            search_key = '%s__icontains' % self.search_field
            qs = qs.filter(**{search_key: request.GET.get("q")})\
                .order_by(self.search_field).distinct(self.search_field)
        return self.qs_to_values(qs)

    def qs_to_values(self, qs):
        return [{"value": i} for i in qs.values_list(self.search_field, flat=True)[:self.DEFAULT_LIMIT]]


class SubmitView(JSONResponseView):
    error_message = 'Error'
    success_message = 'Success'

    def response(self, request, *args, **kwargs):
        try:
            data = self.process(request)
        except:
            data = self.failure()
        return JsonResponse(data, encoder=ImprovedDjangoJSONEncoder, safe=False)

    def get_success_message(self):
        return self.success_message

    def get_error_message(self):
        return self.error_message

    def failure(self):
        return {'message': self.get_error_message(), 'status': 'error'}

    def success(self, data=None):
        ret = {'message': self.get_success_message(), 'status': 'success'}
        if data is not None:
            ret.update(data)
        return ret


class AjaxListView(ReviewerQSMixin, AjaxResponseMixin, BaseCustomListView):
    json_fields = []
    extra_json_fields = []
    annotate = {}

    # TODO: remove duplication with BaseCustomListView
    # handle "export" requests
    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()

        if request.is_ajax():
            if 'export' in self.request.GET:
                return export_qs_to_file(
                    request, qs=qs, **self.export_params)
            if request.GET.get('export_to') in ['csv', 'xlsx', 'pdf']:
                data = self.get_json_data(qs=qs)
                if isinstance(data, dict) and 'data' in data:
                    data = data['data']
                return self.export(data,
                                   source_name=self.get_export_file_name() or
                                               qs.model.__name__.lower(),
                                   fmt=request.GET.get('export_to'))
            return self.render_to_response(qs=qs)

        self.object_list = qs
        context = self.get_context_data()
        if request.GET.get('debug') == 'true':
            context['json_data'] = self.get_json_data(qs=qs)
        return self.render_to_response(context)

    def get_json_data(self, **kwargs):
        qs = kwargs.get('qs')
        if qs is None:
            qs = self.get_queryset()
        extra_json_fields = list(self.extra_json_fields)
        extra_json_fields.append('pk')
        extra_json_fields += list(self.annotate.keys())
        if not self.json_fields:
            self.json_fields = [f.name for f in self.model._meta.concrete_fields]

        if 'columns' in self.request.GET:
            columns = self.request.GET['columns'].split(',')
        else:
            columns = self.json_fields + extra_json_fields
        data = list(qs.annotate(**self.annotate).values(*columns))

        # TODO: consider replace none_to_bool - either use default=False or update jqWidgets
        bool_fields = [i.name for i in self.model._meta.fields
                       if isinstance(i, django_fields.BooleanField)]
        for row in data:
            row.update((k, False) for k, v in row.items() if v is None and k in bool_fields)
            if not kwargs.get('keep_tags'):
                row.update((k, v.replace("<", "&lt;").replace(">", "&gt;"))
                           for k, v in row.items() if isinstance(v, str))

        return data

    def export(self, data, source_name, fmt='csv'):
        data = self.process_export_data(data)
        return download(data, fmt, file_name=source_name)

    def process_export_data(self, data):
        return data

    def get_export_file_name(self):
        return


class JqPaginatedListMixin:
    conditions = dict(EQUAL='iexact',  # should be plain for numbers
                      EQUAL_CASE_SENSITIVE='exact',
                      FULL_TEXT_SEARCH='full_text_search',
                      CONTAINS='icontains',
                      CONTAINS_CASE_SENSITIVE='contains',
                      LESS_THAN='lt',
                      LESS_THAN_OR_EQUAL='lte',
                      GREATER_THAN='gt',
                      GREATER_THAN_OR_EQUAL='gte',
                      STARTS_WITH='istartswith',
                      ENDS_WITH='iendswith',
                      STARTS_WITH_CASE_SENSITIVE='startswith',
                      ENDS_WITH_CASE_SENSITIVE='endswith')
    equal_as_exact_db_types = ['integer', 'smallint', 'double precision']
    string_only_conditions = {
        'iexact', 'exact', 'icontains', 'istartswith', 'iendswith',
        'startswith', 'endswith'}

    conditions_empty = dict(EMPTY=('exact', ''),
                            NULL=('isnull', True),
                            NOT_NULL=('isnull', False))
    conditions_neg = dict(DOES_NOT_CONTAIN='icontains',
                          DOES_NOT_CONTAIN_CASE_SENSITIVE='contains',
                          NOT_EQUAL='exact')
    field_types = dict()
    field_name_transform_map = {}
    unique_field = 'pk'

    def get_field_types(self):
        return self.field_types

    def filter_and_sort(self, qs):
        """
        Filter and sort data on server side.
        """
        qs = self.filter(qs)

        qs = self.sort(qs)

        return qs

    def read_request_filters(self) -> Dict[str, Any]:
        filterscount = int(self.request.GET.get('filterscount', 0))
        # server-side filtering
        filters = dict()
        if filterscount:
            for filter_num in range(filterscount):
                num = str(filter_num)
                field = self.request.GET.get('filterdatafield' + num).replace('-', '_')
                field = self.field_name_transform_map.get(field, field)
                value = (self.get_field_types() or self.field_types).get(field, str)(
                    self.request.GET.get('filtervalue' + num))
                condition = self.request.GET.get('filtercondition' + num)
                op = int(self.request.GET.get('filteroperator' + num, 0))
                if not filters.get(field):
                    filters[field] = list()
                filters[field].append(dict(value=value, condition=condition, operator=op))
        return filters

    def filter(self, qs: QuerySet) -> QuerySet:
        filters = self.read_request_filters()
        field_types = self.get_field_types() or self.field_types or {}
        if not filters:
            return qs

        q_all = Q()
        q_all.op = 0    # 0 - AND, 1 - OR
        for field in filters:
            field_q = Q()
            for field_condition in filters[field]:

                cond = field_condition['condition']
                val = field_condition['value']
                op = field_condition['operator']    # 0 - AND, 1 - OR

                q_curr = Q()

                # TODO: check if bool/null filter improved in new jqWidgets grid
                # if vale is False filter None and False
                field_type = field_types.get(field, str)
                field_type_name = field_type.__name__ if field_type else ''

                if field_type_name == 'bool_lookup':
                    if cond == 'NOT_EQUAL' and val is True or cond == 'EQUAL' and val is False:
                        q_curr = Q(**{field: False}) | Q(**{'%s__isnull' % field: True})
                    else:
                        q_curr = Q(**{field: True})
                elif cond in self.conditions:
                    # prevent transform EQUAL into _iexact for int/float columns
                    if cond == 'EQUAL' and self.get_db_column_type(qs, field) in self.equal_as_exact_db_types:
                        cond_str = '%s__exact' % field
                    else:
                        cond_str = self.make_condition(field_type_name, field, self.conditions[cond])
                    q_curr = Q(**{cond_str: val})
                elif cond in self.conditions_empty:
                    cond_str = self.make_condition(field_type_name, field, self.conditions_empty[cond][0])
                    val = self.conditions_empty[cond][1]
                    q_curr = Q(**{cond_str: val})
                elif cond in self.conditions_neg:
                    cond_str = self.make_condition(field_type_name, field, self.conditions_neg[cond])
                    q_curr = ~Q(**{cond_str: val})
                # filter out empty and None values as well
                elif cond == 'NOT_EMPTY':
                    q_curr = ~Q(**{field: ''}) & Q(**{'%s__isnull' % field: False})

                field_q = field_q & q_curr if op == 0 else field_q | q_curr
            q_all = q_all & field_q

        qs = qs.filter(q_all)
        return qs

    @staticmethod
    def get_db_column_type(qs, field):
        if field in qs.query.annotations:
            output_field = qs.query.annotations[field].output_field
        else:
            try:
                output_field = qs.model._meta.get_field(field)
            except:
                return
        return output_field.cast_db_type(connection)

    @classmethod
    def make_condition(cls, field_type: str, field: str, cond: str) -> str:
        if field_type != 'str' and cond in cls.string_only_conditions:
            return field
        return f'{field}__{cond}'

    def sort(self, qs):
        # server-side sorting
        sortfield = self.request.GET.get('sortdatafield')
        sortorder = self.request.GET.get('sortorder', 'asc')
        if sortfield:
            sortfield = sortfield.replace('-', '_')
            if sortorder == 'desc':
                qs = qs.order_by('-%s' % sortfield)
            elif sortorder == 'asc':
                qs = qs.order_by(sortfield)
        return qs

    def paginate(self, qs) -> Tuple[Union[List, Any], Paginator]:
        # server-side pagination
        page = self.request.GET.get('pagenum')
        size = self.request.GET.get('pagesize')
        # here we disable query caching because query would return a list
        # for the page, and we will not be able to annotate the list
        qs = QuerySetWoCache.wrap(qs)
        paginator = Paginator(qs, size)
        try:
            pg = paginator.page(int(page) + 1)
        except ValueError:
            # If page is not an integer, deliver first page.
            pg = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            return [], paginator
            # pg = paginator.page(paginator.num_pages)
        qs = pg.object_list
        if hasattr(qs, 'total_records'):
            qs.total_records = pg.paginator.count
        elif isinstance(qs, list):
            raise RuntimeError(f'paginate() arg is {qs.__class__}')
        return qs, paginator

    def get_json_data(self, **kwargs):
        qs = kwargs.get('qs') or self.get_queryset()    # .distinct()
        if 'qs' in kwargs:
            del kwargs['qs']

        enable_pagination = json.loads(self.request.GET.get('enable_pagination', 'null'))
        export_to = self.request.GET.get('export_to')
        qs = self.filter_and_sort(qs)

        if hasattr(self, 'annotate_after_filter'):
            qs = qs.annotate(**self.annotate_after_filter)

        if enable_pagination and not export_to:
            qs, paginator = self.paginate(qs)
            total_records = paginator.count

        else:
            total_records = qs.count()

        if getattr(self, 'deep_processing', True):
            data = super().get_json_data(qs=qs, **kwargs)
        else:
            data = list(qs)

        return {'data': data, 'total_records': total_records}

    @staticmethod
    def date_lookup(value):
        """
        Allows to input date in 'mm-dd-yyyy' format
        """
        try:
            res = datetime.datetime.strptime(value, '%m-%d-%Y').strftime('%Y-%m-%d')
        except ValueError:
            res = value
        return res

    @staticmethod
    def bool_lookup(value):
        rel = {'1': True, 'true': True, 'True': True, 'good': True, 'Good': True,
               '0': False, 'false': False, 'False': False, 'bad': False, 'Bad': False,
               'none': None, 'None': None, 'null': None, 'Null': None}
        ret_value = rel.get(value, '')
        return ret_value

    def full_reverse(self, *args, **kwargs):
        return full_reverse(*args, **kwargs, request=self.request)


class JqPaginatedListView(JqPaginatedListMixin, AjaxListView):
    pass


class SimpleRelationSerializer(rest_framework.serializers.ModelSerializer):
    """
    Serializer that extracts nested relations as char field
    """

    def get_fields(self):
        for field in self.Meta.fields:
            if '__' in field:
                self._declared_fields[field] = rest_framework.serializers.CharField(
                    source='.'.join(field.split('__')),
                    read_only=True)
        return super().get_fields()


class JqFilterBackend(rest_framework.filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, *args):
        jq_view = JqPaginatedListView(request=request)
        if 'sortdatafield' in request.GET or 'filterscount' in request.GET:
            queryset = jq_view.filter_and_sort(queryset)
        enable_pagination = json.loads(request.GET.get('enable_pagination', 'null'))
        if enable_pagination and 'pagenum' in request.GET:
            queryset, _ = jq_view.paginate(queryset)
        return queryset


class ModelFieldFilterBackend(rest_framework.filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, *args):
        for param_name, param_value in request.GET.items():
            try:
                if param_name.endswith('_contains'):
                    param_name = param_name.replace('_contains', '__icontains')
                queryset = queryset.filter(**{param_name: param_value})
            except FieldError:
                continue
        return queryset


class APIResponseMixin:
    response_unifier_serializer = None
    new_instance = None

    def handle_exception(self, exc):
        try:
            return super().handle_exception(exc)
        except Exception as e:
            return Response({'status': 'error',
                             'reason': str(e),
                             'traceback': traceback.format_exc()})

    def destroy(self, request, *args, **kwargs):
        _ = super().destroy(request, *args, **kwargs)
        return Response('OK', status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        self.new_instance = serializer.save()

    def finalize_response(self, request, response, *args, **kwargs):
        if self.response_unifier_serializer and \
                str(response.status_code)[0] not in ('4', '5') and \
                self.get_serializer_class() != self.response_unifier_serializer:
            try:
                if self.new_instance:
                    instance = self.new_instance
                else:
                    instance = self.get_object()
                response.data = self.response_unifier_serializer(instance, many=False).data
            except:
                pass
        return super().finalize_response(request, response, *args, **kwargs)


class APIFormFieldsMixin:
    """
    Mixin to provide info about instance or model fields defined in "options_serializer",
    delivers data like field type, name, choices and other attributes listed in default_field_attrs.
    Provides unified UI field type like input/select/checkbox, see "ui_elements_map".

    """
    default_field_attrs = ['field_name', 'label', 'help_text', 'required',
                           'choices', 'read_only', 'allow_null']
    options_serializer = None
    ui_elements_map = {
        "UUIDField": {'type': None, 'data_type': 'uid'},
        "JSONField": {'type': 'input', 'data_type': 'json'},
        "CharField": {'type': 'input', 'data_type': 'string'},
        "ManyRelatedField": {'type': 'select', 'multichoice': True, 'data_type': 'array'},
        "ChoiceField": {'type': 'select', 'multichoice': False, 'data_type': 'string'},
        "PrimaryKeyRelatedField": {'type': 'select', 'multichoice': False, 'data_type': 'id'},
        "DateField": {'type': 'input', 'data_type': 'date'},
        "DateTimeField": {'type': 'input', 'data_type': 'datetime'},
        "BooleanField": {'type': 'checkbox', 'data_type': 'boolean'},
        "IntegerField": {'type': 'input', 'data_type': 'integer'},
    }
    default_ui_element = {'type': 'input', 'data_type': 'string'}
    complex_ui_element = {'type': 'complex', 'data_type': 'array'}
    optional_ui_attrs = ('max_length', 'max_value', 'min_value')
    default_always_null_fields = ('UUIDField',)

    def get_ui_element(self, field_code, field_class):
        field_class_name = field_class.__class__.__name__
        if "Serializer" in field_class_name:
            ui_element_data = dict(self.complex_ui_element)
        else:
            ui_element_data = dict(self.ui_elements_map.get(
                field_class_name, self.default_ui_element))
            for ui_attr in self.optional_ui_attrs:
                if hasattr(field_class, ui_attr):
                    ui_element_data[ui_attr] = getattr(field_class, ui_attr)
        return ui_element_data

    def get_fields_data(self):
        fields = OrderedDict()
        serializer_class = self.options_serializer or self.get_serializer_class()
        try:
            instance = self.get_object()
        except:
            instance = None
        serializer = serializer_class(instance)
        model = serializer.Meta.model

        for field_code, field_class in serializer.get_fields().items():
            field_type = field_class.__class__.__name__
            fields[field_code] = {'field_type': field_type,
                                  'ui_element': self.get_ui_element(field_code, field_class)}
            for field_attr_name in self.default_field_attrs:
                field_attr_value = getattr(field_class, field_attr_name, None)
                if callable(field_attr_value):
                    if field_attr_value == EMPTY:
                        field_attr_value = ''
                    else:
                        try:
                            # try to get value from callable, without args/kwargs
                            field_attr_value = field_attr_value()
                        except:
                            field_attr_value = str(field_attr_value)
                fields[field_code][field_attr_name] = field_attr_value
            # set default values from a model data
            fields[field_code]['default'] = None
            if field_type not in self.default_always_null_fields:
                try:
                    default_value = model._meta.get_field(field_code).default
                    if default_value != NOT_PROVIDED:
                        if callable(default_value):
                            default_value = default_value()
                        try:
                            json.dumps(default_value)
                        except:
                            default_value = str(default_value)
                        fields[field_code]['default'] = default_value
                except:
                    pass

        if instance:
            instance_data = serializer_class(instance, many=False).data
            for field_name, field_data in fields.items():
                field_data['value'] = instance_data.get(field_name)

        return fields

    @action(detail=False, methods=['get'], url_path='form-fields')
    def new_object_fields(self, request, *args, **kwargs):
        """
        GET model form fields description to build UI form for an object:\n
             - field_type: str - CharField, IntegerField, SomeSerializerField - i.e. fields from a serializer
             - ui_element: dict - {type: ("input" | "select" | "checkbox" | ...), data_type: ("string", "integer", "date", ...), ...}
             - label: str - field label declared in a serializer field (default NULL)
             - field_name: str - field name declared in a serializer field (default NULL)
             - help_text: str - field help text declared in a serializer field (default NULL)
             - required: bool - whether field is required
             - read_only: bool - whether field is read only
             - allow_null: bool - whether field is may be null
             - default: bool - default (initial) field value for a new object (default NULL)
             - choices: array - choices to select from [{choice_id1: choice_verbose_name1, ....}] (default NULL)
        """
        return Response(self.get_fields_data())

    @action(detail=True, methods=['get'], url_path='form-fields')
    def existing_object_fields(self, request, *args, **kwargs):
        """
        GET model form fields description to build UI form for EXISTING object:\n
             - value: any - object field value
             - field_type: str - CharField, IntegerField, SomeSerializerField - i.e. fields from a serializer
             - ui_element: dict - {type: ("input" | "select" | "checkbox" | ...), data_type: ("string", "integer", "date", ...), ...}
             - label: str - field label declared in a serializer field (default NULL)
             - field_name: str - field name declared in a serializer field (default NULL)
             - help_text: str - field help text declared in a serializer field (default NULL)
             - required: bool - whether field is required
             - read_only: bool - whether field is read only
             - allow_null: bool - whether field is may be null
             - default: bool - default (initial) field value for a new object (default NULL)
             - choices: array - choices to select from [{choice_id1: choice_verbose_name1, ....}] (default NULL)
        """
        return Response(self.get_fields_data())


class JqListAPIMixin(JqPaginatedListMixin):
    """
    Filter, sort and paginate queryset using jqWidgets' grid GET params
    return {'data': [.....], 'total_records': N}
    """
    extra_data = None

    def filter_queryset(self, queryset):
        if 'sortdatafield' in self.request.GET or 'filterscount' in self.request.GET:
            queryset = self.filter_and_sort(queryset)
        return queryset

    def paginate_queryset(self, queryset):
        enable_pagination = json.loads(self.request.GET.get('enable_pagination', 'null'))
        if enable_pagination and 'pagenum' in self.request.GET:
            queryset, _ = self.paginate(queryset)
        return queryset

    def list(self, request, *args, **kwargs):
        # 1. get full queryset
        queryset = self.get_queryset()
        # 2. filter and sort
        queryset = self.filter_queryset(queryset)
        # 2.1 export in xlsx if needed
        if request.GET.get('export_to') in ['csv', 'xlsx', 'pdf']:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

            if 'columns' in request.GET:
                columns = request.GET['columns'].split(',')
                data = [{k: v for k, v in i.items() if k in columns} for i in data]
            return self.export(data,
                               source_name=self.get_export_file_name() or
                                           queryset.model.__name__.lower(),
                               fmt=request.GET.get('export_to'))
        # 3. count total records !before queryset paginated
        # try:
        #     total_records = queryset.count()
        # except:
        #     total_records = len(queryset)
        # 4. get extra data !before queryset paginated
        extra_data = self.get_extra_data(queryset)
        # 5. paginate
        queryset = self.paginate_queryset(queryset)
        # 6. serialize
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        if isinstance(data, GeneratorType):
            data = list(data)
        # 6.1 filter "columns"
        if 'columns' in request.GET:
            columns = request.GET['columns'].split(',')
            data = [{k: v for k, v in i.items() if k in columns} for i in data]
        # 7. compose returned data
        show_total_records = json.loads(self.request.GET.get('total_records', 'false'))
        if show_total_records:
            # first try to use paginator to get total records
            total_records = getattr(queryset, 'total_records', None)
            if total_records is None:
                total_records = len(data)
            ret = {'data': data,
                   'total_records': total_records}
            if extra_data:
                ret.update(extra_data)
            return rest_framework.response.Response(ret)
        return rest_framework.response.Response(data)

    def get_extra_data(self, queryset):
        return self.extra_data or {}

    def export(self, data, source_name, fmt='xlsx'):
        # if generator, then export to csv using StreamingResponse
        if isinstance(data, GeneratorType):
            resp = StreamingHttpResponse(
                csv_gen_from_dicts(data),
                content_type='text/csv')
            resp['Content-Disposition'] = 'attachment; filename="export.csv"'
            return resp
        data = pd.DataFrame(data).fillna('')
        data = self.process_export_data(data)
        return download(data, fmt, file_name=source_name)

    def get_export_file_name(self):
        pass

    def process_export_data(self, data):
        return data


class JqListAPIView(JqListAPIMixin, rest_framework.generics.ListAPIView):
    """
    Filter, sort and paginate queryset using jqWidgets' grid GET params
    """
    pass


class TypeaheadAPIView(ReviewerQSMixin, rest_framework.generics.ListAPIView):

    def get(self, request, *args, **kwargs):
        field_name = self.kwargs.get('field_name')
        try:
            _ = self.model._meta.get_field(field_name)
        except:
            raise RuntimeError('Wrong field name "{}" for model "{}"'.format(
                field_name, self.model.__name__))
        qs = self.model.objects.all()
        if "q" in request.GET:
            search_key = '%s__icontains' % field_name
            qs = qs.filter(**{search_key: request.GET.get("q")})\
                .order_by(field_name).distinct(field_name)
        return JsonResponse(self.qs_to_values(qs, field_name), encoder=ImprovedDjangoJSONEncoder, safe=False)

    def qs_to_values(self, qs, field_name):
        return [{"value": i} for i in qs.values_list(field_name, flat=True)]


class NestedKeyTextTransform(KeyTextTransform):
    """
    Create annotation for nested json fields.
    F.e. for field like "metadata__level1__level2":
    >>> NestedKeyTextTransform(['level1', 'level2'], 'metadata')
    >>> NestedKeyTextTransform(['level1', 'level2'], 'metadata', output_field=FloatField())
    """
    def __init__(self, nested_key_names, *args, **kwargs):
        super().__init__(nested_key_names, *args, **kwargs)
        self.nested_key_names = nested_key_names
        self.nested_operator = '#>>'
        self._output_field = kwargs.get('output_field') or self._output_field

    def as_sql(self, compiler, connection):
        """
        Postgres specific way to cast data type!
        f.e. see django/db/models/functions/base.py:Cast
        """
        lhs, params = compiler.compile(self.lhs)
        return "(%s %s %%s)::%s" % (lhs, self.nested_operator,
                                    self._output_field.db_type(connection)),\
               [self.nested_key_names] + list(params)


class APIActionMixin:
    """
    Mixin class to track user activity in Action model
    """
    user_action_methods = dict(
        POST='create',
        PUT='update',
        PATCH='update',
        GET='detail',
        DELETE='delete',
    )
    user_action = None

    def dispatch(self, request, *args, **kwargs):
        request.needs_action_logging = getattr(request, 'needs_action_logging', (request.method != 'GET'))
        response = super().dispatch(request, *args, **kwargs)
        if not request.needs_action_logging:
            return response

        if not request.user or not request.user.is_authenticated:
            return response

        user_action_name = self.get_action_name() or self.user_action_methods.get(request.method)\
                           or 'unknown'

        user_action_object_pk = user_action_object = None
        if 'pk' in self.kwargs:
            # need this to get rid of extra sql in elif
            user_action_object_pk = self.kwargs['pk']
            user_action_object_pk = None \
                if str(user_action_object_pk).lower() == 'null' else user_action_object_pk
        elif (self.lookup_url_kwarg or self.lookup_field) in self.kwargs:
            user_action_object = self.get_object()
        else:
            if request.method == 'GET':
                user_action_name = 'list'
        model = self.queryset.model
        content_type = ContentType.objects.get_for_model(model)
        user_action = Action(
            user=request.user,
            name=user_action_name,
            # content_type=content_type
        )
        if user_action_object_pk:
            user_action.object_pk = user_action_object_pk
        else:
            user_action.object = user_action_object
        # this should be added after all otherwise it throws error object has no content type
        user_action.content_type = content_type
        user_action.save()
        self.user_action = user_action
        return response

    def perform_create(self, serializer):
        obj = serializer.save()
        if self.user_action is not None:
            self.user_action.object = obj
            self.user_action.save()
        return obj

    def get_action_name(self):
        """
        Helper to define custom action name
        """
        pass


class APILoggingMixin(LoggingMixin):
    def should_log(self, request, response):
        """
        Log only if enable logging via AppVar
        """
        # do not log FileResponse and other possible large responses
        if isinstance(response, StreamingHttpResponse):
            return False
        from apps.common.app_vars import TRACK_API
        return TRACK_API.val

    def handle_log(self):
        """
        Try to check if response time limit is enabled
        """
        from apps.common.app_vars import TRACK_API_GREATER_THAN
        if self.log['response_ms'] <= TRACK_API_GREATER_THAN.val:
            return
        from apps.common.app_vars import TRACK_API_SAVE_SQL_LOG
        if TRACK_API_SAVE_SQL_LOG.val:
            self.log['sql_log'] = '\n'.join(['({}) {}'.format(
                q.get('time') or q.get('duration', 0) / 1000, q.get('sql') or '')
                for q in connection.queries])
        CustomAPIRequestLog(**self.log).save()


class CustomCountQuerySet(QuerySet):
    @staticmethod
    def wrap(qs: QuerySet):
        qs.__class__ = CustomCountQuerySet
        return qs

    def __init__(self, model=None, query=None, using=None, hints=None):
        super().__init__(model=model, query=query, using=using, hints=hints)
        self.optional_count_query = None  # type: Optional[str]

    def set_optional_count_query(self, query: Optional[str] = None):
        self.optional_count_query = query

    # TODO: delete this
    def count(self):
        """
        Unlike base "count" this one limits count
        by "limit" parameter in query
        """
        if hasattr(self, 'optional_count_query') and self.optional_count_query:
            return self.get_count_custom_sql()
        return super().count()

    def get_count_custom_sql(self):
        """
        Perform a COUNT() query using custom SQL
        """
        #if self._result_cache is not None:
        #    return len(self._result_cache)

        with connection.cursor() as cursor:
            cursor.execute(self.optional_count_query)
            row = cursor.fetchone()
        return row[0]


# TODO: commented out - check how views work without it (not sure why this code was added)
# from django.db.models.expressions import OrderBy, Random, RawSQL, Ref
# from django.db.models.sql.constants import ORDER_DIR
# from django.db.models.sql.query import get_order_dir
# from django.db.utils import DatabaseError


# def get_group_by(self, select, order_by):
#     """
#     See original get_group_by at django.db.models.sql.compiler>SQLCompiler
#     """
#     if self.query.group_by is None:
#         return []
#     expressions = []
#     if self.query.group_by is not True:
#         for expr in self.query.group_by:
#             if not hasattr(expr, 'as_sql'):
#                 expressions.append(self.query.resolve_ref(expr))
#             else:
#                 expressions.append(expr)
#     for expr, _, _ in select:
#         cols = expr.get_group_by_cols()
#         for col in cols:
#             expressions.append(col)
#     for expr, (sql, params, is_ref) in order_by:
#         if expr.contains_aggregate:
#             continue
#         if is_ref:
#             continue
#         expressions.extend(expr.get_source_expressions())
#     having_group_by = self.having.get_group_by_cols() if self.having else ()
#     for expr in having_group_by:
#         expressions.append(expr)
#     result = []
#     # changed from set() to []
#     seen = []
#     expressions = self.collapse_group_by(expressions, having_group_by)
#
#     for expr in expressions:
#         sql, params = self.compile(expr)
#         if (sql, tuple(params)) not in seen:
#             result.append((sql, params))
#             # changed from add to append
#             seen.append((sql, tuple(params)))
#     return result
#
#
# def get_order_by(self):
#     """
#     See original get_group_by at django.db.models.sql.compiler>SQLCompiler
#     """
#     if self.query.extra_order_by:
#         ordering = self.query.extra_order_by
#     elif not self.query.default_ordering:
#         ordering = self.query.order_by
#     else:
#         ordering = (self.query.order_by or self.query.get_meta().ordering or [])
#     if self.query.standard_ordering:
#         asc, desc = ORDER_DIR['ASC']
#     else:
#         asc, desc = ORDER_DIR['DESC']
#
#     order_by = []
#     for field in ordering:
#         if hasattr(field, 'resolve_expression'):
#             if not isinstance(field, OrderBy):
#                 field = field.asc()
#             if not self.query.standard_ordering:
#                 field.reverse_ordering()
#             order_by.append((field, False))
#             continue
#         if field == '?':  # random
#             order_by.append((OrderBy(Random()), False))
#             continue
#
#         col, order = get_order_dir(field, asc)
#         descending = True if order == 'DESC' else False
#
#         if col in self.query.annotation_select:
#             # Reference to expression in SELECT clause
#             order_by.append((
#                 OrderBy(Ref(col, self.query.annotation_select[col]), descending=descending),
#                 True))
#             continue
#         if col in self.query.annotations:
#             # References to an expression which is masked out of the SELECT clause
#             order_by.append((
#                 OrderBy(self.query.annotations[col], descending=descending),
#                 False))
#             continue
#
#         if '.' in field:
#             # This came in through an extra(order_by=...) addition. Pass it
#             # on verbatim.
#             table, col = col.split('.', 1)
#             order_by.append((
#                 OrderBy(
#                     RawSQL('%s.%s' % (self.quote_name_unless_alias(table), col), []),
#                     descending=descending
#                 ), False))
#             continue
#
#         if not self.query._extra or col not in self.query._extra:
#             # 'col' is of the form 'field' or 'field1__field2' or
#             # '-field1__field2__field', etc.
#             order_by.extend(self.find_ordering_name(
#                 field, self.query.get_meta(), default_order=asc))
#         else:
#             if col not in self.query.extra_select:
#                 order_by.append((
#                     OrderBy(RawSQL(*self.query.extra[col]), descending=descending),
#                     False))
#             else:
#                 order_by.append((
#                     OrderBy(Ref(col, RawSQL(*self.query.extra[col])), descending=descending),
#                     True))
#     result = []
#     # changed from set() to []
#     seen = []
#
#     for expr, is_ref in order_by:
#         if self.query.combinator:
#             src = expr.get_source_expressions()[0]
#             # Relabel order by columns to raw numbers if this is a combined
#             # query; necessary since the columns can't be referenced by the
#             # fully qualified name and the simple column names may collide.
#             for idx, (sel_expr, _, col_alias) in enumerate(self.select):
#                 if is_ref and col_alias == src.refs:
#                     src = src.source
#                 elif col_alias:
#                     continue
#                 if src == sel_expr:
#                     expr.set_source_expressions([RawSQL('%d' % (idx + 1), ())])
#                     break
#             else:
#                 raise DatabaseError('ORDER BY term does not match any column in the result set.')
#         resolved = expr.resolve_expression(
#             self.query, allow_joins=True, reuse=None)
#         sql, params = self.compile(resolved)
#         # Don't add the same column twice, but the order direction is
#         # not taken into account so we strip it. When this entire method
#         # is refactored into expressions, then we can check each part as we
#         # generate it.
#         without_ordering = self.ordering_parts.search(sql).group(1)
#         if (without_ordering, tuple(params)) in seen:
#             continue
#         # changed from add to append
#         seen.append((without_ordering, tuple(params)))
#         result.append((resolved, (sql, params, is_ref)))
#     return result


# from django.db.models.sql.compiler import SQLCompiler
# SQLCompiler.get_group_by = get_group_by
# SQLCompiler.get_order_by = get_order_by
