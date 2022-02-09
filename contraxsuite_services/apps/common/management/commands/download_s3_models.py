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

# Imports
import os
import regex as re
import tempfile
from typing import List, Dict, Tuple, Optional

from django.core.management.commands.migrate import Command as MigrateCommand
from django.conf import settings

from apps.analyze.models import MLModel
from apps.common.file_storage import get_file_storage
from apps.common.logger import CsLogger
from apps.common.s3.s3_browser import S3ResourceBrowser, S3Resource

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


logger = CsLogger.get_django_logger()


class VersionFiles:
    """
    The class is only a storage for:
    - version, which is a string + a tuple, "1.9.0" + (1, 9, 0)
    - S3Resource records dictionary where the key is a relative resource (model) path
    """
    def __init__(self, version: str):
        self.version_str = version
        self.version: Tuple[int, int, int] = self.get_version_cortege(version)
        # { <relative model path>: <S3Resource (key, size, date)> }
        self.s3_key_by_rel_path: Dict[str, S3Resource] = {}

    @classmethod
    def get_version_cortege(cls, vers_str: str) -> Tuple[int, int, int]:
        vers = [int(s) for s in vers_str.split('.')]
        vers_list = vers + [0] * (3 - len(vers))
        return (*vers_list, )

    @classmethod
    def get_version_str(cls, vers: Tuple[int, int, int]) -> str:
        return f'{vers[0]}.{vers[1]}.{vers[2]}'

    def __str__(self):
        keys = [k for k in self.s3_key_by_rel_path]
        keys.sort(key=lambda k: len(k))
        shortest_key = keys[0] if keys else ''
        return f'{self.version_str}, root: "{shortest_key}", count: {len(keys)}'

    def __repr__(self):
        return self.__str__()


