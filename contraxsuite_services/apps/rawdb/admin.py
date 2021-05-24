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
from django.contrib import admin
from django.forms import ModelForm

# Project imports
from apps.document.models import DocumentType
from apps.project.models import Project
from apps.rawdb.models import SavedFilter

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


none_type = type(None)


class SavedFiltersAdminForm(ModelForm):

    def validate_json_field(self, field_name: str, assert_types=None) -> None:
        json_value = self.data.get(field_name)
        try:
            value = json.loads(json_value)
            if assert_types is not None:
                assert(isinstance(value, assert_types) is True)
        except AssertionError:
            self.add_error(field_name, 'This field accepts {} data types only'.format(str(assert_types)))
        except Exception as exc:
            self.add_error(field_name, exc)

    def clean(self):
        project = self.cleaned_data['project']  # type: Project
        document_type = self.cleaned_data['document_type']  # type: DocumentType

        self.validate_json_field('columns', assert_types=(list, none_type))
        self.validate_json_field('column_filters', assert_types=(dict, none_type))
        self.validate_json_field('order_by')

        if project and project.type != document_type:
            self.add_error('project', 'Specified project has different document type.')


class SavedFiltersAdmin(admin.ModelAdmin):
    list_display = ('pk', 'filter_type', 'user_name', 'title', 'document_type_code', 'project_name',
                    'display_order', 'column_filters', 'order_by')
    search_fields = ('pk', 'document_type__code', 'project__name', 'title', 'filter_type', 'user__name',
                     'user__username')

    form = SavedFiltersAdminForm

    def get_search_results(self, request, queryset, search_term):
        qs, has_duplicates = super().get_search_results(request, queryset, search_term)
        return qs.select_related('document_type', 'project', 'user'), has_duplicates

    @staticmethod
    def document_type_code(obj):
        return obj.document_type.code if obj.document_type else None

    @staticmethod
    def project_name(obj):
        return obj.project.name if obj.project else None

    @staticmethod
    def user_name(obj):
        return obj.user.name if obj.user else None


admin.site.register(SavedFilter, SavedFiltersAdmin)
