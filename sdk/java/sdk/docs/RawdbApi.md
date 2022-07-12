# RawdbApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**rawdbConfigGET**](RawdbApi.md#rawdbConfigGET) | **GET** /api/v1/rawdb/config/ |  |
| [**rawdbDocumentsDocumentTypeCodeGET**](RawdbApi.md#rawdbDocumentsDocumentTypeCodeGET) | **GET** /api/v1/rawdb/documents/{document_type_code}/ |  |
| [**rawdbDocumentsDocumentTypeCodePOST**](RawdbApi.md#rawdbDocumentsDocumentTypeCodePOST) | **POST** /api/v1/rawdb/documents/{document_type_code}/ |  |
| [**rawdbProjectStatsProjectIdGET**](RawdbApi.md#rawdbProjectStatsProjectIdGET) | **GET** /api/v1/rawdb/project_stats/{project_id}/ |  |


<a name="rawdbConfigGET"></a>
# **rawdbConfigGET**
> Map&lt;String, Object&gt; rawdbConfigGET()





### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.RawdbApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    RawdbApi apiInstance = new RawdbApi(defaultClient);
    try {
      Map<String, Object> result = apiInstance.rawdbConfigGET();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling RawdbApi#rawdbConfigGET");
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
| **200** |  |  -  |

<a name="rawdbDocumentsDocumentTypeCodeGET"></a>
# **rawdbDocumentsDocumentTypeCodeGET**
> Map&lt;String, Object&gt; rawdbDocumentsDocumentTypeCodeGET(documentTypeCode, projectIds, columns, associatedText, asZip, fmt, limit, orderBy, savedFilters, saveFilter, returnReviewed, returnTotal, returnData, ignoreErrors, filters)





### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.RawdbApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    RawdbApi apiInstance = new RawdbApi(defaultClient);
    String documentTypeCode = "documentTypeCode_example"; // String | 
    String projectIds = "projectIds_example"; // String | Project ids separated by commas
    String columns = "columns_example"; // String | Column names separated by commas
    Boolean associatedText = true; // Boolean | Boolean - show associated text
    Boolean asZip = true; // Boolean | Boolean - export as zip
    String fmt = "json"; // String | Export format
    Integer limit = 56; // Integer | Page Size
    String orderBy = "orderBy_example"; // String | Sort order - column names separated by commas
    String savedFilters = "savedFilters_example"; // String | Saved filter ids separated by commas
    Boolean saveFilter = true; // Boolean | Save filter
    Boolean returnReviewed = true; // Boolean | Return Reviewed documents count
    Boolean returnTotal = true; // Boolean | Return total documents count
    Boolean returnData = true; // Boolean | Return data
    Boolean ignoreErrors = true; // Boolean | Ignore errors
    Map<String, String> filters = new HashMap(); // Map<String, String> | Filter params
    try {
      Map<String, Object> result = apiInstance.rawdbDocumentsDocumentTypeCodeGET(documentTypeCode, projectIds, columns, associatedText, asZip, fmt, limit, orderBy, savedFilters, saveFilter, returnReviewed, returnTotal, returnData, ignoreErrors, filters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling RawdbApi#rawdbDocumentsDocumentTypeCodeGET");
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
| **documentTypeCode** | **String**|  | |
| **projectIds** | **String**| Project ids separated by commas | [optional] |
| **columns** | **String**| Column names separated by commas | [optional] |
| **associatedText** | **Boolean**| Boolean - show associated text | [optional] |
| **asZip** | **Boolean**| Boolean - export as zip | [optional] |
| **fmt** | **String**| Export format | [optional] [enum: json, csv, xlsx] |
| **limit** | **Integer**| Page Size | [optional] |
| **orderBy** | **String**| Sort order - column names separated by commas | [optional] |
| **savedFilters** | **String**| Saved filter ids separated by commas | [optional] |
| **saveFilter** | **Boolean**| Save filter | [optional] |
| **returnReviewed** | **Boolean**| Return Reviewed documents count | [optional] |
| **returnTotal** | **Boolean**| Return total documents count | [optional] |
| **returnData** | **Boolean**| Return data | [optional] |
| **ignoreErrors** | **Boolean**| Ignore errors | [optional] |
| **filters** | [**Map&lt;String, String&gt;**](String.md)| Filter params | [optional] |

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
| **200** |  |  -  |

<a name="rawdbDocumentsDocumentTypeCodePOST"></a>
# **rawdbDocumentsDocumentTypeCodePOST**
> Map&lt;String, Object&gt; rawdbDocumentsDocumentTypeCodePOST(documentTypeCode, rawdbDocumentsPOSTRequest)



See .get() method signature, .post() method just reflects it and uses the same request.GET params to get data

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.RawdbApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    RawdbApi apiInstance = new RawdbApi(defaultClient);
    String documentTypeCode = "documentTypeCode_example"; // String | 
    RawdbDocumentsPOSTRequest rawdbDocumentsPOSTRequest = new RawdbDocumentsPOSTRequest(); // RawdbDocumentsPOSTRequest | 
    try {
      Map<String, Object> result = apiInstance.rawdbDocumentsDocumentTypeCodePOST(documentTypeCode, rawdbDocumentsPOSTRequest);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling RawdbApi#rawdbDocumentsDocumentTypeCodePOST");
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
| **documentTypeCode** | **String**|  | |
| **rawdbDocumentsPOSTRequest** | [**RawdbDocumentsPOSTRequest**](RawdbDocumentsPOSTRequest.md)|  | [optional] |

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

<a name="rawdbProjectStatsProjectIdGET"></a>
# **rawdbProjectStatsProjectIdGET**
> Map&lt;String, Object&gt; rawdbProjectStatsProjectIdGET(projectId)





### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.RawdbApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    RawdbApi apiInstance = new RawdbApi(defaultClient);
    String projectId = "projectId_example"; // String | 
    try {
      Map<String, Object> result = apiInstance.rawdbProjectStatsProjectIdGET(projectId);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling RawdbApi#rawdbProjectStatsProjectIdGET");
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
| **projectId** | **String**|  | |

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
| **200** |  |  -  |

