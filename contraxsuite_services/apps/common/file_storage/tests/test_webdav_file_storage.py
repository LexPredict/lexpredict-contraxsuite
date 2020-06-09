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

from apps.common.file_storage.webdav_file_storage import ContraxsuiteWebDAVFileStorage
from tests.django_test_case import DjangoTestCase

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


this_dir = os.path.dirname(__file__)


class ContraxsuiteWebDAVFileStorageTest(DjangoTestCase):

    def test_parse_propfind(self):
        with open(os.path.join(this_dir, 'webdav_propfind_response_example.xml'), 'r') as f:
            propfind_xml = f.read()

        stor = ContraxsuiteWebDAVFileStorage('http://localhost:8090/',
                                             'user',
                                             'password')

        files = [fn for fn, is_dir in stor.
            parse_propfind_response('/documents/dav spaces supported test/', propfind_xml) if not is_dir]

        self.assertEqual(files, ['documents/davtest/1001635_1998-03-26_10 Spaces should be decoded.txt',
                                 'documents/davtest/1002037_2005-10-11_2.txt',
                                 'documents/davtest/1002037_2005-08-09_4.txt'])

        # this time we provide non-relevant path to exclude and it should return the single dir
        dirs = [fn for fn, is_dir in ContraxsuiteWebDAVFileStorage()
            .parse_propfind_response('something', propfind_xml) if is_dir]

        self.assertEqual(dirs, ['documents/dav spaces supported test'])
