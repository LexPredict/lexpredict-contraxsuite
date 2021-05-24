import datetime
import logging
import os.path
from typing import Optional, List

import boto3
from botocore import UNSIGNED
from botocore.client import Config


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
                 region: str = 'us-west-1'):
        self.s3client = boto3.client(
            's3',
            region_name=region,
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
