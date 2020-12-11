# TusApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**tusUploadSessionUploadSessionIdUploadGuidPATCH**](TusApi.md#tusUploadSessionUploadSessionIdUploadGuidPATCH) | **PATCH** /api/v1/tus/upload-session/{upload_session_id}/upload/{guid}/ | 
[**tusUploadSessionUploadSessionIdUploadPOST**](TusApi.md#tusUploadSessionUploadSessionIdUploadPOST) | **POST** /api/v1/tus/upload-session/{upload_session_id}/upload/ | 


<a name="tusUploadSessionUploadSessionIdUploadGuidPATCH"></a>
# **tusUploadSessionUploadSessionIdUploadGuidPATCH**
> InlineResponse400 tusUploadSessionUploadSessionIdUploadGuidPATCH(uploadSessionId, guid, uploadOffset, tusResumable, force, body)



Transfer file data

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.TusApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    TusApi apiInstance = new TusApi(defaultClient);
    String uploadSessionId = "uploadSessionId_example"; // String | 
    String guid = "guid_example"; // String | 
    Integer uploadOffset = 56; // Integer | Upload offset, bytes.
    String tusResumable = "tusResumable_example"; // String | 1.0.0
    Boolean force = true; // Boolean | Upload a file even if it exists.
    File body = new File("/path/to/file"); // File | 
    try {
      InlineResponse400 result = apiInstance.tusUploadSessionUploadSessionIdUploadGuidPATCH(uploadSessionId, guid, uploadOffset, tusResumable, force, body);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling TusApi#tusUploadSessionUploadSessionIdUploadGuidPATCH");
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
 **uploadSessionId** | **String**|  |
 **guid** | **String**|  |
 **uploadOffset** | **Integer**| Upload offset, bytes. |
 **tusResumable** | **String**| 1.0.0 |
 **force** | **Boolean**| Upload a file even if it exists. | [optional]
 **body** | **File**|  | [optional]

### Return type

[**InlineResponse400**](InlineResponse400.md)

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

<a name="tusUploadSessionUploadSessionIdUploadPOST"></a>
# **tusUploadSessionUploadSessionIdUploadPOST**
> tusUploadSessionUploadSessionIdUploadPOST(uploadSessionId, uploadLength, uploadMetadata, tusResumable, force, body)



Create an Upload

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.TusApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    TusApi apiInstance = new TusApi(defaultClient);
    String uploadSessionId = "uploadSessionId_example"; // String | 
    Integer uploadLength = 56; // Integer | File length.
    String uploadMetadata = "uploadMetadata_example"; // String | Upload metadata include file name, relative path, etc.
    String tusResumable = "tusResumable_example"; // String | 1.0.0
    Boolean force = true; // Boolean | Upload a file even if it exists.
    Object body = null; // Object | 
    try {
      apiInstance.tusUploadSessionUploadSessionIdUploadPOST(uploadSessionId, uploadLength, uploadMetadata, tusResumable, force, body);
    } catch (ApiException e) {
      System.err.println("Exception when calling TusApi#tusUploadSessionUploadSessionIdUploadPOST");
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
 **uploadSessionId** | **String**|  |
 **uploadLength** | **Integer**| File length. |
 **uploadMetadata** | **String**| Upload metadata include file name, relative path, etc. |
 **tusResumable** | **String**| 1.0.0 |
 **force** | **Boolean**| Upload a file even if it exists. | [optional]
 **body** | **Object**|  | [optional]

### Return type

null (empty response body)

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

