# Org.OpenAPITools.Api.CommonApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CommonActionsGET**](CommonApi.md#commonactionsget) | **GET** /api/v1/common/actions/ | 
[**CommonActionsIdGET**](CommonApi.md#commonactionsidget) | **GET** /api/v1/common/actions/{id}/ | 
[**CommonAppVariablesGET**](CommonApi.md#commonappvariablesget) | **GET** /api/v1/common/app-variables/ | 
[**CommonAppVariablesListGET**](CommonApi.md#commonappvariableslistget) | **GET** /api/v1/common/app-variables/list/ | 
[**CommonAppVariablesProjectProjectIdGET**](CommonApi.md#commonappvariablesprojectprojectidget) | **GET** /api/v1/common/app-variables/project/{project_id}/ | 
[**CommonAppVariablesProjectProjectIdPUT**](CommonApi.md#commonappvariablesprojectprojectidput) | **PUT** /api/v1/common/app-variables/project/{project_id}/ | 
[**CommonMediaPathGET**](CommonApi.md#commonmediapathget) | **GET** /api/v1/common/media/{path}/ | 
[**CommonMenuGroupsFormFieldsGET**](CommonApi.md#commonmenugroupsformfieldsget) | **GET** /api/v1/common/menu-groups/form-fields/ | 
[**CommonMenuGroupsGET**](CommonApi.md#commonmenugroupsget) | **GET** /api/v1/common/menu-groups/ | 
[**CommonMenuGroupsIdDELETE**](CommonApi.md#commonmenugroupsiddelete) | **DELETE** /api/v1/common/menu-groups/{id}/ | 
[**CommonMenuGroupsIdFormFieldsGET**](CommonApi.md#commonmenugroupsidformfieldsget) | **GET** /api/v1/common/menu-groups/{id}/form-fields/ | 
[**CommonMenuGroupsIdGET**](CommonApi.md#commonmenugroupsidget) | **GET** /api/v1/common/menu-groups/{id}/ | 
[**CommonMenuGroupsIdPATCH**](CommonApi.md#commonmenugroupsidpatch) | **PATCH** /api/v1/common/menu-groups/{id}/ | 
[**CommonMenuGroupsIdPUT**](CommonApi.md#commonmenugroupsidput) | **PUT** /api/v1/common/menu-groups/{id}/ | 
[**CommonMenuGroupsPOST**](CommonApi.md#commonmenugroupspost) | **POST** /api/v1/common/menu-groups/ | 
[**CommonMenuItemsFormFieldsGET**](CommonApi.md#commonmenuitemsformfieldsget) | **GET** /api/v1/common/menu-items/form-fields/ | 
[**CommonMenuItemsGET**](CommonApi.md#commonmenuitemsget) | **GET** /api/v1/common/menu-items/ | 
[**CommonMenuItemsIdDELETE**](CommonApi.md#commonmenuitemsiddelete) | **DELETE** /api/v1/common/menu-items/{id}/ | 
[**CommonMenuItemsIdFormFieldsGET**](CommonApi.md#commonmenuitemsidformfieldsget) | **GET** /api/v1/common/menu-items/{id}/form-fields/ | 
[**CommonMenuItemsIdGET**](CommonApi.md#commonmenuitemsidget) | **GET** /api/v1/common/menu-items/{id}/ | 
[**CommonMenuItemsIdPATCH**](CommonApi.md#commonmenuitemsidpatch) | **PATCH** /api/v1/common/menu-items/{id}/ | 
[**CommonMenuItemsIdPUT**](CommonApi.md#commonmenuitemsidput) | **PUT** /api/v1/common/menu-items/{id}/ | 
[**CommonMenuItemsPOST**](CommonApi.md#commonmenuitemspost) | **POST** /api/v1/common/menu-items/ | 
[**CommonReviewStatusGroupsGET**](CommonApi.md#commonreviewstatusgroupsget) | **GET** /api/v1/common/review-status-groups/ | 
[**CommonReviewStatusGroupsIdDELETE**](CommonApi.md#commonreviewstatusgroupsiddelete) | **DELETE** /api/v1/common/review-status-groups/{id}/ | 
[**CommonReviewStatusGroupsIdGET**](CommonApi.md#commonreviewstatusgroupsidget) | **GET** /api/v1/common/review-status-groups/{id}/ | 
[**CommonReviewStatusGroupsIdPATCH**](CommonApi.md#commonreviewstatusgroupsidpatch) | **PATCH** /api/v1/common/review-status-groups/{id}/ | 
[**CommonReviewStatusGroupsIdPUT**](CommonApi.md#commonreviewstatusgroupsidput) | **PUT** /api/v1/common/review-status-groups/{id}/ | 
[**CommonReviewStatusGroupsPOST**](CommonApi.md#commonreviewstatusgroupspost) | **POST** /api/v1/common/review-status-groups/ | 
[**CommonReviewStatusesGET**](CommonApi.md#commonreviewstatusesget) | **GET** /api/v1/common/review-statuses/ | 
[**CommonReviewStatusesIdDELETE**](CommonApi.md#commonreviewstatusesiddelete) | **DELETE** /api/v1/common/review-statuses/{id}/ | 
[**CommonReviewStatusesIdGET**](CommonApi.md#commonreviewstatusesidget) | **GET** /api/v1/common/review-statuses/{id}/ | 
[**CommonReviewStatusesIdPATCH**](CommonApi.md#commonreviewstatusesidpatch) | **PATCH** /api/v1/common/review-statuses/{id}/ | 
[**CommonReviewStatusesIdPUT**](CommonApi.md#commonreviewstatusesidput) | **PUT** /api/v1/common/review-statuses/{id}/ | 
[**CommonReviewStatusesPOST**](CommonApi.md#commonreviewstatusespost) | **POST** /api/v1/common/review-statuses/ | 



## CommonActionsGET

> List&lt;List&lt;Action&gt;&gt; CommonActionsGET (int? projectId = null, int? documentId = null, List<string> viewActions = null, Dictionary<string, string> jqFilters = null)



Action List

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonActionsGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var projectId = 56;  // int? | Project ID (optional) 
            var documentId = 56;  // int? | Document ID (optional) 
            var viewActions = new List<string>(); // List<string> | Action names (optional) 
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                List<List<Action>> result = apiInstance.CommonActionsGET(projectId, documentId, viewActions, jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonActionsGET: " + e.Message );
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
 **projectId** | **int?**| Project ID | [optional] 
 **documentId** | **int?**| Document ID | [optional] 
 **viewActions** | [**List&lt;string&gt;**](string.md)| Action names | [optional] 
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

### Return type

**List<List<Action>>**

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


## CommonActionsIdGET

> List&lt;Action&gt; CommonActionsIdGET (string id, int? projectId = null, int? documentId = null, List<string> viewActions = null, Dictionary<string, string> jqFilters = null)



Retrieve Action

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonActionsIdGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var id = id_example;  // string | A unique integer value identifying this action.
            var projectId = 56;  // int? | Project ID (optional) 
            var documentId = 56;  // int? | Document ID (optional) 
            var viewActions = new List<string>(); // List<string> | Action names (optional) 
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                List<Action> result = apiInstance.CommonActionsIdGET(id, projectId, documentId, viewActions, jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonActionsIdGET: " + e.Message );
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
 **id** | **string**| A unique integer value identifying this action. | 
 **projectId** | **int?**| Project ID | [optional] 
 **documentId** | **int?**| Document ID | [optional] 
 **viewActions** | [**List&lt;string&gt;**](string.md)| Action names | [optional] 
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

### Return type

[**List&lt;Action&gt;**](Action.md)

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


## CommonAppVariablesGET

> Dictionary&lt;string, Object&gt; CommonAppVariablesGET (string name = null)



Retrieve App Variable(s)      Params:         - name: str - retrieve specific variable

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonAppVariablesGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var name = name_example;  // string | App var name (optional) 

            try
            {
                Dictionary<string, Object> result = apiInstance.CommonAppVariablesGET(name);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonAppVariablesGET: " + e.Message );
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
 **name** | **string**| App var name | [optional] 

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


## CommonAppVariablesListGET

> List&lt;AppVar&gt; CommonAppVariablesListGET (Dictionary<string, string> jqFilters = null)



### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonAppVariablesListGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                List<AppVar> result = apiInstance.CommonAppVariablesListGET(jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonAppVariablesListGET: " + e.Message );
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

[**List&lt;AppVar&gt;**](AppVar.md)

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


## CommonAppVariablesProjectProjectIdGET

> List&lt;ProjectAppVar&gt; CommonAppVariablesProjectProjectIdGET (string projectId)



Based on custom AppVar model storage

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonAppVariablesProjectProjectIdGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var projectId = projectId_example;  // string | 

            try
            {
                List<ProjectAppVar> result = apiInstance.CommonAppVariablesProjectProjectIdGET(projectId);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonAppVariablesProjectProjectIdGET: " + e.Message );
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

[**List&lt;ProjectAppVar&gt;**](ProjectAppVar.md)

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


## CommonAppVariablesProjectProjectIdPUT

> string CommonAppVariablesProjectProjectIdPUT (string projectId, List<ProjectAppVar> projectAppVar = null)



Based on custom AppVar model storage

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonAppVariablesProjectProjectIdPUTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var projectId = projectId_example;  // string | 
            var projectAppVar = new List<ProjectAppVar>(); // List<ProjectAppVar> |  (optional) 

            try
            {
                string result = apiInstance.CommonAppVariablesProjectProjectIdPUT(projectId, projectAppVar);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonAppVariablesProjectProjectIdPUT: " + e.Message );
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
 **projectAppVar** | [**List&lt;ProjectAppVar&gt;**](ProjectAppVar.md)|  | [optional] 

### Return type

**string**

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


## CommonMediaPathGET

> Dictionary&lt;string, Object&gt; CommonMediaPathGET (string path, string action = null)



If directory:   action: None: - list directory   action: download - list directory (TODO - download directory)   action: info: - dict(info about directory) If file:   action: None: - show file   action: download - download file   action: info: - dict(info about directory)  :param request: :param path: str - relative path in /media directory  :query param action: optional str [\"download\", \"info\"] :return:

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonMediaPathGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var path = path_example;  // string | 
            var action = action_example;  // string | Action name (optional)  (default to download)

            try
            {
                Dictionary<string, Object> result = apiInstance.CommonMediaPathGET(path, action);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonMediaPathGET: " + e.Message );
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
 **path** | **string**|  | 
 **action** | **string**| Action name | [optional] [default to download]

### Return type

**Dictionary<string, Object>**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json, */*


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CommonMenuGroupsFormFieldsGET

> Dictionary&lt;string, Object&gt; CommonMenuGroupsFormFieldsGET ()



GET model form fields description to build UI form for an object:       - field_type: str - CharField, IntegerField, SomeSerializerField - i.e. fields from a serializer      - ui_element: dict - {type: (\"input\" | \"select\" | \"checkbox\" | ...), data_type: (\"string\", \"integer\", \"date\", ...), ...}      - label: str - field label declared in a serializer field (default NULL)      - field_name: str - field name declared in a serializer field (default NULL)      - help_text: str - field help text declared in a serializer field (default NULL)      - required: bool - whether field is required      - read_only: bool - whether field is read only      - allow_null: bool - whether field is may be null      - default: bool - default (initial) field value for a new object (default NULL)      - choices: array - choices to select from [{choice_id1: choice_verbose_name1, ....}] (default NULL)

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonMenuGroupsFormFieldsGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);

            try
            {
                Dictionary<string, Object> result = apiInstance.CommonMenuGroupsFormFieldsGET();
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonMenuGroupsFormFieldsGET: " + e.Message );
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


## CommonMenuGroupsGET

> List&lt;MenuGroup&gt; CommonMenuGroupsGET ()



MenuGroup List

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonMenuGroupsGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);

            try
            {
                List<MenuGroup> result = apiInstance.CommonMenuGroupsGET();
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonMenuGroupsGET: " + e.Message );
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

[**List&lt;MenuGroup&gt;**](MenuGroup.md)

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


## CommonMenuGroupsIdDELETE

> void CommonMenuGroupsIdDELETE (string id)



Delete MenuGroup

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonMenuGroupsIdDELETEExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var id = id_example;  // string | 

            try
            {
                apiInstance.CommonMenuGroupsIdDELETE(id);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonMenuGroupsIdDELETE: " + e.Message );
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
 **id** | **string**|  | 

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


## CommonMenuGroupsIdFormFieldsGET

> Dictionary&lt;string, Object&gt; CommonMenuGroupsIdFormFieldsGET (string id)



GET model form fields description to build UI form for EXISTING object:       - value: any - object field value      - field_type: str - CharField, IntegerField, SomeSerializerField - i.e. fields from a serializer      - ui_element: dict - {type: (\"input\" | \"select\" | \"checkbox\" | ...), data_type: (\"string\", \"integer\", \"date\", ...), ...}      - label: str - field label declared in a serializer field (default NULL)      - field_name: str - field name declared in a serializer field (default NULL)      - help_text: str - field help text declared in a serializer field (default NULL)      - required: bool - whether field is required      - read_only: bool - whether field is read only      - allow_null: bool - whether field is may be null      - default: bool - default (initial) field value for a new object (default NULL)      - choices: array - choices to select from [{choice_id1: choice_verbose_name1, ....}] (default NULL)

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonMenuGroupsIdFormFieldsGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var id = id_example;  // string | A unique integer value identifying this user.

            try
            {
                Dictionary<string, Object> result = apiInstance.CommonMenuGroupsIdFormFieldsGET(id);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonMenuGroupsIdFormFieldsGET: " + e.Message );
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
 **id** | **string**| A unique integer value identifying this user. | 

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


## CommonMenuGroupsIdGET

> MenuGroup CommonMenuGroupsIdGET (string id)



Retrieve MenuGroup

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonMenuGroupsIdGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var id = id_example;  // string | 

            try
            {
                MenuGroup result = apiInstance.CommonMenuGroupsIdGET(id);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonMenuGroupsIdGET: " + e.Message );
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
 **id** | **string**|  | 

### Return type

[**MenuGroup**](MenuGroup.md)

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


## CommonMenuGroupsIdPATCH

> MenuGroup CommonMenuGroupsIdPATCH (string id, MenuGroup menuGroup = null)



Partial Update MenuGroup

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonMenuGroupsIdPATCHExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var id = id_example;  // string | 
            var menuGroup = new MenuGroup(); // MenuGroup |  (optional) 

            try
            {
                MenuGroup result = apiInstance.CommonMenuGroupsIdPATCH(id, menuGroup);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonMenuGroupsIdPATCH: " + e.Message );
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
 **id** | **string**|  | 
 **menuGroup** | [**MenuGroup**](MenuGroup.md)|  | [optional] 

### Return type

[**MenuGroup**](MenuGroup.md)

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


## CommonMenuGroupsIdPUT

> MenuGroup CommonMenuGroupsIdPUT (string id, MenuGroup menuGroup = null)



Update MenuGroup

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonMenuGroupsIdPUTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var id = id_example;  // string | 
            var menuGroup = new MenuGroup(); // MenuGroup |  (optional) 

            try
            {
                MenuGroup result = apiInstance.CommonMenuGroupsIdPUT(id, menuGroup);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonMenuGroupsIdPUT: " + e.Message );
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
 **id** | **string**|  | 
 **menuGroup** | [**MenuGroup**](MenuGroup.md)|  | [optional] 

### Return type

[**MenuGroup**](MenuGroup.md)

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


## CommonMenuGroupsPOST

> MenuGroup CommonMenuGroupsPOST (MenuGroup menuGroup = null)



Create MenuGroup

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonMenuGroupsPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var menuGroup = new MenuGroup(); // MenuGroup |  (optional) 

            try
            {
                MenuGroup result = apiInstance.CommonMenuGroupsPOST(menuGroup);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonMenuGroupsPOST: " + e.Message );
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
 **menuGroup** | [**MenuGroup**](MenuGroup.md)|  | [optional] 

### Return type

[**MenuGroup**](MenuGroup.md)

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


## CommonMenuItemsFormFieldsGET

> Dictionary&lt;string, Object&gt; CommonMenuItemsFormFieldsGET ()



GET model form fields description to build UI form for an object:       - field_type: str - CharField, IntegerField, SomeSerializerField - i.e. fields from a serializer      - ui_element: dict - {type: (\"input\" | \"select\" | \"checkbox\" | ...), data_type: (\"string\", \"integer\", \"date\", ...), ...}      - label: str - field label declared in a serializer field (default NULL)      - field_name: str - field name declared in a serializer field (default NULL)      - help_text: str - field help text declared in a serializer field (default NULL)      - required: bool - whether field is required      - read_only: bool - whether field is read only      - allow_null: bool - whether field is may be null      - default: bool - default (initial) field value for a new object (default NULL)      - choices: array - choices to select from [{choice_id1: choice_verbose_name1, ....}] (default NULL)

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonMenuItemsFormFieldsGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);

            try
            {
                Dictionary<string, Object> result = apiInstance.CommonMenuItemsFormFieldsGET();
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonMenuItemsFormFieldsGET: " + e.Message );
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


## CommonMenuItemsGET

> List&lt;MenuItem&gt; CommonMenuItemsGET ()



MenuItem List

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonMenuItemsGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);

            try
            {
                List<MenuItem> result = apiInstance.CommonMenuItemsGET();
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonMenuItemsGET: " + e.Message );
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

[**List&lt;MenuItem&gt;**](MenuItem.md)

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


## CommonMenuItemsIdDELETE

> void CommonMenuItemsIdDELETE (string id)



Delete MenuItem

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonMenuItemsIdDELETEExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var id = id_example;  // string | 

            try
            {
                apiInstance.CommonMenuItemsIdDELETE(id);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonMenuItemsIdDELETE: " + e.Message );
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
 **id** | **string**|  | 

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


## CommonMenuItemsIdFormFieldsGET

> Dictionary&lt;string, Object&gt; CommonMenuItemsIdFormFieldsGET (string id)



GET model form fields description to build UI form for EXISTING object:       - value: any - object field value      - field_type: str - CharField, IntegerField, SomeSerializerField - i.e. fields from a serializer      - ui_element: dict - {type: (\"input\" | \"select\" | \"checkbox\" | ...), data_type: (\"string\", \"integer\", \"date\", ...), ...}      - label: str - field label declared in a serializer field (default NULL)      - field_name: str - field name declared in a serializer field (default NULL)      - help_text: str - field help text declared in a serializer field (default NULL)      - required: bool - whether field is required      - read_only: bool - whether field is read only      - allow_null: bool - whether field is may be null      - default: bool - default (initial) field value for a new object (default NULL)      - choices: array - choices to select from [{choice_id1: choice_verbose_name1, ....}] (default NULL)

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonMenuItemsIdFormFieldsGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var id = id_example;  // string | A unique integer value identifying this user.

            try
            {
                Dictionary<string, Object> result = apiInstance.CommonMenuItemsIdFormFieldsGET(id);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonMenuItemsIdFormFieldsGET: " + e.Message );
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
 **id** | **string**| A unique integer value identifying this user. | 

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


## CommonMenuItemsIdGET

> MenuItem CommonMenuItemsIdGET (string id)



Retrieve MenuItem

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonMenuItemsIdGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var id = id_example;  // string | 

            try
            {
                MenuItem result = apiInstance.CommonMenuItemsIdGET(id);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonMenuItemsIdGET: " + e.Message );
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
 **id** | **string**|  | 

### Return type

[**MenuItem**](MenuItem.md)

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


## CommonMenuItemsIdPATCH

> MenuItem CommonMenuItemsIdPATCH (string id, MenuItem menuItem = null)



Partial Update MenuItem

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonMenuItemsIdPATCHExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var id = id_example;  // string | 
            var menuItem = new MenuItem(); // MenuItem |  (optional) 

            try
            {
                MenuItem result = apiInstance.CommonMenuItemsIdPATCH(id, menuItem);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonMenuItemsIdPATCH: " + e.Message );
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
 **id** | **string**|  | 
 **menuItem** | [**MenuItem**](MenuItem.md)|  | [optional] 

### Return type

[**MenuItem**](MenuItem.md)

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


## CommonMenuItemsIdPUT

> MenuItem CommonMenuItemsIdPUT (string id, MenuItem menuItem = null)



Update MenuItem

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonMenuItemsIdPUTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var id = id_example;  // string | 
            var menuItem = new MenuItem(); // MenuItem |  (optional) 

            try
            {
                MenuItem result = apiInstance.CommonMenuItemsIdPUT(id, menuItem);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonMenuItemsIdPUT: " + e.Message );
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
 **id** | **string**|  | 
 **menuItem** | [**MenuItem**](MenuItem.md)|  | [optional] 

### Return type

[**MenuItem**](MenuItem.md)

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


## CommonMenuItemsPOST

> MenuItem CommonMenuItemsPOST (MenuItem menuItem = null)



Create MenuItem

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonMenuItemsPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var menuItem = new MenuItem(); // MenuItem |  (optional) 

            try
            {
                MenuItem result = apiInstance.CommonMenuItemsPOST(menuItem);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonMenuItemsPOST: " + e.Message );
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
 **menuItem** | [**MenuItem**](MenuItem.md)|  | [optional] 

### Return type

[**MenuItem**](MenuItem.md)

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


## CommonReviewStatusGroupsGET

> List&lt;ReviewStatusGroup&gt; CommonReviewStatusGroupsGET (Dictionary<string, string> jqFilters = null)



ReviewStatusGroup List

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonReviewStatusGroupsGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                List<ReviewStatusGroup> result = apiInstance.CommonReviewStatusGroupsGET(jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonReviewStatusGroupsGET: " + e.Message );
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

[**List&lt;ReviewStatusGroup&gt;**](ReviewStatusGroup.md)

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


## CommonReviewStatusGroupsIdDELETE

> void CommonReviewStatusGroupsIdDELETE (string id)



Delete ReviewStatusGroup

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonReviewStatusGroupsIdDELETEExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var id = id_example;  // string | A unique integer value identifying this Review Status Group.

            try
            {
                apiInstance.CommonReviewStatusGroupsIdDELETE(id);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonReviewStatusGroupsIdDELETE: " + e.Message );
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
 **id** | **string**| A unique integer value identifying this Review Status Group. | 

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


## CommonReviewStatusGroupsIdGET

> ReviewStatusGroup CommonReviewStatusGroupsIdGET (string id, Dictionary<string, string> jqFilters = null)



Retrieve ReviewStatusGroup

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonReviewStatusGroupsIdGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var id = id_example;  // string | A unique integer value identifying this Review Status Group.
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                ReviewStatusGroup result = apiInstance.CommonReviewStatusGroupsIdGET(id, jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonReviewStatusGroupsIdGET: " + e.Message );
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
 **id** | **string**| A unique integer value identifying this Review Status Group. | 
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

### Return type

[**ReviewStatusGroup**](ReviewStatusGroup.md)

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


## CommonReviewStatusGroupsIdPATCH

> ReviewStatusGroup CommonReviewStatusGroupsIdPATCH (string id, ReviewStatusGroup reviewStatusGroup = null)



Partial Update ReviewStatusGroup

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonReviewStatusGroupsIdPATCHExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var id = id_example;  // string | A unique integer value identifying this Review Status Group.
            var reviewStatusGroup = new ReviewStatusGroup(); // ReviewStatusGroup |  (optional) 

            try
            {
                ReviewStatusGroup result = apiInstance.CommonReviewStatusGroupsIdPATCH(id, reviewStatusGroup);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonReviewStatusGroupsIdPATCH: " + e.Message );
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
 **id** | **string**| A unique integer value identifying this Review Status Group. | 
 **reviewStatusGroup** | [**ReviewStatusGroup**](ReviewStatusGroup.md)|  | [optional] 

### Return type

[**ReviewStatusGroup**](ReviewStatusGroup.md)

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


## CommonReviewStatusGroupsIdPUT

> ReviewStatusGroup CommonReviewStatusGroupsIdPUT (string id, ReviewStatusGroup reviewStatusGroup = null)



Update ReviewStatusGroup

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonReviewStatusGroupsIdPUTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var id = id_example;  // string | A unique integer value identifying this Review Status Group.
            var reviewStatusGroup = new ReviewStatusGroup(); // ReviewStatusGroup |  (optional) 

            try
            {
                ReviewStatusGroup result = apiInstance.CommonReviewStatusGroupsIdPUT(id, reviewStatusGroup);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonReviewStatusGroupsIdPUT: " + e.Message );
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
 **id** | **string**| A unique integer value identifying this Review Status Group. | 
 **reviewStatusGroup** | [**ReviewStatusGroup**](ReviewStatusGroup.md)|  | [optional] 

### Return type

[**ReviewStatusGroup**](ReviewStatusGroup.md)

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


## CommonReviewStatusGroupsPOST

> ReviewStatusGroup CommonReviewStatusGroupsPOST (ReviewStatusGroup reviewStatusGroup = null)



Create ReviewStatusGroup

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonReviewStatusGroupsPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var reviewStatusGroup = new ReviewStatusGroup(); // ReviewStatusGroup |  (optional) 

            try
            {
                ReviewStatusGroup result = apiInstance.CommonReviewStatusGroupsPOST(reviewStatusGroup);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonReviewStatusGroupsPOST: " + e.Message );
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
 **reviewStatusGroup** | [**ReviewStatusGroup**](ReviewStatusGroup.md)|  | [optional] 

### Return type

[**ReviewStatusGroup**](ReviewStatusGroup.md)

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


## CommonReviewStatusesGET

> List&lt;ReviewStatusDetail&gt; CommonReviewStatusesGET (Dictionary<string, string> jqFilters = null)



ReviewStatus List

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonReviewStatusesGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                List<ReviewStatusDetail> result = apiInstance.CommonReviewStatusesGET(jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonReviewStatusesGET: " + e.Message );
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

[**List&lt;ReviewStatusDetail&gt;**](ReviewStatusDetail.md)

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


## CommonReviewStatusesIdDELETE

> void CommonReviewStatusesIdDELETE (string id)



Delete ReviewStatus

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonReviewStatusesIdDELETEExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var id = id_example;  // string | A unique integer value identifying this Review Status.

            try
            {
                apiInstance.CommonReviewStatusesIdDELETE(id);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonReviewStatusesIdDELETE: " + e.Message );
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
 **id** | **string**| A unique integer value identifying this Review Status. | 

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


## CommonReviewStatusesIdGET

> ReviewStatusDetail CommonReviewStatusesIdGET (string id, Dictionary<string, string> jqFilters = null)



Retrieve ReviewStatus

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonReviewStatusesIdGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var id = id_example;  // string | A unique integer value identifying this Review Status.
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                ReviewStatusDetail result = apiInstance.CommonReviewStatusesIdGET(id, jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonReviewStatusesIdGET: " + e.Message );
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
 **id** | **string**| A unique integer value identifying this Review Status. | 
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

### Return type

[**ReviewStatusDetail**](ReviewStatusDetail.md)

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


## CommonReviewStatusesIdPATCH

> ReviewStatus CommonReviewStatusesIdPATCH (string id, ReviewStatus reviewStatus = null)



Partial Update ReviewStatus

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonReviewStatusesIdPATCHExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var id = id_example;  // string | A unique integer value identifying this Review Status.
            var reviewStatus = new ReviewStatus(); // ReviewStatus |  (optional) 

            try
            {
                ReviewStatus result = apiInstance.CommonReviewStatusesIdPATCH(id, reviewStatus);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonReviewStatusesIdPATCH: " + e.Message );
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
 **id** | **string**| A unique integer value identifying this Review Status. | 
 **reviewStatus** | [**ReviewStatus**](ReviewStatus.md)|  | [optional] 

### Return type

[**ReviewStatus**](ReviewStatus.md)

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


## CommonReviewStatusesIdPUT

> ReviewStatus CommonReviewStatusesIdPUT (string id, ReviewStatus reviewStatus = null)



Update ReviewStatus

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonReviewStatusesIdPUTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var id = id_example;  // string | A unique integer value identifying this Review Status.
            var reviewStatus = new ReviewStatus(); // ReviewStatus |  (optional) 

            try
            {
                ReviewStatus result = apiInstance.CommonReviewStatusesIdPUT(id, reviewStatus);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonReviewStatusesIdPUT: " + e.Message );
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
 **id** | **string**| A unique integer value identifying this Review Status. | 
 **reviewStatus** | [**ReviewStatus**](ReviewStatus.md)|  | [optional] 

### Return type

[**ReviewStatus**](ReviewStatus.md)

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


## CommonReviewStatusesPOST

> ReviewStatus CommonReviewStatusesPOST (ReviewStatus reviewStatus = null)



Create ReviewStatus

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class CommonReviewStatusesPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new CommonApi(Configuration.Default);
            var reviewStatus = new ReviewStatus(); // ReviewStatus |  (optional) 

            try
            {
                ReviewStatus result = apiInstance.CommonReviewStatusesPOST(reviewStatus);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling CommonApi.CommonReviewStatusesPOST: " + e.Message );
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
 **reviewStatus** | [**ReviewStatus**](ReviewStatus.md)|  | [optional] 

### Return type

[**ReviewStatus**](ReviewStatus.md)

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

