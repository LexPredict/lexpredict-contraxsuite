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
import gc
from typing import Callable, Union, List, Tuple, Any, Iterable, Optional

import pandas as pd
import psutil
import numpy as np
import scipy.sparse as scp
from django.db import connection

from django.db.models import Sum, QuerySet, F
from pandas import CategoricalDtype

from apps.analyze.ml.sparse_matrix import SparseAllFeaturesTable, SparseSingleFeatureTable
from apps.analyze.ml.transform import Doc2VecTransformer
from apps.analyze.ml.utils import ProjectsNameFilter
from apps.analyze.models import DocumentVector, TextUnitVector, MLModel
from apps.document.models import Document, TextUnit, DocumentText
import apps.extract.models as models
from apps.project.models import Project

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class EmptyDataSetError(Exception):

    def __init__(self, *args, **kwargs):
        self.feature_source = kwargs.pop('feature_source', None)
        super().__init__(*args, **kwargs)


class Features:
    """
    Encapsulates info about features for certain model objects
    """
    def __init__(self,
                 feature_df: pd.DataFrame,
                 item_names: list,
                 unqualified_item_ids: Union[list, None] = None,
                 unqualified_item_names: Union[list, None] = None):
        self.feature_df = feature_df
        self.item_names = item_names
        self.unqualified_item_ids = unqualified_item_ids or []
        self.unqualified_item_names = unqualified_item_names or []

    @property
    def term_frequency_matrix(self):
        return self.feature_df.values

    @property
    def item_index(self):
        return self.feature_df.index.tolist()

    @property
    def feature_names(self):
        return self.feature_df.columns.tolist()


def get_mb(size):
    return round(size / 1024 / 1024, 2)


def get_df_info(df):
    size = get_mb(df.memory_usage().sum())
    return f'shape={df.shape} size={size}M'


