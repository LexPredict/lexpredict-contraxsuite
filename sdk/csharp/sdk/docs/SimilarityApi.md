# Org.OpenAPITools.Api.SimilarityApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**SimilarityDocumentSimilarityByFeaturesGET**](SimilarityApi.md#similaritydocumentsimilaritybyfeaturesget) | **GET** /api/v1/similarity/document-similarity-by-features/ | 
[**SimilarityDocumentSimilarityByFeaturesPOST**](SimilarityApi.md#similaritydocumentsimilaritybyfeaturespost) | **POST** /api/v1/similarity/document-similarity-by-features/ | 
[**SimilarityPartySimilarityGET**](SimilarityApi.md#similaritypartysimilarityget) | **GET** /api/v1/similarity/party-similarity/ | 
[**SimilarityPartySimilarityPOST**](SimilarityApi.md#similaritypartysimilaritypost) | **POST** /api/v1/similarity/party-similarity/ | 
[**SimilarityProjectDocumentsSimilarityByVectorsGET**](SimilarityApi.md#similarityprojectdocumentssimilaritybyvectorsget) | **GET** /api/v1/similarity/project-documents-similarity-by-vectors/ | 
[**SimilarityProjectDocumentsSimilarityByVectorsPOST**](SimilarityApi.md#similarityprojectdocumentssimilaritybyvectorspost) | **POST** /api/v1/similarity/project-documents-similarity-by-vectors/ | 
[**SimilarityProjectTextUnitsSimilarityByVectorsGET**](SimilarityApi.md#similarityprojecttextunitssimilaritybyvectorsget) | **GET** /api/v1/similarity/project-text-units-similarity-by-vectors/ | 
[**SimilarityProjectTextUnitsSimilarityByVectorsPOST**](SimilarityApi.md#similarityprojecttextunitssimilaritybyvectorspost) | **POST** /api/v1/similarity/project-text-units-similarity-by-vectors/ | 
[**SimilaritySimilarityGET**](SimilarityApi.md#similaritysimilarityget) | **GET** /api/v1/similarity/similarity/ | 
[**SimilaritySimilarityPOST**](SimilarityApi.md#similaritysimilaritypost) | **POST** /api/v1/similarity/similarity/ | 
[**SimilarityTextUnitSimilarityByFeaturesGET**](SimilarityApi.md#similaritytextunitsimilaritybyfeaturesget) | **GET** /api/v1/similarity/text-unit-similarity-by-features/ | 
[**SimilarityTextUnitSimilarityByFeaturesPOST**](SimilarityApi.md#similaritytextunitsimilaritybyfeaturespost) | **POST** /api/v1/similarity/text-unit-similarity-by-features/ | 



## SimilarityDocumentSimilarityByFeaturesGET

> Dictionary&lt;string, Object&gt; SimilarityDocumentSimilarityByFeaturesGET ()



\"Similarity\" admin task  POST params:     - similarity_threshold: int     - use_tfidf: bool     - delete: bool     - project: int     - feature_source: list - list[date, definition, duration, court,       currency_name, currency_value, term, party, geoentity]     - distance_type: str - see scipy.spatial.distance._METRICS

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class SimilarityDocumentSimilarityByFeaturesGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new SimilarityApi(Configuration.Default);

            try
            {
                Dictionary<string, Object> result = apiInstance.SimilarityDocumentSimilarityByFeaturesGET();
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling SimilarityApi.SimilarityDocumentSimilarityByFeaturesGET: " + e.Message );
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


## SimilarityDocumentSimilarityByFeaturesPOST

> SimilarityPOSTObjectResponse SimilarityDocumentSimilarityByFeaturesPOST (DocumentSimilarityByFeaturesForm documentSimilarityByFeaturesForm = null)



\"Similarity\" admin task  POST params:     - similarity_threshold: int     - use_tfidf: bool     - delete: bool     - project: int     - feature_source: list - list[date, definition, duration, court,       currency_name, currency_value, term, party, geoentity]     - distance_type: str - see scipy.spatial.distance._METRICS

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class SimilarityDocumentSimilarityByFeaturesPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new SimilarityApi(Configuration.Default);
            var documentSimilarityByFeaturesForm = new DocumentSimilarityByFeaturesForm(); // DocumentSimilarityByFeaturesForm |  (optional) 

            try
            {
                SimilarityPOSTObjectResponse result = apiInstance.SimilarityDocumentSimilarityByFeaturesPOST(documentSimilarityByFeaturesForm);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling SimilarityApi.SimilarityDocumentSimilarityByFeaturesPOST: " + e.Message );
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
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## SimilarityPartySimilarityGET

> Dictionary&lt;string, Object&gt; SimilarityPartySimilarityGET ()



\"Party Similarity\" admin task  POST params:     - case_sensitive: bool     - similarity_type: str[]     - similarity_threshold: int     - delete: bool

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class SimilarityPartySimilarityGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new SimilarityApi(Configuration.Default);

            try
            {
                Dictionary<string, Object> result = apiInstance.SimilarityPartySimilarityGET();
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling SimilarityApi.SimilarityPartySimilarityGET: " + e.Message );
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


## SimilarityPartySimilarityPOST

> SimilarityPOSTObjectResponse SimilarityPartySimilarityPOST (PartySimilarityForm partySimilarityForm = null)



\"Party Similarity\" admin task  POST params:     - case_sensitive: bool     - similarity_type: str[]     - similarity_threshold: int     - delete: bool

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class SimilarityPartySimilarityPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new SimilarityApi(Configuration.Default);
            var partySimilarityForm = new PartySimilarityForm(); // PartySimilarityForm |  (optional) 

            try
            {
                SimilarityPOSTObjectResponse result = apiInstance.SimilarityPartySimilarityPOST(partySimilarityForm);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling SimilarityApi.SimilarityPartySimilarityPOST: " + e.Message );
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
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## SimilarityProjectDocumentsSimilarityByVectorsGET

> Dictionary&lt;string, Object&gt; SimilarityProjectDocumentsSimilarityByVectorsGET ()



\"Similarity\" admin task  POST params:     - project_id: int     - distance_type: str - see scipy.spatial.distance._METRICS     - similarity_threshold: int     - feature_source: \"vector\"     - create_reverse_relations: bool - create B-A relations     - item_id: int     - use_tfidf: bool     - delete: bool

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class SimilarityProjectDocumentsSimilarityByVectorsGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new SimilarityApi(Configuration.Default);

            try
            {
                Dictionary<string, Object> result = apiInstance.SimilarityProjectDocumentsSimilarityByVectorsGET();
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling SimilarityApi.SimilarityProjectDocumentsSimilarityByVectorsGET: " + e.Message );
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


## SimilarityProjectDocumentsSimilarityByVectorsPOST

> SimilarityPOSTObjectResponse SimilarityProjectDocumentsSimilarityByVectorsPOST (ProjectDocumentsSimilarityByVectorsForm projectDocumentsSimilarityByVectorsForm = null)



\"Similarity\" admin task  POST params:     - project_id: int     - distance_type: str - see scipy.spatial.distance._METRICS     - similarity_threshold: int     - feature_source: \"vector\"     - create_reverse_relations: bool - create B-A relations     - item_id: int     - use_tfidf: bool     - delete: bool

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class SimilarityProjectDocumentsSimilarityByVectorsPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new SimilarityApi(Configuration.Default);
            var projectDocumentsSimilarityByVectorsForm = new ProjectDocumentsSimilarityByVectorsForm(); // ProjectDocumentsSimilarityByVectorsForm |  (optional) 

            try
            {
                SimilarityPOSTObjectResponse result = apiInstance.SimilarityProjectDocumentsSimilarityByVectorsPOST(projectDocumentsSimilarityByVectorsForm);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling SimilarityApi.SimilarityProjectDocumentsSimilarityByVectorsPOST: " + e.Message );
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
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## SimilarityProjectTextUnitsSimilarityByVectorsGET

> Dictionary&lt;string, Object&gt; SimilarityProjectTextUnitsSimilarityByVectorsGET ()



\"Similarity\" admin task  POST params:     - project_id: int     - distance_type: str - see scipy.spatial.distance._METRICS     - similarity_threshold: int     - unit_type: str sentence|paragraph     - feature_source: \"vector\"     - create_reverse_relations: bool - create B-A relations     - use_tfidf: bool     - delete: bool

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class SimilarityProjectTextUnitsSimilarityByVectorsGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new SimilarityApi(Configuration.Default);

            try
            {
                Dictionary<string, Object> result = apiInstance.SimilarityProjectTextUnitsSimilarityByVectorsGET();
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling SimilarityApi.SimilarityProjectTextUnitsSimilarityByVectorsGET: " + e.Message );
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


## SimilarityProjectTextUnitsSimilarityByVectorsPOST

> SimilarityPOSTObjectResponse SimilarityProjectTextUnitsSimilarityByVectorsPOST (ProjectTextUnitsSimilarityByVectorsForm projectTextUnitsSimilarityByVectorsForm = null)



\"Similarity\" admin task  POST params:     - project_id: int     - distance_type: str - see scipy.spatial.distance._METRICS     - similarity_threshold: int     - unit_type: str sentence|paragraph     - feature_source: \"vector\"     - create_reverse_relations: bool - create B-A relations     - use_tfidf: bool     - delete: bool

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class SimilarityProjectTextUnitsSimilarityByVectorsPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new SimilarityApi(Configuration.Default);
            var projectTextUnitsSimilarityByVectorsForm = new ProjectTextUnitsSimilarityByVectorsForm(); // ProjectTextUnitsSimilarityByVectorsForm |  (optional) 

            try
            {
                SimilarityPOSTObjectResponse result = apiInstance.SimilarityProjectTextUnitsSimilarityByVectorsPOST(projectTextUnitsSimilarityByVectorsForm);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling SimilarityApi.SimilarityProjectTextUnitsSimilarityByVectorsPOST: " + e.Message );
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
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## SimilaritySimilarityGET

> Dictionary&lt;string, Object&gt; SimilaritySimilarityGET ()



\"Similarity\" admin task  POST params:     - search_similar_documents: bool     - search_similar_text_units: bool     - similarity_threshold: int     - use_idf: bool     - delete: bool     - project: bool

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class SimilaritySimilarityGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new SimilarityApi(Configuration.Default);

            try
            {
                Dictionary<string, Object> result = apiInstance.SimilaritySimilarityGET();
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling SimilarityApi.SimilaritySimilarityGET: " + e.Message );
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


## SimilaritySimilarityPOST

> SimilarityPOSTObjectResponse SimilaritySimilarityPOST (SimilarityForm similarityForm = null)



\"Similarity\" admin task  POST params:     - search_similar_documents: bool     - search_similar_text_units: bool     - similarity_threshold: int     - use_idf: bool     - delete: bool     - project: bool

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class SimilaritySimilarityPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new SimilarityApi(Configuration.Default);
            var similarityForm = new SimilarityForm(); // SimilarityForm |  (optional) 

            try
            {
                SimilarityPOSTObjectResponse result = apiInstance.SimilaritySimilarityPOST(similarityForm);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling SimilarityApi.SimilaritySimilarityPOST: " + e.Message );
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
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## SimilarityTextUnitSimilarityByFeaturesGET

> Dictionary&lt;string, Object&gt; SimilarityTextUnitSimilarityByFeaturesGET ()



\"Similarity\" admin task  POST params:     - similarity_threshold: int     - use_tfidf: bool     - delete: bool     - project: int     - feature_source: list - list[date, definition, duration, court,       currency_name, currency_value, term, party, geoentity]     - unit_type: str sentence|paragraph     - distance_type: str - see scipy.spatial.distance._METRICS

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class SimilarityTextUnitSimilarityByFeaturesGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new SimilarityApi(Configuration.Default);

            try
            {
                Dictionary<string, Object> result = apiInstance.SimilarityTextUnitSimilarityByFeaturesGET();
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling SimilarityApi.SimilarityTextUnitSimilarityByFeaturesGET: " + e.Message );
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


## SimilarityTextUnitSimilarityByFeaturesPOST

> SimilarityPOSTObjectResponse SimilarityTextUnitSimilarityByFeaturesPOST (TextUnitSimilarityByFeaturesForm textUnitSimilarityByFeaturesForm = null)



\"Similarity\" admin task  POST params:     - similarity_threshold: int     - use_tfidf: bool     - delete: bool     - project: int     - feature_source: list - list[date, definition, duration, court,       currency_name, currency_value, term, party, geoentity]     - unit_type: str sentence|paragraph     - distance_type: str - see scipy.spatial.distance._METRICS

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class SimilarityTextUnitSimilarityByFeaturesPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new SimilarityApi(Configuration.Default);
            var textUnitSimilarityByFeaturesForm = new TextUnitSimilarityByFeaturesForm(); // TextUnitSimilarityByFeaturesForm |  (optional) 

            try
            {
                SimilarityPOSTObjectResponse result = apiInstance.SimilarityTextUnitSimilarityByFeaturesPOST(textUnitSimilarityByFeaturesForm);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling SimilarityApi.SimilarityTextUnitSimilarityByFeaturesPOST: " + e.Message );
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
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

