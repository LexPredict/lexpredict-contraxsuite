"""
    Contraxsuite API

    Contraxsuite API  # noqa: E501

    The version of the OpenAPI document: 2.0.0
    Generated by: https://openapi-generator.tech
"""


import re  # noqa: F401
import sys  # noqa: F401

from openapi_client.api_client import ApiClient, Endpoint as _Endpoint
from openapi_client.model_utils import (  # noqa: F401
    check_allowed_values,
    check_validations,
    date,
    datetime,
    file_type,
    none_type,
    validate_and_convert_types
)
from openapi_client.model.rawdb_documents_post_request import RawdbDocumentsPOSTRequest
from openapi_client.model.social_accounts_response import SocialAccountsResponse


class RawdbApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

        def __rawdb_config_get(
            self,
            **kwargs
        ):
            """rawdb_config_get  # noqa: E501

            This method makes a synchronous HTTP request by default. To make an
            asynchronous HTTP request, please pass async_req=True

            >>> thread = api.rawdb_config_get(async_req=True)
            >>> result = thread.get()


            Keyword Args:
                _return_http_data_only (bool): response data without head status
                    code and headers. Default is True.
                _preload_content (bool): if False, the urllib3.HTTPResponse object
                    will be returned without reading/decoding response data.
                    Default is True.
                _request_timeout (float/tuple): timeout setting for this request. If one
                    number provided, it will be total request timeout. It can also
                    be a pair (tuple) of (connection, read) timeouts.
                    Default is None.
                _check_input_type (bool): specifies if type checking
                    should be done one the data sent to the server.
                    Default is True.
                _check_return_type (bool): specifies if type checking
                    should be done one the data received from the server.
                    Default is True.
                _host_index (int/None): specifies the index of the server
                    that we want to use.
                    Default is read from the configuration.
                async_req (bool): execute request asynchronously

            Returns:
                {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}
                    If the method is called asynchronously, returns the request
                    thread.
            """
            kwargs['async_req'] = kwargs.get(
                'async_req', False
            )
            kwargs['_return_http_data_only'] = kwargs.get(
                '_return_http_data_only', True
            )
            kwargs['_preload_content'] = kwargs.get(
                '_preload_content', True
            )
            kwargs['_request_timeout'] = kwargs.get(
                '_request_timeout', None
            )
            kwargs['_check_input_type'] = kwargs.get(
                '_check_input_type', True
            )
            kwargs['_check_return_type'] = kwargs.get(
                '_check_return_type', True
            )
            kwargs['_host_index'] = kwargs.get('_host_index')
            return self.call_with_http_info(**kwargs)

        self.rawdb_config_get = _Endpoint(
            settings={
                'response_type': ({str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)},),
                'auth': [
                    'AuthToken'
                ],
                'endpoint_path': '/api/v1/rawdb/config/',
                'operation_id': 'rawdb_config_get',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                ],
                'required': [],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                },
                'attribute_map': {
                },
                'location_map': {
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [],
            },
            api_client=api_client,
            callable=__rawdb_config_get
        )

        def __rawdb_documents_document_type_code_get(
            self,
            document_type_code,
            **kwargs
        ):
            """rawdb_documents_document_type_code_get  # noqa: E501

            This method makes a synchronous HTTP request by default. To make an
            asynchronous HTTP request, please pass async_req=True

            >>> thread = api.rawdb_documents_document_type_code_get(document_type_code, async_req=True)
            >>> result = thread.get()

            Args:
                document_type_code (str):

            Keyword Args:
                project_ids (str): Project ids separated by commas. [optional]
                columns (str): Column names separated by commas. [optional]
                associated_text (bool): Boolean - show associated text. [optional]
                as_zip (bool): Boolean - export as zip. [optional]
                fmt (str): Export format. [optional]
                limit (int): Page Size. [optional]
                order_by (str): Sort order - column names separated by commas. [optional]
                saved_filters (str): Saved filter ids separated by commas. [optional]
                save_filter (bool): Save filter. [optional]
                return_reviewed (bool): Return Reviewed documents count. [optional]
                return_total (bool): Return total documents count. [optional]
                return_data (bool): Return data. [optional]
                ignore_errors (bool): Ignore errors. [optional]
                filters ({str: (str,)}): Filter params. [optional]
                _return_http_data_only (bool): response data without head status
                    code and headers. Default is True.
                _preload_content (bool): if False, the urllib3.HTTPResponse object
                    will be returned without reading/decoding response data.
                    Default is True.
                _request_timeout (float/tuple): timeout setting for this request. If one
                    number provided, it will be total request timeout. It can also
                    be a pair (tuple) of (connection, read) timeouts.
                    Default is None.
                _check_input_type (bool): specifies if type checking
                    should be done one the data sent to the server.
                    Default is True.
                _check_return_type (bool): specifies if type checking
                    should be done one the data received from the server.
                    Default is True.
                _host_index (int/None): specifies the index of the server
                    that we want to use.
                    Default is read from the configuration.
                async_req (bool): execute request asynchronously

            Returns:
                {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}
                    If the method is called asynchronously, returns the request
                    thread.
            """
            kwargs['async_req'] = kwargs.get(
                'async_req', False
            )
            kwargs['_return_http_data_only'] = kwargs.get(
                '_return_http_data_only', True
            )
            kwargs['_preload_content'] = kwargs.get(
                '_preload_content', True
            )
            kwargs['_request_timeout'] = kwargs.get(
                '_request_timeout', None
            )
            kwargs['_check_input_type'] = kwargs.get(
                '_check_input_type', True
            )
            kwargs['_check_return_type'] = kwargs.get(
                '_check_return_type', True
            )
            kwargs['_host_index'] = kwargs.get('_host_index')
            kwargs['document_type_code'] = \
                document_type_code
            return self.call_with_http_info(**kwargs)

        self.rawdb_documents_document_type_code_get = _Endpoint(
            settings={
                'response_type': ({str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)},),
                'auth': [
                    'AuthToken'
                ],
                'endpoint_path': '/api/v1/rawdb/documents/{document_type_code}/',
                'operation_id': 'rawdb_documents_document_type_code_get',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'document_type_code',
                    'project_ids',
                    'columns',
                    'associated_text',
                    'as_zip',
                    'fmt',
                    'limit',
                    'order_by',
                    'saved_filters',
                    'save_filter',
                    'return_reviewed',
                    'return_total',
                    'return_data',
                    'ignore_errors',
                    'filters',
                ],
                'required': [
                    'document_type_code',
                ],
                'nullable': [
                ],
                'enum': [
                    'fmt',
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                    ('fmt',): {

                        "JSON": "json",
                        "CSV": "csv",
                        "XLSX": "xlsx"
                    },
                },
                'openapi_types': {
                    'document_type_code':
                        (str,),
                    'project_ids':
                        (str,),
                    'columns':
                        (str,),
                    'associated_text':
                        (bool,),
                    'as_zip':
                        (bool,),
                    'fmt':
                        (str,),
                    'limit':
                        (int,),
                    'order_by':
                        (str,),
                    'saved_filters':
                        (str,),
                    'save_filter':
                        (bool,),
                    'return_reviewed':
                        (bool,),
                    'return_total':
                        (bool,),
                    'return_data':
                        (bool,),
                    'ignore_errors':
                        (bool,),
                    'filters':
                        ({str: (str,)},),
                },
                'attribute_map': {
                    'document_type_code': 'document_type_code',
                    'project_ids': 'project_ids',
                    'columns': 'columns',
                    'associated_text': 'associated_text',
                    'as_zip': 'as_zip',
                    'fmt': 'fmt',
                    'limit': 'limit',
                    'order_by': 'order_by',
                    'saved_filters': 'saved_filters',
                    'save_filter': 'save_filter',
                    'return_reviewed': 'return_reviewed',
                    'return_total': 'return_total',
                    'return_data': 'return_data',
                    'ignore_errors': 'ignore_errors',
                    'filters': 'filters',
                },
                'location_map': {
                    'document_type_code': 'path',
                    'project_ids': 'query',
                    'columns': 'query',
                    'associated_text': 'query',
                    'as_zip': 'query',
                    'fmt': 'query',
                    'limit': 'query',
                    'order_by': 'query',
                    'saved_filters': 'query',
                    'save_filter': 'query',
                    'return_reviewed': 'query',
                    'return_total': 'query',
                    'return_data': 'query',
                    'ignore_errors': 'query',
                    'filters': 'query',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [],
            },
            api_client=api_client,
            callable=__rawdb_documents_document_type_code_get
        )

        def __rawdb_documents_document_type_code_post(
            self,
            document_type_code,
            **kwargs
        ):
            """rawdb_documents_document_type_code_post  # noqa: E501

            See .get() method signature, .post() method just reflects it and uses the same request.GET params to get data  # noqa: E501
            This method makes a synchronous HTTP request by default. To make an
            asynchronous HTTP request, please pass async_req=True

            >>> thread = api.rawdb_documents_document_type_code_post(document_type_code, async_req=True)
            >>> result = thread.get()

            Args:
                document_type_code (str):

            Keyword Args:
                rawdb_documents_post_request (RawdbDocumentsPOSTRequest): [optional]
                _return_http_data_only (bool): response data without head status
                    code and headers. Default is True.
                _preload_content (bool): if False, the urllib3.HTTPResponse object
                    will be returned without reading/decoding response data.
                    Default is True.
                _request_timeout (float/tuple): timeout setting for this request. If one
                    number provided, it will be total request timeout. It can also
                    be a pair (tuple) of (connection, read) timeouts.
                    Default is None.
                _check_input_type (bool): specifies if type checking
                    should be done one the data sent to the server.
                    Default is True.
                _check_return_type (bool): specifies if type checking
                    should be done one the data received from the server.
                    Default is True.
                _host_index (int/None): specifies the index of the server
                    that we want to use.
                    Default is read from the configuration.
                async_req (bool): execute request asynchronously

            Returns:
                {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}
                    If the method is called asynchronously, returns the request
                    thread.
            """
            kwargs['async_req'] = kwargs.get(
                'async_req', False
            )
            kwargs['_return_http_data_only'] = kwargs.get(
                '_return_http_data_only', True
            )
            kwargs['_preload_content'] = kwargs.get(
                '_preload_content', True
            )
            kwargs['_request_timeout'] = kwargs.get(
                '_request_timeout', None
            )
            kwargs['_check_input_type'] = kwargs.get(
                '_check_input_type', True
            )
            kwargs['_check_return_type'] = kwargs.get(
                '_check_return_type', True
            )
            kwargs['_host_index'] = kwargs.get('_host_index')
            kwargs['document_type_code'] = \
                document_type_code
            return self.call_with_http_info(**kwargs)

        self.rawdb_documents_document_type_code_post = _Endpoint(
            settings={
                'response_type': ({str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)},),
                'auth': [
                    'AuthToken'
                ],
                'endpoint_path': '/api/v1/rawdb/documents/{document_type_code}/',
                'operation_id': 'rawdb_documents_document_type_code_post',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                    'document_type_code',
                    'rawdb_documents_post_request',
                ],
                'required': [
                    'document_type_code',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'document_type_code':
                        (str,),
                    'rawdb_documents_post_request':
                        (RawdbDocumentsPOSTRequest,),
                },
                'attribute_map': {
                    'document_type_code': 'document_type_code',
                },
                'location_map': {
                    'document_type_code': 'path',
                    'rawdb_documents_post_request': 'body',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [
                    'application/json',
                    'application/x-www-form-urlencoded',
                    'multipart/form-data'
                ]
            },
            api_client=api_client,
            callable=__rawdb_documents_document_type_code_post
        )

        def __rawdb_project_stats_project_id_get(
            self,
            project_id,
            **kwargs
        ):
            """rawdb_project_stats_project_id_get  # noqa: E501

            This method makes a synchronous HTTP request by default. To make an
            asynchronous HTTP request, please pass async_req=True

            >>> thread = api.rawdb_project_stats_project_id_get(project_id, async_req=True)
            >>> result = thread.get()

            Args:
                project_id (str):

            Keyword Args:
                _return_http_data_only (bool): response data without head status
                    code and headers. Default is True.
                _preload_content (bool): if False, the urllib3.HTTPResponse object
                    will be returned without reading/decoding response data.
                    Default is True.
                _request_timeout (float/tuple): timeout setting for this request. If one
                    number provided, it will be total request timeout. It can also
                    be a pair (tuple) of (connection, read) timeouts.
                    Default is None.
                _check_input_type (bool): specifies if type checking
                    should be done one the data sent to the server.
                    Default is True.
                _check_return_type (bool): specifies if type checking
                    should be done one the data received from the server.
                    Default is True.
                _host_index (int/None): specifies the index of the server
                    that we want to use.
                    Default is read from the configuration.
                async_req (bool): execute request asynchronously

            Returns:
                {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)}
                    If the method is called asynchronously, returns the request
                    thread.
            """
            kwargs['async_req'] = kwargs.get(
                'async_req', False
            )
            kwargs['_return_http_data_only'] = kwargs.get(
                '_return_http_data_only', True
            )
            kwargs['_preload_content'] = kwargs.get(
                '_preload_content', True
            )
            kwargs['_request_timeout'] = kwargs.get(
                '_request_timeout', None
            )
            kwargs['_check_input_type'] = kwargs.get(
                '_check_input_type', True
            )
            kwargs['_check_return_type'] = kwargs.get(
                '_check_return_type', True
            )
            kwargs['_host_index'] = kwargs.get('_host_index')
            kwargs['project_id'] = \
                project_id
            return self.call_with_http_info(**kwargs)

        self.rawdb_project_stats_project_id_get = _Endpoint(
            settings={
                'response_type': ({str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)},),
                'auth': [
                    'AuthToken'
                ],
                'endpoint_path': '/api/v1/rawdb/project_stats/{project_id}/',
                'operation_id': 'rawdb_project_stats_project_id_get',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'project_id',
                ],
                'required': [
                    'project_id',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'project_id':
                        (str,),
                },
                'attribute_map': {
                    'project_id': 'project_id',
                },
                'location_map': {
                    'project_id': 'path',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [],
            },
            api_client=api_client,
            callable=__rawdb_project_stats_project_id_get
        )

        def __rawdb_social_accounts_get(
            self,
            **kwargs
        ):
            """rawdb_social_accounts_get  # noqa: E501

            This method makes a synchronous HTTP request by default. To make an
            asynchronous HTTP request, please pass async_req=True

            >>> thread = api.rawdb_social_accounts_get(async_req=True)
            >>> result = thread.get()


            Keyword Args:
                _return_http_data_only (bool): response data without head status
                    code and headers. Default is True.
                _preload_content (bool): if False, the urllib3.HTTPResponse object
                    will be returned without reading/decoding response data.
                    Default is True.
                _request_timeout (float/tuple): timeout setting for this request. If one
                    number provided, it will be total request timeout. It can also
                    be a pair (tuple) of (connection, read) timeouts.
                    Default is None.
                _check_input_type (bool): specifies if type checking
                    should be done one the data sent to the server.
                    Default is True.
                _check_return_type (bool): specifies if type checking
                    should be done one the data received from the server.
                    Default is True.
                _host_index (int/None): specifies the index of the server
                    that we want to use.
                    Default is read from the configuration.
                async_req (bool): execute request asynchronously

            Returns:
                SocialAccountsResponse
                    If the method is called asynchronously, returns the request
                    thread.
            """
            kwargs['async_req'] = kwargs.get(
                'async_req', False
            )
            kwargs['_return_http_data_only'] = kwargs.get(
                '_return_http_data_only', True
            )
            kwargs['_preload_content'] = kwargs.get(
                '_preload_content', True
            )
            kwargs['_request_timeout'] = kwargs.get(
                '_request_timeout', None
            )
            kwargs['_check_input_type'] = kwargs.get(
                '_check_input_type', True
            )
            kwargs['_check_return_type'] = kwargs.get(
                '_check_return_type', True
            )
            kwargs['_host_index'] = kwargs.get('_host_index')
            return self.call_with_http_info(**kwargs)

        self.rawdb_social_accounts_get = _Endpoint(
            settings={
                'response_type': (SocialAccountsResponse,),
                'auth': [
                    'AuthToken'
                ],
                'endpoint_path': '/api/v1/rawdb/social_accounts/',
                'operation_id': 'rawdb_social_accounts_get',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                ],
                'required': [],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                },
                'attribute_map': {
                },
                'location_map': {
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [],
            },
            api_client=api_client,
            callable=__rawdb_social_accounts_get
        )