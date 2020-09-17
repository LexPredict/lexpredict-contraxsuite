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

import os
import tempfile
from contextlib import contextmanager
from typing import List, Tuple, Generator
from typing import Optional
from urllib.parse import quote, unquote
from xml.etree import ElementTree

import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth

from apps.common.file_storage.file_storage import ContraxsuiteFileStorage, UnableToReadFile
from apps.common.singleton import Singleton

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class WebDAVError(Exception):
    pass


@Singleton
class ContraxsuiteWebDAVFileStorage(ContraxsuiteFileStorage):
    """
    WebDAV-based file storage client.
    Reads/writes files from/to a WebDAV server running at the configured host/port.
    """

    def __init__(self,
                 root_url: str = '',
                 username: str = '',
                 password: str = '') -> None:
        super().__init__()
        self.root_url = root_url or \
                        settings.CONTRAX_FILE_STORAGE_WEBDAV_ROOT_URL.rstrip('/')
        self.auth = HTTPBasicAuth(username or settings.CONTRAX_FILE_STORAGE_WEBDAV_USERNAME,
                                  password or settings.CONTRAX_FILE_STORAGE_WEBDAV_PASSWORD)
        try:
            self.mkdir(self.documents_path)
        except:
            pass
        try:
            self.mkdir(self.export_path)
        except:
            pass

    def mkdir(self, path: str):
        url = self.sub_path_join(self.root_url, quote(path))
        if not url.endswith('/'):
            url = url + '/'
        resp = requests.request('MKCOL', url, auth=self.auth)
        if resp.status_code not in {200, 201}:
            msg = f'Unable to create dir at WebDAV storage: {url}\n' \
                f'Http status: {resp.status_code}\n' \
                f'Response:\n' \
                f'{resp.text}'
            raise Exception(msg)

    def write_file(self, path: str, contents_file_like_object, content_length: int = None):
        url = self.sub_path_join(self.root_url, quote(path))
        resp = requests.put(url, data=contents_file_like_object, auth=self.auth,
                            headers={'Content-Length': str(content_length)})
        if resp.status_code not in {200, 201}:
            msg = f'Unable to write data to WebDAV storage: {url}\n' \
                f'Http status: {resp.status_code}\n' \
                f'Response:\n' \
                f'{resp.text}'
            raise Exception(msg)

    @classmethod
    def parse_propfind_response(cls,
                                exclude_path: Optional[str],
                                propfind_xml: str) -> Generator[Tuple[str, bool], None, None]:
        # see tests/webdav_propfind_response_example.xml
        root = ElementTree.fromstring(propfind_xml)  # type: ElementTree.Element
        for response in root:  # type: ElementTree.Element
            href_elem = response.find('{DAV:}href')
            href = unquote(href_elem.text.strip('/'))
            if href == exclude_path:
                continue
            collection = response.find('{DAV:}propstat/{DAV:}prop/{DAV:}resourcetype/{DAV:}collection')
            is_dir = collection is not None
            yield href, is_dir

    def _exists(self, url: str) -> bool:
        r = requests.head(url, auth=self.auth)
        return r.status_code == 200

    def document_exists(self, rel_path: str):
        url = os.path.join(self.root_url, self.documents_path, rel_path.lstrip('/'))
        r = requests.head(url, auth=self.auth, allow_redirects=True)
        return r.status_code == 200

    def _list_impl(self, file_list: List[str], path: str):
        url = self.sub_path_join(self.root_url, quote(path))
        r = requests.request('PROPFIND', url, auth=self.auth, headers={'Depth': '1'})
        if r.status_code == 301:
            if path and not path.endswith('/'):
                self._list_impl(file_list, path + '/')
            return
        elif r.status_code == 404:
            return
        elif r.status_code != 207:
            raise WebDAVError('Unable to read file: {0}. Http status code: {1}. Http message: {2}'
                              .format(url, r.status_code, r.text))

        for fn, is_dir in self.parse_propfind_response(None, r.text):
            if is_dir:
                if fn != path:
                    self._list_impl(file_list, fn)
            else:
                file_list.append(fn)

    def list(self, rel_file_path: str = ''):
        file_list = []
        self._list_impl(file_list, rel_file_path)
        return file_list

    def delete_file(self, rel_file_path: str):
        """
        Delete files by full URI
        """
        url = self.sub_path_join(self.root_url, quote(rel_file_path))
        resp = requests.request('DELETE', url, auth=self.auth)
        if resp.status_code not in {200, 201, 204}:
            msg = f'Unable to delete file at WebDAV storage: {url}\n' \
                f'Http status: {resp.status_code}\n' \
                f'Response:\n' \
                f'{resp.text}'
            if resp.status_code == 404:
                raise FileNotFoundError(msg)
            else:
                raise Exception(msg)

    def rename_file(self, old_rel_path: str, new_rel_path: str):
        url = self.sub_path_join(self.root_url, quote(old_rel_path))
        dest_url = self.sub_path_join(self.root_url, quote(new_rel_path))
        resp = requests.request('MOVE',
                                url,
                                auth=self.auth,
                                headers={'Destination': dest_url})
        if resp.status_code not in {200, 201, 204}:
            msg = f'Unable to MOVE file at WebDAV storage: {old_rel_path} -> {new_rel_path}\n' \
                f'Http status: {resp.status_code}\n' \
                f'Response:\n' \
                f'{resp.text}'
            raise Exception(msg)

    @contextmanager
    def get_as_local_fn(self, rel_file_path: str):
        url = self.sub_path_join(self.root_url, quote(rel_file_path))
        r = requests.get(url, stream=True, auth=self.auth)
        if r.status_code != 200:
            raise UnableToReadFile('Unable to read file: {0}. Http status code: {1}. Http message: {2}'
                                   .format(url, r.status_code, r.text))

        _, ext = os.path.splitext(rel_file_path)
        _fd, fn = tempfile.mkstemp(suffix=ext)
        try:
            with open(fn, 'bw') as f:
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
            r.close()
            yield fn, rel_file_path
        finally:
            r.close()
            os.remove(fn)

    def read(self, rel_file_path: str) -> Optional[bytes]:
        url = self.sub_path_join(self.root_url, quote(rel_file_path))
        r = requests.get(url, stream=True, auth=self.auth)
        if r.status_code == 404:
            return None
        elif r.status_code != 200:
            raise WebDAVError('Unable to read file: {0}. Http status code: {1}. Http message: {2}'
                              .format(url, r.status_code, r.text))
        try:
            return r.content
        finally:
            r.close()

    def __str__(self):
        return f'{self.__class__.__name__}: {self.root_url}'
