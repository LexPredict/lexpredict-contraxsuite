# openapi_client.ProjectApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**project_project_clustering_get**](ProjectApi.md#project_project_clustering_get) | **GET** /api/v1/project/project-clustering/ | 
[**project_project_clustering_id_get**](ProjectApi.md#project_project_clustering_id_get) | **GET** /api/v1/project/project-clustering/{id}/ | 
[**project_projects_get**](ProjectApi.md#project_projects_get) | **GET** /api/v1/project/projects/ | 
[**project_projects_id_annotations_assignees_get**](ProjectApi.md#project_projects_id_annotations_assignees_get) | **GET** /api/v1/project/projects/{id}/annotations_assignees/ | 
[**project_projects_id_assign_annotations_post**](ProjectApi.md#project_projects_id_assign_annotations_post) | **POST** /api/v1/project/projects/{id}/assign_annotations/ | 
[**project_projects_id_assign_document_post**](ProjectApi.md#project_projects_id_assign_document_post) | **POST** /api/v1/project/projects/{id}/assign_document/ | 
[**project_projects_id_assign_documents_post**](ProjectApi.md#project_projects_id_assign_documents_post) | **POST** /api/v1/project/projects/{id}/assign_documents/ | 
[**project_projects_id_assignees_get**](ProjectApi.md#project_projects_id_assignees_get) | **GET** /api/v1/project/projects/{id}/assignees/ | 
[**project_projects_id_cleanup_post**](ProjectApi.md#project_projects_id_cleanup_post) | **POST** /api/v1/project/projects/{id}/cleanup/ | 
[**project_projects_id_cluster_post**](ProjectApi.md#project_projects_id_cluster_post) | **POST** /api/v1/project/projects/{id}/cluster/ | 
[**project_projects_id_clustering_status_get**](ProjectApi.md#project_projects_id_clustering_status_get) | **GET** /api/v1/project/projects/{id}/clustering-status/ | 
[**project_projects_id_delete**](ProjectApi.md#project_projects_id_delete) | **DELETE** /api/v1/project/projects/{id}/ | 
[**project_projects_id_detect_field_values_post**](ProjectApi.md#project_projects_id_detect_field_values_post) | **POST** /api/v1/project/projects/{id}/detect_field_values/ | 
[**project_projects_id_get**](ProjectApi.md#project_projects_id_get) | **GET** /api/v1/project/projects/{id}/ | 
[**project_projects_id_make_searchable_pdf_post**](ProjectApi.md#project_projects_id_make_searchable_pdf_post) | **POST** /api/v1/project/projects/{id}/make-searchable-pdf/ | 
[**project_projects_id_mark_delete_post**](ProjectApi.md#project_projects_id_mark_delete_post) | **POST** /api/v1/project/projects/{id}/mark_delete/ | 
[**project_projects_id_patch**](ProjectApi.md#project_projects_id_patch) | **PATCH** /api/v1/project/projects/{id}/ | 
[**project_projects_id_progress_get**](ProjectApi.md#project_projects_id_progress_get) | **GET** /api/v1/project/projects/{id}/progress/ | 
[**project_projects_id_put**](ProjectApi.md#project_projects_id_put) | **PUT** /api/v1/project/projects/{id}/ | 
[**project_projects_id_send_clusters_to_project_post**](ProjectApi.md#project_projects_id_send_clusters_to_project_post) | **POST** /api/v1/project/projects/{id}/send-clusters-to-project/ | 
[**project_projects_id_set_annotation_status_post**](ProjectApi.md#project_projects_id_set_annotation_status_post) | **POST** /api/v1/project/projects/{id}/set_annotation_status/ | 
[**project_projects_id_set_status_post**](ProjectApi.md#project_projects_id_set_status_post) | **POST** /api/v1/project/projects/{id}/set_status/ | 
[**project_projects_id_unmark_delete_post**](ProjectApi.md#project_projects_id_unmark_delete_post) | **POST** /api/v1/project/projects/{id}/unmark_delete/ | 
[**project_projects_post**](ProjectApi.md#project_projects_post) | **POST** /api/v1/project/projects/ | 
[**project_projects_project_stats_get**](ProjectApi.md#project_projects_project_stats_get) | **GET** /api/v1/project/projects/project_stats/ | 
[**project_projects_recent_get**](ProjectApi.md#project_projects_recent_get) | **GET** /api/v1/project/projects/recent/ | 
[**project_projects_select_projects_post**](ProjectApi.md#project_projects_select_projects_post) | **POST** /api/v1/project/projects/select_projects/ | 
[**project_task_queues_get**](ProjectApi.md#project_task_queues_get) | **GET** /api/v1/project/task-queues/ | 
[**project_task_queues_id_delete**](ProjectApi.md#project_task_queues_id_delete) | **DELETE** /api/v1/project/task-queues/{id}/ | 
[**project_task_queues_id_get**](ProjectApi.md#project_task_queues_id_get) | **GET** /api/v1/project/task-queues/{id}/ | 
[**project_task_queues_id_patch**](ProjectApi.md#project_task_queues_id_patch) | **PATCH** /api/v1/project/task-queues/{id}/ | 
[**project_task_queues_id_put**](ProjectApi.md#project_task_queues_id_put) | **PUT** /api/v1/project/task-queues/{id}/ | 
[**project_task_queues_post**](ProjectApi.md#project_task_queues_post) | **POST** /api/v1/project/task-queues/ | 
[**project_upload_session_get**](ProjectApi.md#project_upload_session_get) | **GET** /api/v1/project/upload-session/ | 
[**project_upload_session_post**](ProjectApi.md#project_upload_session_post) | **POST** /api/v1/project/upload-session/ | 
[**project_upload_session_status_get**](ProjectApi.md#project_upload_session_status_get) | **GET** /api/v1/project/upload-session/status/ | 
[**project_upload_session_uid_batch_upload_post**](ProjectApi.md#project_upload_session_uid_batch_upload_post) | **POST** /api/v1/project/upload-session/{uid}/_batch_upload/ | 
[**project_upload_session_uid_batch_upload_post_0**](ProjectApi.md#project_upload_session_uid_batch_upload_post_0) | **POST** /api/v1/project/upload-session/{uid}/batch_upload/ | 
[**project_upload_session_uid_cancel_delete**](ProjectApi.md#project_upload_session_uid_cancel_delete) | **DELETE** /api/v1/project/upload-session/{uid}/cancel/ | 
[**project_upload_session_uid_delete**](ProjectApi.md#project_upload_session_uid_delete) | **DELETE** /api/v1/project/upload-session/{uid}/ | 
[**project_upload_session_uid_delete_file_delete**](ProjectApi.md#project_upload_session_uid_delete_file_delete) | **DELETE** /api/v1/project/upload-session/{uid}/delete-file/ | 
[**project_upload_session_uid_files_post**](ProjectApi.md#project_upload_session_uid_files_post) | **POST** /api/v1/project/upload-session/{uid}/files/ | 
[**project_upload_session_uid_get**](ProjectApi.md#project_upload_session_uid_get) | **GET** /api/v1/project/upload-session/{uid}/ | 
[**project_upload_session_uid_progress_get**](ProjectApi.md#project_upload_session_uid_progress_get) | **GET** /api/v1/project/upload-session/{uid}/progress/ | 
[**project_upload_session_uid_upload_post**](ProjectApi.md#project_upload_session_uid_upload_post) | **POST** /api/v1/project/upload-session/{uid}/upload/ | 


# **project_project_clustering_get**
> list[ProjectClustering] project_project_clustering_get(jq_filters=jq_filters)



ProjectCluster List

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
    api_instance = openapi_client.ProjectApi(api_client)
    jq_filters = {'key': 'jq_filters_example'} # dict(str, str) | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    try:
        api_response = api_instance.project_project_clustering_get(jq_filters=jq_filters)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_project_clustering_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jq_filters** | [**dict(str, str)**](str.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

### Return type

[**list[ProjectClustering]**](ProjectClustering.md)

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

# **project_project_clustering_id_get**
> ProjectClustering project_project_clustering_id_get(id, jq_filters=jq_filters)



ProjectCluster Details

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this project clustering.
jq_filters = {'key': 'jq_filters_example'} # dict(str, str) | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    try:
        api_response = api_instance.project_project_clustering_id_get(id, jq_filters=jq_filters)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_project_clustering_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this project clustering. | 
 **jq_filters** | [**dict(str, str)**](str.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

### Return type

[**ProjectClustering**](ProjectClustering.md)

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

# **project_projects_get**
> list[ProjectList] project_projects_get(jq_filters=jq_filters)



Project List

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
    api_instance = openapi_client.ProjectApi(api_client)
    jq_filters = {'key': 'jq_filters_example'} # dict(str, str) | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    try:
        api_response = api_instance.project_projects_get(jq_filters=jq_filters)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jq_filters** | [**dict(str, str)**](str.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

### Return type

[**list[ProjectList]**](ProjectList.md)

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

# **project_projects_id_annotations_assignees_get**
> list[ProjectAnnotationsAssigneesResponse] project_projects_id_annotations_assignees_get(id)



Get assignees data for FieldAnnotations

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this project.

    try:
        api_response = api_instance.project_projects_id_annotations_assignees_get(id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_id_annotations_assignees_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this project. | 

### Return type

[**list[ProjectAnnotationsAssigneesResponse]**](ProjectAnnotationsAssigneesResponse.md)

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

# **project_projects_id_assign_annotations_post**
> CountSuccessResponse project_projects_id_assign_annotations_post(id, assign_project_annotations_request=assign_project_annotations_request)



Bulk assign batch of annotations to a review team member      Params:         annotation_ids: list[int]         all: any value - update all annotations if any value         no_annotation_ids: list[int] - exclude those annotations from action (if \"all\" is set)         assignee_id: int     Returns:         int (number of reassigned annotations)

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this project.
assign_project_annotations_request = openapi_client.AssignProjectAnnotationsRequest() # AssignProjectAnnotationsRequest |  (optional)

    try:
        api_response = api_instance.project_projects_id_assign_annotations_post(id, assign_project_annotations_request=assign_project_annotations_request)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_id_assign_annotations_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this project. | 
 **assign_project_annotations_request** | [**AssignProjectAnnotationsRequest**](AssignProjectAnnotationsRequest.md)|  | [optional] 

### Return type

[**CountSuccessResponse**](CountSuccessResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **project_projects_id_assign_document_post**
> CountSuccessResponse project_projects_id_assign_document_post(id, assign_project_document_request=assign_project_document_request)



Bulk assign batch of documents to a review team member      Params:         document_id: int         assignee_id: int     Returns:         bool (number of reassigned documents)

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this project.
assign_project_document_request = openapi_client.AssignProjectDocumentRequest() # AssignProjectDocumentRequest |  (optional)

    try:
        api_response = api_instance.project_projects_id_assign_document_post(id, assign_project_document_request=assign_project_document_request)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_id_assign_document_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this project. | 
 **assign_project_document_request** | [**AssignProjectDocumentRequest**](AssignProjectDocumentRequest.md)|  | [optional] 

### Return type

[**CountSuccessResponse**](CountSuccessResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **project_projects_id_assign_documents_post**
> CountSuccessResponse project_projects_id_assign_documents_post(id, assign_project_documents_request=assign_project_documents_request)



Bulk assign batch of documents to a review team member      Params:         document_ids: list[int]         all: any value - update all documents if any value         no_document_ids: list[int] - exclude those docs from action (if \"all\" is set)         assignee_id: int     Returns:         int (number of reassigned documents)

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this project.
assign_project_documents_request = openapi_client.AssignProjectDocumentsRequest() # AssignProjectDocumentsRequest |  (optional)

    try:
        api_response = api_instance.project_projects_id_assign_documents_post(id, assign_project_documents_request=assign_project_documents_request)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_id_assign_documents_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this project. | 
 **assign_project_documents_request** | [**AssignProjectDocumentsRequest**](AssignProjectDocumentsRequest.md)|  | [optional] 

### Return type

[**CountSuccessResponse**](CountSuccessResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **project_projects_id_assignees_get**
> list[ProjectDocumentsAssigneesResponse] project_projects_id_assignees_get(id)



Get assignees data

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this project.

    try:
        api_response = api_instance.project_projects_id_assignees_get(id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_id_assignees_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this project. | 

### Return type

[**list[ProjectDocumentsAssigneesResponse]**](ProjectDocumentsAssigneesResponse.md)

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

# **project_projects_id_cleanup_post**
> str project_projects_id_cleanup_post(id, cleanup_project_request=cleanup_project_request)



Clean project (Generic Contract Type project)

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this project.
cleanup_project_request = openapi_client.CleanupProjectRequest() # CleanupProjectRequest |  (optional)

    try:
        api_response = api_instance.project_projects_id_cleanup_post(id, cleanup_project_request=cleanup_project_request)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_id_cleanup_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this project. | 
 **cleanup_project_request** | [**CleanupProjectRequest**](CleanupProjectRequest.md)|  | [optional] 

### Return type

**str**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **project_projects_id_cluster_post**
> ClusterProjectResponse project_projects_id_cluster_post(id, cluster_project_request=cluster_project_request)



Cluster Project Documents      Params:         - method: str[KMeans, MiniBatchKMeans, Birch, DBSCAN]         - cluster_by: str[term, date, text, definition, duration, party,                           geoentity, currency_name, currency_value]         - n_clusters: int         - force: bool (optional) - force clustering if uncompleted tasks exist

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this project.
cluster_project_request = openapi_client.ClusterProjectRequest() # ClusterProjectRequest |  (optional)

    try:
        api_response = api_instance.project_projects_id_cluster_post(id, cluster_project_request=cluster_project_request)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_id_cluster_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this project. | 
 **cluster_project_request** | [**ClusterProjectRequest**](ClusterProjectRequest.md)|  | [optional] 

### Return type

[**ClusterProjectResponse**](ClusterProjectResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |
**400** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **project_projects_id_clustering_status_get**
> ProjectClusteringStatusResponse project_projects_id_clustering_status_get(id, project_clustering_id=project_clustering_id)



Last Clustering task status/data      Params:         - project_clustering_id: int (optional) - return last if not provided

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this project.
project_clustering_id = 56 # int | Get by project_clustering_id (optional)

    try:
        api_response = api_instance.project_projects_id_clustering_status_get(id, project_clustering_id=project_clustering_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_id_clustering_status_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this project. | 
 **project_clustering_id** | **int**| Get by project_clustering_id | [optional] 

### Return type

[**ProjectClusteringStatusResponse**](ProjectClusteringStatusResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **project_projects_id_delete**
> project_projects_id_delete(id)



Delete Project

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this project.

    try:
        api_instance.project_projects_id_delete(id)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_id_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this project. | 

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

# **project_projects_id_detect_field_values_post**
> TaskIdResponse project_projects_id_detect_field_values_post(id, detect_project_field_values_request=detect_project_field_values_request)



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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this project.
detect_project_field_values_request = openapi_client.DetectProjectFieldValuesRequest() # DetectProjectFieldValuesRequest |  (optional)

    try:
        api_response = api_instance.project_projects_id_detect_field_values_post(id, detect_project_field_values_request=detect_project_field_values_request)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_id_detect_field_values_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this project. | 
 **detect_project_field_values_request** | [**DetectProjectFieldValuesRequest**](DetectProjectFieldValuesRequest.md)|  | [optional] 

### Return type

[**TaskIdResponse**](TaskIdResponse.md)

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

# **project_projects_id_get**
> ProjectDetail project_projects_id_get(id, jq_filters=jq_filters)



Retrieve Project

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this project.
jq_filters = {'key': 'jq_filters_example'} # dict(str, str) | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    try:
        api_response = api_instance.project_projects_id_get(id, jq_filters=jq_filters)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this project. | 
 **jq_filters** | [**dict(str, str)**](str.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

### Return type

[**ProjectDetail**](ProjectDetail.md)

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

# **project_projects_id_make_searchable_pdf_post**
> TaskIdResponse project_projects_id_make_searchable_pdf_post(id, make_searchable_pdf_request=make_searchable_pdf_request)



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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this project.
make_searchable_pdf_request = openapi_client.MakeSearchablePDFRequest() # MakeSearchablePDFRequest |  (optional)

    try:
        api_response = api_instance.project_projects_id_make_searchable_pdf_post(id, make_searchable_pdf_request=make_searchable_pdf_request)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_id_make_searchable_pdf_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this project. | 
 **make_searchable_pdf_request** | [**MakeSearchablePDFRequest**](MakeSearchablePDFRequest.md)|  | [optional] 

### Return type

[**TaskIdResponse**](TaskIdResponse.md)

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

# **project_projects_id_mark_delete_post**
> MarkUnmarkForDeleteProjectsReponse project_projects_id_mark_delete_post(id, mark_unmark_for_delete_projects_request=mark_unmark_for_delete_projects_request)



Method marks the whole project (remove_all=True) / the project's documents (remove_all=False) for deleting. These marked documents (and the project) will become hidden in API. Documents, listed in excluded_ids list, will not be marked for deleting.      Params:         - all: bool - mark all filtered by a user documents         - remove_all: bool - mark project+documents         - exclude_document_ids: list[int]

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this project.
mark_unmark_for_delete_projects_request = openapi_client.MarkUnmarkForDeleteProjectsRequest() # MarkUnmarkForDeleteProjectsRequest |  (optional)

    try:
        api_response = api_instance.project_projects_id_mark_delete_post(id, mark_unmark_for_delete_projects_request=mark_unmark_for_delete_projects_request)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_id_mark_delete_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this project. | 
 **mark_unmark_for_delete_projects_request** | [**MarkUnmarkForDeleteProjectsRequest**](MarkUnmarkForDeleteProjectsRequest.md)|  | [optional] 

### Return type

[**MarkUnmarkForDeleteProjectsReponse**](MarkUnmarkForDeleteProjectsReponse.md)

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

# **project_projects_id_patch**
> ProjectUpdate project_projects_id_patch(id, project_update=project_update)



Partial Update Project

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this project.
project_update = openapi_client.ProjectUpdate() # ProjectUpdate |  (optional)

    try:
        api_response = api_instance.project_projects_id_patch(id, project_update=project_update)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_id_patch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this project. | 
 **project_update** | [**ProjectUpdate**](ProjectUpdate.md)|  | [optional] 

### Return type

[**ProjectUpdate**](ProjectUpdate.md)

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

# **project_projects_id_progress_get**
> ProjectProgressResponse project_projects_id_progress_get(id)



Get current progress of all project sessions / clusterings

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this project.

    try:
        api_response = api_instance.project_projects_id_progress_get(id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_id_progress_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this project. | 

### Return type

[**ProjectProgressResponse**](ProjectProgressResponse.md)

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

# **project_projects_id_put**
> ProjectUpdate project_projects_id_put(id, project_update=project_update)



Update Project

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this project.
project_update = openapi_client.ProjectUpdate() # ProjectUpdate |  (optional)

    try:
        api_response = api_instance.project_projects_id_put(id, project_update=project_update)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_id_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this project. | 
 **project_update** | [**ProjectUpdate**](ProjectUpdate.md)|  | [optional] 

### Return type

[**ProjectUpdate**](ProjectUpdate.md)

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

# **project_projects_id_send_clusters_to_project_post**
> str project_projects_id_send_clusters_to_project_post(id, send_cluster_to_project_request=send_cluster_to_project_request)



Send clusters to another Project      Params:         - cluster_ids: list[int]         - project_id: int

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this project.
send_cluster_to_project_request = openapi_client.SendClusterToProjectRequest() # SendClusterToProjectRequest |  (optional)

    try:
        api_response = api_instance.project_projects_id_send_clusters_to_project_post(id, send_cluster_to_project_request=send_cluster_to_project_request)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_id_send_clusters_to_project_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this project. | 
 **send_cluster_to_project_request** | [**SendClusterToProjectRequest**](SendClusterToProjectRequest.md)|  | [optional] 

### Return type

**str**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |
**200** |  |  -  |
**400** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **project_projects_id_set_annotation_status_post**
> OneOfCountSuccessResponseSetProjectAnnotationsStatusAsyncResponse project_projects_id_set_annotation_status_post(id, set_project_annotations_status_request=set_project_annotations_status_request)



Bulk set status for batch of annotations      Params:         document_ids: list[int]         all: any value - update all annotations if any value         no_annotation_ids: list[int] - exclude those annotations from action (if \"all\" is set)         status_id: int - field annotation status id         run_mode: str - 'sync', 'background', 'smart'     Returns:         int (number of reassigned annotations)

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this project.
set_project_annotations_status_request = openapi_client.SetProjectAnnotationsStatusRequest() # SetProjectAnnotationsStatusRequest |  (optional)

    try:
        api_response = api_instance.project_projects_id_set_annotation_status_post(id, set_project_annotations_status_request=set_project_annotations_status_request)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_id_set_annotation_status_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this project. | 
 **set_project_annotations_status_request** | [**SetProjectAnnotationsStatusRequest**](SetProjectAnnotationsStatusRequest.md)|  | [optional] 

### Return type

[**OneOfCountSuccessResponseSetProjectAnnotationsStatusAsyncResponse**](OneOfCountSuccessResponseSetProjectAnnotationsStatusAsyncResponse.md)

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

# **project_projects_id_set_status_post**
> CountSuccessResponse project_projects_id_set_status_post(id, set_project_documents_status_request=set_project_documents_status_request)



Bulk set status for batch of documents      Params:         document_ids: list[int]         no_document_ids: list[int] - exclude those docs from action (if \"all\" is set)         all: any value - update all documents if any value         status_id: int     Returns:         int (number of reassigned documents)

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this project.
set_project_documents_status_request = openapi_client.SetProjectDocumentsStatusRequest() # SetProjectDocumentsStatusRequest |  (optional)

    try:
        api_response = api_instance.project_projects_id_set_status_post(id, set_project_documents_status_request=set_project_documents_status_request)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_id_set_status_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this project. | 
 **set_project_documents_status_request** | [**SetProjectDocumentsStatusRequest**](SetProjectDocumentsStatusRequest.md)|  | [optional] 

### Return type

[**CountSuccessResponse**](CountSuccessResponse.md)

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

# **project_projects_id_unmark_delete_post**
> MarkUnmarkForDeleteProjectsReponse project_projects_id_unmark_delete_post(id, mark_unmark_for_delete_projects_request=mark_unmark_for_delete_projects_request)



Method removes soft delete sign from project only (remove_all=False) or from the project and the project's documents (remove_all=True)     Body params:         - all: bool - unmark all filtered by a user documents         - remove_all: bool - unmark project+documents         - exclude_document_ids: List[int]

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this project.
mark_unmark_for_delete_projects_request = openapi_client.MarkUnmarkForDeleteProjectsRequest() # MarkUnmarkForDeleteProjectsRequest |  (optional)

    try:
        api_response = api_instance.project_projects_id_unmark_delete_post(id, mark_unmark_for_delete_projects_request=mark_unmark_for_delete_projects_request)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_id_unmark_delete_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this project. | 
 **mark_unmark_for_delete_projects_request** | [**MarkUnmarkForDeleteProjectsRequest**](MarkUnmarkForDeleteProjectsRequest.md)|  | [optional] 

### Return type

[**MarkUnmarkForDeleteProjectsReponse**](MarkUnmarkForDeleteProjectsReponse.md)

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

# **project_projects_post**
> ProjectCreate project_projects_post(project_create=project_create)



Create Project

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
    api_instance = openapi_client.ProjectApi(api_client)
    project_create = openapi_client.ProjectCreate() # ProjectCreate |  (optional)

    try:
        api_response = api_instance.project_projects_post(project_create=project_create)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_create** | [**ProjectCreate**](ProjectCreate.md)|  | [optional] 

### Return type

[**ProjectCreate**](ProjectCreate.md)

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

# **project_projects_project_stats_get**
> list[ProjectStats] project_projects_project_stats_get(project_ids=project_ids)



Get project stats across all projects see related code in get_queryset() and serializer

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
    api_instance = openapi_client.ProjectApi(api_client)
    project_ids = 'project_ids_example' # str | Project ids separated by commas (optional)

    try:
        api_response = api_instance.project_projects_project_stats_get(project_ids=project_ids)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_project_stats_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_ids** | **str**| Project ids separated by commas | [optional] 

### Return type

[**list[ProjectStats]**](ProjectStats.md)

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

# **project_projects_recent_get**
> list[dict(str, object)] project_projects_recent_get(n=n)



Get recent N projects      Params:         n: int - default is 5

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
    api_instance = openapi_client.ProjectApi(api_client)
    n = 56 # int | Max rows number (optional)

    try:
        api_response = api_instance.project_projects_recent_get(n=n)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_recent_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **n** | **int**| Max rows number | [optional] 

### Return type

**list[dict(str, object)]**

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

# **project_projects_select_projects_post**
> SelectProjectsResponse project_projects_select_projects_post(select_projects_request=select_projects_request)



Select projects for review in Explorer UI

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
    api_instance = openapi_client.ProjectApi(api_client)
    select_projects_request = openapi_client.SelectProjectsRequest() # SelectProjectsRequest |  (optional)

    try:
        api_response = api_instance.project_projects_select_projects_post(select_projects_request=select_projects_request)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_projects_select_projects_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **select_projects_request** | [**SelectProjectsRequest**](SelectProjectsRequest.md)|  | [optional] 

### Return type

[**SelectProjectsResponse**](SelectProjectsResponse.md)

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

# **project_task_queues_get**
> list[TaskQueue] project_task_queues_get(jq_filters=jq_filters)



Task Queue List

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
    api_instance = openapi_client.ProjectApi(api_client)
    jq_filters = {'key': 'jq_filters_example'} # dict(str, str) | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    try:
        api_response = api_instance.project_task_queues_get(jq_filters=jq_filters)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_task_queues_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jq_filters** | [**dict(str, str)**](str.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

### Return type

[**list[TaskQueue]**](TaskQueue.md)

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

# **project_task_queues_id_delete**
> project_task_queues_id_delete(id)



Delete Task Queue

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this task queue.

    try:
        api_instance.project_task_queues_id_delete(id)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_task_queues_id_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this task queue. | 

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

# **project_task_queues_id_get**
> TaskQueue project_task_queues_id_get(id, jq_filters=jq_filters)



Retrieve Task Queue

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this task queue.
jq_filters = {'key': 'jq_filters_example'} # dict(str, str) | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    try:
        api_response = api_instance.project_task_queues_id_get(id, jq_filters=jq_filters)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_task_queues_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this task queue. | 
 **jq_filters** | [**dict(str, str)**](str.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

### Return type

[**TaskQueue**](TaskQueue.md)

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

# **project_task_queues_id_patch**
> TaskQueue project_task_queues_id_patch(id, task_queue=task_queue)



Partial Update Task Queue

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this task queue.
task_queue = openapi_client.TaskQueue() # TaskQueue |  (optional)

    try:
        api_response = api_instance.project_task_queues_id_patch(id, task_queue=task_queue)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_task_queues_id_patch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this task queue. | 
 **task_queue** | [**TaskQueue**](TaskQueue.md)|  | [optional] 

### Return type

[**TaskQueue**](TaskQueue.md)

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

# **project_task_queues_id_put**
> TaskQueue project_task_queues_id_put(id, task_queue=task_queue)



Update Task Queue      PUT params:         - pk: int         - description: str         - documents: list[int]         - completed_documents: list[int]         - reviewers: list[int]     Optional params for add/remove document from/to a TaskQueue:         - add_document: int         - remove_document: int     Optional params for complete/reopen document in a TaskQueue:         - complete_document: int         - open_document: int     Optional param to add documents from DocumentCluster:         - add_documents_from_cluster: int (cluster id)

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
    api_instance = openapi_client.ProjectApi(api_client)
    id = 'id_example' # str | A unique integer value identifying this task queue.
task_queue = openapi_client.TaskQueue() # TaskQueue |  (optional)

    try:
        api_response = api_instance.project_task_queues_id_put(id, task_queue=task_queue)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_task_queues_id_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this task queue. | 
 **task_queue** | [**TaskQueue**](TaskQueue.md)|  | [optional] 

### Return type

[**TaskQueue**](TaskQueue.md)

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

# **project_task_queues_post**
> TaskQueue project_task_queues_post(task_queue=task_queue)



Create Task Queue

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
    api_instance = openapi_client.ProjectApi(api_client)
    task_queue = openapi_client.TaskQueue() # TaskQueue |  (optional)

    try:
        api_response = api_instance.project_task_queues_post(task_queue=task_queue)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_task_queues_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **task_queue** | [**TaskQueue**](TaskQueue.md)|  | [optional] 

### Return type

[**TaskQueue**](TaskQueue.md)

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

# **project_upload_session_get**
> list[UploadSessionDetail] project_upload_session_get(jq_filters=jq_filters)



Session Upload List

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
    api_instance = openapi_client.ProjectApi(api_client)
    jq_filters = {'key': 'jq_filters_example'} # dict(str, str) | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    try:
        api_response = api_instance.project_upload_session_get(jq_filters=jq_filters)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_upload_session_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jq_filters** | [**dict(str, str)**](str.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

### Return type

[**list[UploadSessionDetail]**](UploadSessionDetail.md)

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

# **project_upload_session_post**
> UploadSession project_upload_session_post(upload_session=upload_session)



Create Session Upload

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
    api_instance = openapi_client.ProjectApi(api_client)
    upload_session = openapi_client.UploadSession() # UploadSession |  (optional)

    try:
        api_response = api_instance.project_upload_session_post(upload_session=upload_session)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_upload_session_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **upload_session** | [**UploadSession**](UploadSession.md)|  | [optional] 

### Return type

[**UploadSession**](UploadSession.md)

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

# **project_upload_session_status_get**
> dict(str, object) project_upload_session_status_get(project_id=project_id)



Get status of Upload Sessions     Params:         - project_id: int

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
    api_instance = openapi_client.ProjectApi(api_client)
    project_id = 'project_id_example' # str | Project id (optional)

    try:
        api_response = api_instance.project_upload_session_status_get(project_id=project_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_upload_session_status_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**| Project id | [optional] 

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

# **project_upload_session_uid_batch_upload_post**
> UploadSessionDetail project_upload_session_uid_batch_upload_post(uid, upload_session_detail=upload_session_detail)



Upload batch of files      Params:         - folder (source_path): str - absolute path to a directory containing files         - force: bool (optional) - whether rewrite existing file and Document

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
    api_instance = openapi_client.ProjectApi(api_client)
    uid = 'uid_example' # str | A UUID string identifying this upload session.
upload_session_detail = openapi_client.UploadSessionDetail() # UploadSessionDetail |  (optional)

    try:
        api_response = api_instance.project_upload_session_uid_batch_upload_post(uid, upload_session_detail=upload_session_detail)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_upload_session_uid_batch_upload_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uid** | **str**| A UUID string identifying this upload session. | 
 **upload_session_detail** | [**UploadSessionDetail**](UploadSessionDetail.md)|  | [optional] 

### Return type

[**UploadSessionDetail**](UploadSessionDetail.md)

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

# **project_upload_session_uid_batch_upload_post_0**
> UploadSessionDetail project_upload_session_uid_batch_upload_post_0(uid, upload_session_batch_upload_request=upload_session_batch_upload_request)



Upload files from given sub-folder in media/data/documents folder      Params:         - source_path: relative path to a folder with documents

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
    api_instance = openapi_client.ProjectApi(api_client)
    uid = 'uid_example' # str | A UUID string identifying this upload session.
upload_session_batch_upload_request = openapi_client.UploadSessionBatchUploadRequest() # UploadSessionBatchUploadRequest |  (optional)

    try:
        api_response = api_instance.project_upload_session_uid_batch_upload_post_0(uid, upload_session_batch_upload_request=upload_session_batch_upload_request)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_upload_session_uid_batch_upload_post_0: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uid** | **str**| A UUID string identifying this upload session. | 
 **upload_session_batch_upload_request** | [**UploadSessionBatchUploadRequest**](UploadSessionBatchUploadRequest.md)|  | [optional] 

### Return type

[**UploadSessionDetail**](UploadSessionDetail.md)

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

# **project_upload_session_uid_cancel_delete**
> project_upload_session_uid_cancel_delete(uid)



Delete a file from session      Params:         - filename: str

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
    api_instance = openapi_client.ProjectApi(api_client)
    uid = 'uid_example' # str | A UUID string identifying this upload session.

    try:
        api_instance.project_upload_session_uid_cancel_delete(uid)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_upload_session_uid_cancel_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uid** | **str**| A UUID string identifying this upload session. | 

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

# **project_upload_session_uid_delete**
> project_upload_session_uid_delete(uid)



Delete Session Upload

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
    api_instance = openapi_client.ProjectApi(api_client)
    uid = 'uid_example' # str | A UUID string identifying this upload session.

    try:
        api_instance.project_upload_session_uid_delete(uid)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_upload_session_uid_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uid** | **str**| A UUID string identifying this upload session. | 

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

# **project_upload_session_uid_delete_file_delete**
> str project_upload_session_uid_delete_file_delete(uid, upload_session_delete_file_request=upload_session_delete_file_request)



Delete a file from session      Params:         - filename: str

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
    api_instance = openapi_client.ProjectApi(api_client)
    uid = 'uid_example' # str | A UUID string identifying this upload session.
upload_session_delete_file_request = openapi_client.UploadSessionDeleteFileRequest() # UploadSessionDeleteFileRequest |  (optional)

    try:
        api_response = api_instance.project_upload_session_uid_delete_file_delete(uid, upload_session_delete_file_request=upload_session_delete_file_request)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_upload_session_uid_delete_file_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uid** | **str**| A UUID string identifying this upload session. | 
 **upload_session_delete_file_request** | [**UploadSessionDeleteFileRequest**](UploadSessionDeleteFileRequest.md)|  | [optional] 

### Return type

**str**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** |  |  -  |
**200** |  |  -  |
**404** |  |  -  |
**500** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **project_upload_session_uid_files_post**
> ProjectUploadSessionFilesResponse project_upload_session_uid_files_post(uid, content_length, file_name, force=force, directory_path=directory_path, force2=force2, body=body)



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
    api_instance = openapi_client.ProjectApi(api_client)
    uid = 'uid_example' # str | A UUID string identifying this upload session.
content_length = 56 # int | Content Length
file_name = 'file_name_example' # str | Content Length
force = True # bool | Force upload (optional)
directory_path = True # bool | Directory Path (optional)
force2 = True # bool | Force upload (optional)
body = '/path/to/file' # file |  (optional)

    try:
        api_response = api_instance.project_upload_session_uid_files_post(uid, content_length, file_name, force=force, directory_path=directory_path, force2=force2, body=body)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_upload_session_uid_files_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uid** | **str**| A UUID string identifying this upload session. | 
 **content_length** | **int**| Content Length | 
 **file_name** | **str**| Content Length | 
 **force** | **bool**| Force upload | [optional] 
 **directory_path** | **bool**| Directory Path | [optional] 
 **force2** | **bool**| Force upload | [optional] 
 **body** | **file**|  | [optional] 

### Return type

[**ProjectUploadSessionFilesResponse**](ProjectUploadSessionFilesResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: application/offset+octet-stream
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |
**204** |  |  -  |
**400** |  |  -  |
**500** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **project_upload_session_uid_get**
> UploadSessionDetail project_upload_session_uid_get(uid, jq_filters=jq_filters)



Retrieve Session Upload

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
    api_instance = openapi_client.ProjectApi(api_client)
    uid = 'uid_example' # str | A UUID string identifying this upload session.
jq_filters = {'key': 'jq_filters_example'} # dict(str, str) | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    try:
        api_response = api_instance.project_upload_session_uid_get(uid, jq_filters=jq_filters)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_upload_session_uid_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uid** | **str**| A UUID string identifying this upload session. | 
 **jq_filters** | [**dict(str, str)**](str.md)| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional] 

### Return type

[**UploadSessionDetail**](UploadSessionDetail.md)

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

# **project_upload_session_uid_progress_get**
> ProjectUploadSessionProgressResponse project_upload_session_uid_progress_get(uid)



Get Progress for a session per files (short form)

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
    api_instance = openapi_client.ProjectApi(api_client)
    uid = 'uid_example' # str | A UUID string identifying this upload session.

    try:
        api_response = api_instance.project_upload_session_uid_progress_get(uid)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_upload_session_uid_progress_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uid** | **str**| A UUID string identifying this upload session. | 

### Return type

[**ProjectUploadSessionProgressResponse**](ProjectUploadSessionProgressResponse.md)

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

# **project_upload_session_uid_upload_post**
> ProjectUploadSessionPOSTResponse project_upload_session_uid_upload_post(uid, file_name, file_encoding, force=force, review_file=review_file, directory_path=directory_path, body=body)



Upload a File      Params:         - file: file object         - force: bool (optional) - whether rewrite existing file and Document         - review_file: bool - whether skip file check (exists or not)         - directory_path: str - may be passed from TUS plugin

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
    api_instance = openapi_client.ProjectApi(api_client)
    uid = 'uid_example' # str | A UUID string identifying this upload session.
file_name = True # bool | File Name
file_encoding = 'file_encoding_example' # str | File Encoding
force = True # bool | Force upload (optional)
review_file = True # bool | Review File (optional)
directory_path = True # bool | Directory Path (optional)
body = '/path/to/file' # file |  (optional)

    try:
        api_response = api_instance.project_upload_session_uid_upload_post(uid, file_name, file_encoding, force=force, review_file=review_file, directory_path=directory_path, body=body)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectApi->project_upload_session_uid_upload_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uid** | **str**| A UUID string identifying this upload session. | 
 **file_name** | **bool**| File Name | 
 **file_encoding** | **str**| File Encoding | 
 **force** | **bool**| Force upload | [optional] 
 **review_file** | **bool**| Review File | [optional] 
 **directory_path** | **bool**| Directory Path | [optional] 
 **body** | **file**|  | [optional] 

### Return type

[**ProjectUploadSessionPOSTResponse**](ProjectUploadSessionPOSTResponse.md)

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**400** |  |  -  |
**500** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

