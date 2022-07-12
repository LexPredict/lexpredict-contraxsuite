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


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# standard library
import tarfile
import zipfile
from typing import Final
from pathlib import Path
from datetime import datetime
from io import BufferedRandom
from tempfile import NamedTemporaryFile

# Django
from django.test import SimpleTestCase

# ContraxSuite
from apps.common.log_utils import ProcessLogger
from apps.analyze.ml.contract_type_classifier import ContractTypeClassifier
from apps.common.file_storage.local_file_storage import ContraxsuiteInstanceLocalFileStorage


class TestFileStorage(ContraxsuiteInstanceLocalFileStorage):
    def __init__(self, local_folder: str):
        super().__init__()
        self.root_dir = local_folder
        self.local_folder = local_folder

    def init_basic_folders(self):
        pass


class TestContractTypeClassifier(SimpleTestCase):

    test_pipeline: Final[str] = 'pipeline_contract_type_classifier.cloudpickle'
    local_folder: Final[Path] = Path(__file__).parent.absolute() / 'test_data'

    @staticmethod
    def _build_file_storage() -> TestFileStorage:
        local_folder: Path = Path(__file__).parent.absolute() / 'test_data'
        return TestFileStorage(local_folder=str(local_folder))

    def _f(self, temporary_file: BufferedRandom):
        """
        """
        # set file storage to TestFileStorage
        file_storage: TestFileStorage = self._build_file_storage()
        ContractTypeClassifier._file_storage = file_storage

        # ensure caches are empty
        ContractTypeClassifier._cache_files.clear()
        ContractTypeClassifier._cache_probability_predictor_contract_type.clear()

        # set the name of the pipeline file
        ContractTypeClassifier.pipeline_file_name = Path(temporary_file.name).name

        # test basic building
        start: datetime = datetime.now()
        probability_predictor_contract_type = \
            ContractTypeClassifier.get_probability_predictor_contract_type(
                log=ProcessLogger(),
                document_language='en',
                project_id=0,
            )
        # print(f'{probability_predictor_contract_type.pipeline=}')
        self.assertIsNotNone(probability_predictor_contract_type)
        duration: float = (datetime.now() - start).total_seconds()

    def test_load_from_zip(self):
        model_folder: str = ContractTypeClassifier._get_model_folder('en', 0)
        with NamedTemporaryFile(
            prefix=f'{self.local_folder}/{model_folder}/',
            suffix='.zip',
        ) as temporary_file:
            with zipfile.ZipFile(file=temporary_file, mode='w') as file_zip:
                p: Path = self.local_folder / model_folder / self.test_pipeline
                file_zip.write(filename=p, arcname=self.test_pipeline)

            self._f(temporary_file=temporary_file)

    def test_load_from_tar_gz(self):
        model_folder: str = ContractTypeClassifier._get_model_folder('en', 0)
        with NamedTemporaryFile(
            prefix=f'{self.local_folder}/{model_folder}/',
            suffix='.tar.gz',
        ) as temporary_file:
            with tarfile.open(fileobj=temporary_file, mode='w|gz') as file_tar_gz:
                p: Path = self.local_folder / model_folder / self.test_pipeline
                file_tar_gz.add(name=p, arcname=self.test_pipeline)

            self._f(temporary_file=temporary_file)

    def test_load_from_tar_xz(self):
        model_folder: str = ContractTypeClassifier._get_model_folder('en', 0)
        with NamedTemporaryFile(
            prefix=f'{self.local_folder}/{model_folder}/',
            suffix='.tar.xz',
        ) as temporary_file:
            with tarfile.open(fileobj=temporary_file, mode='w|xz') as file_tar_xz:
                p: Path = self.local_folder / model_folder / self.test_pipeline
                file_tar_xz.add(name=p, arcname=self.test_pipeline)

            self._f(temporary_file=temporary_file)

    def test_load_from_tar(self):
        model_folder: str = ContractTypeClassifier._get_model_folder('en', 0)
        with NamedTemporaryFile(
            prefix=f'{self.local_folder}/{model_folder}/',
            suffix='.tar',
        ) as temporary_file:
            with tarfile.open(fileobj=temporary_file, mode='w|') as file_tar:
                p: Path = self.local_folder / model_folder / self.test_pipeline
                file_tar.add(name=p, arcname=self.test_pipeline)

            self._f(temporary_file=temporary_file)

    def test_load_from_file(self):
        model_folder: str = ContractTypeClassifier._get_model_folder('en', 0)
        with NamedTemporaryFile(
            prefix=f'{self.local_folder}/{model_folder}/',
        ) as temporary_file:
            p: Path = self.local_folder / model_folder / self.test_pipeline
            with p.open('rb') as f:
                temporary_file.write(f.read())

            self._f(temporary_file=temporary_file)

    def test_build_predictor(self):

        # set file storage to TestFileStorage
        file_storage: TestFileStorage = self._build_file_storage()
        ContractTypeClassifier._file_storage = file_storage

        # ensure caches are empty
        ContractTypeClassifier._cache_files.clear()
        ContractTypeClassifier._cache_probability_predictor_contract_type.clear()

        # set the name of the pickled pipeline file
        ContractTypeClassifier.pipeline_file_name = self.test_pipeline

        # test basic building
        start: datetime = datetime.now()
        probability_predictor_contract_type = \
            ContractTypeClassifier.get_probability_predictor_contract_type(
                log=ProcessLogger(),
                document_language='en',
                project_id=0,
            )
        # print(f'{probability_predictor_contract_type.pipeline=}')
        self.assertIsNotNone(probability_predictor_contract_type)
        self.assertEqual(1, ContractTypeClassifier._cache_files.currsize)
        self.assertEqual(1, ContractTypeClassifier._cache_probability_predictor_contract_type.currsize)
        duration_without_cached_values: float = (datetime.now() - start).total_seconds()
        print(f'{duration_without_cached_values=}')

        # test that caches are indeed faster
        start: datetime = datetime.now()
        probability_predictor_contract_type = \
            ContractTypeClassifier.get_probability_predictor_contract_type(
                log=ProcessLogger(),
                document_language='en',
                project_id=0,
            )
        # print(f'{probability_predictor_contract_type.pipeline=}')
        self.assertIsNotNone(probability_predictor_contract_type)
        duration_with_cached_values: float = (datetime.now() - start).total_seconds()
        self.assertLess(duration_with_cached_values, duration_without_cached_values)
        print(f'{duration_with_cached_values=}')

        # instead of uploading a new file, we just spoil the cache by artificially
        # ... increasing the size_bytes recorded in a FileInformation instance
        file_information = ContractTypeClassifier._cache_files[('en', 0)]
        file_information.size_bytes += 1

        start: datetime = datetime.now()
        probability_predictor_contract_type = \
            ContractTypeClassifier.get_probability_predictor_contract_type(
                log=ProcessLogger(),
                document_language='en',
                project_id=0,
            )
        # print(f'{probability_predictor_contract_type.pipeline=}')
        self.assertIsNotNone(probability_predictor_contract_type)
        duration_spoiled_cache: float = (datetime.now() - start).total_seconds()
        print(f'{duration_spoiled_cache=}')
        self.assertLess(duration_with_cached_values, duration_without_cached_values)

    def test_runtime_error(self):
        # test that nonexistent models throw errors
        with self.assertRaises(RuntimeError):
            _ = ContractTypeClassifier.get_probability_predictor_contract_type(
                log=ProcessLogger(),
                document_language='nonexistent_language',
                project_id=0,
                fallback_to_lexnlp_default_pipeline=False,
            )
