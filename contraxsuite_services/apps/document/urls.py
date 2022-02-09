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

# Future imports
from __future__ import absolute_import, unicode_literals

# Django imports
from django.conf.urls import url

# Project imports
from django.urls import reverse_lazy
from django.views.generic import RedirectView

from apps.common.utils import create_standard_urls
from apps.document import views
from apps.document.models import Document, DocumentProperty, DocumentRelation, DocumentNote, DocumentTag, \
    TextUnit, TextUnitProperty, TextUnitNote, TextUnitTag

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# URL pattern list
urlpatterns = []


def register(model, view_types):
    """
    Convenience method for global URL registration.
    :param model:
    :param view_types:
    :return:
    """
    global urlpatterns
    urlpatterns += create_standard_urls(model, views, view_types)


# Register views through helper method
register(Document, view_types=('list', 'detail'))
register(DocumentProperty, view_types=('list', 'update', 'delete'))
register(DocumentRelation, view_types=('list',))
register(DocumentTag, view_types=('list', 'delete'))
register(TextUnit, view_types=('list', 'detail'))
register(TextUnitProperty, view_types=('list', 'delete'))
register(TextUnitNote, view_types=('list', 'delete'))
register(DocumentNote, view_types=('list', 'delete'))
register(TextUnitTag, view_types=('list', 'delete'))

# Add hard-coded URL mappings
urlpatterns += [
    url(
        r'^search/$',
        views.search,
        name='search'
    ),
    url(
        r'^stats/$',
        views.view_stats,
        name='stats'
    ),
    url(
        r'^document/(?P<pk>\d+)/actions/$',
        views.DocumentActionListView.as_view(),
        name='document-actions'
    ),
    url(
        r'^text-unit-by-language/list/$',
        views.TextUnitByLangListView.as_view(),
        name='text-unit-by-lang-list'
    ),
    url(
        r'^document-property/(?:(?P<pk>\d+)/)?add/$',
        views.DocumentPropertyCreateView.as_view(),
        name='document-property-add'
    ),
    url(
        r'^document/(?P<pk>\d+)/source/$',
        views.DocumentSourceView.as_view(),
        name='document-source'
    ),
    url(
        r'^document/(?P<pk>\d+)/show/$',
        views.show_document,
        name='show-document'
    ),
    url(
        r'^document/(?P<pk>\d+)/enhanced-view/$',
        views.DocumentEnhancedView.as_view(),
        name='document-enhanced-view'
    ),

    url(
        r'^complete/document/description/$',
        views.TypeaheadDocumentDescription.as_view(),
        name='document-description-complete',
    ),
    url(
        r'^complete/document/name/$',
        views.TypeaheadDocumentName.as_view(),
        name='document-name-complete',
    ),
    url(
        r'^complete/document-property/key/$',
        views.TypeaheadDocumentPropertyKey.as_view(),
        name='document-property-key-complete',
    ),
    url(
        r'^complete/text-unit-tag/tag/$',
        views.TypeaheadTextUnitTag.as_view(),
        name='text-unit-tag-complete',
    ),

    url(
        r'^submit/document-tag/$',
        views.SubmitDocumentTagView.as_view(),
        name='document-tag-submit',
    ),
    url(
        r'^submit/cluster-documents-tag/$',
        views.SubmitClusterDocumentsTagView.as_view(),
        name='cluster-documents-tag-submit',
    ),
    url(
        r'^submit/cluster-documents-property/$',
        views.SubmitClusterDocumentsPropertyView.as_view(),
        name='cluster-documents-property-submit',
    ),
    url(
        r'^submit/cluster-documents-language/$',
        views.SubmitClusterDocumentsLanguageView.as_view(),
        name='cluster-documents-language-submit',
    ),

    url(
        r'^submit/text-unit-tag/$',
        views.SubmitTextUnitTagView.as_view(),
        name='text-unit-tag-submit',
    ),
    url(
        r'^submit/document-property/$',
        views.SubmitDocumentPropertyView.as_view(),
        name='document-property-submit',
    ),
    url(
        r'^submit/text-unit-property/$',
        views.SubmitTextUnitPropertyView.as_view(),
        name='text-unit-property-submit',
    ),
    url(
        r'^submit/note/$',
        views.SubmitNoteView.as_view(),
        name='note-submit',
    ),
    url(
        r'^detect-field-values/$',
        views.DetectFieldValuesTaskView.as_view(),
        name='detect-field-values',
    ),

    url(
        r'^train-document-field-detector-model/$',
        views.TrainDocumentFieldDetectorModelTaskView.as_view(),
        name='train-document-field-detector-model',
    ),
    url(
        r'^find-broken-document-field-values/$',
        views.FindBrokenDocumentFieldValuesTaskView.as_view(),
        name='find-broken-document-field-values',
    ),
    url(
        r'^fix-document-field-codes/$',
        views.FixDocumentFieldCodesTaskView.as_view(),
        name='fix-document-field-codes',
    ),
    url(
        r'^train-and-test/$',
        views.TrainAndTestTaskView.as_view(),
        name='train-and-test',
    ),
    url(
        r'^load-document-with-fields/$',
        views.LoadDocumentWithFieldsView.as_view(),
        name='load-document-with-fields',
    ),
    url(
        r'^import-simple-field-detection-config/$',
        views.ImportCSVFieldDetectionConfigView.as_view(),
        name='import-simple-field-detection-config',
    ),
    url(
        r'^export-document-type/$',
        views.ExportDocumentTypeView.as_view(),
        name='export-document-type',
    ),
    url(
        r'^export-documents/$',
        views.ExportDocumentsView.as_view(),
        name='export-documents',
    ),
    url(
        r'^import-document-type/$',
        views.ImportDocumentTypeView.as_view(),
        name='import-document-type',
    ),
    url(
        r'^import-documents/$',
        views.ImportDocumentsView.as_view(),
        name='import-documents',
    ),
    url(
        r'^indentify-contracts/$',
        views.IdentifyContractsView.as_view(),
        name='indentify-contracts',
    ),
    url(
        r'^document-query-help/$',
        views.DocumentQueryView.as_view(),
        name='document-query-help',
    ),
    url(
        r'^textunit-query-help/$',
        views.TextUnitQueryView.as_view(),
        name='textunit-query-help',
    ),
    url(r'^document/list/introspect/$',
        views.DjangoQLDocumentIntrospectView.as_view(),
        name='introspect'
    ),
    url(r'^text-unit/list/introspect/$',
        views.DjangoQLTextUnitIntrospectView.as_view(),
        name='introspect'
    ),
    url(r'^document/list/djangoql-syntax/$',
        RedirectView.as_view(
            url=reverse_lazy('admin:djangoql_syntax_help'), permanent=False)),
    url(r'^text-unit/list/djangoql-syntax/$',
        RedirectView.as_view(
            url=reverse_lazy('admin:djangoql_syntax_help'), permanent=False))
]
