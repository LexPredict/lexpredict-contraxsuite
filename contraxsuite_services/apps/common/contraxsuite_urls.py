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

from django.conf import settings

from apps.document.constants import DOCUMENT_TYPE_CODE_GENERIC_DOCUMENT

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def attach_proto(url: str) -> str:
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url
    return url


def root_url():
    frontend_root_url = settings.FRONTEND_ROOT_URL  # type: str
    if frontend_root_url:
        return attach_proto(frontend_root_url)
    backend_root_url = settings.HOST_NAME.strip('/') + '/' + settings.BASE_URL.strip('/')
    return attach_proto(backend_root_url)


def doc_editor_url(document_type_code: str, project_id: int, document_id: int) -> str:
    """
    Returns URL to document in frontend in annotation mode
    if settings.FRONTEND_ROOT_URL is set up or an admin GUI
    reference to the document
    :param document_id: id of Document entity
    :param document_type_code: like 'lease.LeaseDocument'
    :param project_id: id or Project entity
    :return: http://192.168.31.198:8080/#/contract_analysis/62/annotator/442
    """
    frontend_root_url = settings.FRONTEND_ROOT_URL  # type: str
    if frontend_root_url:
        if document_type_code == DOCUMENT_TYPE_CODE_GENERIC_DOCUMENT:
            return '{root_url}/#/batch_analysis/{project_id}/analysis/{document_id}' \
                .format(root_url=attach_proto(frontend_root_url), project_id=project_id, document_id=document_id)
        else:
            return '{root_url}/#/contract_analysis/{project_id}/annotator/{document_id}' \
                .format(root_url=attach_proto(frontend_root_url), project_id=project_id, document_id=document_id)
    backend_root_url = settings.HOST_NAME.strip('/') + '/' + settings.BASE_URL.strip('/')
    return '{root_url}/admin/document/document/{document_id}/change/' \
        .format(root_url=attach_proto(backend_root_url), document_id=document_id)


def project_documents_url(document_type_code: str, project_id: int) -> str:
    """
    Returns URL to project in frontend (a list of project's documents)
    if settings.FRONTEND_ROOT_URL is set up
    :param document_type_code: like 'lease.LeaseDocument'
    :param project_id: id or Project entity
    :return: http://192.168.31.198:8080/#/contract_analysis/62
    """
    frontend_root_url = settings.FRONTEND_ROOT_URL  # type: str
    if frontend_root_url:
        if document_type_code == DOCUMENT_TYPE_CODE_GENERIC_DOCUMENT:
            return '{root_url}/#/batch_analysis/{project_id}/' \
                .format(root_url=attach_proto(frontend_root_url), project_id=project_id)
        else:
            return '{root_url}/#/contract_analysis/{project_id}/' \
                .format(root_url=attach_proto(frontend_root_url), project_id=project_id)
    # backend URL doesnt make sense here
    return '#'
