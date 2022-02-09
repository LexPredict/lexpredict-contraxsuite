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

from scipy.spatial.distance import _METRICS

from rest_framework import serializers
from apps.common.schemas import CustomAutoSchema, ObjectResponseSchema, \
    ObjectToItemResponseMixin, json_ct, string_content, object_content, binary_string_schema

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# --------------------------------------------
#            commons
# --------------------------------------------

class CountSuccessResponseSerializer(serializers.Serializer):
    success = serializers.IntegerField(required=False, allow_null=True)


response_404_details = {
    'content': {
        json_ct: {
            'schema': {
                'type': 'object',
                'properties': {
                    'details': {
                        'type': 'string'}},
                'required': ['details']}
        }
    },
    'description': ''}


class TaskIdResponseSerializer(serializers.Serializer):
    task_id = serializers.UUIDField()


# -------------------------------------------
#        end commons
# -------------------------------------------


class ProjectStatsSchema(CustomAutoSchema):
    parameters = [
        {'name': 'project_ids',
         'in': 'query',
         'required': False,
         'description': 'Project ids separated by commas',
         'schema': {'type': 'string'}}]

    def get_responses(self, path, method):
        resp = super().get_responses(path, method)
        item_schema = resp['200']['content'][json_ct]['schema']
        resp['200']['content'][json_ct]['schema'] = {'type': 'array', 'items': item_schema}
        return resp


class ProjectProgressSchema(CustomAutoSchema):

    class ProjectProgressResponseSerializer(serializers.Serializer):
        project_has_completed_sessions = serializers.BooleanField()
        user_uncompleted_session_progress = serializers.DictField(allow_null=True)
        other_uncompleted_session_progress = serializers.DictField(allow_null=True)
        clustering = serializers.CharField(required=False)
        require_clustering = serializers.BooleanField(required=False)

    response_serializer = ProjectProgressResponseSerializer()


class ProjectDocumentsAssigneesSchema(ObjectToItemResponseMixin, CustomAutoSchema):

    class ProjectDocumentsAssigneesResponseSerializer(serializers.Serializer):
        assignee_id = serializers.IntegerField()
        assignee_name = serializers.CharField()
        documents_count = serializers.IntegerField()
        document_ids = serializers.ListField(child=serializers.IntegerField())

    response_serializer = ProjectDocumentsAssigneesResponseSerializer()


class ProjectAnnotationsAssigneesSchema(ObjectToItemResponseMixin, CustomAutoSchema):

    class ProjectAnnotationsAssigneesResponseSerializer(serializers.Serializer):
        assignee_id = serializers.IntegerField()
        assignee_name = serializers.CharField()
        annotations_count = serializers.IntegerField()
        annotation_uids = serializers.ListField(child=serializers.UUIDField())

    response_serializer = ProjectAnnotationsAssigneesResponseSerializer()


class RecentProjectsSchema(ObjectToItemResponseMixin, ObjectResponseSchema):
    parameters = [
        {'name': 'n',
         'in': 'query',
         'required': False,
         'description': 'Max rows number',
         'schema': {'type': 'integer'}}]


class SendClusterToProjectSchema(CustomAutoSchema):

    class SendClusterToProjectRequestSerializer(serializers.Serializer):
        cluster_ids = serializers.ListField(child=serializers.IntegerField())
        project_id = serializers.IntegerField()

    request_serializer = SendClusterToProjectRequestSerializer()

    def get_responses(self, path, method):
        responses = super().get_responses(path, method)
        responses['200'] = string_content
        responses['400'] = string_content
        return responses


class CleanupProjectSchema(CustomAutoSchema):

    class CleanupProjectRequestSerializer(serializers.Serializer):
        delete = serializers.BooleanField(required=False)

    request_serializer = CleanupProjectRequestSerializer()

    def get_responses(self, path, method):
        responses = super().get_responses(path, method)
        responses['200'] = string_content
        return responses


class SelectProjectsSchema(CustomAutoSchema):

    class SelectProjectsRequestSerializer(serializers.Serializer):
        project_ids = serializers.ListField(child=serializers.IntegerField())

    class SelectProjectsResponseSerializer(serializers.Serializer):
        saved_filter_id = serializers.IntegerField()
        user_id = serializers.IntegerField()
        project_ids = serializers.ListField(child=serializers.IntegerField())
        show_warning = serializers.BooleanField()

    request_serializer = SelectProjectsRequestSerializer()
    response_serializer = SelectProjectsResponseSerializer()


