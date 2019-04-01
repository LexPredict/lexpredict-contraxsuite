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
from django.contrib import admin
from django.forms import ModelForm

from apps.document.models import DocumentType
from apps.project.models import Project
# Project imports
from .models import SavedFilter

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.0/LICENSE"
__version__ = "1.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class SavedFiltersAdminForm(ModelForm):
    def clean(self):
        project = self.cleaned_data['project']  # type: Project
        document_type = self.cleaned_data['document_type']  # type: DocumentType

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
        return obj.user.get_full_name() if obj.user else None


admin.site.register(SavedFilter, SavedFiltersAdmin)
