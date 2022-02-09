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
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# Standard imports
import inspect
import json
import urllib
import re
import subprocess
from functools import lru_cache
from typing import Any, Dict, Tuple

# Django imports
from django.conf import settings
from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

# Project imports
from apps.common.utils import cap_words
from apps.common.models import AppVar

register = Library()

_REPOS: Tuple[str, str] = (
    # [0] public
    'https://www.github.com/LexPredict/lexpredict-contraxsuite',

    # [1] private
    'https://www.github.com/LexPredict/lexpredict-contraxsuite-services',
)


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


@register.simple_tag
def app_var_value(name, category='Common'):
    """
    Get AppVar value by name and category
    :return: setting value
    """
    value = AppVar.objects.filter(name=name, category=category)
    if value.exists():
        return value.last().value
    return ''


@register.simple_tag
def admin_email():
    """
    Get admin email from AppVar or settings
    :return: email (string)
    """
    value = AppVar.objects.filter(name='support_email', category='Common')
    if value.exists():
        return value.last().value
    if not hasattr(settings, 'ADMINS'):
        return ''
    admins = settings.ADMINS
    if not admins:
        return ''
    if len(admins[0]) > 1:
        return admins[0][1]
    return admins[0]


@register.simple_tag
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


@register.filter(is_safe=True)
def js(obj):
    return mark_safe(json.dumps(obj))


@lru_cache(maxsize=3)
def _get_git_data(git_command: str) -> subprocess.CompletedProcess:
    """
    Called by `get_model_permalink`.

    Because `get_model_permalink(model)` is called for each of N models iterated
        over in the graph_models theme template, this deterministic action is
        repeated N number of times. It is far more efficient to cache the
        results and return the same `subprocess.CompletedProcess` for each git
        command, since the models are all part of the same codebase on the same
        machine with the same git configuration (or lack thereof).
    """
    return subprocess.run(
        args=git_command.split(' '),
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    )


@lru_cache(maxsize=1)
def _get_build_info_txt_file(git_data: Tuple) -> Dict[str, str]:
    """
    Called by `get_model_permalink`.

    Because `get_model_permalink(model)` is called for each of N models iterated
        over in the graph_models theme template, this deterministic action is
        repeated N number of times. It is far more efficient to cache the
        results and return the same `git_data` for each model, since they are
        all part of the same codebase.
    """
    with open('/build_info.txt') as build_info:
        d: Dict[str, str] = dict(
            line.lower().strip('\n').split(': ')
            for line in build_info
        )
        git_data: Dict[str, str] = {key: '' for key in git_data}
        git_data['commit_hash']: str = d['contraxsuite commit']
        git_data['branch_name']: str = d['contraxsuite git branch']
        git_data['remote_url']: str = \
            _REPOS[1] \
            if git_data['branch_name'] == 'develop'\
            else _REPOS[0]
        return git_data


@register.filter(name='get_model_permalink', is_safe=True)
def get_model_permalink(value: Dict) -> str:
    """
    Takes a django model and returns a permalink to GitHub.

    Args:
        value: a `model` dictionary
            as generated by the `django_extensions.graph_models module`

    Returns:
        A string permalink to either the public or private GitHub repositories.

    Usage:
        HREF="{{ model|get_model_permalink }}"

    Note:
        The public/private repository inference logic is imperfect.
    """
    # get model information
    model = value['model']
    try:
        line_number: int = inspect.getsourcelines(model)[1]
    except:
        return _REPOS[0]

    # gather data for permalink construction
    git_data: Dict[str, Any] = {
        'commit_hash': 'git rev-parse HEAD',
        'branch_name': 'git rev-parse --abbrev-ref HEAD',
        'remote_url': 'git config --get remote.origin.url',
    }

    # try to infer commit, branch, and remote URL from local git repository
    for key, git_command in git_data.items():
        git_data[key]: subprocess.CompletedProcess = _get_git_data(git_command)

    # if the codebase is not a git repository, then check for a build_info file
    for key, completed_process in git_data.items():
        if completed_process.returncode == 0:
            git_data[key] = completed_process.stdout.strip('\n').strip('.git')
        else:
            try:
                git_data: Dict[str, str] = \
                    _get_build_info_txt_file((*git_data.keys(),))
                break
            except:
                return _REPOS[0]

    return f'{git_data["remote_url"]}' \
           f'/blob/{git_data["commit_hash"]}/contraxsuite_services/' \
           f'{"/".join(model.__module__.split("."))}' \
           f'.py#L{line_number}'
