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

from apps.common.file_storage.file_storage import ContraxsuiteFileStorage, PathManipulationsProhibited
from tests.django_test_case import DjangoTestCase

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


this_dir = os.path.dirname(__file__)


class ContraxsuiteWebDAVFileStorageTest(DjangoTestCase):

    def test_path_manipulations(self):
        self.assertRaises(PathManipulationsProhibited,
                          lambda: ContraxsuiteFileStorage.check_for_path_manipulations('../hello'))
        self.assertRaises(PathManipulationsProhibited,
                          lambda: ContraxsuiteFileStorage.check_for_path_manipulations('/he/../llo'))
        self.assertRaises(PathManipulationsProhibited,
                          lambda: ContraxsuiteFileStorage.check_for_path_manipulations('h.ello/../'))
        self.assertRaises(PathManipulationsProhibited,
                          lambda: ContraxsuiteFileStorage.check_for_path_manipulations('hello/..'))

    def test_sub_path_join(self):
        self.assertEqual(ContraxsuiteFileStorage.sub_path_join('root/', '/hello'), 'root/hello')
        self.assertEqual(ContraxsuiteFileStorage.sub_path_join('root/', '/hel///lo'), 'root/hel/lo')
        self.assertEqual(ContraxsuiteFileStorage.sub_path_join('/root/', 'hello/'), '/root/hello')
        self.assertEqual(ContraxsuiteFileStorage.sub_path_join('/root', 'hello'), '/root/hello')

    def test_get_parent_dir(self):
        self.assertEqual(ContraxsuiteFileStorage.get_parent_path('parent/sub-parent/child/'), 'parent/sub-parent/')
        self.assertEqual(ContraxsuiteFileStorage.get_parent_path('parent/child'), 'parent/')