class DocumentFeatures:
    """
    Collects features for Documents.
    Transforms a model queryset into features.
    :Example:
        >>> feature_obj = DocumentFeatures(
        ...:        queryset=some_queryset,
        ...:        project_id=18,
        ...:        feature_source="term",
        ...:        unit_type="sentence").get_features()
    Returns Feature object (see above for its signature)
    """
    source_item = 'document'
    source_model = Document
    target_id_field = 'document_id'
    unit_type_filter = 'text_unit__unit_type'
    aggregation_function = Sum('count')
    max_chunk_size = 5000

    source_models = dict(
        date=models.DateUsage,
        definition=models.DefinitionUsage,
        duration=models.DateDurationUsage,
        court=models.CourtUsage,
        currency_name=models.CurrencyUsage,
        currency_value=models.CurrencyUsage,
        term=models.TermUsage,
        party=models.PartyUsage,
        geoentity=models.GeoEntityUsage)

    source_fields = dict(
        date='date',
        definition='definition',
        duration='duration_days',
        court='court__name',
        currency_name='currency',
        currency_value='amount',
        term='term__term',
        party='party__name',
        geoentity='entity__name')

    def __init__(self,
                 queryset: Optional[Union[QuerySet, Iterable[Document]]] = None,
                 project_id: Optional[Union[int, List[int]]] = None,
                 project_name_filter: Optional[str] = None,
                 unit_type='sentence',
                 feature_source='term',
                 drop_empty_rows=True,
                 drop_empty_columns=True,
                 external_feature_names=None,
                 log_message: Callable[[str, str], None] = None,
                 **extra_kwargs):
        """
        :param queryset: Document queryset
        :param project_id: int
        :param project_name_filter: str - alternative to project_id
        :param unit_type: str - one of "sentence", "paragraph"
        :param feature_source: str or list[str] - source name - e.g. "term", or ["term", "date"]
        :param drop_empty_rows: bool - whether skip empty rows from resulted queryset
        :param drop_empty_columns: bool - whether skip empty columns in resulted dataframe
        :param external_feature_names: list of feature names to compose final matrix according with
        """
        self.queryset = queryset
        self.project_id = project_id
        self.project_name_filter = project_name_filter
        self.unit_type = unit_type
        self.feature_source = [feature_source] if isinstance(feature_source, str) else feature_source
        self.drop_empty_rows = drop_empty_rows
        self.drop_empty_columns = drop_empty_columns
        self.external_feature_names = external_feature_names
        self.log_message_routine = log_message
        self.extra_kwargs = extra_kwargs or {}
        self.filter_projects_by_name()
        self.check_arguments()

    def check_arguments(self):
        if 'text' in self.feature_source:
            raise RuntimeError('"text" is not implemented among other feature sources, see Document2VecFeatures')
        if self.unit_type not in ('sentence', 'paragraph'):
            raise RuntimeError('The "unit_type" argument should be one of "sentence", "paragraph".')
        if not isinstance(self.feature_source, (list, tuple)):
            raise RuntimeError('The "feature_source" argument should be of string or list type.')
        if set(self.feature_source).difference(set(self.source_fields)):
            raise RuntimeError('The "feature_source" argument should contain only {}, but it includes {}'.format(
                str(list(self.source_fields.keys())), str(self.feature_source)))

    def filter_projects_by_name(self):
        project_name_filter = (self.project_name_filter or '').strip()
        if project_name_filter and not self.project_id:
            self.project_id = ProjectsNameFilter.filter_objects_by_name(
                Project, project_name_filter)
            self.project_name_filter = ''

    def get_queryset(self):
        """
        Get target model queryset (Document vs TextUnit)
        :return: queryset
        """
        target_qs = self.queryset or self.source_model.objects
        target_qs = target_qs.filter()
        target_qs = self.filter_queryset(target_qs)
        if not target_qs.exists():
            msg = 'Initial queryset {}is empty.'.format(
                'of chosen project_id={} '.format(self.project_id) if self.project_id else '')
            raise EmptyDataSetError(msg, feature_source=self.feature_source)
        return target_qs.distinct()

    def filter_queryset(self, queryset) -> Any:
        queryset = queryset.filter(processed=True, delete_pending=False)

        # perm check - use only allowed docs
        user_id = self.extra_kwargs.get('user_id')
        if user_id:
            allowed_document_ids = Document.get_allowed_document_ids(user_id)
            queryset = queryset.filter(pk__in=allowed_document_ids)

        if not self.project_id:
            return queryset
        project_ids = [self.project_id] if isinstance(self.project_id, (int, str)) else self.project_id or []
        return queryset.filter(project_id__in=project_ids)

    def get_chunk_size(self, row_cost, memory_use=0.1, zeros=3):
        free_memory = psutil.virtual_memory().available
        chunk_size = free_memory * memory_use / row_cost
        len_chunk_size = len(str(int(chunk_size)))
        zeros = min([zeros, len_chunk_size - 1])
        return int(str(chunk_size)[0:len_chunk_size - zeros] + '0' * zeros)

    def get_feature_df(self) -> Tuple[pd.DataFrame, List[Any]]:
        """
        Transform incoming data into pandas dataframe
        :return: tuple(features pandas.DataFrame, unqualified item id list)
        """
        # prepare features dataframe
        target_qs = self.get_queryset()
        all_sample_ids = list(target_qs.values_list('id', flat=True))
        # TODO: all documents ref. by all_sample_ids should be in feature_table
        feature_table: Optional[pd.DataFrame] = None
        counter = 'counter'

        for feature_source_item in self.feature_source:
            msg = f'Get "{feature_source_item}" feature data:'
            self.log_message(msg)
            self.log_message('_' * len(msg))

            # get aggregation queryset parameters for .annotate function
            source_model = self.source_models[feature_source_item]
            source_field = self.source_fields[feature_source_item]
            target_id_field = self.target_id_field
            aggregation = {counter: self.aggregation_function}

            # try to decrease memory usage iterating over chunks and using sparse dataframes
            # Note: pivot_table takes extra memory so use lower memory limits
            source_qs = source_model.objects.filter(**{target_id_field + '__in': all_sample_ids})

            if hasattr(source_model, 'text_unit'):
                source_qs = source_qs.filter(**{self.unit_type_filter: self.unit_type})

            ids = sorted(source_qs.order_by(target_id_field).values_list(target_id_field, flat=True).distinct())
            terms = sorted(source_qs.order_by(source_field).values_list(source_field, flat=True).distinct())
            id_count = len(ids)
            term_count = len(terms)

            self.log_message(f'{self.source_item}s containing "{feature_source_item}": {id_count}')
            self.log_message(f'unique "{feature_source_item}" items: {term_count}')

            if not term_count:
                self.log_message(f'WARN: there are no "{feature_source_item}" entities found')
                continue

            from_mem_chunk_size = self.get_chunk_size(term_count * 2)    # np.uint16 - 2 bytes
            chunk_size = min([self.max_chunk_size, from_mem_chunk_size])
            self.log_message(f'chunk_size from_mem/min/final: {from_mem_chunk_size}/{self.max_chunk_size}/{chunk_size}')

            # TODO: we stopped using pd.SparseDataFrame as there's no such class anymore
            single_feature_table = SparseSingleFeatureTable(feature_source_item)

            for step in range(0, id_count, chunk_size):
                self.log_message(f'...process "{feature_source_item}" feature: "{self.source_item}s" range: {step}-{step + chunk_size}')
                sample_ids = ids[step:step + chunk_size]

                chunk_qs = source_qs \
                    .filter(**{target_id_field + '__in': sample_ids}) \
                    .order_by(target_id_field, source_field) \
                    .values(target_id_field, source_field) \
                    .annotate(**aggregation)

                df_src = list(chunk_qs)
                chunk_df = pd.DataFrame.from_records(df_src)
                del chunk_qs
                gc.collect()  # try to free up memory

                doc_cat = CategoricalDtype(sample_ids, ordered=True)
                # TODO: fix for date features: pandas can't compare dates, but datetimes only
                if terms and isinstance(terms[0], datetime.date):
                    terms = [datetime.datetime.combine(d, datetime.datetime.min.time()) for d in terms]

                if not chunk_df[source_field].empty and isinstance(chunk_df[source_field][0], datetime.date):
                    chunk_df[source_field] = \
                        [datetime.datetime.combine(d, datetime.datetime.min.time())
                         for d in chunk_df[source_field]]

                term_cat = CategoricalDtype(terms, ordered=True)

                row = [] if chunk_df.empty else chunk_df[self.target_id_field].astype(doc_cat).cat.codes
                col = [] if chunk_df.empty else chunk_df[source_field].astype(term_cat).cat.codes
                val = [] if chunk_df.empty else chunk_df[counter]
                sparse_matrix = scp.csr_matrix(
                    (val, (row, col)),
                    shape=(len(sample_ids), term_cat.categories.size),
                    dtype=np.uint16)
                single_feature_table.join(sparse_matrix)

                del chunk_df
                gc.collect()  # try to free up memory

                mem = psutil.virtual_memory()
                self.log_message(f'......available memory: {get_mb(mem.available)}M ({mem.percent}%)')

            # join feature_source_item-specific dataframe into results dataframe
            gc.collect()    # try to free up memory

            single_feature_df_src = SparseAllFeaturesTable(ids)
            single_feature_df_src.add_feature_table(single_feature_table, terms)

            if feature_table is None:
                feature_table = single_feature_df_src.to_dataframe()
            else:
                feature_table = feature_table.join(single_feature_df_src.to_dataframe(), how='outer')

            del single_feature_table
            del single_feature_df_src
            gc.collect()    # try to free up memory
            # end of "for feature_source_item in self.feature_source"

        df = feature_table

        if df is not None and self.drop_empty_columns:
            df.dropna(axis=1, how='all', inplace=True)

        if df is None or df.empty:
            no_features_msg = f'No features of chosen "feature_source" options {self.feature_source} detected.'
            raise EmptyDataSetError(no_features_msg, feature_source=self.feature_source)

        self.log_message(f'df: {get_df_info(df)}')
        mem = psutil.virtual_memory()
        self.log_message(f'available memory: {get_mb(mem.available)}M ({mem.percent}%)')

        # item ids not included in feature df which don't have features at all
        initial_id_set = set(target_qs.values_list('id', flat=True))
        feature_id_set = set(df.index.tolist())
        unqualified_item_ids = sorted(list(initial_id_set.difference(feature_id_set)))

        self.log_message('count unqualified_item_ids: {}'.format(len(unqualified_item_ids)))

        if not self.drop_empty_rows and unqualified_item_ids:
            unqualified_items_df = pd.DataFrame(index=unqualified_item_ids, columns=df.columns).fillna(0)

            self.log_message('unqualified_items_df shape: {} size: {}'.format(
                unqualified_items_df.shape, unqualified_items_df.memory_usage().sum()))

            df = pd.concat([df, unqualified_items_df]).fillna(0).astype(np.uint16)

            self.log_message(f'df: {get_df_info(df)}')

        return df, unqualified_item_ids

    def get_features(self) -> Features:
        """
        Aggregator method to transform incoming queryset into features and indexes
        :return: Features object
        """
        feature_df, unqualified_item_ids = self.get_feature_df()

        if self.external_feature_names is not None:
            feature_df = self.force_use_external_feature_names(feature_df)

        feature_df = feature_df.reindex(sorted(feature_df.columns), axis=1).fillna(0)
        item_index = feature_df.index.tolist()
        item_names = self.get_item_names(item_index)
        unqualified_item_names = self.get_item_names(unqualified_item_ids)
        res = Features(feature_df, item_names, unqualified_item_ids, unqualified_item_names)
        return res

    def force_use_external_feature_names(self, feature_df):
        """
        Resize curren feature_df according to provided external_feature_names list, -
        final feature_df will have the same columns
        :param feature_df: initial feature df
        :return: updated feature df
        """
        # delete extra columns from feature_df
        feature_df = feature_df.filter(self.external_feature_names, axis=1)
        # add new columns from external_feature_names
        new_columns = set(self.external_feature_names) - set(feature_df.columns)
        feature_df = feature_df.reindex(feature_df.columns.tolist() + list(new_columns), axis=1)
        return feature_df

    def get_item_names(self, item_index):
        """
        Get Document names corresponding to passed id set
        :param item_index: list(id)
        :return: list(str)
        """
        document_id_to_name = dict(Document.objects.filter(id__in=item_index).values_list('id', 'name'))
        return [document_id_to_name[i] for i in item_index]

    def log_message(self, msg: str, msg_key='') -> None:
        if self.log_message_routine:
            try:
                self.log_message_routine(msg, msg_key)
            except TypeError:
                self.log_message_routine(msg)


