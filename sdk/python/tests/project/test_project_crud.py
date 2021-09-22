import unittest

import openapi_client
from openapi_client.api import project_api
from openapi_client.models import ProjectCreate, ProjectDetail

from config import base_configuration
from utils import login, TestApiClient
from .utils import get_document_type, create_test_project, delete_test_project


class TestProjectCreate(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.auth_configuration = login()
        self.doc_type_uid, _ = get_document_type()

    def test_admin_access(self):
        with openapi_client.ApiClient(self.auth_configuration) as api_client:
            api_instance = project_api.ProjectApi(api_client)
            request_data = ProjectCreate(name='test1', type=self.doc_type_uid)
            resp = api_instance.project_projects_post(project_create=request_data)

        self.assertIsInstance(resp, ProjectCreate)
        self.assertEqual(resp['name'], request_data['name'])
        self.assertEqual(resp['type'], self.doc_type_uid)

        delete_test_project(resp['pk'])

    def test_unauth_access(self):
        with TestApiClient(base_configuration, return_http_response=True) as api_client:
            api_instance = project_api.ProjectApi(api_client)
            request_data = ProjectCreate(name='test1', type=self.doc_type_uid)
            resp = api_instance.project_projects_post(project_create=request_data, _preload_content=False)

        self.assertEqual(resp.status, 401)

    def test_permissions(self):
        # TODO: test all groups, like reviewer
        pass

    def tearDown(self):
        pass


class TestProjectList(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.auth_configuration = login()
        self.doc_type_uid, _ = get_document_type()

        self.project_1_name, self.project_1_id = create_test_project()
        self.project_2_name, self.project_2_id = create_test_project()

    def test_admin_access(self):
        with openapi_client.ApiClient(self.auth_configuration) as api_client:
            api_instance = project_api.ProjectApi(api_client)
            resp = api_instance.project_projects_get()

        self.assertIsInstance(resp, dict)
        self.assertIn('data', resp)
        self.assertIsInstance(resp['data'], list)

    def test_unauth_access(self):
        with TestApiClient(base_configuration, return_http_response=True) as api_client:
            api_instance = project_api.ProjectApi(api_client)
            resp = api_instance.project_projects_get(_preload_content=False)

        self.assertEqual(resp.status, 401)

    def test_jq_filters_contains_both(self):
        jq_filters = {
            "filterscount": "1",
            "filterdatafield0": "name",
            "filtervalue0": "test-project",
            "filtercondition0": "CONTAINS",
        }
        with openapi_client.ApiClient(self.auth_configuration) as api_client:
            api_instance = project_api.ProjectApi(api_client)
            resp = api_instance.project_projects_get(jq_filters=jq_filters)

        self.assertIsInstance(resp, dict)
        self.assertIn('data', resp)
        self.assertIsInstance(resp['data'], list)

        response_project_names = [i['name'] for i in resp['data']]
        self.assertIn(self.project_1_name, response_project_names)
        self.assertIn(self.project_2_name, response_project_names)

    def test_jq_filters_contains_one(self):
        jq_filters = {
            "filterscount": "1",
            "filterdatafield0": "name",
            "filtervalue0": self.project_1_name,
            "filtercondition0": "CONTAINS",
        }
        with openapi_client.ApiClient(self.auth_configuration) as api_client:
            api_instance = project_api.ProjectApi(api_client)
            resp = api_instance.project_projects_get(jq_filters=jq_filters)

        self.assertIsInstance(resp, dict)
        self.assertIn('data', resp)
        self.assertIsInstance(resp['data'], list)
        self.assertTrue(len(resp['data']), 1)

        response_project_names = [i['name'] for i in resp['data']]
        self.assertListEqual([self.project_1_name], response_project_names)

    def test_permissions(self):
        # TODO: test all groups, like reviewer
        pass

    def tearDown(self):
        delete_test_project(self.project_1_id)
        delete_test_project(self.project_2_id)


class TestProjectDetail(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.auth_configuration = login()
        self.doc_type_uid, _ = get_document_type()

        self.project_1_name, self.project_1_id = create_test_project()

    def test_admin_access(self):
        with openapi_client.ApiClient(self.auth_configuration) as api_client:
            api_instance = project_api.ProjectApi(api_client)
            resp = api_instance.project_projects_id_get(id=self.project_1_id)

        self.assertIsInstance(resp, ProjectDetail)
        self.assertEqual(resp.pk, self.project_1_id)
        self.assertEqual(resp.name, self.project_1_name)

    def test_unauth_access(self):
        with TestApiClient(base_configuration, return_http_response=True) as api_client:
            api_instance = project_api.ProjectApi(api_client)
            resp = api_instance.project_projects_id_get(id=self.project_1_id, _preload_content=False)

        self.assertEqual(resp.status, 401)

    def test_permissions(self):
        # TODO: test all groups, like reviewer
        pass

    def tearDown(self):
        delete_test_project(self.project_1_id)


class TestProjectDelete(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.auth_configuration = login()
        self.doc_type_uid, _ = get_document_type()

        self.project_1_name, self.project_1_id = create_test_project()

    def test_admin_access(self):
        with openapi_client.ApiClient(self.auth_configuration) as api_client:
            api_instance = project_api.ProjectApi(api_client)
            resp = api_instance.project_projects_id_delete(id=self.project_1_id, _preload_content=False)

        self.assertEqual(resp.status, 204)

    def test_unauth_access(self):
        with TestApiClient(base_configuration, return_http_response=True) as api_client:
            api_instance = project_api.ProjectApi(api_client)
            resp = api_instance.project_projects_id_delete(id=self.project_1_id, _preload_content=False)

        self.assertEqual(resp.status, 401)

    def test_permissions(self):
        # TODO: test all groups, like reviewer
        pass

    def tearDown(self):
        delete_test_project(self.project_1_id)
