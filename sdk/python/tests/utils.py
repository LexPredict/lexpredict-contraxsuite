import copy
from functools import lru_cache

import openapi_client
from openapi_client.api import rest_auth_api
from openapi_client.model.login import Login
from openapi_client.model.login_response import LoginResponse

from config import ADMIN_USER_NAME, ADMIN_USER_PASSWORD, base_configuration


class TestRESTResponse:

    def __init__(self, ex):
        self.status = ex.status
        self.reason = ex.reason
        self.data = getattr(ex, 'data', None)
        self.body = ex.body
        self.headers = ex.headers


class TestApiClient(openapi_client.ApiClient):
    """
    Test client to catch error responses as http response rather than exception,
    in this case
    a) pass return_http_response=True like with TestApiClient(conf, return_http_response=True) as api_client:...
    b) pass _preload_content=False like resp = api_instance.project_projects_get(_preload_content=False)...

        with TestApiClient(configuration, return_http_response=True) as api_client:
            api_instance = some_api.SomeApi(api_client)
            resp = api_instance.some_api_endpoint(_preload_content=False)
        self.assertEqual(resp.status, ...)

    otherwise need to catch exception in 2 places: if exception raises and if not:

        with openapi_client.ApiClient(configuration) as api_client:
            api_instance = some_api.SomeApi(api_client)
            try:
                resp = api_instance.some_api_endpoint()
                assert ...
            except Exception as e:
                assert e.status == ...
    """
    def __init__(self, *args, **kwargs):
        self.return_http_response = kwargs.pop('return_http_response', False)
        super().__init__(*args, **kwargs)

    def request(self, *args, **kwargs):
        try:
            return super().request(*args, **kwargs)
        except Exception as e:
            if self.return_http_response and hasattr(e, 'status'):
                return TestRESTResponse(e)
            raise e


@lru_cache(typed=True)
def login(username: str = None, password: str = None):
    """
    Login a user to get auth token,
    Return configuration for further authenticated requests
    Cache configuration for each type of passed arguments separately (up to 128 calls by default)
    """
    username = username or ADMIN_USER_NAME
    password = password or ADMIN_USER_PASSWORD
    param = Login(username=username, password=password)

    with openapi_client.ApiClient(base_configuration) as api_client:
        api_instance = rest_auth_api.RestAuthApi(api_client)
        resp = api_instance.rest_auth_login_post(login=param)

    assert isinstance(resp, LoginResponse)
    auth_configuration = copy.deepcopy(base_configuration)
    auth_configuration.api_key_prefix['AuthToken'] = 'Token'
    auth_configuration.api_key['AuthToken'] = resp["key"]
    auth_configuration.user_id = resp.user['id']

    # print('===> login')
    return auth_configuration
