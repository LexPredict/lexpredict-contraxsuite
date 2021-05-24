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

# Standard library imports
from typing import Generator, List, Tuple

# Django imports
from settings import PROJECT_APPS
from django.apps import apps
from django.forms import CharField, CheckboxSelectMultiple, Form, MultipleChoiceField
from django.utils.translation import ugettext_lazy as _

# Project imports
from apps.common.widgets import LTRCheckboxField, LTRCheckboxWidget
from apps.common.widgets import FriendlyPasswordInput

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def checkbox_field(label,
                   input_class=None,
                   label_class=None,
                   initial=False,
                   required=False):
    """
    helper method to construct Checkbox field
    :param label: label text
    :param input_class: class for input element
    :param label_class: class for label
    :param initial: initial value
    :param required: required value
    :return:
    """
    defaults = dict(
        label=_(label),
        initial=initial,
        required=required)
    if input_class or label_class:
        widget_attrs = {}
        if input_class:
            widget_attrs['class'] = input_class
        if label_class:
            widget_attrs['label_class'] = label_class
        defaults['widget'] = LTRCheckboxWidget(attrs=widget_attrs)
    return LTRCheckboxField(**defaults)


class FriendlyPasswordField(CharField):
    def __init__(self, max_length=None, min_length=None, *args, **kwargs):
        super().__init__(max_length=max_length, min_length=min_length, strip=True, empty_value=None,
                         widget=FriendlyPasswordInput,
                         *args,
                         **kwargs)

    def clean(self, value):
        if value and not value.strip():
            return False
        return super().clean(value)


class ReindexDBForm(Form):
    header = 'Reindex Database and run VACUUM ANALYZE. Warning: this may take a while,' \
             ' please do not do inserts/updates/deletes in DB while the task is running.'
    reindex = checkbox_field("Run REINDEX DATABASE", initial=True)
    vacuum = checkbox_field("Run VACUUM ANALYZE")


class DBSchemaSelectionForm(Form):

    project_apps: Generator[str, None, None] = \
        (app.split('.')[1] for app in PROJECT_APPS)

    choices: List[Tuple[str, str]] = sorted(set(
        (app_name, app_name) for app_name in project_apps
        if next(apps.get_app_config(app_name).get_models(), None) is not None
    ))

    contraxsuite_apps = MultipleChoiceField(
        choices=choices,
        label='ContraxSuite Apps',
        widget=CheckboxSelectMultiple,
    )
