import unittest

import openapi_client
from openapi_client.api import rest_auth_api
from openapi_client.model.login import Login
from openapi_client.model.login_response import LoginResponse

from config import ADMIN_USER_NAME, ADMIN_USER_PASSWORD, base_configuration


class TestLogin(unittest.TestCase):

    def test_auth(self):
        with openapi_client.ApiClient(base_configuration) as api_client:
            api_instance = rest_auth_api.RestAuthApi(api_client)
            login = Login(username=ADMIN_USER_NAME, password=ADMIN_USER_PASSWORD)
            auth_resp = api_instance.rest_auth_login_post(login=login)
            self.assertIsInstance(auth_resp, LoginResponse)
            self.assertTrue(auth_resp['key'])
