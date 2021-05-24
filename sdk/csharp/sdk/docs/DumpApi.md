# Org.OpenAPITools.Api.DumpApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**DumpDocumentConfigGET**](DumpApi.md#dumpdocumentconfigget) | **GET** /api/v1/dump/document-config/ | 
[**DumpDocumentConfigPUT**](DumpApi.md#dumpdocumentconfigput) | **PUT** /api/v1/dump/document-config/ | 
[**DumpDumpFixturePOST**](DumpApi.md#dumpdumpfixturepost) | **POST** /api/v1/dump/dump-fixture/ | 
[**DumpDumpGET**](DumpApi.md#dumpdumpget) | **GET** /api/v1/dump/dump/ | 
[**DumpDumpPUT**](DumpApi.md#dumpdumpput) | **PUT** /api/v1/dump/dump/ | 
[**DumpFieldValuesGET**](DumpApi.md#dumpfieldvaluesget) | **GET** /api/v1/dump/field-values/ | 
[**DumpFieldValuesPUT**](DumpApi.md#dumpfieldvaluesput) | **PUT** /api/v1/dump/field-values/ | 
[**DumpLoadFixturePOST**](DumpApi.md#dumploadfixturepost) | **POST** /api/v1/dump/load-fixture/ | 



## DumpDocumentConfigGET

> OneOfarrayfile DumpDocumentConfigGET (bool? download = null, string documentTypeCodes = null)



Dump document types, fields, field detectors and  document filters to json.

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class DumpDocumentConfigGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new DumpApi(Configuration.Default);
            var download = true;  // bool? | Download as file (optional) 
            var documentTypeCodes = documentTypeCodes_example;  // string | Document Type codes separated by comma (optional) 

            try
            {
                OneOfarrayfile result = apiInstance.DumpDocumentConfigGET(download, documentTypeCodes);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling DumpApi.DumpDocumentConfigGET: " + e.Message );
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
 **download** | **bool?**| Download as file | [optional] 
 **documentTypeCodes** | **string**| Document Type codes separated by comma | [optional] 

### Return type

[**OneOfarrayfile**](OneOfarrayfile.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |
| **400** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DumpDocumentConfigPUT

> string DumpDocumentConfigPUT (List<Dictionary<string, Object>> requestBody = null)



Dump document types, fields, field detectors and  document filters to json.

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class DumpDocumentConfigPUTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new DumpApi(Configuration.Default);
            var requestBody = new List<Dictionary<string, Object>>(); // List<Dictionary<string, Object>> |  (optional) 

            try
            {
                string result = apiInstance.DumpDocumentConfigPUT(requestBody);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling DumpApi.DumpDocumentConfigPUT: " + e.Message );
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
 **requestBody** | [**List&lt;Dictionary&lt;string, Object&gt;&gt;**](Dictionary.md)|  | [optional] 

### Return type

**string**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |
| **400** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DumpDumpFixturePOST

> System.IO.Stream DumpDumpFixturePOST (DumpFixture dumpFixture = null)



Download model fixture

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class DumpDumpFixturePOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new DumpApi(Configuration.Default);
            var dumpFixture = new DumpFixture(); // DumpFixture |  (optional) 

            try
            {
                System.IO.Stream result = apiInstance.DumpDumpFixturePOST(dumpFixture);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling DumpApi.DumpDumpFixturePOST: " + e.Message );
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
 **dumpFixture** | [**DumpFixture**](DumpFixture.md)|  | [optional] 

### Return type

**System.IO.Stream**

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


## DumpDumpGET

> OneOfarrayfile DumpDumpGET (bool? download = null)



Dump all users, email addresses, review statuses, review status groups, app vars, document types, fields, field detectors and document filters to json.

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class DumpDumpGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new DumpApi(Configuration.Default);
            var download = true;  // bool? | Download as file (optional) 

            try
            {
                OneOfarrayfile result = apiInstance.DumpDumpGET(download);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling DumpApi.DumpDumpGET: " + e.Message );
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
 **download** | **bool?**| Download as file | [optional] 

### Return type

[**OneOfarrayfile**](OneOfarrayfile.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |
| **400** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DumpDumpPUT

> string DumpDumpPUT (List<Dictionary<string, Object>> requestBody = null)



Dump all users, email addresses, review statuses, review status groups, app vars, document types, fields, field detectors and document filters to json.

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class DumpDumpPUTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new DumpApi(Configuration.Default);
            var requestBody = new List<Dictionary<string, Object>>(); // List<Dictionary<string, Object>> |  (optional) 

            try
            {
                string result = apiInstance.DumpDumpPUT(requestBody);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling DumpApi.DumpDumpPUT: " + e.Message );
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
 **requestBody** | [**List&lt;Dictionary&lt;string, Object&gt;&gt;**](Dictionary.md)|  | [optional] 

### Return type

**string**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |
| **400** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DumpFieldValuesGET

> OneOfarrayfile DumpFieldValuesGET (bool? download = null)



Dump field values to json.

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class DumpFieldValuesGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new DumpApi(Configuration.Default);
            var download = true;  // bool? | Download as file (optional) 

            try
            {
                OneOfarrayfile result = apiInstance.DumpFieldValuesGET(download);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling DumpApi.DumpFieldValuesGET: " + e.Message );
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
 **download** | **bool?**| Download as file | [optional] 

### Return type

[**OneOfarrayfile**](OneOfarrayfile.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |
| **400** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DumpFieldValuesPUT

> string DumpFieldValuesPUT (List<Dictionary<string, Object>> requestBody = null)



Upload field values

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class DumpFieldValuesPUTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new DumpApi(Configuration.Default);
            var requestBody = new List<Dictionary<string, Object>>(); // List<Dictionary<string, Object>> |  (optional) 

            try
            {
                string result = apiInstance.DumpFieldValuesPUT(requestBody);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling DumpApi.DumpFieldValuesPUT: " + e.Message );
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
 **requestBody** | [**List&lt;Dictionary&lt;string, Object&gt;&gt;**](Dictionary.md)|  | [optional] 

### Return type

**string**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |
| **400** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DumpLoadFixturePOST

> List&lt;Dictionary&lt;string, Object&gt;&gt; DumpLoadFixturePOST (LoadFixture loadFixture = null)



Install model fixtures

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class DumpLoadFixturePOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new DumpApi(Configuration.Default);
            var loadFixture = new LoadFixture(); // LoadFixture |  (optional) 

            try
            {
                List<Dictionary<string, Object>> result = apiInstance.DumpLoadFixturePOST(loadFixture);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling DumpApi.DumpLoadFixturePOST: " + e.Message );
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
 **loadFixture** | [**LoadFixture**](LoadFixture.md)|  | [optional] 

### Return type

**List<Dictionary<string, Object>>**

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

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

