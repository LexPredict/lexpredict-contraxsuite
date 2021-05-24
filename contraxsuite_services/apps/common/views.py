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

# Standard library imports
import json
import re
from tempfile import TemporaryDirectory
import urllib.parse

# Third-party imports
import pandas as pd

# Django imports
from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render

# Project imports
from apps.common import redis
from apps.common.forms import ReindexDBForm, DBSchemaSelectionForm
from apps.common.mixins import JqPaginatedListView, AjaxListView
from apps.common.models import MethodStats
from apps.common.permissions import SuperuserRequiredMixin
from apps.common.tasks import ReindexDB
from apps.task.views import BaseAjaxTaskView

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def test_500_view(request):
    raise RuntimeError('Test 500 error')
    # return


class MethodStatsOverviewListView(SuperuserRequiredMixin, JqPaginatedListView):
    template_name = 'common/method_stats_overview.html'
    model = MethodStats

    def get_json_data(self, **kwargs):
        data = list(self.model.get(as_dataframe=False))
        return {'data': data, 'total_records': len(data)}


class DBStatsView(SuperuserRequiredMixin, AjaxListView):
    template_name = 'common/db_stats.html'
    model = MethodStats  # just to keep AjaxListView behavior

    def get_json_data(self, **kwargs):
        if self.request.GET.get('source') == 'pg_stat_statements':
            return self.get_pg_stat_statements_data()
        if self.request.GET.get('source') == 'pg_stat_activity':
            return self.get_pg_stat_activity_data()
        if self.request.GET.get('columns_table_name'):
            return self.get_table_columns_data()
        if self.request.GET.get('indexes_table_name'):
            return self.get_table_indexes_data()
        return self.get_database_data()

    def get_database_data(self):
        sql = '''
          SELECT *, total_bytes-index_bytes-COALESCE(toast_bytes,0) AS table_bytes FROM (
              SELECT relname AS TABLE_NAME
                      , c.reltuples AS rows
                      , pg_total_relation_size(c.oid) AS total_bytes
                      , pg_indexes_size(c.oid) AS index_bytes
                      , pg_total_relation_size(reltoastrelid) AS toast_bytes
                  FROM pg_class c
                  LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
                  WHERE relkind = 'r'
          ) a;'''

        with connection.cursor() as cursor:
            cursor.execute(sql)
            data = self.dictfetchall(cursor)
            df = pd.DataFrame(data).fillna(0)

            df['table_percent'] = df.apply(lambda row: row.table_bytes / row.total_bytes * 100, axis=1)
            df['index_percent'] = df.apply(lambda row: row.index_bytes / row.total_bytes * 100, axis=1)
            df['toast_percent'] = df.apply(lambda row: row.toast_bytes / row.total_bytes * 100, axis=1)

            df.sort_values('total_bytes', ascending=False, inplace=True)
            return {'data': df.to_dict(orient='records')}

    def get_table_columns_data(self):
        table_name = self.request.GET['columns_table_name']
        sql_columns = '''
            SELECT
                f.attnum AS number,
                f.attname AS name,
                f.attnotnull::int::numeric(1,0) AS notnull,
                pg_catalog.format_type(f.atttypid,f.atttypmod) AS type,
                CASE
                    WHEN p.contype = 'p' THEN 1
                    ELSE 0
                END AS primarykey,
                CASE
                    WHEN p.contype = 'u' THEN 1
                    ELSE 0
                END AS uniquekey,
                CASE
                    WHEN p.contype = 'f' THEN g.relname
                END AS foreignkey,
                CASE
                    WHEN f.atthasdef = 't' THEN pg_get_expr(d.adbin, d.adrelid)
                END AS default
            FROM pg_attribute f
                JOIN pg_class c ON c.oid = f.attrelid
                JOIN pg_type t ON t.oid = f.atttypid
                LEFT JOIN pg_attrdef d ON d.adrelid = c.oid AND d.adnum = f.attnum
                LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
                LEFT JOIN pg_constraint p ON p.conrelid = c.oid AND f.attnum = ANY (p.conkey)
                LEFT JOIN pg_class AS g ON p.confrelid = g.oid
            WHERE c.relkind = 'r'::char
                AND c.relname = '{}'
                AND f.attnum > 0 ORDER BY number
            ;
        '''.format(table_name)

        with connection.cursor() as cursor:
            cursor.execute(sql_columns)
            data = self.dictfetchall(cursor)
            columns_df = pd.DataFrame(data).fillna('')
            columns_df.sort_values('number', ascending=True, inplace=True)

            return {'data': columns_df.to_dict(orient='records')}

    def get_table_indexes_data(self):
        table_name = self.request.GET['indexes_table_name']
        sql_indexes = '''
            SELECT
                indexname,
                pg_relation_size(quote_ident(indexname)::text) as size,
                indexdef
            FROM
                pg_indexes
            WHERE
                tablename = '{}'
            ORDER BY
                indexname;
        '''.format(table_name)

        with connection.cursor() as cursor:
            cursor.execute(sql_indexes)
            data = self.dictfetchall(cursor)
            indexes_df = pd.DataFrame(data).fillna('')
            indexes_df.sort_values('size', ascending=False, inplace=True)

            return {'data': indexes_df.to_dict(orient='records')}

    def get_pg_stat_statements_data(self):
        sql_pg_stats = 'SELECT * FROM pg_stat_statements;'

        with connection.cursor() as cursor:
            try:
                cursor.execute(sql_pg_stats)
            except Exception as e:
                if e.args and 'relation "pg_stat_statements" does not exist' in e.args[0] or \
                        'pg_stat_statements must be loaded via shared_preload_libraries' in e.args[0]:
                    return {'data': [], 'error': e.args[0]}
                raise e
            data = self.dictfetchall(cursor)
            pg_stats_df = pd.DataFrame(data).fillna('')
            pg_stats_df.sort_values('total_time', ascending=False, inplace=True)

            return {'data': pg_stats_df.to_dict(orient='records')}

    def get_pg_stat_activity_data(self):
        sql_pg_stats = 'SELECT query_start, state, query FROM pg_stat_activity WHERE state IS NOT NULL;'

        with connection.cursor() as cursor:
            try:
                cursor.execute(sql_pg_stats)
            except Exception as e:
                if e.args and 'relation "pg_stat_activity" does not exist' in e.args[0] or \
                        'pg_stat_activity must be loaded via shared_preload_libraries' in \
                        e.args[0]:
                    return {'data': [], 'error': e.args[0]}
                raise e
            data = self.dictfetchall(cursor)
            pg_stats_df = pd.DataFrame(data).fillna('')
            pg_stats_df.sort_values('state', ascending=True, inplace=True)

            return {'data': pg_stats_df.to_dict(orient='records')}

    @staticmethod
    def dictfetchall(cursor):
        """
        Return all rows from a cursor as a dict
        """
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def prettify_bytes(value):
        for unit in ['bytes', 'kB', 'MB', 'GB', 'TB']:
            if abs(value) < 1024.0:
                return "%3.1f %s" % (value, unit)
            value /= 1024.0
        return "%.1f %s" % (value, 'X')


