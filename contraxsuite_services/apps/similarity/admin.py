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

# Django imports
from django.contrib import admin
from django.forms import ModelForm

from apps.document.models import DocumentField
# Project imports
from apps.similarity.models import DocumentSimilarityConfig, ATTR_DST_FIELD,\
    ATTR_DATE_CONSTRAINT_DAYS, ATTR_DATE_CONSTRAINT_FIELD

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class SimilarDocumentsFieldConfigAdminForm(ModelForm):
    def clean(self):
        dst_field = self.cleaned_data.get(ATTR_DST_FIELD)  # type: DocumentField
        date_constraint_field = self.cleaned_data.get(ATTR_DATE_CONSTRAINT_FIELD)  # type: DocumentField
        date_constraint_days = self.cleaned_data.get(ATTR_DATE_CONSTRAINT_DAYS)  # type: int
        errors = DocumentSimilarityConfig.validate(dst_field, date_constraint_field, date_constraint_days)
        if errors:
            for attr, err in errors:
                self.add_error(attr, err)


class SimilarDocumentsFieldConfigAdmin(admin.ModelAdmin):
    list_display = ('pk', 'dst_field_code', 'similarity_threshold')
    search_fields = ('pk', 'dst_field__code', 'similarity_threshold')

    form = SimilarDocumentsFieldConfigAdminForm

    def get_search_results(self, request, queryset, search_term):
        qs, has_duplicates = super().get_search_results(request, queryset, search_term)
        return qs.select_related('dst_field'), has_duplicates

    @staticmethod
    def dst_field_code(obj):
        return obj.dst_field.code if obj.dst_field else None


admin.site.register(DocumentSimilarityConfig, SimilarDocumentsFieldConfigAdmin)
