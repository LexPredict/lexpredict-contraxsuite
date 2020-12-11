# RestAuthApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**restAuthLoginPOST**](RestAuthApi.md#restAuthLoginPOST) | **POST** /rest-auth/login/ | 
[**restAuthLogoutGET**](RestAuthApi.md#restAuthLogoutGET) | **GET** /rest-auth/logout/ | 
[**restAuthLogoutPOST**](RestAuthApi.md#restAuthLogoutPOST) | **POST** /rest-auth/logout/ | 
[**restAuthPasswordChangePOST**](RestAuthApi.md#restAuthPasswordChangePOST) | **POST** /rest-auth/password/change/ | 
[**restAuthPasswordResetConfirmPOST**](RestAuthApi.md#restAuthPasswordResetConfirmPOST) | **POST** /rest-auth/password/reset/confirm/ | 
[**restAuthPasswordResetPOST**](RestAuthApi.md#restAuthPasswordResetPOST) | **POST** /rest-auth/password/reset/ | 
[**restAuthRegistrationPOST**](RestAuthApi.md#restAuthRegistrationPOST) | **POST** /rest-auth/registration/ | 
[**restAuthRegistrationVerifyEmailPOST**](RestAuthApi.md#restAuthRegistrationVerifyEmailPOST) | **POST** /rest-auth/registration/verify-email/ | 


<a name="restAuthLoginPOST"></a>
# **restAuthLoginPOST**
> LoginResponse restAuthLoginPOST(login)



Check the credentials and return the REST Token if the credentials are valid and authenticated. Calls Django Auth login method to register User ID in Django session framework  Accept the following POST parameters: username, password Return the REST Framework Token Object&#39;s key.

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.RestAuthApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    RestAuthApi apiInstance = new RestAuthApi(defaultClient);
    Login login = new Login(); // Login | 
    try {
      LoginResponse result = apiInstance.restAuthLoginPOST(login);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling RestAuthApi#restAuthLoginPOST");
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
 **login** | [**Login**](Login.md)|  | [optional]

### Return type

[**LoginResponse**](LoginResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

<a name="restAuthLogoutGET"></a>
# **restAuthLogoutGET**
> List&lt;RestAuthCommonResponse&gt; restAuthLogoutGET()



Calls Django logout method and delete the Token object assigned to the current User object.  Accepts/Returns nothing.

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.RestAuthApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    RestAuthApi apiInstance = new RestAuthApi(defaultClient);
    try {
      List<RestAuthCommonResponse> result = apiInstance.restAuthLogoutGET();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling RestAuthApi#restAuthLogoutGET");
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

[**List&lt;RestAuthCommonResponse&gt;**](RestAuthCommonResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

<a name="restAuthLogoutPOST"></a>
# **restAuthLogoutPOST**
> RestAuthCommonResponse restAuthLogoutPOST(requestBody)



Calls Django logout method and delete the Token object assigned to the current User object.  Accepts/Returns nothing.

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.RestAuthApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    RestAuthApi apiInstance = new RestAuthApi(defaultClient);
    Map<String, Object> requestBody = null; // Map<String, Object> | 
    try {
      RestAuthCommonResponse result = apiInstance.restAuthLogoutPOST(requestBody);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling RestAuthApi#restAuthLogoutPOST");
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
 **requestBody** | [**Map&lt;String, Object&gt;**](Object.md)|  | [optional]

### Return type

[**RestAuthCommonResponse**](RestAuthCommonResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

<a name="restAuthPasswordChangePOST"></a>
# **restAuthPasswordChangePOST**
> RestAuthCommonResponse restAuthPasswordChangePOST(customPasswordChange)



Calls Django Auth SetPasswordForm save method.  Accepts the following POST parameters: new_password1, new_password2 Returns the success/fail message.

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.RestAuthApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    RestAuthApi apiInstance = new RestAuthApi(defaultClient);
    CustomPasswordChange customPasswordChange = new CustomPasswordChange(); // CustomPasswordChange | 
    try {
      RestAuthCommonResponse result = apiInstance.restAuthPasswordChangePOST(customPasswordChange);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling RestAuthApi#restAuthPasswordChangePOST");
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
 **customPasswordChange** | [**CustomPasswordChange**](CustomPasswordChange.md)|  | [optional]

### Return type

[**RestAuthCommonResponse**](RestAuthCommonResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

<a name="restAuthPasswordResetConfirmPOST"></a>
# **restAuthPasswordResetConfirmPOST**
> RestAuthCommonResponse restAuthPasswordResetConfirmPOST(customPasswordResetConfirm)



Password reset e-mail link is confirmed, therefore this resets the user&#39;s password.  Accepts the following POST parameters: token, uid,     new_password1, new_password2 Returns the success/fail message.

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.RestAuthApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    RestAuthApi apiInstance = new RestAuthApi(defaultClient);
    CustomPasswordResetConfirm customPasswordResetConfirm = new CustomPasswordResetConfirm(); // CustomPasswordResetConfirm | 
    try {
      RestAuthCommonResponse result = apiInstance.restAuthPasswordResetConfirmPOST(customPasswordResetConfirm);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling RestAuthApi#restAuthPasswordResetConfirmPOST");
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
 **customPasswordResetConfirm** | [**CustomPasswordResetConfirm**](CustomPasswordResetConfirm.md)|  | [optional]

### Return type

[**RestAuthCommonResponse**](RestAuthCommonResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

<a name="restAuthPasswordResetPOST"></a>
# **restAuthPasswordResetPOST**
> RestAuthCommonResponse restAuthPasswordResetPOST(customPasswordReset)



Calls Django Auth PasswordResetForm save method.  Accepts the following POST parameters: email Returns the success/fail message.

### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.RestAuthApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    RestAuthApi apiInstance = new RestAuthApi(defaultClient);
    CustomPasswordReset customPasswordReset = new CustomPasswordReset(); // CustomPasswordReset | 
    try {
      RestAuthCommonResponse result = apiInstance.restAuthPasswordResetPOST(customPasswordReset);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling RestAuthApi#restAuthPasswordResetPOST");
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
 **customPasswordReset** | [**CustomPasswordReset**](CustomPasswordReset.md)|  | [optional]

### Return type

[**RestAuthCommonResponse**](RestAuthCommonResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

<a name="restAuthRegistrationPOST"></a>
# **restAuthRegistrationPOST**
> Register restAuthRegistrationPOST(register)



### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.RestAuthApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    RestAuthApi apiInstance = new RestAuthApi(defaultClient);
    Register register = new Register(); // Register | 
    try {
      Register result = apiInstance.restAuthRegistrationPOST(register);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling RestAuthApi#restAuthRegistrationPOST");
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
 **register** | [**Register**](Register.md)|  | [optional]

### Return type

[**Register**](Register.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

<a name="restAuthRegistrationVerifyEmailPOST"></a>
# **restAuthRegistrationVerifyEmailPOST**
> VerifyEmail restAuthRegistrationVerifyEmailPOST(verifyEmail)



### Example
```java
// Import classes:
import org.openapitools.client.ApiClient;
import org.openapitools.client.ApiException;
import org.openapitools.client.Configuration;
import org.openapitools.client.auth.*;
import org.openapitools.client.models.*;
import org.openapitools.client.api.RestAuthApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");
    
    // Configure API key authorization: AuthToken
    ApiKeyAuth AuthToken = (ApiKeyAuth) defaultClient.getAuthentication("AuthToken");
    AuthToken.setApiKey("YOUR API KEY");
    // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
    //AuthToken.setApiKeyPrefix("Token");

    RestAuthApi apiInstance = new RestAuthApi(defaultClient);
    VerifyEmail verifyEmail = new VerifyEmail(); // VerifyEmail | 
    try {
      VerifyEmail result = apiInstance.restAuthRegistrationVerifyEmailPOST(verifyEmail);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling RestAuthApi#restAuthRegistrationVerifyEmailPOST");
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
 **verifyEmail** | [**VerifyEmail**](VerifyEmail.md)|  | [optional]

### Return type

[**VerifyEmail**](VerifyEmail.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

