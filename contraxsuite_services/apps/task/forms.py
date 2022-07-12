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
import json

# Django imports
from typing import List

from celery.states import PENDING, SUCCESS, FAILURE, REVOKED
from django import forms
from django.conf import settings

# Project imports
from django.urls import reverse

from apps.common.forms import checkbox_field
from apps.common.widgets import LTRCheckgroupWidget
from apps.document.models import DocumentType
from apps.project.models import Project
from apps.task.models import Task, TaskLogEntry

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


path_help_text_sample = '''
Relative path to a file with {}. A file should be in "&lt;ROOT_DIR&gt;/data/"
 or "&lt;APPS_DIR&gt;/media/%s" folder.''' % settings.FILEBROWSER_DOCUMENTS_DIRECTORY


class LoadDocumentsForm(forms.Form):
    header = 'Parse documents to create Documents and Text Units.'
    project = forms.ModelChoiceField(queryset=Project.objects.order_by('-pk'), required=False)
    source_data = forms.CharField(
        max_length=1000,
        required=True,
        help_text='''
        Path to a folder with uploaded files relative to "/media/%s". For example, "new" or "/".<br />
        Create new folders and upload new documents if needed.
        ''' % settings.FILEBROWSER_DOCUMENTS_DIRECTORY)
    source_type = forms.CharField(
        max_length=100,
        required=False)
    document_type = forms.ModelChoiceField(queryset=DocumentType.objects.all(), required=False)
    detect_contract = checkbox_field("Detect if a document is contract", initial=True)
    delete = checkbox_field("Delete existing Documents")
    run_standard_locators = checkbox_field("Run Standard Locators", initial=False)


def locate_field(label, parent_class='checkbox-parent'):
    return checkbox_field(label, input_class=parent_class)


def child_field(delete_tip=None, label='Delete existing usages', child_class='checkbox-child'):
    if delete_tip:
        label = "Delete existing %s Usages" % delete_tip
    return checkbox_field(label, input_class=child_class, label_class='checkbox-small level-1')


