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

from drf_braces.serializers.form_serializer import make_form_serializer_field
from drf_braces.serializers.form_serializer import FormSerializer as BaseFormSerializer
from rest_framework import serializers

from apps.common.widgets import CustomLabelModelChoiceField, LTRCheckboxField

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class WritableSerializerMethodField(serializers.Field):

    def __init__(self, to_repr_method_name=None, to_internal_method_name=None,
                 read_only=False, write_only=False, **kwargs):
        kwargs['source'] = '*'
        super().__init__(read_only, write_only, **kwargs)
        self.to_repr_method_name = to_repr_method_name
        self.to_internal_method_name = to_internal_method_name

    def bind(self, field_name, parent):
        super().bind(field_name, parent)
        if not self.to_repr_method_name:
            self.to_repr_method_name = f'get_{field_name}'
        if not self.to_internal_method_name:
            self.to_internal_method_name = f'deserialize_{field_name}'

    def to_internal_value(self, data):
        method = getattr(self.parent, self.to_internal_method_name)
        return {self.field_name: method(data)}

    def to_representation(self, value):
        method = getattr(self.parent, self.to_repr_method_name)
        return method(value)


class FormSerializer(BaseFormSerializer):

    def __init__(self, *args, **kwargs):
        if 'form' in kwargs:
            form = kwargs.pop('form')
            self.Meta.form = form
        super().__init__(*args, **kwargs)

    class Meta:
        form = True
        field_mapping = {
            LTRCheckboxField: make_form_serializer_field(serializers.BooleanField),
            CustomLabelModelChoiceField: make_form_serializer_field(serializers.ChoiceField)
        }

    def _get_field_kwargs(self, form_field, serializer_field_class):
        kwargs = super()._get_field_kwargs(form_field, serializer_field_class)
        if isinstance(form_field, LTRCheckboxField):
            kwargs.pop('default', None)
        return kwargs
