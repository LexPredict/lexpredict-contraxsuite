# Org.OpenAPITools.Api.LoggingApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**LoggingLogMessagePOST**](LoggingApi.md#logginglogmessagepost) | **POST** /api/v1/logging/log_message/ | 



## LoggingLogMessagePOST

> Dictionary&lt;string, Object&gt; LoggingLogMessagePOST (LoggingAPIViewRequest loggingAPIViewRequest = null)



Log provided data

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class LoggingLogMessagePOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new LoggingApi(Configuration.Default);
            var loggingAPIViewRequest = new LoggingAPIViewRequest(); // LoggingAPIViewRequest |  (optional) 

            try
            {
                Dictionary<string, Object> result = apiInstance.LoggingLogMessagePOST(loggingAPIViewRequest);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling LoggingApi.LoggingLogMessagePOST: " + e.Message );
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
 **loggingAPIViewRequest** | [**LoggingAPIViewRequest**](LoggingAPIViewRequest.md)|  | [optional] 

### Return type

**Dictionary<string, Object>**

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

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

