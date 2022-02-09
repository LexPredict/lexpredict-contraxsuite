import os
import uuid
from functools import lru_cache

import openapi_client
from openapi_client.api import document_api, project_api
from openapi_client.models import ProjectCreate, UploadSessionCreate

from utils import login


TUS_RESUMABLE = '1.0.0'
DOCUMENTS_ROOT_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')


@lru_cache(typed=True)
def get_document_type(code: str = None):
    """
    Get Document Type uid, the first non-generic by default, otherwise for the specified document type code.
    """
    auth_configuration = login()
    jq_filters = {
        "filterscount": "1",
        "filterdatafield0": "code",
        "filtervalue0": "generic",
        "filtercondition0": "DOES_NOT_CONTAIN",
    }
    if code:
        jq_filters['filtervalue0'] = code
        jq_filters['filtercondition0'] = 'CONTAINS'

    with openapi_client.ApiClient(auth_configuration) as api_client:
        api_instance = document_api.DocumentApi(api_client)
        resp = api_instance.document_document_types_get(jq_filters=jq_filters)
        assert isinstance(resp, dict)
        assert 'data' in resp
        assert len(resp['data']) > 0

        doc_type = resp['data'][0]
        return doc_type['uid'], doc_type['code']


def create_test_project(name: str = None, doc_type_uid: str = None):
    """
    Create test project of specified "name" and "doc_type_uid",
    Return its ID
    """
    auth_configuration = login()

    if not name:
        name = f'test-project-{uuid.uuid4()}'
    if not doc_type_uid:
        doc_type_uid, _ = get_document_type()

    with openapi_client.ApiClient(auth_configuration) as api_client:
        api_instance = project_api.ProjectApi(api_client)
        request_data = ProjectCreate(name=name, type=doc_type_uid)
        resp = api_instance.project_projects_post(project_create=request_data)

    assert isinstance(resp, ProjectCreate)
    assert resp['name'] == name

    # print(f'===> project #{resp["pk"]} created')
    return name, resp['pk']


def delete_test_project(project_id: int, full_clean=True):
    """
    Delete test project of specified ID
    """
    auth_configuration = login()
    if full_clean:
        with openapi_client.ApiClient(auth_configuration) as api_client:
            api_instance = project_api.ProjectApi(api_client)
            try:
                resp = api_instance.project_projects_id_cleanup_post(id=project_id, _preload_content=False)
                assert resp.status == 200
                # print(f'===> Task CleanupProject #{project_id} started')
            except Exception as e:
                assert e.status == 404
        return

    with openapi_client.ApiClient(auth_configuration) as api_client:
        api_instance = project_api.ProjectApi(api_client)
        try:
            resp = api_instance.project_projects_id_delete(id=project_id, _preload_content=False)
            assert resp.status == 204
            # print(f'===> project #{project_id} deleted')
        except Exception as e:
            assert e.status == 404


def create_test_upload_session(project_id: int, user_id: int = None, upload_files: dict = None):
    """
    Create test upload_session
    Return its UID
    """
    auth_configuration = login()
    if user_id is None:
        user_id = auth_configuration.user_id

    if upload_files is None:
        # dummy file
        upload_files = {f'{uuid.uuid4()}.txt': 100}

    with openapi_client.ApiClient(auth_configuration) as api_client:
        api_instance = project_api.ProjectApi(api_client)
        request_data = UploadSessionCreate(
            project=project_id,
            created_by=user_id,
            # upload_files=upload_files
        )
        resp = api_instance.project_upload_session_post(upload_session_create=request_data)
        assert isinstance(resp, UploadSessionCreate)
        return resp['uid']
