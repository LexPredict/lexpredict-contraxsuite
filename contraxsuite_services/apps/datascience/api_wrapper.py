"""
    Copyright (C) 2017, ContraxSuite, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    You can also be released from the requirements of the license by purchasing
    a commercial license from ContraxSuite, LLC. Buying such a license is
    mandatory as soon as you develop commercial activities involving ContraxSuite
    software without disclosing the source code of your own applications.  These
    activities include: offering paid services to customers as an ASP or "cloud"
    provider, processing documents on the fly in a web application,
    or shipping ContraxSuite within a closed source product.
"""
# -*- coding: utf-8 -*-

# standard-library imports
import io
import json
import time
import logging
import pathlib
import datetime
import operator
from abc import ABC
from urllib.parse import urljoin
from typing import Any, Callable, Dict, Generator

# third-party library imports
import requests
from tqdm import tqdm

# configuration

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


class _Router(ABC):
    """
    Provides generic REST methods. Implemented by ContraxSuiteAPIWrapper.
    """
    def get(
        self,
        endpoint: str,
        parameters: dict = None,
    ) -> requests.models.Response:
        """
        Args:
            endpoint (str): An API endpoint to query.
        
        Returns:
            requests.models.Response: The request response.
        """
        request_url = urljoin(self.fqdn, endpoint)
        logging.debug('GET from %s', request_url)
        return self.session.get(request_url, params=parameters)

    def post(
        self,
        endpoint: str,
        data: dict = None,
        json: dict = None,
        files: dict = None
    ) -> requests.models.Response:
        """
        Args:
            endpoint (str): An API endpoint to query.
            data (dict): Data to POST.
            files (dict): Files to POST.
        
        Returns:
            requests.models.Response: The request response.
        """
        request_url = urljoin(self.fqdn, endpoint)
        logging.debug('POST to %s with data=%s and files=%s', request_url, data, files)
        return self.session.post(request_url, data=data, json=json, files=files)
    
    def patch(
        self,
        endpoint: str,
        data: dict = None
    ) -> requests.models.Response:
        """
        Args:
            endpoint (str): An API endpoint to query.
            data (dict): Data to PATCH.
        
        Returns:
            requests.models.Response: The request response.
        """
        logging.warn('PATCH methods have not been fully tested.')
        request_url = urljoin(self.fqdn, endpoint)
        logging.debug('PATCH to %s with data=%s', request_url, data)
        return self.session.patch(request_url, data=data)

    def put(
        self,
        endpoint: str,
        data: dict = None
    ) -> requests.models.Response:
        """
        Args:
            endpoint (str): An API endpoint to query.
            data (dict): Data to PUT.
        
        Returns:
            requests.models.Response: The request response.
        """
        logging.warn('PUT methods have not been fully tested.')
        request_url = urljoin(self.fqdn, endpoint)
        logging.debug('PUT to %s with data=%s', request_url, data)
        return self.session.put(request_url, data=data)
        
    def delete(
        self,
        endpoint: str
    ) -> requests.models.Response:
        """
        Args:
            endpoint (str): An API endpoint to query.
        
        Returns:
            requests.models.Response: The request response.
        """
        logging.warn('DELETE methods have not been fully tested.')
        request_url = urljoin(self.fqdn, endpoint)
        logging.debug('DELETE from %s with data=%s', request_url)
        return self.session.delete(request_url)    


