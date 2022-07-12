# openapi_client.TusApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**tus_upload_session_upload_session_id_upload_guid_patch**](TusApi.md#tus_upload_session_upload_session_id_upload_guid_patch) | **PATCH** /api/v1/tus/upload-session/{upload_session_id}/upload/{guid}/ | 
[**tus_upload_session_upload_session_id_upload_post**](TusApi.md#tus_upload_session_upload_session_id_upload_post) | **POST** /api/v1/tus/upload-session/{upload_session_id}/upload/ | 


# **tus_upload_session_upload_session_id_upload_guid_patch**
> TusUploadSessionUploadSessionIdUploadPOST400Response tus_upload_session_upload_session_id_upload_guid_patch(upload_session_id, guid, upload_offset, tus_resumable)



Transfer file data

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import tus_api
from openapi_client.model.tus_upload_session_upload_session_id_upload_post400_response import TusUploadSessionUploadSessionIdUploadPOST400Response
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
    api_instance = tus_api.TusApi(api_client)
    upload_session_id = "upload_session_id_example" # str | 
    guid = "guid_example" # str | 
    upload_offset = 1 # int | Upload offset, bytes.
    tus_resumable = "Tus-Resumable_example" # str | 1.0.0
    force = True # bool | Upload a file even if it exists. (optional)
    body = open('/path/to/file', 'rb') # file_type |  (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.tus_upload_session_upload_session_id_upload_guid_patch(upload_session_id, guid, upload_offset, tus_resumable)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TusApi->tus_upload_session_upload_session_id_upload_guid_patch: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.tus_upload_session_upload_session_id_upload_guid_patch(upload_session_id, guid, upload_offset, tus_resumable, force=force, body=body)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TusApi->tus_upload_session_upload_session_id_upload_guid_patch: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **upload_session_id** | **str**|  |
 **guid** | **str**|  |
 **upload_offset** | **int**| Upload offset, bytes. |
 **tus_resumable** | **str**| 1.0.0 |
 **force** | **bool**| Upload a file even if it exists. | [optional]
 **body** | **file_type**|  | [optional]

### Return type

[**TusUploadSessionUploadSessionIdUploadPOST400Response**](TusUploadSessionUploadSessionIdUploadPOST400Response.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/offset+octet-stream
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** |  |  * Upload-Offset -  <br>  * Upload-Expires -  <br>  * Tus-Resumable -  <br>  |
**400** |  |  -  |
**460** |  |  -  |
**500** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **tus_upload_session_upload_session_id_upload_post**
> tus_upload_session_upload_session_id_upload_post(upload_session_id, upload_length, upload_metadata, tus_resumable)



Create an Upload

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import tus_api
from openapi_client.model.tus_upload_session_upload_session_id_upload_post400_response import TusUploadSessionUploadSessionIdUploadPOST400Response
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
    api_instance = tus_api.TusApi(api_client)
    upload_session_id = "upload_session_id_example" # str | 
    upload_length = 1 # int | File length.
    upload_metadata = "Upload-Metadata_example" # str | Upload metadata include file name, relative path, etc.
    tus_resumable = "Tus-Resumable_example" # str | 1.0.0
    force = True # bool | Upload a file even if it exists. (optional)
    request_body = {} # {str: (bool, date, datetime, dict, float, int, list, str, none_type)} |  (optional)

    # example passing only required values which don't have defaults set
    try:
        api_instance.tus_upload_session_upload_session_id_upload_post(upload_session_id, upload_length, upload_metadata, tus_resumable)
    except openapi_client.ApiException as e:
        print("Exception when calling TusApi->tus_upload_session_upload_session_id_upload_post: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_instance.tus_upload_session_upload_session_id_upload_post(upload_session_id, upload_length, upload_metadata, tus_resumable, force=force, request_body=request_body)
    except openapi_client.ApiException as e:
        print("Exception when calling TusApi->tus_upload_session_upload_session_id_upload_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **upload_session_id** | **str**|  |
 **upload_length** | **int**| File length. |
 **upload_metadata** | **str**| Upload metadata include file name, relative path, etc. |
 **tus_resumable** | **str**| 1.0.0 |
 **force** | **bool**| Upload a file even if it exists. | [optional]
 **request_body** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}**|  | [optional]

### Return type

void (empty response body)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  * Location -  <br>  * Upload-Expires -  <br>  * Tus-Resumable -  <br>  |
**400** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

