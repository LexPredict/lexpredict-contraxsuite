# openapi_client.MediaDataApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**media_data_path_get**](MediaDataApi.md#media_data_path_get) | **GET** /api/media-data/{path}/ | 


# **media_data_path_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} media_data_path_get(path)



If directory:   action: None: - list directory   action: download - list directory (TODO - download directory)   action: info: - dict(info about directory) If file:   action: None: - show file   action: download - download file   action: info: - dict(info about directory)  :param request: :param path: str - relative path in /media directory  :query param action: optional str [\"download\", \"info\"] :return:

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import media_data_api
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
    api_instance = media_data_api.MediaDataApi(api_client)
    path = "path_example" # str | 
    action = "download" # str | Action name (optional) if omitted the server will use the default value of "download"

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.media_data_path_get(path)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling MediaDataApi->media_data_path_get: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.media_data_path_get(path, action=action)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling MediaDataApi->media_data_path_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **path** | **str**|  |
 **action** | **str**| Action name | [optional] if omitted the server will use the default value of "download"

### Return type

**{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, */*


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

