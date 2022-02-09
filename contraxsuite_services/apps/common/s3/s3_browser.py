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

import datetime
import logging
import os.path
from typing import Optional, List

import boto3
from botocore import UNSIGNED
from botocore.client import Config

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class S3Resource:
    def __init__(self,
                 key: str,
                 size: int,
                 last_modified: datetime):
        self.key = key
        self.size = size
        self.last_modified = last_modified

    @property
    def is_folder(self) -> bool:
        return self.size == 0

    def __repr__(self):
        return f'"{self.key}", size={self.size}, last mod="{self.last_modified}"'

    def __str__(self):
        return self.__repr__()


class S3ResourceBrowser:
    def __init__(self,
                 bucket: str,
                 region: str = 'us-west-1',
                 ssl_verify: bool = True):
        self.s3client = boto3.client(
            's3',
            region_name=region,
            verify=ssl_verify,
            config=Config(signature_version=UNSIGNED))
        self.bucket = bucket

    def list_folder(self, folder: Optional[str]) -> List[S3Resource]:
        resources = []
        for key in self.s3client.list_objects_v2(Bucket=self.bucket, Prefix=folder)['Contents']:
            up_time = key['LastModified']
            rs = S3Resource(key['Key'], key['Size'], up_time)
            resources.append(rs)

        return resources

    def download_resource(self,
                          key: str,
                          target_file_name: Optional[str] = None,
                          target_folder: Optional[str] = None) -> str:
        if not target_file_name and not target_folder:
            raise RuntimeError('Either "target_file_name" or "target_folder" should be provided')
        if not target_file_name:
            target_file_name = os.path.basename(key)
            target_file_name = os.path.join(target_folder, target_file_name)

        self.s3client.download_file(self.bucket, key, target_file_name)


def make_s3_browser_silent():
    logger_codes = ['boto3', 'botocore', 'nose', 's3transfer']
    for logger_code in logger_codes:
        logging.getLogger(logger_code).setLevel(logging.CRITICAL)


make_s3_browser_silent()
