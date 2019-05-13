from django.conf import settings

from apps.document.constants import DOCUMENT_TYPE_CODE_GENERIC_DOCUMENT


def attach_proto(url: str) -> str:
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url
    return url


def root_url():
    frontend_root_url = settings.FRONTEND_ROOT_URL  # type: str
    if frontend_root_url:
        return attach_proto(frontend_root_url)
    else:
        backend_root_url = settings.HOST_NAME.strip('/') + '/' + settings.BASE_URL.strip('/')
        return attach_proto(backend_root_url)


def doc_editor_url(document_type_code, project_id, document_id) -> str:
    frontend_root_url = settings.FRONTEND_ROOT_URL  # type: str
    if frontend_root_url:
        if document_type_code == DOCUMENT_TYPE_CODE_GENERIC_DOCUMENT:
            return '{root_url}/#/batch_analysis/{project_id}/analysis/{document_id}' \
                .format(root_url=attach_proto(frontend_root_url), project_id=project_id, document_id=document_id)
        else:
            return '{root_url}/#/contract_analysis/{project_id}/annotator/{document_id}' \
                .format(root_url=attach_proto(frontend_root_url), project_id=project_id, document_id=document_id)
    else:
        backend_root_url = settings.HOST_NAME.strip('/') + '/' + settings.BASE_URL.strip('/')
        return '{root_url}/admin/document/document/{document_id}/change/' \
            .format(root_url=attach_proto(backend_root_url), document_id=document_id)
