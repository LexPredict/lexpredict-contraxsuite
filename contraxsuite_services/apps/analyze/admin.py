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

from django.contrib import admin
from django.db.models import F

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from apps.analyze.models import (
    DocumentCluster, DocumentSimilarity, PartySimilarity,
    DocumentClassification, DocumentClassifier, DocumentClassifierSuggestion,
    TextUnitClassification, TextUnitClassifier, TextUnitClassifierSuggestion,
    TextUnitSimilarity, TextUnitCluster,
    DocumentTransformer, TextUnitTransformer, DocumentVector, TextUnitVector)


class DocumentClusterAdmin(admin.ModelAdmin):
    list_display = ('cluster_id', 'name', 'self_name', 'cluster_by', 'using')
    search_fields = ('name', 'self_name')


class TextUnitClusterAdmin(DocumentClusterAdmin):
    raw_id_fields = ('text_units',)


class DocumentSimilarityAdmin(admin.ModelAdmin):
    list_display = ('document_a', 'document_b', 'similarity')
    search_fields = ('document_a__name', 'document_b__name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('document_a', 'document_b') \
            .only('document_a__name', 'document_b__name', 'similarity')
        return qs


class PartySimilarityAdmin(admin.ModelAdmin):
    list_display = ('party_a', 'party_b', 'similarity')
    search_fields = ('party_a__name', 'party_b__name')


class TextUnitSimilarityAdmin(admin.ModelAdmin):
    list_display = ('similarity',
                    'document_a_name', 'text_unit_a_id',
                    'document_b_name', 'text_unit_b_id')
    search_fields = ('document_a_name', 'document_b_name',
                     'text_unit_a_id__exact', 'text_unit_b_id__exact')
    raw_id_fields = ('text_unit_a', 'text_unit_b')

    @staticmethod
    def document_a_name(obj):
        return obj.document_a_name

    @staticmethod
    def document_b_name(obj):
        return obj.document_b_name

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(document_a_name=F('text_unit_a__document__name'),
                         document_b_name=F('text_unit_b__document__name'))
        return qs

    def get_search_fields(self, request):
        q = request.GET.get('q')
        if q and q.isdigit():
            return 'text_unit_a_id__exact', 'text_unit_b_id__exact'
        return 'document_a_name', 'document_b_name'


class DocumentClassificationAdmin(admin.ModelAdmin):
    list_display = ('document_id', 'document', 'class_name', 'class_value')
    search_fields = ('document__name', 'class_name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('document') \
            .only('document_id', 'document__name', 'class_name', 'class_value')
        return qs


class DocumentClassifierAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'class_name')
    search_fields = ('name', 'version', 'class_name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.only('name', 'version', 'class_name')
        return qs


class DocumentClassifierSuggestionAdmin(admin.ModelAdmin):
    list_display = ('classifier_id', 'document_id', 'classifier_run', 'classifier_confidence', 'class_name')
    search_fields = ('classifier__name', 'classifier__version', 'classifier_run', 'classifier_id',
                     'classifier_confidence', 'class_name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('classifier', 'document') \
            .only('classifier_id', 'classifier__name', 'document_id',
                  'classifier_run', 'classifier_confidence', 'class_name')
        return qs


class TextUnitClassificationAdmin(admin.ModelAdmin):
    list_display = ('text_unit_id', 'class_name', 'class_value')
    search_fields = ('text_unit__unit_type', 'class_name')
    raw_id_fields = ('text_unit',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('text_unit') \
            .only('text_unit_id', 'class_name', 'class_value')
        return qs


class TextUnitClassifierAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'class_name')
    search_fields = ('name', 'version', 'class_name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.only('name', 'version', 'class_name')
        return qs


class TextUnitClassifierSuggestionAdmin(admin.ModelAdmin):
    list_display = ('classifier_id', 'text_unit_id', 'classifier_run', 'classifier_confidence', 'class_name')
    search_fields = ('classifier__name', 'classifier__version', 'classifier_run', 'classifier_id',
                     'classifier_confidence', 'class_name')
    raw_id_fields = ('text_unit',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('classifier', 'text_unit') \
            .only('classifier_id', 'classifier__name', 'text_unit_id',
                  'classifier_run', 'classifier_confidence', 'class_name')
        return qs


class DocumentTransformerAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'is_active')
    search_fields = ('name', 'version', 'vector_name')


class TextUnitTransformerAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'text_unit_type', 'is_active')
    search_fields = ('name', 'version', 'vector_name', 'text_unit_type')


class DocumentVectorAdmin(admin.ModelAdmin):
    list_display = ('vector_name', 'transformer_name', 'document', 'project', 'timestamp')
    search_fields = ('vector_name', 'transformer__name', 'document__name')

    @staticmethod
    def transformer_name(obj):
        return obj.transformer.name

    @staticmethod
    def project(obj):
        return obj.document.project.name


class TextUnitVectorAdmin(admin.ModelAdmin):
    list_display = ('vector_name', 'transformer_name', 'text_unit', 'document', 'project', 'timestamp')
    search_fields = ('vector_name', 'text_unit__document__name', 'text_unit__document__project__name')
    raw_id_fields = ('text_unit',)

    @staticmethod
    def transformer_name(obj):
        return obj.transformer.name

    @staticmethod
    def document(obj):
        return obj.text_unit.document.name

    @staticmethod
    def project(obj):
        return obj.text_unit.document.project.name


admin.site.register(DocumentCluster, DocumentClusterAdmin)
admin.site.register(TextUnitCluster, TextUnitClusterAdmin)
admin.site.register(DocumentSimilarity, DocumentSimilarityAdmin)
admin.site.register(TextUnitSimilarity, TextUnitSimilarityAdmin)
admin.site.register(PartySimilarity, PartySimilarityAdmin)
admin.site.register(DocumentClassification, DocumentClassificationAdmin)
admin.site.register(DocumentClassifier, DocumentClassifierAdmin)
admin.site.register(DocumentClassifierSuggestion, DocumentClassifierSuggestionAdmin)
admin.site.register(TextUnitClassification, TextUnitClassificationAdmin)
admin.site.register(TextUnitClassifier, TextUnitClassifierAdmin)
admin.site.register(TextUnitClassifierSuggestion, TextUnitClassifierSuggestionAdmin)
admin.site.register(DocumentTransformer, DocumentTransformerAdmin)
admin.site.register(TextUnitTransformer, TextUnitTransformerAdmin)
admin.site.register(DocumentVector, DocumentVectorAdmin)
admin.site.register(TextUnitVector, TextUnitVectorAdmin)
