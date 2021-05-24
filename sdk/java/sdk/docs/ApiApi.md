# ApiApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**listLocales**](ApiApi.md#listLocales) | **GET** /api/v1/project/locales/ | 


<a name="listLocales"></a>
# **listLocales**
> List&lt;Map&lt;String, Object&gt;&gt; listLocales()



### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.ApiApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    ApiApi apiInstance = new ApiApi(defaultClient);
    try {
      List<Map<String, Object>> result = apiInstance.listLocales();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling ApiApi#listLocales");
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

[**List&lt;Map&lt;String, Object&gt;&gt;**](Map.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**500** |  |  -  |

