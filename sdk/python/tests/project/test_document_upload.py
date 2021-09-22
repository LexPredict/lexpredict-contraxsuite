import os
import time
import unittest

import openapi_client
from openapi_client.api import document_api, project_api, tus_api, rawdb_api
from openapi_client.models import DocumentsForUser, ProjectUploadSessionProgressResponse, RawdbDocumentsPOSTRequest

from config import base_configuration
from utils import login, TestApiClient
from .utils import create_test_project, delete_test_project, create_test_upload_session, get_document_type, \
    TUS_RESUMABLE, DOCUMENTS_ROOT_DIR


class TestDocumentUpload(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.auth_configuration = login()
        self.doc_type_uid, self.doc_type_code = get_document_type()
        self.project_name, self.project_id = create_test_project(doc_type_uid=self.doc_type_uid)
        self.source_document_name = 'doc1.txt'

    def test_upload(self):
        path = os.path.join(DOCUMENTS_ROOT_DIR, self.source_document_name)
        with open(path, 'r') as f:
            file_content = f.read()
        file_data = {self.source_document_name: len(file_content)}

        # TODO: make a helper method in utils.py to upload N files in a project
        # 1. Create Upload Session
        upload_session_uid = create_test_upload_session(self.project_id, upload_files=file_data)

        # 2. Create TUS Upload - POST
        with openapi_client.ApiClient(self.auth_configuration) as api_client:
            api_instance = tus_api.TusApi(api_client)
            resp = api_instance.tus_upload_session_upload_session_id_upload_post(
                upload_session_id=upload_session_uid,
                upload_length=len(file_content),
                # taken from real request using the same file on dev server TODO: play with decoding
                upload_metadata='relativePath bnVsbA==,name ZG9jMS50eHQ=,type dGV4dC9wbGFpbg==,filetype dGV4dC9wbGFpbg==,filename ZG9jMS50eHQ=',
                tus_resumable=TUS_RESUMABLE,
                force=False,
                _preload_content=False
            )

        self.assertEqual(resp.status, 201)
        self.assertIn('Location', resp.headers)
        location = resp.headers['Location']

        # 3. Upload file itself TUS - PATCH
        with openapi_client.ApiClient(self.auth_configuration) as api_client:
            api_instance = tus_api.TusApi(api_client)
            resp = api_instance.tus_upload_session_upload_session_id_upload_guid_patch(
                upload_session_id=upload_session_uid,
                guid=location.strip('/').split('/')[-1],
                upload_offset=0,
                tus_resumable=TUS_RESUMABLE,
                force=False,
                body=file_content,
                _preload_content=False,
            )
        self.assertEqual(resp.status, 204)
        self.assertEqual(resp.headers['Upload-Offset'], str(len(file_content)))

        # 4. Check Upload Session status (60 times x 5sec = 300sec = 5 min should be enough)
        for attempt in range(60):
            with openapi_client.ApiClient(self.auth_configuration) as api_client:
                api_instance = project_api.ProjectApi(api_client)
                resp = api_instance.project_upload_session_uid_progress_get(uid=upload_session_uid)

            self.assertIsInstance(resp, ProjectUploadSessionProgressResponse)
            self.assertEqual(resp['project_id'], self.project_id)
            if resp['document_tasks_progress_total'] == 100:
                self.assertEqual(resp['session_status'], 'Parsed')
                break
            self.assertIn(resp['session_status'], [None, 'Parsing'])
            time.sleep(5)
        else:
            raise RuntimeError('Document Upload hangs')

        # 5. Check Document exists in a Project
        with openapi_client.ApiClient(self.auth_configuration) as api_client:
            api_instance = document_api.DocumentApi(api_client)
            resp = api_instance.document_project_project_pk_documents_get(project_pk=self.project_id)

        self.assertIsInstance(resp, dict)
        self.assertIn('data', resp)
        doc_data = resp['data'][0]
        self.assertIsInstance(doc_data, dict)
        self.assertEqual(doc_data['name'], self.source_document_name)
        self.assertEqual(doc_data['project'], self.project_id)
        self.assertEqual(doc_data['document_type'], self.doc_type_uid)

        # 6. Check Document indexed in rawdb
        with openapi_client.ApiClient(self.auth_configuration) as api_client:
            api_instance = rawdb_api.RawdbApi(api_client)
            request_data = RawdbDocumentsPOSTRequest(project_ids=f'{self.project_id}')
            resp = api_instance.rawdb_documents_document_type_code_post(
                document_type_code=self.doc_type_code,
                rawdb_documents_post_request=request_data
            )

        self.assertIsInstance(resp, dict)
        self.assertIn('items', resp)
        doc_data = resp['items'][0]
        self.assertEqual(doc_data['document_name'], self.source_document_name)
        self.assertEqual(doc_data['project_id'], self.project_id)
        self.assertEqual(doc_data['project_name'], self.project_name)
        # self.assertEqual(doc_data['created_by'], self.user_name)

    # def test_multiple_docs_upload(self):
    #     pass
    #
    # def test_pdf_upload(self):
    #     pass
    #
    # def test_img_upload(self):
    #     pass
    #
    # def test_zip_upload(self):
    #     pass
    #
    # def test_tar_upload(self):
    #     pass
    #
    # def test_damaged_file_upload(self):
    #     pass
    #
    # def test_folder_upload(self):
    #     pass
    #
    # def test_mixed_files_n_folders_upload(self):
    #     pass
    #
    # def test_unauth_access(self):
    #     pass

    def tearDown(self):
        delete_test_project(self.project_id)
