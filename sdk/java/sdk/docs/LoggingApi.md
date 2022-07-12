# LoggingApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**loggingLogMessagePOST**](LoggingApi.md#loggingLogMessagePOST) | **POST** /api/v1/logging/log_message/ |  |


<a name="loggingLogMessagePOST"></a>
# **loggingLogMessagePOST**
> Map&lt;String, Object&gt; loggingLogMessagePOST(loggingAPIViewRequest)



Log provided data

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.LoggingApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    LoggingApi apiInstance = new LoggingApi(defaultClient);
    LoggingAPIViewRequest loggingAPIViewRequest = new LoggingAPIViewRequest(); // LoggingAPIViewRequest | 
    try {
      Map<String, Object> result = apiInstance.loggingLogMessagePOST(loggingAPIViewRequest);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling LoggingApi#loggingLogMessagePOST");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
    }
  }
}
```

### Parameters

| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **loggingAPIViewRequest** | [**LoggingAPIViewRequest**](LoggingAPIViewRequest.md)|  | [optional] |

### Return type

**Map&lt;String, Object&gt;**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |
| **400** |  |  -  |
| **500** |  |  -  |

