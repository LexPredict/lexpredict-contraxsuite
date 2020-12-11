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

from rest_framework import serializers
from apps.common.schemas import CustomAutoSchema, JqFiltersListViewSchema, ObjectResponseSchema,\
    ObjectItemsResponseSchema, ObjectToItemResponseMixin, json_ct
from apps.document.models import Document, DocumentField

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DocumentNoteViewSetSchema(JqFiltersListViewSchema):
    get_parameters = [
        {'name': 'project_id',
         'in': 'query',
         'required': False,
         'description': 'Filter by project id',
         'schema': {'type': 'string'}},
        {'name': 'document_id',
         'in': 'query',
         'required': False,
         'description': 'Filter by document id',
         'schema': {'type': 'string'}},
        {'name': 'force',
         'in': 'query',
         'required': False,
         'description': 'For deleted documents as well',
         'schema': {'type': 'boolean'}},
        {'name': 'export_to',
         'in': 'query',
         'required': False,
         'description': 'Export data',
         'schema': {'type': 'boolean'}}
    ]

    def get_operation(self, path, method):
        op = super().get_operation(path, method)
        if method == 'GET' and self.view.action == 'list':
            op['parameters'].extend(self.get_parameters)
        return op


class DocumentViewSetSchema(JqFiltersListViewSchema):
    get_parameters = [
        {'name': 'cluster_id',
         'in': 'query',
         'required': False,
         'description': 'Cluster id to filter by',
         'schema': {
             'type': 'integer'}
         },
        {'name': 'q',
         'in': 'query',
         'required': False,
         'description': 'Search parameters for djangoQL',
         'schema': {
             'type': 'string'}
         }
    ]

    def get_operation(self, path, method):
        op = super().get_operation(path, method)
        if method == 'GET' and self.view.action in ('list', 'for_user'):
            op['parameters'].extend(self.get_parameters)
        return op

    # TODO: "oneOf" instruction seems still isn't presented by python openapi generator,
    # TODO: if fails with AttributeError: module 'openapi_client.models' has no attribute 'OneOfDocumentsForUserDocumentDetailDjangoQL'
    # TODO: so move "q" in separate @action
    # def get_components(self, path, method):
    #     res = super().get_components(path, method)
    #     from apps.document.api.v1 import DocumentDetailDjangoQLSerializer
    #     res['DocumentDetailDjangoQL'] = self.map_serializer(DocumentDetailDjangoQLSerializer())
    #     return res
    #
    # def get_responses(self, path, method):
    #     res = super().get_responses(path, method)
    #     if method == 'GET' and self.view.action in ('list',):
    #         def_schema = res['200']['content'][json_ct]['schema']['items']
    #         res['200']['content'][json_ct]['schema']['items'] = {
    #             'oneOf': [def_schema, {'$ref': '#/components/schemas/DocumentDetailDjangoQL'}]
    #         }
    #     return res


class DocumentsForUserSerializer(serializers.ModelSerializer):
    """
    Serializer for user documents
    """
    status_name = serializers.CharField()

    class Meta:
        model = Document
        fields = ['pk', 'name', 'document_type', 'project', 'status_name']


class DocumentsForUserResponseSerializer(serializers.Serializer):
    total_documents = serializers.IntegerField()
    data = serializers.ListField(child=DocumentsForUserSerializer())


class DocumentForUserSchema(ObjectResponseSchema):
    response_serializer = DocumentsForUserResponseSerializer()

    def get_responses(self, path, method):
        res = super().get_responses(path, method)
        res['200']['content'][json_ct]['schema'] = {'$ref': 'DocumentsForUserResponse'}
        return res


class DocumentDefinitionsSchema(ObjectToItemResponseMixin, CustomAutoSchema):

    class DocumentDefinitionsSerializer(serializers.Serializer):
        definition = serializers.CharField()
        matches = serializers.ListField(child=serializers.DictField())
        descriptions = serializers.ListField(child=serializers.DictField())

    response_serializer = DocumentDefinitionsSerializer()