class DockerStatsView(SuperuserRequiredMixin, AjaxListView):
    template_name = 'common/docker_stats.html'
    model = MethodStats  # just to keep AjaxListView behavior

    def get_json_data(self, **kwargs):
        if self.request.GET.get('source') == 'docker_services':
            return self.get_docker_services_data()
        if self.request.GET.get('source') == 'docker_services_plain':
            return self.get_docker_services_plain_data()
        if self.request.GET.get('source') == 'docker_nodes':
            return self.get_docker_nodes_data()
        if self.request.GET.get('source') == 'docker_stats':
            return self.get_docker_stats_data()
        raise RuntimeError('Source is not specified')

    def get_docker_nodes_data(self):
        try:
            with open(settings.DOCKER_STATS_DIR + '/docker_nodes.txt', 'r') as f:
                return {'data': json.loads(f.read())}
        except Exception as e:
            return {'data': [], 'error': str(e)}

    def get_docker_services_data(self):
        try:
            with open(settings.DOCKER_STATS_DIR + '/docker_services.txt', 'r') as f:
                return {'data': json.loads(f.read())}
        except Exception as e:
            return {'data': [], 'error': str(e)}

    def get_docker_services_plain_data(self):
        try:
            df = pd.read_csv(settings.DOCKER_STATS_DIR + '/docker_services_plain.txt',
                             delimiter=r'\s{2,}')
            return {'data': list(df.T.to_dict().values())}
        except Exception as e:
            return {'data': [], 'error': str(e)}

    def get_docker_stats_data(self):
        try:
            df = pd.read_fwf(settings.DOCKER_STATS_DIR + '/docker_stats.txt').fillna('')
            df['NAME'] = df['NAME'].apply(lambda i: str(i).split('.')[0])
            df['CPU %'] = df['CPU %'].apply(lambda i: str(i).rstrip('%'))
            df['MEM %'] = df['MEM %'].apply(lambda i: str(i).rstrip('%'))
            df.columns = [re.sub(r'\W', '', i).lower() for i in df.columns]
            return {'data': list(df.T.to_dict().values())}
        except Exception as e:
            return {'data': [], 'error': str(e)}

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from apps.task.app_vars import DISK_USAGE
        ctx['disk_usage'] = DISK_USAGE.val()
        return ctx


