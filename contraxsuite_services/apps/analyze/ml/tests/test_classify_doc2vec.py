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
import pathlib
from apps.common.file_storage.local_file_storage import ContraxsuiteInstanceLocalFileStorage
from apps.analyze.ml.features import Document2VecFeatures
from apps.analyze.ml.tests.texts_collection import TEST_TEXTS
from tests.django_db_mock import MockObjectManager, MockQuerySet
from django.db.models import QuerySet
from apps.analyze.ml.classifier_repository import ClassifierRepository, ClassifierRepositoryBuilder
from typing import List, Any, Optional, Dict, Iterable, Union, Tuple
from django.test import TestCase
from apps.analyze.models import DocumentClassification, DocumentVector, \
    DocumentClassifierAssessment, TextUnitClassifierAssessment, DocumentClassifier, \
    TextUnitClassifier, MLModel
from apps.analyze.ml.classify import ClassifyDocuments
from apps.document.models import Document, DocumentText

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class MockClassifierRepository(ClassifierRepository):
    DOCUMENT_TEXTS: Dict[int, str] = {}

    EVENTS: List[str] = []

    def get_fulltext_by_doc(self, project_ids: Iterable[int]):
        return [(id, self.DOCUMENT_TEXTS[id]) for id in self.DOCUMENT_TEXTS]

    def get_document_plain_texts(self,
                                 document_qs: Optional[Union[QuerySet, Iterable[Document]]] = None,
                                 project_ids: Optional[Iterable[int]] = None) -> Tuple[Iterable[str], int]:
        return [self.DOCUMENT_TEXTS[id] for id in self.DOCUMENT_TEXTS], len(self.DOCUMENT_TEXTS)

    def get_vector_document_name(self, vector: DocumentVector) -> str:
        return f'document {vector.document_id}'

    def save_classifications(self,
                             model_class,
                             classifications: List[Union[DocumentClassifierAssessment,
                                                         TextUnitClassifierAssessment]]):
        self.EVENTS.append(f'stored {len(classifications)} records of {model_class.__name__}')

    def save_classifier(self,
                        classifier: Union[DocumentClassifier, TextUnitClassifier]):
        self.EVENTS.append(f'{type(classifier).__name__} stored')

    def ensure_unique_name(self, name: str, model_class) -> str:
        return name

    def save_transformer(self,
                         transformer_class: Any,
                         **kwargs) -> Any:
        self.EVENTS.append(f'{transformer_class.__name__} stored')
        return transformer_class(**kwargs)


class TestFileStorage(ContraxsuiteInstanceLocalFileStorage):
    def __init__(self, local_folder: str):
        super().__init__()
        self.root_dir = local_folder
        self.local_folder = local_folder

    def init_basic_folders(self):
        pass


class Document2VecFeaturesMock(Document2VecFeatures):
    def __init__(self, *args, **kwargs):
        module_path = pathlib.Path(__file__).parent.absolute()
        file_storage = TestFileStorage(os.path.join(module_path, 'test_data'))
        kwargs['file_storage'] = file_storage
        super(Document2VecFeatures, self).__init__(*args, **kwargs)

        self.transformer = MLModel()
        self.transformer.project_id = self.project_id
        self.transformer.pk = 1
        self.transformer.name = 'test'
        self.doc_by_id: Dict[int, Document] = {}
        self.file_storage = kwargs.get('file_storage')

    def get_document_data(self, qs: Union[QuerySet, Iterable[Document]]):
        self.doc_by_id = {d.pk: d for d in qs}
        return [(d.pk, d.full_text) for d in qs]

    def get_vectors(self) -> List[DocumentVector]:
        vectors = super().get_vectors()
        for v in vectors:
            v.document = self.doc_by_id[v.document_id]
        return vectors


class MockClassifyDocuments(ClassifyDocuments):
    classification_db_model = MockObjectManager()

    @classmethod
    def get_features_engine_class(cls, classify_by: Optional[str]):
        return Document2VecFeaturesMock


class TestClassifyDoc2Vec(TestCase):
    @classmethod
    def setUpClass(cls):
        builder = ClassifierRepositoryBuilder()
        builder._repository = MockClassifierRepository()

    @classmethod
    def tearDownClass(cls):
        builder = ClassifierRepositoryBuilder()
        builder._repository = ClassifierRepository()

    @classmethod
    def make_documents(cls, doc_ids: List[int]):
        texts = TEST_TEXTS

        docs: List[Document] = []
        text_index = 0
        for id in doc_ids:
            doc = Document()
            doc.pk = id
            doc.project_id = 1
            doc.documenttext = DocumentText()
            doc.documenttext.full_text = texts[text_index]
            text_index += 1
            docs.append(doc)
        return docs

    def test_classify(self):
        MockClassifyDocuments.classification_db_model.objects.objects = []
        doc_id_value = {1: 1, 2: 1, 3: 2, 4: 1, 5: 2}
        for doc_id in doc_id_value:
            clsf = DocumentClassification()
            clsf.document_id = doc_id
            clsf.class_value = doc_id_value[doc_id]
            MockClassifyDocuments.classification_db_model.objects.objects.append(clsf)

        class_name = 'category'
        test_documents = self.make_documents(list(doc_id_value))
        queryset = MockQuerySet(test_documents)
        MockClassifierRepository.DOCUMENT_TEXTS = {d.pk: d.full_text for d in test_documents}

        engine = MockClassifyDocuments()
        _ = engine.build_classifier(
            train_queryset=queryset,  # restrict train data
            class_name=class_name,  # restrict train data
            classifier_assessment=True,  # create accuracy metrics (TextUnitClassifierAssessment objects)
            metric_pos_label='true',  # this is required if classifier_assessment=True
            classifier_algorithm='RandomForestClassifier',
            classifier_name='Open Edgar Doc2Vec classifier',  # may be omitted
            classify_by=['text'],  # list or sentence like 'term' for one source
            metric_average='weighted'
        )

        print(MockClassifierRepository.EVENTS)
        self.assertTrue('stored 4 records of DocumentClassifierAssessment'
                        in MockClassifierRepository.EVENTS)
        self.assertTrue('DocumentClassifier stored' in MockClassifierRepository.EVENTS)
        self.assertTrue('MLModel stored' in MockClassifierRepository.EVENTS)
        # TODO: test classifiers on another document set with similar texts like this:
        # count = engine.run_classifier(
        #     classifier,
        #     test_queryset=MockQuerySet(...),
        #     min_confidence=90)