class TextUnitFeatures(DocumentFeatures):
    """
    Collects features for TextUnits
    See DocumentFeatures docstring.
    """
    source_item = 'text_unit'
    source_model = TextUnit
    target_id_field = 'text_unit_id'
    max_chunk_size = 20000

    def get_item_names(self, item_index):
        """
        Get TextUnit names corresponding to passed id set
        :param item_index: list(id)
        :return: list(str)
        """
        return item_index

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(unit_type=self.unit_type)
        return qs

    def check(self):
        """
        Validate incoming data
        """
        # super().check()
        if len(self.feature_source) > 1 and 'text' in self.feature_source:
            raise RuntimeError('"text" could be the only feature source')
        if self.queryset is None and self.project_id is None:
            raise RuntimeError(
                '''Without providing either "queryset" or "project_id"
                argument executing the task may be impossible.''')

    def filter_queryset(self, queryset) -> Any:
        queryset = queryset.filter(document__processed=True, document__delete_pending=False)

        # perm check - use only allowed docs
        user_id = self.extra_kwargs.get('user_id')
        if user_id:
            allowed_document_ids = Document.get_allowed_document_ids(user_id)
            queryset = queryset.filter(document_id__in=allowed_document_ids)

        if not self.project_id:
            return queryset
        project_ids = [self.project_id] if isinstance(self.project_id, (int, str)) else self.project_id or []
        return queryset.filter(document__project_id__in=project_ids)