class Command(MigrateCommand):
    """
    The command first checks S3 public bucket

    There in the certain folder we expect a number of subfolders and files,
    each subfolder starts with a version string like "2.0" or "2.1.184" ...

    Then the command checks MLModels. Each MLModel reference a WebDAV file or directory path.
    By this path we expect one or more files.

    The command updates these files from S3 bucket if some files are missing or have older version
    than the S3 file. The command doesn't download the files which are newer than
    the ContraxSuite instance itself.
    """
    help = 'Download ML model files from S3 bucket'
    # S3 bucket has the directory <S3_FOLDER> and we search for version subdirectories in this folder
    S3_FOLDER = 'ml'
    # each S3 version folder (<S3_FOLDER>/<version>) stores ML models in <S3_MODEL_ROOT> subfolder
    # we may also store some other metadata / metamodels in the <S3_FOLDER>/<version> folders so instead of
    # defining one "S3_MODEL_ROOT" we may have more complex mappings in future
    S3_MODEL_ROOT = 'ml/classifiers'
    # S3 bucket <S3_FOLDER>/<version>/<S3_MODEL_ROOT> contents is mapped to WebDAV <WEBDAV_MODEL_ROOT> relative path
    WEBDAV_MODEL_ROOT = 'models'
    # a regular expression for picking the version from the S3 path like
    # ml/2.4.11/ml/classifiers/en/ -> '2.4.11'
    RE_S3_VERSION = re.compile(fr'(?<=^{S3_FOLDER}/)\d+\.\d+(?:\.\d+)?')

    STORAGE = get_file_storage()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client: Optional[S3ResourceBrowser] = None
        self.cs_version_str = settings.VERSION_NUMBER
        self.cs_version = VersionFiles.get_version_cortege(self.cs_version_str)
        self.s3_keys: List[S3Resource] = []
        self.s3_versions: Dict[Tuple[int, int, int], VersionFiles] = {}
        self.models: List[MLModel] = []

    def handle(self, *args, **options):
        self.client = S3ResourceBrowser(settings.MODEL_S3_BUCKET,
                                        region=settings.MODEL_S3_REGION,
                                        ssl_verify=settings.MODEL_S3_SSL_VERIFY)
        self.s3_keys = self.client.list_folder(self.S3_FOLDER)
        self.read_versioned_folders()
        self.models: List[MLModel] = list(MLModel.objects.all())

        for model in self.models:
            # path without "ml" or other prefixes from both WebDAV / S3 root folders
            rel_path = self.model_path_to_rel_path(model.model_path)
            s3_version, s3_key = self.find_most_relevant_file_version(rel_path)
            if not s3_key:
                continue

            # upload the file if it is missing
            file_data = self.STORAGE.check_path(model.model_path)
            if not file_data['exists'] and not file_data['is_folder'] and not s3_key.is_folder:
                self.ensure_file(rel_path, s3_key)
                continue

            # check the WebDAV folder has all the files
            if s3_key.is_folder:
                self.ensure_files_in_folder(rel_path, False, s3_key)

            if model.user_modified:
                continue

            # update the files if the model (CS) version is older than S3 file (folder)
            model_vers = (0, 0, 0)
            try:
                model_vers = VersionFiles.get_version_cortege(model.codebase_version)
            except:
                self.log_error(f'Model "{model.name}": codebase_version is ' +
                               f'incorrect or not set ("{model.codebase_version}")')
            if self.compare_versions(s3_version, model_vers) <= 0:
                continue

            if not file_data['is_folder'] and not s3_key.is_folder:
                self.rewrite_file(rel_path, s3_key)
            else:
                self.ensure_files_in_folder(rel_path, True, s3_key)

            model.codebase_version = VersionFiles.get_version_str(s3_version)
            model.save(update_fields=['codebase_version'])

        return

    def find_most_relevant_file_version(self, rel_path: str) -> \
            Tuple[Optional[Tuple[int, int, int]], Optional[S3Resource]]:
        # find the closest versions for the file specified by "rel_path" in S3 subfolders
        # skipping the versions that are newer than CS instance itself
        file_versions: List[Tuple[Tuple[int, int, int], S3Resource]] = []
        for vers in self.s3_versions:
            vers_data = self.s3_versions[vers]
            if rel_path in vers_data.s3_key_by_rel_path:
                file_versions.append((vers, vers_data.s3_key_by_rel_path[rel_path]))
        if not file_versions:
            return None, None

        # find the most appropriate version
        version_range = []
        for vers, s3_key in file_versions:
            v_range = self.compare_versions(self.cs_version, vers)
            # we don't take S3 files that have newer version
            if v_range < 0:
                continue
            version_range.append((v_range, vers, s3_key))
        # get the closest to the CS version S3 version
        if not version_range:
            return None, None
        version_range.sort(key=lambda v: v[0])
        return version_range[0][1], version_range[0][2]

    @classmethod
    def compare_versions(cls, a: Tuple[int, int, int], b: Tuple[int, int, int]) -> int:
        # Returns "range" between the versions, a positive number if a > b,
        # a negative number if b > a and 0 if a = b
        # Not only the sign but the number itself means a thing
        return (a[0] - b[0]) * 10000 * 10000 + \
               (a[1] - b[1]) * 10000 + \
               (a[2] - b[2])

    def ensure_file(self, rel_path: str, s3_key: S3Resource):
        # uploads a file given by its s3_key to the WebDAV
        # if the file already exists throws a generic exception
        self.log_message(f'Creating files "{rel_path}"')
        file_name = os.path.basename(rel_path)
        self.upload_file_on_webdav(rel_path, file_name, s3_key)

    def rewrite_file(self, rel_path: str, s3_key: S3Resource):
        # uploads a file given by its s3_key to the WebDAV
        # if the file already exists throws a generic exception - first deletes the file
        self.log_message(f'Updating existing files "{rel_path}"')
        file_name = os.path.basename(rel_path)
        webdav_path = self.rel_path_to_webdav(rel_path)
        self.STORAGE.delete_file(webdav_path)
        self.upload_file_on_webdav(rel_path, file_name, s3_key)

    def ensure_files_in_folder(self, rel_path: str, rewrite_existing: bool, s3_folder_key: S3Resource):
        # check the WebDAV folder has the same files S3 folder has
        # en/is_contract
        s3_files = [k for k in self.s3_keys if self.path_is_parent(s3_folder_key.key, k.key) and not k.is_folder]
        for s3_key in s3_files:
            file_name = os.path.basename(s3_key.key)
            file_rel_path = os.path.join(rel_path, file_name)
            webdav_path = self.rel_path_to_webdav(file_rel_path)
            if not rewrite_existing:
                if not self.check_webdav_file_exists(webdav_path):
                    self.ensure_file(file_rel_path, s3_key)
            else:
                try:
                    self.STORAGE.delete_file(webdav_path)
                except:
                    # file may not exist
                    pass
                self.ensure_file(file_rel_path, s3_key)

    def upload_file_on_webdav(self, rel_path: str, file_name: str, s3_res: S3Resource):
        # downloads the file from S3 by s3_res reference to the temporary local folder
        # then uploads the file to WebDAV (rel_path -> WebDAV path)
        s3_path = s3_res.key
        webdav_path = self.rel_path_to_webdav(rel_path)
        webdav_folder = os.path.dirname(webdav_path)
        self.STORAGE.ensure_folder_exists(webdav_folder)

        with tempfile.TemporaryDirectory() as temporary_directory:
            self.log_message(f'Downloading file "{s3_path}", {s3_res.size} bytes')
            self.client.download_resource(s3_path, target_folder=temporary_directory)
            local_path = os.path.join(temporary_directory, file_name)
            with open(local_path, 'rb') as local_file:
                self.STORAGE.write_file(webdav_path, local_file)

    @classmethod
    def rel_path_to_webdav(cls, rel_path: str) -> str:
        return os.path.join(cls.WEBDAV_MODEL_ROOT, rel_path)

    @classmethod
    def model_path_to_rel_path(cls, model_path: str) -> str:
        return model_path[len(cls.WEBDAV_MODEL_ROOT):].strip('/\\')

    @classmethod
    def s3_path_to_rel_path(cls, s3_path: str, vers_str: str) -> str:
        s3_path = s3_path.strip('/\\')
        path_prefix = os.path.join(cls.S3_FOLDER, vers_str, cls.S3_MODEL_ROOT)
        if len(s3_path) <= len(path_prefix):
            return ''
        return s3_path[len(path_prefix):].strip('/\\')

    def check_webdav_file_exists(self, webdav_path: str) -> bool:
        status = self.STORAGE.check_path(webdav_path)
        return status['exists'] and not status['is_folder']

    def read_versioned_folders(self):
        # enumerates S3 keys, sort the keys by version
        # for each version collects S3 keys into {relative_path: S3 key} dictionary
        for s3_k in self.s3_keys:
            s3_vers = self.get_version_from_s3_path(s3_k.key)
            if not s3_vers:
                continue
            rel_path = self.s3_path_to_rel_path(s3_k.key, s3_vers)
            if not rel_path:
                continue

            s3_vers_cortege = VersionFiles.get_version_cortege(s3_vers)
            if s3_vers_cortege in self.s3_versions:
                self.s3_versions[s3_vers_cortege].s3_key_by_rel_path[rel_path] = s3_k
            else:
                self.s3_versions[s3_vers_cortege] = VersionFiles(s3_vers)
                self.s3_versions[s3_vers_cortege].s3_key_by_rel_path[rel_path] = s3_k

        if not self.s3_versions:
            self.log_error(f'No ContraxSuite version reference is found among {len(self.s3_keys)} S3 keys')
            return
        versions = sorted([v for v in self.s3_versions], reverse=True)
        latest_vers = versions[0]
        self.log_message(f'''{len(self.s3_versions)} ContraxSuite versions are found, the latest is
            {latest_vers[0]}.{latest_vers[1]}.{latest_vers[2]}. There are {len(self.s3_keys)} S3 keys''')

    @classmethod
    def get_version_from_s3_path(cls, path: str) -> str:
        versions = [i.group(0) for i in cls.RE_S3_VERSION.finditer(path)]
        return versions[0] if versions else ''

    @classmethod
    def path_is_parent(cls, parent_path: str, child_path: str) -> bool:
        parent_path = os.path.abspath(parent_path)
        child_path = os.path.abspath(child_path)
        return os.path.commonpath([parent_path]) == os.path.commonpath([parent_path, child_path])

    @classmethod
    def log_message(cls, message: str):
        print(message)
        logger.info(message)

    @classmethod
    def log_error(cls, message: str):
        print(message)
        logger.error(message)
