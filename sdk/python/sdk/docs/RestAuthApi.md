# openapi_client.RestAuthApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**rest_auth_login_post**](RestAuthApi.md#rest_auth_login_post) | **POST** /rest-auth/login/ | 
[**rest_auth_logout_get**](RestAuthApi.md#rest_auth_logout_get) | **GET** /rest-auth/logout/ | 
[**rest_auth_logout_post**](RestAuthApi.md#rest_auth_logout_post) | **POST** /rest-auth/logout/ | 
[**rest_auth_password_change_post**](RestAuthApi.md#rest_auth_password_change_post) | **POST** /rest-auth/password/change/ | 
[**rest_auth_password_reset_confirm_post**](RestAuthApi.md#rest_auth_password_reset_confirm_post) | **POST** /rest-auth/password/reset/confirm/ | 
[**rest_auth_password_reset_post**](RestAuthApi.md#rest_auth_password_reset_post) | **POST** /rest-auth/password/reset/ | 
[**rest_auth_registration_post**](RestAuthApi.md#rest_auth_registration_post) | **POST** /rest-auth/registration/ | 
[**rest_auth_registration_verify_email_post**](RestAuthApi.md#rest_auth_registration_verify_email_post) | **POST** /rest-auth/registration/verify-email/ | 


# **rest_auth_login_post**
> LoginResponse rest_auth_login_post()



Check the credentials and return the REST Token if the credentials are valid and authenticated. Calls Django Auth login method to register User ID in Django session framework  Accept the following POST parameters: username, password Return the REST Framework Token Object's key.

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import rest_auth_api
from openapi_client.model.login_response import LoginResponse
from openapi_client.model.login import Login
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
    api_instance = rest_auth_api.RestAuthApi(api_client)
    login = Login(
        username="username_example",
        email="email_example",
        password="password_example",
    ) # Login |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.rest_auth_login_post(login=login)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling RestAuthApi->rest_auth_login_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **login** | [**Login**](Login.md)|  | [optional]

### Return type

[**LoginResponse**](LoginResponse.md)

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

# **rest_auth_logout_get**
> [RestAuthCommonResponse] rest_auth_logout_get()



Calls Django logout method and delete the Token object assigned to the current User object.  Accepts/Returns nothing.

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import rest_auth_api
from openapi_client.model.rest_auth_common_response import RestAuthCommonResponse
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
    api_instance = rest_auth_api.RestAuthApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_response = api_instance.rest_auth_logout_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling RestAuthApi->rest_auth_logout_get: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

[**[RestAuthCommonResponse]**](RestAuthCommonResponse.md)

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

# **rest_auth_logout_post**
> RestAuthCommonResponse rest_auth_logout_post()



Calls Django logout method and delete the Token object assigned to the current User object.  Accepts/Returns nothing.

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import rest_auth_api
from openapi_client.model.rest_auth_common_response import RestAuthCommonResponse
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
    api_instance = rest_auth_api.RestAuthApi(api_client)
    request_body = {
        "key": {},
    } # {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.rest_auth_logout_post(request_body=request_body)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling RestAuthApi->rest_auth_logout_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | **{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**|  | [optional]

### Return type

[**RestAuthCommonResponse**](RestAuthCommonResponse.md)

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

# **rest_auth_password_change_post**
> RestAuthCommonResponse rest_auth_password_change_post()



Calls Django Auth SetPasswordForm save method.  Accepts the following POST parameters: new_password1, new_password2 Returns the success/fail message.

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import rest_auth_api
from openapi_client.model.rest_auth_common_response import RestAuthCommonResponse
from openapi_client.model.custom_password_change import CustomPasswordChange
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
    api_instance = rest_auth_api.RestAuthApi(api_client)
    custom_password_change = CustomPasswordChange(
        old_password="old_password_example",
        new_password="new_password_example",
    ) # CustomPasswordChange |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.rest_auth_password_change_post(custom_password_change=custom_password_change)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling RestAuthApi->rest_auth_password_change_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **custom_password_change** | [**CustomPasswordChange**](CustomPasswordChange.md)|  | [optional]

### Return type

[**RestAuthCommonResponse**](RestAuthCommonResponse.md)

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

# **rest_auth_password_reset_confirm_post**
> RestAuthCommonResponse rest_auth_password_reset_confirm_post()



Password reset e-mail link is confirmed, therefore this resets the user's password.  Accepts the following POST parameters: token, uid,     new_password1, new_password2 Returns the success/fail message.

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import rest_auth_api
from openapi_client.model.custom_password_reset_confirm import CustomPasswordResetConfirm
from openapi_client.model.rest_auth_common_response import RestAuthCommonResponse
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
    api_instance = rest_auth_api.RestAuthApi(api_client)
    custom_password_reset_confirm = CustomPasswordResetConfirm(
        new_password1="new_password1_example",
        new_password2="new_password2_example",
        uid="uid_example",
        token="token_example",
    ) # CustomPasswordResetConfirm |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.rest_auth_password_reset_confirm_post(custom_password_reset_confirm=custom_password_reset_confirm)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling RestAuthApi->rest_auth_password_reset_confirm_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **custom_password_reset_confirm** | [**CustomPasswordResetConfirm**](CustomPasswordResetConfirm.md)|  | [optional]

### Return type

[**RestAuthCommonResponse**](RestAuthCommonResponse.md)

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

# **rest_auth_password_reset_post**
> RestAuthCommonResponse rest_auth_password_reset_post()



Calls Django Auth PasswordResetForm save method.  Accepts the following POST parameters: email Returns the success/fail message.

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import rest_auth_api
from openapi_client.model.rest_auth_common_response import RestAuthCommonResponse
from openapi_client.model.custom_password_reset import CustomPasswordReset
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
    api_instance = rest_auth_api.RestAuthApi(api_client)
    custom_password_reset = CustomPasswordReset(
        email="email_example",
    ) # CustomPasswordReset |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.rest_auth_password_reset_post(custom_password_reset=custom_password_reset)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling RestAuthApi->rest_auth_password_reset_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **custom_password_reset** | [**CustomPasswordReset**](CustomPasswordReset.md)|  | [optional]

### Return type

[**RestAuthCommonResponse**](RestAuthCommonResponse.md)

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

# **rest_auth_registration_post**
> Register rest_auth_registration_post()



### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import rest_auth_api
from openapi_client.model.register import Register
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
    api_instance = rest_auth_api.RestAuthApi(api_client)
    register = Register(
        username="username_example",
        email="email_example",
        password1="password1_example",
        password2="password2_example",
    ) # Register |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.rest_auth_registration_post(register=register)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling RestAuthApi->rest_auth_registration_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **register** | [**Register**](Register.md)|  | [optional]

### Return type

[**Register**](Register.md)

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

# **rest_auth_registration_verify_email_post**
> VerifyEmail rest_auth_registration_verify_email_post()



### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import rest_auth_api
from openapi_client.model.verify_email import VerifyEmail
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
    api_instance = rest_auth_api.RestAuthApi(api_client)
    verify_email = VerifyEmail(
        key="key_example",
    ) # VerifyEmail |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.rest_auth_registration_verify_email_post(verify_email=verify_email)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling RestAuthApi->rest_auth_registration_verify_email_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verify_email** | [**VerifyEmail**](VerifyEmail.md)|  | [optional]

### Return type

[**VerifyEmail**](VerifyEmail.md)

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

