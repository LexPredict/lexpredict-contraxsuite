# Org.OpenAPITools.Api.RawdbApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**RawdbConfigGET**](RawdbApi.md#rawdbconfigget) | **GET** /api/v1/rawdb/config/ | 
[**RawdbDocumentsDocumentTypeCodeGET**](RawdbApi.md#rawdbdocumentsdocumenttypecodeget) | **GET** /api/v1/rawdb/documents/{document_type_code}/ | 
[**RawdbDocumentsDocumentTypeCodePOST**](RawdbApi.md#rawdbdocumentsdocumenttypecodepost) | **POST** /api/v1/rawdb/documents/{document_type_code}/ | 
[**RawdbProjectStatsProjectIdGET**](RawdbApi.md#rawdbprojectstatsprojectidget) | **GET** /api/v1/rawdb/project_stats/{project_id}/ | 
[**RawdbSocialAccountsGET**](RawdbApi.md#rawdbsocialaccountsget) | **GET** /api/v1/rawdb/social_accounts/ | 



## RawdbConfigGET

> Dictionary&lt;string, Object&gt; RawdbConfigGET ()



### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class RawdbConfigGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new RawdbApi(Configuration.Default);

            try
            {
                Dictionary<string, Object> result = apiInstance.RawdbConfigGET();
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling RawdbApi.RawdbConfigGET: " + e.Message );
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


## RawdbDocumentsDocumentTypeCodeGET

> Dictionary&lt;string, Object&gt; RawdbDocumentsDocumentTypeCodeGET (string documentTypeCode, string projectIds = null, string columns = null, bool? associatedText = null, bool? asZip = null, string fmt = null, int? limit = null, string orderBy = null, string savedFilters = null, bool? saveFilter = null, bool? returnReviewed = null, bool? returnTotal = null, bool? returnData = null, bool? ignoreErrors = null, Dictionary<string, string> filters = null)



### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class RawdbDocumentsDocumentTypeCodeGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new RawdbApi(Configuration.Default);
            var documentTypeCode = documentTypeCode_example;  // string | 
            var projectIds = projectIds_example;  // string | Project ids separated by commas (optional) 
            var columns = columns_example;  // string | Column names separated by commas (optional) 
            var associatedText = true;  // bool? | Boolean - show associated text (optional) 
            var asZip = true;  // bool? | Boolean - export as zip (optional) 
            var fmt = fmt_example;  // string | Export format (optional) 
            var limit = 56;  // int? | Page Size (optional) 
            var orderBy = orderBy_example;  // string | Sort order - column names separated by commas (optional) 
            var savedFilters = savedFilters_example;  // string | Saved filter ids separated by commas (optional) 
            var saveFilter = true;  // bool? | Save filter (optional) 
            var returnReviewed = true;  // bool? | Return Reviewed documents count (optional) 
            var returnTotal = true;  // bool? | Return total documents count (optional) 
            var returnData = true;  // bool? | Return data (optional) 
            var ignoreErrors = true;  // bool? | Ignore errors (optional) 
            var filters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params (optional) 

            try
            {
                Dictionary<string, Object> result = apiInstance.RawdbDocumentsDocumentTypeCodeGET(documentTypeCode, projectIds, columns, associatedText, asZip, fmt, limit, orderBy, savedFilters, saveFilter, returnReviewed, returnTotal, returnData, ignoreErrors, filters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling RawdbApi.RawdbDocumentsDocumentTypeCodeGET: " + e.Message );
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
 **documentTypeCode** | **string**|  | 
 **projectIds** | **string**| Project ids separated by commas | [optional] 
 **columns** | **string**| Column names separated by commas | [optional] 
 **associatedText** | **bool?**| Boolean - show associated text | [optional] 
 **asZip** | **bool?**| Boolean - export as zip | [optional] 
 **fmt** | **string**| Export format | [optional] 
 **limit** | **int?**| Page Size | [optional] 
 **orderBy** | **string**| Sort order - column names separated by commas | [optional] 
 **savedFilters** | **string**| Saved filter ids separated by commas | [optional] 
 **saveFilter** | **bool?**| Save filter | [optional] 
 **returnReviewed** | **bool?**| Return Reviewed documents count | [optional] 
 **returnTotal** | **bool?**| Return total documents count | [optional] 
 **returnData** | **bool?**| Return data | [optional] 
 **ignoreErrors** | **bool?**| Ignore errors | [optional] 
 **filters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params | [optional] 

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


## RawdbDocumentsDocumentTypeCodePOST

> Dictionary&lt;string, Object&gt; RawdbDocumentsDocumentTypeCodePOST (string documentTypeCode, RawdbDocumentsPOSTRequest rawdbDocumentsPOSTRequest = null)



See .get() method signature, .post() method just reflects it and uses the same request.GET params to get data

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class RawdbDocumentsDocumentTypeCodePOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new RawdbApi(Configuration.Default);
            var documentTypeCode = documentTypeCode_example;  // string | 
            var rawdbDocumentsPOSTRequest = new RawdbDocumentsPOSTRequest(); // RawdbDocumentsPOSTRequest |  (optional) 

            try
            {
                Dictionary<string, Object> result = apiInstance.RawdbDocumentsDocumentTypeCodePOST(documentTypeCode, rawdbDocumentsPOSTRequest);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling RawdbApi.RawdbDocumentsDocumentTypeCodePOST: " + e.Message );
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
 **documentTypeCode** | **string**|  | 
 **rawdbDocumentsPOSTRequest** | [**RawdbDocumentsPOSTRequest**](RawdbDocumentsPOSTRequest.md)|  | [optional] 

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

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RawdbProjectStatsProjectIdGET

> Dictionary&lt;string, Object&gt; RawdbProjectStatsProjectIdGET (string projectId)



### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class RawdbProjectStatsProjectIdGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new RawdbApi(Configuration.Default);
            var projectId = projectId_example;  // string | 

            try
            {
                Dictionary<string, Object> result = apiInstance.RawdbProjectStatsProjectIdGET(projectId);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling RawdbApi.RawdbProjectStatsProjectIdGET: " + e.Message );
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
 **projectId** | **string**|  | 

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


## RawdbSocialAccountsGET

> SocialAccountsResponse RawdbSocialAccountsGET ()



### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class RawdbSocialAccountsGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new RawdbApi(Configuration.Default);

            try
            {
                SocialAccountsResponse result = apiInstance.RawdbSocialAccountsGET();
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling RawdbApi.RawdbSocialAccountsGET: " + e.Message );
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

[**SocialAccountsResponse**](SocialAccountsResponse.md)

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

