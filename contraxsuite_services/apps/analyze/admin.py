from django.contrib import admin

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.1/LICENSE"
__version__ = "1.0.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from apps.analyze.models import (
    DocumentCluster, DocumentSimilarity, PartySimilarity,
    TextUnitClassification, TextUnitClassifier, TextUnitClassifierSuggestion,
    TextUnitSimilarity, TextUnitCluster)


class DocumentClusterAdmin(admin.ModelAdmin):
    list_display = ('cluster_id', 'name', 'self_name', 'cluster_by', 'using')
    search_fields = ('name', 'self_name')


class TextUnitClusterAdmin(DocumentClusterAdmin):
    pass


class DocumentSimilarityAdmin(admin.ModelAdmin):
    list_display = ('document_a', 'document_b', 'similarity')
    search_fields = ('document_a__name', 'document_b__name')


class PartySimilarityAdmin(admin.ModelAdmin):
    list_display = ('party_a', 'party_b', 'similarity')
    search_fields = ('party_a__name', 'party_b__name')


class TextUnitSimilarityAdmin(admin.ModelAdmin):
    list_display = ('text_unit_a', 'text_unit_b', 'similarity')
    search_fields = ('text_unit_a', 'text_unit_b')


class TextUnitClassificationAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'class_name')
    search_fields = ('text_unit__unit_type', 'class_name')


class TextUnitClassifierAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'class_name')
    search_fields = ('name', 'version', 'class_name')


class TextUnitClassifierSuggestionAdmin(admin.ModelAdmin):
    list_display = ('classifier', 'classifier_run', 'classifier_confidence', 'class_name')
    search_fields = ('classifier__name', 'classifier__version', 'classifier_run',
                     'classifier_confidence', 'class_name')


admin.site.register(DocumentCluster, DocumentClusterAdmin)
admin.site.register(TextUnitCluster, TextUnitClusterAdmin)
admin.site.register(DocumentSimilarity, DocumentSimilarityAdmin)
admin.site.register(TextUnitSimilarity, TextUnitSimilarityAdmin)
admin.site.register(PartySimilarity, PartySimilarityAdmin)
admin.site.register(TextUnitClassification, TextUnitClassificationAdmin)
admin.site.register(TextUnitClassifier, TextUnitClassifierAdmin)
admin.site.register(TextUnitClassifierSuggestion, TextUnitClassifierSuggestionAdmin)
