# Org.OpenAPITools.Api.TusApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**TusUploadSessionUploadSessionIdUploadGuidPATCH**](TusApi.md#tusuploadsessionuploadsessioniduploadguidpatch) | **PATCH** /api/v1/tus/upload-session/{upload_session_id}/upload/{guid}/ | 
[**TusUploadSessionUploadSessionIdUploadPOST**](TusApi.md#tusuploadsessionuploadsessioniduploadpost) | **POST** /api/v1/tus/upload-session/{upload_session_id}/upload/ | 



## TusUploadSessionUploadSessionIdUploadGuidPATCH

> TusUploadSessionUploadSessionIdUploadPOST400Response TusUploadSessionUploadSessionIdUploadGuidPATCH (string uploadSessionId, string guid, int uploadOffset, string tusResumable, bool? force = null, System.IO.Stream body = null)



Transfer file data

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class TusUploadSessionUploadSessionIdUploadGuidPATCHExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new TusApi(Configuration.Default);
            var uploadSessionId = "uploadSessionId_example";  // string | 
            var guid = "guid_example";  // string | 
            var uploadOffset = 56;  // int | Upload offset, bytes.
            var tusResumable = "tusResumable_example";  // string | 1.0.0
            var force = true;  // bool? | Upload a file even if it exists. (optional) 
            var body = new System.IO.MemoryStream(System.IO.File.ReadAllBytes("/path/to/file.txt"));  // System.IO.Stream |  (optional) 

            try
            {
                TusUploadSessionUploadSessionIdUploadPOST400Response result = apiInstance.TusUploadSessionUploadSessionIdUploadGuidPATCH(uploadSessionId, guid, uploadOffset, tusResumable, force, body);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling TusApi.TusUploadSessionUploadSessionIdUploadGuidPATCH: " + e.Message );
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
 **uploadSessionId** | **string**|  | 
 **guid** | **string**|  | 
 **uploadOffset** | **int**| Upload offset, bytes. | 
 **tusResumable** | **string**| 1.0.0 | 
 **force** | **bool?**| Upload a file even if it exists. | [optional] 
 **body** | **System.IO.Stream**|  | [optional] 

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
| **204** |  |  * Upload-Offset -  <br>  * Upload-Expires -  <br>  * Tus-Resumable -  <br>  |
| **400** |  |  -  |
| **460** |  |  -  |
| **500** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## TusUploadSessionUploadSessionIdUploadPOST

> void TusUploadSessionUploadSessionIdUploadPOST (string uploadSessionId, int uploadLength, string uploadMetadata, string tusResumable, bool? force = null, Dictionary<string, Object> requestBody = null)



Create an Upload

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class TusUploadSessionUploadSessionIdUploadPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new TusApi(Configuration.Default);
            var uploadSessionId = "uploadSessionId_example";  // string | 
            var uploadLength = 56;  // int | File length.
            var uploadMetadata = "uploadMetadata_example";  // string | Upload metadata include file name, relative path, etc.
            var tusResumable = "tusResumable_example";  // string | 1.0.0
            var force = true;  // bool? | Upload a file even if it exists. (optional) 
            var requestBody = new Dictionary<string, Object>(); // Dictionary<string, Object> |  (optional) 

            try
            {
                apiInstance.TusUploadSessionUploadSessionIdUploadPOST(uploadSessionId, uploadLength, uploadMetadata, tusResumable, force, requestBody);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling TusApi.TusUploadSessionUploadSessionIdUploadPOST: " + e.Message );
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
 **uploadSessionId** | **string**|  | 
 **uploadLength** | **int**| File length. | 
 **uploadMetadata** | **string**| Upload metadata include file name, relative path, etc. | 
 **tusResumable** | **string**| 1.0.0 | 
 **force** | **bool?**| Upload a file even if it exists. | [optional] 
 **requestBody** | [**Dictionary&lt;string, Object&gt;**](Object.md)|  | [optional] 

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
| **201** |  |  * Location -  <br>  * Upload-Expires -  <br>  * Tus-Resumable -  <br>  |
| **400** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

