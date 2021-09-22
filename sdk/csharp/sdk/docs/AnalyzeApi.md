# Org.OpenAPITools.Api.AnalyzeApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**AnalyzeDocumentClusterGET**](AnalyzeApi.md#analyzedocumentclusterget) | **GET** /api/v1/analyze/document-cluster/ | 
[**AnalyzeDocumentClusterIdGET**](AnalyzeApi.md#analyzedocumentclusteridget) | **GET** /api/v1/analyze/document-cluster/{id}/ | 
[**AnalyzeDocumentClusterIdPATCH**](AnalyzeApi.md#analyzedocumentclusteridpatch) | **PATCH** /api/v1/analyze/document-cluster/{id}/ | 
[**AnalyzeDocumentClusterIdPUT**](AnalyzeApi.md#analyzedocumentclusteridput) | **PUT** /api/v1/analyze/document-cluster/{id}/ | 
[**AnalyzeDocumentSimilarityListGET**](AnalyzeApi.md#analyzedocumentsimilaritylistget) | **GET** /api/v1/analyze/document-similarity/list/ | 
[**AnalyzeDocumentTransformerListGET**](AnalyzeApi.md#analyzedocumenttransformerlistget) | **GET** /api/v1/analyze/document-transformer/list/ | 
[**AnalyzeMlModelListGET**](AnalyzeApi.md#analyzemlmodellistget) | **GET** /api/v1/analyze/ml-model/list/ | 
[**AnalyzePartySimilarityListGET**](AnalyzeApi.md#analyzepartysimilaritylistget) | **GET** /api/v1/analyze/party-similarity/list/ | 
[**AnalyzeProjectDocumentSimilarityListGET**](AnalyzeApi.md#analyzeprojectdocumentsimilaritylistget) | **GET** /api/v1/analyze/project-document-similarity/list/ | 
[**AnalyzeProjectTextUnitSimilarityListGET**](AnalyzeApi.md#analyzeprojecttextunitsimilaritylistget) | **GET** /api/v1/analyze/project-text-unit-similarity/list/ | 
[**AnalyzeProjectTextUnitSimilarityListPOST**](AnalyzeApi.md#analyzeprojecttextunitsimilaritylistpost) | **POST** /api/v1/analyze/project-text-unit-similarity/list/ | 
[**AnalyzeSimilarityRunsGET**](AnalyzeApi.md#analyzesimilarityrunsget) | **GET** /api/v1/analyze/similarity-runs/ | 
[**AnalyzeSimilarityRunsIdDELETE**](AnalyzeApi.md#analyzesimilarityrunsiddelete) | **DELETE** /api/v1/analyze/similarity-runs/{id}/ | 
[**AnalyzeSimilarityRunsIdGET**](AnalyzeApi.md#analyzesimilarityrunsidget) | **GET** /api/v1/analyze/similarity-runs/{id}/ | 
[**AnalyzeTextUnitClassificationsGET**](AnalyzeApi.md#analyzetextunitclassificationsget) | **GET** /api/v1/analyze/text-unit-classifications/ | 
[**AnalyzeTextUnitClassificationsIdDELETE**](AnalyzeApi.md#analyzetextunitclassificationsiddelete) | **DELETE** /api/v1/analyze/text-unit-classifications/{id}/ | 
[**AnalyzeTextUnitClassificationsIdGET**](AnalyzeApi.md#analyzetextunitclassificationsidget) | **GET** /api/v1/analyze/text-unit-classifications/{id}/ | 
[**AnalyzeTextUnitClassificationsPOST**](AnalyzeApi.md#analyzetextunitclassificationspost) | **POST** /api/v1/analyze/text-unit-classifications/ | 
[**AnalyzeTextUnitClassifierSuggestionsGET**](AnalyzeApi.md#analyzetextunitclassifiersuggestionsget) | **GET** /api/v1/analyze/text-unit-classifier-suggestions/ | 
[**AnalyzeTextUnitClassifierSuggestionsIdDELETE**](AnalyzeApi.md#analyzetextunitclassifiersuggestionsiddelete) | **DELETE** /api/v1/analyze/text-unit-classifier-suggestions/{id}/ | 
[**AnalyzeTextUnitClassifierSuggestionsIdGET**](AnalyzeApi.md#analyzetextunitclassifiersuggestionsidget) | **GET** /api/v1/analyze/text-unit-classifier-suggestions/{id}/ | 
[**AnalyzeTextUnitClassifiersGET**](AnalyzeApi.md#analyzetextunitclassifiersget) | **GET** /api/v1/analyze/text-unit-classifiers/ | 
[**AnalyzeTextUnitClassifiersIdDELETE**](AnalyzeApi.md#analyzetextunitclassifiersiddelete) | **DELETE** /api/v1/analyze/text-unit-classifiers/{id}/ | 
[**AnalyzeTextUnitClassifiersIdGET**](AnalyzeApi.md#analyzetextunitclassifiersidget) | **GET** /api/v1/analyze/text-unit-classifiers/{id}/ | 
[**AnalyzeTextUnitClusterListGET**](AnalyzeApi.md#analyzetextunitclusterlistget) | **GET** /api/v1/analyze/text-unit-cluster/list/ | 
[**AnalyzeTextUnitSimilarityListGET**](AnalyzeApi.md#analyzetextunitsimilaritylistget) | **GET** /api/v1/analyze/text-unit-similarity/list/ | 
[**AnalyzeTextUnitTransformerListGET**](AnalyzeApi.md#analyzetextunittransformerlistget) | **GET** /api/v1/analyze/text-unit-transformer/list/ | 
[**AnalyzeTypeaheadTextUnitClassificationFieldNameGET**](AnalyzeApi.md#analyzetypeaheadtextunitclassificationfieldnameget) | **GET** /api/v1/analyze/typeahead/text-unit-classification/{field_name}/ | 



## AnalyzeDocumentClusterGET

> List&lt;DocumentCluster&gt; AnalyzeDocumentClusterGET (Dictionary<string, string> jqFilters = null)



Document Cluster List

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeDocumentClusterGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                List<DocumentCluster> result = apiInstance.AnalyzeDocumentClusterGET(jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeDocumentClusterGET: " + e.Message );
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
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

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
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AnalyzeDocumentClusterIdGET

> DocumentCluster AnalyzeDocumentClusterIdGET (string id, Dictionary<string, string> jqFilters = null)



Retrieve Document Cluster

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeDocumentClusterIdGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var id = id_example;  // string | A unique integer value identifying this document cluster.
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                DocumentCluster result = apiInstance.AnalyzeDocumentClusterIdGET(id, jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeDocumentClusterIdGET: " + e.Message );
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
 **id** | **string**| A unique integer value identifying this document cluster. | 
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

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
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AnalyzeDocumentClusterIdPATCH

> DocumentClusterUpdate AnalyzeDocumentClusterIdPATCH (string id, DocumentClusterUpdate documentClusterUpdate = null)



Partial Update Document Cluster (name)

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeDocumentClusterIdPATCHExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var id = id_example;  // string | A unique integer value identifying this document cluster.
            var documentClusterUpdate = new DocumentClusterUpdate(); // DocumentClusterUpdate |  (optional) 

            try
            {
                DocumentClusterUpdate result = apiInstance.AnalyzeDocumentClusterIdPATCH(id, documentClusterUpdate);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeDocumentClusterIdPATCH: " + e.Message );
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
 **id** | **string**| A unique integer value identifying this document cluster. | 
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
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AnalyzeDocumentClusterIdPUT

> DocumentClusterUpdate AnalyzeDocumentClusterIdPUT (string id, DocumentClusterUpdate documentClusterUpdate = null)



Update Document Cluster (name)

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeDocumentClusterIdPUTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var id = id_example;  // string | A unique integer value identifying this document cluster.
            var documentClusterUpdate = new DocumentClusterUpdate(); // DocumentClusterUpdate |  (optional) 

            try
            {
                DocumentClusterUpdate result = apiInstance.AnalyzeDocumentClusterIdPUT(id, documentClusterUpdate);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeDocumentClusterIdPUT: " + e.Message );
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
 **id** | **string**| A unique integer value identifying this document cluster. | 
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
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AnalyzeDocumentSimilarityListGET

> List&lt;DocumentSimilarity&gt; AnalyzeDocumentSimilarityListGET (Dictionary<string, string> jqFilters = null)



Base Document Similarity List

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeDocumentSimilarityListGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                List<DocumentSimilarity> result = apiInstance.AnalyzeDocumentSimilarityListGET(jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeDocumentSimilarityListGET: " + e.Message );
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
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

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
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AnalyzeDocumentTransformerListGET

> List&lt;Transformer&gt; AnalyzeDocumentTransformerListGET (Dictionary<string, string> jqFilters = null)



MLModel List - document transformers only

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeDocumentTransformerListGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                List<Transformer> result = apiInstance.AnalyzeDocumentTransformerListGET(jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeDocumentTransformerListGET: " + e.Message );
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
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

### Return type

[**List&lt;Transformer&gt;**](Transformer.md)

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


## AnalyzeMlModelListGET

> List&lt;MLModel&gt; AnalyzeMlModelListGET (Dictionary<string, string> jqFilters = null)



MLModel List

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeMlModelListGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                List<MLModel> result = apiInstance.AnalyzeMlModelListGET(jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeMlModelListGET: " + e.Message );
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
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

### Return type

[**List&lt;MLModel&gt;**](MLModel.md)

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


## AnalyzePartySimilarityListGET

> List&lt;PartySimilarity&gt; AnalyzePartySimilarityListGET (Dictionary<string, string> jqFilters = null)



Party Similarity List

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzePartySimilarityListGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                List<PartySimilarity> result = apiInstance.AnalyzePartySimilarityListGET(jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzePartySimilarityListGET: " + e.Message );
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
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

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
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AnalyzeProjectDocumentSimilarityListGET

> ProjectDocumentSimilarityResponse AnalyzeProjectDocumentSimilarityListGET (int? textMaxLength = null, int? runId = null, int? documentId = null, Dictionary<string, string> jqFilters = null)



Project Document Similarity List for ONE document

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeProjectDocumentSimilarityListGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var textMaxLength = 56;  // int? | document b text max length, 0 to get all text (optional) 
            var runId = 56;  // int? | run id or document id required (optional) 
            var documentId = 56;  // int? | run id or document id required (optional) 
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                ProjectDocumentSimilarityResponse result = apiInstance.AnalyzeProjectDocumentSimilarityListGET(textMaxLength, runId, documentId, jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeProjectDocumentSimilarityListGET: " + e.Message );
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
 **textMaxLength** | **int?**| document b text max length, 0 to get all text | [optional] 
 **runId** | **int?**| run id or document id required | [optional] 
 **documentId** | **int?**| run id or document id required | [optional] 
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

### Return type

[**ProjectDocumentSimilarityResponse**](ProjectDocumentSimilarityResponse.md)

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


## AnalyzeProjectTextUnitSimilarityListGET

> List&lt;ProjectTextUnitSimilarity&gt; AnalyzeProjectTextUnitSimilarityListGET (Dictionary<string, string> jqFilters = null, int? textMaxLength = null, int? runId = null, bool? lastRun = null, int? textUnitId = null, int? documentId = null, int? locationStart = null, int? locationEnd = null, List<Object> selection = null)



Project Text Unit Similarity List for ONE text unit

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeProjectTextUnitSimilarityListGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 
            var textMaxLength = 56;  // int? | text unit b text max length, 0 to get all text (optional) 
            var runId = 56;  // int? | run id or text unit id required (optional) 
            var lastRun = true;  // bool? | run id or last_run or text unit id required (optional) 
            var textUnitId = 56;  // int? | run id or text unit id required (optional) 
            var documentId = 56;  // int? | document ID (optional) 
            var locationStart = 56;  // int? | start of chosen text block in a Document (optional) 
            var locationEnd = 56;  // int? | end of chosen text block in a Document (optional) 
            var selection = new List<Object>(); // List<Object> | selection coordinates (optional) 

            try
            {
                List<ProjectTextUnitSimilarity> result = apiInstance.AnalyzeProjectTextUnitSimilarityListGET(jqFilters, textMaxLength, runId, lastRun, textUnitId, documentId, locationStart, locationEnd, selection);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeProjectTextUnitSimilarityListGET: " + e.Message );
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
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 
 **textMaxLength** | **int?**| text unit b text max length, 0 to get all text | [optional] 
 **runId** | **int?**| run id or text unit id required | [optional] 
 **lastRun** | **bool?**| run id or last_run or text unit id required | [optional] 
 **textUnitId** | **int?**| run id or text unit id required | [optional] 
 **documentId** | **int?**| document ID | [optional] 
 **locationStart** | **int?**| start of chosen text block in a Document | [optional] 
 **locationEnd** | **int?**| end of chosen text block in a Document | [optional] 
 **selection** | [**List&lt;Object&gt;**](Object.md)| selection coordinates | [optional] 

### Return type

[**List&lt;ProjectTextUnitSimilarity&gt;**](ProjectTextUnitSimilarity.md)

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


## AnalyzeProjectTextUnitSimilarityListPOST

> ProjectTextUnitSimilarity AnalyzeProjectTextUnitSimilarityListPOST (SimilarProjectTextUnitsRequest similarProjectTextUnitsRequest = null)



Project Text Unit Similarity List for ONE text unit

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeProjectTextUnitSimilarityListPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var similarProjectTextUnitsRequest = new SimilarProjectTextUnitsRequest(); // SimilarProjectTextUnitsRequest |  (optional) 

            try
            {
                ProjectTextUnitSimilarity result = apiInstance.AnalyzeProjectTextUnitSimilarityListPOST(similarProjectTextUnitsRequest);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeProjectTextUnitSimilarityListPOST: " + e.Message );
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
 **similarProjectTextUnitsRequest** | [**SimilarProjectTextUnitsRequest**](SimilarProjectTextUnitsRequest.md)|  | [optional] 

### Return type

[**ProjectTextUnitSimilarity**](ProjectTextUnitSimilarity.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AnalyzeSimilarityRunsGET

> List&lt;SimilarityRun&gt; AnalyzeSimilarityRunsGET (string unitSource = null, int? projectId = null, Dictionary<string, string> jqFilters = null)



list Similarity Run objects

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeSimilarityRunsGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var unitSource = unitSource_example;  // string | document / text_unit (optional) 
            var projectId = 56;  // int? | Project ID (optional) 
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                List<SimilarityRun> result = apiInstance.AnalyzeSimilarityRunsGET(unitSource, projectId, jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeSimilarityRunsGET: " + e.Message );
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
 **unitSource** | **string**| document / text_unit | [optional] 
 **projectId** | **int?**| Project ID | [optional] 
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

### Return type

[**List&lt;SimilarityRun&gt;**](SimilarityRun.md)

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


## AnalyzeSimilarityRunsIdDELETE

> void AnalyzeSimilarityRunsIdDELETE (string id, string unitSource = null, int? projectId = null)



delete Similarity Run object

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeSimilarityRunsIdDELETEExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var id = id_example;  // string | A unique integer value identifying this similarity run.
            var unitSource = unitSource_example;  // string | document / text_unit (optional) 
            var projectId = 56;  // int? | Project ID (optional) 

            try
            {
                apiInstance.AnalyzeSimilarityRunsIdDELETE(id, unitSource, projectId);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeSimilarityRunsIdDELETE: " + e.Message );
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
 **id** | **string**| A unique integer value identifying this similarity run. | 
 **unitSource** | **string**| document / text_unit | [optional] 
 **projectId** | **int?**| Project ID | [optional] 

### Return type

void (empty response body)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AnalyzeSimilarityRunsIdGET

> SimilarityRun AnalyzeSimilarityRunsIdGET (string id, string unitSource = null, int? projectId = null, Dictionary<string, string> jqFilters = null)



get Similarity Run object

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeSimilarityRunsIdGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var id = id_example;  // string | A unique integer value identifying this similarity run.
            var unitSource = unitSource_example;  // string | document / text_unit (optional) 
            var projectId = 56;  // int? | Project ID (optional) 
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                SimilarityRun result = apiInstance.AnalyzeSimilarityRunsIdGET(id, unitSource, projectId, jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeSimilarityRunsIdGET: " + e.Message );
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
 **id** | **string**| A unique integer value identifying this similarity run. | 
 **unitSource** | **string**| document / text_unit | [optional] 
 **projectId** | **int?**| Project ID | [optional] 
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

### Return type

[**SimilarityRun**](SimilarityRun.md)

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


## AnalyzeTextUnitClassificationsGET

> List&lt;TextUnitClassification&gt; AnalyzeTextUnitClassificationsGET (Dictionary<string, string> jqFilters = null)



Text Unit Classification List

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeTextUnitClassificationsGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                List<TextUnitClassification> result = apiInstance.AnalyzeTextUnitClassificationsGET(jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeTextUnitClassificationsGET: " + e.Message );
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
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

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
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AnalyzeTextUnitClassificationsIdDELETE

> void AnalyzeTextUnitClassificationsIdDELETE (string id)



Delete Text Unit Classification

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeTextUnitClassificationsIdDELETEExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var id = id_example;  // string | A unique integer value identifying this text unit classification.

            try
            {
                apiInstance.AnalyzeTextUnitClassificationsIdDELETE(id);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeTextUnitClassificationsIdDELETE: " + e.Message );
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
 **id** | **string**| A unique integer value identifying this text unit classification. | 

### Return type

void (empty response body)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AnalyzeTextUnitClassificationsIdGET

> TextUnitClassification AnalyzeTextUnitClassificationsIdGET (string id, Dictionary<string, string> jqFilters = null)



Retrieve Text Unit Classification

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeTextUnitClassificationsIdGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var id = id_example;  // string | A unique integer value identifying this text unit classification.
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                TextUnitClassification result = apiInstance.AnalyzeTextUnitClassificationsIdGET(id, jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeTextUnitClassificationsIdGET: " + e.Message );
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
 **id** | **string**| A unique integer value identifying this text unit classification. | 
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

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
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AnalyzeTextUnitClassificationsPOST

> TextUnitClassificationCreate AnalyzeTextUnitClassificationsPOST (TextUnitClassificationCreate textUnitClassificationCreate = null)



Create Text Unit Classification

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeTextUnitClassificationsPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var textUnitClassificationCreate = new TextUnitClassificationCreate(); // TextUnitClassificationCreate |  (optional) 

            try
            {
                TextUnitClassificationCreate result = apiInstance.AnalyzeTextUnitClassificationsPOST(textUnitClassificationCreate);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeTextUnitClassificationsPOST: " + e.Message );
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
| **201** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AnalyzeTextUnitClassifierSuggestionsGET

> List&lt;TextUnitClassifierSuggestion&gt; AnalyzeTextUnitClassifierSuggestionsGET (Dictionary<string, string> jqFilters = null)



Text Unit Classifier Suggestion List

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeTextUnitClassifierSuggestionsGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                List<TextUnitClassifierSuggestion> result = apiInstance.AnalyzeTextUnitClassifierSuggestionsGET(jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeTextUnitClassifierSuggestionsGET: " + e.Message );
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
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

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
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AnalyzeTextUnitClassifierSuggestionsIdDELETE

> void AnalyzeTextUnitClassifierSuggestionsIdDELETE (string id)



Delete Text Unit Classifier Suggestion

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeTextUnitClassifierSuggestionsIdDELETEExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var id = id_example;  // string | A unique integer value identifying this text unit classifier suggestion.

            try
            {
                apiInstance.AnalyzeTextUnitClassifierSuggestionsIdDELETE(id);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeTextUnitClassifierSuggestionsIdDELETE: " + e.Message );
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
 **id** | **string**| A unique integer value identifying this text unit classifier suggestion. | 

### Return type

void (empty response body)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AnalyzeTextUnitClassifierSuggestionsIdGET

> TextUnitClassifierSuggestion AnalyzeTextUnitClassifierSuggestionsIdGET (string id, Dictionary<string, string> jqFilters = null)



### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeTextUnitClassifierSuggestionsIdGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var id = id_example;  // string | A unique integer value identifying this text unit classifier suggestion.
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                TextUnitClassifierSuggestion result = apiInstance.AnalyzeTextUnitClassifierSuggestionsIdGET(id, jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeTextUnitClassifierSuggestionsIdGET: " + e.Message );
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
 **id** | **string**| A unique integer value identifying this text unit classifier suggestion. | 
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

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
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AnalyzeTextUnitClassifiersGET

> List&lt;TextUnitClassifier&gt; AnalyzeTextUnitClassifiersGET (Dictionary<string, string> jqFilters = null)



Text Unit Classifier List

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeTextUnitClassifiersGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                List<TextUnitClassifier> result = apiInstance.AnalyzeTextUnitClassifiersGET(jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeTextUnitClassifiersGET: " + e.Message );
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
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

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
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AnalyzeTextUnitClassifiersIdDELETE

> void AnalyzeTextUnitClassifiersIdDELETE (string id)



Delete Text Unit Classifier

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeTextUnitClassifiersIdDELETEExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var id = id_example;  // string | A unique integer value identifying this text unit classifier.

            try
            {
                apiInstance.AnalyzeTextUnitClassifiersIdDELETE(id);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeTextUnitClassifiersIdDELETE: " + e.Message );
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
 **id** | **string**| A unique integer value identifying this text unit classifier. | 

### Return type

void (empty response body)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AnalyzeTextUnitClassifiersIdGET

> TextUnitClassifier AnalyzeTextUnitClassifiersIdGET (string id, Dictionary<string, string> jqFilters = null)



### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeTextUnitClassifiersIdGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var id = id_example;  // string | A unique integer value identifying this text unit classifier.
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                TextUnitClassifier result = apiInstance.AnalyzeTextUnitClassifiersIdGET(id, jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeTextUnitClassifiersIdGET: " + e.Message );
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
 **id** | **string**| A unique integer value identifying this text unit classifier. | 
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

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
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AnalyzeTextUnitClusterListGET

> List&lt;TextUnitCluster&gt; AnalyzeTextUnitClusterListGET (Dictionary<string, string> jqFilters = null)



Text Unit Cluster List

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeTextUnitClusterListGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                List<TextUnitCluster> result = apiInstance.AnalyzeTextUnitClusterListGET(jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeTextUnitClusterListGET: " + e.Message );
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
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

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
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AnalyzeTextUnitSimilarityListGET

> List&lt;TextUnitSimilarity&gt; AnalyzeTextUnitSimilarityListGET (Dictionary<string, string> jqFilters = null)



Base Text Unit Similarity List

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeTextUnitSimilarityListGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                List<TextUnitSimilarity> result = apiInstance.AnalyzeTextUnitSimilarityListGET(jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeTextUnitSimilarityListGET: " + e.Message );
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
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

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
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AnalyzeTextUnitTransformerListGET

> List&lt;Transformer&gt; AnalyzeTextUnitTransformerListGET (Dictionary<string, string> jqFilters = null)



MLModel List - text unit transformers only

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeTextUnitTransformerListGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                List<Transformer> result = apiInstance.AnalyzeTextUnitTransformerListGET(jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeTextUnitTransformerListGET: " + e.Message );
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
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

### Return type

[**List&lt;Transformer&gt;**](Transformer.md)

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


## AnalyzeTypeaheadTextUnitClassificationFieldNameGET

> Typeahead AnalyzeTypeaheadTextUnitClassificationFieldNameGET (string fieldName, string q)



Typeahead TextUnitClassification      Kwargs: field_name: [class_name, class_value]     GET params:       - q: str

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class AnalyzeTypeaheadTextUnitClassificationFieldNameGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new AnalyzeApi(Configuration.Default);
            var fieldName = fieldName_example;  // string | 
            var q = q_example;  // string | Typeahead string

            try
            {
                Typeahead result = apiInstance.AnalyzeTypeaheadTextUnitClassificationFieldNameGET(fieldName, q);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling AnalyzeApi.AnalyzeTypeaheadTextUnitClassificationFieldNameGET: " + e.Message );
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
 **fieldName** | **string**|  | 
 **q** | **string**| Typeahead string | 

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
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

