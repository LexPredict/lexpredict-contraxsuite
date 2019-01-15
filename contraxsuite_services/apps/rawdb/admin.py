from django.contrib import admin

# Project imports
from .models import SavedFilter


class SavedFiltersAdmin(admin.ModelAdmin):
    list_display = ('pk', 'document_type_code', 'project_name',
                    'display_order', 'title', 'column_filters', 'order_by')
    search_fields = ('pk', 'document_type__code', 'project__name')

    @staticmethod
    def document_type_code(obj):
        return obj.document_type.code if obj.document_type else None

    @staticmethod
    def project_name(obj):
        return obj.project.name if obj.project else None


admin.site.register(SavedFilter, SavedFiltersAdmin)
