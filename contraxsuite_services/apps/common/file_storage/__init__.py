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

from django.conf import settings

from apps.common.file_storage.file_storage import ContraxsuiteFileStorage
from apps.common.file_storage.local_file_storage import ContraxsuiteLocalFileStorage
from apps.common.file_storage.webdav_file_storage import ContraxsuiteWebDAVFileStorage

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def get_file_storage() -> ContraxsuiteFileStorage:
    access_type = settings.CONTRAX_FILE_STORAGE_TYPE
    if access_type == 'Local':
        return ContraxsuiteLocalFileStorage()  # singleton - always returns the same instance
    if access_type == 'WebDAV':
        return ContraxsuiteWebDAVFileStorage()
    raise Exception(f'Unknown file storage type: {access_type}')


def get_filebrowser_site(url_as_download=True):
    from filebrowser.sites import site
    storage = get_media_file_storage(url_as_download=url_as_download)
    site.storage = storage
    site.directory = ''
    return site


def get_media_file_storage(folder='', url_as_download=True):
    from apps.common.migration_utils import is_migration_in_process
    if is_migration_in_process():
        return None

    access_type = settings.CONTRAX_FILE_STORAGE_TYPE
    from filebrowser.sites import FileSystemStorage
    from apps.common.file_storage.filebrowser_webdav_file_storage import FileBrowserWebdavStorage

    folder = folder.strip("/")
    base_url = settings.MEDIA_API_URL

    if folder:
        base_url = os.path.join(base_url, folder + '/')

    if access_type == 'Local':
        location = settings.CONTRAX_FILE_STORAGE_LOCAL_ROOT_DIR
        location = location if not folder else os.path.join(location, folder + '/')
        storage = FileSystemStorage(
            base_url=base_url,
            location=location)

    elif access_type == 'WebDAV':
        webdav_root = '/' if not folder else f'/{folder}/'
        storage = FileBrowserWebdavStorage(
            base_url=base_url,
            url_as_download=url_as_download,
            webdav_root=webdav_root)
    else:
        raise Exception(f'Unknown file storage type: {access_type}')
    return storage