class MarkUnmarkForDeleteProjectsSchema(CustomAutoSchema):

    class MarkUnmarkForDeleteProjectsRequestSerializer(serializers.Serializer):
        all = serializers.BooleanField(required=False)
        remove_all = serializers.BooleanField(required=False)
        exclude_document_ids = serializers.ListField(required=False,
                                                     child=serializers.IntegerField())

    class MarkUnmarkForDeleteProjectsReponseSerializer(serializers.Serializer):
        count_deleted = serializers.IntegerField()

    request_serializer = MarkUnmarkForDeleteProjectsRequestSerializer()
    response_serializer = MarkUnmarkForDeleteProjectsReponseSerializer()


class AssignProjectDocumentsSchema(CustomAutoSchema):

    class AssignProjectDocumentsRequestSerializer(serializers.Serializer):
        assignee_id = serializers.IntegerField(required=False, allow_null=True)
        all = serializers.BooleanField(required=False)
        document_ids = serializers.ListField(required=False, child=serializers.IntegerField())
        no_document_ids = serializers.ListField(required=False, child=serializers.IntegerField())

    request_serializer = AssignProjectDocumentsRequestSerializer()
    response_serializer = CountSuccessResponseSerializer()

    def get_responses(self, path, method):
        res = super().get_responses(path, method)
        res['200'] = dict(res['201'])
        del res['201']
        res['404'] = dict(res['200'])
        res['404'] = response_404_details
        return res


class AssignProjectDocumentSchema(CustomAutoSchema):

    class AssignProjectDocumentRequestSerializer(serializers.Serializer):
        assignee_id = serializers.IntegerField(required=False, allow_null=True)
        document_id = serializers.IntegerField(required=False, allow_null=True)

    request_serializer = AssignProjectDocumentRequestSerializer()
    response_serializer = CountSuccessResponseSerializer()

    def get_responses(self, path, method):
        res = super().get_responses(path, method)
        res['200'] = dict(res['201'])
        del res['201']
        res['404'] = dict(res['200'])
        res['404'] = response_404_details
        return res


class UpdateProjectDocumentsFieldsSchema(CustomAutoSchema):

    class UpdateProjectDocumentsFieldsRequestSerializer(serializers.Serializer):
        all = serializers.BooleanField(required=False)
        document_ids = serializers.ListField(required=False, child=serializers.IntegerField())
        no_document_ids = serializers.ListField(required=False, child=serializers.IntegerField())
        fields_data = serializers.DictField(required=True, child=serializers.CharField())
        on_existing_value = serializers.CharField(required=False)

    request_serializer = UpdateProjectDocumentsFieldsRequestSerializer()
    response_serializer = TaskIdResponseSerializer()

    def get_responses(self, path, method):
        res = super().get_responses(path, method)
        res['200'] = dict(res['201'])
        del res['201']
        res['404'] = dict(res['200'])
        res['404'] = response_404_details
        return res


class SetProjectDocumentsStatusSchema(CustomAutoSchema):

    class SetProjectDocumentsStatusRequestSerializer(serializers.Serializer):
        status_id = serializers.IntegerField(required=False, allow_null=True)
        all = serializers.BooleanField(required=False)
        document_ids = serializers.ListField(required=False, child=serializers.IntegerField())
        no_document_ids = serializers.ListField(required=False, child=serializers.IntegerField())

    request_serializer = SetProjectDocumentsStatusRequestSerializer()
    response_serializer = CountSuccessResponseSerializer()


class ClusterProjectSchema(CustomAutoSchema):

    class ClusterProjectRequestSerializer(serializers.Serializer):
        n_clusters = serializers.IntegerField()
        force = serializers.BooleanField(required=False)
        cluster_by = serializers.ChoiceField(choices=[
            'term', 'date', 'text', 'definition', 'duration', 'party',
            'geoentity', 'currency_name', 'currency_value'])
        method = serializers.ChoiceField(choices=['kmeans', 'minibatchkmeans', 'birch'])
        require_confirmation = serializers.BooleanField(required=False)

    class ClusterProjectResponseSerializer(serializers.Serializer):
        task_id = serializers.UUIDField()
        project_clustering_id = serializers.IntegerField()

    request_serializer = ClusterProjectRequestSerializer()
    response_serializer = ClusterProjectResponseSerializer()

    def get_responses(self, path, method):
        responses = super().get_responses(path, method)
        responses['400'] = string_content
        return responses


class ProjectClusteringStatusSchema(CustomAutoSchema):

    class ProjectClusteringStatusResponseSerializer(serializers.Serializer):
        document_clusters = serializers.ListField(child=serializers.DictField())
        project_clusters_documents_count = serializers.IntegerField()
        project_clusters_actions_count = serializers.IntegerField()
        status = serializers.CharField(allow_null=True)

    response_serializer = ProjectClusteringStatusResponseSerializer()
    parameters = [
        {'name': 'project_clustering_id',
         'in': 'query',
         'required': False,
         'description': 'Get by project_clustering_id',
         'schema': {
             'type': 'integer'}
         }
    ]

    def get_responses(self, path, method):
        responses = super().get_responses(path, method)
        responses['404'] = response_404_details
        return responses


