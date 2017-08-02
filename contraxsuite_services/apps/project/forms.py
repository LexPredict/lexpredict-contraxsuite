# -*- coding: utf-8 -*-

# Django imports
from django import forms

# Project imports
from apps.project.models import Project, TaskQueue

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0/LICENSE.pdf"
__version__ = "1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@lexpredict.com"


class TaskQueueForm(forms.ModelForm):
    class Meta:
        model = TaskQueue
        fields = ['description', 'reviewers']


class TaskQueueChoiceForm(forms.Form):
    task_queue = forms.MultipleChoiceField(
        choices=[(tq.pk, tq.__str__()) for tq in TaskQueue.objects.all()],
        required=True)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'project_description']

    project_description = forms.CharField(widget=forms.Textarea)


class ProjectChoiceForm(forms.Form):
    project = forms.MultipleChoiceField(
        choices=[(p.pk, p.__str__()) for p in Project.objects.all()],
        required=True)
