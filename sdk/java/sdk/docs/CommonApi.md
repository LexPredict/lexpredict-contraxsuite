# CommonApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**commonActionsGET**](CommonApi.md#commonActionsGET) | **GET** /api/v1/common/actions/ | 
[**commonActionsIdGET**](CommonApi.md#commonActionsIdGET) | **GET** /api/v1/common/actions/{id}/ | 
[**commonAppVariablesGET**](CommonApi.md#commonAppVariablesGET) | **GET** /api/v1/common/app-variables/ | 
[**commonAppVariablesListGET**](CommonApi.md#commonAppVariablesListGET) | **GET** /api/v1/common/app-variables/list/ | 
[**commonAppVariablesProjectProjectIdGET**](CommonApi.md#commonAppVariablesProjectProjectIdGET) | **GET** /api/v1/common/app-variables/project/{project_id}/ | 
[**commonAppVariablesProjectProjectIdPUT**](CommonApi.md#commonAppVariablesProjectProjectIdPUT) | **PUT** /api/v1/common/app-variables/project/{project_id}/ | 
[**commonMediaPathGET**](CommonApi.md#commonMediaPathGET) | **GET** /api/v1/common/media/{path}/ | 
[**commonMenuGroupsFormFieldsGET**](CommonApi.md#commonMenuGroupsFormFieldsGET) | **GET** /api/v1/common/menu-groups/form-fields/ | 
[**commonMenuGroupsGET**](CommonApi.md#commonMenuGroupsGET) | **GET** /api/v1/common/menu-groups/ | 
[**commonMenuGroupsIdDELETE**](CommonApi.md#commonMenuGroupsIdDELETE) | **DELETE** /api/v1/common/menu-groups/{id}/ | 
[**commonMenuGroupsIdFormFieldsGET**](CommonApi.md#commonMenuGroupsIdFormFieldsGET) | **GET** /api/v1/common/menu-groups/{id}/form-fields/ | 
[**commonMenuGroupsIdGET**](CommonApi.md#commonMenuGroupsIdGET) | **GET** /api/v1/common/menu-groups/{id}/ | 
[**commonMenuGroupsIdPATCH**](CommonApi.md#commonMenuGroupsIdPATCH) | **PATCH** /api/v1/common/menu-groups/{id}/ | 
[**commonMenuGroupsIdPUT**](CommonApi.md#commonMenuGroupsIdPUT) | **PUT** /api/v1/common/menu-groups/{id}/ | 
[**commonMenuGroupsPOST**](CommonApi.md#commonMenuGroupsPOST) | **POST** /api/v1/common/menu-groups/ | 
[**commonMenuItemsFormFieldsGET**](CommonApi.md#commonMenuItemsFormFieldsGET) | **GET** /api/v1/common/menu-items/form-fields/ | 
[**commonMenuItemsGET**](CommonApi.md#commonMenuItemsGET) | **GET** /api/v1/common/menu-items/ | 
[**commonMenuItemsIdDELETE**](CommonApi.md#commonMenuItemsIdDELETE) | **DELETE** /api/v1/common/menu-items/{id}/ | 
[**commonMenuItemsIdFormFieldsGET**](CommonApi.md#commonMenuItemsIdFormFieldsGET) | **GET** /api/v1/common/menu-items/{id}/form-fields/ | 
[**commonMenuItemsIdGET**](CommonApi.md#commonMenuItemsIdGET) | **GET** /api/v1/common/menu-items/{id}/ | 
[**commonMenuItemsIdPATCH**](CommonApi.md#commonMenuItemsIdPATCH) | **PATCH** /api/v1/common/menu-items/{id}/ | 
[**commonMenuItemsIdPUT**](CommonApi.md#commonMenuItemsIdPUT) | **PUT** /api/v1/common/menu-items/{id}/ | 
[**commonMenuItemsPOST**](CommonApi.md#commonMenuItemsPOST) | **POST** /api/v1/common/menu-items/ | 
[**commonReviewStatusGroupsGET**](CommonApi.md#commonReviewStatusGroupsGET) | **GET** /api/v1/common/review-status-groups/ | 
[**commonReviewStatusGroupsIdDELETE**](CommonApi.md#commonReviewStatusGroupsIdDELETE) | **DELETE** /api/v1/common/review-status-groups/{id}/ | 
[**commonReviewStatusGroupsIdGET**](CommonApi.md#commonReviewStatusGroupsIdGET) | **GET** /api/v1/common/review-status-groups/{id}/ | 
[**commonReviewStatusGroupsIdPATCH**](CommonApi.md#commonReviewStatusGroupsIdPATCH) | **PATCH** /api/v1/common/review-status-groups/{id}/ | 
[**commonReviewStatusGroupsIdPUT**](CommonApi.md#commonReviewStatusGroupsIdPUT) | **PUT** /api/v1/common/review-status-groups/{id}/ | 
[**commonReviewStatusGroupsPOST**](CommonApi.md#commonReviewStatusGroupsPOST) | **POST** /api/v1/common/review-status-groups/ | 
[**commonReviewStatusesGET**](CommonApi.md#commonReviewStatusesGET) | **GET** /api/v1/common/review-statuses/ | 
[**commonReviewStatusesIdDELETE**](CommonApi.md#commonReviewStatusesIdDELETE) | **DELETE** /api/v1/common/review-statuses/{id}/ | 
[**commonReviewStatusesIdGET**](CommonApi.md#commonReviewStatusesIdGET) | **GET** /api/v1/common/review-statuses/{id}/ | 
[**commonReviewStatusesIdPATCH**](CommonApi.md#commonReviewStatusesIdPATCH) | **PATCH** /api/v1/common/review-statuses/{id}/ | 
[**commonReviewStatusesIdPUT**](CommonApi.md#commonReviewStatusesIdPUT) | **PUT** /api/v1/common/review-statuses/{id}/ | 
[**commonReviewStatusesPOST**](CommonApi.md#commonReviewStatusesPOST) | **POST** /api/v1/common/review-statuses/ | 


<a name="commonActionsGET"></a>
# **commonActionsGET**
> List&lt;Action&gt; commonActionsGET(projectId, documentId, viewActions, jqFilters)



Action List

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    Integer projectId = 56; // Integer | Project ID
    Integer documentId = 56; // Integer | Document ID
    List<String> viewActions = Arrays.asList(); // List<String> | Action names
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      List<Action> result = apiInstance.commonActionsGET(projectId, documentId, viewActions, jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonActionsGET");
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
 **projectId** | **Integer**| Project ID | [optional]
 **documentId** | **Integer**| Document ID | [optional]
 **viewActions** | [**List&lt;String&gt;**](String.md)| Action names | [optional]
 **jqFilters** | [**Map&lt;String, String&gt;**](String.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

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
**200** |  |  -  |

<a name="commonActionsIdGET"></a>
# **commonActionsIdGET**
> Action commonActionsIdGET(id, projectId, documentId, viewActions, jqFilters)



Retrieve Action

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this action.
    Integer projectId = 56; // Integer | Project ID
    Integer documentId = 56; // Integer | Document ID
    List<String> viewActions = Arrays.asList(); // List<String> | Action names
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      Action result = apiInstance.commonActionsIdGET(id, projectId, documentId, viewActions, jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonActionsIdGET");
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
 **id** | **String**| A unique integer value identifying this action. |
 **projectId** | **Integer**| Project ID | [optional]
 **documentId** | **Integer**| Document ID | [optional]
 **viewActions** | [**List&lt;String&gt;**](String.md)| Action names | [optional]
 **jqFilters** | [**Map&lt;String, String&gt;**](String.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**Action**](Action.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="commonAppVariablesGET"></a>
# **commonAppVariablesGET**
> Map&lt;String, Object&gt; commonAppVariablesGET(name)



Retrieve App Variable(s)      Params:         - name: str - retrieve specific variable

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String name = "name_example"; // String | App var name
    try {
      Map<String, Object> result = apiInstance.commonAppVariablesGET(name);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonAppVariablesGET");
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
 **name** | **String**| App var name | [optional]

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

<a name="commonAppVariablesListGET"></a>
# **commonAppVariablesListGET**
> List&lt;AppVar&gt; commonAppVariablesListGET(jqFilters)



### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      List<AppVar> result = apiInstance.commonAppVariablesListGET(jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonAppVariablesListGET");
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

[**List&lt;AppVar&gt;**](AppVar.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="commonAppVariablesProjectProjectIdGET"></a>
# **commonAppVariablesProjectProjectIdGET**
> List&lt;ProjectAppVar&gt; commonAppVariablesProjectProjectIdGET(projectId)



Based on custom AppVar model storage

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String projectId = "projectId_example"; // String | 
    try {
      List<ProjectAppVar> result = apiInstance.commonAppVariablesProjectProjectIdGET(projectId);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonAppVariablesProjectProjectIdGET");
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
 **projectId** | **String**|  |

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
**200** |  |  -  |

<a name="commonAppVariablesProjectProjectIdPUT"></a>
# **commonAppVariablesProjectProjectIdPUT**
> String commonAppVariablesProjectProjectIdPUT(projectId, projectAppVar)



Based on custom AppVar model storage

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String projectId = "projectId_example"; // String | 
    List<ProjectAppVar> projectAppVar = Arrays.asList(); // List<ProjectAppVar> | 
    try {
      String result = apiInstance.commonAppVariablesProjectProjectIdPUT(projectId, projectAppVar);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonAppVariablesProjectProjectIdPUT");
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
 **projectId** | **String**|  |
 **projectAppVar** | [**List&lt;ProjectAppVar&gt;**](ProjectAppVar.md)|  | [optional]

### Return type

**String**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="commonMediaPathGET"></a>
# **commonMediaPathGET**
> Map&lt;String, Object&gt; commonMediaPathGET(path, action)



If directory:   action: None: - list directory   action: download - list directory (TODO - download directory)   action: info: - dict(info about directory) If file:   action: None: - show file   action: download - download file   action: info: - dict(info about directory)  :param request: :param path: str - relative path in /media directory  :query param action: optional str [\&quot;download\&quot;, \&quot;info\&quot;] :return:

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String path = "path_example"; // String | 
    String action = "download"; // String | Action name
    try {
      Map<String, Object> result = apiInstance.commonMediaPathGET(path, action);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonMediaPathGET");
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
 **path** | **String**|  |
 **action** | **String**| Action name | [optional] [default to download] [enum: info, download]

### Return type

**Map&lt;String, Object&gt;**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, */*

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="commonMenuGroupsFormFieldsGET"></a>
# **commonMenuGroupsFormFieldsGET**
> Map&lt;String, Object&gt; commonMenuGroupsFormFieldsGET()



GET model form fields description to build UI form for an object:       - field_type: str - CharField, IntegerField, SomeSerializerField - i.e. fields from a serializer      - ui_element: dict - {type: (\&quot;input\&quot; | \&quot;select\&quot; | \&quot;checkbox\&quot; | ...), data_type: (\&quot;string\&quot;, \&quot;integer\&quot;, \&quot;date\&quot;, ...), ...}      - label: str - field label declared in a serializer field (default NULL)      - field_name: str - field name declared in a serializer field (default NULL)      - help_text: str - field help text declared in a serializer field (default NULL)      - required: bool - whether field is required      - read_only: bool - whether field is read only      - allow_null: bool - whether field is may be null      - default: bool - default (initial) field value for a new object (default NULL)      - choices: array - choices to select from [{choice_id1: choice_verbose_name1, ....}] (default NULL)

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    try {
      Map<String, Object> result = apiInstance.commonMenuGroupsFormFieldsGET();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonMenuGroupsFormFieldsGET");
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

<a name="commonMenuGroupsGET"></a>
# **commonMenuGroupsGET**
> List&lt;MenuGroup&gt; commonMenuGroupsGET()



MenuGroup List

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    try {
      List<MenuGroup> result = apiInstance.commonMenuGroupsGET();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonMenuGroupsGET");
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

[**List&lt;MenuGroup&gt;**](MenuGroup.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="commonMenuGroupsIdDELETE"></a>
# **commonMenuGroupsIdDELETE**
> commonMenuGroupsIdDELETE(id)



Delete MenuGroup

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String id = "id_example"; // String | 
    try {
      apiInstance.commonMenuGroupsIdDELETE(id);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonMenuGroupsIdDELETE");
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
 **id** | **String**|  |

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

<a name="commonMenuGroupsIdFormFieldsGET"></a>
# **commonMenuGroupsIdFormFieldsGET**
> Map&lt;String, Object&gt; commonMenuGroupsIdFormFieldsGET(id)



GET model form fields description to build UI form for EXISTING object:       - value: any - object field value      - field_type: str - CharField, IntegerField, SomeSerializerField - i.e. fields from a serializer      - ui_element: dict - {type: (\&quot;input\&quot; | \&quot;select\&quot; | \&quot;checkbox\&quot; | ...), data_type: (\&quot;string\&quot;, \&quot;integer\&quot;, \&quot;date\&quot;, ...), ...}      - label: str - field label declared in a serializer field (default NULL)      - field_name: str - field name declared in a serializer field (default NULL)      - help_text: str - field help text declared in a serializer field (default NULL)      - required: bool - whether field is required      - read_only: bool - whether field is read only      - allow_null: bool - whether field is may be null      - default: bool - default (initial) field value for a new object (default NULL)      - choices: array - choices to select from [{choice_id1: choice_verbose_name1, ....}] (default NULL)

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this user.
    try {
      Map<String, Object> result = apiInstance.commonMenuGroupsIdFormFieldsGET(id);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonMenuGroupsIdFormFieldsGET");
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
 **id** | **String**| A unique integer value identifying this user. |

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

<a name="commonMenuGroupsIdGET"></a>
# **commonMenuGroupsIdGET**
> MenuGroup commonMenuGroupsIdGET(id)



Retrieve MenuGroup

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String id = "id_example"; // String | 
    try {
      MenuGroup result = apiInstance.commonMenuGroupsIdGET(id);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonMenuGroupsIdGET");
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
 **id** | **String**|  |

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
**200** |  |  -  |

<a name="commonMenuGroupsIdPATCH"></a>
# **commonMenuGroupsIdPATCH**
> MenuGroup commonMenuGroupsIdPATCH(id, menuGroup)



Partial Update MenuGroup

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String id = "id_example"; // String | 
    MenuGroup menuGroup = new MenuGroup(); // MenuGroup | 
    try {
      MenuGroup result = apiInstance.commonMenuGroupsIdPATCH(id, menuGroup);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonMenuGroupsIdPATCH");
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
 **id** | **String**|  |
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
**200** |  |  -  |

<a name="commonMenuGroupsIdPUT"></a>
# **commonMenuGroupsIdPUT**
> MenuGroup commonMenuGroupsIdPUT(id, menuGroup)



Update MenuGroup

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String id = "id_example"; // String | 
    MenuGroup menuGroup = new MenuGroup(); // MenuGroup | 
    try {
      MenuGroup result = apiInstance.commonMenuGroupsIdPUT(id, menuGroup);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonMenuGroupsIdPUT");
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
 **id** | **String**|  |
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
**200** |  |  -  |

<a name="commonMenuGroupsPOST"></a>
# **commonMenuGroupsPOST**
> MenuGroup commonMenuGroupsPOST(menuGroup)



Create MenuGroup

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    MenuGroup menuGroup = new MenuGroup(); // MenuGroup | 
    try {
      MenuGroup result = apiInstance.commonMenuGroupsPOST(menuGroup);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonMenuGroupsPOST");
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
**201** |  |  -  |

<a name="commonMenuItemsFormFieldsGET"></a>
# **commonMenuItemsFormFieldsGET**
> Map&lt;String, Object&gt; commonMenuItemsFormFieldsGET()



GET model form fields description to build UI form for an object:       - field_type: str - CharField, IntegerField, SomeSerializerField - i.e. fields from a serializer      - ui_element: dict - {type: (\&quot;input\&quot; | \&quot;select\&quot; | \&quot;checkbox\&quot; | ...), data_type: (\&quot;string\&quot;, \&quot;integer\&quot;, \&quot;date\&quot;, ...), ...}      - label: str - field label declared in a serializer field (default NULL)      - field_name: str - field name declared in a serializer field (default NULL)      - help_text: str - field help text declared in a serializer field (default NULL)      - required: bool - whether field is required      - read_only: bool - whether field is read only      - allow_null: bool - whether field is may be null      - default: bool - default (initial) field value for a new object (default NULL)      - choices: array - choices to select from [{choice_id1: choice_verbose_name1, ....}] (default NULL)

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    try {
      Map<String, Object> result = apiInstance.commonMenuItemsFormFieldsGET();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonMenuItemsFormFieldsGET");
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

<a name="commonMenuItemsGET"></a>
# **commonMenuItemsGET**
> List&lt;MenuItem&gt; commonMenuItemsGET()



MenuItem List

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    try {
      List<MenuItem> result = apiInstance.commonMenuItemsGET();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonMenuItemsGET");
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

[**List&lt;MenuItem&gt;**](MenuItem.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="commonMenuItemsIdDELETE"></a>
# **commonMenuItemsIdDELETE**
> commonMenuItemsIdDELETE(id)



Delete MenuItem

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String id = "id_example"; // String | 
    try {
      apiInstance.commonMenuItemsIdDELETE(id);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonMenuItemsIdDELETE");
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
 **id** | **String**|  |

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

<a name="commonMenuItemsIdFormFieldsGET"></a>
# **commonMenuItemsIdFormFieldsGET**
> Map&lt;String, Object&gt; commonMenuItemsIdFormFieldsGET(id)



GET model form fields description to build UI form for EXISTING object:       - value: any - object field value      - field_type: str - CharField, IntegerField, SomeSerializerField - i.e. fields from a serializer      - ui_element: dict - {type: (\&quot;input\&quot; | \&quot;select\&quot; | \&quot;checkbox\&quot; | ...), data_type: (\&quot;string\&quot;, \&quot;integer\&quot;, \&quot;date\&quot;, ...), ...}      - label: str - field label declared in a serializer field (default NULL)      - field_name: str - field name declared in a serializer field (default NULL)      - help_text: str - field help text declared in a serializer field (default NULL)      - required: bool - whether field is required      - read_only: bool - whether field is read only      - allow_null: bool - whether field is may be null      - default: bool - default (initial) field value for a new object (default NULL)      - choices: array - choices to select from [{choice_id1: choice_verbose_name1, ....}] (default NULL)

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this user.
    try {
      Map<String, Object> result = apiInstance.commonMenuItemsIdFormFieldsGET(id);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonMenuItemsIdFormFieldsGET");
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
 **id** | **String**| A unique integer value identifying this user. |

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

<a name="commonMenuItemsIdGET"></a>
# **commonMenuItemsIdGET**
> MenuItem commonMenuItemsIdGET(id)



Retrieve MenuItem

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String id = "id_example"; // String | 
    try {
      MenuItem result = apiInstance.commonMenuItemsIdGET(id);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonMenuItemsIdGET");
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
 **id** | **String**|  |

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
**200** |  |  -  |

<a name="commonMenuItemsIdPATCH"></a>
# **commonMenuItemsIdPATCH**
> MenuItem commonMenuItemsIdPATCH(id, menuItem)



Partial Update MenuItem

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String id = "id_example"; // String | 
    MenuItem menuItem = new MenuItem(); // MenuItem | 
    try {
      MenuItem result = apiInstance.commonMenuItemsIdPATCH(id, menuItem);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonMenuItemsIdPATCH");
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
 **id** | **String**|  |
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
**200** |  |  -  |

<a name="commonMenuItemsIdPUT"></a>
# **commonMenuItemsIdPUT**
> MenuItem commonMenuItemsIdPUT(id, menuItem)



Update MenuItem

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String id = "id_example"; // String | 
    MenuItem menuItem = new MenuItem(); // MenuItem | 
    try {
      MenuItem result = apiInstance.commonMenuItemsIdPUT(id, menuItem);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonMenuItemsIdPUT");
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
 **id** | **String**|  |
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
**200** |  |  -  |

<a name="commonMenuItemsPOST"></a>
# **commonMenuItemsPOST**
> MenuItem commonMenuItemsPOST(menuItem)



Create MenuItem

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    MenuItem menuItem = new MenuItem(); // MenuItem | 
    try {
      MenuItem result = apiInstance.commonMenuItemsPOST(menuItem);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonMenuItemsPOST");
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
**201** |  |  -  |

<a name="commonReviewStatusGroupsGET"></a>
# **commonReviewStatusGroupsGET**
> List&lt;ReviewStatusGroup&gt; commonReviewStatusGroupsGET(jqFilters)



ReviewStatusGroup List

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      List<ReviewStatusGroup> result = apiInstance.commonReviewStatusGroupsGET(jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonReviewStatusGroupsGET");
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

[**List&lt;ReviewStatusGroup&gt;**](ReviewStatusGroup.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="commonReviewStatusGroupsIdDELETE"></a>
# **commonReviewStatusGroupsIdDELETE**
> commonReviewStatusGroupsIdDELETE(id)



Delete ReviewStatusGroup

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this Review Status Group.
    try {
      apiInstance.commonReviewStatusGroupsIdDELETE(id);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonReviewStatusGroupsIdDELETE");
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
 **id** | **String**| A unique integer value identifying this Review Status Group. |

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

<a name="commonReviewStatusGroupsIdGET"></a>
# **commonReviewStatusGroupsIdGET**
> ReviewStatusGroup commonReviewStatusGroupsIdGET(id, jqFilters)



Retrieve ReviewStatusGroup

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this Review Status Group.
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      ReviewStatusGroup result = apiInstance.commonReviewStatusGroupsIdGET(id, jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonReviewStatusGroupsIdGET");
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
 **id** | **String**| A unique integer value identifying this Review Status Group. |
 **jqFilters** | [**Map&lt;String, String&gt;**](String.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

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
**200** |  |  -  |

<a name="commonReviewStatusGroupsIdPATCH"></a>
# **commonReviewStatusGroupsIdPATCH**
> ReviewStatusGroup commonReviewStatusGroupsIdPATCH(id, reviewStatusGroup)



Partial Update ReviewStatusGroup

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this Review Status Group.
    ReviewStatusGroup reviewStatusGroup = new ReviewStatusGroup(); // ReviewStatusGroup | 
    try {
      ReviewStatusGroup result = apiInstance.commonReviewStatusGroupsIdPATCH(id, reviewStatusGroup);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonReviewStatusGroupsIdPATCH");
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
 **id** | **String**| A unique integer value identifying this Review Status Group. |
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
**200** |  |  -  |

<a name="commonReviewStatusGroupsIdPUT"></a>
# **commonReviewStatusGroupsIdPUT**
> ReviewStatusGroup commonReviewStatusGroupsIdPUT(id, reviewStatusGroup)



Update ReviewStatusGroup

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this Review Status Group.
    ReviewStatusGroup reviewStatusGroup = new ReviewStatusGroup(); // ReviewStatusGroup | 
    try {
      ReviewStatusGroup result = apiInstance.commonReviewStatusGroupsIdPUT(id, reviewStatusGroup);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonReviewStatusGroupsIdPUT");
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
 **id** | **String**| A unique integer value identifying this Review Status Group. |
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
**200** |  |  -  |

<a name="commonReviewStatusGroupsPOST"></a>
# **commonReviewStatusGroupsPOST**
> ReviewStatusGroup commonReviewStatusGroupsPOST(reviewStatusGroup)



Create ReviewStatusGroup

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    ReviewStatusGroup reviewStatusGroup = new ReviewStatusGroup(); // ReviewStatusGroup | 
    try {
      ReviewStatusGroup result = apiInstance.commonReviewStatusGroupsPOST(reviewStatusGroup);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonReviewStatusGroupsPOST");
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
**201** |  |  -  |

<a name="commonReviewStatusesGET"></a>
# **commonReviewStatusesGET**
> List&lt;ReviewStatusDetail&gt; commonReviewStatusesGET(jqFilters)



ReviewStatus List

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      List<ReviewStatusDetail> result = apiInstance.commonReviewStatusesGET(jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonReviewStatusesGET");
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

[**List&lt;ReviewStatusDetail&gt;**](ReviewStatusDetail.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="commonReviewStatusesIdDELETE"></a>
# **commonReviewStatusesIdDELETE**
> commonReviewStatusesIdDELETE(id)



Delete ReviewStatus

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this Review Status.
    try {
      apiInstance.commonReviewStatusesIdDELETE(id);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonReviewStatusesIdDELETE");
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
 **id** | **String**| A unique integer value identifying this Review Status. |

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

<a name="commonReviewStatusesIdGET"></a>
# **commonReviewStatusesIdGET**
> ReviewStatusDetail commonReviewStatusesIdGET(id, jqFilters)



Retrieve ReviewStatus

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this Review Status.
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      ReviewStatusDetail result = apiInstance.commonReviewStatusesIdGET(id, jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonReviewStatusesIdGET");
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
 **id** | **String**| A unique integer value identifying this Review Status. |
 **jqFilters** | [**Map&lt;String, String&gt;**](String.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

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
**200** |  |  -  |

<a name="commonReviewStatusesIdPATCH"></a>
# **commonReviewStatusesIdPATCH**
> ReviewStatus commonReviewStatusesIdPATCH(id, reviewStatus)



Partial Update ReviewStatus

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this Review Status.
    ReviewStatus reviewStatus = new ReviewStatus(); // ReviewStatus | 
    try {
      ReviewStatus result = apiInstance.commonReviewStatusesIdPATCH(id, reviewStatus);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonReviewStatusesIdPATCH");
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
 **id** | **String**| A unique integer value identifying this Review Status. |
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
**200** |  |  -  |

<a name="commonReviewStatusesIdPUT"></a>
# **commonReviewStatusesIdPUT**
> ReviewStatus commonReviewStatusesIdPUT(id, reviewStatus)



Update ReviewStatus

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this Review Status.
    ReviewStatus reviewStatus = new ReviewStatus(); // ReviewStatus | 
    try {
      ReviewStatus result = apiInstance.commonReviewStatusesIdPUT(id, reviewStatus);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonReviewStatusesIdPUT");
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
 **id** | **String**| A unique integer value identifying this Review Status. |
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
**200** |  |  -  |

<a name="commonReviewStatusesPOST"></a>
# **commonReviewStatusesPOST**
> ReviewStatus commonReviewStatusesPOST(reviewStatus)



Create ReviewStatus

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.CommonApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    CommonApi apiInstance = new CommonApi(defaultClient);
    ReviewStatus reviewStatus = new ReviewStatus(); // ReviewStatus | 
    try {
      ReviewStatus result = apiInstance.commonReviewStatusesPOST(reviewStatus);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling CommonApi#commonReviewStatusesPOST");
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
**201** |  |  -  |

