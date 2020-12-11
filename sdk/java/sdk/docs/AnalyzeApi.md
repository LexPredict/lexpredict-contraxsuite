# AnalyzeApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**analyzeDocumentClusterGET**](AnalyzeApi.md#analyzeDocumentClusterGET) | **GET** /api/v1/analyze/document-cluster/ | 
[**analyzeDocumentClusterIdGET**](AnalyzeApi.md#analyzeDocumentClusterIdGET) | **GET** /api/v1/analyze/document-cluster/{id}/ | 
[**analyzeDocumentClusterIdPATCH**](AnalyzeApi.md#analyzeDocumentClusterIdPATCH) | **PATCH** /api/v1/analyze/document-cluster/{id}/ | 
[**analyzeDocumentClusterIdPUT**](AnalyzeApi.md#analyzeDocumentClusterIdPUT) | **PUT** /api/v1/analyze/document-cluster/{id}/ | 
[**analyzeDocumentSimilarityListGET**](AnalyzeApi.md#analyzeDocumentSimilarityListGET) | **GET** /api/v1/analyze/document-similarity/list/ | 
[**analyzePartySimilarityListGET**](AnalyzeApi.md#analyzePartySimilarityListGET) | **GET** /api/v1/analyze/party-similarity/list/ | 
[**analyzeTextUnitClassificationsGET**](AnalyzeApi.md#analyzeTextUnitClassificationsGET) | **GET** /api/v1/analyze/text-unit-classifications/ | 
[**analyzeTextUnitClassificationsIdDELETE**](AnalyzeApi.md#analyzeTextUnitClassificationsIdDELETE) | **DELETE** /api/v1/analyze/text-unit-classifications/{id}/ | 
[**analyzeTextUnitClassificationsIdGET**](AnalyzeApi.md#analyzeTextUnitClassificationsIdGET) | **GET** /api/v1/analyze/text-unit-classifications/{id}/ | 
[**analyzeTextUnitClassificationsPOST**](AnalyzeApi.md#analyzeTextUnitClassificationsPOST) | **POST** /api/v1/analyze/text-unit-classifications/ | 
[**analyzeTextUnitClassifierSuggestionsGET**](AnalyzeApi.md#analyzeTextUnitClassifierSuggestionsGET) | **GET** /api/v1/analyze/text-unit-classifier-suggestions/ | 
[**analyzeTextUnitClassifierSuggestionsIdDELETE**](AnalyzeApi.md#analyzeTextUnitClassifierSuggestionsIdDELETE) | **DELETE** /api/v1/analyze/text-unit-classifier-suggestions/{id}/ | 
[**analyzeTextUnitClassifierSuggestionsIdGET**](AnalyzeApi.md#analyzeTextUnitClassifierSuggestionsIdGET) | **GET** /api/v1/analyze/text-unit-classifier-suggestions/{id}/ | 
[**analyzeTextUnitClassifiersGET**](AnalyzeApi.md#analyzeTextUnitClassifiersGET) | **GET** /api/v1/analyze/text-unit-classifiers/ | 
[**analyzeTextUnitClassifiersIdDELETE**](AnalyzeApi.md#analyzeTextUnitClassifiersIdDELETE) | **DELETE** /api/v1/analyze/text-unit-classifiers/{id}/ | 
[**analyzeTextUnitClassifiersIdGET**](AnalyzeApi.md#analyzeTextUnitClassifiersIdGET) | **GET** /api/v1/analyze/text-unit-classifiers/{id}/ | 
[**analyzeTextUnitClusterListGET**](AnalyzeApi.md#analyzeTextUnitClusterListGET) | **GET** /api/v1/analyze/text-unit-cluster/list/ | 
[**analyzeTextUnitSimilarityListGET**](AnalyzeApi.md#analyzeTextUnitSimilarityListGET) | **GET** /api/v1/analyze/text-unit-similarity/list/ | 
[**analyzeTypeaheadTextUnitClassificationFieldNameGET**](AnalyzeApi.md#analyzeTypeaheadTextUnitClassificationFieldNameGET) | **GET** /api/v1/analyze/typeahead/text-unit-classification/{field_name}/ | 


<a name="analyzeDocumentClusterGET"></a>
# **analyzeDocumentClusterGET**
> List&lt;DocumentCluster&gt; analyzeDocumentClusterGET(jqFilters)



Document Cluster List

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.AnalyzeApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    AnalyzeApi apiInstance = new AnalyzeApi(defaultClient);
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      List<DocumentCluster> result = apiInstance.analyzeDocumentClusterGET(jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AnalyzeApi#analyzeDocumentClusterGET");
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
 **jqFilters** | [**Map&lt;String, String&gt;**](String.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**List&lt;DocumentCluster&gt;**](DocumentCluster.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="analyzeDocumentClusterIdGET"></a>
# **analyzeDocumentClusterIdGET**
> DocumentCluster analyzeDocumentClusterIdGET(id, jqFilters)



Retrieve Document Cluster

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.AnalyzeApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    AnalyzeApi apiInstance = new AnalyzeApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this document cluster.
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      DocumentCluster result = apiInstance.analyzeDocumentClusterIdGET(id, jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AnalyzeApi#analyzeDocumentClusterIdGET");
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
 **id** | **String**| A unique integer value identifying this document cluster. |
 **jqFilters** | [**Map&lt;String, String&gt;**](String.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**DocumentCluster**](DocumentCluster.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="analyzeDocumentClusterIdPATCH"></a>
# **analyzeDocumentClusterIdPATCH**
> DocumentClusterUpdate analyzeDocumentClusterIdPATCH(id, documentClusterUpdate)



Partial Update Document Cluster (name)

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.AnalyzeApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    AnalyzeApi apiInstance = new AnalyzeApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this document cluster.
    DocumentClusterUpdate documentClusterUpdate = new DocumentClusterUpdate(); // DocumentClusterUpdate | 
    try {
      DocumentClusterUpdate result = apiInstance.analyzeDocumentClusterIdPATCH(id, documentClusterUpdate);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AnalyzeApi#analyzeDocumentClusterIdPATCH");
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
 **id** | **String**| A unique integer value identifying this document cluster. |
 **documentClusterUpdate** | [**DocumentClusterUpdate**](DocumentClusterUpdate.md)|  | [optional]

### Return type

[**DocumentClusterUpdate**](DocumentClusterUpdate.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="analyzeDocumentClusterIdPUT"></a>
# **analyzeDocumentClusterIdPUT**
> DocumentClusterUpdate analyzeDocumentClusterIdPUT(id, documentClusterUpdate)



Update Document Cluster (name)

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.AnalyzeApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    AnalyzeApi apiInstance = new AnalyzeApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this document cluster.
    DocumentClusterUpdate documentClusterUpdate = new DocumentClusterUpdate(); // DocumentClusterUpdate | 
    try {
      DocumentClusterUpdate result = apiInstance.analyzeDocumentClusterIdPUT(id, documentClusterUpdate);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AnalyzeApi#analyzeDocumentClusterIdPUT");
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
 **id** | **String**| A unique integer value identifying this document cluster. |
 **documentClusterUpdate** | [**DocumentClusterUpdate**](DocumentClusterUpdate.md)|  | [optional]

### Return type

[**DocumentClusterUpdate**](DocumentClusterUpdate.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="analyzeDocumentSimilarityListGET"></a>
# **analyzeDocumentSimilarityListGET**
> List&lt;DocumentSimilarity&gt; analyzeDocumentSimilarityListGET(jqFilters)



Document Similarity List

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.AnalyzeApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    AnalyzeApi apiInstance = new AnalyzeApi(defaultClient);
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      List<DocumentSimilarity> result = apiInstance.analyzeDocumentSimilarityListGET(jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AnalyzeApi#analyzeDocumentSimilarityListGET");
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
 **jqFilters** | [**Map&lt;String, String&gt;**](String.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**List&lt;DocumentSimilarity&gt;**](DocumentSimilarity.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="analyzePartySimilarityListGET"></a>
# **analyzePartySimilarityListGET**
> List&lt;PartySimilarity&gt; analyzePartySimilarityListGET(jqFilters)



Party Similarity List

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.AnalyzeApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    AnalyzeApi apiInstance = new AnalyzeApi(defaultClient);
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      List<PartySimilarity> result = apiInstance.analyzePartySimilarityListGET(jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AnalyzeApi#analyzePartySimilarityListGET");
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
 **jqFilters** | [**Map&lt;String, String&gt;**](String.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**List&lt;PartySimilarity&gt;**](PartySimilarity.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="analyzeTextUnitClassificationsGET"></a>
# **analyzeTextUnitClassificationsGET**
> List&lt;TextUnitClassification&gt; analyzeTextUnitClassificationsGET(jqFilters)



Text Unit Classification List

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.AnalyzeApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    AnalyzeApi apiInstance = new AnalyzeApi(defaultClient);
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      List<TextUnitClassification> result = apiInstance.analyzeTextUnitClassificationsGET(jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AnalyzeApi#analyzeTextUnitClassificationsGET");
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
 **jqFilters** | [**Map&lt;String, String&gt;**](String.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**List&lt;TextUnitClassification&gt;**](TextUnitClassification.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="analyzeTextUnitClassificationsIdDELETE"></a>
# **analyzeTextUnitClassificationsIdDELETE**
> analyzeTextUnitClassificationsIdDELETE(id)



Delete Text Unit Classification

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.AnalyzeApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    AnalyzeApi apiInstance = new AnalyzeApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this text unit classification.
    try {
      apiInstance.analyzeTextUnitClassificationsIdDELETE(id);
    } catch (ApiException e) {
      System.err.println("Exception when calling AnalyzeApi#analyzeTextUnitClassificationsIdDELETE");
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
 **id** | **String**| A unique integer value identifying this text unit classification. |

### Return type

null (empty response body)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** |  |  -  |

<a name="analyzeTextUnitClassificationsIdGET"></a>
# **analyzeTextUnitClassificationsIdGET**
> TextUnitClassification analyzeTextUnitClassificationsIdGET(id, jqFilters)



Retrieve Text Unit Classification

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.AnalyzeApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    AnalyzeApi apiInstance = new AnalyzeApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this text unit classification.
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      TextUnitClassification result = apiInstance.analyzeTextUnitClassificationsIdGET(id, jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AnalyzeApi#analyzeTextUnitClassificationsIdGET");
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
 **id** | **String**| A unique integer value identifying this text unit classification. |
 **jqFilters** | [**Map&lt;String, String&gt;**](String.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**TextUnitClassification**](TextUnitClassification.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="analyzeTextUnitClassificationsPOST"></a>
# **analyzeTextUnitClassificationsPOST**
> TextUnitClassificationCreate analyzeTextUnitClassificationsPOST(textUnitClassificationCreate)



Create Text Unit Classification

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.AnalyzeApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    AnalyzeApi apiInstance = new AnalyzeApi(defaultClient);
    TextUnitClassificationCreate textUnitClassificationCreate = new TextUnitClassificationCreate(); // TextUnitClassificationCreate | 
    try {
      TextUnitClassificationCreate result = apiInstance.analyzeTextUnitClassificationsPOST(textUnitClassificationCreate);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AnalyzeApi#analyzeTextUnitClassificationsPOST");
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
 **textUnitClassificationCreate** | [**TextUnitClassificationCreate**](TextUnitClassificationCreate.md)|  | [optional]

### Return type

[**TextUnitClassificationCreate**](TextUnitClassificationCreate.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

<a name="analyzeTextUnitClassifierSuggestionsGET"></a>
# **analyzeTextUnitClassifierSuggestionsGET**
> List&lt;TextUnitClassifierSuggestion&gt; analyzeTextUnitClassifierSuggestionsGET(jqFilters)



Text Unit Classifier Suggestion List

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.AnalyzeApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    AnalyzeApi apiInstance = new AnalyzeApi(defaultClient);
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      List<TextUnitClassifierSuggestion> result = apiInstance.analyzeTextUnitClassifierSuggestionsGET(jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AnalyzeApi#analyzeTextUnitClassifierSuggestionsGET");
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
 **jqFilters** | [**Map&lt;String, String&gt;**](String.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**List&lt;TextUnitClassifierSuggestion&gt;**](TextUnitClassifierSuggestion.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="analyzeTextUnitClassifierSuggestionsIdDELETE"></a>
# **analyzeTextUnitClassifierSuggestionsIdDELETE**
> analyzeTextUnitClassifierSuggestionsIdDELETE(id)



Delete Text Unit Classifier Suggestion

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.AnalyzeApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    AnalyzeApi apiInstance = new AnalyzeApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this text unit classifier suggestion.
    try {
      apiInstance.analyzeTextUnitClassifierSuggestionsIdDELETE(id);
    } catch (ApiException e) {
      System.err.println("Exception when calling AnalyzeApi#analyzeTextUnitClassifierSuggestionsIdDELETE");
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
 **id** | **String**| A unique integer value identifying this text unit classifier suggestion. |

### Return type

null (empty response body)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** |  |  -  |

<a name="analyzeTextUnitClassifierSuggestionsIdGET"></a>
# **analyzeTextUnitClassifierSuggestionsIdGET**
> TextUnitClassifierSuggestion analyzeTextUnitClassifierSuggestionsIdGET(id, jqFilters)



### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.AnalyzeApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    AnalyzeApi apiInstance = new AnalyzeApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this text unit classifier suggestion.
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      TextUnitClassifierSuggestion result = apiInstance.analyzeTextUnitClassifierSuggestionsIdGET(id, jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AnalyzeApi#analyzeTextUnitClassifierSuggestionsIdGET");
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
 **id** | **String**| A unique integer value identifying this text unit classifier suggestion. |
 **jqFilters** | [**Map&lt;String, String&gt;**](String.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**TextUnitClassifierSuggestion**](TextUnitClassifierSuggestion.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="analyzeTextUnitClassifiersGET"></a>
# **analyzeTextUnitClassifiersGET**
> List&lt;TextUnitClassifier&gt; analyzeTextUnitClassifiersGET(jqFilters)



Text Unit Classifier List

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.AnalyzeApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    AnalyzeApi apiInstance = new AnalyzeApi(defaultClient);
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      List<TextUnitClassifier> result = apiInstance.analyzeTextUnitClassifiersGET(jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AnalyzeApi#analyzeTextUnitClassifiersGET");
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
 **jqFilters** | [**Map&lt;String, String&gt;**](String.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**List&lt;TextUnitClassifier&gt;**](TextUnitClassifier.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="analyzeTextUnitClassifiersIdDELETE"></a>
# **analyzeTextUnitClassifiersIdDELETE**
> analyzeTextUnitClassifiersIdDELETE(id)



Delete Text Unit Classifier

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.AnalyzeApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    AnalyzeApi apiInstance = new AnalyzeApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this text unit classifier.
    try {
      apiInstance.analyzeTextUnitClassifiersIdDELETE(id);
    } catch (ApiException e) {
      System.err.println("Exception when calling AnalyzeApi#analyzeTextUnitClassifiersIdDELETE");
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
 **id** | **String**| A unique integer value identifying this text unit classifier. |

### Return type

null (empty response body)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** |  |  -  |

<a name="analyzeTextUnitClassifiersIdGET"></a>
# **analyzeTextUnitClassifiersIdGET**
> TextUnitClassifier analyzeTextUnitClassifiersIdGET(id, jqFilters)



### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.AnalyzeApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    AnalyzeApi apiInstance = new AnalyzeApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this text unit classifier.
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      TextUnitClassifier result = apiInstance.analyzeTextUnitClassifiersIdGET(id, jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AnalyzeApi#analyzeTextUnitClassifiersIdGET");
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
 **id** | **String**| A unique integer value identifying this text unit classifier. |
 **jqFilters** | [**Map&lt;String, String&gt;**](String.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**TextUnitClassifier**](TextUnitClassifier.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="analyzeTextUnitClusterListGET"></a>
# **analyzeTextUnitClusterListGET**
> List&lt;TextUnitCluster&gt; analyzeTextUnitClusterListGET(jqFilters)



Text Unit Cluster List

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.AnalyzeApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    AnalyzeApi apiInstance = new AnalyzeApi(defaultClient);
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      List<TextUnitCluster> result = apiInstance.analyzeTextUnitClusterListGET(jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AnalyzeApi#analyzeTextUnitClusterListGET");
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
 **jqFilters** | [**Map&lt;String, String&gt;**](String.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**List&lt;TextUnitCluster&gt;**](TextUnitCluster.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="analyzeTextUnitSimilarityListGET"></a>
# **analyzeTextUnitSimilarityListGET**
> List&lt;TextUnitSimilarity&gt; analyzeTextUnitSimilarityListGET(jqFilters)



Text Unit Similarity List

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.AnalyzeApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    AnalyzeApi apiInstance = new AnalyzeApi(defaultClient);
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      List<TextUnitSimilarity> result = apiInstance.analyzeTextUnitSimilarityListGET(jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AnalyzeApi#analyzeTextUnitSimilarityListGET");
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
 **jqFilters** | [**Map&lt;String, String&gt;**](String.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**List&lt;TextUnitSimilarity&gt;**](TextUnitSimilarity.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="analyzeTypeaheadTextUnitClassificationFieldNameGET"></a>
# **analyzeTypeaheadTextUnitClassificationFieldNameGET**
> Typeahead analyzeTypeaheadTextUnitClassificationFieldNameGET(fieldName, q)



Typeahead TextUnitClassification      Kwargs: field_name: [class_name, class_value]     GET params:       - q: str

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.AnalyzeApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    AnalyzeApi apiInstance = new AnalyzeApi(defaultClient);
    String fieldName = "fieldName_example"; // String | 
    String q = "q_example"; // String | Typeahead string
    try {
      Typeahead result = apiInstance.analyzeTypeaheadTextUnitClassificationFieldNameGET(fieldName, q);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AnalyzeApi#analyzeTypeaheadTextUnitClassificationFieldNameGET");
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
 **fieldName** | **String**|  |
 **q** | **String**| Typeahead string |

### Return type

[**Typeahead**](Typeahead.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

