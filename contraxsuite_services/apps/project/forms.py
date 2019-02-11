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

# Django imports
from django import forms

# Project imports
from apps.document.models import Document
from apps.project.models import Project, TaskQueue, DocumentFilter

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.8/LICENSE"
__version__ = "1.1.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TaskQueueForm(forms.ModelForm):
    class Meta:
        model = TaskQueue
        fields = ['description', 'reviewers']


class TaskQueueChoiceForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['task_queue'] = forms.MultipleChoiceField(
            choices=[(tq.pk, tq.__str__()) for tq in TaskQueue.objects.all()],
            required=True)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'project_description']

    project_description = forms.CharField(widget=forms.Textarea)


class ProjectChoiceForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'] = forms.MultipleChoiceField(
            choices=[(p.pk, p.__str__()) for p in Project.objects.all()],
            required=True)


class DocumentFilterForm(forms.ModelForm):
    filter_query = forms.CharField(
        widget=forms.Textarea,
        required=True,
        help_text='Query in Lucene format based on filed codes'
    )

    document_sort_order = forms.CharField(
        required=False,
        help_text='Format: field_code[:ASC|DESC]'
    )

    def clean(self):
        try:
            filter_query = self.data['filter_query']
            if filter_query and filter_query.strip():
                filter_tree = DocumentFilter.parse_filter(filter_query)
                DocumentFilter.build_filter(filter_tree, DocumentFilter.default_field_resolver)
        except Exception as exc:
            self.add_error('filter_query', exc)

        try:
            document_sort_order = self.data['document_sort_order']
            DocumentFilter(document_sort_order=document_sort_order).order_by(Document.objects)
        except Exception as exc:
            self.add_error('document_sort_order', exc)

        return super().clean()
