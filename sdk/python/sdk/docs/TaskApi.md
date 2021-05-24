# openapi_client.TaskApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**task_clean_tasks_post**](TaskApi.md#task_clean_tasks_post) | **POST** /api/v1/task/clean-tasks/ | 
[**task_load_dictionaries_post**](TaskApi.md#task_load_dictionaries_post) | **POST** /api/v1/task/load-dictionaries/ | 
[**task_load_documents_get**](TaskApi.md#task_load_documents_get) | **GET** /api/v1/task/load-documents/ | 
[**task_load_documents_post**](TaskApi.md#task_load_documents_post) | **POST** /api/v1/task/load-documents/ | 
[**task_locate_get**](TaskApi.md#task_locate_get) | **GET** /api/v1/task/locate/ | 
[**task_locate_post**](TaskApi.md#task_locate_post) | **POST** /api/v1/task/locate/ | 
[**task_process_text_extraction_results_request_id_post**](TaskApi.md#task_process_text_extraction_results_request_id_post) | **POST** /api/v1/task/process_text_extraction_results/{request_id}/ | 
[**task_purge_task_post**](TaskApi.md#task_purge_task_post) | **POST** /api/v1/task/purge-task/ | 
[**task_recall_task_get**](TaskApi.md#task_recall_task_get) | **GET** /api/v1/task/recall-task/ | 
[**task_recall_task_post**](TaskApi.md#task_recall_task_post) | **POST** /api/v1/task/recall-task/ | 
[**task_reindexroutines_check_schedule_post**](TaskApi.md#task_reindexroutines_check_schedule_post) | **POST** /api/v1/task/reindexroutines/check_schedule | 
[**task_task_log_get**](TaskApi.md#task_task_log_get) | **GET** /api/v1/task/task-log/ | 
[**task_task_status_get**](TaskApi.md#task_task_status_get) | **GET** /api/v1/task/task-status/ | 
[**task_tasks_get**](TaskApi.md#task_tasks_get) | **GET** /api/v1/task/tasks/ | 
[**task_tasks_id_get**](TaskApi.md#task_tasks_id_get) | **GET** /api/v1/task/tasks/{id}/ | 
[**task_tasks_project_project_id_active_tasks_get**](TaskApi.md#task_tasks_project_project_id_active_tasks_get) | **GET** /api/v1/task/tasks/project/{project_id}/active-tasks/ | 
[**task_tasks_project_project_id_tasks_get**](TaskApi.md#task_tasks_project_project_id_tasks_get) | **GET** /api/v1/task/tasks/project/{project_id}/tasks/ | 
[**task_update_elastic_index_get**](TaskApi.md#task_update_elastic_index_get) | **GET** /api/v1/task/update-elastic-index/ | 
[**task_update_elastic_index_post**](TaskApi.md#task_update_elastic_index_post) | **POST** /api/v1/task/update-elastic-index/ | 


# **task_clean_tasks_post**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} task_clean_tasks_post()



\"Clean Tasks\" admin task

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import task_api
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
    api_instance = task_api.TaskApi(api_client)
    request_body = {
        "key": {},
    } # {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.task_clean_tasks_post(request_body=request_body)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_clean_tasks_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | **{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**|  | [optional]

### Return type

**{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**

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

# **task_load_dictionaries_post**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} task_load_dictionaries_post()



\"Load Dictionaries\" admin task  POST params:     - terms_accounting: bool:     - terms_accounting_1: bool:     - terms_accounting_1_locale_en: bool:     - terms_accounting_2: bool:     - terms_accounting_2_locale_en: bool:     - terms_accounting_3: bool:     - terms_accounting_3_locale_en: bool:     - terms_accounting_4: bool:     - terms_accounting_4_locale_en: bool:     - terms_accounting_5: bool:     - terms_accounting_5_locale_en: bool:     - terms_scientific: bool:     - terms_scientific_1: bool:     - terms_scientific1_locale_en: bool:     - terms_financial: bool:     - terms_financial_1: bool:     - terms_financial_1_locale_en: bool:     - terms_legal: bool:     - terms_legal_1: bool:     - terms_legal_1_locale_en: bool:     - terms_legal_2: bool:     - terms_legal_2_locale_en: bool:     - terms_legal_3: bool:     - terms_legal_3_locale_en: bool:     - terms_legal_4: bool:     - terms_legal_4_locale_en: bool:     - terms_file_path: str:     - terms_delete: bool:     - courts: bool:     - courts_1: bool:     - courts_1_locale_en: bool:     - courts_2: bool:     - courts_2_locale_en: bool:     - courts_file_path: str:     - courts_delete: bool:     - geoentities: bool:     - geoentities_1: bool:     - geoentities_1_locale_multi: bool:     - geoentities_file_path: str:     - geoentities_delete: bool:

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import task_api
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
    api_instance = task_api.TaskApi(api_client)
    request_body = {
        "key": {},
    } # {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.task_load_dictionaries_post(request_body=request_body)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_load_dictionaries_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | **{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**|  | [optional]

### Return type

**{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**

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

# **task_load_documents_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} task_load_documents_get()



\"Load Documents\" admin task  POST params:     - project: int     - source_data: str     - source_type: str     - document_type: str     - delete: bool     - run_standard_locators: bool

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import task_api
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
    api_instance = task_api.TaskApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_response = api_instance.task_load_documents_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_load_documents_get: %s\n" % e)
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

# **task_load_documents_post**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} task_load_documents_post()



\"Load Documents\" admin task  POST params:     - project: int     - source_data: str     - source_type: str     - document_type: str     - delete: bool     - run_standard_locators: bool

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import task_api
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
    api_instance = task_api.TaskApi(api_client)
    request_body = {
        "key": {},
    } # {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.task_load_documents_post(request_body=request_body)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_load_documents_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | **{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**|  | [optional]

### Return type

**{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**

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

# **task_locate_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} task_locate_get()



\"Locate\" admin task  POST params:     - locate_all: bool     - geoentity_locate: bool     - geoentity_priority: bool     - geoentity_delete: bool     - date_locate: bool     - date_strict: bool     - date_delete: bool     - amount_locate: bool     - amount_delete: bool     - citation_locate: bool     - citation_delete: bool     - copyright_locate: bool     - copyright_delete: bool     - court_locate: bool     - court_delete: bool     - currency_locate: bool     - currency_delete: bool     - duration_locate: bool     - duration_delete: bool     - definition_locate: bool     - definition_delete: bool     - distance_locate: bool     - distance_delete: bool     - party_locate: bool     - party_delete: bool     - percent_locate: bool     - percent_delete: bool     - ratio_locate: bool     - ratio_delete: bool     - regulation_locate: bool     - regulation_delete: bool     - term_locate: bool     - term_delete: bool     - trademark_locate: bool     - trademark_delete: bool     - url_locate: bool     - url_delete: bool     - parse_choice_sentence: bool     - parse_choice_paragraph: bool     - project: int

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import task_api
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
    api_instance = task_api.TaskApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_response = api_instance.task_locate_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_locate_get: %s\n" % e)
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

# **task_locate_post**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} task_locate_post()



\"Locate\" admin task  POST params:     - locate_all: bool     - geoentity_locate: bool     - geoentity_priority: bool     - geoentity_delete: bool     - date_locate: bool     - date_strict: bool     - date_delete: bool     - amount_locate: bool     - amount_delete: bool     - citation_locate: bool     - citation_delete: bool     - copyright_locate: bool     - copyright_delete: bool     - court_locate: bool     - court_delete: bool     - currency_locate: bool     - currency_delete: bool     - duration_locate: bool     - duration_delete: bool     - definition_locate: bool     - definition_delete: bool     - distance_locate: bool     - distance_delete: bool     - party_locate: bool     - party_delete: bool     - percent_locate: bool     - percent_delete: bool     - ratio_locate: bool     - ratio_delete: bool     - regulation_locate: bool     - regulation_delete: bool     - term_locate: bool     - term_delete: bool     - trademark_locate: bool     - trademark_delete: bool     - url_locate: bool     - url_delete: bool     - parse_choice_sentence: bool     - parse_choice_paragraph: bool     - project: int

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import task_api
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
    api_instance = task_api.TaskApi(api_client)
    request_body = {
        "key": {},
    } # {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.task_locate_post(request_body=request_body)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_locate_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | **{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**|  | [optional]

### Return type

**{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**

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

# **task_process_text_extraction_results_request_id_post**
> bool, date, datetime, dict, float, int, list, str, none_type task_process_text_extraction_results_request_id_post(request_id)



### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import task_api
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
    api_instance = task_api.TaskApi(api_client)
    request_id = "request_id_example" # str | 
    request_body = {
        "key": {},
    } # {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} |  (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.task_process_text_extraction_results_request_id_post(request_id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_process_text_extraction_results_request_id_post: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.task_process_text_extraction_results_request_id_post(request_id, request_body=request_body)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_process_text_extraction_results_request_id_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_id** | **str**|  |
 **request_body** | **{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**|  | [optional]

### Return type

**bool, date, datetime, dict, float, int, list, str, none_type**

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

# **task_purge_task_post**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} task_purge_task_post()



\"Purge Task\" admin task  POST params:     - task_pk: int

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import task_api
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
    api_instance = task_api.TaskApi(api_client)
    request_body = {
        "key": {},
    } # {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.task_purge_task_post(request_body=request_body)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_purge_task_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | **{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**|  | [optional]

### Return type

**{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**

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

# **task_recall_task_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} task_recall_task_get()



\"Recall Task\" admin task  POST params:     - task_pk: int

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import task_api
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
    api_instance = task_api.TaskApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_response = api_instance.task_recall_task_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_recall_task_get: %s\n" % e)
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

# **task_recall_task_post**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} task_recall_task_post()



\"Recall Task\" admin task  POST params:     - task_pk: int

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import task_api
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
    api_instance = task_api.TaskApi(api_client)
    request_body = {
        "key": {},
    } # {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.task_recall_task_post(request_body=request_body)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_recall_task_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | **{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**|  | [optional]

### Return type

**{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**

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

# **task_reindexroutines_check_schedule_post**
> bool, date, datetime, dict, float, int, list, str, none_type task_reindexroutines_check_schedule_post()



### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import task_api
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
    api_instance = task_api.TaskApi(api_client)
    request_body = {
        "key": {},
    } # {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.task_reindexroutines_check_schedule_post(request_body=request_body)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_reindexroutines_check_schedule_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | **{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**|  | [optional]

### Return type

**bool, date, datetime, dict, float, int, list, str, none_type**

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

# **task_task_log_get**
> [TaskLogResponse] task_task_log_get(task_id)



Get task log records GET params:     - task_id: int     - records_limit: int

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import task_api
from openapi_client.model.task_log_response import TaskLogResponse
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
    api_instance = task_api.TaskApi(api_client)
    task_id = "task_id_example" # str | 
    records_limit = 1 # int |  (optional)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.task_task_log_get(task_id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_task_log_get: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.task_task_log_get(task_id, records_limit=records_limit, jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_task_log_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **task_id** | **str**|  |
 **records_limit** | **int**|  | [optional]
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**[TaskLogResponse]**](TaskLogResponse.md)

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

# **task_task_status_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} task_task_status_get()



Check admin task status  GET params:     - task_id: int

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import task_api
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
    api_instance = task_api.TaskApi(api_client)
    task_id = "task_id_example" # str |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.task_task_status_get(task_id=task_id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_task_status_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **task_id** | **str**|  | [optional]

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
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **task_tasks_get**
> [Task] task_tasks_get()



Task List

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import task_api
from openapi_client.model.task import Task
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
    api_instance = task_api.TaskApi(api_client)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.task_tasks_get(jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_tasks_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**[Task]**](Task.md)

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

# **task_tasks_id_get**
> Task task_tasks_id_get(id)



Retrieve Task

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import task_api
from openapi_client.model.task import Task
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
    api_instance = task_api.TaskApi(api_client)
    id = "id_example" # str | A unique value identifying this task.
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.task_tasks_id_get(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_tasks_id_get: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.task_tasks_id_get(id, jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_tasks_id_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique value identifying this task. |
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

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
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **task_tasks_project_project_id_active_tasks_get**
> [ProjectActiveTasks] task_tasks_project_project_id_active_tasks_get(project_id)



### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import task_api
from openapi_client.model.project_active_tasks import ProjectActiveTasks
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
    api_instance = task_api.TaskApi(api_client)
    project_id = "project_id_example" # str | 
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.task_tasks_project_project_id_active_tasks_get(project_id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_tasks_project_project_id_active_tasks_get: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.task_tasks_project_project_id_active_tasks_get(project_id, jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_tasks_project_project_id_active_tasks_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  |
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**[ProjectActiveTasks]**](ProjectActiveTasks.md)

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

# **task_tasks_project_project_id_tasks_get**
> [ProjectTasks] task_tasks_project_project_id_tasks_get(project_id)



### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import task_api
from openapi_client.model.project_tasks import ProjectTasks
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
    api_instance = task_api.TaskApi(api_client)
    project_id = "project_id_example" # str | 
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.task_tasks_project_project_id_tasks_get(project_id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_tasks_project_project_id_tasks_get: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.task_tasks_project_project_id_tasks_get(project_id, jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_tasks_project_project_id_tasks_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  |
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**[ProjectTasks]**](ProjectTasks.md)

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

# **task_update_elastic_index_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} task_update_elastic_index_get()



\"Update ElasticSearch Index\" admin task

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import task_api
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
    api_instance = task_api.TaskApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_response = api_instance.task_update_elastic_index_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_update_elastic_index_get: %s\n" % e)
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

# **task_update_elastic_index_post**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} task_update_elastic_index_post()



\"Update ElasticSearch Index\" admin task

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import task_api
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
    api_instance = task_api.TaskApi(api_client)
    request_body = {
        "key": {},
    } # {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.task_update_elastic_index_post(request_body=request_body)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling TaskApi->task_update_elastic_index_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | **{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**|  | [optional]

### Return type

**{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**

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

