import unittest

import openapi_client
from openapi_client.api import common_api
from openapi_client.models import AppVar

from utils import login, base_configuration, TestApiClient


class TestAppVarAPIAuthUser(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.auth_configuration = login()

    def test_app_var_list(self):
        jq_filters = {
            "filterscount": "1",
            "filterdatafield0": "name",
            "filtervalue0": "release_version",
            "filtercondition0": "CONTAINS",
        }
        with openapi_client.ApiClient(self.auth_configuration) as api_client:
            api_instance = common_api.CommonApi(api_client)
            resp = api_instance.common_app_variables_list_get(jq_filters=jq_filters)

        self.assertIsInstance(resp, list)
        self.assertIsInstance(resp[0], AppVar)
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0]['name'], 'release_version')

    def test_app_var_get(self):
        with openapi_client.ApiClient(self.auth_configuration) as api_client:
            api_instance = common_api.CommonApi(api_client)
            resp = api_instance.common_app_variables_get(name='release_version')

        self.assertIsInstance(resp, dict)
        self.assertEqual(len(resp), 1)
        self.assertIn('release_version', resp)


class TestAppVarAPINonAuthUser(unittest.TestCase):

    def test_app_var_list(self):
        with TestApiClient(base_configuration, return_http_response=True) as api_client:
            api_instance = common_api.CommonApi(api_client)
            resp = api_instance.common_app_variables_list_get(_preload_content=False)

        self.assertEqual(resp.status, 403)

    def test_app_var_get(self):
        # test disallowed for non-auth access variables
        with TestApiClient(base_configuration, return_http_response=True) as api_client:
            api_instance = common_api.CommonApi(api_client)
            resp = api_instance.common_app_variables_get(name='max_files_upload', _preload_content=False)

        self.assertEqual(resp.status, 404)

        # test allowed for non-auth access variables
        with TestApiClient(base_configuration, return_http_response=True) as api_client:
            api_instance = common_api.CommonApi(api_client)
            resp = api_instance.common_app_variables_get(name='support_email')

        self.assertIsInstance(resp, dict)
        self.assertEqual(len(resp), 1)
        self.assertIn('support_email', resp)
