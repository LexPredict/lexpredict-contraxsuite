# openapi_client.UsersApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**users_social_accounts_get**](UsersApi.md#users_social_accounts_get) | **GET** /api/v1/users/social_accounts/ | 
[**users_users_form_fields_get**](UsersApi.md#users_users_form_fields_get) | **GET** /api/v1/users/users/form-fields/ | 
[**users_users_get**](UsersApi.md#users_users_get) | **GET** /api/v1/users/users/ | 
[**users_users_id_form_fields_get**](UsersApi.md#users_users_id_form_fields_get) | **GET** /api/v1/users/users/{id}/form-fields/ | 
[**users_users_id_get**](UsersApi.md#users_users_id_get) | **GET** /api/v1/users/users/{id}/ | 
[**users_users_id_patch**](UsersApi.md#users_users_id_patch) | **PATCH** /api/v1/users/users/{id}/ | 
[**users_users_id_put**](UsersApi.md#users_users_id_put) | **PUT** /api/v1/users/users/{id}/ | 
[**users_users_post**](UsersApi.md#users_users_post) | **POST** /api/v1/users/users/ | 
[**users_users_user_stats_get**](UsersApi.md#users_users_user_stats_get) | **GET** /api/v1/users/users/user_stats/ | 
[**users_verify_token_post**](UsersApi.md#users_verify_token_post) | **POST** /api/v1/users/verify-token/ | 


# **users_social_accounts_get**
> SocialAccountsResponse users_social_accounts_get()



### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import users_api
from openapi_client.model.social_accounts_response import SocialAccountsResponse
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AuthToken
configuration.api_key['AuthToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = users_api.UsersApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_response = api_instance.users_social_accounts_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling UsersApi->users_social_accounts_get: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

[**SocialAccountsResponse**](SocialAccountsResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **users_users_form_fields_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} users_users_form_fields_get()



GET model form fields description to build UI form for an object:       - field_type: str - CharField, IntegerField, SomeSerializerField - i.e. fields from a serializer      - ui_element: dict - {type: (\"input\" | \"select\" | \"checkbox\" | ...), data_type: (\"string\", \"integer\", \"date\", ...), ...}      - label: str - field label declared in a serializer field (default NULL)      - field_name: str - field name declared in a serializer field (default NULL)      - help_text: str - field help text declared in a serializer field (default NULL)      - required: bool - whether field is required      - read_only: bool - whether field is read only      - allow_null: bool - whether field is may be null      - default: bool - default (initial) field value for a new object (default NULL)      - choices: array - choices to select from [{choice_id1: choice_verbose_name1, ....}] (default NULL)

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import users_api
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AuthToken
configuration.api_key['AuthToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = users_api.UsersApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_response = api_instance.users_users_form_fields_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling UsersApi->users_users_form_fields_get: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

**{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **users_users_get**
> [User] users_users_get()



User List

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import users_api
from openapi_client.model.user import User
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AuthToken
configuration.api_key['AuthToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = users_api.UsersApi(api_client)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.users_users_get(jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling UsersApi->users_users_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**[User]**](User.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **users_users_id_form_fields_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} users_users_id_form_fields_get(id)



GET model form fields description to build UI form for EXISTING object:       - value: any - object field value      - field_type: str - CharField, IntegerField, SomeSerializerField - i.e. fields from a serializer      - ui_element: dict - {type: (\"input\" | \"select\" | \"checkbox\" | ...), data_type: (\"string\", \"integer\", \"date\", ...), ...}      - label: str - field label declared in a serializer field (default NULL)      - field_name: str - field name declared in a serializer field (default NULL)      - help_text: str - field help text declared in a serializer field (default NULL)      - required: bool - whether field is required      - read_only: bool - whether field is read only      - allow_null: bool - whether field is may be null      - default: bool - default (initial) field value for a new object (default NULL)      - choices: array - choices to select from [{choice_id1: choice_verbose_name1, ....}] (default NULL)

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import users_api
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AuthToken
configuration.api_key['AuthToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = users_api.UsersApi(api_client)
    id = "id_example" # str | A unique integer value identifying this user.

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.users_users_id_form_fields_get(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling UsersApi->users_users_id_form_fields_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this user. |

### Return type

**{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **users_users_id_get**
> User users_users_id_get(id)



Retrieve User

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import users_api
from openapi_client.model.user import User
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AuthToken
configuration.api_key['AuthToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = users_api.UsersApi(api_client)
    id = "id_example" # str | A unique integer value identifying this user.
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.users_users_id_get(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling UsersApi->users_users_id_get: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.users_users_id_get(id, jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling UsersApi->users_users_id_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this user. |
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**User**](User.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **users_users_id_patch**
> UserProfile users_users_id_patch(id)



Partial Update User

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import users_api
from openapi_client.model.user_profile import UserProfile
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AuthToken
configuration.api_key['AuthToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = users_api.UsersApi(api_client)
    id = "id_example" # str | A unique integer value identifying this user.
    user_profile = UserProfile(
        last_name="last_name_example",
        first_name="first_name_example",
        name="name_example",
        photo=open('/path/to/file', 'rb'),
        organization="organization_example",
    ) # UserProfile |  (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.users_users_id_patch(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling UsersApi->users_users_id_patch: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.users_users_id_patch(id, user_profile=user_profile)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling UsersApi->users_users_id_patch: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this user. |
 **user_profile** | [**UserProfile**](UserProfile.md)|  | [optional]

### Return type

[**UserProfile**](UserProfile.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **users_users_id_put**
> UserProfile users_users_id_put(id)



Update User

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import users_api
from openapi_client.model.user_profile import UserProfile
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AuthToken
configuration.api_key['AuthToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = users_api.UsersApi(api_client)
    id = "id_example" # str | A unique integer value identifying this user.
    user_profile = UserProfile(
        last_name="last_name_example",
        first_name="first_name_example",
        name="name_example",
        photo=open('/path/to/file', 'rb'),
        organization="organization_example",
    ) # UserProfile |  (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.users_users_id_put(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling UsersApi->users_users_id_put: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.users_users_id_put(id, user_profile=user_profile)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling UsersApi->users_users_id_put: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this user. |
 **user_profile** | [**UserProfile**](UserProfile.md)|  | [optional]

### Return type

[**UserProfile**](UserProfile.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **users_users_post**
> UserProfile users_users_post()



Create User

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import users_api
from openapi_client.model.user_profile import UserProfile
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AuthToken
configuration.api_key['AuthToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = users_api.UsersApi(api_client)
    user_profile = UserProfile(
        last_name="last_name_example",
        first_name="first_name_example",
        name="name_example",
        photo=open('/path/to/file', 'rb'),
        organization="organization_example",
    ) # UserProfile |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.users_users_post(user_profile=user_profile)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling UsersApi->users_users_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_profile** | [**UserProfile**](UserProfile.md)|  | [optional]

### Return type

[**UserProfile**](UserProfile.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **users_users_user_stats_get**
> [UserStats] users_users_user_stats_get()



User stats: projects, document types, tasks

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import users_api
from openapi_client.model.user_stats import UserStats
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AuthToken
configuration.api_key['AuthToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = users_api.UsersApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_response = api_instance.users_users_user_stats_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling UsersApi->users_users_user_stats_get: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

[**[UserStats]**](UserStats.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **users_verify_token_post**
> VerifyAuthTokenResponse users_verify_token_post()



Get user data for provided auth_token.

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import users_api
from openapi_client.model.verify_auth_token_request import VerifyAuthTokenRequest
from openapi_client.model.verify_auth_token_response import VerifyAuthTokenResponse
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AuthToken
configuration.api_key['AuthToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = users_api.UsersApi(api_client)
    verify_auth_token_request = VerifyAuthTokenRequest(
        auth_token="auth_token_example",
    ) # VerifyAuthTokenRequest |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.users_verify_token_post(verify_auth_token_request=verify_auth_token_request)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling UsersApi->users_verify_token_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verify_auth_token_request** | [**VerifyAuthTokenRequest**](VerifyAuthTokenRequest.md)|  | [optional]

### Return type

[**VerifyAuthTokenResponse**](VerifyAuthTokenResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |
**403** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

