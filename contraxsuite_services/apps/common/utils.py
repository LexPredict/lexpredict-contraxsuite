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
import random
import re
import uuid

# Django imports
from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.utils.text import slugify
import django_excel as excel

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.5/LICENSE"
__version__ = "1.0.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def cap_words(value):
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
    protocol = 'https' if request.is_secure() else 'http'
    return '{protocol}://{host}{rel_url}'.format(
        protocol=protocol, host=request.get_host(), rel_url=rel_url)


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
    return uuid.UUID(int=random.getrandbits(128), version=4)
