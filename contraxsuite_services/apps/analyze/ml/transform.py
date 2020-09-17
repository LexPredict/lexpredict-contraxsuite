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

# Third-party imports
from typing import Tuple, Iterable, Any, List

import gensim.models.doc2vec
from django.db import transaction
from django.db.models import F
from lexnlp.nlp.en.tokens import get_token_list

# Project imports
from apps.analyze.ml.utils import ModelUniqueNameBuilder
from apps.analyze.models import DocumentTransformer, TextUnitTransformer, TextUnitVector, DocumentVector, \
    BaseTransformer, BaseVector
from apps.document.models import DocumentText, TextUnit

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
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

    def __init__(self, vector_size=100, window=10, min_count=10, dm=1):
        """
        Setup main arguments for gensim.models.doc2vec.Doc2Vec model
        see https://radimrehurek.com/gensim/models/doc2vec.html
        """
        self.vector_size = vector_size
        self.window = window
        self.min_count = min_count
        self.dm = dm

    def train_doc2vec_model(self, data) -> gensim.models.doc2vec.Doc2Vec:
        """
        Train doc2vec model from queryset values

        :param data: training data - iterable set of texts
        :return: Doc2Vec trained model
        """
        doc2vec_data = []
        for index, text in enumerate(data):
            if not text:
                continue
            # Get tokens with LexNLP
            text_tokens = get_token_list(text, stopword=True, lowercase=True)
            # Append gensim object
            doc2vec_data.append(gensim.models.doc2vec.TaggedDocument(text_tokens, [index]))

        if not doc2vec_data:
            raise RuntimeError('Empty data set, unable to create Doc2Vec model.')

        # Train model
        try:
            doc2vec_model = gensim.models.doc2vec.Doc2Vec(doc2vec_data,
                                                          vector_size=self.vector_size,
                                                          window=self.window,
                                                          dm=self.dm,
                                                          min_count=self.min_count,
                                                          workers=1)
            # finished training a model (=no more updates, only querying), reduce memory usage
            doc2vec_model.delete_temporary_training_data(keep_doctags_vectors=True,
                                                         keep_inference=True)
        except Exception as e:
            raise RuntimeError('Bad data set, unable to create Doc2Vec model.') from e

        return doc2vec_model

    def create_transformer_object(self, transformer_db_model,
                                  source_name, doc2vec_model,
                                  **transformer_object_kwargs):
        """
        Create and store in DB TextUnitTransformer or DocumentTransformer model object from arguments.

        :param transformer_db_model: TextUnitTransformer or DocumentTransformer
        :param source_name: str - to use in standardized name representation ["document", "text_unit"]
        :param doc2vec_model: Doc2Vec trained model object
        :param transformer_object_kwargs: additional keyword arguments for Transformer model object
        :return: TextUnitTransformer or DocumentTransformer model object
        """

        # apply default name if a user doesn't provide custom one
        if not transformer_object_kwargs.get('name'):
            vector_name = f'{source_name}_doc2vec_dm={self.dm}_vector={self.vector_size}_window={self.window}'
            vector_name = ModelUniqueNameBuilder.ensure_unique_name(vector_name, transformer_db_model)
            transformer_object_kwargs['name'] = vector_name

        obj = transformer_db_model.objects.create(
            version="{}".format(datetime.datetime.now().isoformat()),
            vector_name=transformer_object_kwargs['name'],
            model_object=doc2vec_model,
            **transformer_object_kwargs)
        return obj

    def build_doc2vec_document_model(self,
                                     document_qs=None,
                                     project_ids=None,
                                     transformer_name=None) -> Tuple[gensim.models.doc2vec.Doc2Vec,
                                                                     BaseTransformer]:
        """
        Build a doc2vec model for Documents from a queryset or all documents.

        :param document_qs: Document.objects queryset (optional)
        :param project_ids: list[int] (optional) - Project ids to filter document queryset
        :param transformer_name: str (optional) - name for Transformer object
        :return: tuple(Doc2Vec trained model object, DocumentTransformer model object)
        """
        text_queryset = DocumentText.objects
        if document_qs is not None:
            text_queryset = text_queryset.filter(document__in=document_qs)
        if project_ids is not None:
            text_queryset = text_queryset.filter(document__project_id__in=project_ids)

        data = text_queryset.values_list('full_text', flat=True).iterator()

        with transaction.atomic():
            doc2vec_model = self.train_doc2vec_model(data)

        transformer = self.create_transformer_object(
            transformer_db_model=DocumentTransformer,
            source_name='document',
            doc2vec_model=doc2vec_model,
            name=transformer_name)

        return doc2vec_model, transformer

    def build_doc2vec_text_unit_model(self,
                                      text_unit_qs=None,
                                      project_ids=None,
                                      text_unit_type="sentence",
                                      transformer_name=None) -> Tuple[gensim.models.doc2vec.Doc2Vec,
                                                                      BaseTransformer]:
        """
        Build a doc2vec model for TextUnits from all text units either for given text unit queryset,
        and for given text unit type.

        :param text_unit_qs: TextUnit.objects queryset (optional)
        :param text_unit_type: str - either "sentence" or "paragraph"
        :param project_ids: list[int] (optional) - Project ids to filter document queryset
        :param transformer_name: str (optional) - name for Transformer object
        :return: tuple(Doc2Vec trained model object, TextUnitTransformer model object)
        """
        queryset = text_unit_qs or TextUnit.objects
        if text_unit_type is not None:
            queryset = queryset.filter(unit_type=text_unit_type)
        if project_ids is not None:
            queryset = queryset.filter(project_id__in=project_ids)

        queryset = queryset.annotate(text=F('textunittext__text'))
        data = queryset.values_list('text', flat=True).iterator()

        doc2vec_model = self.train_doc2vec_model(data)

        transformer = self.create_transformer_object(
            transformer_db_model=TextUnitTransformer,
            source_name='text_unit',
            doc2vec_model=doc2vec_model,
            text_unit_type=text_unit_type,
            name=transformer_name)

        return doc2vec_model, transformer

    @staticmethod
    def create_vectors(transformer_obj: BaseTransformer,
                       data: Iterable[Tuple[Any, str]],
                       vector_db_model,
                       vector_target_id_name: str) -> List[BaseVector]:
        """
        Aggregated method to create Vector objects from arguments

        :param transformer_obj: DocumentTransformer or TextUnitTransformer object
        :param data: data to transform - values queryset iterator containing of tuples (id, text)
        :param vector_db_model: target model - DocumentVector or TextUnitVector
        :param vector_target_id_name: str - one of "document_id" or "text_unit_id"
        :return: None
        """
        doc2vec_model = transformer_obj.model_object

        vector_list = []
        for target_id, text in data:

            # Get tokens with LexNLP
            text_tokens = get_token_list(text, stopword=True, lowercase=True)

            # Calculate and store vector
            vector = vector_db_model()
            setattr(vector, vector_target_id_name, target_id)
            vector.transformer = transformer_obj
            vector.vector_value = doc2vec_model.infer_vector(text_tokens)
            vector_list.append(vector)

        # vector_db_model.objects.bulk_create(vector_list)
        return vector_list

    def run_doc2vec_text_unit_model(self, text_unit_transformer_id: int, text_unit_qs=None,
                                    project_ids=None):
        """
        Execute a given doc2vec TextUnitTransformer model
        for some TextUnit queryset or all Text Units to create TextUnitVector objects.

        :param text_unit_transformer_id: int - TextUnitTransformer object id
        :param text_unit_qs: TextUnit.objects queryset (optional)
        :param project_ids: list[int] (optional) - Project ids to filter document queryset
        :return: None
        """
        transformer_obj = TextUnitTransformer.objects.get(id=text_unit_transformer_id)
        queryset = text_unit_qs or TextUnit.objects
        if project_ids is not None:
            queryset = queryset.filter(document__project_id__in=project_ids)

        data = queryset.annotate(text=F('textunittext__text')).filter(
            unit_type=transformer_obj.text_unit_type).values_list('id', 'text').iterator()

        return self.create_vectors(
            transformer_obj=transformer_obj,
            data=data,
            vector_db_model=TextUnitVector,
            vector_target_id_name='text_unit_id')

    def run_doc2vec_document_model(self, document_transformer_id: int, document_qs=None,
                                   project_ids=None):
        """
        Execute a given doc2vec DocumentTransformer model
        for some Document queryset or all Documents to create DocumentVector objects.

        :param document_transformer_id: int - DocumentTransformer object id
        :param document_qs: Document.objects queryset (optional)
        :param project_ids: list[int] (optional) - Project ids to filter document queryset
        :return: None
        """
        transformer_obj = DocumentTransformer.objects.get(id=document_transformer_id)
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
            vector_target_id_name='document_id')
