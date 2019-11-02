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

import cgi
from typing import Dict, List, Tuple, Optional

import psycopg2
import pytds
import requests
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.deletion import CASCADE

from apps.common.log_utils import ProcessLogger
from apps.common.script_utils import exec_script
from apps.document.models import DocumentType, Document
from apps.project.models import Project
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.3.0/LICENSE"
__version__ = "1.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def search_request_params_default():
    return {'scope': 'US!6511311'}


class DocumentNotFoundAtIManage(Exception):
    pass


class IManageConfig(models.Model):
    code = models.CharField(max_length=1024, blank=False, null=False, db_index=True, unique=True)

    enabled = models.BooleanField(default=False, blank=False, null=False)

    root_url = models.CharField(max_length=1024, blank=False, null=False, help_text='''Root of the URL of iManage API 
        from the start and until (not including) "/api/v1" (eg. https://my_imanage.server.com)''')

    auth_user = models.CharField(max_length=100, blank=False, null=False)

    auth_password = models.CharField(max_length=100, blank=True, null=True)

    requests_proxies = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)

    requests_verify_ssl_certs = models.BooleanField(default=True, null=False, blank=False)

    document_type = models.ForeignKey(DocumentType, blank=False, null=False, help_text='''Type of documents on 
        Contraxsuite side to be created based on iManage documents.''', on_delete=CASCADE)

    project = models.ForeignKey(Project, blank=True, null=True, help_text='''Project into which the iManage documents
    should be saved.''', on_delete=CASCADE)

    project_resolving_code = models.TextField(blank=True, null=True, help_text='''Python code returning project 
    based on the provided iManage document data in the form of dict.''')

    assignee = models.ForeignKey(User, blank=True, null=True, help_text='''User to which the iManage documents 
    should be assigned.''', on_delete=CASCADE)

    assignee_resolving_code = models.TextField(blank=True, null=True, help_text='''Python code returning assignee user 
        based on the provided iManage document data in the form of dict.''')

    imanage_to_contraxsuite_field_binding = JSONField(encoder=DjangoJSONEncoder,
                                                      null=True, blank=True,
                                                      help_text='''JSON mapping of iManage field codes to Contraxsuite 
                                                      field codes. Example: { "custom1": "field_code_1" }''')

    last_sync_start = models.DateTimeField(null=True, blank=True)

    sync_frequency_minutes = models.PositiveIntegerField(default=120, null=False, blank=False)

    search_request_params = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder,
                                      default=search_request_params_default)

    class Meta:
        verbose_name = 'iManage config'
        verbose_name_plural = 'iManage configs'

    def __str__(self):
        return self.__class__.__name__ + ': ' + self.code

    @staticmethod
    def prepare_eval_locals(imanage_doc_data: Dict, log: ProcessLogger) -> Dict:
        return {
            'Project': Project,
            'User': User,
            'imanage_doc': imanage_doc_data,
            'psycopg2': psycopg2,
            'pytds': pytds,
            'log': log
        }

    def resolve_dst_project(self, imanage_doc_data: Dict, log: ProcessLogger) -> Project:
        if self.project:
            return self.project
        if not self.project_resolving_code:
            raise RuntimeError('Unable to resolve project for iManage document. Neither project nor project '
                               'resolving code are defined in iManage Config {0}'.format(self.code))

        eval_locals = self.prepare_eval_locals(imanage_doc_data, log)

        project = exec_script('project by iManage doc resolution', self.project_resolving_code, eval_locals)
        return project

    def resolve_assignee(self, imanage_doc_data: Dict, log: ProcessLogger) -> Optional[User]:
        if self.assignee:
            return self.assignee
        if not self.assignee_resolving_code:
            return None

        eval_locals = self.prepare_eval_locals(imanage_doc_data, log)
        assignee = exec_script('assignee by iManage doc resolution', self.assignee_resolving_code, eval_locals)
        return assignee

    def build_url(self, path: str):
        root_url = self.root_url
        return root_url.rstrip('/') + '/' + path.lstrip('/')

    def login(self) -> str:
        url = self.build_url('/api/v1/session/login')
        resp = requests.put(url,
                            json={'user_id': self.auth_user,
                                  'password': self.auth_password},
                            proxies=self.requests_proxies,
                            verify=self.requests_verify_ssl_certs)
        if resp.status_code != 200:
            raise Exception('Unable to login to iManage at {0}\nStatus code: {1}\nResponse text:\n{1}'
                            .format(url, resp.status_code, resp.text or resp.json()))
        r_imanage_auth = resp.json()
        return r_imanage_auth["X-Auth-Token"]

    def search_documents(self, auth_token: str, additional_params: Dict = None) -> List[Dict]:
        params = dict()
        if self.search_request_params:
            params.update(self.search_request_params)

        if additional_params:
            params.update(additional_params)

        resp = requests.get(self.build_url('/api/v1/documents/search'),
                            proxies=self.requests_proxies,
                            verify=self.requests_verify_ssl_certs,
                            headers={'X-Auth-Token': auth_token},
                            params=params).json()
        return resp['data']

    def load_document(self, auth_token: str, imanage_doc_id: str) -> Tuple[str, requests.Response]:
        resp = requests.get(self.build_url('/api/v1/documents/{doc_id}/download'.format(doc_id=imanage_doc_id)),
                            headers={'X-Auth-Token': auth_token},
                            proxies=self.requests_proxies,
                            verify=self.requests_verify_ssl_certs,
                            params={'latest': 1},
                            stream=True)
        if resp.status_code == 404:
            raise DocumentNotFoundAtIManage()
        content_disposition = resp.headers['Content-Disposition']
        value, params = cgi.parse_header(content_disposition)
        filename = params['filename']
        return filename, resp


class IManageDocument(models.Model):
    imanage_config = models.ForeignKey(IManageConfig, null=False, blank=False, on_delete=CASCADE)

    imanage_doc_id = models.CharField(max_length=1024, null=False, blank=False, db_index=True)

    imanage_doc_number = models.CharField(max_length=1024, null=True, blank=True, db_index=True)

    imanage_doc_data = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)

    document = models.ForeignKey(Document, null=True, blank=True, on_delete=CASCADE)

    last_sync_date = models.DateTimeField(null=True, blank=True)

    import_problem = models.BooleanField(null=False, blank=False, default=False)

    class Meta:
        unique_together = (("imanage_config", "imanage_doc_id"),)
        verbose_name = 'iManage document'
        verbose_name_plural = 'iManage documents'
        ordering = ('imanage_config', 'imanage_doc_id',)
