import os
import unittest
import uuid

import openapi_client
from openapi_client.api import project_api
from openapi_client.models import UploadSessionCreate, ProjectUploadSessionProgressResponse, UploadSessionDetail

from config import base_configuration
from utils import login, TestApiClient
from .utils import create_test_project, delete_test_project, create_test_upload_session, \
    TUS_RESUMABLE, DOCUMENTS_ROOT_DIR


class TestUploadSession(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.auth_configuration = login()
        _, self.project_id = create_test_project()
        self.user_id = self.auth_configuration.user_id

    def test_upload_session_create(self):
        with openapi_client.ApiClient(self.auth_configuration) as api_client:
            api_instance = project_api.ProjectApi(api_client)
            request_data = UploadSessionCreate._from_openapi_data(
                project=self.project_id,
                created_by=self.user_id,
                upload_files={f'{uuid.uuid4()}.txt': 100}
            )
            resp = api_instance.project_upload_session_post(upload_session_create=request_data)

        self.assertIsInstance(resp, UploadSessionCreate)
        self.assertEqual(resp['project'], self.project_id)
        self.assertEqual(resp['created_by'], self.user_id)
        self.assertIn('uid', resp)

    def test_upload_session_progress(self):
        session_id = create_test_upload_session(self.project_id)
        with openapi_client.ApiClient(self.auth_configuration) as api_client:
            api_instance = project_api.ProjectApi(api_client)
            resp = api_instance.project_upload_session_uid_progress_get(uid=session_id)

        self.assertIsInstance(resp, ProjectUploadSessionProgressResponse)
        self.assertEqual(resp['project_id'], self.project_id)
        self.assertIn(resp['document_tasks_progress'], [None, 0])
        self.assertIn(resp['document_tasks_progress_total'], [None, 0])
        self.assertIn(resp['documents_total_size'], [None, 0])
        self.assertIsNone(resp['session_status'])

    def test_upload_sessions_status(self):
        session_id = create_test_upload_session(self.project_id)
        with openapi_client.ApiClient(self.auth_configuration) as api_client:
            api_instance = project_api.ProjectApi(api_client)
            resp = api_instance.project_upload_session_status_get(project_id=self.project_id)

        self.assertIsInstance(resp, dict)
        self.assertIsNone(resp[session_id])

    def tearDown(self):
        delete_test_project(self.project_id)
