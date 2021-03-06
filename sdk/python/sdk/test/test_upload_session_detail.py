# coding: utf-8

"""

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 1.0.0
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest
import datetime

import openapi_client
from openapi_client.models.upload_session_detail import UploadSessionDetail  # noqa: E501
from openapi_client.rest import ApiException

class TestUploadSessionDetail(unittest.TestCase):
    """UploadSessionDetail unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test UploadSessionDetail
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = openapi_client.models.upload_session_detail.UploadSessionDetail()  # noqa: E501
        if include_optional :
            return UploadSessionDetail(
                uid = '0', 
                project = openapi_client.models.upload_session_detail_project.UploadSessionDetail_project(
                    pk = 56, 
                    name = '0', 
                    description = '0', 
                    send_email_notification = True, 
                    hide_clause_review = True, 
                    status = 56, 
                    status_data = openapi_client.models.project_list_status_data.ProjectList_status_data(
                        id = 56, 
                        name = '0', 
                        code = '0', 
                        order = 0, 
                        is_active = True, 
                        group = 56, ), 
                    owners = [
                        56
                        ], 
                    owners_data = [
                        openapi_client.models.project_detail_owners_data.ProjectDetail_owners_data(
                            id = 56, 
                            username = 'a', 
                            last_name = '0', 
                            first_name = '0', 
                            email = '0', 
                            is_superuser = True, 
                            is_staff = True, 
                            is_active = True, 
                            name = '0', 
                            role = 56, 
                            role_data = openapi_client.models.project_detail_role_data.ProjectDetail_role_data(
                                id = 56, 
                                name = '0', 
                                code = '0', 
                                abbr = '0', 
                                order = 0, 
                                is_admin = True, 
                                is_top_manager = True, 
                                is_manager = True, 
                                is_reviewer = '0', ), 
                            organization = '0', 
                            photo = '0', 
                            permissions = openapi_client.models.permissions.permissions(), 
                            groups = [
                                56
                                ], )
                        ], 
                    reviewers = [
                        56
                        ], 
                    reviewers_data = [
                        openapi_client.models.project_detail_owners_data.ProjectDetail_owners_data(
                            id = 56, 
                            username = 'a', 
                            last_name = '0', 
                            first_name = '0', 
                            email = '0', 
                            is_superuser = True, 
                            is_staff = True, 
                            is_active = True, 
                            name = '0', 
                            role = 56, 
                            organization = '0', 
                            photo = '0', 
                            permissions = openapi_client.models.permissions.permissions(), )
                        ], 
                    super_reviewers = [
                        56
                        ], 
                    super_reviewers_data = [
                        openapi_client.models.project_detail_owners_data.ProjectDetail_owners_data(
                            id = 56, 
                            username = 'a', 
                            last_name = '0', 
                            first_name = '0', 
                            email = '0', 
                            is_superuser = True, 
                            is_staff = True, 
                            is_active = True, 
                            name = '0', 
                            role = 56, 
                            organization = '0', 
                            photo = '0', 
                            permissions = openapi_client.models.permissions.permissions(), )
                        ], 
                    junior_reviewers = [
                        56
                        ], 
                    junior_reviewers_data = [
                        openapi_client.models.project_detail_owners_data.ProjectDetail_owners_data(
                            id = 56, 
                            username = 'a', 
                            last_name = '0', 
                            first_name = '0', 
                            email = '0', 
                            is_superuser = True, 
                            is_staff = True, 
                            is_active = True, 
                            name = '0', 
                            role = 56, 
                            organization = '0', 
                            photo = '0', 
                            permissions = openapi_client.models.permissions.permissions(), )
                        ], 
                    type = '0', 
                    type_data = openapi_client.models.project_list_type_data.ProjectList_type_data(
                        uid = '0', 
                        code = '0', 
                        title = '0', ), 
                    progress = '0', 
                    user_permissions = '0', ), 
                created_by = openapi_client.models.task_queue_reviewers_data.TaskQueue_reviewers_data(
                    pk = 56, 
                    username = 'a', 
                    role = 56, ), 
                created_date = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                document_type = '0', 
                progress = '0'
            )
        else :
            return UploadSessionDetail(
                created_by = openapi_client.models.task_queue_reviewers_data.TaskQueue_reviewers_data(
                    pk = 56, 
                    username = 'a', 
                    role = 56, ),
        )

    def testUploadSessionDetail(self):
        """Test UploadSessionDetail"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
