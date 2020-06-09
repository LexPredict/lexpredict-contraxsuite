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

import datetime

import dataclasses
from django.db import transaction
from django.db.models import Subquery
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.mixins import SimpleRelationSerializer
from apps.document.api.v1 import BaseDocumentSerializer, DocumentNoteDetailSerializer, Document, DocumentField
from apps.document.constants import DocumentSystemField
from apps.document.repository.document_field_repository import DocumentFieldRepository
from apps.document.repository.dto import FieldValueDTO
from apps.document.tasks import plan_process_document_changed

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DocumentWithFieldsDTOSerializer(BaseDocumentSerializer):
    """
    Serializer for document review page with detailed document field values
    """
    field_repo = DocumentFieldRepository()

    field_values = serializers.SerializerMethodField()
    notes = DocumentNoteDetailSerializer(source='documentnote_set', many=True)
    prev_id = serializers.SerializerMethodField()
    next_id = serializers.SerializerMethodField()
    sections = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['pk', 'name', 'document_type', 'file_size',
                  'status', 'status_data', 'available_statuses_data',
                  'assignee', 'assign_date', 'assignee_data', 'available_assignees_data',
                  'description', 'title', 'full_text', 'notes',
                  'field_values',
                  'prev_id', 'next_id', 'sections', 'cluster_id']

    def get_neighbours(self, document, use_saved_filter=True):
        prev_id = next_id = None
        user = self.context['request'].user
        project = document.project
        from apps.rawdb.api.v1 import DocumentsAPIView

        ids = DocumentsAPIView.simulate_get(user, project, use_saved_filter=use_saved_filter)

        if document.pk in ids:
            pos = ids.index(document.pk)
        else:
            return self.get_neighbours(document, use_saved_filter=False)

        prev_ids = ids[:pos]
        if prev_ids:
            prev_id = prev_ids[-1]
        next_ids = ids[pos + 1:]
        if next_ids:
            next_id = next_ids[0]
        return prev_id, next_id

    def get_prev_id(self, obj):
        return self.get_neighbours(obj)[0]

    def get_next_id(self, obj):
        return self.get_neighbours(obj)[1]

    def get_sections(self, obj):
        if isinstance(obj.metadata, dict) and 'sections' in obj.metadata:
            return obj.metadata['sections']

    def get_field_values(self, doc: Document):
        fvals = self.field_repo.get_document_field_val_dtos(doc_id=doc.pk)
        for code in fvals:
            fvals[code] = dataclasses.asdict(fvals[code])
        return fvals

    def update(self, instance: Document, validated_data):
        with transaction.atomic():
            system_fields_changed = list()

            new_status = validated_data.get('status')
            if new_status is not None and new_status.pk != instance.status_id:
                is_active = instance.status and instance.status.is_active
                if new_status.is_active != is_active:
                    field_ids = self.field_repo.get_doc_field_ids_with_values(instance.pk)
                    DocumentField.objects \
                        .filter(document_type_id=instance.document_type_id, pk__in=Subquery(field_ids)) \
                        .update(dirty=True)
                system_fields_changed.append(DocumentSystemField.status.value)

            user = self.context['request'].user  # type: User
            new_assignee = validated_data.get('assignee')
            prev_assignee = instance.assignee
            if new_assignee is None and prev_assignee is not None:
                validated_data['assign_date'] = None
                system_fields_changed.append(DocumentSystemField.assignee.value)
            elif new_assignee is not None and (prev_assignee is None or new_assignee.pk != prev_assignee.pk):
                validated_data['assign_date'] = datetime.datetime.now(tz=user.get_time_zone())
                system_fields_changed.append(DocumentSystemField.assignee.value)

            res = super().update(instance, validated_data)

            plan_process_document_changed(doc_id=instance.pk,
                                          system_fields_changed=system_fields_changed,
                                          generic_fields_changed=False,
                                          user_fields_changed=False,
                                          changed_by_user_id=user.pk)
            return res


class FieldValueDTOSerializer(SimpleRelationSerializer):
    class Meta:
        model = FieldValueDTO
        fields = ['field_value', 'annotations']


class FieldValueViewSet(viewsets.ModelViewSet):
    """
    list: Annotation (Document Field Value) List
    retrieve: Retrieve Annotation (Document Field Value)
    create: Create Annotation (Document Field Value)
    update: Update Annotation (Document Field Value)
    delete: Delete Annotation (Document Field Value)
    """
    field_repo = DocumentFieldRepository()
    queryset = field_repo.get_all_docfieldvalues()
    serializer_class = FieldValueDTOSerializer
    http_method_names = ['put', 'patch']

    @action(detail=True, methods=['patch'])
    def patch_fields(self, request):
        """
        http.patch
        {
          "field_code1": { "field_value": ....,
                           "annotations": [ {"location_start": ...,
                                             "location_end": ....,
                                             "annotation_value": ....}]
                         },
        }
        """
        res = self.field_repo.update_field_values(request.data)
        return Response(res)

    def update(self, request, pk=None):
        # $http.put()
        res = self.field_repo.update_field_values(request.data)
        return Response(res)