class Document2VecFeatures(DocumentFeatures):
    """
    Replaces DocumentFeatures when the only feature source is "text"
    (full document text)
    """
    transformer_qs = MLModel.document_transformers

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transformer = None
        transformer_id = self.extra_kwargs.get('transformer_id')
        transformer_qs = self.transformer_qs
        if transformer_id:
            # case: transformer passed in admin task form in explorer UI
            self.transformer = transformer_qs.get(pk=transformer_id)
        elif transformer_qs.filter(project=self.project_id).exists():
            # case: use transformer defined in a project
            self.transformer = transformer_qs.get(project=self.project_id)
        elif transformer_qs.filter(default=True).exists():
            # case: transformer is not defined, get default one (should be only one)
            # f.e.: clustering by text if a project doesn't have transformer
            self.transformer = transformer_qs.get(default=True)
        else:
            # TODO: may be take ANY existing like transformer_qs.last() ?
            raise RuntimeError('Clustering by text vectors requires transformer,')
        self.file_storage = kwargs.get('file_storage')

    def check_arguments(self) -> None:
        if isinstance(self.feature_source, (list, tuple)):
            if len(self.feature_source) != 1:
                raise RuntimeError('Currently only one feature source at a time supported')
            self.feature_source = self.feature_source[0]
        elif not isinstance(self.feature_source, str):
            raise RuntimeError('Feature source should be list or string type')
        if self.feature_source not in ['vector', 'text']:
            raise RuntimeError('The only feature source should be "text" or "vector"')
        if self.feature_source == 'vector' and (
                self.extra_kwargs.get('transformer_id') is None and self.project_id is None):
            raise RuntimeError('Transformer or project id is required for "vector" feature source')

    def build_doc2vec_model(self) -> MLModel:
        transformer = Doc2VecTransformer(vector_size=100, window=10, min_count=10, dm=1,
                                         file_storage=self.file_storage)
        qs = self.get_queryset()    # type: Document.objects
        _, trans_obj = transformer.build_doc2vec_document_model(document_qs=qs)
        return trans_obj

    def get_vectors(self) -> List[DocumentVector]:
        qs = self.get_queryset()    # type: Document.objects

        if self.feature_source == 'vector':
            docs_wo_vectors = qs.exclude(documentvector__transformer=self.transformer)
            if docs_wo_vectors.exists():
                data = DocumentText.objects \
                    .filter(document__in=docs_wo_vectors) \
                    .values_list('document_id', 'full_text')
                Doc2VecTransformer.create_vectors(
                    self.transformer, data, DocumentVector, 'document_id', save=True)
            return list(DocumentVector.objects.filter(document__in=qs, transformer=self.transformer))

        # self.feature_source == 'text'
        transformer = self.build_doc2vec_model()
        data = self.get_document_data(qs)
        return Doc2VecTransformer.create_vectors(transformer, data, DocumentVector,
                                                 'document_id', file_storage=self.file_storage)

    def get_document_data(self, qs: Union[QuerySet, Iterable[Document]]):
        return DocumentText.objects.filter(document__in=qs).values_list('document_id', 'full_text')

    def get_features(self) -> Features:
        """
        Aggregator method to transform incoming data into features and indexes
        """
        vectors = self.get_vectors()
        item_names = [v.document.name for v in vectors]
        columns = ['id'] + [f'f{i}' for i in range(len(vectors[0].vector_value))]
        vectors_indexed = [[v.document.pk] + list(v.vector_value) for v in vectors]
        feature_df = pd.DataFrame(vectors_indexed, columns=columns)
        feature_df.set_index('id', inplace=True)
        feature_df = feature_df.astype(np.float32)
        return Features(feature_df, item_names)


