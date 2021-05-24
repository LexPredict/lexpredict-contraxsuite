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

import io
import os
from datetime import datetime

from django.conf import settings
from django.core.files.storage import Storage, get_valid_filename, filepath_to_uri, urljoin
from django.core.files import File
from django.utils import timezone

from filebrowser.storage import StorageMixin
from webdav3.client import Client

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class FileBrowserWebdavStorage(StorageMixin, Storage):

    def __init__(self, base_url='/', url_as_download=True, simple_listdir=False, webdav_root='/'):
        self.base_url = base_url
        self.url_as_download = url_as_download
        self.simple_listdir = simple_listdir

        webdav_client_options = {
            'webdav_hostname': settings.CONTRAX_FILE_STORAGE_WEBDAV_ROOT_URL.rstrip('/'),
            'webdav_login': settings.CONTRAX_FILE_STORAGE_WEBDAV_USERNAME,
            'webdav_password': settings.CONTRAX_FILE_STORAGE_WEBDAV_PASSWORD,
        }
        self.client = Client(webdav_client_options)

        try:
            self.client.mkdir('/media')
            self.client.mkdir('/media/photo')
        except:
            pass
        self.client.webdav.root = webdav_root
        self.client.root = webdav_root

    def path(self, name):
        """
        Return a local filesystem path where the file can be retrieved using
        Python's built-in open() function. Storage systems that can't be
        accessed using open() should *not* implement this method.
        """
        # FIXME: this would be useful with self.location != ''
        # in this case use this notation:
        # 1. define self.location in __init__
        # 2. rewrite path() method to be like
        # return os.oath.join(self.location, name)
        # 3. everywhere in other sel.methods use self.path(name) instead of name attr
        return name

    def isdir(self, path):
        """
        Returns true if name exists and is a directory.
        """
        return self.client.check(path) and self.client.is_dir(path)

    def isfile(self, path):
        """
        Returns true if name exists and is a regular file.
        """
        return self.client.check(path) and not self.client.is_dir(path)

    def move(self, old_file_name, new_file_name, allow_overwrite=False):
        """
        Moves safely a file from one location to another.

        If allow_ovewrite==False and new_file_name exists, raises an exception.
        """
        return self.client.move(remote_path_from=old_file_name,
                                remote_path_to=new_file_name,
                                overwrite=allow_overwrite)

    def makedirs(self, path):
        """
        Creates all missing directories specified by name. Analogue to os.mkdirs().
        """
        return self.client.mkdir(path)

    def rmtree(self, path):
        """
        Deletes a directory and everything it contains. Analogue to shutil.rmtree().
        """
        return self.client.clean(path)

    def setpermission(self, path):
        """
        Sets file permission
        """

    def _open(self, path, mode='rb'):
        tmp = io.BytesIO()
        self.client.download_from(tmp, path)
        tmp.seek(0)
        return File(tmp)

    def _save(self, path, content):
        res = self.client.resource(path)
        res.read_from(content)
        return path

    def get_valid_name(self, name):
        """
        Return a filename, based on the provided filename, that's suitable for
        use in the target storage system.
        """
        return get_valid_filename(name)

    def delete(self, path):
        """
        Delete the specified file from the storage system.
        """
        if self.exists(path):
            self.client.clean(path)

    def exists(self, path):
        """
        Return True if a file referenced by the given name already exists in the
        storage system, or False if the name is available for a new file.
        """
        return self.client.check(path)

    def listdir(self, path):
        """
        List the contents of the specified path. Return a 2-tuple of lists:
        the first item being directories, the second item being files.
        """
        _list = self.client.list(path)

        # for API: iterating over big directory take too much time
        if self.simple_listdir:
            return _list

        # for filebrowser
        directories, files = [], []
        for entry in _list:
            entry_path = os.path.join(path, entry)
            if self.isdir(entry_path):
                directories.append(entry.rstrip('/'))
            else:
                files.append(entry)
        return directories, files

    def size(self, path):
        """
        Return the total size, in bytes, of the file specified by name.
        """
        return self.client.info(path)['size']

    def url(self, path):
        """
        Return an absolute URL where the file's contents can be accessed
        directly by a Web browser.
        """
        url = filepath_to_uri(path)
        if url is not None:
            url = url.lstrip('/')
        url = urljoin(self.base_url, url)
        if self.url_as_download and self.isfile(path):
            url += '?action=download'
        return url

    @staticmethod
    def _datetime_from_timestamp(ts, fmt):
        """
        If timezone support is enabled, make an aware datetime object in UTC;
        otherwise make a naive one in the local timezone.
        """
        dt = datetime.strptime(ts, fmt)
        if settings.USE_TZ:
            # Safe to use .replace() because UTC doesn't have DST
            return dt.replace(tzinfo=timezone.utc)
        return dt

    def get_accessed_time(self, path):
        """
        Return the last accessed time (as a datetime) of the file specified by
        name. The datetime will be timezone-aware if USE_TZ=True.
        """

    def get_created_time(self, path):
        """
        Return the creation time (as a datetime) of the file specified by name.
        The datetime will be timezone-aware if USE_TZ=True.
        """
        return self._datetime_from_timestamp(self.client.info(path)['created'],
                                             fmt='%Y-%m-%dT%H:%M:%SZ')

    def get_modified_time(self, path):
        """
        Return the last modified time (as a datetime) of the file specified by
        name. The datetime will be timezone-aware if USE_TZ=True.
        """
        return self._datetime_from_timestamp(self.client.info(path)['modified'],
                                             fmt='%a, %d %b %Y %H:%M:%S %Z')
