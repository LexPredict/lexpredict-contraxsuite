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
from django.core.validators import MinValueValidator, MaxValueValidator

# Project imports
from apps.project.models import Project

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TrainDocumentDoc2VecTaskForm(forms.Form):
    header = 'Train doc2vec model from Document queryset.'

    source = forms.CharField(initial='document', widget=forms.HiddenInput())
    transformer_name = forms.CharField(max_length=200, required=False)
    vector_size = forms.IntegerField(initial=100, required=False)
    window = forms.IntegerField(initial=10, required=False)
    min_count = forms.IntegerField(initial=10, required=False)
    dm = forms.IntegerField(initial=1, required=False, validators=(MinValueValidator(0),
                                                                   MaxValueValidator(1)))
    project = forms.ModelMultipleChoiceField(
        queryset=Project.objects.all(),
        widget=forms.SelectMultiple(
            attrs={'class': 'chosen compact'}),
        required=False)

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['project_ids'] = list(cleaned_data['project'].values_list('pk', flat=True))\
            if cleaned_data['project'] is not None else None
        del cleaned_data['project']


class TrainTextUnitDoc2VecTaskForm(TrainDocumentDoc2VecTaskForm):
    header = 'Train doc2vec model from Text Unit queryset.'

    source = forms.CharField(initial='text_unit', widget=forms.HiddenInput())
    text_unit_type = forms.ChoiceField(choices=(('sentence', 'sentence'),
                                                ('paragraph', 'paragraph')),
                                       required=True)
