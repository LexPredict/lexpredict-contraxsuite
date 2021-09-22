# Org.OpenAPITools.Api.NotificationsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**NotificationsWebNotificationsGET**](NotificationsApi.md#notificationswebnotificationsget) | **GET** /api/v1/notifications/web-notifications/ | 
[**NotificationsWebNotificationsMarkSeenPOST**](NotificationsApi.md#notificationswebnotificationsmarkseenpost) | **POST** /api/v1/notifications/web-notifications/mark_seen/ | 



## NotificationsWebNotificationsGET

> Dictionary&lt;string, Object&gt; NotificationsWebNotificationsGET ()



Web Notification List

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class NotificationsWebNotificationsGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new NotificationsApi(Configuration.Default);

            try
            {
                Dictionary<string, Object> result = apiInstance.NotificationsWebNotificationsGET();
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling NotificationsApi.NotificationsWebNotificationsGET: " + e.Message );
                Debug.Print("Status Code: "+ e.ErrorCode);
                Debug.Print(e.StackTrace);
            }
        }
    }
}
```

### Parameters

This endpoint does not need any parameter.

### Return type

**Dictionary<string, Object>**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## NotificationsWebNotificationsMarkSeenPOST

> MarkForSeenWebNotificationResponse NotificationsWebNotificationsMarkSeenPOST (MarkForSeenWebNotificationRequest markForSeenWebNotificationRequest = null)



Method marks a number of web notifications for updating as seen/not seen. :param request: provide a list of web notification message ids here:

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class NotificationsWebNotificationsMarkSeenPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new NotificationsApi(Configuration.Default);
            var markForSeenWebNotificationRequest = new MarkForSeenWebNotificationRequest(); // MarkForSeenWebNotificationRequest |  (optional) 

            try
            {
                MarkForSeenWebNotificationResponse result = apiInstance.NotificationsWebNotificationsMarkSeenPOST(markForSeenWebNotificationRequest);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling NotificationsApi.NotificationsWebNotificationsMarkSeenPOST: " + e.Message );
                Debug.Print("Status Code: "+ e.ErrorCode);
                Debug.Print(e.StackTrace);
            }
        }
    }
}
```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **markForSeenWebNotificationRequest** | [**MarkForSeenWebNotificationRequest**](MarkForSeenWebNotificationRequest.md)|  | [optional] 

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
| **201** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

