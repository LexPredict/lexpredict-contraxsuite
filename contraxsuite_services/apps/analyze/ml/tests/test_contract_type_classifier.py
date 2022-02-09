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
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from tests.django_test_case import *
import datetime
import pathlib
from apps.common.file_storage.local_file_storage import ContraxsuiteInstanceLocalFileStorage
from apps.analyze.ml.contract_type_classifier import ContractTypeClassifier


class TestFileStorage(ContraxsuiteInstanceLocalFileStorage):
    def __init__(self, local_folder: str):
        super().__init__()
        self.root_dir = local_folder
        self.local_folder = local_folder

    def init_basic_folders(self):
        pass


class TestContractTypeClassifier(TestCase):
    def test_build_detector(self):
        module_path = pathlib.Path(__file__).parent.absolute()

        ContractTypeClassifier.cached_contract_detector = {}
        ContractTypeClassifier.file_storage = TestFileStorage(
            os.path.join(module_path, 'test_data'))

        started = datetime.datetime.now()
        detector = ContractTypeClassifier.get_contract_detector('en', 0)
        self.assertIsNotNone(detector)
        took_wo_cache = (datetime.datetime.now() - started).total_seconds()

        started = datetime.datetime.now()
        detector = ContractTypeClassifier.get_contract_detector('en', 0)
        self.assertIsNotNone(detector)
        took_with_cache = (datetime.datetime.now() - started).total_seconds()
        self.assertLess(took_with_cache, 0.1 * took_wo_cache)

        # instead of uploading a new file we just spoil cache here
        file_info = ContractTypeClassifier.cached_model_files[ContractTypeClassifier.RF_MODEL_FILE]
        file_info.size += 1

        started = datetime.datetime.now()
        detector = ContractTypeClassifier.get_contract_detector('en', 0)
        self.assertIsNotNone(detector)
        took_wo_cache = (datetime.datetime.now() - started).total_seconds()
        self.assertLess(took_with_cache, 0.1 * took_wo_cache)

        detector = ContractTypeClassifier.get_contract_detector('en', 1)
        self.assertIsNotNone(detector)

        detector = ContractTypeClassifier.get_contract_detector('ru', 0)
        self.assertIsNotNone(detector)
        self.assertEqual(1, len(ContractTypeClassifier.cached_contract_detector))
