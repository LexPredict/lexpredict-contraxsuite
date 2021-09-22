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
import importlib
import io
import re
import subprocess
import sys
import uuid
from typing import Union, Optional, Dict, Any

# Third-party imports
import dateparser
import django_excel as excel
import pandas as pd
import pdfkit as pdf
from django.utils.timezone import get_current_timezone
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# Django imports
from django.conf import settings
from django.conf.urls import url
from django.contrib.postgres.fields import ArrayField
from django.contrib.sites.models import Site
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Aggregate, CharField, Value, IntegerField, Func
from django.db.models.functions import Cast
from django.http import HttpResponse
from django.urls import reverse
from django.utils import numberformat
from django.utils.text import slugify


# App imports
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class Map(dict):
    """
    Class that converts dict into class-like object with access to its values via .key
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    print(m.first_name, m.age)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super().__delitem__(key)
        del self.__dict__[key]


def cap_words(value: Optional[str]) -> Optional[str]:
    """
    Capitalizes the first character of every word in the value.
    Use except_words dict for exceptions.
    """
    if value is None:
        return None
    words = []
    except_words = ['of', 'or', 'in', 'on', 'to', 'the']
    for elem in value.replace('_', ' ').split():
        if elem in except_words:
            words.append(elem)
        else:
            words.append(elem[0].upper() + elem[1:])
    return value and ' '.join(words)


def clean_html_tags(html):
    """
    Simple regex HTML tag cleaner.
    """
    return re.sub(r'<.+?>', '', html)


def construct_full_url(request, rel_url):
    """
    URL constructor based on request and relative URL.
    :param request: request object
    :param rel_url: URL, beginning with slash
    :return:
    """
    # UWSGI - Daphne migration
    if request is WSGIRequest:
        return request.build_absolute_uri(rel_url)
    protocol = 'https' if request.is_secure() else 'http'
    return '{protocol}://{host}{rel_url}'.format(
        protocol=protocol, host=request.get_host(), rel_url=rel_url)


def full_reverse(*args, **kwargs):
    """
    Get full absolute url for a given url name
    :param args: args for reverse
    :param kwargs: kwargs for reverse
    :param request: Request object
    :return:
    """
    # keep for further using, delete "request" kwarg from from callers if needed
    _ = kwargs.pop('request', None)

    if 'protocol' in kwargs:
        protocol = kwargs.pop('protocol')
    else:
        protocol = settings.API_URL_PROTOCOL

    rel_url = reverse(*args, **kwargs)
    # UWSGI - Daphne migration
    # if request is not None:
    #     return construct_full_url(request, rel_url)
    host_name = Site.objects.get_current().domain
    # UWSGI - Daphne migration
    abs_url = host_name.rstrip('/\\') + '/' + rel_url.lstrip('/\\')
    return f'{protocol}://{abs_url}'


def export_qs_to_file(request, qs, column_names=None,
                      file_type='xlsx', file_name=None,
                      url_name=None, get_params=None,
                      url_arg=None):
    """
    Export query to file.

    :param request:
    :param qs:
    :param column_names:
    :param file_type:
    :param file_name:
    :param url_name:
    :param get_params:
    :param url_arg:
    :return:
    """

    # columns names - go into file
    # fields - extract from db
    if column_names:
        column_names = list(column_names)

    # construct file name if it's not given
    if file_name is None:
        file_name = '{}_list_{}.{}'.format(
            qs.model._meta.model_name,
            datetime.datetime.now().isoformat(),
            file_type
        )

    # split fields into fk, m2m, others
    fields = [f.name for f in qs.model._meta.local_fields
              if f.__class__.__name__ not in ('ManyToOneRel', 'ForeignKey')]
    fields_fk = [f.name for f in qs.model._meta.local_fields
                 if f.__class__.__name__ == 'ForeignKey']
    fields_m2m = [f.name for f in qs.model._meta.many_to_many]

    fields_rtf = [f.name for f in qs.model._meta.local_fields
                  if f.__class__.__name__ == 'RichTextField']

    # if custom column names
    if column_names is not None:
        fields_fk = set(column_names) & set(fields_fk)
        fields_m2m = set(column_names) & set(fields_m2m)
        fields = list(set(column_names) - fields_fk - fields_m2m)
    else:
        column_names = fields + list(fields_fk) + list(fields_m2m)

    if url_name is not None:
        column_names.append('link')

    if 'pk' not in fields:
        fields.append('pk')

    if url_arg:
        fields.append(url_arg)

    # get data from local fields (not fk or m2m)
    data = qs.values(*fields)

    get_params = get_params(request) if callable(get_params) else get_params
    get_params = '?{}'.format(get_params) if get_params else ''

    for item in data:

        # add link to concrete object to each row if needed
        if url_name is not None:
            item['link'] = construct_full_url(
                request,
                reverse(
                    url_name,
                    args=[item[url_arg] if url_arg else item['pk']])) + get_params

        # hit db only if these fields are present
        if fields_fk or fields_m2m:
            obj = qs.model.objects.get(pk=item['pk'])
            # get __str__ for fk
            for fk_field in fields_fk:
                item[fk_field] = str(getattr(obj, fk_field))
            # get list of __str__ for each object in m2m
            for m2m_field in fields_m2m:
                item[m2m_field] = ', '.join([str(i) for i in getattr(obj, m2m_field).all()])
        # clean ReachTextField value from html tags
        for rtf_field in fields_rtf:
            item[rtf_field] = clean_html_tags(item[rtf_field])

    # convert to array
    array_header = list([cap_words(re.sub(r'_+', ' ', i)) for i in column_names])
    array_data = [[row[field_name] for field_name in column_names] for row in data]
    array = [array_header] + array_data

    return excel.make_response_from_array(
        array, file_type, status=200, file_name=file_name,
        sheet_name='book')


def create_standard_urls(model, views, view_types=('list', 'add', 'detail', 'update', 'delete')):
    """
    Create standard urls based on slugified model name
    :param model: actual model
    :param views: views
    :param view_types: list or tuple ('list', 'add', 'detail', 'update', 'delete')
    :return:
    """
    model_slug = slugify(model._meta.verbose_name)
    view_pattern = '%s{}%s' % (model.__name__, 'View')
    urlpatterns = []

    if 'top_list' in view_types:
        urlpatterns += [
            url(r'^{}/list/$'.format('top-' + model_slug),
                getattr(views, 'Top' + view_pattern.format('List')).as_view(),
                name='top-{}-list'.format(model_slug))]
    if 'list' in view_types:
        urlpatterns += [
            url(r'^{}/list/$'.format(model_slug),
                getattr(views, view_pattern.format('List')).as_view(),
                name='{}-list'.format(model_slug))]
    if 'add' in view_types:
        urlpatterns += [
            url(r'^{}/add/$'.format(model_slug),
                getattr(views, view_pattern.format('Create')).as_view(),
                name='{}-add'.format(model_slug))]
    if 'detail' in view_types:
        urlpatterns += [
            url(r'^{}/(?P<pk>\d+)/detail/$'.format(model_slug),
                getattr(views, view_pattern.format('Detail')).as_view(),
                name='{}-detail'.format(model_slug))]
    if 'update' in view_types:
        urlpatterns += [
            url(r'^{}/(?P<pk>\d+)/update/$'.format(model_slug),
                getattr(views, view_pattern.format('Update')).as_view(),
                name='{}-update'.format(model_slug))]
    if 'delete' in view_types:
        urlpatterns += [
            url(r'^{}/(?P<pk>\d+)/delete/$'.format(model_slug),
                getattr(views, view_pattern.format('Delete')).as_view(),
                name='{}-delete'.format(model_slug))]
    return urlpatterns


def fast_uuid():
    # this function may be used for overriding generating uuids
    # used for various needs in the project
    # Originally we were creating uuids fully based on Python random generation
    # but next we replaced it with the standard implementation to avoid too straightforward
    # dependency on the random seed.
    return uuid.uuid4()


def get_api_module(app_name):
    module_path_str = 'apps.{app_name}.api.{api_version}.api'.format(
        app_name=app_name,
        api_version=settings.REST_FRAMEWORK['DEFAULT_VERSION']
    )
    try:
        return importlib.import_module(module_path_str)
    except ImportError:
        module_path_str = 'apps.{app_name}.api.{api_version}'.format(
            app_name=app_name,
            api_version=settings.REST_FRAMEWORK['DEFAULT_VERSION']
        )
        return importlib.import_module(module_path_str)


def download_xls(data: pd.DataFrame, file_name='output', sheet_name='doc'):
    if isinstance(data, list):
        data = pd.DataFrame(data)
    buffer = io.BytesIO()
    writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
    data.to_excel(writer, index=False, sheet_name=sheet_name, encoding='utf-8')
    writer.save()
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="{}.{}"'.format(file_name, 'xlsx')
    response.write(buffer.getvalue())
    return response


def download_csv(data: pd.DataFrame, file_name='output'):
    buffer = io.StringIO()
    data.to_csv(buffer, index=False, encoding='utf-8')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.{}"'.format(file_name, 'csv')
    response.write(buffer.getvalue())
    return response


def download_pdf(data: pd.DataFrame, file_name='output'):
    data_html = data.to_html(index=False)
    try:
        data_pdf = pdf.from_string(data_html, False)
    except OSError:
        env = Environment(loader=FileSystemLoader(settings.PROJECT_DIR('templates')))
        template = env.get_template('pdf_export.html')
        template_vars = {"title": file_name.capitalize(),
                         "table": data_html}
        data_pdf = HTML(string=template.render(template_vars)).write_pdf()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{}.{}"'.format(file_name, 'pdf')
    response.write(data_pdf)
    return response


def download(data: [list, pd.DataFrame], fmt='csv', file_name='output'):
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)
    data[data.select_dtypes(['object', 'datetime64[ns, UTC]']).columns] = data.select_dtypes(
        ['object', 'datetime64[ns, UTC]']).apply(lambda x: x.astype(str))
    data.fillna('', inplace=True)
    columns = {i: cap_words(i) for i in data.columns}
    data.rename(columns=columns, inplace=True)
    if fmt == 'xlsx':
        return download_xls(data, file_name=file_name)
    if fmt == 'pdf':
        return download_pdf(data, file_name=file_name)
    return download_csv(data, file_name=file_name)


def get_test_user():
    from allauth.account.models import EmailAddress
    test_user, created = User.objects.update_or_create(
        username='test_user',
        defaults=dict(
            first_name='Test',
            last_name='User',
            name='Test User',
            email='test@user.com',
            is_active=True))
    if created:
        test_user.set_password('test_user')
        test_user.save()
        EmailAddress.objects.create(
            user=test_user,
            email=test_user.email,
            verified=True,
            primary=True)

    return test_user


def format_number(num):
    """
    Add thousand separator to a number
    """
    return numberformat.format(num,
                               grouping=3,
                               decimal_sep='.',
                               thousand_sep=',',
                               force_grouping=True)


class Serializable(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # hack to fix _json.so make_encoder serialize properly
        self.__setitem__('dummy', 1)

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

    def _myattrs(self):
        return [
            (x, self._repr(getattr(self, x)))
            for x in self.__dir__()
            if x not in Serializable().__dir__()
        ]

    def _repr(self, value):
        if isinstance(value, (str, int, float, list, tuple, dict)):
            return value
        return repr(value)

    def __repr__(self):
        return '<%s.%s object at %s>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            hex(id(self))
        )

    def keys(self):
        return iter([x[0] for x in self._myattrs()])

    def values(self):
        return iter([x[1] for x in self._myattrs()])

    def items(self):
        return iter(self._myattrs())


def fetchone(pattern, text, flags=None):
    args = (pattern, text, flags) if flags is not None else (pattern, text)
    res = re.findall(*args)
    if res:
        return res[0]


def migrating():
    return 'makemigrations' in sys.argv or 'migrate' in sys.argv


def dictfetchall(cursor):
    """
    Return all rows from a cursor as a dict
    """
    columns = [col[0] for col in cursor.description]
    values = cursor.fetchall()
    if values:
        return [dict(zip(columns, row)) for row in values]
    return []


def dictfetchone(cursor):
    """
    Return one row from a cursor as a dict
    """
    columns = [col[0] for col in cursor.description]
    value = cursor.fetchone()
    if value is not None:
        return dict(zip(columns, value))


def safe_to_int(s: str) -> Union[int, None]:
    if not s:
        return
    try:
        return int(s)
    except ValueError:
        return


class GroupConcat(Aggregate):
    """
    Concatenate kind of m2m fields for an instance into one string with a separator like:
    User.objects.annotate(group_names=GroupConcat('groups__name', separator='; '))
    <QuerySet [{'username': 'test', 'group_names': 'Technical Admin; Super Admin', ...}, ...]>
    User.objects.annotate(group_ids=GroupConcat('groups__pk'))
    <QuerySet [{'username': 'test', 'group_ids': '1, 2', ...}, ...]>
    """
    function = 'GROUP_CONCAT'
    template = '%(function)s(%(expressions)s)'
    separator = ', '
    output_field = CharField()
    allow_distinct = True

    def __init__(self, expression, **extra):
        output_field = extra.pop('output_field', self.output_field)
        separator = Value(extra.pop('separator', self.separator))
        expression = Cast(expression, output_field=output_field)
        super().__init__(expression, separator, output_field=output_field, **extra)

    def as_postgresql(self, compiler, connection):
        self.function = 'STRING_AGG'
        return super().as_sql(compiler, connection)


class ArrayPosition(Func):
    """
    Annotate/sort by some external order
    qs.annotate(ordering=ArrayPosition(external_pk_list, F('pk'), base_field=UUIDField())).order_by('ordering')
    """
    function = 'array_position'
    output_field = IntegerField()

    def __init__(self, items, *expressions, **extra):
        if 'base_field' in extra:
            base_field = extra['base_field']
        else:
            if isinstance(items[0], int):
                base_field = IntegerField()
            else:
                base_field = CharField(max_length=max(len(i) for i in items))
        first_arg = Value(list(items), output_field=ArrayField(base_field))
        expressions = (first_arg,) + expressions
        extra['output_field'] = self.output_field
        super().__init__(*expressions, **extra)


def get_free_mem() -> str:
    process = subprocess.Popen(['free', '-m'], stdout=subprocess.PIPE)
    output, _error = process.communicate()
    data = output.decode('utf-8')
    values = [int(m.group(0)) for m in re.finditer(r'\d+', data)]
    if len(values) > 3:
        return f'Total={values[0]} MB. Used={values[1]} MB. Free={values[2]} MB.'
    return data


def unpack_nested_dict(data: dict, to_level: Union[int, None] = 1, level_sep: str = '__',
                       level: int = 1, parent: str = None):
    """
    Unpack nested dict
    :param data: dict to unpack
    :param parent: inner parent counter
    :param to_level: max recursion level to unpack else None to unpack all
    :param level: inner level counter
    :param level_sep: str to join level names level1__level2__level3
    :return:
    Example:
    a = [{'a':1, 'b': 'aaa', 'c': {'c1': 1, 'c2': {'cc1':1, 'cc2':2}}}, {'a':3, 'b': 'aaa111', 'c': {'c1': 2, 'c2': 'fff'}}]
    In: [dict(unpack_nested_dict(i, to_level=None)) for i in a]
    Out: [{'a': 1, 'b': 'aaa', 'c__c1': 1, 'c__c2__cc1': 1, 'c__c2__cc2': 2},
          {'a': 3, 'b': 'aaa111', 'c__c1': 2, 'c__c2': 'fff'}]
    """
    for k, v in data.items():
        k = k if parent is None else f'{parent}{level_sep}{k}'
        if isinstance(v, dict) and (to_level is None or level <= to_level):
            yield from unpack_nested_dict(v, parent=k, to_level=to_level, level=level + 1, level_sep=level_sep)
        else:
            yield k, v


def unpack_dict_columns(data: dict, unpack_columns=None, unpack_columns_recursive=None, to_level=None, level_sep='__'):
    """
    Unpack nested dict if columns to unpack provided
    :param data: dict
    :param unpack_columns: unpack columns to 1st level only (non-recursive)
    :param unpack_columns_recursive: unpack columns recursively
    :param to_level: max recursion level to unpack else None to unpack all
    :param level_sep: str to join level names level1__level2__level3
    :return:
    """
    unpack_columns = unpack_columns or []
    unpack_columns_recursive = unpack_columns_recursive or []
    for k, v in data.items():
        if (k not in unpack_columns and k not in unpack_columns_recursive) or not isinstance(v, dict):
            yield k, v
        else:
            to_level = to_level if k in unpack_columns_recursive else 1
            yield from unpack_nested_dict(v, parent=k, to_level=to_level, level=2, level_sep=level_sep)


def parse_date(date_str: str) -> Optional[datetime.datetime]:
    if not date_str:
        return None
    return dateparser.parse(date_str, settings={
        'TIMEZONE': get_current_timezone().zone})
