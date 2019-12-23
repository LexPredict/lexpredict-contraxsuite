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

import re
from contextlib import contextmanager
from typing import Optional, BinaryIO

from django.conf import settings

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class PathManipulationsProhibited(Exception):
    pass


class UnableToReadFile(Exception):
    pass


class ContraxsuiteFileStorage:
    """
    Accumulates several methods for accessing shared files from different machines of the Contraxsuite cluster.

    Contraxsuite is intended for running in a distributed environment and emulates a cluster even if running
    all services on a single machines. Usually the main/master machine is the one providing web services and also
    there are one or more Celery worker machines which load documents, do the field value extracting and several other
    things.

    Usually document files are loaded from clients into Contraxsuite via web API and next Celery worker machines
    need to access these files.

    Web API machine (UWSGI) is able to write files into its local folder while Celery workers have no straightforward
    access to UWSGI machine's file system.

    This is an abstract class providing methods for accessing files shared with some framework.
    Concrete implementations are in the descending classes.

    The methods of this class are specific for Contraxsuite purposes.
    As the most frequent use case is loading documents into the system there are few specific methods for
    accessing the "documents" sub-directory. They are here mainly as a code-reuse solution.

    """

    def __init__(self) -> None:
        super().__init__()
        self.documents_path = settings.CONTRAX_FILE_STORAGE_DOCUMENTS_DIR.strip('/')

    RE_PATH_PROHIBITED = re.compile(r'(^\.\./)|(/\.\.$)|(/\.\./)')
    RE_PATH_DOUBLE_SLASH = re.compile(r'/+')

    @classmethod
    def check_for_path_manipulations(cls, path: str):
        if cls.RE_PATH_PROHIBITED.search(path):
            raise PathManipulationsProhibited()

    @classmethod
    def sub_path_join(cls, parent_path: str, relative_path: str) -> str:
        """
        Join relative child to parent path in safe OS-independent manner.
        As concrete implementations may use different path separators we set '/' as the universal one
        and the descendent classes may replace it with whatever is required.
        """
        cls.check_for_path_manipulations(relative_path)

        if not relative_path:
            return parent_path

        relative_path = cls.RE_PATH_DOUBLE_SLASH.sub('/', relative_path)

        return parent_path.rstrip('/') + '/' + relative_path.strip('/')

    @classmethod
    def get_parent_path(cls, child_path: str):
        ar = child_path.strip('/').split('/')
        del ar[-1]
        return '/'.join(ar) + '/'

    def list(self, rel_file_path: str):
        """
        List files in a dir..
        :param rel_file_path: Path to the directory - related to the root of the file storage.
        :return:
        """
        pass

    def delete_file(self, rel_file_path: str):
        """
        Delete files by absolute path (file system) or full URI
        """
        pass

    def rename_file(self, old_file_path: str, new_file_path: str):
        """
        Rename files by absolute path (file system) or full URI
        """
        pass

    @contextmanager
    def get_as_local_fn(self, rel_file_path: str):
        """
        Download file from the file storage into a temp local file, delete after the work is done.
        Common use case:

        with file_storage.get_as_local_fn('path/to/file') as file_name:
            do_some_work

        :param rel_file_path: Path to file - relative to the root of the storage.
        :return:
        """
        pass

    def mkdir(self, rel_path: str):
        """
        Create directory in the file storage.
        :param rel_path: Path relative to the root of the storage.
        :return:
        """
        pass

    def document_exists(self, rel_path: str):
        """
        Detect by rel path if a document or a folder exists.
        :param rel_path: Path relative to the root of the storage.
        :return:
        """
        pass

    def write_file(self, rel_file_path: str, contents_file_like_object: BinaryIO, content_length: int = None):
        """
        Write file into the file storage.
        :param rel_file_path: Path to the new file related to the root of the file storage.
        :param contents_file_like_object: Data to write into the file.
        :param content_length: Length of file if available
        :return:
        """
        pass

    def mk_doc_dir(self, rel_path: str):
        """
        Create directory in the "documents" storage - a sub-dir in the file storage intended for storing the documents.
        :param rel_path: Path of the dir related to the "documents" sub-dir of the file storage.
        :return:
        """
        self.mkdir(self.sub_path_join(self.documents_path, rel_path))

    def write_document(self, rel_file_path: str, contents_file_like_object: BinaryIO, content_length: int = None):
        """
        Write contents into a file in the documents sub-dir of the file storage.
        :param rel_file_path: Path related to the "documents" sub-dir.
        :param contents_file_like_object:
        :param content_length:
        :return:
        """
        p = self.sub_path_join(self.documents_path, rel_file_path)
        self.write_file(p, contents_file_like_object, content_length)

    @contextmanager
    def get_document_as_local_fn(self, rel_file_path: str):
        """
        Cache a file in the "documents" sub-dir of the file storage into a local temp file, delete after processing.

        See also get_as_local_fn().
        :param rel_file_path: Path to file - relative to "documents" sub-dir.
        :return:
        """
        p = self.sub_path_join(self.documents_path, rel_file_path)

        with self.get_as_local_fn(p) as (fn, file_name):
            try:
                yield fn, rel_file_path
            finally:
                pass

    def delete_document(self, rel_file_path: str):
        """
        Delete document by path relative to the documents folder.
        """
        p = self.sub_path_join(self.documents_path, rel_file_path)
        self.delete_file(p)

    def rename_document(self,
                        old_rel_file_path: str,
                        new_rel_file_path: str):
        """
        Rename document given by path relative to the documents folder.
        """
        old_path = self.sub_path_join(self.documents_path, old_rel_file_path)
        new_path = self.sub_path_join(self.documents_path, new_rel_file_path)
        self.rename_file(old_path, new_path)

    def list_documents(self, rel_file_path: str = ''):
        """
        List files in a dir placed in the "documents" sub-dir of the file storage.
        If rel_file_path represents a dir: list of files in the dir and all its sub-dirs.
        If rel_file_path represents a file: return [file_name] if it exists or empty list otherwise.
        :param rel_file_path: Path relative to the "documents" sub-dir.
        :return:
        """
        lst = self.list(self.sub_path_join(self.documents_path, rel_file_path))
        if not lst:
            return lst
        return [p[len(self.documents_path):] for p in lst]

    def read(self, rel_file_path: str) -> Optional[bytes]:
        """
        Read file contents.
        :param rel_file_path: File path related to the root of the file storage.
        :return:
        """
        pass
