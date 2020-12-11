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

from typing import Tuple, Dict

from rest_framework import views
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.document.api.v1 import cache_and_detect_field_values, render_error_json
from apps.document.models import Document, DocumentField
from apps.document.repository.document_field_repository import DocumentFieldRepository
from apps.document.repository.document_repository import DocumentRepository
from apps.document.repository.dto import FieldValueDTO

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class FieldValueView(views.APIView):

    @action(detail=False, methods=['get'])
    def list(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @action(detail=False, methods=['put'])
    def annotate(self, request):
        try:
            doc_id = request.data['document']
            field_id = request.data['field']
            field_val = request.data.get('value')

            doc, field, res = do_save_document_field_value(field_val, doc_id, field_id, request.user)
            cache_and_detect_field_values(doc,
                                          user=request.user,
                                          updated_fields={field})
        except Exception as e:
            res = render_error_json(None, e)

        return Response(res)


def do_save_document_field_value(
        field_val: FieldValueDTO,
        document_id: int,
        field_id: str,
        user) -> \
        Tuple[Document, DocumentField, Dict]:
    field_repo = DocumentFieldRepository()

    document = DocumentRepository().get_document_by_id(document_id)
    field = field_repo.get_document_field_by_id(field_id)
    field_val, field_ants = field_repo.update_field_value_with_dto(document=document,
                                                                   field=field,
                                                                   field_value_dto=field_val,
                                                                   user=user)

    annotation = field_ants[0]

    field_value = {
        'document': document.pk,
        'document_name': document.name,
        'field': field.uid,
        'field_name': field.code,
        'value': field_val.value,
        'pk': annotation.pk,
        'project': document.project.name,
        'location_start': annotation.location_start,
        'location_end': annotation.location_end,
        'location_text': annotation.location_text,
        'modified_by': annotation.modified_by.pk,
        'modified_date': annotation.modified_date
    }

    # return field_repo.save_posted_field_value(request_data, user)
    return document, field, field_value
