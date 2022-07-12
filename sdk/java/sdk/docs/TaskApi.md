# TaskApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**taskCleanTasksPOST**](TaskApi.md#taskCleanTasksPOST) | **POST** /api/v1/task/clean-tasks/ |  |
| [**taskLoadDictionariesPOST**](TaskApi.md#taskLoadDictionariesPOST) | **POST** /api/v1/task/load-dictionaries/ |  |
| [**taskLoadDocumentsGET**](TaskApi.md#taskLoadDocumentsGET) | **GET** /api/v1/task/load-documents/ |  |
| [**taskLoadDocumentsPOST**](TaskApi.md#taskLoadDocumentsPOST) | **POST** /api/v1/task/load-documents/ |  |
| [**taskLocateGET**](TaskApi.md#taskLocateGET) | **GET** /api/v1/task/locate/ |  |
| [**taskLocatePOST**](TaskApi.md#taskLocatePOST) | **POST** /api/v1/task/locate/ |  |
| [**taskProcessTextExtractionResultsRequestIdPOST**](TaskApi.md#taskProcessTextExtractionResultsRequestIdPOST) | **POST** /api/v1/task/process_text_extraction_results/{request_id}/ |  |
| [**taskPurgeTaskPOST**](TaskApi.md#taskPurgeTaskPOST) | **POST** /api/v1/task/purge-task/ |  |
| [**taskRecallTaskGET**](TaskApi.md#taskRecallTaskGET) | **GET** /api/v1/task/recall-task/ |  |
| [**taskRecallTaskPOST**](TaskApi.md#taskRecallTaskPOST) | **POST** /api/v1/task/recall-task/ |  |
| [**taskReindexroutinesCheckSchedulePOST**](TaskApi.md#taskReindexroutinesCheckSchedulePOST) | **POST** /api/v1/task/reindexroutines/check_schedule |  |
| [**taskTaskLogGET**](TaskApi.md#taskTaskLogGET) | **GET** /api/v1/task/task-log/ |  |
| [**taskTaskStatusGET**](TaskApi.md#taskTaskStatusGET) | **GET** /api/v1/task/task-status/ |  |
| [**taskTasksGET**](TaskApi.md#taskTasksGET) | **GET** /api/v1/task/tasks/ |  |
| [**taskTasksIdGET**](TaskApi.md#taskTasksIdGET) | **GET** /api/v1/task/tasks/{id}/ |  |
| [**taskTasksProjectProjectIdActiveTasksGET**](TaskApi.md#taskTasksProjectProjectIdActiveTasksGET) | **GET** /api/v1/task/tasks/project/{project_id}/active-tasks/ |  |
| [**taskTasksProjectProjectIdTasksGET**](TaskApi.md#taskTasksProjectProjectIdTasksGET) | **GET** /api/v1/task/tasks/project/{project_id}/tasks/ |  |
| [**taskUpdateElasticIndexGET**](TaskApi.md#taskUpdateElasticIndexGET) | **GET** /api/v1/task/update-elastic-index/ |  |
| [**taskUpdateElasticIndexPOST**](TaskApi.md#taskUpdateElasticIndexPOST) | **POST** /api/v1/task/update-elastic-index/ |  |


<a name="taskCleanTasksPOST"></a>
# **taskCleanTasksPOST**
> Map&lt;String, Object&gt; taskCleanTasksPOST(requestBody)



\&quot;Clean Tasks\&quot; admin task

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.TaskApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    TaskApi apiInstance = new TaskApi(defaultClient);
    Map<String, Object> requestBody = null; // Map<String, Object> | 
    try {
      Map<String, Object> result = apiInstance.taskCleanTasksPOST(requestBody);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling TaskApi#taskCleanTasksPOST");
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
| **requestBody** | [**Map&lt;String, Object&gt;**](Object.md)|  | [optional] |

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

<a name="taskLoadDictionariesPOST"></a>
# **taskLoadDictionariesPOST**
> Map&lt;String, Object&gt; taskLoadDictionariesPOST(requestBody)



\&quot;Load Dictionaries\&quot; admin task  POST params:     - terms_accounting: bool:     - terms_accounting_1: bool:     - terms_accounting_1_locale_en: bool:     - terms_accounting_2: bool:     - terms_accounting_2_locale_en: bool:     - terms_accounting_3: bool:     - terms_accounting_3_locale_en: bool:     - terms_accounting_4: bool:     - terms_accounting_4_locale_en: bool:     - terms_accounting_5: bool:     - terms_accounting_5_locale_en: bool:     - terms_scientific: bool:     - terms_scientific_1: bool:     - terms_scientific1_locale_en: bool:     - terms_financial: bool:     - terms_financial_1: bool:     - terms_financial_1_locale_en: bool:     - terms_legal: bool:     - terms_legal_1: bool:     - terms_legal_1_locale_en: bool:     - terms_legal_2: bool:     - terms_legal_2_locale_en: bool:     - terms_legal_3: bool:     - terms_legal_3_locale_en: bool:     - terms_legal_4: bool:     - terms_legal_4_locale_en: bool:     - terms_file_path: str:     - terms_delete: bool:     - courts: bool:     - courts_1: bool:     - courts_1_locale_en: bool:     - courts_2: bool:     - courts_2_locale_en: bool:     - courts_file_path: str:     - courts_delete: bool:     - geoentities: bool:     - geoentities_1: bool:     - geoentities_1_locale_multi: bool:     - geoentities_file_path: str:     - geoentities_delete: bool:

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.TaskApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    TaskApi apiInstance = new TaskApi(defaultClient);
    Map<String, Object> requestBody = null; // Map<String, Object> | 
    try {
      Map<String, Object> result = apiInstance.taskLoadDictionariesPOST(requestBody);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling TaskApi#taskLoadDictionariesPOST");
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
| **requestBody** | [**Map&lt;String, Object&gt;**](Object.md)|  | [optional] |

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

<a name="taskLoadDocumentsGET"></a>
# **taskLoadDocumentsGET**
> Map&lt;String, Object&gt; taskLoadDocumentsGET()



\&quot;Load Documents\&quot; admin task  POST params:     - project: int     - source_data: str     - source_type: str     - document_type: str     - delete: bool     - run_standard_locators: bool

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.TaskApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    TaskApi apiInstance = new TaskApi(defaultClient);
    try {
      Map<String, Object> result = apiInstance.taskLoadDocumentsGET();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling TaskApi#taskLoadDocumentsGET");
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

<a name="taskLoadDocumentsPOST"></a>
# **taskLoadDocumentsPOST**
> Map&lt;String, Object&gt; taskLoadDocumentsPOST(requestBody)



\&quot;Load Documents\&quot; admin task  POST params:     - project: int     - source_data: str     - source_type: str     - document_type: str     - delete: bool     - run_standard_locators: bool

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.TaskApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    TaskApi apiInstance = new TaskApi(defaultClient);
    Map<String, Object> requestBody = null; // Map<String, Object> | 
    try {
      Map<String, Object> result = apiInstance.taskLoadDocumentsPOST(requestBody);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling TaskApi#taskLoadDocumentsPOST");
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
| **requestBody** | [**Map&lt;String, Object&gt;**](Object.md)|  | [optional] |

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

<a name="taskLocateGET"></a>
# **taskLocateGET**
> Map&lt;String, Object&gt; taskLocateGET()



\&quot;Locate\&quot; admin task  POST params:     - locate_all: bool     - geoentity_locate: bool     - geoentity_priority: bool     - geoentity_delete: bool     - date_locate: bool     - date_strict: bool     - date_delete: bool     - amount_locate: bool     - amount_delete: bool     - citation_locate: bool     - citation_delete: bool     - copyright_locate: bool     - copyright_delete: bool     - court_locate: bool     - court_delete: bool     - currency_locate: bool     - currency_delete: bool     - duration_locate: bool     - duration_delete: bool     - definition_locate: bool     - definition_delete: bool     - distance_locate: bool     - distance_delete: bool     - party_locate: bool     - party_delete: bool     - percent_locate: bool     - percent_delete: bool     - ratio_locate: bool     - ratio_delete: bool     - regulation_locate: bool     - regulation_delete: bool     - term_locate: bool     - term_delete: bool     - trademark_locate: bool     - trademark_delete: bool     - url_locate: bool     - url_delete: bool     - parse_choice_sentence: bool     - parse_choice_paragraph: bool     - project: int

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.TaskApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    TaskApi apiInstance = new TaskApi(defaultClient);
    try {
      Map<String, Object> result = apiInstance.taskLocateGET();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling TaskApi#taskLocateGET");
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

<a name="taskLocatePOST"></a>
# **taskLocatePOST**
> Map&lt;String, Object&gt; taskLocatePOST(requestBody)



\&quot;Locate\&quot; admin task  POST params:     - locate_all: bool     - geoentity_locate: bool     - geoentity_priority: bool     - geoentity_delete: bool     - date_locate: bool     - date_strict: bool     - date_delete: bool     - amount_locate: bool     - amount_delete: bool     - citation_locate: bool     - citation_delete: bool     - copyright_locate: bool     - copyright_delete: bool     - court_locate: bool     - court_delete: bool     - currency_locate: bool     - currency_delete: bool     - duration_locate: bool     - duration_delete: bool     - definition_locate: bool     - definition_delete: bool     - distance_locate: bool     - distance_delete: bool     - party_locate: bool     - party_delete: bool     - percent_locate: bool     - percent_delete: bool     - ratio_locate: bool     - ratio_delete: bool     - regulation_locate: bool     - regulation_delete: bool     - term_locate: bool     - term_delete: bool     - trademark_locate: bool     - trademark_delete: bool     - url_locate: bool     - url_delete: bool     - parse_choice_sentence: bool     - parse_choice_paragraph: bool     - project: int

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.TaskApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    TaskApi apiInstance = new TaskApi(defaultClient);
    Map<String, Object> requestBody = null; // Map<String, Object> | 
    try {
      Map<String, Object> result = apiInstance.taskLocatePOST(requestBody);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling TaskApi#taskLocatePOST");
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
| **requestBody** | [**Map&lt;String, Object&gt;**](Object.md)|  | [optional] |

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

<a name="taskProcessTextExtractionResultsRequestIdPOST"></a>
# **taskProcessTextExtractionResultsRequestIdPOST**
> Object taskProcessTextExtractionResultsRequestIdPOST(requestId, requestBody)





### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.TaskApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    TaskApi apiInstance = new TaskApi(defaultClient);
    String requestId = "requestId_example"; // String | 
    Map<String, Object> requestBody = null; // Map<String, Object> | 
    try {
      Object result = apiInstance.taskProcessTextExtractionResultsRequestIdPOST(requestId, requestBody);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling TaskApi#taskProcessTextExtractionResultsRequestIdPOST");
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
| **requestId** | **String**|  | |
| **requestBody** | [**Map&lt;String, Object&gt;**](Object.md)|  | [optional] |

### Return type

**Object**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |

<a name="taskPurgeTaskPOST"></a>
# **taskPurgeTaskPOST**
> Map&lt;String, Object&gt; taskPurgeTaskPOST(requestBody)



\&quot;Purge Task\&quot; admin task  POST params:     - task_pk: int

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.TaskApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    TaskApi apiInstance = new TaskApi(defaultClient);
    Map<String, Object> requestBody = null; // Map<String, Object> | 
    try {
      Map<String, Object> result = apiInstance.taskPurgeTaskPOST(requestBody);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling TaskApi#taskPurgeTaskPOST");
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
| **requestBody** | [**Map&lt;String, Object&gt;**](Object.md)|  | [optional] |

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

<a name="taskRecallTaskGET"></a>
# **taskRecallTaskGET**
> Map&lt;String, Object&gt; taskRecallTaskGET()



\&quot;Recall Task\&quot; admin task  POST params:     - task_pk: int

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.TaskApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    TaskApi apiInstance = new TaskApi(defaultClient);
    try {
      Map<String, Object> result = apiInstance.taskRecallTaskGET();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling TaskApi#taskRecallTaskGET");
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

<a name="taskRecallTaskPOST"></a>
# **taskRecallTaskPOST**
> Map&lt;String, Object&gt; taskRecallTaskPOST(requestBody)



\&quot;Recall Task\&quot; admin task  POST params:     - task_pk: int

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.TaskApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    TaskApi apiInstance = new TaskApi(defaultClient);
    Map<String, Object> requestBody = null; // Map<String, Object> | 
    try {
      Map<String, Object> result = apiInstance.taskRecallTaskPOST(requestBody);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling TaskApi#taskRecallTaskPOST");
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
| **requestBody** | [**Map&lt;String, Object&gt;**](Object.md)|  | [optional] |

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

<a name="taskReindexroutinesCheckSchedulePOST"></a>
# **taskReindexroutinesCheckSchedulePOST**
> Object taskReindexroutinesCheckSchedulePOST(requestBody)





### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.TaskApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    TaskApi apiInstance = new TaskApi(defaultClient);
    Map<String, Object> requestBody = null; // Map<String, Object> | 
    try {
      Object result = apiInstance.taskReindexroutinesCheckSchedulePOST(requestBody);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling TaskApi#taskReindexroutinesCheckSchedulePOST");
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
| **requestBody** | [**Map&lt;String, Object&gt;**](Object.md)|  | [optional] |

### Return type

**Object**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |

<a name="taskTaskLogGET"></a>
# **taskTaskLogGET**
> List&lt;TaskLogResponse&gt; taskTaskLogGET(taskId, recordsLimit, jqFilters)



Get task log records GET params:     - task_id: int     - records_limit: int

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.TaskApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    TaskApi apiInstance = new TaskApi(defaultClient);
    String taskId = "taskId_example"; // String | 
    Integer recordsLimit = 56; // Integer | 
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      List<TaskLogResponse> result = apiInstance.taskTaskLogGET(taskId, recordsLimit, jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling TaskApi#taskTaskLogGET");
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
| **taskId** | **String**|  | |
| **recordsLimit** | **Integer**|  | [optional] |
| **jqFilters** | [**Map&lt;String, String&gt;**](String.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] |

### Return type

[**List&lt;TaskLogResponse&gt;**](TaskLogResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

<a name="taskTaskStatusGET"></a>
# **taskTaskStatusGET**
> Map&lt;String, Object&gt; taskTaskStatusGET(taskId)



Check admin task status  GET params:     - task_id: int

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.TaskApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    TaskApi apiInstance = new TaskApi(defaultClient);
    String taskId = "taskId_example"; // String | 
    try {
      Map<String, Object> result = apiInstance.taskTaskStatusGET(taskId);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling TaskApi#taskTaskStatusGET");
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
| **taskId** | **String**|  | [optional] |

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
| **404** |  |  -  |

<a name="taskTasksGET"></a>
# **taskTasksGET**
> List&lt;Task&gt; taskTasksGET(jqFilters)



Task List

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.TaskApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    TaskApi apiInstance = new TaskApi(defaultClient);
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      List<Task> result = apiInstance.taskTasksGET(jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling TaskApi#taskTasksGET");
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
| **jqFilters** | [**Map&lt;String, String&gt;**](String.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] |

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

<a name="taskTasksIdGET"></a>
# **taskTasksIdGET**
> Task taskTasksIdGET(id, jqFilters)



Retrieve Task

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.TaskApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    TaskApi apiInstance = new TaskApi(defaultClient);
    String id = "id_example"; // String | A unique value identifying this task.
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      Task result = apiInstance.taskTasksIdGET(id, jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling TaskApi#taskTasksIdGET");
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
| **id** | **String**| A unique value identifying this task. | |
| **jqFilters** | [**Map&lt;String, String&gt;**](String.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] |

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

<a name="taskTasksProjectProjectIdActiveTasksGET"></a>
# **taskTasksProjectProjectIdActiveTasksGET**
> List&lt;ProjectActiveTasks&gt; taskTasksProjectProjectIdActiveTasksGET(projectId, jqFilters)





### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.TaskApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    TaskApi apiInstance = new TaskApi(defaultClient);
    String projectId = "projectId_example"; // String | 
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      List<ProjectActiveTasks> result = apiInstance.taskTasksProjectProjectIdActiveTasksGET(projectId, jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling TaskApi#taskTasksProjectProjectIdActiveTasksGET");
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
| **jqFilters** | [**Map&lt;String, String&gt;**](String.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] |

### Return type

[**List&lt;ProjectActiveTasks&gt;**](ProjectActiveTasks.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

<a name="taskTasksProjectProjectIdTasksGET"></a>
# **taskTasksProjectProjectIdTasksGET**
> List&lt;ProjectTasks&gt; taskTasksProjectProjectIdTasksGET(projectId, jqFilters)





### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.TaskApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    TaskApi apiInstance = new TaskApi(defaultClient);
    String projectId = "projectId_example"; // String | 
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      List<ProjectTasks> result = apiInstance.taskTasksProjectProjectIdTasksGET(projectId, jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling TaskApi#taskTasksProjectProjectIdTasksGET");
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
| **jqFilters** | [**Map&lt;String, String&gt;**](String.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] |

### Return type

[**List&lt;ProjectTasks&gt;**](ProjectTasks.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

<a name="taskUpdateElasticIndexGET"></a>
# **taskUpdateElasticIndexGET**
> Map&lt;String, Object&gt; taskUpdateElasticIndexGET()



\&quot;Update ElasticSearch Index\&quot; admin task

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.TaskApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    TaskApi apiInstance = new TaskApi(defaultClient);
    try {
      Map<String, Object> result = apiInstance.taskUpdateElasticIndexGET();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling TaskApi#taskUpdateElasticIndexGET");
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

<a name="taskUpdateElasticIndexPOST"></a>
# **taskUpdateElasticIndexPOST**
> Map&lt;String, Object&gt; taskUpdateElasticIndexPOST(requestBody)



\&quot;Update ElasticSearch Index\&quot; admin task

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.TaskApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    TaskApi apiInstance = new TaskApi(defaultClient);
    Map<String, Object> requestBody = null; // Map<String, Object> | 
    try {
      Map<String, Object> result = apiInstance.taskUpdateElasticIndexPOST(requestBody);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling TaskApi#taskUpdateElasticIndexPOST");
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
| **requestBody** | [**Map&lt;String, Object&gt;**](Object.md)|  | [optional] |

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

