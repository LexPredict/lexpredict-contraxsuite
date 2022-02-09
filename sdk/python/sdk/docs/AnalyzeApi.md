# openapi_client.AnalyzeApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**analyze_document_cluster_get**](AnalyzeApi.md#analyze_document_cluster_get) | **GET** /api/v1/analyze/document-cluster/ | 
[**analyze_document_cluster_id_get**](AnalyzeApi.md#analyze_document_cluster_id_get) | **GET** /api/v1/analyze/document-cluster/{id}/ | 
[**analyze_document_cluster_id_patch**](AnalyzeApi.md#analyze_document_cluster_id_patch) | **PATCH** /api/v1/analyze/document-cluster/{id}/ | 
[**analyze_document_cluster_id_put**](AnalyzeApi.md#analyze_document_cluster_id_put) | **PUT** /api/v1/analyze/document-cluster/{id}/ | 
[**analyze_document_similarity_list_get**](AnalyzeApi.md#analyze_document_similarity_list_get) | **GET** /api/v1/analyze/document-similarity/list/ | 
[**analyze_document_transformer_list_get**](AnalyzeApi.md#analyze_document_transformer_list_get) | **GET** /api/v1/analyze/document-transformer/list/ | 
[**analyze_ml_model_list_get**](AnalyzeApi.md#analyze_ml_model_list_get) | **GET** /api/v1/analyze/ml-model/list/ | 
[**analyze_party_similarity_list_get**](AnalyzeApi.md#analyze_party_similarity_list_get) | **GET** /api/v1/analyze/party-similarity/list/ | 
[**analyze_project_document_similarity_list_get**](AnalyzeApi.md#analyze_project_document_similarity_list_get) | **GET** /api/v1/analyze/project-document-similarity/list/ | 
[**analyze_project_text_unit_similarity_list_get**](AnalyzeApi.md#analyze_project_text_unit_similarity_list_get) | **GET** /api/v1/analyze/project-text-unit-similarity/list/ | 
[**analyze_project_text_unit_similarity_list_post**](AnalyzeApi.md#analyze_project_text_unit_similarity_list_post) | **POST** /api/v1/analyze/project-text-unit-similarity/list/ | 
[**analyze_similarity_runs_get**](AnalyzeApi.md#analyze_similarity_runs_get) | **GET** /api/v1/analyze/similarity-runs/ | 
[**analyze_similarity_runs_id_delete**](AnalyzeApi.md#analyze_similarity_runs_id_delete) | **DELETE** /api/v1/analyze/similarity-runs/{id}/ | 
[**analyze_similarity_runs_id_get**](AnalyzeApi.md#analyze_similarity_runs_id_get) | **GET** /api/v1/analyze/similarity-runs/{id}/ | 
[**analyze_text_unit_classifications_get**](AnalyzeApi.md#analyze_text_unit_classifications_get) | **GET** /api/v1/analyze/text-unit-classifications/ | 
[**analyze_text_unit_classifications_id_delete**](AnalyzeApi.md#analyze_text_unit_classifications_id_delete) | **DELETE** /api/v1/analyze/text-unit-classifications/{id}/ | 
[**analyze_text_unit_classifications_id_get**](AnalyzeApi.md#analyze_text_unit_classifications_id_get) | **GET** /api/v1/analyze/text-unit-classifications/{id}/ | 
[**analyze_text_unit_classifications_post**](AnalyzeApi.md#analyze_text_unit_classifications_post) | **POST** /api/v1/analyze/text-unit-classifications/ | 
[**analyze_text_unit_classifier_suggestions_get**](AnalyzeApi.md#analyze_text_unit_classifier_suggestions_get) | **GET** /api/v1/analyze/text-unit-classifier-suggestions/ | 
[**analyze_text_unit_classifier_suggestions_id_delete**](AnalyzeApi.md#analyze_text_unit_classifier_suggestions_id_delete) | **DELETE** /api/v1/analyze/text-unit-classifier-suggestions/{id}/ | 
[**analyze_text_unit_classifier_suggestions_id_get**](AnalyzeApi.md#analyze_text_unit_classifier_suggestions_id_get) | **GET** /api/v1/analyze/text-unit-classifier-suggestions/{id}/ | 
[**analyze_text_unit_classifiers_get**](AnalyzeApi.md#analyze_text_unit_classifiers_get) | **GET** /api/v1/analyze/text-unit-classifiers/ | 
[**analyze_text_unit_classifiers_id_delete**](AnalyzeApi.md#analyze_text_unit_classifiers_id_delete) | **DELETE** /api/v1/analyze/text-unit-classifiers/{id}/ | 
[**analyze_text_unit_classifiers_id_get**](AnalyzeApi.md#analyze_text_unit_classifiers_id_get) | **GET** /api/v1/analyze/text-unit-classifiers/{id}/ | 
[**analyze_text_unit_cluster_list_get**](AnalyzeApi.md#analyze_text_unit_cluster_list_get) | **GET** /api/v1/analyze/text-unit-cluster/list/ | 
[**analyze_text_unit_similarity_list_get**](AnalyzeApi.md#analyze_text_unit_similarity_list_get) | **GET** /api/v1/analyze/text-unit-similarity/list/ | 
[**analyze_text_unit_transformer_list_get**](AnalyzeApi.md#analyze_text_unit_transformer_list_get) | **GET** /api/v1/analyze/text-unit-transformer/list/ | 
[**analyze_typeahead_text_unit_classification_field_name_get**](AnalyzeApi.md#analyze_typeahead_text_unit_classification_field_name_get) | **GET** /api/v1/analyze/typeahead/text-unit-classification/{field_name}/ | 


# **analyze_document_cluster_get**
> [DocumentCluster] analyze_document_cluster_get()



Document Cluster List

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.document_cluster import DocumentCluster
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_document_cluster_get(jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_document_cluster_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**[DocumentCluster]**](DocumentCluster.md)

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

# **analyze_document_cluster_id_get**
> DocumentCluster analyze_document_cluster_id_get(id)



Retrieve Document Cluster

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.document_cluster import DocumentCluster
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    id = "id_example" # str | A unique integer value identifying this document cluster.
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.analyze_document_cluster_id_get(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_document_cluster_id_get: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_document_cluster_id_get(id, jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_document_cluster_id_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this document cluster. |
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**DocumentCluster**](DocumentCluster.md)

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

# **analyze_document_cluster_id_patch**
> DocumentClusterUpdate analyze_document_cluster_id_patch(id)



Partial Update Document Cluster (name)

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.document_cluster_update import DocumentClusterUpdate
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    id = "id_example" # str | A unique integer value identifying this document cluster.
    document_cluster_update = DocumentClusterUpdate(
        name="name_example",
    ) # DocumentClusterUpdate |  (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.analyze_document_cluster_id_patch(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_document_cluster_id_patch: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_document_cluster_id_patch(id, document_cluster_update=document_cluster_update)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_document_cluster_id_patch: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this document cluster. |
 **document_cluster_update** | [**DocumentClusterUpdate**](DocumentClusterUpdate.md)|  | [optional]

### Return type

[**DocumentClusterUpdate**](DocumentClusterUpdate.md)

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

# **analyze_document_cluster_id_put**
> DocumentClusterUpdate analyze_document_cluster_id_put(id)



Update Document Cluster (name)

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.document_cluster_update import DocumentClusterUpdate
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    id = "id_example" # str | A unique integer value identifying this document cluster.
    document_cluster_update = DocumentClusterUpdate(
        name="name_example",
    ) # DocumentClusterUpdate |  (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.analyze_document_cluster_id_put(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_document_cluster_id_put: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_document_cluster_id_put(id, document_cluster_update=document_cluster_update)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_document_cluster_id_put: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this document cluster. |
 **document_cluster_update** | [**DocumentClusterUpdate**](DocumentClusterUpdate.md)|  | [optional]

### Return type

[**DocumentClusterUpdate**](DocumentClusterUpdate.md)

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

# **analyze_document_similarity_list_get**
> [DocumentSimilarity] analyze_document_similarity_list_get()



Base Document Similarity List

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.document_similarity import DocumentSimilarity
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_document_similarity_list_get(jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_document_similarity_list_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**[DocumentSimilarity]**](DocumentSimilarity.md)

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

# **analyze_document_transformer_list_get**
> [Transformer] analyze_document_transformer_list_get()



MLModel List - document transformers only

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.transformer import Transformer
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_document_transformer_list_get(jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_document_transformer_list_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**[Transformer]**](Transformer.md)

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

# **analyze_ml_model_list_get**
> [MLModel] analyze_ml_model_list_get()



MLModel List

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.ml_model import MLModel
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_ml_model_list_get(jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_ml_model_list_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**[MLModel]**](MLModel.md)

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

# **analyze_party_similarity_list_get**
> [PartySimilarity] analyze_party_similarity_list_get()



Party Similarity List

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.party_similarity import PartySimilarity
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_party_similarity_list_get(jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_party_similarity_list_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**[PartySimilarity]**](PartySimilarity.md)

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

# **analyze_project_document_similarity_list_get**
> ProjectDocumentSimilarityResponse analyze_project_document_similarity_list_get()



Project Document Similarity List for ONE document

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.project_document_similarity_response import ProjectDocumentSimilarityResponse
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    text_max_length = 1 # int | document b text max length, 0 to get all text (optional)
    run_id = 1 # int | run id or document id required (optional)
    document_id = 1 # int | run id or document id required (optional)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_project_document_similarity_list_get(text_max_length=text_max_length, run_id=run_id, document_id=document_id, jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_project_document_similarity_list_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **text_max_length** | **int**| document b text max length, 0 to get all text | [optional]
 **run_id** | **int**| run id or document id required | [optional]
 **document_id** | **int**| run id or document id required | [optional]
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**ProjectDocumentSimilarityResponse**](ProjectDocumentSimilarityResponse.md)

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

# **analyze_project_text_unit_similarity_list_get**
> [ProjectTextUnitSimilarity] analyze_project_text_unit_similarity_list_get()



Project Text Unit Similarity List for ONE text unit

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.project_text_unit_similarity import ProjectTextUnitSimilarity
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)
    text_max_length = 1 # int | text unit b text max length, 0 to get all text (optional)
    run_id = 1 # int | run id or text unit id required (optional)
    last_run = True # bool | run id or last_run or text unit id required (optional)
    text_unit_id = 1 # int | run id or text unit id required (optional)
    document_id = 1 # int | document ID (optional)
    location_start = 1 # int | start of chosen text block in a Document (optional)
    location_end = 1 # int | end of chosen text block in a Document (optional)
    selection = [
        {},
    ] # [{str: (bool, date, datetime, dict, float, int, list, str, none_type)}] | selection coordinates (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_project_text_unit_similarity_list_get(jq_filters=jq_filters, text_max_length=text_max_length, run_id=run_id, last_run=last_run, text_unit_id=text_unit_id, document_id=document_id, location_start=location_start, location_end=location_end, selection=selection)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_project_text_unit_similarity_list_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]
 **text_max_length** | **int**| text unit b text max length, 0 to get all text | [optional]
 **run_id** | **int**| run id or text unit id required | [optional]
 **last_run** | **bool**| run id or last_run or text unit id required | [optional]
 **text_unit_id** | **int**| run id or text unit id required | [optional]
 **document_id** | **int**| document ID | [optional]
 **location_start** | **int**| start of chosen text block in a Document | [optional]
 **location_end** | **int**| end of chosen text block in a Document | [optional]
 **selection** | [**[{str: (bool, date, datetime, dict, float, int, list, str, none_type)}]**]({str: (bool, date, datetime, dict, float, int, list, str, none_type)}.md)| selection coordinates | [optional]

### Return type

[**[ProjectTextUnitSimilarity]**](ProjectTextUnitSimilarity.md)

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

# **analyze_project_text_unit_similarity_list_post**
> ProjectTextUnitSimilarity analyze_project_text_unit_similarity_list_post()



Project Text Unit Similarity List for ONE text unit

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.similar_project_text_units_request import SimilarProjectTextUnitsRequest
from openapi_client.model.project_text_unit_similarity import ProjectTextUnitSimilarity
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    similar_project_text_units_request = SimilarProjectTextUnitsRequest(
        text_max_length=1,
        run_id=1,
        last_run=True,
        text_unit_id=1,
        document_id=1,
        location_start=1,
        location_end=1,
        selection=[
            {},
        ],
    ) # SimilarProjectTextUnitsRequest |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_project_text_unit_similarity_list_post(similar_project_text_units_request=similar_project_text_units_request)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_project_text_unit_similarity_list_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **similar_project_text_units_request** | [**SimilarProjectTextUnitsRequest**](SimilarProjectTextUnitsRequest.md)|  | [optional]

### Return type

[**ProjectTextUnitSimilarity**](ProjectTextUnitSimilarity.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **analyze_similarity_runs_get**
> [SimilarityRun] analyze_similarity_runs_get()



list Similarity Run objects

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.similarity_run import SimilarityRun
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    unit_source = "unit_source_example" # str | document / text_unit (optional)
    project_id = 1 # int | Project ID (optional)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_similarity_runs_get(unit_source=unit_source, project_id=project_id, jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_similarity_runs_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **unit_source** | **str**| document / text_unit | [optional]
 **project_id** | **int**| Project ID | [optional]
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**[SimilarityRun]**](SimilarityRun.md)

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

# **analyze_similarity_runs_id_delete**
> analyze_similarity_runs_id_delete(id)



delete Similarity Run object

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    id = "id_example" # str | A unique integer value identifying this similarity run.
    unit_source = "unit_source_example" # str | document / text_unit (optional)
    project_id = 1 # int | Project ID (optional)

    # example passing only required values which don't have defaults set
    try:
        api_instance.analyze_similarity_runs_id_delete(id)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_similarity_runs_id_delete: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_instance.analyze_similarity_runs_id_delete(id, unit_source=unit_source, project_id=project_id)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_similarity_runs_id_delete: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this similarity run. |
 **unit_source** | **str**| document / text_unit | [optional]
 **project_id** | **int**| Project ID | [optional]

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
**204** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **analyze_similarity_runs_id_get**
> SimilarityRun analyze_similarity_runs_id_get(id)



get Similarity Run object

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.similarity_run import SimilarityRun
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    id = "id_example" # str | A unique integer value identifying this similarity run.
    unit_source = "unit_source_example" # str | document / text_unit (optional)
    project_id = 1 # int | Project ID (optional)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.analyze_similarity_runs_id_get(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_similarity_runs_id_get: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_similarity_runs_id_get(id, unit_source=unit_source, project_id=project_id, jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_similarity_runs_id_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this similarity run. |
 **unit_source** | **str**| document / text_unit | [optional]
 **project_id** | **int**| Project ID | [optional]
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**SimilarityRun**](SimilarityRun.md)

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

# **analyze_text_unit_classifications_get**
> [TextUnitClassification] analyze_text_unit_classifications_get()



Text Unit Classification List

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.text_unit_classification import TextUnitClassification
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_text_unit_classifications_get(jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_text_unit_classifications_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**[TextUnitClassification]**](TextUnitClassification.md)

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

# **analyze_text_unit_classifications_id_delete**
> analyze_text_unit_classifications_id_delete(id)



Delete Text Unit Classification

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    id = "id_example" # str | A unique integer value identifying this text unit classification.

    # example passing only required values which don't have defaults set
    try:
        api_instance.analyze_text_unit_classifications_id_delete(id)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_text_unit_classifications_id_delete: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this text unit classification. |

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
**204** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **analyze_text_unit_classifications_id_get**
> TextUnitClassification analyze_text_unit_classifications_id_get(id)



Retrieve Text Unit Classification

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.text_unit_classification import TextUnitClassification
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    id = "id_example" # str | A unique integer value identifying this text unit classification.
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.analyze_text_unit_classifications_id_get(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_text_unit_classifications_id_get: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_text_unit_classifications_id_get(id, jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_text_unit_classifications_id_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this text unit classification. |
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**TextUnitClassification**](TextUnitClassification.md)

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

# **analyze_text_unit_classifications_post**
> TextUnitClassificationCreate analyze_text_unit_classifications_post()



Create Text Unit Classification

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.text_unit_classification_create import TextUnitClassificationCreate
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    text_unit_classification_create = TextUnitClassificationCreate(
        class_name="class_name_example",
        class_value="class_value_example",
        text_unit_id=1,
    ) # TextUnitClassificationCreate |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_text_unit_classifications_post(text_unit_classification_create=text_unit_classification_create)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_text_unit_classifications_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **text_unit_classification_create** | [**TextUnitClassificationCreate**](TextUnitClassificationCreate.md)|  | [optional]

### Return type

[**TextUnitClassificationCreate**](TextUnitClassificationCreate.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **analyze_text_unit_classifier_suggestions_get**
> [TextUnitClassifierSuggestion] analyze_text_unit_classifier_suggestions_get()



Text Unit Classifier Suggestion List

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.text_unit_classifier_suggestion import TextUnitClassifierSuggestion
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_text_unit_classifier_suggestions_get(jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_text_unit_classifier_suggestions_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**[TextUnitClassifierSuggestion]**](TextUnitClassifierSuggestion.md)

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

# **analyze_text_unit_classifier_suggestions_id_delete**
> analyze_text_unit_classifier_suggestions_id_delete(id)



Delete Text Unit Classifier Suggestion

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    id = "id_example" # str | A unique integer value identifying this text unit classifier suggestion.

    # example passing only required values which don't have defaults set
    try:
        api_instance.analyze_text_unit_classifier_suggestions_id_delete(id)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_text_unit_classifier_suggestions_id_delete: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this text unit classifier suggestion. |

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
**204** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **analyze_text_unit_classifier_suggestions_id_get**
> TextUnitClassifierSuggestion analyze_text_unit_classifier_suggestions_id_get(id)



### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.text_unit_classifier_suggestion import TextUnitClassifierSuggestion
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    id = "id_example" # str | A unique integer value identifying this text unit classifier suggestion.
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.analyze_text_unit_classifier_suggestions_id_get(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_text_unit_classifier_suggestions_id_get: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_text_unit_classifier_suggestions_id_get(id, jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_text_unit_classifier_suggestions_id_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this text unit classifier suggestion. |
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**TextUnitClassifierSuggestion**](TextUnitClassifierSuggestion.md)

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

# **analyze_text_unit_classifiers_get**
> [TextUnitClassifier] analyze_text_unit_classifiers_get()



Text Unit Classifier List

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.text_unit_classifier import TextUnitClassifier
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_text_unit_classifiers_get(jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_text_unit_classifiers_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**[TextUnitClassifier]**](TextUnitClassifier.md)

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

# **analyze_text_unit_classifiers_id_delete**
> analyze_text_unit_classifiers_id_delete(id)



Delete Text Unit Classifier

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    id = "id_example" # str | A unique integer value identifying this text unit classifier.

    # example passing only required values which don't have defaults set
    try:
        api_instance.analyze_text_unit_classifiers_id_delete(id)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_text_unit_classifiers_id_delete: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this text unit classifier. |

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
**204** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **analyze_text_unit_classifiers_id_get**
> TextUnitClassifier analyze_text_unit_classifiers_id_get(id)



### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.text_unit_classifier import TextUnitClassifier
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    id = "id_example" # str | A unique integer value identifying this text unit classifier.
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.analyze_text_unit_classifiers_id_get(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_text_unit_classifiers_id_get: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_text_unit_classifiers_id_get(id, jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_text_unit_classifiers_id_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this text unit classifier. |
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**TextUnitClassifier**](TextUnitClassifier.md)

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

# **analyze_text_unit_cluster_list_get**
> [TextUnitCluster] analyze_text_unit_cluster_list_get()



Text Unit Cluster List

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.text_unit_cluster import TextUnitCluster
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_text_unit_cluster_list_get(jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_text_unit_cluster_list_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**[TextUnitCluster]**](TextUnitCluster.md)

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

# **analyze_text_unit_similarity_list_get**
> [TextUnitSimilarity] analyze_text_unit_similarity_list_get()



Base Text Unit Similarity List

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.text_unit_similarity import TextUnitSimilarity
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_text_unit_similarity_list_get(jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_text_unit_similarity_list_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**[TextUnitSimilarity]**](TextUnitSimilarity.md)

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

# **analyze_text_unit_transformer_list_get**
> [Transformer] analyze_text_unit_transformer_list_get()



MLModel List - text unit transformers only

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.transformer import Transformer
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.analyze_text_unit_transformer_list_get(jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_text_unit_transformer_list_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**[Transformer]**](Transformer.md)

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

# **analyze_typeahead_text_unit_classification_field_name_get**
> Typeahead analyze_typeahead_text_unit_classification_field_name_get(field_name, q)



Typeahead TextUnitClassification      Kwargs: field_name: [class_name, class_value]     GET params:       - q: str

### Example

* Api Key Authentication (AuthToken):

```python
import time
import openapi_client
from openapi_client.api import analyze_api
from openapi_client.model.typeahead import Typeahead
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
    api_instance = analyze_api.AnalyzeApi(api_client)
    field_name = "field_name_example" # str | 
    q = "q_example" # str | Typeahead string

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.analyze_typeahead_text_unit_classification_field_name_get(field_name, q)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AnalyzeApi->analyze_typeahead_text_unit_classification_field_name_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **field_name** | **str**|  |
 **q** | **str**| Typeahead string |

### Return type

[**Typeahead**](Typeahead.md)

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

