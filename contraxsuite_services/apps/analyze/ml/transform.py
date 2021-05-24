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

# Standard imports
import datetime
import pickle
from typing import Tuple, Iterable, Any, List, Union, Optional, Callable, Generator

# Third-party imports
import gensim.models.doc2vec
from django.db import transaction
from django.db.models import F, QuerySet
from lexnlp.nlp.en.tokens import get_token_list
from django.conf import settings

# Project imports
from apps.analyze.ml.classifier_repository import ClassifierRepositoryBuilder
from apps.analyze.models import MLModel, TextUnitVector, DocumentVector
from apps.common.file_storage import get_file_storage, ContraxsuiteFileStorage
from apps.common.utils import get_free_mem
from apps.document.models import DocumentText, TextUnit, Document

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# TODO: Implement language-specific tokenization,
# e.g., en vs. es vs. de, inferred from TU/Document .language

class Doc2VecTransformer:
    """
    Doc2VecTransformer class provides ability to
     - train doc2vec models on TextUnit/Document querysets and
     - store trained models in Transformer objects and then
     - create Document/TextUnit Vectors using those models.
    """

    def __init__(self,
                 vector_size=100,
                 window=10,
                 min_count=10,
                 dm=1,
                 file_storage: Optional[ContraxsuiteFileStorage] = None,
                 log_message: Optional[Callable[[str], None]] = None):
        """
        Setup main arguments for gensim.models.doc2vec.Doc2Vec model
        see https://radimrehurek.com/gensim/models/doc2vec.html
        """
        self.vector_size = vector_size
        self.window = window
        self.min_count = min_count
        self.dm = dm
        self.file_storage = file_storage or get_file_storage()
        self.log_message_routine = log_message

    def log_message(self, msg: str):
        if self.log_message_routine:
            self.log_message_routine(msg)
        else:
            print(msg)

    def train_doc2vec_model(self, data: Iterable[str], count: int) -> gensim.models.doc2vec.Doc2Vec:
        """
        Train doc2vec model from queryset values

        :param data: training data - iterable set of texts
        :param data: count - count of text fragments
        :return: Doc2Vec trained model
        """
        self.log_message(f'Start training train_doc2vec_model for {count} vectors')
        if not count:
            raise RuntimeError('Empty data set, unable to create Doc2Vec model.')

        # Train model
        try:
            # we split model "build_vocab" and "train" procedures because
            # both need iterating through TaggedDocuments, and we don't always have enough
            # memory to store all these documents
            doc2vec_model = gensim.models.doc2vec.Doc2Vec(None,
                                                          vector_size=self.vector_size,
                                                          window=self.window,
                                                          dm=self.dm,
                                                          min_count=self.min_count,
                                                          workers=1)
            doc2vec_model.build_vocab(self.iterate_source_texsts(count, data))
            doc2vec_model.train(self.iterate_source_texsts(count, data), total_examples=count,
                                epochs=doc2vec_model.iter)
            # finished training a model (=no more updates, only querying), reduce memory usage
            doc2vec_model.delete_temporary_training_data(keep_doctags_vectors=True,
                                                         keep_inference=True)
        except Exception as e:
            raise RuntimeError('Bad data set, unable to create Doc2Vec model.') from e

        return doc2vec_model

    def iterate_source_texsts(self, count, data) -> \
            Generator[gensim.models.doc2vec.TaggedDocument, None, None]:
        progress = 0
        percent_interval = 1 if count > 5000 else 5 if count > 500 else 10 if count > 100 else 50
        index = -1
        self.log_message(f'Free memory: {get_free_mem()}')
        for text in data:
            index += 1
            if not text:
                continue
            # Get tokens with LexNLP
            text_tokens = get_token_list(text, stopword=True, lowercase=True)
            # Append gensim object
            doc = gensim.models.doc2vec.TaggedDocument(text_tokens, f'{index}')
            new_progress = int((index + 1) * 100 / count)
            if new_progress - progress > percent_interval:
                self.log_message(f'train_doc2vec_model: {new_progress}% done')
                progress = new_progress
                self.log_message(f'Free memory: {get_free_mem()}')
            yield doc

    def create_transformer_object(self,
                                  source_name: str,  # 'document' or 'text_unit'
                                  doc2vec_model: Any,
                                  **transformer_object_kwargs) -> MLModel:
        """
        Create and store in DB MLModel model object from arguments.
        :param source_name: str - to use in standardized name representation ["document", "text_unit"]
        :param doc2vec_model: Doc2Vec trained model object
        :param transformer_object_kwargs: additional keyword arguments for Transformer model object
        :return: MLModel model object
        """

        # apply default name if a user doesn't provide custom one
        if not transformer_object_kwargs.get('name'):
            vector_name = f'{source_name}_doc2vec_dm={self.dm}_vector={self.vector_size}_window={self.window}'
            vector_name = ClassifierRepositoryBuilder().repository.ensure_unique_name(
                vector_name, MLModel)
            transformer_object_kwargs['name'] = vector_name
        transformer_name = transformer_object_kwargs['name']

        stor_folder = f'models/{MLModel.DEFAULT_LANGUAGE}/transformer/{source_name}'
        if transformer_name:
            stor_folder += f'/{transformer_name}'
        stor_path = f'{stor_folder}/model.pickle'
        model_bytes = pickle.dumps(doc2vec_model)
        self.file_storage.ensure_folder_exists(stor_folder)
        self.file_storage.write_file(stor_path, model_bytes)

        obj = ClassifierRepositoryBuilder().repository.save_transformer(
            MLModel,
            version="{}".format(datetime.datetime.now().isoformat()),
            vector_name=transformer_name,
            model_path=stor_path,
            is_active=True,
            target_entity='transformer',
            language=MLModel.DEFAULT_LANGUAGE,
            apply_to=source_name,  # 'document' or 'text_unit'
            user_modified=True,
            codebase_version=settings.VERSION_NUMBER,
            **transformer_object_kwargs)
        return obj

    def build_doc2vec_document_model(self,
                                     document_qs=None,
                                     project_ids=None,
                                     transformer_name='') -> Tuple[gensim.models.doc2vec.Doc2Vec, MLModel]:
        """
        Build a doc2vec model for Documents from a queryset or all documents.

        :param document_qs: Document.objects queryset (optional)
        :param project_ids: list[int] (optional) - Project ids to filter document queryset
        :param transformer_name: str (optional) - name for Transformer object
        :return: tuple(Doc2Vec trained model object, MLModel model object)
        """
        data, count = ClassifierRepositoryBuilder().repository.get_document_plain_texts(
            document_qs, project_ids)
        self.log_message(f'Got {count} document texts')

        # Django uses DB cursors for iterating. This may be executed behind pgbouncer
        # in transaction mode which can replace session for next iteration step
        # with the one which does not have the original cursor.
        # Covered with transaction to workaround this.
        with transaction.atomic():
            doc2vec_model = self.train_doc2vec_model(data, count)
        self.log_message('train_doc2vec_model: completed')

        transformer = self.create_transformer_object(
            source_name='document',
            doc2vec_model=doc2vec_model,
            name=transformer_name)

        return doc2vec_model, transformer

    def build_doc2vec_text_unit_model(self,
                                      text_unit_qs=None,
                                      project_ids=None,
                                      text_unit_type="sentence",
                                      transformer_name=None) -> Tuple[gensim.models.doc2vec.Doc2Vec,
                                                                      MLModel]:
        """
        Build a doc2vec model for TextUnits from all text units either for given text unit queryset,
        and for given text unit type.

        :param text_unit_qs: TextUnit.objects queryset (optional)
        :param text_unit_type: str - either "sentence" or "paragraph"
        :param project_ids: list[int] (optional) - Project ids to filter document queryset
        :param transformer_name: str (optional) - name for Transformer object
        :return: tuple(Doc2Vec trained model object, MLModel model object)
        """
        queryset = text_unit_qs or TextUnit.objects
        if text_unit_type is not None:
            queryset = queryset.filter(unit_type=text_unit_type)
        if project_ids is not None:
            queryset = queryset.filter(project_id__in=project_ids)

        queryset = queryset.annotate(text=F('textunittext__text'))
        data, count = queryset.values_list('text', flat=True).iterator()
        self.log_message(f'Got {count} text unit texts')

        # Django uses DB cursors for iterating. This may be executed behind pgbouncer
        # in transaction mode which can replace session for next iteration step
        # with the one which does not have the original cursor.
        # Covered with transaction to workaround this.
        with transaction.atomic():
            doc2vec_model = self.train_doc2vec_model(data, count)
        self.log_message('train_doc2vec_model: completed')

        transformer = self.create_transformer_object(
            source_name='text_unit',
            doc2vec_model=doc2vec_model,
            text_unit_type=text_unit_type,
            name=transformer_name)

        return doc2vec_model, transformer

    @staticmethod
    def create_vectors(transformer_obj: MLModel,
                       data: Iterable[Tuple[Any, str]],
                       vector_db_model,
                       vector_target_id_name: str,
                       save: bool = False,
                       file_storage: Optional[ContraxsuiteFileStorage] = None,
                       alpha: float = 0.1,
                       epochs: int = 16) -> List[Union[DocumentVector, TextUnitVector]]:
        """
        Aggregated method to create Vector objects from arguments

        :param transformer_obj: MLModel object
        :param data: data to transform - values queryset iterator containing of tuples (id, text)
        :param vector_db_model: target model - DocumentVector or TextUnitVector
        :param vector_target_id_name: str - one of "document_id" or "text_unit_id"
        :param save: bool - store vectors in db
        :param file_storage: ContraxsuiteFileStorage - storage
        :param alpha: float - The initial learning rate. If unspecified, value from model initialization will be reused.
        :param epochs: int - Number of times to train the new document. Larger values take more time, but may improve
            quality and run-to-run stability of inferred vectors. If unspecified, the `epochs` value
            from model initialization will be reused.
        :return: vector object list
        """
        if not transformer_obj.model_path:
            raise Exception(f'create_vectors(MLModel.id={transformer_obj.pk}): model_path is empty')
        file_storage = file_storage or get_file_storage()
        try:
            file_bytes = file_storage.read(transformer_obj.model_path)
            doc2vec_model = pickle.loads(file_bytes)
        except Exception as e:
            raise Exception(f'create_vectors(MLModel.id={transformer_obj.pk}): '
                            f'cannot load model from "{transformer_obj.model_path}"') from e
        if not doc2vec_model:
            raise Exception(f'create_vectors(MLModel.id={transformer_obj.pk}): ' 
                            f'"{transformer_obj.model_path}" contains no model.json file or file is empty')

        vector_list = []
        for target_id, text in data:

            # Get tokens with LexNLP
            text = text or ''    # prevent from exception with None (like case with unprocessed document)
            text_tokens = get_token_list(text, stopword=True, lowercase=True)

            # Calculate and store vector
            vector = vector_db_model()
            setattr(vector, vector_target_id_name, target_id)
            vector.transformer = transformer_obj
            # TODO: consider to make alpha/epochs dynamic depending on data size
            # lower alpha/epochs produces lower distances and huge amount similarities
            # these values are tested and optimal for data size about 5'000-40'000 records
            # default are None, in this case alpha should be taken from model itself, it's usually = 0.025
            vector.vector_value = doc2vec_model.infer_vector(text_tokens, alpha=alpha, epochs=epochs)
            vector_list.append(vector)

        if save:
            vector_db_model.objects.bulk_create(vector_list, ignore_conflicts=True)
        return vector_list

    def run_doc2vec_text_unit_model(self, text_unit_transformer_id: int, text_unit_qs=None,
                                    project_ids=None):
        """
        Execute a given doc2vec MLModel model
        for some TextUnit queryset or all Text Units to create TextUnitVector objects.

        :param text_unit_transformer_id: int - MLModel object id
        :param text_unit_qs: TextUnit.objects queryset (optional)
        :param project_ids: list[int] (optional) - Project ids to filter document queryset
        :return: None
        """
        transformer_obj: MLModel = MLModel.objects.get(id=text_unit_transformer_id)
        queryset = text_unit_qs or TextUnit.objects
        if project_ids is not None:
            queryset = queryset.filter(document__project_id__in=project_ids)

        data = queryset.annotate(text=F('textunittext__text')).filter(
            unit_type=transformer_obj.text_unit_type).values_list('id', 'text').iterator()

        return self.create_vectors(
            transformer_obj=transformer_obj,
            data=data,
            vector_db_model=TextUnitVector,
            vector_target_id_name='text_unit_id',
            save=True)

    def run_doc2vec_document_model(self,
                                   document_transformer_id: int,
                                   document_qs: Optional[Union[QuerySet, List[Document]]] = None,
                                   project_ids: Optional[List[int]] = None):
        """
        Execute a given doc2vec MLModel model
        for some Document queryset or all Documents to create DocumentVector objects.

        :param document_transformer_id: int - MLModel object id
        :param document_qs: Document.objects queryset (optional)
        :param project_ids: list[int] (optional) - Project ids to filter document queryset
        :return: None
        """
        transformer_obj = MLModel.objects.get(id=document_transformer_id)
        queryset = DocumentText.objects
        if document_qs is not None:
            queryset = DocumentText.objects.filter(document__in=document_qs)
        if project_ids is not None:
            queryset = queryset.filter(document__project_id__in=project_ids)

        data = queryset.values_list('document_id', 'full_text').iterator()

        return self.create_vectors(
            transformer_obj=transformer_obj,
            data=data,
            vector_db_model=DocumentVector,
            vector_target_id_name='document_id',
            save=True)
