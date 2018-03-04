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

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.5/LICENSE"
__version__ = "1.0.7"
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