class ContraxSuiteAPIWrapper(_Router):
    """
    Args:
        fqdn (str): A ContraxSuite URL, complete with https://
        username (str): A ContraxSuite username.
        password (str): The username's password.
    
    To-Dos:
        * add logging destination parameter
        * add FQDN validation using urllib.parse
    """

    def __init__(self, fqdn: str, username: str, password: str):
        _subclasses: dict = self._subclass_container()
        self.__dict__.update(**_subclasses)
        del _subclasses
        self.fqdn: str = fqdn
        self.session = requests.Session()
        self._login(username, password)
        self.username: str = username
        self.user_id: str = self._get_me()['id']
        logging.info('Not every endpoint under /api/app has been implemented.')
    
    def _login(
        self,
        username: str,
        password: str
    ) -> requests.models.Response:
        url = 'rest-auth/login/'
        auth = {'username': username, 'password': password}
        response = self.post(url, auth)
        logging.info(response)
        return response

    def _get_me(self) -> dict:
        """
        Get the current user.
        
        Returns:
            dict: This user.
        """
        users = self.users.get_users().json()
        return next(filter(lambda user: user['username'] == self.username, users))
    
    def upload_documents_from_path(
        self,
        project_id: int,
        path: str
    ) -> requests.models.Response:
        """
        Recursively uploads documents from a path to a project.
        
        Args:
            project_id (int): The project ID.
            path (str): A path to the root of files to upload.
            
        Returns:
            requests.models.Response: The request response.
        """
        upload_session = self._create_upload_session(project_id)
        upload_session_id = upload_session.json()['uid']
        path = pathlib.Path(path)
        files = [fp for fp in path.glob('**/*') if fp.is_file()]
        for fp in tqdm(files, total=len(files), desc='UPLOADING', unit='doc'):
            r_upload_document = self.upload_document(
                upload_session_id=upload_session_id,
                file=open(fp, 'rb'),
                # TODO: check if this needs to be cast as a string or if this is redundant
                directory_path=str(fp.relative_to(path))
            )
            logging.debug(r_upload_document.status_code)
        return self._monitor_progress(upload_session_id)
   
    def _create_upload_session(
        self,
        project_id: int,
    ) -> requests.models.Response:
        """
        Creates an upload session.
        
        Args:
            project_id (int): The project ID.
       
        Returns:
            requests.models.Response: The request response.
        """
        self.session.headers.update({'Content-Type': 'application/json'})
        data = json.dumps({'project': project_id, 'created_by': self.user_id})
        return self.post('api/v1/project/upload-session/', data=data)
                
    def upload_document(
        self,
        upload_session_id: str,
        file: io.BufferedReader,
        **kwargs
    ) -> requests.models.Response:
        """
        Uploads a specific document.
        
        Args:
            upload_session_id (str): An upload session UID.
            file (io.BufferedReader): The file to upload.
        
        Kwargs:
            directory_path: Sets the Document folder path.
        
        Returns:
            requests.models.Response: The request response.
        """
        try:
            del self.session.headers['Content-Type']
        except KeyError as key_error:
            logging.debug('%s', key_error)
        logging.debug('Uploading: %s', file)
        logging.debug(self.session.headers)
        return self.post(
            f'api/v1/project/upload-session/{upload_session_id}/upload/',
            data={'send_email_notifications': 'false', **kwargs},
            files={'file': file}
        )
    
    def _monitor_progress(
        self,
        upload_session_id: str,
        check_freq: int = 5
    ) -> requests.models.Response:
        """
        Monitors the status of an upload session.
        
        Args:
            upload_session_id (str): An upload session UID.
            
        Returns:
            requests.models.Response: The upload session progress response.
        """
        with tqdm(total=100, desc='PARSING', unit='doc') as progress_bar:
            while True:
                r_progress = self.get(f'api/v1/project/upload-session/{upload_session_id}/progress/')
                data = r_progress.json()
                percent_complete = data['document_tasks_progress_total']
                progress_bar.update(int(percent_complete) - progress_bar.n)
                if r_progress.status_code != 200:
                    logging.info('%i %% complete.', int(percent_complete))
                    logging.error('HTTP Status Error: code %i', r_progress.status_code)
                    return r_progress
                elif not data['document_tasks_progress']:
                    logging.info('%i %% complete.', int(percent_complete))
                    logging.info('No document tasks')
                    return r_progress
                elif data['document_tasks_progress_total'] >= 100:
                    logging.info('%i %% complete.', int(percent_complete))
                    return r_progress
                else:
                    time.sleep(check_freq)

    def _subclass_container(self) -> Dict[str, Callable]:
        """
        This allows for emulation of package-style function compartmentalization in a single-module Python file.

        Returns:
            Dict[str, Callable]: A dictionary mapping class names to subclasses.
        """
        _parent_class = self

        class _Subclass(ABC):
            """
            This provides __init__ and __new__ methods for inheritence.
            """
            def __init__(self):
                self._parent_class = _parent_class

            def __new__(cls, *args, **kwargs):
                raise RuntimeError(f'{cls} should not be instantiated.')

        class _Analyze(_Subclass):
            """
            For API endpoints available under `api/v1/analyze/`.
            """
            @staticmethod
            def get_document_clusters(document_cluster_id: int = None) -> requests.models.Response:
                """
                Args: 
                    document_cluster_id (str): Optional. A document cluster's ID.
                        * If provided, then this method gets a singular document cluster.
                        * If ommitted, then this method gets the entire document cluster list.

                Returns:
                    requests.models.Response: The request response.
                """
                return self.get(f'api/v1/analyze/document-cluster/{document_cluster_id or ""}/')

            @staticmethod
            def put_rename_document_cluster(document_cluster_id: int, name: str) -> requests.models.Response:
                """
                Args: 
                    document_cluster_id (str): A document cluster's ID.
                    name (str): A name for the document cluster.

                Returns:
                    requests.models.Response: The request response.
                """
                logging.warning('This method has not been fully tested.')
                return self.put(f'api/v1/analyze/document-cluster/{document_cluster_id}/', data={'name': name})

            @staticmethod
            def patch_rename_document_cluster(document_cluster_id: int, name: str) -> requests.models.Response:
                """
                Args:
                    document_cluster_id (str): A document cluster's ID.
                    name (str): A name for the document cluster.

                Returns:
                    requests.models.Response: The request response.
                """
                logging.warning('This method has not been fully tested.')
                return self.patch(f'api/v1/analyze/document-cluster/{document_cluster_id}/', data={'name': name})

            @staticmethod
            def get_document_similarity() -> requests.models.Response:
                """
                Returns:
                    requests.models.Response: The request response.
                """
                return self.get('api/v1/analyze/document-similarity/list/')
            
            @staticmethod
            def get_party_similarity() -> requests.models.Response:
                """
                Returns:
                    requests.models.Response: The request response.                
                """
                return self.get('api/v1/analyze/party-similarity/list/')

            @staticmethod
            def get_textunit_similarity() -> requests.models.Response:
                """
                Returns:
                    requests.models.Response: The request response.                
                """
                return self.get('api/v1/analyze/text-unit-similarity/list/')

            @staticmethod
            def get_textunit_clusters() -> requests.models.Response:
                """
                Gets a list of all TextUnit clusters.

                Returns:
                    requests.models.Response: The request response.                
                """
                return self.get('api/v1/analyze/text-unit-cluster/list/')

            @staticmethod
            def post_textunit_classification(
                text_unit_id: int,
                class_name: str,
                class_value: str
            ) -> requests.models.Response:
                """
                Args:
                    text_unit_id (int): The TextUnit's ID.
                    class_name (str): Type of classification.
                    class_value (str): Classification value.
                
                Returns:
                    requests.models.Response: The request response.
                """
                return self.post('api/v1/analyze/text-unit-classifications/',
                    data={
                        'class_name': class_name,
                        'class_value': class_value,
                        'text_unit_id': text_unit_id
                    }
                )

            @staticmethod
            def get_textunit_classifications(text_unit_classification_id: int = None) -> requests.models.Response:
                """
                Retrieves all TextUnitClassifications or a specific TextUnitClassification.

                Args:
                    text_unit_classification_id (int): The TextUnitClassification's ID.

                Returns:
                    requests.models.Response: The request response.                
                """
                return self.get(f'api/v1/analyze/text-unit-classifications/{text_unit_classification_id or ""}')

            @staticmethod
            def delete_textunit_classification(text_unit_classification_id: int) -> requests.models.Response:
                """
                Removes a TextUnitClassification.

                Args:
                    text_unit_classification_id (int): The TextUnitClassification's ID.

                Returns:
                    requests.models.Response: The request response.                
                """
                return self.delete(f'api/v1/analyze/text-unit-classifications/{text_unit_classification_id}/')

            @staticmethod
            def get_textunit_classifier_suggestions(text_unit_classifier_suggestion_id: int = None) -> requests.models.Response:
                """
                Retrieves all TextUnitClassifierSuggestions or a specific TextUnitClassifierSuggestion.

                Args:
                    text_unit_classifier_suggestion_id (int): The TextUnitClassifierSuggestion's ID.

                Returns:
                    requests.models.Response: The request response.                
                """
                return self.get(f'api/v1/analyze/text-unit-classifier-suggestions/{text_unit_classifier_suggestion_id or ""}')

            @staticmethod
            def delete_textunit_classifier_suggestion(text_unit_classifier_suggestion_id: int) -> requests.models.Response:
                """
                Removes a TextUnitClassifierSuggestion.

                Args:
                    text_unit_classifier_suggestion_id (int): The TextUnitClassifierSuggestion's ID.

                Returns:
                    requests.models.Response: The request response.                
                """
                return self.delete(f'api/v1/analyze/text-unit-classifier-suggestions/{text_unit_classifier_suggestion_id}/')

            @staticmethod
            def get_textunit_classifiers(text_unit_classifier_id: int = None) -> requests.models.Response:
                """
                Retrieves all TextUnitClassifiers or a specific TextUnitClassifier.

                Args:
                    text_unit_classifier_id (int): The TextUnitClassifier's ID.

                Returns:
                    requests.models.Response: The request response.                
                """
                return self.get(f'api/v1/analyze/text-unit-classifiers/{text_unit_classifier_id or ""}')

            @staticmethod
            def delete_textunit_classifier(text_unit_classifier_id: int) -> requests.models.Response:
                """
                Removes a TextUnitClassifier.

                Args:
                    text_unit_classifier_id (int): The TextUnitClassifier's ID.

                Returns:
                    requests.models.Response: The request response.                
                """
                return self.delete(f'api/v1/analyze/text-unit-classifiers/{text_unit_classifier_id}/')

        class _Document(_Subclass):
            """
            For API endpoints available under `api/v1/document/`.
            """
            @staticmethod
            def get_document_types(document_type_uid: str) -> requests.models.Response:
                """
                Args:
                    document_type_uid (str): The DocumentType UID.

                Returns:
                    requests.models.Response: The request response.                
                """
                return self.get(f'api/v1/document/document-types/{document_type_uid}/')

            @staticmethod
            def get_documents(document_id: int = None) -> requests.models.Response:
                """
                Args:
                    document_type_uid (str): A document's ID.

                Returns:
                    requests.models.Response: The request response.
                """
                return self.get(f'api/v1/document/documents/{document_id or ""}/')

            @staticmethod
            def get_field_schemas(document_type_uid: str) -> requests.models.Response:
                """
                Args:
                    document_type_uid (str): The DocumentType UID.

                Returns:
                    requests.models.Response: The request response.
                """
                return self.get(f'api/v1/document/document-types/{document_type_uid}/')

        class _Extract(_Subclass):
            """
            For API endpoints available under `api/v1/users/`.
            """
            @staticmethod
            def get_usage(thing: str, top: bool = True) -> requests.models.Response:
                """
                Args:
                    document_type_uid (str): The DocumentType UID.
                Returns:
                    requests.models.Response: The request response.
                """
                _top = 'top/' if top else ''
                return self.get(f'api/v1/extract/{thing}-usage/{_top}')

        class _Users(_Subclass):
            """
            For API endpoints available under `api/v1/users/`.
            """
            @staticmethod
            def get_users(user_id: int = None) -> requests.models.Response:
                """
                Get a specific user or all users.
                
                Args:
                    user_id (int) (optional): The ID number of a specific user.

                Returns:
                    requests.models.Response: The request response.
                """
                return self.get(f'api/v1/users/users/{user_id or ""}/')

            @staticmethod
            def get_roles(role_id: int = None) -> requests.models.Response:
                """
                Get a specific role or all roles.
                
                Args:
                    role_id (int) (optional): The ID number of a specific role.

                Returns:
                    requests.models.Response: The request response.
                """
                return self.get(f'api/v1/users/roles/{role_id or ""}')
                
        class _Project(_Subclass):
            """
            For API endpoints available under `api/v1/project/`.
            """
            @staticmethod
            def post_upload_session(project_id: int) -> requests.models.Response:
                """
                Creates an upload session.

                Args:
                    project_id (int): The project ID.

                Returns:
                    requests.models.Response: The request response.
                """
                json = {'project': project_id, 'created_by': self.user_id}
                return self.post('api/v1/project/upload-session/', json=json)

            @staticmethod
            def get_upload_session_list() -> requests.models.Response:
                """
                Returns:
                    requests.models.Response: The request response.
                """
                return self.get('api/v1/project/upload-session/')
            
            @staticmethod
            def get_upload_session_statuses() -> requests.models.Response:
                """
                To-Do:
                    * can this be filtered?

                Returns:
                    requests.models.Response: The request response.
                """
                return self.get('api/v1/project/upload-session/status/')

            @staticmethod
            def get_upload_session(upload_session_uid: str) -> requests.models.Response:
                """
                Gets an upload session by its UID.
                
                Args:
                    upload_session_uid (str): An upload session's UID.
                
                Returns:
                    requests.models.Response: The request response.
                """
                return self.get(f'api/v1/project/upload-session/{upload_session_uid}/')

            @staticmethod
            def get_project(project_id: int) -> requests.models.Response:
                """
                Gets a specific project.

                Args:
                    project_id (int): The project ID.

                Returns:
                    requests.models.Response: The request response.
                """
                return self.get(f'api/v1/project/projects/{project_id}/')

            @staticmethod
            def post_create_project(
                name: str,
                description: str,
                type: str,
                send_email_notification: bool
            ) -> requests.models.Response:
                """
                """
                data = {
                    'name': name,
                    'description': description,
                    'type': type,
                    'send_email_notification': send_email_notification
                }
                return self.post('/api/v1/project/projects/', data=data)

        class _RawDB(_Subclass):
            """
            For API endpoints available under `api/v1/rawdb/`.
            """
            @staticmethod
            def get_rawdb_document_information(
                document_type_code: str,
                parameters: Dict[str, str] = None
            ) -> requests.models.Response:
                """
                Args:
                    document_type_code (str): DocumentType code.

                Returns:
                    requests.models.Response: The request response.
                
                Example parameters:
                    ```
                    params = {
                        'columns': 'document_id,document_name,calculated_term',
                        'order_by': 'calculated_term:desc'
                    }
                    ```
                """
                logging.warn('Rename this method...')
                return self.get(f'api/v1/rawdb/documents/{document_type_code}/', parameters=parameters)

            @staticmethod
            def get_project_stats(project_id: int) -> requests.models.Response:
                """
                Args:
                    project_id (int): The project ID.

                Returns:
                    requests.models.Response: The request response.
                """
                return self.get(f'api/v1/rawdb/project_stats/{project_id}/')

            @staticmethod
            def get_documents(
                document_type_code: str,
                parameters: dict = None
            ) -> requests.models.Response:
                """
                """
                return self.get(f'api/v1/rawdb/documents/{document_type_code}/', parameters)
        
        class _Task(_Subclass):
            """
            For API endpoints available under `api/v1/task/`.
            """
            @staticmethod
            def get_tasks(task_id: str = None) -> requests.models.Response:
                """
                Args: 
                    task_id (str): Optional. A task's UUID.
                        * If provided, then this method gets a singular task.
                        * If ommitted, then this method gets the entire task list.

                Returns:
                    requests.models.Response: The request response.
                """
                return self.get(f'api/v1/task/tasks/{task_id or ""}')
            
            @staticmethod
            def post_purge_task(task_id: str) -> requests.models.Response:
                """
                Args: 
                    task_id (str): A task's UUID.
    
                Returns:
                    requests.models.Response: The request response.
                """
                return self.post('api/v1/task/purge-task/', data={'task_pk': task_id})

            @staticmethod
            def get_tasks_conditionally(**kwargs) -> Generator[str, None, None]:
                """
                Kwargs:
                    pk (str): Task UID.
                    name (str): Task type name.
                    date_start (str): A datetime string, fomatted like '2020-05-01T07:52:30'.
                    date_work_start (str): A datetime string, fomatted like '2020-05-01T07:52:30'.
                    date_done (str): A datetime string, fomatted like '2020-05-01T07:52:30'.
                    duration (float):
                    progress (int): Percentage complete.
                    status (str): SUCCESS, PENDING, or FAILURE
                    has_error (bool): Whether or not the task has logged an error.
                    description (str):
                """
                def _timestamp_to_datetime(timestamp: str) -> datetime.datetime:
                    """

                    """
                    try:
                        dt = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%X.%fZ')
                    except ValueError as valueerror_1:
                        try:
                            dt = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%X')
                        except ValueError as valueerror_2:
                            dt = datetime.datetime.strptime(timestamp, '%Y-%m-%d')
                    return dt

                def _normalize_dates(dictionary: dict) -> Dict[str, Any]:
                    """
                    """
                    normalized = dict()
                    for k, v in dictionary.items():
                        if 'date_' in k:
                            if isinstance(v, str):
                                normalized[k] = _timestamp_to_datetime(v)
                            elif isinstance(v, dict):
                                normalized[k] = dict()
                                for op, ts in v.items():
                                    normalized[k][op] = _timestamp_to_datetime(ts)
                            elif isinstance(v, datetime.datetime):
                                normalized[k] = v
                            else:
                                raise ValueError(f'Cannot convert timestamp {v} to datetime object (type: {type(v)}).')
                        else:
                            normalized[k] = v
                    return normalized

                def _kwarg_comparator(task: dict, **kwargs) -> str:
                    """
                    Inplace.

                    task: Dict[str, Any]

                    """
                    task = _normalize_dates(task)    
                    conditions = []
                    for k, v in task.items():
                        query = kwargs.get(k)
                        if query:
                            conditions.extend(
                                [
                                    getattr(operator, qk)(v, qv)
                                    for qk, qv in query.items()
                                ]
                            )
                    if conditions and all(conditions):
                        return task['pk']

                logging.warning('This method is experimental.')
                r_all_tasks = self.task.get_tasks()
                all_tasks_json = r_all_tasks.json()
                kwargs = _normalize_dates(kwargs)
                for task in all_tasks_json:
                    task_id = _kwarg_comparator(task, **kwargs)
                    if task_id:
                        yield task_id

            @staticmethod
            def clear_tasks_conditionally(**kwargs) -> Generator[requests.models.Response, None, None]:
                """
                Kwargs:
                    pk (str): Task UID.
                    name (str): Task type name.
                    date_start (str): A datetime string, fomatted like '2020-05-01T07:52:30'.
                    date_work_start (str): A datetime string, fomatted like '2020-05-01T07:52:30'.
                    date_done (str): A datetime string, fomatted like '2020-05-01T07:52:30'.
                    duration (float):
                    progress (int): Percentage complete.
                    status (str): SUCCESS, PENDING, or FAILURE
                    has_error (bool): Whether or not the task has logged an error.
                    description (str):
    
                Returns:
                    (Generator) requests.models.Response: The request responses.
                """
                for task_id in self.task.get_tasks_conditionally(**kwargs):
                    yield self.task.post_purge_task(task_id)

        return {
            'analyze': _Analyze,
            'document': _Document,
            'extract': _Extract,
            'users': _Users,
            'project': _Project,
            'rawdb': _RawDB,
            'task': _Task,
        }