class RedisStatsView(SuperuserRequiredMixin, AjaxListView):
    template_name = 'common/redis_stats.html'
    model = MethodStats  # just to keep AjaxListView behavior

    def get_json_data(self, **kwargs):
        # TODO: impl server-side filtering, sorting, paging if needed
        data = []
        for key in redis.r.scan_iter('*'):
            key = key.decode('utf-8')
            try:
                value = str(redis.unpickle(redis.r.get(key)))[:100]
            except:
                value = 'unpickle error'
            data.append({'key': key, 'value': value})
        return {'data': data}


class ReindexDBView(BaseAjaxTaskView):
    task_class = ReindexDB
    form_class = ReindexDBForm


def create_db_schema_graph_model_view(request) -> HttpResponse:
    """
    Renders a checkbox form or an SVG.

    Once the form is submitted, this function creates a temporary output file,
        calls the django extension "graph_models" command, and then sends the
        SVG to the output template.

    Args:
        request (WSGIRequest)

    Returns:
        An HttpResponse object which renders the selection or visualization page.
    """
    if request.method == 'POST':
        form = DBSchemaSelectionForm(request.POST)
        if form.is_valid():
            apps = form.cleaned_data['contraxsuite_apps']
            with TemporaryDirectory() as tmpdir:
                _output_filepath: str = f'{tmpdir}/db_schema.svg'
                call_command(
                    'graph_models',
                    '--group-models', *apps,
                    '--output', _output_filepath,
                    '--arrow-shape', 'normal',
                    '--theme', 'contraxsuite_with_repository_permalinks'
                )
                with open(_output_filepath, 'r') as file_svg:
                    svg: str = file_svg.read()
                    svg: str = svg[svg.find('<svg'):]
                    svg: str = svg.replace(' xlink:title="&lt;TABLE&gt;"', '')
                    svg: str = urllib.parse.quote(svg)
            return render(
                request=request,
                template_name='common/db_schema_visualization/output.html',
                context={'svg': svg}
            )
    else:
        form = DBSchemaSelectionForm()
    return render(
        request=request,
        template_name='common/db_schema_visualization/input.html',
        context={'form': form}
    )