class DocumentFullTextSchema(CustomAutoSchema):

    def get_responses(self, path, method):
        res = super().get_responses(path, method)
        res['200']['content'][json_ct]['schema'] = {'type': 'string'}
        return res


class DocumentShowSchema(CustomAutoSchema):
    parameters = [
        {'name': 'alt',
         'in': 'query',
         'required': False,
         'description': 'Get alternative document file if exists',
         'schema': {
             'type': 'boolean'}
         }
    ]

    def get_responses(self, path, method):
        return {
          '200': {
            'content': {
              'application/json': {
                'schema': {
                  'type': 'string', 'format': 'binary'
                }
              }
            },
            'description': ''
          }
        }


class DocumentDownloadZipSchema(CustomAutoSchema):

    class DocumentDownloadZipResponseSerializer(serializers.Serializer):
        task_id = serializers.UUIDField(required=True)
        detail = serializers.CharField(required=True)

    response_serializer = DocumentDownloadZipResponseSerializer()
    parameters = [
        {'name': 'document_ids',
         'in': 'query',
         'required': False,
         'description': 'Filter by Document ids separated by commas',
         'schema': {
             'type': 'string'}
         },
        {'name': 'exclude_document_ids',
         'in': 'query',
         'required': False,
         'description': 'Exclude Document ids separated by commas',
         'schema': {
             'type': 'string'}
         }
    ]

    def get_responses(self, path, method):
        responses = super().get_responses(path, method)
        responses['200']['content']['application/zip'] = {'schema': {'type': 'string', 'format': 'binary'}}
        responses['404'] = {
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'detail': {'type': 'string'}
                        },
                        'required': ['detail']}}}}
        return responses


class MarkUnmarkForDeleteDocumentsSchema(CustomAutoSchema):

    class MarkUnmarkForDeleteDocumentsRequestSerializer(serializers.Serializer):
        all = serializers.BooleanField(required=False)
        project_id = serializers.IntegerField()
        document_ids = serializers.ListField(required=False, child=serializers.IntegerField())

    class MarkUnmarkForDeleteDocumentsResponseSerializer(serializers.Serializer):
        count_deleted = serializers.IntegerField()

    request_serializer = MarkUnmarkForDeleteDocumentsRequestSerializer()
    response_serializer = MarkUnmarkForDeleteDocumentsResponseSerializer()


class TextUnitViewSetSchema(CustomAutoSchema):
    parameters = [
        {'name': 'q',
         'in': 'query',
         'required': False,
         'description': 'Search parameters for djangoQL',
         'schema': {
             'type': 'string'}
         },
    ]


class DocumentTypeImportSchema(CustomAutoSchema):

    class DocumentTypeImportRequestSerializer(serializers.Serializer):
        file = serializers.FileField(required=True)
        update_cache = serializers.BooleanField(required=False)
        action = serializers.ChoiceField(
            required=False, choices=['validate',
                                     'validate|import',
                                     'import|auto_fix|retain_missing_objects',
                                     'import|auto_fix|remove_missing_objects'])
        source_version = serializers.CharField(required=False)

    class DocumentTypeImportResponseSerializer(serializers.Serializer):
        task_id = serializers.UUIDField()

    request_serializer = DocumentTypeImportRequestSerializer()
    response_serializer = DocumentTypeImportResponseSerializer()


class DocumentTypeExportSchema(CustomAutoSchema):

    parameters = [
        {'name': 'target_version',
         'in': 'query',
         'required': False,
         'description': 'Version number',
         'schema': {
             'type': 'string'}
         },
    ]

    def get_responses(self, path, method):
        return {'200': {'content': {
            'application/json': {'schema': {'type': 'string', 'format': 'binary'}}}}}


class CloneDocumentTypeSchema(CustomAutoSchema):

    class CloneDocumentTypeRequestSerializer(serializers.Serializer):
        code = serializers.CharField(required=True)
        title = serializers.CharField(required=True)

    request_serializer = CloneDocumentTypeRequestSerializer()


