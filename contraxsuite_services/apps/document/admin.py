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
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

# Project imports
from apps.document.models import (
    Document, DocumentProperty, DocumentRelation, DocumentNote,
    TextUnit, TextUnitProperty, TextUnitNote, TextUnitTag)

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.5/LICENSE"
__version__ = "1.0.6"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'document_type', 'source_type', 'paragraphs', 'sentences')
    search_fields = ['document_type', 'name']


class DocumentPropertyAdmin(admin.ModelAdmin):
    list_display = ('document', 'key', 'value')
    search_fields = ['document__name', 'key', 'value']


class TextUnitPropertyAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text_unit', 'key', 'value')
    search_fields = ['key', 'value']


class DocumentRelationAdmin(admin.ModelAdmin):
    list_display = ('document_a', 'document_b', 'relation_type')
    search_fields = ['document_a__name', 'document_a__name', 'relation_type']


class TextUnitAdmin(admin.ModelAdmin):
    list_display = ('document', 'unit_type', 'language')
    search_fields = ('document__name', 'document__name', 'unit_type', 'language')


class TextUnitTagAdmin(admin.ModelAdmin):
    list_display = ('text_unit', 'tag')
    search_fields = ('text_unit__unit_type', 'tag')


class TextUnitNoteAdmin(SimpleHistoryAdmin):
    list_display = ('text_unit', 'timestamp')
    search_fields = ('text_unit__unit_type', 'timestamp', 'note')


class DocumentNoteAdmin(SimpleHistoryAdmin):
    list_display = ('document', 'timestamp')
    search_fields = ('document__name', 'timestamp', 'note')


admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentRelation, DocumentRelationAdmin)
admin.site.register(DocumentProperty, DocumentPropertyAdmin)
admin.site.register(TextUnitProperty, TextUnitPropertyAdmin)
admin.site.register(TextUnit, TextUnitAdmin)
admin.site.register(TextUnitTag, TextUnitTagAdmin)
admin.site.register(TextUnitNote, TextUnitNoteAdmin)
admin.site.register(DocumentNote, DocumentNoteAdmin)
