# openapi_client.SimilarityApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**similarity_document_similarity_by_features_get**](SimilarityApi.md#similarity_document_similarity_by_features_get) | **GET** /api/v1/similarity/document-similarity-by-features/ | 
[**similarity_document_similarity_by_features_post**](SimilarityApi.md#similarity_document_similarity_by_features_post) | **POST** /api/v1/similarity/document-similarity-by-features/ | 
[**similarity_party_similarity_get**](SimilarityApi.md#similarity_party_similarity_get) | **GET** /api/v1/similarity/party-similarity/ | 
[**similarity_party_similarity_post**](SimilarityApi.md#similarity_party_similarity_post) | **POST** /api/v1/similarity/party-similarity/ | 
[**similarity_project_documents_similarity_by_vectors_get**](SimilarityApi.md#similarity_project_documents_similarity_by_vectors_get) | **GET** /api/v1/similarity/project-documents-similarity-by-vectors/ | 
[**similarity_project_documents_similarity_by_vectors_post**](SimilarityApi.md#similarity_project_documents_similarity_by_vectors_post) | **POST** /api/v1/similarity/project-documents-similarity-by-vectors/ | 
[**similarity_project_text_units_similarity_by_vectors_get**](SimilarityApi.md#similarity_project_text_units_similarity_by_vectors_get) | **GET** /api/v1/similarity/project-text-units-similarity-by-vectors/ | 
[**similarity_project_text_units_similarity_by_vectors_post**](SimilarityApi.md#similarity_project_text_units_similarity_by_vectors_post) | **POST** /api/v1/similarity/project-text-units-similarity-by-vectors/ | 
[**similarity_similarity_get**](SimilarityApi.md#similarity_similarity_get) | **GET** /api/v1/similarity/similarity/ | 
[**similarity_similarity_post**](SimilarityApi.md#similarity_similarity_post) | **POST** /api/v1/similarity/similarity/ | 
[**similarity_text_unit_similarity_by_features_get**](SimilarityApi.md#similarity_text_unit_similarity_by_features_get) | **GET** /api/v1/similarity/text-unit-similarity-by-features/ | 
[**similarity_text_unit_similarity_by_features_post**](SimilarityApi.md#similarity_text_unit_similarity_by_features_post) | **POST** /api/v1/similarity/text-unit-similarity-by-features/ | 


# **similarity_document_similarity_by_features_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} similarity_document_similarity_by_features_get()



\"Similarity\" admin task  POST params:     - similarity_threshold: int     - use_tfidf: bool     - delete: bool     - project: int     - feature_source: list - list[date, definition, duration, court,       currency_name, currency_value, term, party, geoentity]     - distance_type: str - see scipy.spatial.distance._METRICS

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import similarity_api
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
configuration.api_key['AuthToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = similarity_api.SimilarityApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_response = api_instance.similarity_document_similarity_by_features_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SimilarityApi->similarity_document_similarity_by_features_get: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

**{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**

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

# **similarity_document_similarity_by_features_post**
> SimilarityPOSTObjectResponse similarity_document_similarity_by_features_post()



\"Similarity\" admin task  POST params:     - similarity_threshold: int     - use_tfidf: bool     - delete: bool     - project: int     - feature_source: list - list[date, definition, duration, court,       currency_name, currency_value, term, party, geoentity]     - distance_type: str - see scipy.spatial.distance._METRICS

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import similarity_api
from openapi_client.model.similarity_post_object_response import SimilarityPOSTObjectResponse
from openapi_client.model.document_similarity_by_features_form import DocumentSimilarityByFeaturesForm
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
configuration.api_key['AuthToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = similarity_api.SimilarityApi(api_client)
    document_similarity_by_features_form = DocumentSimilarityByFeaturesForm(
        run_name="run_name_example",
        similarity_threshold=75,
        project=1,
        feature_source="term",
        distance_type="cosine",
        item_id=1,
        create_reverse_relations=True,
        use_tfidf=True,
        delete=True,
    ) # DocumentSimilarityByFeaturesForm |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.similarity_document_similarity_by_features_post(document_similarity_by_features_form=document_similarity_by_features_form)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SimilarityApi->similarity_document_similarity_by_features_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_similarity_by_features_form** | [**DocumentSimilarityByFeaturesForm**](DocumentSimilarityByFeaturesForm.md)|  | [optional]

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

# **similarity_party_similarity_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} similarity_party_similarity_get()



\"Party Similarity\" admin task  POST params:     - case_sensitive: bool     - similarity_type: str[]     - similarity_threshold: int     - delete: bool

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import similarity_api
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
configuration.api_key['AuthToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = similarity_api.SimilarityApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_response = api_instance.similarity_party_similarity_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SimilarityApi->similarity_party_similarity_get: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

**{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**

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
> SimilarityPOSTObjectResponse similarity_party_similarity_post()



\"Party Similarity\" admin task  POST params:     - case_sensitive: bool     - similarity_type: str[]     - similarity_threshold: int     - delete: bool

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import similarity_api
from openapi_client.model.party_similarity_form import PartySimilarityForm
from openapi_client.model.similarity_post_object_response import SimilarityPOSTObjectResponse
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
configuration.api_key['AuthToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = similarity_api.SimilarityApi(api_client)
    party_similarity_form = PartySimilarityForm(
        run_name="run_name_example",
        case_sensitive=True,
        similarity_type="token_set_ratio",
        similarity_threshold=90,
        delete=True,
    ) # PartySimilarityForm |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.similarity_party_similarity_post(party_similarity_form=party_similarity_form)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SimilarityApi->similarity_party_similarity_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **party_similarity_form** | [**PartySimilarityForm**](PartySimilarityForm.md)|  | [optional]

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

# **similarity_project_documents_similarity_by_vectors_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} similarity_project_documents_similarity_by_vectors_get()



\"Similarity\" admin task  POST params:     - project_id: int     - distance_type: str - see scipy.spatial.distance._METRICS     - similarity_threshold: int     - feature_source: \"vector\"     - create_reverse_relations: bool - create B-A relations     - item_id: int     - use_tfidf: bool     - delete: bool

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import similarity_api
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
configuration.api_key['AuthToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = similarity_api.SimilarityApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_response = api_instance.similarity_project_documents_similarity_by_vectors_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SimilarityApi->similarity_project_documents_similarity_by_vectors_get: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

**{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**

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

# **similarity_project_documents_similarity_by_vectors_post**
> SimilarityPOSTObjectResponse similarity_project_documents_similarity_by_vectors_post()



\"Similarity\" admin task  POST params:     - project_id: int     - distance_type: str - see scipy.spatial.distance._METRICS     - similarity_threshold: int     - feature_source: \"vector\"     - create_reverse_relations: bool - create B-A relations     - item_id: int     - use_tfidf: bool     - delete: bool

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import similarity_api
from openapi_client.model.project_documents_similarity_by_vectors_form import ProjectDocumentsSimilarityByVectorsForm
from openapi_client.model.similarity_post_object_response import SimilarityPOSTObjectResponse
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
configuration.api_key['AuthToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = similarity_api.SimilarityApi(api_client)
    project_documents_similarity_by_vectors_form = ProjectDocumentsSimilarityByVectorsForm(
        run_name="run_name_example",
        similarity_threshold=75,
        project=1,
        feature_source="vector",
        distance_type="cosine",
        item_id=1,
        create_reverse_relations=True,
        use_tfidf=True,
        delete=True,
    ) # ProjectDocumentsSimilarityByVectorsForm |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.similarity_project_documents_similarity_by_vectors_post(project_documents_similarity_by_vectors_form=project_documents_similarity_by_vectors_form)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SimilarityApi->similarity_project_documents_similarity_by_vectors_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_documents_similarity_by_vectors_form** | [**ProjectDocumentsSimilarityByVectorsForm**](ProjectDocumentsSimilarityByVectorsForm.md)|  | [optional]

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

# **similarity_project_text_units_similarity_by_vectors_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} similarity_project_text_units_similarity_by_vectors_get()



\"Similarity\" admin task  POST params:     - project_id: int     - distance_type: str - see scipy.spatial.distance._METRICS     - similarity_threshold: int     - unit_type: str sentence|paragraph     - feature_source: \"vector\"     - create_reverse_relations: bool - create B-A relations     - use_tfidf: bool     - delete: bool

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import similarity_api
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
configuration.api_key['AuthToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = similarity_api.SimilarityApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_response = api_instance.similarity_project_text_units_similarity_by_vectors_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SimilarityApi->similarity_project_text_units_similarity_by_vectors_get: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

**{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**

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

# **similarity_project_text_units_similarity_by_vectors_post**
> SimilarityPOSTObjectResponse similarity_project_text_units_similarity_by_vectors_post()



\"Similarity\" admin task  POST params:     - project_id: int     - distance_type: str - see scipy.spatial.distance._METRICS     - similarity_threshold: int     - unit_type: str sentence|paragraph     - feature_source: \"vector\"     - create_reverse_relations: bool - create B-A relations     - use_tfidf: bool     - delete: bool

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import similarity_api
from openapi_client.model.project_text_units_similarity_by_vectors_form import ProjectTextUnitsSimilarityByVectorsForm
from openapi_client.model.similarity_post_object_response import SimilarityPOSTObjectResponse
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
configuration.api_key['AuthToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = similarity_api.SimilarityApi(api_client)
    project_text_units_similarity_by_vectors_form = ProjectTextUnitsSimilarityByVectorsForm(
        run_name="run_name_example",
        similarity_threshold=75,
        project=1,
        feature_source="vector",
        distance_type="cosine",
        item_id=1,
        create_reverse_relations=True,
        use_tfidf=True,
        delete=True,
        unit_type="sentence",
        document_id=1,
        location_start=1,
        location_end=1,
    ) # ProjectTextUnitsSimilarityByVectorsForm |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.similarity_project_text_units_similarity_by_vectors_post(project_text_units_similarity_by_vectors_form=project_text_units_similarity_by_vectors_form)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SimilarityApi->similarity_project_text_units_similarity_by_vectors_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_text_units_similarity_by_vectors_form** | [**ProjectTextUnitsSimilarityByVectorsForm**](ProjectTextUnitsSimilarityByVectorsForm.md)|  | [optional]

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
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} similarity_similarity_get()



\"Similarity\" admin task  POST params:     - search_similar_documents: bool     - search_similar_text_units: bool     - similarity_threshold: int     - use_idf: bool     - delete: bool     - project: bool

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import similarity_api
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
configuration.api_key['AuthToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = similarity_api.SimilarityApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_response = api_instance.similarity_similarity_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SimilarityApi->similarity_similarity_get: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

**{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**

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
> SimilarityPOSTObjectResponse similarity_similarity_post()



\"Similarity\" admin task  POST params:     - search_similar_documents: bool     - search_similar_text_units: bool     - similarity_threshold: int     - use_idf: bool     - delete: bool     - project: bool

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import similarity_api
from openapi_client.model.similarity_post_object_response import SimilarityPOSTObjectResponse
from openapi_client.model.similarity_form import SimilarityForm
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
configuration.api_key['AuthToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = similarity_api.SimilarityApi(api_client)
    similarity_form = SimilarityForm(
        run_name="run_name_example",
        search_similar_documents=True,
        search_similar_text_units=True,
        similarity_threshold=75,
        project="",
        use_idf=True,
        delete=True,
    ) # SimilarityForm |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.similarity_similarity_post(similarity_form=similarity_form)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SimilarityApi->similarity_similarity_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **similarity_form** | [**SimilarityForm**](SimilarityForm.md)|  | [optional]

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

# **similarity_text_unit_similarity_by_features_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} similarity_text_unit_similarity_by_features_get()



\"Similarity\" admin task  POST params:     - similarity_threshold: int     - use_tfidf: bool     - delete: bool     - project: int     - feature_source: list - list[date, definition, duration, court,       currency_name, currency_value, term, party, geoentity]     - unit_type: str sentence|paragraph     - distance_type: str - see scipy.spatial.distance._METRICS

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import similarity_api
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
configuration.api_key['AuthToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = similarity_api.SimilarityApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_response = api_instance.similarity_text_unit_similarity_by_features_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SimilarityApi->similarity_text_unit_similarity_by_features_get: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

**{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**

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

# **similarity_text_unit_similarity_by_features_post**
> SimilarityPOSTObjectResponse similarity_text_unit_similarity_by_features_post()



\"Similarity\" admin task  POST params:     - similarity_threshold: int     - use_tfidf: bool     - delete: bool     - project: int     - feature_source: list - list[date, definition, duration, court,       currency_name, currency_value, term, party, geoentity]     - unit_type: str sentence|paragraph     - distance_type: str - see scipy.spatial.distance._METRICS

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import similarity_api
from openapi_client.model.similarity_post_object_response import SimilarityPOSTObjectResponse
from openapi_client.model.text_unit_similarity_by_features_form import TextUnitSimilarityByFeaturesForm
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
configuration.api_key['AuthToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AuthToken'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = similarity_api.SimilarityApi(api_client)
    text_unit_similarity_by_features_form = TextUnitSimilarityByFeaturesForm(
        run_name="run_name_example",
        similarity_threshold=75,
        project=1,
        feature_source="term",
        distance_type="cosine",
        item_id=1,
        create_reverse_relations=True,
        use_tfidf=True,
        delete=True,
        unit_type="sentence",
    ) # TextUnitSimilarityByFeaturesForm |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.similarity_text_unit_similarity_by_features_post(text_unit_similarity_by_features_form=text_unit_similarity_by_features_form)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SimilarityApi->similarity_text_unit_similarity_by_features_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **text_unit_similarity_by_features_form** | [**TextUnitSimilarityByFeaturesForm**](TextUnitSimilarityByFeaturesForm.md)|  | [optional]

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