class TextUnit2VecFeatures(Document2VecFeatures):
    """
    Replaces TextUnitFeatures when the only feature source is "text" (unit's text)
    """
    transformer_qs = MLModel.textunit_transformers
    source_model = TextUnit

    def check_arguments(self) -> None:
        super().check_arguments()
        if self.unit_type not in ('sentence', 'paragraph'):
            raise RuntimeError('The "unit_type" argument should be one of "sentence", "paragraph".')

    def get_document_queryset(self) -> Union[QuerySet, Iterable[Document]]:
        target_qs: Union[QuerySet, Iterable[Document]] = self.queryset or Document.all_objects  #.none
        target_qs = target_qs.filter()
        target_qs = self.filter_document_queryset(target_qs)

        if not target_qs.exists():
            msg = 'Initial queryset {}is empty.'.format(
                'of chosen project_id={} '.format(self.project_id) if self.project_id else '')
            raise EmptyDataSetError(msg, feature_source=self.feature_source)
        target_qs = target_qs.distinct()
        return target_qs

    def filter_document_queryset(self, queryset) -> Union[QuerySet, Iterable[Document]]:
        queryset = queryset.filter(processed=True, delete_pending=False)
        # perm check - use only allowed docs
        user_id = self.extra_kwargs.get('user_id')
        if user_id:
            allowed_document_ids = Document.get_allowed_document_ids(user_id)
            queryset = queryset.filter(pk__in=allowed_document_ids)

        if not self.project_id:
            return queryset
        project_ids = [self.project_id] if isinstance(self.project_id, (int, str)) else self.project_id or []
        return queryset.filter(project_id__in=project_ids)

    def build_doc2vec_model(self) -> MLModel:
        transformer = Doc2VecTransformer(vector_size=100, window=10, min_count=10, dm=1)
        qs = self.get_queryset()    # type: TextUnit.objects
        _, trans_obj = transformer.build_doc2vec_text_unit_model(text_unit_qs=qs)
        return trans_obj

    def get_vectors(self) -> List[TextUnitVector]:
        qs = self.get_document_queryset()    # type: Union[QuerySet, Iterable[Document]]
        document_ids = list(qs.values_list('pk', flat=True))

        if self.feature_source == 'vector':
            with connection.cursor() as cursor:
                self._ensure_text_unit_vectors(cursor, document_ids)
            return list(TextUnitVector.objects.filter(document_id__in=document_ids,
                                                      unit_type=self.unit_type,
                                                      transformer_id=self.transformer.pk))

        # self.feature_source == 'text'
        transformer = self.build_doc2vec_model()
        data = TextUnit.objects.filter(document_id__in=document_ids,
                                       unit_type=self.unit_type).values_list('id', 'text')
        return Doc2VecTransformer.create_vectors(transformer, data, TextUnitVector, 'id')

    def _ensure_text_unit_vectors(self, cursor, document_ids: List[int]):
        # find text units that don't have vectors and create vectors for these units
        cursor.execute('''
            SELECT A.id FROM document_textunit A 
            WHERE A.id NOT IN 
              (SELECT text_unit_id FROM analyze_textunitvector B WHERE B.text_unit_id = A.id 
                   AND B.transformer_id = %s)
              AND A.unit_type = %s
              AND A.document_id in %s;''', [self.transformer.pk, self.unit_type, tuple(document_ids)])
        tu_wo_vector_ids = []
        for row in cursor.fetchall():
            tu_wo_vector_ids.append(row[0])
        if not tu_wo_vector_ids:
            return

        self.log_message(f'{tu_wo_vector_ids} text unit vectors are missing')
        data = TextUnit.objects \
            .filter(id__in=tu_wo_vector_ids) \
            .values_list('id', 'document_id', 'text', 'unit_type',
                         'location_start', 'location_end')
        Doc2VecTransformer.create_vectors(
            self.transformer, data, TextUnitVector, 'text_unit_id', save=True)
        self.log_message(f'{len(tu_wo_vector_ids)} text unit vectors have been created')

    def get_features(self) -> Features:
        """
        Aggregator method to transform incoming queryset into features and indexes
        """
        vectors = self.get_vectors()
        self.log_message(f'get_features() got {len(vectors or [])} vectors')
        item_names = [v.vector_name for v in vectors]
        columns = ['id'] + [f'f{i}' for i in range(len(vectors[0].vector_value))]
        vectors_indexed = [[v.text_unit_id] + list(v.vector_value) for v in vectors]
        feature_df = pd.DataFrame(vectors_indexed, columns=columns)
        self.log_message('get_features(): setting features DF index')
        feature_df.set_index('id', inplace=True)
        feature_df = feature_df.astype(np.float32)
        return Features(feature_df, item_names)
