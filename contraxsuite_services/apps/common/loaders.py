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
"""
Wrapper for loading templates from "templates" directories
 1. from project apps directories
 2. from project root directory
 3. from other apps directories
packages.
"""

import os
from django.apps import apps
from django.template.loaders.filesystem import Loader as FilesystemLoader
from django.utils._os import upath


class Loader(FilesystemLoader):

    def get_dirs(self):
        project_app_dirs = []
        other_app_dirs = []

        for app_config in apps.get_app_configs():
            if not app_config.path:
                continue
            template_dir = os.path.join(app_config.path, 'templates')
            if os.path.isdir(template_dir):
                if app_config.name.startswith('apps.'):
                    project_app_dirs.append(upath(template_dir))
                else:
                    other_app_dirs.append(upath(template_dir))
        project_dir = super().get_dirs()
        # Immutable return value because it will be cached and shared by callers.
        return tuple(project_app_dirs + project_dir + other_app_dirs)
