# openapi_client.DumpApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**dump_document_config_get**](DumpApi.md#dump_document_config_get) | **GET** /api/v1/dump/document-config/ | 
[**dump_document_config_put**](DumpApi.md#dump_document_config_put) | **PUT** /api/v1/dump/document-config/ | 
[**dump_dump_fixture_post**](DumpApi.md#dump_dump_fixture_post) | **POST** /api/v1/dump/dump-fixture/ | 
[**dump_dump_get**](DumpApi.md#dump_dump_get) | **GET** /api/v1/dump/dump/ | 
[**dump_dump_put**](DumpApi.md#dump_dump_put) | **PUT** /api/v1/dump/dump/ | 
[**dump_field_values_get**](DumpApi.md#dump_field_values_get) | **GET** /api/v1/dump/field-values/ | 
[**dump_field_values_put**](DumpApi.md#dump_field_values_put) | **PUT** /api/v1/dump/field-values/ | 
[**dump_load_fixture_post**](DumpApi.md#dump_load_fixture_post) | **POST** /api/v1/dump/load-fixture/ | 


# **dump_document_config_get**
> bool, date, datetime, dict, float, int, list, str, none_type dump_document_config_get()



Dump document types, fields, field detectors and  document filters to json.

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import dump_api
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
    api_instance = dump_api.DumpApi(api_client)
    download = True # bool | Download as file (optional)
    document_type_codes = "document_type_codes_example" # str | Document Type codes separated by comma (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.dump_document_config_get(download=download, document_type_codes=document_type_codes)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling DumpApi->dump_document_config_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **download** | **bool**| Download as file | [optional]
 **document_type_codes** | **str**| Document Type codes separated by comma | [optional]

### Return type

**bool, date, datetime, dict, float, int, list, str, none_type**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **dump_document_config_put**
> str dump_document_config_put()



Dump document types, fields, field detectors and  document filters to json.

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import dump_api
from openapi_client.model.dump_put_error_response import DumpPUTErrorResponse
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
    api_instance = dump_api.DumpApi(api_client)
    request_body = [
        {},
    ] # [{str: (bool, date, datetime, dict, float, int, list, str, none_type)}] |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.dump_document_config_put(request_body=request_body)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling DumpApi->dump_document_config_put: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | **[{str: (bool, date, datetime, dict, float, int, list, str, none_type)}]**|  | [optional]

### Return type

**str**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **dump_dump_fixture_post**
> file_type dump_dump_fixture_post()



Download model fixture

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import dump_api
from openapi_client.model.dump_fixture import DumpFixture
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
    api_instance = dump_api.DumpApi(api_client)
    dump_fixture = DumpFixture(
        app_name="app_name_example",
        model_name="model_name_example",
        file_name="file_name_example",
        filter_options={},
        indent=4,
    ) # DumpFixture |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.dump_dump_fixture_post(dump_fixture=dump_fixture)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling DumpApi->dump_dump_fixture_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dump_fixture** | [**DumpFixture**](DumpFixture.md)|  | [optional]

### Return type

**file_type**

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

# **dump_dump_get**
> bool, date, datetime, dict, float, int, list, str, none_type dump_dump_get()



Dump all users, email addresses, review statuses, review status groups, app vars, document types, fields, field detectors and document filters to json.

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import dump_api
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
    api_instance = dump_api.DumpApi(api_client)
    download = True # bool | Download as file (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.dump_dump_get(download=download)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling DumpApi->dump_dump_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **download** | **bool**| Download as file | [optional]

### Return type

**bool, date, datetime, dict, float, int, list, str, none_type**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **dump_dump_put**
> str dump_dump_put()



Dump all users, email addresses, review statuses, review status groups, app vars, document types, fields, field detectors and document filters to json.

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import dump_api
from openapi_client.model.dump_put_error_response import DumpPUTErrorResponse
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
    api_instance = dump_api.DumpApi(api_client)
    request_body = [
        {},
    ] # [{str: (bool, date, datetime, dict, float, int, list, str, none_type)}] |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.dump_dump_put(request_body=request_body)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling DumpApi->dump_dump_put: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | **[{str: (bool, date, datetime, dict, float, int, list, str, none_type)}]**|  | [optional]

### Return type

**str**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **dump_field_values_get**
> bool, date, datetime, dict, float, int, list, str, none_type dump_field_values_get()



Dump field values to json.

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import dump_api
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
    api_instance = dump_api.DumpApi(api_client)
    download = True # bool | Download as file (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.dump_field_values_get(download=download)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling DumpApi->dump_field_values_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **download** | **bool**| Download as file | [optional]

### Return type

**bool, date, datetime, dict, float, int, list, str, none_type**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **dump_field_values_put**
> str dump_field_values_put()



Upload field values

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import dump_api
from openapi_client.model.dump_put_error_response import DumpPUTErrorResponse
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
    api_instance = dump_api.DumpApi(api_client)
    request_body = [
        {},
    ] # [{str: (bool, date, datetime, dict, float, int, list, str, none_type)}] |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.dump_field_values_put(request_body=request_body)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling DumpApi->dump_field_values_put: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | **[{str: (bool, date, datetime, dict, float, int, list, str, none_type)}]**|  | [optional]

### Return type

**str**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **dump_load_fixture_post**
> [{str: (bool, date, datetime, dict, float, int, list, str, none_type)}] dump_load_fixture_post()



Install model fixtures

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import dump_api
from openapi_client.model.load_fixture import LoadFixture
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
    api_instance = dump_api.DumpApi(api_client)
    load_fixture = LoadFixture(
        fixture="fixture_example",
        mode="default",
        encoding="utf=8",
    ) # LoadFixture |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.dump_load_fixture_post(load_fixture=load_fixture)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling DumpApi->dump_load_fixture_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **load_fixture** | [**LoadFixture**](LoadFixture.md)|  | [optional]

### Return type

**[{str: (bool, date, datetime, dict, float, int, list, str, none_type)}]**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

