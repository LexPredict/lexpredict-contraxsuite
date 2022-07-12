# Org.OpenAPITools.Api.UsersApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**UsersClientIdsGET**](UsersApi.md#usersclientidsget) | **GET** /api/v1/users/client-ids/ | 
[**UsersElevatePOST**](UsersApi.md#userselevatepost) | **POST** /api/v1/users/elevate/ | 
[**UsersGooglePOST**](UsersApi.md#usersgooglepost) | **POST** /api/v1/users/google/ | 
[**UsersOffice365POST**](UsersApi.md#usersoffice365post) | **POST** /api/v1/users/office365/ | 
[**UsersOktaPOST**](UsersApi.md#usersoktapost) | **POST** /api/v1/users/okta/ | 
[**UsersUsersFormFieldsGET**](UsersApi.md#usersusersformfieldsget) | **GET** /api/v1/users/users/form-fields/ | 
[**UsersUsersGET**](UsersApi.md#usersusersget) | **GET** /api/v1/users/users/ | 
[**UsersUsersIdFormFieldsGET**](UsersApi.md#usersusersidformfieldsget) | **GET** /api/v1/users/users/{id}/form-fields/ | 
[**UsersUsersIdGET**](UsersApi.md#usersusersidget) | **GET** /api/v1/users/users/{id}/ | 
[**UsersUsersIdPATCH**](UsersApi.md#usersusersidpatch) | **PATCH** /api/v1/users/users/{id}/ | 
[**UsersUsersIdPUT**](UsersApi.md#usersusersidput) | **PUT** /api/v1/users/users/{id}/ | 
[**UsersUsersPOST**](UsersApi.md#usersuserspost) | **POST** /api/v1/users/users/ | 
[**UsersUsersUserStatsGET**](UsersApi.md#usersusersuserstatsget) | **GET** /api/v1/users/users/user_stats/ | 
[**UsersVerifyTokenPOST**](UsersApi.md#usersverifytokenpost) | **POST** /api/v1/users/verify-token/ | 



## UsersClientIdsGET

> List&lt;SocialClientList&gt; UsersClientIdsGET ()



### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class UsersClientIdsGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new UsersApi(Configuration.Default);

            try
            {
                List<SocialClientList> result = apiInstance.UsersClientIdsGET();
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling UsersApi.UsersClientIdsGET: " + e.Message );
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

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UsersElevatePOST

> SocialLogin UsersElevatePOST (AccessTokenSchema accessTokenSchema = null)



Authenticate user (register first if the profile doesn't exist) via Elevate in CLM.  The login algorithm is next:  1. Redirect to google auth page `https://elmqa.elevateservices.com/services/oauth/authorize`     with correct `client_id`, `redirect_url`, and `response_type=token`; 2. After elevate auth user will be redirected to callback url; 3. Pass the `access_token` from query params to this endpoint.

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class UsersElevatePOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new UsersApi(Configuration.Default);
            var accessTokenSchema = new AccessTokenSchema(); // AccessTokenSchema |  (optional) 

            try
            {
                SocialLogin result = apiInstance.UsersElevatePOST(accessTokenSchema);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling UsersApi.UsersElevatePOST: " + e.Message );
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
 **accessTokenSchema** | [**AccessTokenSchema**](AccessTokenSchema.md)|  | [optional] 

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

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UsersGooglePOST

> SocialLogin UsersGooglePOST (Code code = null)



Authenticate user (register first if the profile doesn't exist) via Google in CLM.  The login algorithm is next:  1. Redirect to google auth page `https://accounts.google.com/o/oauth2/v2/auth`     with correct `client_id`, `redirect_url`; 2. After google auth user will be redirected to callback url; 3. Pass the `code` from query params to this endpoint.

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class UsersGooglePOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new UsersApi(Configuration.Default);
            var code = new Code(); // Code |  (optional) 

            try
            {
                SocialLogin result = apiInstance.UsersGooglePOST(code);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling UsersApi.UsersGooglePOST: " + e.Message );
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
 **code** | [**Code**](Code.md)|  | [optional] 

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

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UsersOffice365POST

> SocialLogin UsersOffice365POST (Code code = null)



Authenticate user (register first if the profile doesn't exist) via Microsoft office365 in CLM.  The login algorithm is next:  1. Redirect to microsoft auth page `https://login.microsoftonline.com/consumers|common/oauth2/v2.0/authorize`     with correct `client_id`, `redirect_url`, `response_type`, and `scope`; 2. After microsoft auth user will be redirected to callback url; 3. Pass the `code` from query params to this endpoint.

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class UsersOffice365POSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new UsersApi(Configuration.Default);
            var code = new Code(); // Code |  (optional) 

            try
            {
                SocialLogin result = apiInstance.UsersOffice365POST(code);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling UsersApi.UsersOffice365POST: " + e.Message );
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
 **code** | [**Code**](Code.md)|  | [optional] 

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

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UsersOktaPOST

> SocialLogin UsersOktaPOST (Code code = null)



Authenticate user (register first if the profile doesn't exist) via Okta in CLM.  The login algorithm is next:  1. Redirect to okta auth page `https://{{your domain}}.okta.com/oauth2/default/v1/authorize`     with correct `client_id`, `redirect_url`, `scope`, and `state`; 2. After google auth user will be redirected to callback url; 3. Pass the `code` from query params to this endpoint.

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class UsersOktaPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new UsersApi(Configuration.Default);
            var code = new Code(); // Code |  (optional) 

            try
            {
                SocialLogin result = apiInstance.UsersOktaPOST(code);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling UsersApi.UsersOktaPOST: " + e.Message );
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
 **code** | [**Code**](Code.md)|  | [optional] 

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

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UsersUsersFormFieldsGET

> Dictionary&lt;string, Object&gt; UsersUsersFormFieldsGET ()



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
    public class UsersUsersFormFieldsGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new UsersApi(Configuration.Default);

            try
            {
                Dictionary<string, Object> result = apiInstance.UsersUsersFormFieldsGET();
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling UsersApi.UsersUsersFormFieldsGET: " + e.Message );
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


## UsersUsersGET

> List&lt;User&gt; UsersUsersGET (Dictionary<string, string> jqFilters = null)



User List

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class UsersUsersGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new UsersApi(Configuration.Default);
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                List<User> result = apiInstance.UsersUsersGET(jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling UsersApi.UsersUsersGET: " + e.Message );
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

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UsersUsersIdFormFieldsGET

> Dictionary&lt;string, Object&gt; UsersUsersIdFormFieldsGET (string id)



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
    public class UsersUsersIdFormFieldsGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new UsersApi(Configuration.Default);
            var id = "id_example";  // string | A unique integer value identifying this user.

            try
            {
                Dictionary<string, Object> result = apiInstance.UsersUsersIdFormFieldsGET(id);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling UsersApi.UsersUsersIdFormFieldsGET: " + e.Message );
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


## UsersUsersIdGET

> User UsersUsersIdGET (string id, Dictionary<string, string> jqFilters = null)



Retrieve User

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class UsersUsersIdGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new UsersApi(Configuration.Default);
            var id = "id_example";  // string | A unique integer value identifying this user.
            var jqFilters = new Dictionary<string, string>(); // Dictionary<string, string> | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional) 

            try
            {
                User result = apiInstance.UsersUsersIdGET(id, jqFilters);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling UsersApi.UsersUsersIdGET: " + e.Message );
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
 **jqFilters** | [**Dictionary&lt;string, string&gt;**](string.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

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

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UsersUsersIdPATCH

> UserProfile UsersUsersIdPATCH (string id, UserProfile userProfile = null)



Partial Update User

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class UsersUsersIdPATCHExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new UsersApi(Configuration.Default);
            var id = "id_example";  // string | A unique integer value identifying this user.
            var userProfile = new UserProfile(); // UserProfile |  (optional) 

            try
            {
                UserProfile result = apiInstance.UsersUsersIdPATCH(id, userProfile);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling UsersApi.UsersUsersIdPATCH: " + e.Message );
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
 **userProfile** | [**UserProfile**](UserProfile.md)|  | [optional] 

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

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UsersUsersIdPUT

> UserProfile UsersUsersIdPUT (string id, UserProfile userProfile = null)



Update User

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class UsersUsersIdPUTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new UsersApi(Configuration.Default);
            var id = "id_example";  // string | A unique integer value identifying this user.
            var userProfile = new UserProfile(); // UserProfile |  (optional) 

            try
            {
                UserProfile result = apiInstance.UsersUsersIdPUT(id, userProfile);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling UsersApi.UsersUsersIdPUT: " + e.Message );
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
 **userProfile** | [**UserProfile**](UserProfile.md)|  | [optional] 

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

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UsersUsersPOST

> UserProfile UsersUsersPOST (UserProfile userProfile = null)



Create User

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class UsersUsersPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new UsersApi(Configuration.Default);
            var userProfile = new UserProfile(); // UserProfile |  (optional) 

            try
            {
                UserProfile result = apiInstance.UsersUsersPOST(userProfile);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling UsersApi.UsersUsersPOST: " + e.Message );
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
 **userProfile** | [**UserProfile**](UserProfile.md)|  | [optional] 

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

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UsersUsersUserStatsGET

> List&lt;UserStats&gt; UsersUsersUserStatsGET ()



User stats: projects, document types, tasks

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class UsersUsersUserStatsGETExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new UsersApi(Configuration.Default);

            try
            {
                List<UserStats> result = apiInstance.UsersUsersUserStatsGET();
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling UsersApi.UsersUsersUserStatsGET: " + e.Message );
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

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UsersVerifyTokenPOST

> VerifyAuthTokenResponse UsersVerifyTokenPOST (VerifyAuthTokenRequest verifyAuthTokenRequest = null)



Get user data for provided auth_token.

### Example

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Client;
using Org.OpenAPITools.Model;

namespace Example
{
    public class UsersVerifyTokenPOSTExample
    {
        public static void Main()
        {
            Configuration.Default.BasePath = "http://localhost";
            // Configure API key authorization: AuthToken
            Configuration.Default.AddApiKey("Authorization", "YOUR_API_KEY");
            // Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
            // Configuration.Default.AddApiKeyPrefix("Authorization", "Bearer");

            var apiInstance = new UsersApi(Configuration.Default);
            var verifyAuthTokenRequest = new VerifyAuthTokenRequest(); // VerifyAuthTokenRequest |  (optional) 

            try
            {
                VerifyAuthTokenResponse result = apiInstance.UsersVerifyTokenPOST(verifyAuthTokenRequest);
                Debug.WriteLine(result);
            }
            catch (ApiException e)
            {
                Debug.Print("Exception when calling UsersApi.UsersVerifyTokenPOST: " + e.Message );
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
 **verifyAuthTokenRequest** | [**VerifyAuthTokenRequest**](VerifyAuthTokenRequest.md)|  | [optional] 

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

[[Back to top]](#)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

