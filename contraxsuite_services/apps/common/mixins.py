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
from functools import reduce

# Third-party imports
from rest_framework import serializers
from rest_framework.filters import BaseFilterBackend
from rest_framework.generics import ListAPIView

# Django imports
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import FieldError
from django.core.paginator import Paginator, EmptyPage
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.db.models import Q, fields as django_fields
from django.http import JsonResponse
from django.views.generic import ListView
from django.views.generic.base import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import MultipleObjectMixin

# Project imports
from apps.common.utils import cap_words, export_qs_to_file

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.8/LICENSE"
__version__ = "1.0.8"
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


class MessageMixin(object):
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


class TemplateNamesMixin(object):
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


class CustomListView(ReviewerQSMixin, BaseCustomListView):
    pass


class CustomDeleteView(AddModelNameMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'base_delete.html'
    raise_exception = True

    def handle_no_permission(self):
        if self.request.is_ajax():
            data = {'message': 'Permission denied.', 'level': 'error'}
            return JsonResponse(data, encoder=DjangoJSONEncoder, safe=False)
        return super().handle_no_permission()

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            return JsonResponse(str(self.get_object()), encoder=DjangoJSONEncoder, safe=False)
        return super().get(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        msg = base_success_msg % (
            cap_words(obj._meta.verbose_name),
            obj.__str__(), 'deleted')
        if request.is_ajax():
            obj.delete()
            data = {'message': msg, 'level': 'success'}
            return JsonResponse(data, encoder=DjangoJSONEncoder, safe=False)
        messages.success(request, msg)
        return super().post(request, *args, **kwargs)


class AjaxResponseMixin(object):

    def render_to_response(self, *args, **kwargs):
        if self.request.is_ajax():
            data = self.get_json_data(**kwargs)
            return JsonResponse(data, encoder=DjangoJSONEncoder, safe=False)
        return super().render_to_response(*args, **kwargs)


class JSONResponseView(View):

    def response(self, request, *args, **kwargs):
        data = self.get_json_data(request, *args, **kwargs)
        return JsonResponse(data, encoder=DjangoJSONEncoder, safe=False)

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

    def get_json_data(self, request, *args, **kwargs):
        qs = self.model.objects.all()
        if "q" in request.GET:
            search_key = '%s__icontains' % self.search_field
            qs = qs.filter(**{search_key: request.GET.get("q")})\
                .order_by(self.search_field).distinct(self.search_field)
        return self.qs_to_values(qs)

    def qs_to_values(self, qs):
        return [{"value": i} for i in qs.values_list(self.search_field, flat=True)]


class SubmitView(JSONResponseView):
    error_message = 'Error'
    success_message = 'Success'

    def response(self, request, *args, **kwargs):
        try:
            data = self.process(request)
        except:
            data = self.failure()
        return JsonResponse(data, encoder=DjangoJSONEncoder, safe=False)

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
        if 'export' in self.request.GET:
            return export_qs_to_file(
                request, qs=self.get_queryset(), **self.export_params)
        if not request.is_ajax():
            self.object_list = []
            context = self.get_context_data()
            return self.render_to_response(context)
        return self.render_to_response()

    def get_json_data(self, **kwargs):
        qs = kwargs.get('qs')
        if qs is None:
            qs = self.get_queryset()
        extra_json_fields = list(self.extra_json_fields)
        extra_json_fields.append('pk')
        extra_json_fields += list(self.annotate.keys())
        if not self.json_fields:
            self.json_fields = [f.name for f in self.model._meta.concrete_fields]
        data = list(qs.annotate(**self.annotate)
                    .values(*(self.json_fields + extra_json_fields)))

        # TODO: consider replace none_to_bool - either use default=False or update jqWidgets
        bool_fields = [i.name for i in self.model._meta.fields
                       if isinstance(i, django_fields.BooleanField)]
        for row in data:
            row.update((k, False) for k, v in row.items() if v is None and k in bool_fields)
            if not kwargs.get('keep_tags'):
                row.update((k, v.replace("<", "&lt;").replace(">", "&gt;"))
                           for k, v in row.items() if isinstance(v, str))

        return data


class JqPaginatedListView(AjaxListView):
    conditions = dict(EQUAL='exact',
                      EQUAL_CASE_SENSITIVE='iexact',
                      CONTAINS='contains',
                      CONTAINS_CASE_SENSITIVE='icontains',
                      LESS_THAN='lt',
                      LESS_THAN_OR_EQUAL='lte',
                      GREATER_THAN='gt',
                      GREATER_THAN_OR_EQUAL='gte',
                      STARTS_WITH='startswith',
                      ENDS_WITH='endswith',
                      STARTS_WITH_CASE_SENSITIVE='istartswith',
                      ENDS_WITH_CASE_SENSITIVE='iendswith')
    conditions_empty = dict(EMPTY=('exact', ''),
                            NULL=('isnull', True),
                            NOT_NULL=('isnull', False))
    conditions_neg = dict(DOES_NOT_CONTAIN='contains',
                          DOES_NOT_CONTAIN_CASE_SENSITIVE='icontains',
                          NOT_EQUAL='exact')
    field_types = dict()
    unique_field = 'pk'

    def get_field_types(self):
        return self.field_types

    def filter_and_sort(self, qs):
        """
        Filter and sort data on server side.
        """
        sortfield = self.request.GET.get('sortdatafield')
        sortorder = self.request.GET.get('sortorder')
        filterscount = int(self.request.GET.get('filterscount'))

        # server-side filtering
        if filterscount:
            filters = dict()
            for filter_num in range(filterscount):
                num = str(filter_num)
                field = self.request.GET.get('filterdatafield' + num)
                value = (self.get_field_types() or self.field_types).get(field, str)(
                    self.request.GET.get('filtervalue' + num))
                condition = self.request.GET.get('filtercondition' + num)
                op = int(self.request.GET.get('filteroperator' + num))
                if not filters.get(field):
                    filters[field] = list()
                filters[field].append(
                    dict(value=value, condition=condition, operator=op)
                )
            for field in filters:
                q_prev = q_curr = Q()
                op = None
                for field_condition in filters[field]:
                    cond = field_condition['condition']
                    val = field_condition['value']
                    op = field_condition['operator']

                    # TODO: check if bool/null filter improved in new jqWidgets grid
                    # if vale is False filter None and False
                    if (self.get_field_types() or
                            self.field_types).get(field, str).__name__ == 'bool_lookup':
                        if cond == 'NOT_EQUAL' and val is True or cond == 'EQUAL' and val is False:
                            q_curr = Q(**{field: False}) | Q(**{'%s__isnull' % field: True})
                        else:
                            q_curr = Q(**{field: True})
                    elif cond in self.conditions:
                        cond_str = '%s__%s' % (field, self.conditions[cond])
                        q_curr = Q(**{cond_str: val})
                    elif cond in self.conditions_empty:
                        cond_str = '%s__%s' % (field, self.conditions_empty[cond][0])
                        val = self.conditions_empty[cond][1]
                        q_curr = Q(**{cond_str: val})
                    elif cond in self.conditions_neg:
                        cond_str = '%s__%s' % (field, self.conditions_neg[cond])
                        q_curr = ~Q(**{cond_str: val})
                    # filter out empty and None values as well
                    elif cond == 'NOT_EMPTY':
                        q_curr = ~Q(**{field: ''}) & Q(**{'%s__isnull' % field: False})
                    # one field can have 2 conditions maximum
                    if not q_prev:
                        q_prev = q_curr
                        q_curr = Q()
                qs = qs.filter(q_prev | q_curr) if op else qs.filter(q_prev & q_curr)

        # server-side sorting
        if sortfield:
            if sortorder == 'desc':
                qs = qs.order_by('-%s' % sortfield)
            elif sortorder == 'asc':
                qs = qs.order_by(sortfield)

        return qs

    def paginate(self, qs):
        # server-side pagination
        page = self.request.GET.get('pagenum')
        size = self.request.GET.get('pagesize')
        paginator = Paginator(qs, size)
        try:
            pg = paginator.page(int(page) + 1)
        except ValueError:
            # If page is not an integer, deliver first page.
            pg = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            pg = paginator.page(paginator.num_pages)

        qs = qs.filter(
            **{'%s__in' % self.unique_field: [getattr(obj, self.unique_field)
                                              for obj in pg.object_list]})
        return qs

    def get_json_data(self, **kwargs):
        data = []
        qs = self.get_queryset()    # .distinct()
        total_records = qs.count()
        enable_pagination = json.loads(self.request.GET.get('enable_pagination', 'null'))
        if not enable_pagination:
            data = super().get_json_data(qs=qs, **kwargs)
        elif qs.exists():
            qs = self.filter_and_sort(qs)
            total_records = qs.count()
            qs = self.paginate(qs)
            data = super().get_json_data(qs=qs, **kwargs)
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


class SimpleRelationSerializer(serializers.ModelSerializer):
    """
    Serializer that extracts nested relations as char field
    """

    def get_fields(self):
        for field in self.Meta.fields:
            if '__' in field:
                self._declared_fields[field] = serializers.CharField(
                    source='.'.join(field.split('__')),
                    read_only=True)
        return super().get_fields()


class JqFilterBackend(BaseFilterBackend):

    def filter_queryset(self, request, queryset, *args):
        jq_view = JqPaginatedListView(request=request)
        if 'enable_pagination' in request.GET and 'pagenum' in request.GET:
            queryset = jq_view.paginate(queryset)
        if 'sortdatafield' in request.GET or 'filterscount' in request.GET:
            queryset = jq_view.filter_and_sort(queryset)
        return queryset


class ModelFieldFilterBackend(BaseFilterBackend):

    def filter_queryset(self, request, queryset, *args):
        for param_name, param_value in request.GET.items():
            try:
                if param_name.endswith('_contains'):
                    param_name = param_name.replace('_contains', '__icontains')
                queryset = queryset.filter(**{param_name: param_value})
            except FieldError:
                continue
        return queryset


class JqListAPIView(ListAPIView):
    """
    Filter, sort and paginate queryset using jqWidgets' grid GET params
    """
    filter_backends = [JqFilterBackend, ModelFieldFilterBackend]


class JqMixin(object):
    """
    Filter, sort and paginate queryset using jqWidgets' grid GET params
    Filter using model's field name as query param
    """
    filter_backends = [JqFilterBackend, ModelFieldFilterBackend]


class TypeaheadAPIView(ReviewerQSMixin, ListAPIView):

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
        return JsonResponse(self.qs_to_values(qs, field_name), encoder=DjangoJSONEncoder, safe=False)

    def qs_to_values(self, qs, field_name):
        return [{"value": i} for i in qs.values_list(field_name, flat=True)]
