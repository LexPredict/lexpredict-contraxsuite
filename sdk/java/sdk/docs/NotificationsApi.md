# NotificationsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**notificationsWebNotificationsGET**](NotificationsApi.md#notificationsWebNotificationsGET) | **GET** /api/v1/notifications/web-notifications/ | 
[**notificationsWebNotificationsMarkSeenPOST**](NotificationsApi.md#notificationsWebNotificationsMarkSeenPOST) | **POST** /api/v1/notifications/web-notifications/mark_seen/ | 


<a name="notificationsWebNotificationsGET"></a>
# **notificationsWebNotificationsGET**
> Map&lt;String, Object&gt; notificationsWebNotificationsGET()



Web Notification List

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.NotificationsApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    NotificationsApi apiInstance = new NotificationsApi(defaultClient);
    try {
      Map<String, Object> result = apiInstance.notificationsWebNotificationsGET();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling NotificationsApi#notificationsWebNotificationsGET");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
    }
  }
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

**Map&lt;String, Object&gt;**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="notificationsWebNotificationsMarkSeenPOST"></a>
# **notificationsWebNotificationsMarkSeenPOST**
> MarkForSeenWebNotificationResponse notificationsWebNotificationsMarkSeenPOST(markForSeenWebNotificationRequest)



Method marks a number of web notifications for updating as seen/not seen. :param request: provide a list of web notification message ids here:

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.NotificationsApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    NotificationsApi apiInstance = new NotificationsApi(defaultClient);
    MarkForSeenWebNotificationRequest markForSeenWebNotificationRequest = new MarkForSeenWebNotificationRequest(); // MarkForSeenWebNotificationRequest | 
    try {
      MarkForSeenWebNotificationResponse result = apiInstance.notificationsWebNotificationsMarkSeenPOST(markForSeenWebNotificationRequest);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling NotificationsApi#notificationsWebNotificationsMarkSeenPOST");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
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
**201** |  |  -  |