class AssignProjectAnnotationsSchema(CustomAutoSchema):

    class AssignProjectAnnotationsRequestSerializer(serializers.Serializer):
        assignee_id = serializers.IntegerField(required=False, allow_null=True)
        all = serializers.BooleanField(required=False)
        annotation_ids = serializers.ListField(required=False, child=serializers.IntegerField())
        no_annotation_ids = serializers.ListField(required=False, child=serializers.IntegerField())

    request_serializer = AssignProjectAnnotationsRequestSerializer()
    response_serializer = CountSuccessResponseSerializer()

    def get_responses(self, path, method):
        responses = super().get_responses(path, method)
        responses['404'] = response_404_details
        return responses


class SetProjectAnnotationsStatusSchema(CustomAutoSchema):

    class SetProjectAnnotationsStatusRequestSerializer(serializers.Serializer):
        status_id = serializers.IntegerField(required=False, allow_null=True)
        all = serializers.BooleanField(required=False)
        annotation_ids = serializers.ListField(required=False, child=serializers.IntegerField())
        no_annotation_ids = serializers.ListField(required=False, child=serializers.IntegerField())

    class SetProjectAnnotationsStatusAsyncResponseSerializer(serializers.Serializer):
        task_id = serializers.UUIDField()
        annotations = serializers.IntegerField()

    request_serializer = SetProjectAnnotationsStatusRequestSerializer()
    response_serializer = CountSuccessResponseSerializer()

    def get_components(self, path, method):
        components = super().get_components(path, method)
        content = self.map_serializer(self.SetProjectAnnotationsStatusAsyncResponseSerializer())
        components['SetProjectAnnotationsStatusAsyncResponse'] = content
        return components

    def get_responses(self, path, method):
        resp = super().get_responses(path, method)
        resp['200'] = dict(resp['201'])
        del resp['201']
        def_schema = resp['200']['content'][json_ct]['schema']
        resp['200']['content'][json_ct]['schema'] = {
            'oneOf': [def_schema,
                      {'$ref': '#/components/schemas/SetProjectAnnotationsStatusAsyncResponse'}]}
        return resp


class DetectProjectFieldValuesSchema(CustomAutoSchema):

    class DetectProjectFieldValuesRequestSerializer(serializers.Serializer):
        do_not_update_modified = serializers.BooleanField(required=False)
        do_not_write = serializers.BooleanField(required=False)
        document_ids = serializers.ListField(required=False, child=serializers.IntegerField())

    request_serializer = DetectProjectFieldValuesRequestSerializer()
    response_serializer = TaskIdResponseSerializer()


class LocateItemsSchema(CustomAutoSchema):

    class LocateItemsRequestSerializer(serializers.Serializer):
        items_to_locate = serializers.ListField(required=True, child=serializers.CharField())
        project_id = serializers.IntegerField(required=True)
        delete_existing = serializers.BooleanField(required=False)
        search_in = serializers.ListField(required=False, child=serializers.CharField())
        selected_tags = serializers.ListField(required=False, child=serializers.CharField())

    request_serializer = LocateItemsRequestSerializer()
    response_serializer = TaskIdResponseSerializer()


class UploadSessionStatusSchema(ObjectResponseSchema):

    parameters = [
        {'name': 'project_id',
         'in': 'query',
         'required': False,
         'description': 'Project id',
         'schema': {'type': 'string'}}]


class UploadSessionFilesSchema(ObjectResponseSchema):

    parameters = [
        {'name': 'Content-Length',
         'in': 'header',
         'required': True,
         'description': 'Content Length',
         'schema': {'type': 'integer'}},
        {'name': 'File-Name',
         'in': 'header',
         'required': True,
         'description': 'Content Length',
         'schema': {'type': 'string'}},
        {'name': 'Force',
         'in': 'header',
         'required': False,
         'description': 'Force upload',
         'schema': {'type': 'boolean'}},
        {'name': 'Directory-Path',
         'in': 'header',
         'required': False,
         'description': 'Directory Path',
         'schema': {'type': 'boolean'}},
        {'name': 'force',
         'in': 'query',
         'required': False,
         'description': 'Force upload',
         'schema': {'type': 'boolean'}},
    ]

    class ProjectUploadSessionFilesResponseSerializer(serializers.Serializer):
        status = serializers.CharField()

    response_serializer = ProjectUploadSessionFilesResponseSerializer()

    def get_request_body(self, path, method):
        return {'content': {'application/offset+octet-stream': binary_string_schema}}

    def get_responses(self, path, method):
        responses = super().get_responses(path, method)
        responses['204'] = responses['201']
        responses['400'] = object_content
        responses['500'] = string_content
        return responses


