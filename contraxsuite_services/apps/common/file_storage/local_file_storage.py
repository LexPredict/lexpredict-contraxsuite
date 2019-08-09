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
from contextlib import contextmanager
from typing import List
from typing import Optional, BinaryIO

from django.conf import settings

from apps.common.file_storage.file_storage import ContraxsuiteFileStorage
from apps.common.singleton import Singleton
from apps.common.streaming_utils import copy_data

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


@Singleton
class ContraxsuiteLocalFileStorage(ContraxsuiteFileStorage):
    """
    Implementation of the file storage working in a local folder.
    Intended for usage during the development process to avoid having WebDAV server started on the developer machine.
    Also in future may be used for fast switching to distributed file systems.
    """

    def __init__(self) -> None:
        super().__init__()
        self.root_dir = settings.CONTRAX_FILE_STORAGE_LOCAL_ROOT_DIR

    @classmethod
    def sub_path_join(cls, parent_path: str, relative_path: str) -> str:
        res = super().sub_path_join(parent_path, relative_path)

        # if path separator is not "/" (old Windows OS or something like that) then replace "/" with the proper one
        if os.path.sep != '/':
            return os.path.join(*res.split('/'))
        else:
            return res

    @classmethod
    def get_parent_path(cls, child_path: str):
        return os.path.sep.join(child_path.strip(os.path.sep).split(os.path.sep)[:-1])

    def mkdir(self, rel_path: str):
        path = os.path.join(self.root_dir, rel_path)
        os.mkdir(path)

    def write_file(self, rel_file_path: str, contents_file_like_object: BinaryIO):
        path = os.path.join(self.root_dir, rel_file_path)
        with open(path, 'wb') as dst_f:
            copy_data(contents_file_like_object, dst_f)

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
            raise Exception(f'LocalFileStorage: file "{rel_file_path}"' +
                            f' (mapped on "{file_path}") is not found')
        os.remove(file_path)

    @contextmanager
    def get_as_local_fn(self, rel_file_path):
        yield os.path.join(self.root_dir, rel_file_path), rel_file_path

    def read(self, rel_file_path: str) -> Optional[bytes]:
        fn = os.path.join(self.root_dir, rel_file_path)
        if not os.path.isfile(fn):
            return None
        with open(fn, 'rb') as f:
            return f.read()

    def __str__(self):
        return 'ContraxsuiteLocalFileStorage: {0}'.format(self.root_dir)
