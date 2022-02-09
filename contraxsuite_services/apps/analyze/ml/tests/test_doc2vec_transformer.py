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
import shutil
import pathlib
from apps.common.file_storage.local_file_storage import ContraxsuiteInstanceLocalFileStorage
from apps.analyze.ml.tests.texts_collection import TEST_TEXTS
from apps.analyze.models import DocumentVector
from typing import Optional, Iterable, Union, Any, Tuple
from django.db.models import QuerySet
from apps.document.models import Document
from apps.analyze.ml.classifier_repository import ClassifierRepositoryBuilder, ClassifierRepository
from apps.analyze.ml.tests.base_transformer_test import BaseTransformerTest
from apps.analyze.ml.transform import Doc2VecTransformer


class MockClassifierRepository(ClassifierRepository):
    TEXTS = TEST_TEXTS

    def get_document_plain_texts(self,
                                 document_qs: Optional[Union[QuerySet, Iterable[Document]]] = None,
                                 project_ids: Optional[Iterable[int]] = None) -> Tuple[Iterable[str], int]:
        texts = [self.TEXTS[d.pk - 1] for d in document_qs]
        return texts, len(texts)

    def ensure_unique_name(self, name: str, model_class) -> str:
        return name

    def save_transformer(self,
                         transformer_class: Any,
                         **kwargs) -> Any:
        obj = transformer_class()
        for arg in kwargs:
            setattr(obj, arg, kwargs[arg])
        return obj


class TestFileStorage(ContraxsuiteInstanceLocalFileStorage):
    def __init__(self, local_folder: str):
        super().__init__()
        self.root_dir = local_folder
        self.local_folder = local_folder

    def init_basic_folders(self):
        pass


class TestDoc2VecTransformer(BaseTransformerTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        builder = ClassifierRepositoryBuilder()
        builder._repository = MockClassifierRepository()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        builder = ClassifierRepositoryBuilder()
        builder._repository = ClassifierRepository()

    def test_train(self):
        tr = Doc2VecTransformer(100, 10, 10, 1)
        texts = [MockClassifierRepository.TEXTS[i * 2] for i
                 in range(int(len(MockClassifierRepository.TEXTS) / 2))]
        model = tr.train_doc2vec_model(texts, len(texts))
        self.assertIsNotNone(model)

    def test_build_transformer(self):
        train_docs = [Document()] * 3
        train_docs[0].pk = 1
        train_docs[1].pk = 3
        train_docs[2].pk = 5

        module_path = pathlib.Path(__file__).parent.absolute()
        file_storage = TestFileStorage(os.path.join(module_path, 'test_data'))
        tr = Doc2VecTransformer(100, 10, 10, 1, file_storage)

        model_path = os.path.join(
            pathlib.Path(__file__).parent.absolute(),
            'test_data',
            'models/en/transformer/document/document_doc2vec_dm_1_vector_100_window_10/model.pickle')
        model_reserve_path = model_path + '.old'
        try:
            # store the original model file
            shutil.move(model_path, model_reserve_path)
        except:
            pass
        model, trans = tr.build_doc2vec_document_model(train_docs, 'trans_test')
        try:
            os.remove(model_path)
        except:
            pass
        try:
            # restore the original model file
            shutil.move(model_reserve_path, model_path)
        except:
            pass

        self.assertIsNotNone(model)
        self.assertIsNotNone(trans)

        test_docs = [Document()] * 3
        test_docs[0].pk = 0
        test_docs[1].pk = 2
        test_docs[2].pk = 4

        vectors = Doc2VecTransformer.create_vectors(
            trans,
            [(d.pk, MockClassifierRepository.TEXTS[d.pk - 1]) for d in test_docs],
            DocumentVector,
            'document_id',
            file_storage=file_storage,
            save=False)
        self.assertIsNotNone(vectors)
        self.assertEqual(len(test_docs), len(vectors))
        self.assertGreater(len(vectors[0].vector_value), 10)
        sm = sum([v * v for v in vectors[0].vector_value])
        # vector has non-zero dimensions
        self.assertGreater(sm, 0)
