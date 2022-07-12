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

import datetime
import regex as re
import os
import shutil
import tempfile
from contextlib import contextmanager
from typing import List, Tuple, Generator, Any, Dict, Optional, BinaryIO, Union
from urllib.parse import quote, unquote
from xml.etree import ElementTree

import requests
from django.conf import settings
from requests import Response
from requests.auth import HTTPBasicAuth
from django.core.files.storage import get_valid_filename

from apps.common.file_storage.file_storage import ContraxsuiteFileStorage, UnableToReadFile
from apps.common.singleton import Singleton

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
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
    RE_FILE_MODIFY_DATE = re.compile(r'(?<=<lp1:getlastmodified>)[^<]+(?=</lp1:getlastmodified>)', re.IGNORECASE)
    RE_FILE_SIZE = re.compile(r'(?<=<lp1:getcontentlength>)\d+', re.IGNORECASE)

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

    def write_file(self,
                   path: str,
                   contents_file_like_object: Union[BinaryIO, bytes],
                   content_length: int = None,
                   skip_existing: bool = False):
        url = self.sub_path_join(self.root_url, quote(path))
        if skip_existing:
            file_status = self.check_path(quote(path))
            if file_status['exists']:
                if file_status['is_folder']:
                    raise Exception(f'''WebDAV.write_file({path}): there is already a directory
                                        with the name of the file passed.''')
                return
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

    def check_path(self, rel_path: str) -> Dict[str, bool]:
        # returns: { 'exists': True, 'is_folder': True, 'not_empty': False }
        url = os.path.join(self.root_url, rel_path.lstrip('/'))
        r = requests.head(url, auth=self.auth, allow_redirects=True)
        if r.status_code != 200:
            return {
                'exists': False,
                'is_folder': False,
                'not_empty': False
            }

        r = requests.request('PROPFIND', url, auth=self.auth, headers={'Depth': '1'})

        is_folder, has_files = False, False
        rel_path = unquote(rel_path)
        for fn, is_dir in self.parse_propfind_response(None, r.text):
            if fn == rel_path:
                is_folder = is_dir
            else:
                has_files = True
                is_folder = True
                break

        return {
            'exists': True,
            'is_folder': is_folder,
            'not_empty': has_files
        }

    def document_exists(self, rel_path: str):
        url = os.path.join(self.root_url, self.documents_path, quote(rel_path.lstrip('/')))
        r = requests.head(url, auth=self.auth, allow_redirects=True)
        return r.status_code == 200

    def _list_impl(self, file_list: List[str], path: str):
        url = self.sub_path_join(self.root_url, quote(path))
        r = requests.request('PROPFIND', url, auth=self.auth, headers={'Depth': '1'})
        if r.status_code == 301:
            if path and not path.endswith('/'):
                self._list_impl(file_list, path + '/')
            return
        if r.status_code == 404:
            return
        if r.status_code != 207:
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
            raise Exception(msg)

    def file_info(self, rel_file_path: str):
        url = self.sub_path_join(self.root_url, quote(rel_file_path))
        resp = requests.request('PROPFIND', url, auth=self.auth)
        if not resp.ok:
            msg = f'Unable to get file info at WebDAV storage: {url}\n' \
                  f'Http status: {resp.status_code}\n' \
                  f'Response:\n' \
                  f'{resp.text}'
            if resp.status_code == 404:
                raise FileNotFoundError(msg)
            raise Exception(msg)

        date_matches = [i.group(0) for i in self.RE_FILE_MODIFY_DATE.finditer(resp.text)]
        if len(date_matches) != 1:
            raise Exception(f'No one / too many modify date entries found in response ({resp.text})')
        try:
            modify_date = datetime.datetime.strptime(date_matches[0], '%a, %d %b %Y %H:%M:%S %Z')
        except:
            raise Exception(f'Cannot convert "{date_matches[0]}" string to datetime')

        size_matches = [i.group(0) for i in self.RE_FILE_SIZE.finditer(resp.text)]
        if len(size_matches) != 1:
            raise Exception(f'No one / too many modify size entries found in response ({resp.text})')
        try:
            file_size = int(size_matches[0])
        except:
            raise Exception(f'Cannot convert "{size_matches[0]}" string to int')
        return {'date': modify_date, 'size': file_size}

    def rename_file(self,
                    old_rel_path: str,
                    new_rel_path: str,
                    move_file: bool = False):
        url = self.sub_path_join(self.root_url, quote(old_rel_path))
        dest_url = self.sub_path_join(self.root_url, quote(new_rel_path))
        resp = requests.request('MOVE',
                                url,
                                auth=self.auth,
                                headers={'Destination': dest_url})
        allowed_codes = {200, 201, 204}
        if move_file:
            allowed_codes.add(301)
        if resp.status_code not in allowed_codes:
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

        temp_dir = tempfile.mkdtemp()
        try:
            fn = os.path.join(temp_dir, get_valid_filename(os.path.basename(rel_file_path)))
            with open(fn, 'bw') as f:
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
            r.close()
            yield fn, rel_file_path
        finally:
            r.close()
            shutil.rmtree(temp_dir, ignore_errors=True)

    def read(self, rel_file_path: str) -> Optional[bytes]:
        url = self.sub_path_join(self.root_url, quote(rel_file_path))
        r = requests.get(url, stream=True, auth=self.auth)
        if r.status_code == 404:
            return None
        if r.status_code != 200:
            raise WebDAVError('Unable to read file: {0}. Http status code: {1}. Http message: {2}'
                              .format(url, r.status_code, r.text))
        try:
            return r.content
        finally:
            r.close()

    def get_request(self, rel_file_path: str,
                    extra_headers: Optional[Dict[str, Any]] = None) -> Optional[Response]:
        rel_file_path = self.sub_path_join(self.documents_path, rel_file_path)

        url = self.sub_path_join(self.root_url, quote(rel_file_path))
        r = requests.get(url, stream=True, auth=self.auth,
                         headers=extra_headers)
        if r.status_code == 404:
            return None
        if r.status_code < 200 or r.status_code > 299:
            raise WebDAVError('Unable to read file: {0}. Http status code: {1}. Http message: {2}'
                              .format(url, r.status_code, r.text))
        return r

    def __str__(self):
        return f'{self.__class__.__name__}: {self.root_url}'
