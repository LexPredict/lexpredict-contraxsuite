# openapi_client.NotificationsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**notifications_web_notifications_get**](NotificationsApi.md#notifications_web_notifications_get) | **GET** /api/v1/notifications/web-notifications/ | 
[**notifications_web_notifications_mark_seen_post**](NotificationsApi.md#notifications_web_notifications_mark_seen_post) | **POST** /api/v1/notifications/web-notifications/mark_seen/ | 


# **notifications_web_notifications_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} notifications_web_notifications_get()



Web Notification List

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import notifications_api
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
    api_instance = notifications_api.NotificationsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_response = api_instance.notifications_web_notifications_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling NotificationsApi->notifications_web_notifications_get: %s\n" % e)
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

# **notifications_web_notifications_mark_seen_post**
> MarkForSeenWebNotificationResponse notifications_web_notifications_mark_seen_post()



Method marks a number of web notifications for updating as seen/not seen. :param request: provide a list of web notification message ids here:

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import notifications_api
from openapi_client.model.mark_for_seen_web_notification_request import MarkForSeenWebNotificationRequest
from openapi_client.model.mark_for_seen_web_notification_response import MarkForSeenWebNotificationResponse
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
    api_instance = notifications_api.NotificationsApi(api_client)
    mark_for_seen_web_notification_request = MarkForSeenWebNotificationRequest(
        notification_ids=[
            1,
        ],
        is_seen=True,
    ) # MarkForSeenWebNotificationRequest |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.notifications_web_notifications_mark_seen_post(mark_for_seen_web_notification_request=mark_for_seen_web_notification_request)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling NotificationsApi->notifications_web_notifications_mark_seen_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mark_for_seen_web_notification_request** | [**MarkForSeenWebNotificationRequest**](MarkForSeenWebNotificationRequest.md)|  | [optional]

### Return type

[**MarkForSeenWebNotificationResponse**](MarkForSeenWebNotificationResponse.md)

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

