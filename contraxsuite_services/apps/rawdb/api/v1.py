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

import time
from collections import defaultdict
from typing import Dict, List, Set

import rest_framework.views
from django.conf.urls import url
from django.db import transaction
from django.db.models import Q, F
from django.http import StreamingHttpResponse
from rest_framework.response import Response
from django.http import HttpResponse

import apps.common.mixins
from apps.common.errors import APIRequestError
from apps.common.streaming_utils import csv_gen, GeneratorList
from apps.common.url_utils import as_bool, as_int, as_int_list, as_str_list
from apps.document.models import Document, DocumentType
from apps.project.models import Project
from apps.rawdb.constants import FT_COMMON_FILTER, FT_USER_DOC_GRID_CONFIG, FIELD_CODES_SHOW_BY_DEFAULT_NON_GENERIC, \
    FIELD_CODES_SHOW_BY_DEFAULT_GENERIC, FIELD_CODES_HIDE_FROM_CONFIG_API, FIELD_CODE_ANNOTATION_SUFFIX
from apps.rawdb.field_value_tables import get_columns, get_annotation_columns, \
    query_documents, DocumentQueryResults
from apps.rawdb.models import SavedFilter
from apps.rawdb.rawdb.query_parsing import parse_order_by
from apps.rawdb.rawdb.rawdb_field_handlers import ColumnDesc

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def _column_to_dto(column: ColumnDesc, add_query_syntax: bool = False) -> Dict:
    res = {
        'column': column.name,
        'title': column.title,
        'type': column.value_type.value,
    }
    if add_query_syntax:
        res['query_syntax'] = column.get_field_filter_syntax_hint()
    return res


def _document_type_schema_to_dto(document_type: DocumentType, columns: List[ColumnDesc], default_columns: Set[str],
                                 add_query_syntax: bool = False) -> Dict:
    document_type_data = {
        'code': document_type.code,
        'title': document_type.title,
        'columns': [_column_to_dto(column, add_query_syntax) for column in columns],
        'default_columns': default_columns
    }

    return document_type_data


def _query_results_to_json(query_results: DocumentQueryResults, exec_time: float) -> Response:
    res = {
        'offset': query_results.offset,
        'limit': query_results.limit,
        'total_documents': query_results.total,
        'reviewed_documents': query_results.reviewed,
        'items': GeneratorList(query_results.fetch_dicts()),
        'time': exec_time
    }
    return Response({k: v for k, v in res.items() if v is not None})


