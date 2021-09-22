# openapi_client.CommonApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**common_actions_get**](CommonApi.md#common_actions_get) | **GET** /api/v1/common/actions/ | 
[**common_actions_id_get**](CommonApi.md#common_actions_id_get) | **GET** /api/v1/common/actions/{id}/ | 
[**common_app_variables_get**](CommonApi.md#common_app_variables_get) | **GET** /api/v1/common/app-variables/ | 
[**common_app_variables_list_get**](CommonApi.md#common_app_variables_list_get) | **GET** /api/v1/common/app-variables/list/ | 
[**common_app_variables_project_project_id_get**](CommonApi.md#common_app_variables_project_project_id_get) | **GET** /api/v1/common/app-variables/project/{project_id}/ | 
[**common_app_variables_project_project_id_put**](CommonApi.md#common_app_variables_project_project_id_put) | **PUT** /api/v1/common/app-variables/project/{project_id}/ | 
[**common_media_path_get**](CommonApi.md#common_media_path_get) | **GET** /api/v1/common/media/{path}/ | 
[**common_menu_groups_form_fields_get**](CommonApi.md#common_menu_groups_form_fields_get) | **GET** /api/v1/common/menu-groups/form-fields/ | 
[**common_menu_groups_get**](CommonApi.md#common_menu_groups_get) | **GET** /api/v1/common/menu-groups/ | 
[**common_menu_groups_id_delete**](CommonApi.md#common_menu_groups_id_delete) | **DELETE** /api/v1/common/menu-groups/{id}/ | 
[**common_menu_groups_id_form_fields_get**](CommonApi.md#common_menu_groups_id_form_fields_get) | **GET** /api/v1/common/menu-groups/{id}/form-fields/ | 
[**common_menu_groups_id_get**](CommonApi.md#common_menu_groups_id_get) | **GET** /api/v1/common/menu-groups/{id}/ | 
[**common_menu_groups_id_patch**](CommonApi.md#common_menu_groups_id_patch) | **PATCH** /api/v1/common/menu-groups/{id}/ | 
[**common_menu_groups_id_put**](CommonApi.md#common_menu_groups_id_put) | **PUT** /api/v1/common/menu-groups/{id}/ | 
[**common_menu_groups_post**](CommonApi.md#common_menu_groups_post) | **POST** /api/v1/common/menu-groups/ | 
[**common_menu_items_form_fields_get**](CommonApi.md#common_menu_items_form_fields_get) | **GET** /api/v1/common/menu-items/form-fields/ | 
[**common_menu_items_get**](CommonApi.md#common_menu_items_get) | **GET** /api/v1/common/menu-items/ | 
[**common_menu_items_id_delete**](CommonApi.md#common_menu_items_id_delete) | **DELETE** /api/v1/common/menu-items/{id}/ | 
[**common_menu_items_id_form_fields_get**](CommonApi.md#common_menu_items_id_form_fields_get) | **GET** /api/v1/common/menu-items/{id}/form-fields/ | 
[**common_menu_items_id_get**](CommonApi.md#common_menu_items_id_get) | **GET** /api/v1/common/menu-items/{id}/ | 
[**common_menu_items_id_patch**](CommonApi.md#common_menu_items_id_patch) | **PATCH** /api/v1/common/menu-items/{id}/ | 
[**common_menu_items_id_put**](CommonApi.md#common_menu_items_id_put) | **PUT** /api/v1/common/menu-items/{id}/ | 
[**common_menu_items_post**](CommonApi.md#common_menu_items_post) | **POST** /api/v1/common/menu-items/ | 
[**common_review_status_groups_get**](CommonApi.md#common_review_status_groups_get) | **GET** /api/v1/common/review-status-groups/ | 
[**common_review_status_groups_id_delete**](CommonApi.md#common_review_status_groups_id_delete) | **DELETE** /api/v1/common/review-status-groups/{id}/ | 
[**common_review_status_groups_id_get**](CommonApi.md#common_review_status_groups_id_get) | **GET** /api/v1/common/review-status-groups/{id}/ | 
[**common_review_status_groups_id_patch**](CommonApi.md#common_review_status_groups_id_patch) | **PATCH** /api/v1/common/review-status-groups/{id}/ | 
[**common_review_status_groups_id_put**](CommonApi.md#common_review_status_groups_id_put) | **PUT** /api/v1/common/review-status-groups/{id}/ | 
[**common_review_status_groups_post**](CommonApi.md#common_review_status_groups_post) | **POST** /api/v1/common/review-status-groups/ | 
[**common_review_statuses_get**](CommonApi.md#common_review_statuses_get) | **GET** /api/v1/common/review-statuses/ | 
[**common_review_statuses_id_delete**](CommonApi.md#common_review_statuses_id_delete) | **DELETE** /api/v1/common/review-statuses/{id}/ | 
[**common_review_statuses_id_get**](CommonApi.md#common_review_statuses_id_get) | **GET** /api/v1/common/review-statuses/{id}/ | 
[**common_review_statuses_id_patch**](CommonApi.md#common_review_statuses_id_patch) | **PATCH** /api/v1/common/review-statuses/{id}/ | 
[**common_review_statuses_id_put**](CommonApi.md#common_review_statuses_id_put) | **PUT** /api/v1/common/review-statuses/{id}/ | 
[**common_review_statuses_post**](CommonApi.md#common_review_statuses_post) | **POST** /api/v1/common/review-statuses/ | 


# **common_actions_get**
> [Action] common_actions_get()



Action List

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.action import Action
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
    api_instance = common_api.CommonApi(api_client)
    project_id = 1 # int | Project ID (optional)
    document_id = 1 # int | Document ID (optional)
    view_actions = [
        "view_actions_example",
    ] # [str] | Action names (optional)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.common_actions_get(project_id=project_id, document_id=document_id, view_actions=view_actions, jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_actions_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**| Project ID | [optional]
 **document_id** | **int**| Document ID | [optional]
 **view_actions** | **[str]**| Action names | [optional]
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**[Action]**](Action.md)

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

# **common_actions_id_get**
> Action common_actions_id_get(id)



Retrieve Action

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.action import Action
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
    api_instance = common_api.CommonApi(api_client)
    id = "id_example" # str | A unique integer value identifying this action.
    project_id = 1 # int | Project ID (optional)
    document_id = 1 # int | Document ID (optional)
    view_actions = [
        "view_actions_example",
    ] # [str] | Action names (optional)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.common_actions_id_get(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_actions_id_get: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.common_actions_id_get(id, project_id=project_id, document_id=document_id, view_actions=view_actions, jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_actions_id_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this action. |
 **project_id** | **int**| Project ID | [optional]
 **document_id** | **int**| Document ID | [optional]
 **view_actions** | **[str]**| Action names | [optional]
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **common_app_variables_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} common_app_variables_get()



Retrieve App Variable(s)      Params:         - name: str - retrieve specific variable

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
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
    api_instance = common_api.CommonApi(api_client)
    name = "name_example" # str | App var name (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.common_app_variables_get(name=name)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_app_variables_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| App var name | [optional]

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

# **common_app_variables_list_get**
> [AppVar] common_app_variables_list_get()



### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.app_var import AppVar
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
    api_instance = common_api.CommonApi(api_client)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.common_app_variables_list_get(jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_app_variables_list_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**[AppVar]**](AppVar.md)

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

# **common_app_variables_project_project_id_get**
> [ProjectAppVar] common_app_variables_project_project_id_get(project_id)



Based on custom AppVar model storage

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.project_app_var import ProjectAppVar
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
    api_instance = common_api.CommonApi(api_client)
    project_id = "project_id_example" # str | 

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.common_app_variables_project_project_id_get(project_id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_app_variables_project_project_id_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  |

### Return type

[**[ProjectAppVar]**](ProjectAppVar.md)

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

# **common_app_variables_project_project_id_put**
> str common_app_variables_project_project_id_put(project_id)



Based on custom AppVar model storage

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.project_app_var import ProjectAppVar
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
    api_instance = common_api.CommonApi(api_client)
    project_id = "project_id_example" # str | 
    project_app_var = [
        ProjectAppVar(
            category="category_example",
            name="name_example",
            description="description_example",
            value={},
            access_type="access_type_example",
            use_system=True,
            system_value={},
        ),
    ] # [ProjectAppVar] |  (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.common_app_variables_project_project_id_put(project_id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_app_variables_project_project_id_put: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.common_app_variables_project_project_id_put(project_id, project_app_var=project_app_var)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_app_variables_project_project_id_put: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  |
 **project_app_var** | [**[ProjectAppVar]**](ProjectAppVar.md)|  | [optional]

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
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **common_media_path_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} common_media_path_get(path)



If directory:   action: None: - list directory   action: download - list directory (TODO - download directory)   action: info: - dict(info about directory) If file:   action: None: - show file   action: download - download file   action: info: - dict(info about directory)  :param request: :param path: str - relative path in /media directory  :query param action: optional str [\"download\", \"info\"] :return:

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
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
    api_instance = common_api.CommonApi(api_client)
    path = "path_example" # str | 
    action = "download" # str | Action name (optional) if omitted the server will use the default value of "download"

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.common_media_path_get(path)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_media_path_get: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.common_media_path_get(path, action=action)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_media_path_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **path** | **str**|  |
 **action** | **str**| Action name | [optional] if omitted the server will use the default value of "download"

### Return type

**{str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}**

### Authorization

[AuthToken](../README.md#AuthToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, */*


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **common_menu_groups_form_fields_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} common_menu_groups_form_fields_get()



GET model form fields description to build UI form for an object:       - field_type: str - CharField, IntegerField, SomeSerializerField - i.e. fields from a serializer      - ui_element: dict - {type: (\"input\" | \"select\" | \"checkbox\" | ...), data_type: (\"string\", \"integer\", \"date\", ...), ...}      - label: str - field label declared in a serializer field (default NULL)      - field_name: str - field name declared in a serializer field (default NULL)      - help_text: str - field help text declared in a serializer field (default NULL)      - required: bool - whether field is required      - read_only: bool - whether field is read only      - allow_null: bool - whether field is may be null      - default: bool - default (initial) field value for a new object (default NULL)      - choices: array - choices to select from [{choice_id1: choice_verbose_name1, ....}] (default NULL)

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
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
    api_instance = common_api.CommonApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_response = api_instance.common_menu_groups_form_fields_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_menu_groups_form_fields_get: %s\n" % e)
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

# **common_menu_groups_get**
> [MenuGroup] common_menu_groups_get()



MenuGroup List

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.menu_group import MenuGroup
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
    api_instance = common_api.CommonApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_response = api_instance.common_menu_groups_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_menu_groups_get: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

[**[MenuGroup]**](MenuGroup.md)

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

# **common_menu_groups_id_delete**
> common_menu_groups_id_delete(id)



Delete MenuGroup

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
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
    api_instance = common_api.CommonApi(api_client)
    id = "id_example" # str | 

    # example passing only required values which don't have defaults set
    try:
        api_instance.common_menu_groups_id_delete(id)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_menu_groups_id_delete: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  |

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

# **common_menu_groups_id_form_fields_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} common_menu_groups_id_form_fields_get(id)



GET model form fields description to build UI form for EXISTING object:       - value: any - object field value      - field_type: str - CharField, IntegerField, SomeSerializerField - i.e. fields from a serializer      - ui_element: dict - {type: (\"input\" | \"select\" | \"checkbox\" | ...), data_type: (\"string\", \"integer\", \"date\", ...), ...}      - label: str - field label declared in a serializer field (default NULL)      - field_name: str - field name declared in a serializer field (default NULL)      - help_text: str - field help text declared in a serializer field (default NULL)      - required: bool - whether field is required      - read_only: bool - whether field is read only      - allow_null: bool - whether field is may be null      - default: bool - default (initial) field value for a new object (default NULL)      - choices: array - choices to select from [{choice_id1: choice_verbose_name1, ....}] (default NULL)

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
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
    api_instance = common_api.CommonApi(api_client)
    id = "id_example" # str | A unique integer value identifying this user.

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.common_menu_groups_id_form_fields_get(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_menu_groups_id_form_fields_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this user. |

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

# **common_menu_groups_id_get**
> MenuGroup common_menu_groups_id_get(id)



Retrieve MenuGroup

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.menu_group import MenuGroup
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
    api_instance = common_api.CommonApi(api_client)
    id = "id_example" # str | 

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.common_menu_groups_id_get(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_menu_groups_id_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  |

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **common_menu_groups_id_patch**
> MenuGroup common_menu_groups_id_patch(id)



Partial Update MenuGroup

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.menu_group import MenuGroup
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
    api_instance = common_api.CommonApi(api_client)
    id = "id_example" # str | 
    menu_group = MenuGroup(
        name="name_example",
        public=True,
        order=0,
    ) # MenuGroup |  (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.common_menu_groups_id_patch(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_menu_groups_id_patch: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.common_menu_groups_id_patch(id, menu_group=menu_group)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_menu_groups_id_patch: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  |
 **menu_group** | [**MenuGroup**](MenuGroup.md)|  | [optional]

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **common_menu_groups_id_put**
> MenuGroup common_menu_groups_id_put(id)



Update MenuGroup

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.menu_group import MenuGroup
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
    api_instance = common_api.CommonApi(api_client)
    id = "id_example" # str | 
    menu_group = MenuGroup(
        name="name_example",
        public=True,
        order=0,
    ) # MenuGroup |  (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.common_menu_groups_id_put(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_menu_groups_id_put: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.common_menu_groups_id_put(id, menu_group=menu_group)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_menu_groups_id_put: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  |
 **menu_group** | [**MenuGroup**](MenuGroup.md)|  | [optional]

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **common_menu_groups_post**
> MenuGroup common_menu_groups_post()



Create MenuGroup

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.menu_group import MenuGroup
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
    api_instance = common_api.CommonApi(api_client)
    menu_group = MenuGroup(
        name="name_example",
        public=True,
        order=0,
    ) # MenuGroup |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.common_menu_groups_post(menu_group=menu_group)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_menu_groups_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **menu_group** | [**MenuGroup**](MenuGroup.md)|  | [optional]

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **common_menu_items_form_fields_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} common_menu_items_form_fields_get()



GET model form fields description to build UI form for an object:       - field_type: str - CharField, IntegerField, SomeSerializerField - i.e. fields from a serializer      - ui_element: dict - {type: (\"input\" | \"select\" | \"checkbox\" | ...), data_type: (\"string\", \"integer\", \"date\", ...), ...}      - label: str - field label declared in a serializer field (default NULL)      - field_name: str - field name declared in a serializer field (default NULL)      - help_text: str - field help text declared in a serializer field (default NULL)      - required: bool - whether field is required      - read_only: bool - whether field is read only      - allow_null: bool - whether field is may be null      - default: bool - default (initial) field value for a new object (default NULL)      - choices: array - choices to select from [{choice_id1: choice_verbose_name1, ....}] (default NULL)

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
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
    api_instance = common_api.CommonApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_response = api_instance.common_menu_items_form_fields_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_menu_items_form_fields_get: %s\n" % e)
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

# **common_menu_items_get**
> [MenuItem] common_menu_items_get()



MenuItem List

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.menu_item import MenuItem
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
    api_instance = common_api.CommonApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_response = api_instance.common_menu_items_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_menu_items_get: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

[**[MenuItem]**](MenuItem.md)

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

# **common_menu_items_id_delete**
> common_menu_items_id_delete(id)



Delete MenuItem

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
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
    api_instance = common_api.CommonApi(api_client)
    id = "id_example" # str | 

    # example passing only required values which don't have defaults set
    try:
        api_instance.common_menu_items_id_delete(id)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_menu_items_id_delete: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  |

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

# **common_menu_items_id_form_fields_get**
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} common_menu_items_id_form_fields_get(id)



GET model form fields description to build UI form for EXISTING object:       - value: any - object field value      - field_type: str - CharField, IntegerField, SomeSerializerField - i.e. fields from a serializer      - ui_element: dict - {type: (\"input\" | \"select\" | \"checkbox\" | ...), data_type: (\"string\", \"integer\", \"date\", ...), ...}      - label: str - field label declared in a serializer field (default NULL)      - field_name: str - field name declared in a serializer field (default NULL)      - help_text: str - field help text declared in a serializer field (default NULL)      - required: bool - whether field is required      - read_only: bool - whether field is read only      - allow_null: bool - whether field is may be null      - default: bool - default (initial) field value for a new object (default NULL)      - choices: array - choices to select from [{choice_id1: choice_verbose_name1, ....}] (default NULL)

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
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
    api_instance = common_api.CommonApi(api_client)
    id = "id_example" # str | A unique integer value identifying this user.

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.common_menu_items_id_form_fields_get(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_menu_items_id_form_fields_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this user. |

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

# **common_menu_items_id_get**
> MenuItem common_menu_items_id_get(id)



Retrieve MenuItem

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.menu_item import MenuItem
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
    api_instance = common_api.CommonApi(api_client)
    id = "id_example" # str | 

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.common_menu_items_id_get(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_menu_items_id_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  |

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **common_menu_items_id_patch**
> MenuItem common_menu_items_id_patch(id)



Partial Update MenuItem

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.menu_item import MenuItem
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
    api_instance = common_api.CommonApi(api_client)
    id = "id_example" # str | 
    menu_item = MenuItem(
        name="name_example",
        url="url_example",
        group=1,
        public=True,
        order=0,
    ) # MenuItem |  (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.common_menu_items_id_patch(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_menu_items_id_patch: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.common_menu_items_id_patch(id, menu_item=menu_item)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_menu_items_id_patch: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  |
 **menu_item** | [**MenuItem**](MenuItem.md)|  | [optional]

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **common_menu_items_id_put**
> MenuItem common_menu_items_id_put(id)



Update MenuItem

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.menu_item import MenuItem
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
    api_instance = common_api.CommonApi(api_client)
    id = "id_example" # str | 
    menu_item = MenuItem(
        name="name_example",
        url="url_example",
        group=1,
        public=True,
        order=0,
    ) # MenuItem |  (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.common_menu_items_id_put(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_menu_items_id_put: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.common_menu_items_id_put(id, menu_item=menu_item)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_menu_items_id_put: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  |
 **menu_item** | [**MenuItem**](MenuItem.md)|  | [optional]

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **common_menu_items_post**
> MenuItem common_menu_items_post()



Create MenuItem

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.menu_item import MenuItem
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
    api_instance = common_api.CommonApi(api_client)
    menu_item = MenuItem(
        name="name_example",
        url="url_example",
        group=1,
        public=True,
        order=0,
    ) # MenuItem |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.common_menu_items_post(menu_item=menu_item)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_menu_items_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **menu_item** | [**MenuItem**](MenuItem.md)|  | [optional]

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **common_review_status_groups_get**
> [ReviewStatusGroup] common_review_status_groups_get()



ReviewStatusGroup List

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.review_status_group import ReviewStatusGroup
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
    api_instance = common_api.CommonApi(api_client)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.common_review_status_groups_get(jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_review_status_groups_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**[ReviewStatusGroup]**](ReviewStatusGroup.md)

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

# **common_review_status_groups_id_delete**
> common_review_status_groups_id_delete(id)



Delete ReviewStatusGroup

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
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
    api_instance = common_api.CommonApi(api_client)
    id = "id_example" # str | A unique integer value identifying this Review Status Group.

    # example passing only required values which don't have defaults set
    try:
        api_instance.common_review_status_groups_id_delete(id)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_review_status_groups_id_delete: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this Review Status Group. |

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

# **common_review_status_groups_id_get**
> ReviewStatusGroup common_review_status_groups_id_get(id)



Retrieve ReviewStatusGroup

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.review_status_group import ReviewStatusGroup
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
    api_instance = common_api.CommonApi(api_client)
    id = "id_example" # str | A unique integer value identifying this Review Status Group.
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.common_review_status_groups_id_get(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_review_status_groups_id_get: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.common_review_status_groups_id_get(id, jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_review_status_groups_id_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this Review Status Group. |
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **common_review_status_groups_id_patch**
> ReviewStatusGroup common_review_status_groups_id_patch(id)



Partial Update ReviewStatusGroup

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.review_status_group import ReviewStatusGroup
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
    api_instance = common_api.CommonApi(api_client)
    id = "id_example" # str | A unique integer value identifying this Review Status Group.
    review_status_group = ReviewStatusGroup(
        name="name_example",
        code="code_example",
        order=0,
        is_active=True,
    ) # ReviewStatusGroup |  (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.common_review_status_groups_id_patch(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_review_status_groups_id_patch: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.common_review_status_groups_id_patch(id, review_status_group=review_status_group)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_review_status_groups_id_patch: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this Review Status Group. |
 **review_status_group** | [**ReviewStatusGroup**](ReviewStatusGroup.md)|  | [optional]

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **common_review_status_groups_id_put**
> ReviewStatusGroup common_review_status_groups_id_put(id)



Update ReviewStatusGroup

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.review_status_group import ReviewStatusGroup
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
    api_instance = common_api.CommonApi(api_client)
    id = "id_example" # str | A unique integer value identifying this Review Status Group.
    review_status_group = ReviewStatusGroup(
        name="name_example",
        code="code_example",
        order=0,
        is_active=True,
    ) # ReviewStatusGroup |  (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.common_review_status_groups_id_put(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_review_status_groups_id_put: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.common_review_status_groups_id_put(id, review_status_group=review_status_group)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_review_status_groups_id_put: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this Review Status Group. |
 **review_status_group** | [**ReviewStatusGroup**](ReviewStatusGroup.md)|  | [optional]

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **common_review_status_groups_post**
> ReviewStatusGroup common_review_status_groups_post()



Create ReviewStatusGroup

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.review_status_group import ReviewStatusGroup
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
    api_instance = common_api.CommonApi(api_client)
    review_status_group = ReviewStatusGroup(
        name="name_example",
        code="code_example",
        order=0,
        is_active=True,
    ) # ReviewStatusGroup |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.common_review_status_groups_post(review_status_group=review_status_group)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_review_status_groups_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **review_status_group** | [**ReviewStatusGroup**](ReviewStatusGroup.md)|  | [optional]

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **common_review_statuses_get**
> [ReviewStatusDetail] common_review_statuses_get()



ReviewStatus List

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.review_status_detail import ReviewStatusDetail
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
    api_instance = common_api.CommonApi(api_client)
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.common_review_statuses_get(jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_review_statuses_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

### Return type

[**[ReviewStatusDetail]**](ReviewStatusDetail.md)

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

# **common_review_statuses_id_delete**
> common_review_statuses_id_delete(id)



Delete ReviewStatus

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
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
    api_instance = common_api.CommonApi(api_client)
    id = "id_example" # str | A unique integer value identifying this Review Status.

    # example passing only required values which don't have defaults set
    try:
        api_instance.common_review_statuses_id_delete(id)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_review_statuses_id_delete: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this Review Status. |

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

# **common_review_statuses_id_get**
> ReviewStatusDetail common_review_statuses_id_get(id)



Retrieve ReviewStatus

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.review_status_detail import ReviewStatusDetail
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
    api_instance = common_api.CommonApi(api_client)
    id = "id_example" # str | A unique integer value identifying this Review Status.
    jq_filters = {
        "key": "key_example",
    } # {str: (str,)} | Filter params similar to JQWidgets grid filter params:                             filterscount=1,                             filterdatafield0=\"a\",                             filtervalue0=\"b\",                             filtercondition0=\"CONTAINS\",                             filteroperator0=1,                             sortdatafied=\"c\",                            sortorder=\"asc\"                             (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.common_review_statuses_id_get(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_review_statuses_id_get: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.common_review_statuses_id_get(id, jq_filters=jq_filters)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_review_statuses_id_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this Review Status. |
 **jq_filters** | **{str: (str,)}**| Filter params similar to JQWidgets grid filter params:                             filterscount&#x3D;1,                             filterdatafield0&#x3D;\&quot;a\&quot;,                             filtervalue0&#x3D;\&quot;b\&quot;,                             filtercondition0&#x3D;\&quot;CONTAINS\&quot;,                             filteroperator0&#x3D;1,                             sortdatafied&#x3D;\&quot;c\&quot;,                            sortorder&#x3D;\&quot;asc\&quot;                             | [optional]

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **common_review_statuses_id_patch**
> ReviewStatus common_review_statuses_id_patch(id)



Partial Update ReviewStatus

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.review_status import ReviewStatus
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
    api_instance = common_api.CommonApi(api_client)
    id = "id_example" # str | A unique integer value identifying this Review Status.
    review_status = ReviewStatus(
        name="name_example",
        code="code_example",
        order=0,
        is_active=True,
        group=1,
    ) # ReviewStatus |  (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.common_review_statuses_id_patch(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_review_statuses_id_patch: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.common_review_statuses_id_patch(id, review_status=review_status)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_review_statuses_id_patch: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this Review Status. |
 **review_status** | [**ReviewStatus**](ReviewStatus.md)|  | [optional]

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **common_review_statuses_id_put**
> ReviewStatus common_review_statuses_id_put(id)



Update ReviewStatus

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.review_status import ReviewStatus
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
    api_instance = common_api.CommonApi(api_client)
    id = "id_example" # str | A unique integer value identifying this Review Status.
    review_status = ReviewStatus(
        name="name_example",
        code="code_example",
        order=0,
        is_active=True,
        group=1,
    ) # ReviewStatus |  (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.common_review_statuses_id_put(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_review_statuses_id_put: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.common_review_statuses_id_put(id, review_status=review_status)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_review_statuses_id_put: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| A unique integer value identifying this Review Status. |
 **review_status** | [**ReviewStatus**](ReviewStatus.md)|  | [optional]

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **common_review_statuses_post**
> ReviewStatus common_review_statuses_post()



Create ReviewStatus

### Example

* Api Key Authentication (AuthToken):
```python
import time
import openapi_client
from openapi_client.api import common_api
from openapi_client.model.review_status import ReviewStatus
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
    api_instance = common_api.CommonApi(api_client)
    review_status = ReviewStatus(
        name="name_example",
        code="code_example",
        order=0,
        is_active=True,
        group=1,
    ) # ReviewStatus |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.common_review_statuses_post(review_status=review_status)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CommonApi->common_review_statuses_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **review_status** | [**ReviewStatus**](ReviewStatus.md)|  | [optional]

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

