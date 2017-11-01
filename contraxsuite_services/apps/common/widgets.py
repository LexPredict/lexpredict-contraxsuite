# -*- coding: utf-8 -*-

# Django imports
from django import forms
from django.forms.fields import BooleanField, ChoiceField
from django.forms.utils import flatatt
from django.utils.encoding import force_text
from django.utils.html import format_html

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.3/LICENSE"
__version__ = "1.0.3"
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
        super(LTRCheckboxField, self).__init__(*args, **kwargs)


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


class LTRRadioField(ChoiceField):
    widget = LTRRadioWidget
    label_suffix = ''

    def __init__(self, *args, **kwargs):
        kwargs['widget'] = kwargs.get('widget', LTRRadioWidget())
        kwargs['widget'].attrs['choices'] = kwargs['choices']
        kwargs['widget'].attrs['initial'] = kwargs['initial']
        kwargs['label'] = ''
        super(LTRRadioField, self).__init__(*args, **kwargs)
