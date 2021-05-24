# SimilarityApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**similarityDocumentSimilarityByFeaturesGET**](SimilarityApi.md#similarityDocumentSimilarityByFeaturesGET) | **GET** /api/v1/similarity/document-similarity-by-features/ | 
[**similarityDocumentSimilarityByFeaturesPOST**](SimilarityApi.md#similarityDocumentSimilarityByFeaturesPOST) | **POST** /api/v1/similarity/document-similarity-by-features/ | 
[**similarityPartySimilarityGET**](SimilarityApi.md#similarityPartySimilarityGET) | **GET** /api/v1/similarity/party-similarity/ | 
[**similarityPartySimilarityPOST**](SimilarityApi.md#similarityPartySimilarityPOST) | **POST** /api/v1/similarity/party-similarity/ | 
[**similarityProjectDocumentsSimilarityByVectorsGET**](SimilarityApi.md#similarityProjectDocumentsSimilarityByVectorsGET) | **GET** /api/v1/similarity/project-documents-similarity-by-vectors/ | 
[**similarityProjectDocumentsSimilarityByVectorsPOST**](SimilarityApi.md#similarityProjectDocumentsSimilarityByVectorsPOST) | **POST** /api/v1/similarity/project-documents-similarity-by-vectors/ | 
[**similarityProjectTextUnitsSimilarityByVectorsGET**](SimilarityApi.md#similarityProjectTextUnitsSimilarityByVectorsGET) | **GET** /api/v1/similarity/project-text-units-similarity-by-vectors/ | 
[**similarityProjectTextUnitsSimilarityByVectorsPOST**](SimilarityApi.md#similarityProjectTextUnitsSimilarityByVectorsPOST) | **POST** /api/v1/similarity/project-text-units-similarity-by-vectors/ | 
[**similaritySimilarityGET**](SimilarityApi.md#similaritySimilarityGET) | **GET** /api/v1/similarity/similarity/ | 
[**similaritySimilarityPOST**](SimilarityApi.md#similaritySimilarityPOST) | **POST** /api/v1/similarity/similarity/ | 
[**similarityTextUnitSimilarityByFeaturesGET**](SimilarityApi.md#similarityTextUnitSimilarityByFeaturesGET) | **GET** /api/v1/similarity/text-unit-similarity-by-features/ | 
[**similarityTextUnitSimilarityByFeaturesPOST**](SimilarityApi.md#similarityTextUnitSimilarityByFeaturesPOST) | **POST** /api/v1/similarity/text-unit-similarity-by-features/ | 


<a name="similarityDocumentSimilarityByFeaturesGET"></a>
# **similarityDocumentSimilarityByFeaturesGET**
> Map&lt;String, Object&gt; similarityDocumentSimilarityByFeaturesGET()



\&quot;Similarity\&quot; admin task  POST params:     - similarity_threshold: int     - use_tfidf: bool     - delete: bool     - project: int     - feature_source: list - list[date, definition, duration, court,       currency_name, currency_value, term, party, geoentity]     - distance_type: str - see scipy.spatial.distance._METRICS

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.SimilarityApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    SimilarityApi apiInstance = new SimilarityApi(defaultClient);
    try {
      Map<String, Object> result = apiInstance.similarityDocumentSimilarityByFeaturesGET();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling SimilarityApi#similarityDocumentSimilarityByFeaturesGET");
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

<a name="similarityDocumentSimilarityByFeaturesPOST"></a>
# **similarityDocumentSimilarityByFeaturesPOST**
> SimilarityPOSTObjectResponse similarityDocumentSimilarityByFeaturesPOST(documentSimilarityByFeaturesForm)



\&quot;Similarity\&quot; admin task  POST params:     - similarity_threshold: int     - use_tfidf: bool     - delete: bool     - project: int     - feature_source: list - list[date, definition, duration, court,       currency_name, currency_value, term, party, geoentity]     - distance_type: str - see scipy.spatial.distance._METRICS

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.SimilarityApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    SimilarityApi apiInstance = new SimilarityApi(defaultClient);
    DocumentSimilarityByFeaturesForm documentSimilarityByFeaturesForm = new DocumentSimilarityByFeaturesForm(); // DocumentSimilarityByFeaturesForm | 
    try {
      SimilarityPOSTObjectResponse result = apiInstance.similarityDocumentSimilarityByFeaturesPOST(documentSimilarityByFeaturesForm);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling SimilarityApi#similarityDocumentSimilarityByFeaturesPOST");
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
 **documentSimilarityByFeaturesForm** | [**DocumentSimilarityByFeaturesForm**](DocumentSimilarityByFeaturesForm.md)|  | [optional]

### Return type

[**SimilarityPOSTObjectResponse**](SimilarityPOSTObjectResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="similarityPartySimilarityGET"></a>
# **similarityPartySimilarityGET**
> Map&lt;String, Object&gt; similarityPartySimilarityGET()



\&quot;Party Similarity\&quot; admin task  POST params:     - case_sensitive: bool     - similarity_type: str[]     - similarity_threshold: int     - delete: bool

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.SimilarityApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    SimilarityApi apiInstance = new SimilarityApi(defaultClient);
    try {
      Map<String, Object> result = apiInstance.similarityPartySimilarityGET();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling SimilarityApi#similarityPartySimilarityGET");
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

<a name="similarityPartySimilarityPOST"></a>
# **similarityPartySimilarityPOST**
> SimilarityPOSTObjectResponse similarityPartySimilarityPOST(partySimilarityForm)



\&quot;Party Similarity\&quot; admin task  POST params:     - case_sensitive: bool     - similarity_type: str[]     - similarity_threshold: int     - delete: bool

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.SimilarityApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    SimilarityApi apiInstance = new SimilarityApi(defaultClient);
    PartySimilarityForm partySimilarityForm = new PartySimilarityForm(); // PartySimilarityForm | 
    try {
      SimilarityPOSTObjectResponse result = apiInstance.similarityPartySimilarityPOST(partySimilarityForm);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling SimilarityApi#similarityPartySimilarityPOST");
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
 **partySimilarityForm** | [**PartySimilarityForm**](PartySimilarityForm.md)|  | [optional]

### Return type

[**SimilarityPOSTObjectResponse**](SimilarityPOSTObjectResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="similarityProjectDocumentsSimilarityByVectorsGET"></a>
# **similarityProjectDocumentsSimilarityByVectorsGET**
> Map&lt;String, Object&gt; similarityProjectDocumentsSimilarityByVectorsGET()



\&quot;Similarity\&quot; admin task  POST params:     - project_id: int     - distance_type: str - see scipy.spatial.distance._METRICS     - similarity_threshold: int     - feature_source: \&quot;vector\&quot;     - create_reverse_relations: bool - create B-A relations     - item_id: int     - use_tfidf: bool     - delete: bool

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.SimilarityApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    SimilarityApi apiInstance = new SimilarityApi(defaultClient);
    try {
      Map<String, Object> result = apiInstance.similarityProjectDocumentsSimilarityByVectorsGET();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling SimilarityApi#similarityProjectDocumentsSimilarityByVectorsGET");
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

<a name="similarityProjectDocumentsSimilarityByVectorsPOST"></a>
# **similarityProjectDocumentsSimilarityByVectorsPOST**
> SimilarityPOSTObjectResponse similarityProjectDocumentsSimilarityByVectorsPOST(projectDocumentsSimilarityByVectorsForm)



\&quot;Similarity\&quot; admin task  POST params:     - project_id: int     - distance_type: str - see scipy.spatial.distance._METRICS     - similarity_threshold: int     - feature_source: \&quot;vector\&quot;     - create_reverse_relations: bool - create B-A relations     - item_id: int     - use_tfidf: bool     - delete: bool

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.SimilarityApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    SimilarityApi apiInstance = new SimilarityApi(defaultClient);
    ProjectDocumentsSimilarityByVectorsForm projectDocumentsSimilarityByVectorsForm = new ProjectDocumentsSimilarityByVectorsForm(); // ProjectDocumentsSimilarityByVectorsForm | 
    try {
      SimilarityPOSTObjectResponse result = apiInstance.similarityProjectDocumentsSimilarityByVectorsPOST(projectDocumentsSimilarityByVectorsForm);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling SimilarityApi#similarityProjectDocumentsSimilarityByVectorsPOST");
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
 **projectDocumentsSimilarityByVectorsForm** | [**ProjectDocumentsSimilarityByVectorsForm**](ProjectDocumentsSimilarityByVectorsForm.md)|  | [optional]

### Return type

[**SimilarityPOSTObjectResponse**](SimilarityPOSTObjectResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="similarityProjectTextUnitsSimilarityByVectorsGET"></a>
# **similarityProjectTextUnitsSimilarityByVectorsGET**
> Map&lt;String, Object&gt; similarityProjectTextUnitsSimilarityByVectorsGET()



\&quot;Similarity\&quot; admin task  POST params:     - project_id: int     - distance_type: str - see scipy.spatial.distance._METRICS     - similarity_threshold: int     - unit_type: str sentence|paragraph     - feature_source: \&quot;vector\&quot;     - create_reverse_relations: bool - create B-A relations     - use_tfidf: bool     - delete: bool

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.SimilarityApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    SimilarityApi apiInstance = new SimilarityApi(defaultClient);
    try {
      Map<String, Object> result = apiInstance.similarityProjectTextUnitsSimilarityByVectorsGET();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling SimilarityApi#similarityProjectTextUnitsSimilarityByVectorsGET");
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

<a name="similarityProjectTextUnitsSimilarityByVectorsPOST"></a>
# **similarityProjectTextUnitsSimilarityByVectorsPOST**
> SimilarityPOSTObjectResponse similarityProjectTextUnitsSimilarityByVectorsPOST(projectTextUnitsSimilarityByVectorsForm)



\&quot;Similarity\&quot; admin task  POST params:     - project_id: int     - distance_type: str - see scipy.spatial.distance._METRICS     - similarity_threshold: int     - unit_type: str sentence|paragraph     - feature_source: \&quot;vector\&quot;     - create_reverse_relations: bool - create B-A relations     - use_tfidf: bool     - delete: bool

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.SimilarityApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    SimilarityApi apiInstance = new SimilarityApi(defaultClient);
    ProjectTextUnitsSimilarityByVectorsForm projectTextUnitsSimilarityByVectorsForm = new ProjectTextUnitsSimilarityByVectorsForm(); // ProjectTextUnitsSimilarityByVectorsForm | 
    try {
      SimilarityPOSTObjectResponse result = apiInstance.similarityProjectTextUnitsSimilarityByVectorsPOST(projectTextUnitsSimilarityByVectorsForm);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling SimilarityApi#similarityProjectTextUnitsSimilarityByVectorsPOST");
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
 **projectTextUnitsSimilarityByVectorsForm** | [**ProjectTextUnitsSimilarityByVectorsForm**](ProjectTextUnitsSimilarityByVectorsForm.md)|  | [optional]

### Return type

[**SimilarityPOSTObjectResponse**](SimilarityPOSTObjectResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="similaritySimilarityGET"></a>
# **similaritySimilarityGET**
> Map&lt;String, Object&gt; similaritySimilarityGET()



\&quot;Similarity\&quot; admin task  POST params:     - search_similar_documents: bool     - search_similar_text_units: bool     - similarity_threshold: int     - use_idf: bool     - delete: bool     - project: bool

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.SimilarityApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    SimilarityApi apiInstance = new SimilarityApi(defaultClient);
    try {
      Map<String, Object> result = apiInstance.similaritySimilarityGET();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling SimilarityApi#similaritySimilarityGET");
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

<a name="similaritySimilarityPOST"></a>
# **similaritySimilarityPOST**
> SimilarityPOSTObjectResponse similaritySimilarityPOST(similarityForm)



\&quot;Similarity\&quot; admin task  POST params:     - search_similar_documents: bool     - search_similar_text_units: bool     - similarity_threshold: int     - use_idf: bool     - delete: bool     - project: bool

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.SimilarityApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    SimilarityApi apiInstance = new SimilarityApi(defaultClient);
    SimilarityForm similarityForm = new SimilarityForm(); // SimilarityForm | 
    try {
      SimilarityPOSTObjectResponse result = apiInstance.similaritySimilarityPOST(similarityForm);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling SimilarityApi#similaritySimilarityPOST");
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
 **similarityForm** | [**SimilarityForm**](SimilarityForm.md)|  | [optional]

### Return type

[**SimilarityPOSTObjectResponse**](SimilarityPOSTObjectResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="similarityTextUnitSimilarityByFeaturesGET"></a>
# **similarityTextUnitSimilarityByFeaturesGET**
> Map&lt;String, Object&gt; similarityTextUnitSimilarityByFeaturesGET()



\&quot;Similarity\&quot; admin task  POST params:     - similarity_threshold: int     - use_tfidf: bool     - delete: bool     - project: int     - feature_source: list - list[date, definition, duration, court,       currency_name, currency_value, term, party, geoentity]     - unit_type: str sentence|paragraph     - distance_type: str - see scipy.spatial.distance._METRICS

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.SimilarityApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    SimilarityApi apiInstance = new SimilarityApi(defaultClient);
    try {
      Map<String, Object> result = apiInstance.similarityTextUnitSimilarityByFeaturesGET();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling SimilarityApi#similarityTextUnitSimilarityByFeaturesGET");
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

<a name="similarityTextUnitSimilarityByFeaturesPOST"></a>
# **similarityTextUnitSimilarityByFeaturesPOST**
> SimilarityPOSTObjectResponse similarityTextUnitSimilarityByFeaturesPOST(textUnitSimilarityByFeaturesForm)



\&quot;Similarity\&quot; admin task  POST params:     - similarity_threshold: int     - use_tfidf: bool     - delete: bool     - project: int     - feature_source: list - list[date, definition, duration, court,       currency_name, currency_value, term, party, geoentity]     - unit_type: str sentence|paragraph     - distance_type: str - see scipy.spatial.distance._METRICS

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.SimilarityApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    SimilarityApi apiInstance = new SimilarityApi(defaultClient);
    TextUnitSimilarityByFeaturesForm textUnitSimilarityByFeaturesForm = new TextUnitSimilarityByFeaturesForm(); // TextUnitSimilarityByFeaturesForm | 
    try {
      SimilarityPOSTObjectResponse result = apiInstance.similarityTextUnitSimilarityByFeaturesPOST(textUnitSimilarityByFeaturesForm);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling SimilarityApi#similarityTextUnitSimilarityByFeaturesPOST");
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
 **textUnitSimilarityByFeaturesForm** | [**TextUnitSimilarityByFeaturesForm**](TextUnitSimilarityByFeaturesForm.md)|  | [optional]

### Return type

[**SimilarityPOSTObjectResponse**](SimilarityPOSTObjectResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