class UploadSessionUploadSchema(ObjectResponseSchema):

    parameters = [
        {'name': 'File-Name',
         'in': 'header',
         'required': True,
         'description': 'File Name',
         'schema': {'type': 'boolean'}},
        {'name': 'File-Encoding',
         'in': 'header',
         'required': True,
         'description': 'File Encoding',
         'schema': {'type': 'string'}},
        {'name': 'Force',
         'in': 'header',
         'required': False,
         'description': 'Force upload',
         'schema': {'type': 'boolean'}},
        {'name': 'Review-File',
         'in': 'header',
         'required': False,
         'description': 'Review File',
         'schema': {'type': 'boolean'}},
        {'name': 'Directory-Path',
         'in': 'header',
         'required': False,
         'description': 'Directory Path',
         'schema': {'type': 'boolean'}},
    ]

    class ProjectUploadSessionPOSTResponseSerializer(serializers.Serializer):
        status = serializers.CharField()

    response_serializer = ProjectUploadSessionPOSTResponseSerializer()

    def get_request_body(self, path, method):
        return {'content': {'*/*': binary_string_schema}}

    def get_responses(self, path, method):
        resp = super().get_responses(path, method)
        resp['200'] = resp['201']
        del resp['201']
        resp['400'] = object_content
        resp['500'] = string_content
        return resp


class UploadSessionBatchUploadRequestSerializer(serializers.Serializer):
    folder = serializers.CharField()


class UploadSessionBatchUploadSchema(CustomAutoSchema):
    request_serializer = UploadSessionBatchUploadRequestSerializer()


class UploadSessionDeleteFileSchema(CustomAutoSchema):

    request_component_name = 'UploadSessionDeleteFileRequest'

    class UploadSessionDeleteFileRequestSerializer(serializers.Serializer):
        filename = serializers.CharField()

    def get_request_body(self, path, method):
        return {'content': {
            'application/json': {'schema': {
                '$ref': f'#/components/schemas/{self.request_component_name}'}}}}

    def get_components(self, path, method):
        return {self.request_component_name: self.map_serializer(self.UploadSessionDeleteFileRequestSerializer())}

    def get_responses(self, path, method):
        resp = super().get_responses(path, method)
        resp['200'] = string_content
        resp['404'] = string_content
        resp['500'] = string_content
        return resp


class ProjectUploadSessionProgressSchema(CustomAutoSchema):

    class ProjectUploadSessionProgressResponseSerializer(serializers.Serializer):
        project_id = serializers.IntegerField()
        document_tasks_progress = serializers.FloatField(allow_null=True)
        document_tasks_progress_total = serializers.FloatField(allow_null=True)
        documents_total_size = serializers.IntegerField()
        session_status = serializers.CharField(allow_null=True)

    response_serializer = ProjectUploadSessionProgressResponseSerializer()


class ProjectSearchSimilarDocumentsRequestSerializer(serializers.Serializer):
    run_name = serializers.CharField(required=False)
    distance_type = serializers.ChoiceField(choices=list(_METRICS), required=False, default='cosine')
    similarity_threshold = serializers.IntegerField(required=False, default=75)
    create_reverse_relations = serializers.BooleanField(required=False, default=True)
    use_tfidf = serializers.BooleanField(required=False, default=False)
    delete = serializers.BooleanField(required=False, default=True)
    item_id = serializers.IntegerField(required=False)


class ProjectSearchSimilarDocumentsSchema(CustomAutoSchema):

    request_serializer = ProjectSearchSimilarDocumentsRequestSerializer()
    response_serializer = TaskIdResponseSerializer()


class ProjectSearchSimilarTextUnitsSchema(CustomAutoSchema):

    class ProjectSearchSimilarTextUnitsRequestSerializer(ProjectSearchSimilarDocumentsRequestSerializer):
        unit_type = serializers.ChoiceField(
            required=False, choices=['sentence', 'paragraph'], default='sentence')
        document_id = serializers.IntegerField(required=False)
        location_start = serializers.IntegerField(required=False)
        location_end = serializers.IntegerField(required=False)
        item_id = serializers.IntegerField(required=False)

    request_serializer = ProjectSearchSimilarTextUnitsRequestSerializer()
    response_serializer = TaskIdResponseSerializer()