def _query_results_to_xlsx(query_results: DocumentQueryResults) -> HttpResponse:
    from openpyxl import Workbook
    from openpyxl.writer.excel import save_virtual_workbook
    from openpyxl.styles import Font, Alignment

    wb = Workbook()
    ws = wb.active
    ws.append(query_results.column_titles)
    for cells in ws.rows:
        for cell in cells:
            cell.font = Font(name=cell.font.name, bold=True)
            cell.alignment = Alignment(horizontal='center')
        break

    for row in query_results.fetch():
        ws.append(row)

    def str_len(value):
        return len(str(value)) if value is not None else 0

    for column_cells in ws.columns:
        length = min(max(str_len(cell.value) for cell in column_cells), 100) + 1
        ws.column_dimensions[column_cells[0].column_letter].width = length

    response = HttpResponse(save_virtual_workbook(wb),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=export.xlsx'
    return response


def _query_results_to_csv(query_results: DocumentQueryResults) -> StreamingHttpResponse:
    resp = StreamingHttpResponse(
        csv_gen(query_results.column_codes, query_results.fetch(), query_results.column_titles),
        content_type='text/csv')
    resp['Content-Disposition'] = 'attachment; filename="export.csv"'
    return resp


class RawDBConfigAPIView(apps.common.mixins.APILoggingMixin, rest_framework.views.APIView):
    def get(self, request, *args, **kwargs):
        start = time.time()
        add_query_syntax = as_bool(request.GET, 'add_query_syntax', False)

        document_type_schema = dict()
        for document_type in DocumentType.objects.all():
            columns = get_columns(document_type,
                                  include_generic=document_type.is_generic())  # type: List[ColumnDesc]
            columns = [c for c in columns if c.field_code not in FIELD_CODES_HIDE_FROM_CONFIG_API]

            system_fields = FIELD_CODES_SHOW_BY_DEFAULT_GENERIC \
                if document_type.is_generic() else FIELD_CODES_SHOW_BY_DEFAULT_NON_GENERIC
            search_fields = set(document_type.search_fields.all().values_list('code', flat=True))

            default_columns = {c.name for c in columns
                               if c.field_code not in FIELD_CODES_HIDE_FROM_CONFIG_API and
                               (c.field_code in system_fields or c.field_code in search_fields)}

            document_type_schema[document_type.code] = _document_type_schema_to_dto(document_type,
                                                                                    columns,
                                                                                    default_columns,
                                                                                    add_query_syntax)

        common_filters_by_document_type = defaultdict(list)  # type: Dict[List]

        for document_type_code, filter_id, title, display_order in SavedFilter.objects \
                .filter(project_id__isnull=True, filter_type=FT_COMMON_FILTER) \
                .filter(Q(user__isnull=True) | Q(user=request.user)) \
                .values_list('document_type__code', 'id', 'title', 'display_order'):
            common_filters_by_document_type[document_type_code].append({
                'id': filter_id,
                'title': title,
                'display_order': display_order
            })

        common_filters_by_project = defaultdict(list)  # type: Dict[List]

        for project_id, filter_id, title, display_order in SavedFilter.objects \
                .filter(project_id__isnull=False, filter_type=FT_COMMON_FILTER) \
                .filter(Q(user__isnull=True) | Q(user=request.user)) \
                .values_list('project_id', 'id', 'title', 'display_order'):
            common_filters_by_project[project_id].append({
                'id': filter_id,
                'title': title,
                'display_order': display_order
            })

        user_doc_grid_configs_by_project = defaultdict(list)  # type: Dict[List]

        for project_id, columns, column_filters, order_by in SavedFilter.objects \
                .filter(user=request.user, project_id__isnull=False, filter_type=FT_USER_DOC_GRID_CONFIG) \
                .filter(document_type_id=F('project__type_id')) \
                .order_by('pk') \
                .values_list('project_id', 'columns', 'column_filters', 'order_by'):
            user_doc_grid_configs_by_project[project_id] = {
                'columns': columns,
                'column_filters': column_filters,
                'order_by': order_by
            }

        return Response({
            'document_type_schema': document_type_schema,
            'common_filters_by_document_type': common_filters_by_document_type,
            'common_filters_by_project': common_filters_by_project,
            'user_doc_grid_configs_by_project': user_doc_grid_configs_by_project,
            'time': time.time() - start
        })


class DocumentsAPIView(rest_framework.views.APIView):
    URL_PARAM_PREFIX_FILTER = 'where_'

    MAX_RETURNED_DOCUMENTS_JSON = 200

    FMT_JSON = 'json'
    FMT_CSV = 'csv'
    FMT_XLSX = 'xlsx'

    def get(self, request, document_type_code: str, *_args, **_kwargs):
        start = time.time()
        try:
            document_type = DocumentType.objects.get(code=document_type_code)

            project_ids = as_int_list(request.GET, 'project_ids')  # type: List[int]

            columns = as_str_list(request.GET, 'columns')

            include_annotations = as_bool(request.GET, 'associated_text')
            if include_annotations:
                all_annotation_columns = get_annotation_columns(document_type)
                columns += [i.field_code for i in all_annotation_columns
                            if i.field_code.rstrip(FIELD_CODE_ANNOTATION_SUFFIX) in columns]

            fmt = request.GET.get('fmt') or self.FMT_JSON

            offset = as_int(request.GET, 'offset', None)
            if offset is not None and offset < 0:
                offset = None

            limit = as_int(request.GET, 'limit', None)
            if limit is not None and limit <= 0:
                limit = None

            # For json output we limit number of returned documents because we dont use streaming response for JSON
            # and want to keep it fast.
            if fmt == self.FMT_JSON and self.MAX_RETURNED_DOCUMENTS_JSON is not None \
                    and (limit is None or limit > self.MAX_RETURNED_DOCUMENTS_JSON):
                limit = self.MAX_RETURNED_DOCUMENTS_JSON

            saved_filters = as_int_list(request.GET, 'saved_filters')  # type: List[int]

            column_filters = list()
            for param, value in request.GET.items():  # type: str, str
                if param.startswith(self.URL_PARAM_PREFIX_FILTER):
                    column_filters.append((param[len(self.URL_PARAM_PREFIX_FILTER):], value))

            order_by = request.GET.get('order_by') or None  # type: str
            order_by = parse_order_by(order_by) if order_by else None

            save_filter = as_bool(request.GET, 'save_filter', False)  # type: bool

            return_reviewed = as_bool(request.GET, 'return_reviewed', False)
            return_total = as_bool(request.GET, 'return_total', True)
            return_data = as_bool(request.GET, 'return_data', True)
            ignore_errors = as_bool(request.GET, 'ignore_errors', True)

            if project_ids and save_filter:
                column_filters_dict = {c: f for c, f in column_filters}
                for project_id in project_ids:
                    with transaction.atomic():
                        obj = SavedFilter.objects.create(user=request.user,
                                                         document_type=document_type,
                                                         filter_type=FT_USER_DOC_GRID_CONFIG,
                                                         project_id=project_id,
                                                         columns=columns,
                                                         column_filters=column_filters_dict,
                                                         title=None,
                                                         order_by=[(column, direction.value)
                                                                   for
                                                                   column, direction in
                                                                   order_by] if order_by
                                                         else None
                                                         )
                        SavedFilter.objects.filter(user=request.user,
                                                   document_type=document_type,
                                                   filter_type=FT_USER_DOC_GRID_CONFIG,
                                                   project_id=project_id) \
                            .exclude(pk=obj.pk) \
                            .delete()

            query_results = query_documents(requester=request.user,
                                            document_type=document_type,
                                            project_ids=project_ids,
                                            column_names=columns,
                                            saved_filter_ids=saved_filters,
                                            column_filters=column_filters,
                                            order_by=order_by,
                                            offset=offset,
                                            limit=limit,
                                            return_documents=return_data,
                                            return_reviewed_count=return_reviewed,
                                            return_total_count=return_total,
                                            ignore_errors=ignore_errors,
                                            include_annotation_fields=True)  # type: DocumentQueryResults

            if fmt in {self.FMT_XLSX, self.FMT_CSV} and not return_data:
                raise APIRequestError('Export to csv/xlsx requested with return_data=false')

            if fmt == self.FMT_CSV:
                return _query_results_to_csv(query_results)
            elif fmt == self.FMT_XLSX:
                return _query_results_to_xlsx(query_results)
            else:
                if query_results is None:
                    return Response({'time': time.time() - start})
                return _query_results_to_json(query_results, time.time() - start)
        except APIRequestError as e:
            return e.to_response()
        except Exception as e:
            return APIRequestError(message='Unable to process request', caused_by=e, http_status_code=500).to_response()

    @classmethod
    def simulate_get(cls, user, project, return_ids=True, use_saved_filter=True):
        """
        Re-use DocumentsAPIView and SavedFilter to fetch all filtered project documents
        """
        # TODO: Do not simulate http requests, use query_documents()
        filters = order_by = None

        if isinstance(project, int):
            project = Project.objects.get(pk=project)

        if use_saved_filter:
            try:
                saved_filter = SavedFilter.objects.get(project_id=project.id, user=user)
                filters = saved_filter.column_filters
                order_by = saved_filter.order_by
            except:
                pass

        if order_by is None:
            order_by = [['document_name', 'asc']]

        class FakeRequest:
            def __init__(the_self):
                the_self.user = user
                the_self.GET = {'columns': 'document_id',
                                'project_ids': str(project.id),
                                'order_by': ','.join('{}:{}'.format(field, order) for field, order in order_by),
                                'save_filter': 'false'}
                if filters:
                    for field_name, condition in filters.items():
                        the_self.GET['where_{}'.format(field_name)] = condition

        request = FakeRequest()
        doc_type_code = project.type.code
        view = cls(request=request, format_kwarg=doc_type_code)
        view.MAX_RETURNED_DOCUMENTS_JSON = None
        resp = view.get(request=request, document_type_code=doc_type_code).data['items']
        ids = [i['document_id'] for i in resp]

        if return_ids:
            return ids
        return Document.all_objects.filter(id__in=ids)


class ProjectStatsAPIView(rest_framework.views.APIView):
    def get(self, request, project_id: int, *_args, **_kwargs):
        try:
            start = time.time()
            project = Project.objects.filter(pk=project_id).select_related('type').first()
            if not project:
                return Response({'error': 'Project not found'}, status=404)

            saved_filters = as_int_list(request.GET, 'saved_filters')  # type: List[int]

            query_results = query_documents(requester=request.user,
                                            document_type=project.type,
                                            project_ids=[project.pk],
                                            saved_filter_ids=saved_filters,
                                            return_reviewed_count=True,
                                            return_documents=False,
                                            return_total_count=True,
                                            include_annotation_fields=True)  # type: DocumentQueryResults
            if not query_results:
                return Response({'time': time.time() - start})

            return _query_results_to_json(query_results, time.time() - start)
        except APIRequestError as e:
            return e.to_response()
        except Exception as e:
            return APIRequestError(message='Unable to process request', caused_by=e, http_status_code=500).to_response()


urlpatterns = [
    url(r'documents/(?P<document_type_code>[^/]+)/$', DocumentsAPIView.as_view(), name='documents'),
    url(r'project_stats/(?P<project_id>\d+)/$', ProjectStatsAPIView.as_view(), name='project_stats'),
    url(r'config/$', RawDBConfigAPIView.as_view(), name='config'),
]
