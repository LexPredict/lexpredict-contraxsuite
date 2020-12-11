# openapi_client.SimilarityApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**similarity_party_similarity_get**](SimilarityApi.md#similarity_party_similarity_get) | **GET** /api/v1/similarity/party-similarity/ | 
[**similarity_party_similarity_post**](SimilarityApi.md#similarity_party_similarity_post) | **POST** /api/v1/similarity/party-similarity/ | 
[**similarity_similarity_by_features_get**](SimilarityApi.md#similarity_similarity_by_features_get) | **GET** /api/v1/similarity/similarity-by-features/ | 
[**similarity_similarity_by_features_post**](SimilarityApi.md#similarity_similarity_by_features_post) | **POST** /api/v1/similarity/similarity-by-features/ | 
[**similarity_similarity_get**](SimilarityApi.md#similarity_similarity_get) | **GET** /api/v1/similarity/similarity/ | 
[**similarity_similarity_post**](SimilarityApi.md#similarity_similarity_post) | **POST** /api/v1/similarity/similarity/ | 


# **similarity_party_similarity_get**
> dict(str, object) similarity_party_similarity_get()



\"Party Similarity\" admin task  POST params:     - case_sensitive: bool     - similarity_type: str[]     - similarity_threshold: int     - delete: bool

### Example

* Api Key Authentication (AuthToken):
```python
from __future__ import print_function
import time
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AuthToken
configuration = openapi_client.Configuration(
    host = "http://localhost",
    api_key = {
        'AuthToken': 'YOUR_API_KEY'
    }
)
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.SimilarityApi(api_client)
    
    try:
        api_response = api_instance.similarity_party_similarity_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling SimilarityApi->similarity_party_similarity_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**dict(str, object)**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **similarity_party_similarity_post**
> SimilarityPOSTObjectResponse similarity_party_similarity_post(request_body=request_body)



\"Party Similarity\" admin task  POST params:     - case_sensitive: bool     - similarity_type: str[]     - similarity_threshold: int     - delete: bool

### Example

* Api Key Authentication (AuthToken):
```python
from __future__ import print_function
import time
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AuthToken
configuration = openapi_client.Configuration(
    host = "http://localhost",
    api_key = {
        'AuthToken': 'YOUR_API_KEY'
    }
)
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.SimilarityApi(api_client)
    request_body = None # dict(str, object) |  (optional)

    try:
        api_response = api_instance.similarity_party_similarity_post(request_body=request_body)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling SimilarityApi->similarity_party_similarity_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**dict(str, object)**](object.md)|  | [optional] 

### Return type

[**SimilarityPOSTObjectResponse**](SimilarityPOSTObjectResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **similarity_similarity_by_features_get**
> dict(str, object) similarity_similarity_by_features_get()



\"Similarity\" admin task  POST params:     - search_similar_documents: bool     - search_similar_text_units: bool     - similarity_threshold: int     - use_idf: bool     - delete: bool     - project: int     - feature_source: list - list[date, definition, duration, court,       currency_name, currency_value, term, party, geoentity]     - unit_type: str sentence|paragraph     - distance_type: str - see scipy.spatial.distance._METRICS

### Example

* Api Key Authentication (AuthToken):
```python
from __future__ import print_function
import time
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AuthToken
configuration = openapi_client.Configuration(
    host = "http://localhost",
    api_key = {
        'AuthToken': 'YOUR_API_KEY'
    }
)
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.SimilarityApi(api_client)
    
    try:
        api_response = api_instance.similarity_similarity_by_features_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling SimilarityApi->similarity_similarity_by_features_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**dict(str, object)**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **similarity_similarity_by_features_post**
> SimilarityPOSTObjectResponse similarity_similarity_by_features_post(request_body=request_body)



\"Similarity\" admin task  POST params:     - search_similar_documents: bool     - search_similar_text_units: bool     - similarity_threshold: int     - use_idf: bool     - delete: bool     - project: int     - feature_source: list - list[date, definition, duration, court,       currency_name, currency_value, term, party, geoentity]     - unit_type: str sentence|paragraph     - distance_type: str - see scipy.spatial.distance._METRICS

### Example

* Api Key Authentication (AuthToken):
```python
from __future__ import print_function
import time
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AuthToken
configuration = openapi_client.Configuration(
    host = "http://localhost",
    api_key = {
        'AuthToken': 'YOUR_API_KEY'
    }
)
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.SimilarityApi(api_client)
    request_body = None # dict(str, object) |  (optional)

    try:
        api_response = api_instance.similarity_similarity_by_features_post(request_body=request_body)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling SimilarityApi->similarity_similarity_by_features_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**dict(str, object)**](object.md)|  | [optional] 

### Return type

[**SimilarityPOSTObjectResponse**](SimilarityPOSTObjectResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **similarity_similarity_get**
> dict(str, object) similarity_similarity_get()



\"Similarity\" admin task  POST params:     - search_similar_documents: bool     - search_similar_text_units: bool     - similarity_threshold: int     - use_idf: bool     - delete: bool     - project: bool

### Example

* Api Key Authentication (AuthToken):
```python
from __future__ import print_function
import time
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AuthToken
configuration = openapi_client.Configuration(
    host = "http://localhost",
    api_key = {
        'AuthToken': 'YOUR_API_KEY'
    }
)
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.SimilarityApi(api_client)
    
    try:
        api_response = api_instance.similarity_similarity_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling SimilarityApi->similarity_similarity_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**dict(str, object)**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **similarity_similarity_post**
> SimilarityPOSTObjectResponse similarity_similarity_post(request_body=request_body)



\"Similarity\" admin task  POST params:     - search_similar_documents: bool     - search_similar_text_units: bool     - similarity_threshold: int     - use_idf: bool     - delete: bool     - project: bool

### Example

* Api Key Authentication (AuthToken):
```python
from __future__ import print_function
import time
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AuthToken
configuration = openapi_client.Configuration(
    host = "http://localhost",
    api_key = {
        'AuthToken': 'YOUR_API_KEY'
    }
)
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.SimilarityApi(api_client)
    request_body = None # dict(str, object) |  (optional)

    try:
        api_response = api_instance.similarity_similarity_post(request_body=request_body)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling SimilarityApi->similarity_similarity_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**dict(str, object)**](object.md)|  | [optional] 

### Return type

[**SimilarityPOSTObjectResponse**](SimilarityPOSTObjectResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

