# openapi_client.RawdbApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**rawdb_config_get**](RawdbApi.md#rawdb_config_get) | **GET** /api/v1/rawdb/config/ | 
[**rawdb_documents_document_type_code_get**](RawdbApi.md#rawdb_documents_document_type_code_get) | **GET** /api/v1/rawdb/documents/{document_type_code}/ | 
[**rawdb_documents_document_type_code_post**](RawdbApi.md#rawdb_documents_document_type_code_post) | **POST** /api/v1/rawdb/documents/{document_type_code}/ | 
[**rawdb_project_stats_project_id_get**](RawdbApi.md#rawdb_project_stats_project_id_get) | **GET** /api/v1/rawdb/project_stats/{project_id}/ | 
[**rawdb_social_accounts_get**](RawdbApi.md#rawdb_social_accounts_get) | **GET** /api/v1/rawdb/social_accounts/ | 


# **rawdb_config_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} rawdb_config_get()



### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import rawdb_api
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
    api_instance = rawdb_api.RawdbApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_response = api_instance.rawdb_config_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling RawdbApi->rawdb_config_get: %s\n" % e)
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

# **rawdb_documents_document_type_code_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} rawdb_documents_document_type_code_get(document_type_code)



### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import rawdb_api
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
    api_instance = rawdb_api.RawdbApi(api_client)
    document_type_code = "document_type_code_example" # str | 
    project_ids = "project_ids_example" # str | Project ids separated by commas (optional)
    columns = "columns_example" # str | Column names separated by commas (optional)
    associated_text = True # bool | Boolean - show associated text (optional)
    as_zip = True # bool | Boolean - export as zip (optional)
    fmt = "json" # str | Export format (optional)
    limit = 1 # int | Page Size (optional)
    order_by = "order_by_example" # str | Sort order - column names separated by commas (optional)
    saved_filters = "saved_filters_example" # str | Saved filter ids separated by commas (optional)
    save_filter = True # bool | Save filter (optional)
    return_reviewed = True # bool | Return Reviewed documents count (optional)
    return_total = True # bool | Return total documents count (optional)
    return_data = True # bool | Return data (optional)
    ignore_errors = True # bool | Ignore errors (optional)
    filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.rawdb_documents_document_type_code_get(document_type_code)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling RawdbApi->rawdb_documents_document_type_code_get: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.rawdb_documents_document_type_code_get(document_type_code, project_ids=project_ids, columns=columns, associated_text=associated_text, as_zip=as_zip, fmt=fmt, limit=limit, order_by=order_by, saved_filters=saved_filters, save_filter=save_filter, return_reviewed=return_reviewed, return_total=return_total, return_data=return_data, ignore_errors=ignore_errors, filters=filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling RawdbApi->rawdb_documents_document_type_code_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_type_code** | **str**|  |
 **project_ids** | **str**| Project ids separated by commas | [optional]
 **columns** | **str**| Column names separated by commas | [optional]
 **associated_text** | **bool**| Boolean - show associated text | [optional]
 **as_zip** | **bool**| Boolean - export as zip | [optional]
 **fmt** | **str**| Export format | [optional]
 **limit** | **int**| Page Size | [optional]
 **order_by** | **str**| Sort order - column names separated by commas | [optional]
 **saved_filters** | **str**| Saved filter ids separated by commas | [optional]
 **save_filter** | **bool**| Save filter | [optional]
 **return_reviewed** | **bool**| Return Reviewed documents count | [optional]
 **return_total** | **bool**| Return total documents count | [optional]
 **return_data** | **bool**| Return data | [optional]
 **ignore_errors** | **bool**| Ignore errors | [optional]
 **filters** | **{str: (str,)}**| Filter params | [optional]

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

# **rawdb_documents_document_type_code_post**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} rawdb_documents_document_type_code_post(document_type_code)



See .get() method signature, .post() method just reflects it and uses the same request.GET params to get data

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import rawdb_api
from openapi_client.model.rawdb_documents_post_request import RawdbDocumentsPOSTRequest
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
    api_instance = rawdb_api.RawdbApi(api_client)
    document_type_code = "document_type_code_example" # str | 
    rawdb_documents_post_request = RawdbDocumentsPOSTRequest(
        project_ids="project_ids_example",
        columns="columns_example",
        associated_text=True,
        as_zip=True,
        fmt="fmt_example",
        limit=1,
        order_by="order_by_example",
        saved_filters="saved_filters_example",
        save_filter=True,
        return_reviewed=True,
        return_total=True,
        return_data=True,
        ignore_errors=True,
        filters={
            "key": "key_example",
        },
    ) # RawdbDocumentsPOSTRequest |  (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.rawdb_documents_document_type_code_post(document_type_code)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling RawdbApi->rawdb_documents_document_type_code_post: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.rawdb_documents_document_type_code_post(document_type_code, rawdb_documents_post_request=rawdb_documents_post_request)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling RawdbApi->rawdb_documents_document_type_code_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_type_code** | **str**|  |
 **rawdb_documents_post_request** | [**RawdbDocumentsPOSTRequest**](RawdbDocumentsPOSTRequest.md)|  | [optional]

### Return type

**{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**

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

# **rawdb_project_stats_project_id_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} rawdb_project_stats_project_id_get(project_id)



### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import rawdb_api
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
    api_instance = rawdb_api.RawdbApi(api_client)
    project_id = "project_id_example" # str | 

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.rawdb_project_stats_project_id_get(project_id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling RawdbApi->rawdb_project_stats_project_id_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  |

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

# **rawdb_social_accounts_get**
> SocialAccountsResponse rawdb_social_accounts_get()



### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import rawdb_api
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
    api_instance = rawdb_api.RawdbApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_response = api_instance.rawdb_social_accounts_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling RawdbApi->rawdb_social_accounts_get: %s\n" % e)
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

