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
import html
from typing import Optional
import pandas as pd

from django import forms
from django.forms.fields import BooleanField, ChoiceField
from django.forms.utils import flatatt
from django.forms.widgets import PasswordInput, Select, Textarea
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import SafeText

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class LTRCheckboxWidget(forms.widgets.CheckboxInput):
    def render(self, name, value, attrs=None, renderer=None):
        label_class = ' '.join(['checkbox-style-3-label', self.attrs.pop('label_class', '')])
        final_attrs = self.build_attrs(self.attrs, attrs)
        final_attrs['class'] = ' '.join(['checkbox-style', self.attrs.pop('class', '')])
        final_attrs['type'] = 'checkbox'
        final_attrs['name'] = name
        if self.check_test(value):
            final_attrs['checked'] = 'checked'
        if not (value is True or value is False or value is None or value == ''):
            final_attrs['value'] = force_text(value)
        label = final_attrs.pop('label')
        return format_html('<input{0} /><label for="{1}" class="{2}"> {3}</label>',
                           flatatt(final_attrs), attrs['id'], label_class, label)


class LTRCheckboxField(BooleanField):
    widget = LTRCheckboxWidget
    label_suffix = ''

    def __init__(self, *args, **kwargs):
        kwargs['widget'] = kwargs.get('widget', LTRCheckboxWidget())
        kwargs['widget'].attrs['label'] = kwargs['label']
        kwargs['label'] = ''
        super().__init__(*args, **kwargs)


class LTRRadioWidget(forms.widgets.RadioSelect):
    def render(self, name, value, attrs=None, renderer=None):
        label_class = ' '.join(['radio-style-3-label', self.attrs.pop('label_class', '')])
        choices = self.attrs.pop('choices', [])
        initial = self.attrs.pop('initial', '')
        final_attrs = self.build_attrs(self.attrs, attrs)
        final_attrs['class'] = ' '.join(['radio-style', self.attrs.pop('class', '')])
        final_attrs['type'] = 'radio'
        final_attrs['name'] = name
        html = ''
        for n, choice in enumerate(choices):
            choice_name, choice_label = choice
            choice_id = '{}_{}'.format(attrs['id'], n)
            final_attrs['id'] = choice_id
            final_attrs['value'] = choice_name
            checked = ' checked' if choice_name == initial else ''
            html += '<span><input{0}{1} /><label for="{2}" class="{3}"> {4}</label></span>'.format(
                flatatt(final_attrs), checked, choice_id, label_class, choice_label)
        return html


class LTRCheckgroupWidget(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, renderer=None):
        option_class = self.attrs.get('option_class') or 'checkbox-ltr-full-width checkbox-parent'
        check_class = self.attrs.get('check_class') or 'checkbox-style checkbox-parent'
        label_class = self.attrs.get('label_class') or 'checkbox-style-3-label'
        list_class = self.attrs.get('list_class') or ''

        widget_id = attrs['id']
        choices = self.choices

        html = f'<ul id="{widget_id}" class="{list_class}">\n'
        for n, choice in enumerate(choices):
            choice_name, choice_label = choice
            choice_id = '{}_{}'.format(widget_id, n)

            html += f'  <li>\n    <div class="{option_class}">\n'
            html += f'       <input class="{check_class}" '
            html += f'id="{choice_id}" name="{name}_choice_{choice_name}" type="checkbox">\n'
            html += f'       <label for="{choice_id}" class="{label_class}">{choice_label}</label>\n'
            html += '      </div>\n  </li>\n'

        html += '</ul>\n'
        return html

    def value_from_datadict(self, data, files, name):
        # find checked choices
        selected_options = set()
        for choice_name, _ in self.choices:
            choice_input_name = f'{name}_choice_{choice_name}'
            if choice_input_name in data:
                selected_options.add(choice_name)
        return list(selected_options)


class LTRRadioField(ChoiceField):
    widget = LTRRadioWidget
    label_suffix = ''

    def __init__(self, *args, **kwargs):
        kwargs['widget'] = kwargs.get('widget', LTRRadioWidget())
        kwargs['widget'].attrs['choices'] = kwargs['choices']
        kwargs['widget'].attrs['initial'] = kwargs['initial']
        kwargs['label'] = ''
        super().__init__(*args, **kwargs)


class FilterableProjectSelectField(forms.ModelChoiceField):
    def _get_choices(self):
        choices = super()._get_choices()
        return choices


class FiltrableProjectSelectWidget(Select):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager_id = None  # type: Optional[str]

    def render(self, name: str, value, attrs=None, renderer=None):
        """
        name='project', value=None, attrs={'id': 'id_project'}
        <select name="project" id="id_project">
        """
        wig_id = attrs['id']
        html = self.build_manager_change_script(wig_id)
        html += f'<select name="{name}" id="{wig_id}">\n'
        html += '    <option value="" selected>---------</option>\n'

        proj_set = [(p.pk, p.type.code, p.name, p.type_id) for p in self.choices.queryset.order_by('-pk')]

        for id, proj_type, proj_name, proj_type_pk in proj_set:
            val_str = f'{proj_name} ({proj_type}, #{id})'
            html += f'    <option value="{id}" data_type="{proj_type_pk}" >'
            html += f'{val_str}</option>\n'

        html += '</select>\n'
        html_safe = SafeText(html)
        return html_safe

    def build_manager_change_script(self, wig_id: str):
        markup = f"""
        <script>
            window.on_manager_changed = function() {{
                manager_val = $('#{self.manager_id}').val();
                $("#{wig_id} option[data_type]").each(function(index) {{
                    var tp_id = $(this).attr('data_type');
                    if (!manager_val || tp_id == manager_val)
                        $(this).show();
                    else
                        $(this).hide();
                }});
            }};
            $('#{self.manager_id}').on("change", window.on_manager_changed);
        </script>\n
        """
        return markup


class FriendlyPasswordInput(PasswordInput):
    empty_password_value = '        '

    def get_context(self, name, value, attrs):
        if not self.render_value:
            value = self.empty_password_value
        return super(PasswordInput, self).get_context(name, value, attrs)


class EditableTableWidget(Textarea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        from apps.document.models import DocumentFieldMultilineRegexDetector
        df = DocumentFieldMultilineRegexDetector.get_csv_as_pandas_df(value)
        if df is None:
            df = pd.DataFrame(columns=['value', 'pattern'])
        df.sort_values('value', inplace=True)

        # build an HTML table
        markup = f'<table name="{name}_table" ' \
                 f'class="table table-striped table-bordered table-hover table-condensed">' \
                 f'<tr><th>Value</th><th>Pattern</th></tr>\n'
        for _, row in df.iterrows():
            cell_value = html.escape(row[0])
            cell_pattern = html.escape(row[1])
            markup += f'<tr><td>{cell_value}</td><td>{cell_pattern}</td></tr>'
        markup += '<tr><td data-row="new-row"><a href="#">Add row...</a></td>' \
                  '<td data-row="new-row"><a href="#">Add row...</a></td></tr>'
        markup += '</table>\n'

        html_value = html.escape(value or '', quote=True)
        markup += f'<input name="{name}" type="hidden" value="{html_value}" />\n'
        return markup


class CustomLabelModelChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        self.custom_formatter = kwargs.get('custom_formatter')
        if self.custom_formatter:
            del kwargs['custom_formatter']
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        return self.custom_formatter(obj) if self.custom_formatter else super().label_from_instance(obj)