class LocateForm(forms.Form):
    header = 'Locate specific terms in existing text units.'

    locate_all = checkbox_field(
        label="Locate all items / Reverse choice",
        label_class='main-label')

    geoentity_locate = locate_field("Geo Entities and Geo Aliases", parent_class='')
    geoentity_priority = child_field(
        label="Use first entity occurrence to resolve ambiguous entities",
        child_class='')
    geoentity_delete = child_field(
        label="Delete existing Geo Entity Usages and Geo Alias Usages",
        child_class='')

    date_locate = locate_field(label='Dates', parent_class='')
    date_strict = child_field(label="Strict", child_class='')
    date_delete = child_field("Date", child_class='')

    amount_locate = locate_field('Amounts')
    amount_delete = child_field("Amount")

    citation_locate = locate_field("Citations")
    citation_delete = child_field("Citation")

    copyright_locate = locate_field("Copyrights")
    copyright_delete = child_field("Copyright")

    court_locate = locate_field('Courts')
    court_delete = child_field('Court')

    currency_locate = locate_field('Currencies')
    currency_delete = child_field('Currency')

    duration_locate = locate_field('Date Durations')
    duration_delete = child_field('Date Duration')

    definition_locate = locate_field('Definitions')
    definition_delete = child_field('Definition')

    distance_locate = locate_field('Distances')
    distance_delete = child_field('Distance')

    party_locate = locate_field('Parties')
    party_delete = child_field('Parties and Party Usages')

    percent_locate = locate_field('Percents')
    percent_delete = child_field('Percent')

    ratio_locate = locate_field('Ratios')
    ratio_delete = child_field('Ratio')

    regulation_locate = locate_field('Regulations')
    regulation_delete = child_field('Regulation')

    term_locate = locate_field('Terms')
    term_delete = child_field('Term')

    trademark_locate = locate_field('Trademarks')
    trademark_delete = child_field('Trademark')

    url_locate = locate_field('Urls')
    url_delete = child_field('Url')

    parse = forms.MultipleChoiceField(
        widget=LTRCheckgroupWidget(),
        choices=(('sentence', 'Find in sentences'),
                 ('paragraph', 'Find in paragraphs')),
        label="Text units where to find terms")
    '''
    parse = LTRRadioField(
        choices=(('sentence', 'Parse Text Units with "sentence" types'),
                 ('paragraph', 'Parse Text Units with "paragraph" type')),
        initial='sentence',
        required=False)
    '''

    project = forms.ModelChoiceField(queryset=Project.objects.order_by('-pk'), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        from apps.extract.app_vars import STANDARD_LOCATORS, OPTIONAL_LOCATORS
        available_locators = set(STANDARD_LOCATORS.val()) | set(OPTIONAL_LOCATORS.val())

        for field in list(self.fields.keys()):
            if field in ['parse', 'locate_all', 'project']:
                continue
            field_name = field.split('_')[0]
            if field_name not in available_locators:
                del self.fields[field]

    def is_valid(self):
        is_form_valid = super().is_valid()

        # check at least one "locate" choice is selected
        has_locate_chosen = bool([1 for k, v in self.cleaned_data.items() if 'locate' in k and v is True])
        if has_locate_chosen is False:
            self.add_error('locate_all', 'Please choose a locator.')

        if not is_form_valid:
            return False

        # check at least one "parse" choice is selected
        if 'parse' not in self.cleaned_data or not self.cleaned_data['parse']:
            return False
        return True


class UpdateElasticSearchForm(forms.Form):
    header = 'The update index command will freshen all of the content ' \
             'in Elasticsearch index. Use it after loading new documents.'


class TotalCleanupForm(forms.Form):
    header = 'Delete all existing Projects, Documents, Tasks, etc.'


class TaskDetailForm(forms.Form):
    task = forms.CharField(disabled=True)
    parents = forms.CharField(disabled=True)
    child_tasks = forms.CharField(disabled=True)
    log = forms.CharField(widget=forms.Textarea, disabled=True)
    COLOR_BY_STATUS = {PENDING: '#ca3', SUCCESS: '#190', FAILURE: '#900', 'default': '#666'}
    NO_STACK_TRACE_EXCEPTIONS = ['document is injured', 'No text extracted.']

    def __init__(self, prefix, instance: Task, initial):
        super().__init__()
        display_name = instance.display_name or instance.name
        if display_name != instance.name:
            display_name += f' ({instance.name})'
        if instance.status != SUCCESS:
            display_name += f' STATUS: {instance.status}'
        if instance.progress < 100:
            display_name += f' ({instance.progress}%)'

        self.fields['task'].initial = display_name
        self.fields['parents'].initial = ''
        self.fields['child_tasks'].initial = ''

        logs = []  # type: List[str]
        # on this stage it was quite hard to implement proper formatting in templates
        # so putting some html/js right here.
        # TODO: Refactor, put formatting to the templates

        # list ancestors (parent tasks) up to the root
        parents_markup = []
        this_task = instance
        while this_task.parent_task_id:
            parent = this_task.parent_task
            task_name = parent.display_name or parent.name
            url = reverse('task:task-detail', args=[parent.pk])
            color = self.COLOR_BY_STATUS.get(parent.status) or self.COLOR_BY_STATUS['default']
            link_name = task_name if parent.progress == 100 else f'{task_name} ({parent.progress}%)'
            parents_markup.append(f'<a style="{color}" href="{url}">{link_name}</a>')
            this_task = this_task.parent_task

        markup = ''
        if parents_markup:
            markup = ' &lt;- '.join(parents_markup)
        self.fields['parents'].initial = markup

        # list child tasks
        child_query = Task.objects.filter(parent_task_id=instance.pk)
        children_count = child_query.count()
        children = list(child_query.values_list(
            'pk', 'name', 'display_name', 'status', 'progress')[:30])
        children_markup = []
        for pk, name, display_name, status, progress in children:
            url = reverse('task:task-detail', args=[pk])
            color = self.COLOR_BY_STATUS.get(status) or self.COLOR_BY_STATUS['default']
            task_name = display_name or name
            link_name = task_name if progress == 100 else f'{task_name} ({progress}%)'
            children_markup.append(f'<a style="{color}" href="{url}">{link_name}</a>')
        if children_count > len(children):
            children_markup.append(f' ... and {children_count - len(children)} more')
        self.fields['child_tasks'].initial = ', '.join(children_markup)

        if this_task.result and 'exc_type' in this_task.result:
            ex_module = this_task.result.get('exc_module') or '-'
            ex_message = this_task.result.get('exc_message') or '-'
            msg = f'<b><span style="color:red">ERROR</span> {this_task.result["exc_type"]} ' + \
                  f'in {ex_module}:\n{ex_message}'
            logs.append(msg)

        # Main problem is that this form's template uses base template which replaces \n with <br />
        should_search_errors = this_task.status in {FAILURE, REVOKED} or \
            this_task.own_status in {FAILURE, REVOKED}
        all_records = instance.get_task_log_from_elasticsearch(should_search_errors)
        task_records = [r for r in all_records if r.task_name]
        genr_records = [r for r in all_records if not r.task_name]

        for record in task_records:
            color = self.get_task_record_color(record)
            ts = record.timestamp.strftime('%Y-%m-%d %H:%M:%S') if record.timestamp else ''
            level = record.log_level or 'INFO'
            message = record.message or ''
            message = '<br />' + message if '\n' in message else message
            message = message.replace('\n', '<br />')
            log_add = f'<b><span style="color: {color}">{level}</span> {ts} ' \
                      f'| {record.task_name or "no task"} |</b> {message}'
            logs.append(log_add)

            if record.stack_trace \
                    and all([i not in record.message for i in self.NO_STACK_TRACE_EXCEPTIONS]):
                # Adding JS to toggle stack trace showing/hiding
                stack = record.stack_trace.replace('<', '&lt;').replace(
                    '>', '&gt;').replace('\n', '<br />')
                self.render_collapsible_block(logs, stack, 'Stack trace')

        # show system-wide errors in collapsible block
        if genr_records:
            logs.append(f'<br/><h4>{len(genr_records)} error(s) also occurred after completing '
                        f'the task</h4>')
            inner_block = ''
            for record in genr_records:
                color = self.get_task_record_color(record)
                ts = record.timestamp.strftime('%Y-%m-%d %H:%M:%S') if record.timestamp else ''
                level = record.log_level or 'INFO'
                message = record.message or ''
                message = '<br />' + message if '\n' in message else message
                log_add = f'<b><span style="color: {color}">{level}</span> {ts} </b> ' \
                          f'{message}<br/>'
                inner_block += log_add
            self.render_collapsible_block(logs, inner_block, 'System-wide errors')

        self.fields['log'].initial = '\n'.join(logs)

    @classmethod
    def render_collapsible_block(cls,
                                 logs: List[str],
                                 block_text: str,
                                 block_heading: str):
        logs.append(f'<a onclick="showHideToggleOnclick(this)">[+] {block_heading}:</a>'
                    f'<div style="display: none; border-left: 1px solid grey; padding-left: 16px">{block_text}</div>')

    @classmethod
    def get_task_record_color(cls, record: TaskLogEntry) -> str:
        color = 'green'
        if record.log_level == 'WARN':
            color = 'yellow'
        elif record.log_level == 'ERROR':
            color = 'red'
        return color


class CleanProjectForm(forms.Form):
    header = 'Clean Project (delete project content or project itself as well.'
    _project = forms.ModelChoiceField(queryset=Project.objects.order_by('-pk'), required=True)
    delete = checkbox_field("Delete Project itself as well.", initial=True)

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['_project_id'] = cleaned_data['_project'].pk
        del cleaned_data['_project']


class LoadFixtureForm(forms.Form):
    header = 'Load Model objects from fixture file'
    fixture_file = forms.FileField(required=True, allow_empty_file=False)
    mode = forms.ChoiceField(
        label='Algorithm',
        choices=[('default', 'Default - Install all, replace existing objects by id'),
                 ('shift', 'Shift - Install all, make new object if object with that id exists, '
                           'either skip for non-unique object'),
                 ('partial', 'Partial - Install only new objects by id'),
                 ('soft', 'Soft - do not install if any objects already exists')],
        required=True,
        initial='default',
        help_text='Method for fixtures installation')


class DumpFixtureForm(forms.Form):
    header = 'Dump Model objects to fixture file'
    app_name = forms.CharField(
        label='Application Name',
        max_length=10,
        required=True)
    model_name = forms.CharField(
        label='Model Name',
        max_length=20,
        required=True)
    file_name = forms.CharField(
        label='File Name',
        max_length=20,
        required=True)
    filter_options = forms.CharField(
        max_length=100,
        required=False,
        help_text='E.g. django queryset filter options for a given model: '
                  '{"name__contains": "Agreement", "pk__gte": 123}')
    indent = forms.IntegerField(
        label='Indent',
        initial=4,
        required=False)

    def clean_filter_options(self):
        filter_options = self.cleaned_data['filter_options']
        if filter_options:
            try:
                filter_options = json.loads(filter_options)
            except:
                raise forms.ValidationError("Invalid data in filter_options")
        return filter_options


class BuildOCRRatingLanguageModelForm(forms.Form):
    header = 'Build OCR Rating Language Model'

    source_files_archive = forms.FileField(required=True, label='Packed text files (zip)')

    lang = forms.ChoiceField(choices=(('en', 'English'),
                                      ('de', 'German'),
                                      ('es', 'Spanish')),
                             required=True, label='Sample files language')
    extension = forms.ChoiceField(choices=(('*', 'all files inside the archive (*.*)'),
                                           ('txt', 'text files only (*.txt)')),
                                  required=True, label='Extension')


class LoadTermsForm(forms.Form):
    source_file = forms.FileField(required=True, allow_empty_file=False)


class LoadCompanyTypesForm(forms.Form):
    source_file = forms.FileField(required=True, allow_empty_file=False)
