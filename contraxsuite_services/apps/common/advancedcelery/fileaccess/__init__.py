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

from django.conf import settings

from apps.common.advancedcelery.fileaccess.file_access import FileAccessHandler
from apps.common.advancedcelery.fileaccess.local_file_access import LocalFileAccess
from apps.common.advancedcelery.fileaccess.nginx_http_file_access import NginxHttpFileAccess


def prepare_file_access_handler() -> FileAccessHandler:
    access_type = settings.CELERY_FILE_ACCESS_TYPE
    if access_type == 'Local':
        return LocalFileAccess(settings.CELERY_FILE_ACCESS_LOCAL_ROOT_DIR)
    elif access_type == 'Nginx':
        return NginxHttpFileAccess(settings.CELERY_FILE_ACCESS_NGINX_ROOT_URL)
    else:
        return None
