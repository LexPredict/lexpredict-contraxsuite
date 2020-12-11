# Org.OpenAPITools.Api.TaskApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**TaskCleanTasksPOST**](TaskApi.md#taskcleantaskspost) | **POST** /api/v1/task/clean-tasks/ | 
[**TaskLoadDictionariesPOST**](TaskApi.md#taskloaddictionariespost) | **POST** /api/v1/task/load-dictionaries/ | 
[**TaskLoadDocumentsGET**](TaskApi.md#taskloaddocumentsget) | **GET** /api/v1/task/load-documents/ | 
[**TaskLoadDocumentsPOST**](TaskApi.md#taskloaddocumentspost) | **POST** /api/v1/task/load-documents/ | 
[**TaskLocateGET**](TaskApi.md#tasklocateget) | **GET** /api/v1/task/locate/ | 
[**TaskLocatePOST**](TaskApi.md#tasklocatepost) | **POST** /api/v1/task/locate/ | 
[**TaskPurgeTaskPOST**](TaskApi.md#taskpurgetaskpost) | **POST** /api/v1/task/purge-task/ | 
[**TaskRecallTaskGET**](TaskApi.md#taskrecalltaskget) | **GET** /api/v1/task/recall-task/ | 
[**TaskRecallTaskPOST**](TaskApi.md#taskrecalltaskpost) | **POST** /api/v1/task/recall-task/ | 
[**TaskTaskLogGET**](TaskApi.md#tasktasklogget) | **GET** /api/v1/task/task-log/ | 
[**TaskTaskStatusGET**](TaskApi.md#tasktaskstatusget) | **GET** /api/v1/task/task-status/ | 
[**TaskTasksGET**](TaskApi.md#tasktasksget) | **GET** /api/v1/task/tasks/ | 
[**TaskTasksIdGET**](TaskApi.md#tasktasksidget) | **GET** /api/v1/task/tasks/{id}/ | 
[**TaskUpdateElasticIndexGET**](TaskApi.md#taskupdateelasticindexget) | **GET** /api/v1/task/update-elastic-index/ | 
[**TaskUpdateElasticIndexPOST**](TaskApi.md#taskupdateelasticindexpost) | **POST** /api/v1/task/update-elastic-index/ | 



## TaskCleanTasksPOST

> Dictionary&lt;string, Object&gt; TaskCleanTasksPOST (Dictionary<string, Object> requestBody = null)



\"Clean Tasks\" admin task

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class TaskCleanTasksPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new TaskApi(Configuration.Default);
            var requestBody = new Dictionary<string, Object>(); // Dictionary<string, Object> |  (optional) 

            try
            {
                Dictionary<string, Object> result = apiInstance.TaskCleanTasksPOST(requestBody);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling TaskApi.TaskCleanTasksPOST: " + e.Message );
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
 **requestBody** | [**Dictionary&lt;string, Object&gt;**](Object.md)|  | [optional] 

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


## TaskLoadDictionariesPOST

> Dictionary&lt;string, Object&gt; TaskLoadDictionariesPOST (Dictionary<string, Object> requestBody = null)



\"Load Dictionaries\" admin task  POST params:     - terms_accounting: bool:     - terms_accounting_1: bool:     - terms_accounting_1_locale_en: bool:     - terms_accounting_2: bool:     - terms_accounting_2_locale_en: bool:     - terms_accounting_3: bool:     - terms_accounting_3_locale_en: bool:     - terms_accounting_4: bool:     - terms_accounting_4_locale_en: bool:     - terms_accounting_5: bool:     - terms_accounting_5_locale_en: bool:     - terms_scientific: bool:     - terms_scientific_1: bool:     - terms_scientific1_locale_en: bool:     - terms_financial: bool:     - terms_financial_1: bool:     - terms_financial_1_locale_en: bool:     - terms_legal: bool:     - terms_legal_1: bool:     - terms_legal_1_locale_en: bool:     - terms_legal_2: bool:     - terms_legal_2_locale_en: bool:     - terms_legal_3: bool:     - terms_legal_3_locale_en: bool:     - terms_legal_4: bool:     - terms_legal_4_locale_en: bool:     - terms_file_path: str:     - terms_delete: bool:     - courts: bool:     - courts_1: bool:     - courts_1_locale_en: bool:     - courts_2: bool:     - courts_2_locale_en: bool:     - courts_file_path: str:     - courts_delete: bool:     - geoentities: bool:     - geoentities_1: bool:     - geoentities_1_locale_multi: bool:     - geoentities_file_path: str:     - geoentities_delete: bool:

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class TaskLoadDictionariesPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new TaskApi(Configuration.Default);
            var requestBody = new Dictionary<string, Object>(); // Dictionary<string, Object> |  (optional) 

            try
            {
                Dictionary<string, Object> result = apiInstance.TaskLoadDictionariesPOST(requestBody);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling TaskApi.TaskLoadDictionariesPOST: " + e.Message );
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
 **requestBody** | [**Dictionary&lt;string, Object&gt;**](Object.md)|  | [optional] 

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


## TaskLoadDocumentsGET

> Dictionary&lt;string, Object&gt; TaskLoadDocumentsGET ()



\"Load Documents\" admin task  POST params:     - project: int     - source_data: str     - source_type: str     - document_type: str     - delete: bool     - run_standard_locators: bool

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class TaskLoadDocumentsGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new TaskApi(Configuration.Default);

            try
            {
                Dictionary<string, Object> result = apiInstance.TaskLoadDocumentsGET();
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling TaskApi.TaskLoadDocumentsGET: " + e.Message );
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


## TaskLoadDocumentsPOST

> Dictionary&lt;string, Object&gt; TaskLoadDocumentsPOST (Dictionary<string, Object> requestBody = null)



\"Load Documents\" admin task  POST params:     - project: int     - source_data: str     - source_type: str     - document_type: str     - delete: bool     - run_standard_locators: bool

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class TaskLoadDocumentsPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new TaskApi(Configuration.Default);
            var requestBody = new Dictionary<string, Object>(); // Dictionary<string, Object> |  (optional) 

            try
            {
                Dictionary<string, Object> result = apiInstance.TaskLoadDocumentsPOST(requestBody);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling TaskApi.TaskLoadDocumentsPOST: " + e.Message );
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
 **requestBody** | [**Dictionary&lt;string, Object&gt;**](Object.md)|  | [optional] 

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


## TaskLocateGET

> Dictionary&lt;string, Object&gt; TaskLocateGET ()



\"Locate\" admin task  POST params:     - locate_all: bool     - geoentity_locate: bool     - geoentity_priority: bool     - geoentity_delete: bool     - date_locate: bool     - date_strict: bool     - date_delete: bool     - amount_locate: bool     - amount_delete: bool     - citation_locate: bool     - citation_delete: bool     - copyright_locate: bool     - copyright_delete: bool     - court_locate: bool     - court_delete: bool     - currency_locate: bool     - currency_delete: bool     - duration_locate: bool     - duration_delete: bool     - definition_locate: bool     - definition_delete: bool     - distance_locate: bool     - distance_delete: bool     - party_locate: bool     - party_delete: bool     - percent_locate: bool     - percent_delete: bool     - ratio_locate: bool     - ratio_delete: bool     - regulation_locate: bool     - regulation_delete: bool     - term_locate: bool     - term_delete: bool     - trademark_locate: bool     - trademark_delete: bool     - url_locate: bool     - url_delete: bool     - parse_choice_sentence: bool     - parse_choice_paragraph: bool     - project: int

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class TaskLocateGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new TaskApi(Configuration.Default);

            try
            {
                Dictionary<string, Object> result = apiInstance.TaskLocateGET();
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling TaskApi.TaskLocateGET: " + e.Message );
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


## TaskLocatePOST

> Dictionary&lt;string, Object&gt; TaskLocatePOST (Dictionary<string, Object> requestBody = null)



\"Locate\" admin task  POST params:     - locate_all: bool     - geoentity_locate: bool     - geoentity_priority: bool     - geoentity_delete: bool     - date_locate: bool     - date_strict: bool     - date_delete: bool     - amount_locate: bool     - amount_delete: bool     - citation_locate: bool     - citation_delete: bool     - copyright_locate: bool     - copyright_delete: bool     - court_locate: bool     - court_delete: bool     - currency_locate: bool     - currency_delete: bool     - duration_locate: bool     - duration_delete: bool     - definition_locate: bool     - definition_delete: bool     - distance_locate: bool     - distance_delete: bool     - party_locate: bool     - party_delete: bool     - percent_locate: bool     - percent_delete: bool     - ratio_locate: bool     - ratio_delete: bool     - regulation_locate: bool     - regulation_delete: bool     - term_locate: bool     - term_delete: bool     - trademark_locate: bool     - trademark_delete: bool     - url_locate: bool     - url_delete: bool     - parse_choice_sentence: bool     - parse_choice_paragraph: bool     - project: int

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class TaskLocatePOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new TaskApi(Configuration.Default);
            var requestBody = new Dictionary<string, Object>(); // Dictionary<string, Object> |  (optional) 

            try
            {
                Dictionary<string, Object> result = apiInstance.TaskLocatePOST(requestBody);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling TaskApi.TaskLocatePOST: " + e.Message );
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
 **requestBody** | [**Dictionary&lt;string, Object&gt;**](Object.md)|  | [optional] 

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


## TaskPurgeTaskPOST

> Dictionary&lt;string, Object&gt; TaskPurgeTaskPOST (Dictionary<string, Object> requestBody = null)



\"Purge Task\" admin task  POST params:     - task_pk: int

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class TaskPurgeTaskPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new TaskApi(Configuration.Default);
            var requestBody = new Dictionary<string, Object>(); // Dictionary<string, Object> |  (optional) 

            try
            {
                Dictionary<string, Object> result = apiInstance.TaskPurgeTaskPOST(requestBody);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling TaskApi.TaskPurgeTaskPOST: " + e.Message );
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
 **requestBody** | [**Dictionary&lt;string, Object&gt;**](Object.md)|  | [optional] 

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


## TaskRecallTaskGET

> Dictionary&lt;string, Object&gt; TaskRecallTaskGET ()



\"Recall Task\" admin task  POST params:     - task_pk: int

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class TaskRecallTaskGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new TaskApi(Configuration.Default);

            try
            {
                Dictionary<string, Object> result = apiInstance.TaskRecallTaskGET();
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling TaskApi.TaskRecallTaskGET: " + e.Message );
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


## TaskRecallTaskPOST

> Dictionary&lt;string, Object&gt; TaskRecallTaskPOST (Dictionary<string, Object> requestBody = null)



\"Recall Task\" admin task  POST params:     - task_pk: int

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class TaskRecallTaskPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new TaskApi(Configuration.Default);
            var requestBody = new Dictionary<string, Object>(); // Dictionary<string, Object> |  (optional) 

            try
            {
                Dictionary<string, Object> result = apiInstance.TaskRecallTaskPOST(requestBody);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling TaskApi.TaskRecallTaskPOST: " + e.Message );
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
 **requestBody** | [**Dictionary&lt;string, Object&gt;**](Object.md)|  | [optional] 

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


## TaskTaskLogGET

> Dictionary&lt;string, Object&gt; TaskTaskLogGET (string taskId = null, int? recordsLimit = null)



Get task log records GET params:     - task_id: int     - records_limit: int

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class TaskTaskLogGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new TaskApi(Configuration.Default);
            var taskId = taskId_example;  // string |  (optional) 
            var recordsLimit = 56;  // int? |  (optional) 

            try
            {
                Dictionary<string, Object> result = apiInstance.TaskTaskLogGET(taskId, recordsLimit);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling TaskApi.TaskTaskLogGET: " + e.Message );
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
 **taskId** | **string**|  | [optional] 
 **recordsLimit** | **int?**|  | [optional] 

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


## TaskTaskStatusGET

> Dictionary&lt;string, Object&gt; TaskTaskStatusGET (string taskId = null)



Check admin task status  GET params:     - task_id: int

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class TaskTaskStatusGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new TaskApi(Configuration.Default);
            var taskId = taskId_example;  // string |  (optional) 

            try
            {
                Dictionary<string, Object> result = apiInstance.TaskTaskStatusGET(taskId);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling TaskApi.TaskTaskStatusGET: " + e.Message );
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
 **taskId** | **string**|  | [optional] 

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
| **404** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## TaskTasksGET

> List&lt;Task&gt; TaskTasksGET (Dictionary<string, string> jqFilters = null)



Task List

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class TaskTasksGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new TaskApi(Configuration.Default);
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                List<Task> result = apiInstance.TaskTasksGET(jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling TaskApi.TaskTasksGET: " + e.Message );
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

[**List&lt;Task&gt;**](Task.md)

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


## TaskTasksIdGET

> Task TaskTasksIdGET (string id, Dictionary<string, string> jqFilters = null)



Retrieve Task

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class TaskTasksIdGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new TaskApi(Configuration.Default);
            var id = id_example;  // string | A unique value identifying this task.
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                Task result = apiInstance.TaskTasksIdGET(id, jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling TaskApi.TaskTasksIdGET: " + e.Message );
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
 **id** | **string**| A unique value identifying this task. | 
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

### Return type

[**Task**](Task.md)

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


## TaskUpdateElasticIndexGET

> Dictionary&lt;string, Object&gt; TaskUpdateElasticIndexGET ()



\"Update ElasticSearch Index\" admin task

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class TaskUpdateElasticIndexGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new TaskApi(Configuration.Default);

            try
            {
                Dictionary<string, Object> result = apiInstance.TaskUpdateElasticIndexGET();
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling TaskApi.TaskUpdateElasticIndexGET: " + e.Message );
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


## TaskUpdateElasticIndexPOST

> Dictionary&lt;string, Object&gt; TaskUpdateElasticIndexPOST (Dictionary<string, Object> requestBody = null)



\"Update ElasticSearch Index\" admin task

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class TaskUpdateElasticIndexPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new TaskApi(Configuration.Default);
            var requestBody = new Dictionary<string, Object>(); // Dictionary<string, Object> |  (optional) 

            try
            {
                Dictionary<string, Object> result = apiInstance.TaskUpdateElasticIndexPOST(requestBody);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling TaskApi.TaskUpdateElasticIndexPOST: " + e.Message );
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
 **requestBody** | [**Dictionary&lt;string, Object&gt;**](Object.md)|  | [optional] 

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

