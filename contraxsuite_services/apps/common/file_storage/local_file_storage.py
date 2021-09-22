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
import time
from contextlib import contextmanager
from typing import List, Any, Dict
from typing import Optional, BinaryIO

import magic
import requests
from django.conf import settings
from requests import Response

from apps.common.file_storage.file_storage import ContraxsuiteFileStorage
from apps.common.file_storage.local_file_adapter import LocalFileAdapter
from apps.common.singleton import Singleton
from apps.common.streaming_utils import copy_data

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class ContraxsuiteInstanceLocalFileStorage(ContraxsuiteFileStorage):
    """
    Implementation of the file storage working in a local folder.
    Intended for usage during the development process to avoid having WebDAV server started on the developer machine.
    Also in future may be used for fast switching to distributed file systems.

    ContraxsuiteLocalFileStorage inherits this class and make it a Singleton,
    thus ContraxsuiteLocalFileStorage becomes a "sealed" class.
    """

    def __init__(self) -> None:
        super().__init__()
        self.root_dir = settings.CONTRAX_FILE_STORAGE_LOCAL_ROOT_DIR
        self.init_basic_folders()

    def init_basic_folders(self):
        try:
            self.mkdir(self.documents_path)
        except:
            pass
        try:
            self.mkdir(self.export_path)
        except:
            pass

    @classmethod
    def sub_path_join(cls, parent_path: str, relative_path: str) -> str:
        res = super().sub_path_join(parent_path, relative_path)

        # if path separator is not "/" (old Windows OS or something like that) then replace "/" with the proper one
        if os.path.sep != '/':
            return os.path.join(*res.split('/'))
        return res

    @classmethod
    def get_parent_path(cls, child_path: str):
        return os.path.sep.join(child_path.strip(os.path.sep).split(os.path.sep)[:-1])

    def mkdir(self, rel_path: str):
        path = os.path.join(self.root_dir, rel_path)
        os.mkdir(path)

    def write_file(self,
                   rel_file_path: str,
                   contents_file_like_object: BinaryIO,
                   content_length: int = None,
                   skip_existing: bool = False):
        path = os.path.join(self.root_dir, rel_file_path)
        if skip_existing and os.path.isfile(path):
            return
        with open(path, 'wb') as dst_f:
            copy_data(contents_file_like_object, dst_f)

    def check_path(self, rel_path: str) -> Dict[str, bool]:
        # returns: { 'exists': True, 'is_folder': True, 'not_empty': False }
        path = os.path.join(self.root_dir, rel_path)
        if not os.path.exists(path):
            return {
                'exists': False,
                'is_folder': False,
                'not_empty': False
            }
        if not os.path.isdir(path):
            return {
                'exists': True,
                'is_folder': False,
                'not_empty': False
            }
        has_files = False
        for _f in os.listdir(path):
            has_files = True
            break

        return {
            'exists': True,
            'is_folder': True,
            'not_empty': has_files
        }

    def document_exists(self, rel_path: str):
        abs_path = os.path.join(self.root_dir, self.documents_path, rel_path.lstrip('/'))
        return os.path.exists(abs_path)

    def list(self, rel_file_path: str) -> List[str]:
        file_list = []
        full_path = os.path.join(self.root_dir, rel_file_path)

        if os.path.isfile(full_path):
            file_list.append(rel_file_path)
        else:
            for root, _, files in os.walk(full_path):
                for filename in files:
                    file_list.append(os.path.relpath(os.path.join(root, filename), self.root_dir))
        return file_list

    def delete_file(self, rel_file_path: str):
        """
        Delete files by absolute path in file system
        """
        file_path = os.path.join(self.root_dir, rel_file_path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'LocalFileStorage.delete_file(): file "{rel_file_path}"' +
                                    f' (mapped on "{file_path}") is not found')
        os.remove(file_path)

    def file_info(self, rel_file_path: str):
        file_path = os.path.join(self.root_dir, rel_file_path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'LocalFileStorage.file_info(): file "{rel_file_path}"' +
                                    f' (mapped on "{file_path}") is not found')
        return {
            'size': os.path.getsize(file_path),
            'date': time.ctime(os.path.getmtime(file_path))
        }

    def rename_file(self, old_rel_path: str, new_rel_path: str, move_file: bool = False):
        """
        Rename files by absolute path (file system) or full URI
        """
        old_path = os.path.join(self.root_dir, old_rel_path)
        if not os.path.exists(old_path):
            raise FileNotFoundError(f'LocalFileStorage.rename: source file "{old_rel_path}"' +
                                    f' (mapped on "{old_path}") is not found')
        new_path = os.path.join(self.root_dir, new_rel_path)
        if os.path.exists(new_path):
            raise Exception(f'LocalFileStorage.rename: dest file "{new_rel_path}"' +
                            f' (mapped on "{new_path}") already exists')
        os.rename(old_path, new_path)

    @contextmanager
    def get_as_local_fn(self, rel_file_path):
        yield os.path.join(self.root_dir, rel_file_path), rel_file_path

    def read(self, rel_file_path: str) -> Optional[bytes]:
        fn = os.path.join(self.root_dir, rel_file_path)
        if not os.path.isfile(fn):
            return
        with open(fn, 'rb') as f:
            return f.read()

    def get_request(self, rel_file_path: str, extra_headers: Optional[Dict[str, Any]]) -> Optional[Response]:
        rel_file_path = self.sub_path_join(self.documents_path, rel_file_path)
        fn = os.path.join(self.root_dir, rel_file_path)

        requests_session = requests.session()
        requests_session.mount('file://', LocalFileAdapter())
        for h in extra_headers:
            requests_session.headers[h] = extra_headers[h]
        resp = requests_session.get(f'file:///{fn}')
        mime = magic.Magic(mime=True)
        resp.headers['Content-Type'] = mime.from_file(fn)
        return resp

    def __str__(self):
        return f'ContraxsuiteLocalFileStorage: {self.root_dir}'


@Singleton
class ContraxsuiteLocalFileStorage(ContraxsuiteInstanceLocalFileStorage):
    """
    This class is a sealed (it doesn't allow inheriting)
    descendant of ContraxsuiteInstanceLocalFileStorage.
    """
