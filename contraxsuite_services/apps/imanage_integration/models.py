import cgi
from typing import Dict, List, Tuple, Optional

import psycopg2
import pytds
import requests
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from apps.common.script_utils import exec_script
from apps.document.models import DocumentType, Document
from apps.project.models import Project
from apps.users.models import User


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
        Contraxsuite side to be created based on iManage documents.''')

    project = models.ForeignKey(Project, blank=True, null=True, help_text='''Project into which the imanage documents
    should be saved.''')

    project_resolving_code = models.TextField(blank=True, null=True, help_text='''Python code returning project 
    based on the provided iManage document data in the form of dict.''')

    assignee = models.ForeignKey(User, blank=True, null=True, help_text='''User to which the imanage documents 
    should be assigned.''')

    assignee_resolving_code = models.TextField(blank=True, null=True, help_text='''Python code returning assignee user 
        based on the provided iManage document data in the form of dict.''')

    last_sync_start = models.DateTimeField(null=True, blank=True)

    sync_frequency_minutes = models.PositiveIntegerField(default=120, null=False, blank=False)

    search_request_params = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder, default={'scope': 'US!6511311'})

    class Meta:
        verbose_name = 'iManage config'
        verbose_name_plural = 'iManage configs'

    def __str__(self):
        return self.__class__.__name__ + ': ' + self.code

    @staticmethod
    def prepare_eval_locals(imanage_doc_data: Dict) -> Dict:
        return {
            'Project': Project,
            'User': User,
            'imanage_doc': imanage_doc_data,
            'psycopg2': psycopg2,
            'pytds': pytds
        }

    def resolve_dst_project(self, imanage_doc_data: Dict) -> Project:
        if self.project:
            return self.project
        if not self.project_resolving_code:
            raise RuntimeError('Unable to resolve project for iManage document. Neither project nor project '
                               'resolving code are defined in iManage Config {0}'.format(self.code))

        eval_locals = self.prepare_eval_locals(imanage_doc_data)

        project = exec_script('project by iManage doc resolution', self.project_resolving_code, eval_locals)
        return project

    def resolve_assignee(self, imanage_doc_data: Dict) -> Optional[User]:
        if self.assignee:
            return self.assignee
        if not self.assignee_resolving_code:
            return None

        eval_locals = self.prepare_eval_locals(imanage_doc_data)
        assignee = exec_script('assignee by iManage doc resolution', self.assignee_resolving_code, eval_locals)
        return assignee

    def build_url(self, path: str):
        root_url = self.root_url
        return root_url.rstrip('/') + '/' + path.lstrip('/')

    def login(self) -> str:
        r_imanage_auth = requests.put(self.build_url('/api/v1/session/login'),
                                      json={'user_id': self.auth_user,
                                            'password': self.auth_password},
                                      proxies=self.requests_proxies,
                                      verify=self.requests_verify_ssl_certs).json()
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
        content_disposition = resp.headers['Content-Disposition']
        value, params = cgi.parse_header(content_disposition)
        filename = params['filename']
        return filename, resp


class IManageDocument(models.Model):
    imanage_config = models.ForeignKey(IManageConfig, null=False, blank=False)

    imanage_doc_id = models.CharField(max_length=1024, null=False, blank=False, db_index=True)

    imanage_doc_number = models.CharField(max_length=1024, null=True, blank=True, db_index=True)

    imanage_doc_data = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)

    document = models.ForeignKey(Document, null=True, blank=True)

    last_sync_date = models.DateTimeField(null=True, blank=True)

    import_problem = models.BooleanField(null=False, blank=False, default=False)

    class Meta:
        unique_together = (("imanage_config", "imanage_doc_id"),)
        verbose_name = 'iManage document'
        verbose_name_plural = 'iManage documents'
        ordering = ('imanage_config', 'imanage_doc_id',)