class CloneDocumentFieldSchema(CustomAutoSchema):

    class CloneDocumentFieldRequestSerializer(serializers.Serializer):
        code = serializers.CharField(required=True)
        document_type = serializers.UUIDField(required=True)

    request_serializer = CloneDocumentFieldRequestSerializer()


class CheckDocumentFieldFormulaSchema(ObjectResponseSchema):

    class CheckDocumentFieldFormulaRequestSerializer(serializers.Serializer):
        formula = serializers.CharField(required=False)
        hide_until_python = serializers.CharField(required=False)

    request_serializer = CheckDocumentFieldFormulaRequestSerializer()

    def get_responses(self, path, method):
        resp = super().get_responses(path, method)
        resp['200'] = resp['201']
        del resp['201']
        resp['200']['content'][json_ct]['schema'] = self.object_schema
        return resp


class CheckNewDocumentFieldFormulaSchema(CustomAutoSchema):

    class CheckNewDocumentFieldFormulaRequestSerializer(serializers.Serializer):
        formula = serializers.CharField(required=False)
        hide_until_python = serializers.CharField(required=False)
        field_type = serializers.CharField(required=False)
        document_type = serializers.CharField(required=False)
        depends_on_fields = serializers.ListField(child=serializers.UUIDField())

    request_serializer = CheckNewDocumentFieldFormulaRequestSerializer()


class AnnotationSuggestSchema(ObjectResponseSchema):

    class AnnotationSuggestRequestSerializer(serializers.Serializer):
        field = serializers.UUIDField()
        document = serializers.IntegerField()
        quite = serializers.CharField()

    request_serializer = AnnotationSuggestRequestSerializer()


class AnnotationBatchSchema(CustomAutoSchema):

    class AnnotationBatchRequestSerializer(serializers.Serializer):
        class RequestDataSerialiser(serializers.Serializer):
            document = serializers.IntegerField()
            field = serializers.UUIDField()
            location_start = serializers.IntegerField()
            location_end = serializers.IntegerField()
            value = serializers.CharField()

        operation_uid = serializers.UUIDField()
        action = serializers.ChoiceField(choices=['delete', 'save'])
        id = serializers.IntegerField()
        data = serializers.DictField(child=RequestDataSerialiser())

    class AnnotationBatchResponseSerializer(serializers.Serializer):
        operation_uid = serializers.UUIDField()
        status = serializers.CharField()
        data = serializers.DictField()

    request_serializer = AnnotationBatchRequestSerializer()
    response_serializer = AnnotationBatchResponseSerializer()

    def get_request_body(self, path, method):
        req = super().get_request_body(path, method)
        return {
            'content': {
                ct: {
                    'schema': {
                        'type': 'array',
                        'items': req['content'][ct]['schema']}
                } for ct in self.request_media_types
            }
        }

    def get_responses(self, path, method):
        resp = super().get_responses(path, method)
        resp['200']['content']['application/json']['schema'] = {
                'type': 'array',
                'items': resp['200']['content']['application/json']['schema']}
        return resp


class DocumentFieldStatsResponseSerializer(serializers.Serializer):
    code = serializers.CharField()
    title = serializers.CharField()
    total = serializers.IntegerField()
    todo = serializers.IntegerField()
    sys_generated_confirm_correct = serializers.IntegerField()
    rejected = serializers.IntegerField()
    user_generated = serializers.IntegerField()
    deps_on_fields = serializers.ListField(child=serializers.CharField())
    # TODO: keep it for potential use later
    # user_generated_confirm_correct = serializers.IntegerField()


class DocumentFieldStatsSchema(ObjectToItemResponseMixin, CustomAutoSchema):
    parameters = [
        {'name': 'document_type_uid',
         'in': 'query',
         'required': False,
         'description': 'Filter by document type uid',
         'schema': {'type': 'string'}},
    ]
    response_serializer = DocumentFieldStatsResponseSerializer()
