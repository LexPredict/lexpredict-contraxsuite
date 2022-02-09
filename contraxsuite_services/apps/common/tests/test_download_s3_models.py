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

from tests.django_test_case import *

import datetime

from apps.common.s3.s3_browser import S3Resource
from django.test import TestCase
from apps.common.management.commands.download_s3_models import Command, VersionFiles

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestDownloadS3Models(TestCase):
    def test_rel_2_webdav(self):
        cmd = Command()
        webdav_path = cmd.rel_path_to_webdav('en/is_contract')
        self.assertEqual('models/en/is_contract', webdav_path)

    def test_path_is_parent(self):
        cmd = Command()
        self.assertTrue(cmd.path_is_parent('models/en', 'models/en/is_contract'))
        self.assertFalse(cmd.path_is_parent('/models/en/is_contract', '/models/is_contract'))

    def test_find_most_relevant_vers(self):
        cmd = Command()
        now_tm = datetime.datetime.now()
        versions = ['2.0.0', '2.0.1', '1.9.0']

        for v in versions:
            resources = [
                S3Resource(f'ml/{v}/', 0, now_tm),
                S3Resource(f'ml/{v}/ml/', 0, now_tm),
                S3Resource(f'ml/{v}/ml/classifiers', 0, now_tm),
                S3Resource(f'ml/{v}/ml/classifiers/en/', 0, now_tm),
                S3Resource(f'ml/{v}/ml/classifiers/en/contract_type_classifier', 0, now_tm),
                S3Resource(f'ml/{v}/ml/classifiers/en/contract_type_classifier/model.pickle', 0, now_tm),
            ]
            vers_tuple = VersionFiles.get_version_cortege(v)
            cmd.s3_versions[vers_tuple] = VersionFiles(v)
            cmd.s3_versions[vers_tuple].s3_key_by_rel_path = {cmd.s3_path_to_rel_path(s.key, v): s for s in resources}

        cmd.cs_version = (2, 0, 0)
        vers, rc = cmd.find_most_relevant_file_version('en/contract_type_classifier/model.pickle')
        self.assertEqual((2, 0, 0), vers)
        self.assertEqual('ml/2.0.0/ml/classifiers/en/contract_type_classifier/model.pickle', rc.key)

        cmd.cs_version = (2, 0, 1)
        vers, _rc = cmd.find_most_relevant_file_version('en/contract_type_classifier/model.pickle')
        self.assertEqual((2, 0, 1), vers)

        cmd.cs_version = (2, 0, 2)
        vers, _rc = cmd.find_most_relevant_file_version('en/contract_type_classifier/model.pickle')
        self.assertEqual((2, 0, 1), vers)

        cmd.cs_version = (1, 8, 200)
        vers, _rc = cmd.find_most_relevant_file_version('en/contract_type_classifier/model.pickle')
        self.assertIsNone(vers)

    def test_compare_versions(self):
        self.assertEqual(0, Command.compare_versions((0, 1, 2), (0, 1, 2)))
        a = Command.compare_versions((1, 1, 2), (0, 1, 2))
        b = Command.compare_versions((1, 1, 2), (0, 1000, 2000))
        c = Command.compare_versions((1, 1, 2), (1, 1, 3))

        self.assertTrue(a > 0)
        self.assertTrue(b > 0)
        self.assertTrue(c < 0)
        # version (0, 1000, 2000) is closer to (1, 1, 2) than (0, 1, 2) is
        self.assertTrue(b < a)

    def test_s3_path_to_rel_path(self):
        self.assertEqual('en/contract_type_classifier',
                         Command.s3_path_to_rel_path('ml/1.9.0/ml/classifiers/en/contract_type_classifier/', '1.9.0'))
        self.assertEqual('', Command.s3_path_to_rel_path('ml/1.9.0/ml/classifiers', '1.9.0'))
        self.assertEqual('', Command.s3_path_to_rel_path('s', '1.9.0'))

    def test_get_version_from_s3_path(self):
        self.assertEqual('1.9.0',
                         Command.get_version_from_s3_path('ml/1.9.0/ml/classifiers/en/contract_type_classifier/'))
        self.assertEqual('',
                         Command.get_version_from_s3_path('ml/nl/1.9.0/ml/classifiers/en/contract_type_classifier/'))
        self.assertEqual('2.0',
                         Command.get_version_from_s3_path('ml/2.0'))
