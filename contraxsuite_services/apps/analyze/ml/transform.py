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
from os import path, stat
import pickle
from typing import Tuple, Iterable, Any, List, Union, Optional, Callable, Generator
from tempfile import NamedTemporaryFile
from gc import collect

# Third-party imports
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim import __version__ as version_gensim
from gensim.models.callbacks import CallbackAny2Vec
from lexnlp.nlp.en.tokens import get_token_list, get_tokens
from django.conf import settings
from django.db import transaction
from django.db.models import F, QuerySet

# Project imports
from apps.analyze.ml.classifier_repository import ClassifierRepositoryBuilder
from apps.analyze.models import MLModel, TextUnitVector, DocumentVector, BaseVector
from apps.common.file_storage import get_file_storage, ContraxsuiteFileStorage
from apps.common.utils import get_free_mem
from apps.document.models import DocumentText, TextUnit, Document

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# TODO: Implement language-specific tokenization,
# e.g., en vs. es vs. de, inferred from TU/Document .language


class TrainingCallback(CallbackAny2Vec):
    """
    """

    def __init__(self, log: Callable[[str], None]) -> None:
        """
        Note that the logger cannot be pickled, and so this callback cannot be
        saved with the model.
        """
        self.log: Callable[[str], None] = log
        self.completed_epochs: int = 0
        self.epoch: int = 0

    def on_epoch_begin(self, model: Doc2Vec) -> None:
        """
        Called at the start of each training epoch.
        """
        self.epoch += 1
        self.log(f'Started epoch {self.epoch} / {model.epochs}')

    def on_epoch_end(self, model: Doc2Vec) -> None:
        """
        Called at the end of each training epoch.

        Take note if we want to compute and log loss:
        https://stackoverflow.com/a/58188779/4189676
        https://stackoverflow.com/a/56085717/4189676
        """
        self.log(
            f'...[Epoch {self.epoch} |'
            f' Memory: {get_free_mem()} |'
            f' total_train_time: {model.total_train_time}]'
        )
        self.completed_epochs += 1

    def on_train_begin(self, model: Doc2Vec) -> None:
        """
        Called at the start of the training process.
        """
        self.log('Started training...')
        self.log(
            f'Gensim version: {version_gensim}, '
            f'{model.vector_size=}, '
            f'{model.window=}, '
            f'{model.min_count=}, '
            f'{model.dm=}'
        )

    def on_train_end(self, model: Doc2Vec) -> None:
        """
        Called at the start of the training process.
        """
        self.log('Ended training.')


class Doc2VecTransformer:
    """
    Doc2VecTransformer class provides ability to
     - train doc2vec models on TextUnit/Document QuerySets and
     - store trained models in Transformer objects and then
     - create Document/TextUnit Vectors using those models.
    """

    def __init__(
        self,
        vector_size: int = 100,
        window: int = 10,
        min_count: int = 10,
        dm: int = 1,
        file_storage: Optional[ContraxsuiteFileStorage] = None,
        log_message: Optional[Callable[[str], None]] = None,
    ):
        """
        Setup main arguments for gensim.models.doc2vec.Doc2Vec model.
        See https://radimrehurek.com/gensim/models/doc2vec.html
        """
        self.vector_size: int = vector_size
        self.window: int = window
        self.min_count: int = min_count
        self.dm: int = dm
        self.file_storage: ContraxsuiteFileStorage = file_storage or get_file_storage()
        self.log_message_routine: Optional[Callable[[str], None]] = log_message

    def log_message(self, msg: str) -> None:
        if self.log_message_routine:
            self.log_message_routine(msg)
        else:
            print(msg)

    def train_doc2vec_model(self, data: Iterable[str], count: int) -> Doc2Vec:
        """
        Train doc2vec model from QuerySet values

        :param data: Iterable set of texts used as training data
        :param count: Number of text fragments
        :return: Doc2Vec trained model
        """
        self.log_message(f'Starting to train Doc2Vec model on {count} samples...')
        if not count:
            raise RuntimeError('Empty data set, unable to create Doc2Vec model.')

        # File-based training should eliminate memory issues.
        # Gensim author's blog: https://notebook.community/piskvorky/gensim/docs/notebooks/Any2Vec_Filebased
        # If, for whatever reason, memory issues persist, we can split back into:
        #  - model instantiation with `corpus_file=None`
        #  - doc2vec_model.build_vocab(corpus_file=corpus_file, ...)
        #  - doc2vec_model.train(corpus_file=corpus_file, ...)
        with NamedTemporaryFile(mode='w') as corpus_file:

            self.log_message('Tokenizing training data...')
            corpus_file.writelines(
                ' '.join(tokens) + '\n'
                for text in data
                for tokens in get_tokens(text=text, stopword=True, lowercase=True)
            )

            self.log_message(
                f'...tokenized training data;'
                f' corpus_file "{corpus_file.name}"'
                f' is {stat(corpus_file.name).st_size} bytes.'
            )

            # force garbage collection to clean up before training
            collect()

            doc2vec_model: Doc2Vec = Doc2Vec(
                documents=None,
                corpus_file=corpus_file.name,
                vector_size=self.vector_size,
                window=self.window,
                dm=self.dm,
                min_count=self.min_count,
                workers=1,
                callbacks=(TrainingCallback(log=self.log_message_routine),) if self.log_message_routine else (),
            )

        return doc2vec_model

    def create_transformer_object(self,
                                  source_name: str,  # 'document' or 'text_unit'
                                  doc2vec_model: Doc2Vec,
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

        subfolder = self.file_storage.normalize_folder_name(source_name)
        stor_folder = f'models/{MLModel.DEFAULT_LANGUAGE}/transformer/{subfolder}'
        if transformer_name:
            trans_folder = self.file_storage.normalize_folder_name(transformer_name)
            stor_folder += f'/{trans_folder}'
        stor_path = f'{stor_folder}/model.pickle'
        model_bytes = pickle.dumps(doc2vec_model)

        stor_folder = path.dirname(stor_path)
        file_storage = self.file_storage or get_file_storage()
        file_storage.ensure_folder_exists(stor_folder)
        file_storage.write_file(stor_path, model_bytes, skip_existing=True)

        obj = ClassifierRepositoryBuilder().repository.save_transformer(
            MLModel,
            version=f'{datetime.datetime.now().isoformat()}',
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

    def build_doc2vec_document_model(
        self,
        document_qs: Optional[QuerySet] = None,
        project_ids: Optional[List[int]] = None,
        transformer_name: str = '',
    ) -> Tuple[Doc2Vec, MLModel]:
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

    def build_doc2vec_text_unit_model(
        self,
        text_unit_qs=None,
        project_ids=None,
        text_unit_type="sentence",
        transformer_name=None
    ) -> Tuple[Doc2Vec, MLModel]:
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

        values_list = queryset.values_list('text', flat=True)
        count: int = values_list.count()
        data = values_list.iterator()
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

    @classmethod
    def create_vectors(cls,
                       transformer_obj: MLModel,
                       data: Iterable[Union[Tuple[Any, str], Tuple[Any, int, str, str, int, int]]],
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
        for row in data:
            document_id, location_start, location_end, unit_type = None, None, None, None
            if len(row) == 2:
                target_id, text = row
            else:
                target_id, document_id, text, unit_type, location_start, location_end = row

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
            if document_id:
                vector.document_id = document_id
            if location_start is not None:
                vector.vector_name = f'[{location_start}:{location_end}]'
            vector.unit_type = unit_type

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

        data = queryset.annotate(text=F('text')).filter(
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
