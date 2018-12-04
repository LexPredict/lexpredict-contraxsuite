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
__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.6/LICENSE"
__version__ = "1.1.6"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

# Standard imports
import urllib
import re

# Django imports
from django.conf import settings
from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

# Project imports
from apps.common.utils import cap_words

register = Library()


@register.filter(is_safe=True)
@stringfilter
def capwords(value):
    """
    Capitalizes the first character of every word in the value.
    Use except_words dict for exceptions.
    """
    return cap_words(value)


@register.filter(name='add_class')
def add_class(value, arg):
    """
    Extend widget classes collection
    :param value: form field
    :param arg: class name
    :return: updated form field
    """
    cls = value.field.widget.attrs.get('class') or ''
    return value.as_widget(attrs={'class': arg + ' ' + cls})


@register.filter(name='readonly')
def readonly(value):
    """
    Set readonly attr for a field
    """
    value.field.widget.attrs['readonly'] = True
    value.field.widget.attrs['disabled'] = True
    return value


@register.filter(name='get_field_type')
def get_field_type(form_field):
    """
    Get form field type
    """
    return form_field.field.__class__.__name__.lower()


@register.filter(name='as_dd')
def as_dd(field):
    """
    Get form field value/values wrapped by <dd>
    """
    if field.is_hidden:
        return ''
    field_type = get_field_type(field)
    if field_type == 'booleanfield':
        cls = 'fa-check-square-o' if field.value() else 'fa-square-o'
        html = '<dd><i class="fa %s"></i></dd>' % cls
    elif 'multiplechoicefield' in field_type:
        li = ''.join(['<li>{}</li>'.format(n)
                      for i, n in field.field.choices if i in field.value()])
        html = '<dd><ul class="list-unstyled">%s</ul></dd>' % li
    elif field_type in ('typedchoicefield', 'modelchoicefield'):
        if field.value():
            html = '<dd>{}</dd>'.format(dict(field.field.choices)[field.value()])
        else:
            html = '<dd>-</dd>'
    else:
        html = '<dd>{}</dd>'.format(field.value())
    html = html.replace('\n', '<br />')
    html = re.sub(r'==(\w[\w\s]+\w)==', r'<i class="term-link">\1</i>', html)
    html = re.sub(r'<<(.+?)\|(.+?)>>', r'<a href="\1">\2</a>', html)
    return mark_safe('<dt>%s</dt>' % field.label + html)


@register.simple_tag
def get_attr(obj, attr):
    return getattr(obj, attr)


@register.simple_tag
def replace(value, arg1, arg2):
    """
    Python's replace analog
    """
    return value.replace(arg1, arg2)


@register.simple_tag
def settings_value(name):
    """
    Get django settings variable by name
    :param name: variable name
    :return: setting value
    """
    value = getattr(settings, name, "")
    if isinstance(value, (list, tuple)):
        value = mark_safe(list(value))
    return value


@register.assignment_tag
def get_settings_value(name):
    """
    Get django settings variable by name
    :param name: variable name
    :return: setting value
    """
    return settings_value(name)


@register.filter(name='simple_replace')
def simple_replace(value, repl):
    return value.replace('REPLACE', str(repl))


@register.filter(name='linebreak_replace')
def linebreak_replace(value, repl='<br />'):
    return mark_safe(value.replace('\n', repl))


@register.filter(name='get_query')
def get_query(request, delete_page=True):
    query = request.GET.dict()
    if delete_page:
        query.pop('page', None)
    return urllib.parse.urlencode(query)


@register.filter(name='as_tr')
def as_tr(field):
    """
    Get form field value/values wrapped by <dd>
    """
    if field.is_hidden:
        return ''
    field_type = get_field_type(field)
    if field_type == 'booleanfield':
        cls = 'fa-check-square-o' if field.value() else 'fa-square-o'
        td = '<td><i class="fa %s"></i></td>' % cls
    elif 'multiplechoicefield' in field_type:
        li = ''.join(['<li>{}</li>'.format(n)
                      for i, n in field.field.choices if i in field.value()])
        td = '<td><ul class="list-unstyled">%s</ul></td>' % li
    elif field_type in ('typedchoicefield', 'modelchoicefield'):
        if field.value():
            td = '<td>{}</td>'.format(dict(field.field.choices)[field.value()])
        else:
            td = '<td>-</td>'
    else:
        td = '<td>{}</td>'.format(field.value())
    td = td.replace('\n', '<br />')
    td = re.sub(r'==(\w[\w\s]+\w)==', r'<i class="term-link">\1</i>', td)
    td = re.sub(r'<<(.+?)\|(.+?)>>', r'<a href="\1">\2</a>', td)
    th = '<td class="as-th text-right">%s</td>' % field.label
    return mark_safe('<tr class="text-left">%s%s</tr>' % (th, td))


@register.filter(name='is_in')
def is_in(value, collection):
    return value in collection


@register.simple_tag
def _url(url):
    """
    Pseudo tag - instead of temporary / not existing url
    :param url: url
    :return: "#"
    """
    return "#"
