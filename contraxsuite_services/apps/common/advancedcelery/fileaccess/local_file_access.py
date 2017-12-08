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
import os
from contextlib import contextmanager


class LocalFileAccess:

    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def list(self, rel_file_path: str = '/'):
        rel_file_path = rel_file_path.strip('/')
        file_list = []
        full_path = os.path.join(self.root_dir, rel_file_path)

        if os.path.isfile(full_path):
            file_list.append(rel_file_path)
        else:
            for root, _, files in os.walk(full_path):
                for filename in files:
                    file_list.append(os.path.relpath(os.path.join(root, filename), self.root_dir))
        return file_list

    @contextmanager
    def get_local_fn(self, rel_file_path):
        yield os.path.join(self.root_dir, rel_file_path), rel_file_path

    def __str__(self):
        return 'LocalFileAccess: {0}'.format(self.root_dir)

