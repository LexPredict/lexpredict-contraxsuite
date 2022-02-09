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

import json

from django import forms

from apps.common.widgets import FiltrableProjectSelectWidget, FilterableProjectSelectField
from apps.document.models import DocumentType
from apps.document.tasks import MODULE_NAME
import task_names
from apps.project.models import Project

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class ProjectModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj[1]

    def clean(self, values):
        if not values:
            return super().clean(values)
        return [json.loads(value.replace('\'', '"'))[0] for value in values]


class ReindexForm(forms.Form):
    header = task_names.TASK_NAME_MANUAL_REINDEX

    document_type = forms.ModelChoiceField(
        queryset=DocumentType.objects.all(),
        widget=forms.widgets.Select(attrs={'class': 'chosen'}),
        label='Document Type',
        required=False)

    project = FilterableProjectSelectField(
        queryset=Project.objects.order_by('-pk'),
        required=False,
        label='Restrict to project',
        widget=FiltrableProjectSelectWidget)

    recreate_tables = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'].widget.manager_id = 'id_document_type'

    def _post_clean(self):
        super()._post_clean()
        self.cleaned_data['module_name'] = MODULE_NAME
