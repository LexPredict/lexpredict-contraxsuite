# UsersApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**usersClientIdsGET**](UsersApi.md#usersClientIdsGET) | **GET** /api/v1/users/client-ids/ |  |
| [**usersElevatePOST**](UsersApi.md#usersElevatePOST) | **POST** /api/v1/users/elevate/ |  |
| [**usersGooglePOST**](UsersApi.md#usersGooglePOST) | **POST** /api/v1/users/google/ |  |
| [**usersOffice365POST**](UsersApi.md#usersOffice365POST) | **POST** /api/v1/users/office365/ |  |
| [**usersOktaPOST**](UsersApi.md#usersOktaPOST) | **POST** /api/v1/users/okta/ |  |
| [**usersUsersFormFieldsGET**](UsersApi.md#usersUsersFormFieldsGET) | **GET** /api/v1/users/users/form-fields/ |  |
| [**usersUsersGET**](UsersApi.md#usersUsersGET) | **GET** /api/v1/users/users/ |  |
| [**usersUsersIdFormFieldsGET**](UsersApi.md#usersUsersIdFormFieldsGET) | **GET** /api/v1/users/users/{id}/form-fields/ |  |
| [**usersUsersIdGET**](UsersApi.md#usersUsersIdGET) | **GET** /api/v1/users/users/{id}/ |  |
| [**usersUsersIdPATCH**](UsersApi.md#usersUsersIdPATCH) | **PATCH** /api/v1/users/users/{id}/ |  |
| [**usersUsersIdPUT**](UsersApi.md#usersUsersIdPUT) | **PUT** /api/v1/users/users/{id}/ |  |
| [**usersUsersPOST**](UsersApi.md#usersUsersPOST) | **POST** /api/v1/users/users/ |  |
| [**usersUsersUserStatsGET**](UsersApi.md#usersUsersUserStatsGET) | **GET** /api/v1/users/users/user_stats/ |  |
| [**usersVerifyTokenPOST**](UsersApi.md#usersVerifyTokenPOST) | **POST** /api/v1/users/verify-token/ |  |


<a name="usersClientIdsGET"></a>
# **usersClientIdsGET**
> List&lt;SocialClientList&gt; usersClientIdsGET()





### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.UsersApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    UsersApi apiInstance = new UsersApi(defaultClient);
    try {
      List<SocialClientList> result = apiInstance.usersClientIdsGET();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling UsersApi#usersClientIdsGET");
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

[**List&lt;SocialClientList&gt;**](SocialClientList.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

<a name="usersElevatePOST"></a>
# **usersElevatePOST**
> SocialLogin usersElevatePOST(accessTokenSchema)



Authenticate user (register first if the profile doesn&#39;t exist) via Elevate in CLM.  The login algorithm is next:  1. Redirect to google auth page &#x60;https://elmqa.elevateservices.com/services/oauth/authorize&#x60;     with correct &#x60;client_id&#x60;, &#x60;redirect_url&#x60;, and &#x60;response_type&#x3D;token&#x60;; 2. After elevate auth user will be redirected to callback url; 3. Pass the &#x60;access_token&#x60; from query params to this endpoint.

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.UsersApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    UsersApi apiInstance = new UsersApi(defaultClient);
    AccessTokenSchema accessTokenSchema = new AccessTokenSchema(); // AccessTokenSchema | 
    try {
      SocialLogin result = apiInstance.usersElevatePOST(accessTokenSchema);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling UsersApi#usersElevatePOST");
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
| **accessTokenSchema** | [**AccessTokenSchema**](AccessTokenSchema.md)|  | [optional] |

### Return type

[**SocialLogin**](SocialLogin.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |

<a name="usersGooglePOST"></a>
# **usersGooglePOST**
> SocialLogin usersGooglePOST(code)



Authenticate user (register first if the profile doesn&#39;t exist) via Google in CLM.  The login algorithm is next:  1. Redirect to google auth page &#x60;https://accounts.google.com/o/oauth2/v2/auth&#x60;     with correct &#x60;client_id&#x60;, &#x60;redirect_url&#x60;; 2. After google auth user will be redirected to callback url; 3. Pass the &#x60;code&#x60; from query params to this endpoint.

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.UsersApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    UsersApi apiInstance = new UsersApi(defaultClient);
    Code code = new Code(); // Code | 
    try {
      SocialLogin result = apiInstance.usersGooglePOST(code);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling UsersApi#usersGooglePOST");
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
| **code** | [**Code**](Code.md)|  | [optional] |

### Return type

[**SocialLogin**](SocialLogin.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |

<a name="usersOffice365POST"></a>
# **usersOffice365POST**
> SocialLogin usersOffice365POST(code)



Authenticate user (register first if the profile doesn&#39;t exist) via Microsoft office365 in CLM.  The login algorithm is next:  1. Redirect to microsoft auth page &#x60;https://login.microsoftonline.com/consumers|common/oauth2/v2.0/authorize&#x60;     with correct &#x60;client_id&#x60;, &#x60;redirect_url&#x60;, &#x60;response_type&#x60;, and &#x60;scope&#x60;; 2. After microsoft auth user will be redirected to callback url; 3. Pass the &#x60;code&#x60; from query params to this endpoint.

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.UsersApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    UsersApi apiInstance = new UsersApi(defaultClient);
    Code code = new Code(); // Code | 
    try {
      SocialLogin result = apiInstance.usersOffice365POST(code);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling UsersApi#usersOffice365POST");
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
| **code** | [**Code**](Code.md)|  | [optional] |

### Return type

[**SocialLogin**](SocialLogin.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |

<a name="usersOktaPOST"></a>
# **usersOktaPOST**
> SocialLogin usersOktaPOST(code)



Authenticate user (register first if the profile doesn&#39;t exist) via Okta in CLM.  The login algorithm is next:  1. Redirect to okta auth page &#x60;https://{{your domain}}.okta.com/oauth2/default/v1/authorize&#x60;     with correct &#x60;client_id&#x60;, &#x60;redirect_url&#x60;, &#x60;scope&#x60;, and &#x60;state&#x60;; 2. After google auth user will be redirected to callback url; 3. Pass the &#x60;code&#x60; from query params to this endpoint.

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.UsersApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    UsersApi apiInstance = new UsersApi(defaultClient);
    Code code = new Code(); // Code | 
    try {
      SocialLogin result = apiInstance.usersOktaPOST(code);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling UsersApi#usersOktaPOST");
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
| **code** | [**Code**](Code.md)|  | [optional] |

### Return type

[**SocialLogin**](SocialLogin.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |

<a name="usersUsersFormFieldsGET"></a>
# **usersUsersFormFieldsGET**
> Map&lt;String, Object&gt; usersUsersFormFieldsGET()



GET model form fields description to build UI form for an object:       - field_type: str - CharField, IntegerField, SomeSerializerField - i.e. fields from a serializer      - ui_element: dict - {type: (\&quot;input\&quot; | \&quot;select\&quot; | \&quot;checkbox\&quot; | ...), data_type: (\&quot;string\&quot;, \&quot;integer\&quot;, \&quot;date\&quot;, ...), ...}      - label: str - field label declared in a serializer field (default NULL)      - field_name: str - field name declared in a serializer field (default NULL)      - help_text: str - field help text declared in a serializer field (default NULL)      - required: bool - whether field is required      - read_only: bool - whether field is read only      - allow_null: bool - whether field is may be null      - default: bool - default (initial) field value for a new object (default NULL)      - choices: array - choices to select from [{choice_id1: choice_verbose_name1, ....}] (default NULL)

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.UsersApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    UsersApi apiInstance = new UsersApi(defaultClient);
    try {
      Map<String, Object> result = apiInstance.usersUsersFormFieldsGET();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling UsersApi#usersUsersFormFieldsGET");
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

<a name="usersUsersGET"></a>
# **usersUsersGET**
> List&lt;User&gt; usersUsersGET(jqFilters)



User List

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.UsersApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    UsersApi apiInstance = new UsersApi(defaultClient);
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      List<User> result = apiInstance.usersUsersGET(jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling UsersApi#usersUsersGET");
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

[**List&lt;User&gt;**](User.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

<a name="usersUsersIdFormFieldsGET"></a>
# **usersUsersIdFormFieldsGET**
> Map&lt;String, Object&gt; usersUsersIdFormFieldsGET(id)



GET model form fields description to build UI form for EXISTING object:       - value: any - object field value      - field_type: str - CharField, IntegerField, SomeSerializerField - i.e. fields from a serializer      - ui_element: dict - {type: (\&quot;input\&quot; | \&quot;select\&quot; | \&quot;checkbox\&quot; | ...), data_type: (\&quot;string\&quot;, \&quot;integer\&quot;, \&quot;date\&quot;, ...), ...}      - label: str - field label declared in a serializer field (default NULL)      - field_name: str - field name declared in a serializer field (default NULL)      - help_text: str - field help text declared in a serializer field (default NULL)      - required: bool - whether field is required      - read_only: bool - whether field is read only      - allow_null: bool - whether field is may be null      - default: bool - default (initial) field value for a new object (default NULL)      - choices: array - choices to select from [{choice_id1: choice_verbose_name1, ....}] (default NULL)

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.UsersApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    UsersApi apiInstance = new UsersApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this user.
    try {
      Map<String, Object> result = apiInstance.usersUsersIdFormFieldsGET(id);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling UsersApi#usersUsersIdFormFieldsGET");
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
| **id** | **String**| A unique integer value identifying this user. | |

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

<a name="usersUsersIdGET"></a>
# **usersUsersIdGET**
> User usersUsersIdGET(id, jqFilters)



Retrieve User

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.UsersApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    UsersApi apiInstance = new UsersApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this user.
    Map<String, String> jqFilters = new HashMap(); // Map<String, String> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                            
    try {
      User result = apiInstance.usersUsersIdGET(id, jqFilters);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling UsersApi#usersUsersIdGET");
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
| **id** | **String**| A unique integer value identifying this user. | |
| **jqFilters** | [**Map&lt;String, String&gt;**](String.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] |

### Return type

[**User**](User.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

<a name="usersUsersIdPATCH"></a>
# **usersUsersIdPATCH**
> UserProfile usersUsersIdPATCH(id, userProfile)



Partial Update User

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.UsersApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    UsersApi apiInstance = new UsersApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this user.
    UserProfile userProfile = new UserProfile(); // UserProfile | 
    try {
      UserProfile result = apiInstance.usersUsersIdPATCH(id, userProfile);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling UsersApi#usersUsersIdPATCH");
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
| **id** | **String**| A unique integer value identifying this user. | |
| **userProfile** | [**UserProfile**](UserProfile.md)|  | [optional] |

### Return type

[**UserProfile**](UserProfile.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

<a name="usersUsersIdPUT"></a>
# **usersUsersIdPUT**
> UserProfile usersUsersIdPUT(id, userProfile)



Update User

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.UsersApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    UsersApi apiInstance = new UsersApi(defaultClient);
    String id = "id_example"; // String | A unique integer value identifying this user.
    UserProfile userProfile = new UserProfile(); // UserProfile | 
    try {
      UserProfile result = apiInstance.usersUsersIdPUT(id, userProfile);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling UsersApi#usersUsersIdPUT");
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
| **id** | **String**| A unique integer value identifying this user. | |
| **userProfile** | [**UserProfile**](UserProfile.md)|  | [optional] |

### Return type

[**UserProfile**](UserProfile.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

<a name="usersUsersPOST"></a>
# **usersUsersPOST**
> UserProfile usersUsersPOST(userProfile)



Create User

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.UsersApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    UsersApi apiInstance = new UsersApi(defaultClient);
    UserProfile userProfile = new UserProfile(); // UserProfile | 
    try {
      UserProfile result = apiInstance.usersUsersPOST(userProfile);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling UsersApi#usersUsersPOST");
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
| **userProfile** | [**UserProfile**](UserProfile.md)|  | [optional] |

### Return type

[**UserProfile**](UserProfile.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |

<a name="usersUsersUserStatsGET"></a>
# **usersUsersUserStatsGET**
> List&lt;UserStats&gt; usersUsersUserStatsGET()



User stats: projects, document types, tasks

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.UsersApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    UsersApi apiInstance = new UsersApi(defaultClient);
    try {
      List<UserStats> result = apiInstance.usersUsersUserStatsGET();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling UsersApi#usersUsersUserStatsGET");
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

[**List&lt;UserStats&gt;**](UserStats.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

<a name="usersVerifyTokenPOST"></a>
# **usersVerifyTokenPOST**
> VerifyAuthTokenResponse usersVerifyTokenPOST(verifyAuthTokenRequest)



Get user data for provided auth_token.

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.UsersApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    UsersApi apiInstance = new UsersApi(defaultClient);
    VerifyAuthTokenRequest verifyAuthTokenRequest = new VerifyAuthTokenRequest(); // VerifyAuthTokenRequest | 
    try {
      VerifyAuthTokenResponse result = apiInstance.usersVerifyTokenPOST(verifyAuthTokenRequest);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling UsersApi#usersVerifyTokenPOST");
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
| **verifyAuthTokenRequest** | [**VerifyAuthTokenRequest**](VerifyAuthTokenRequest.md)|  | [optional] |

### Return type

[**VerifyAuthTokenResponse**](VerifyAuthTokenResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |
| **403** |  |  -  |

