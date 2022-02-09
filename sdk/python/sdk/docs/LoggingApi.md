# openapi_client.LoggingApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**logging_log_message_post**](LoggingApi.md#logging_log_message_post) | **POST** /api/v1/logging/log_message/ | 


# **logging_log_message_post**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} logging_log_message_post()



Log provided data

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import logging_api
from openapi_client.model.logging_api_view_request import LoggingAPIViewRequest
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
    api_instance = logging_api.LoggingApi(api_client)
    logging_api_view_request = LoggingAPIViewRequest(
        query_info={},
        records=[
            {},
        ],
    ) # LoggingAPIViewRequest |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.logging_log_message_post(logging_api_view_request=logging_api_view_request)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling LoggingApi->logging_log_message_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **logging_api_view_request** | [**LoggingAPIViewRequest**](LoggingAPIViewRequest.md)|  | [optional]

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
**400** |  |  -  |
**500** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

