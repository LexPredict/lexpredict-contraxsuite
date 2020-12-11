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

import gc
from typing import Callable, Optional, Union, List, Tuple, Any

import gensim
import pandas as pd
import psutil
import numpy as np

from django.db.models import Sum, Value, Q, Case, When, IntegerField, QuerySet, CharField

from apps.analyze.ml.transform import Doc2VecTransformer
from apps.analyze.ml.utils import ProjectsNameFilter
from apps.analyze.models import DocumentVector, BaseTransformer, TextUnitVector
from apps.document.models import Document, TextUnit, DocumentText, TextUnitText
from apps.extract.models import *
from apps.project.models import Project

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
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
                 unqualified_item_ids: list,
                 unqualified_item_names: list):
        self.feature_df = feature_df
        self.item_names = item_names
        self.unqualified_item_ids = unqualified_item_ids
        self.unqualified_item_names = unqualified_item_names

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
        date=DateUsage,
        definition=DefinitionUsage,
        duration=DateDurationUsage,
        court=CourtUsage,
        currency_name=CurrencyUsage,
        currency_value=CurrencyUsage,
        term=TermUsage,
        party=PartyUsage,
        geoentity=GeoEntityUsage)

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
                 queryset=None,
                 project_id: Optional[Union[int, List[int]]] = None,
                 project_name_filter: Optional[str] = None,
                 unit_type='sentence',
                 feature_source='term',
                 drop_empty_rows=True,
                 drop_empty_columns=True,
                 external_feature_names=None,
                 log_message: Callable[[str, str], None] = None):
        """
        :param queryset: Document/TextUnit queryset
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
        self.filter_projects_by_name()
        self.check_arguments()

    def check_arguments(self):
        if 'text' in self.feature_source:
            raise RuntimeError('"text" is not implemented among other feature sources, see Document2VecFeatures')
        if self.unit_type not in ('sentence', 'paragraph'):
            raise RuntimeError('The "unit_type" argument should be one of "sentence", "paragraph".')
        if not isinstance(self.feature_source, (list, tuple)):
            raise RuntimeError('The "feature_source" argument should be of string or list type.')
        elif set(self.feature_source).difference(set(self.source_fields)):
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
        target_qs = self.filter_by_project_id(target_qs)
        if not target_qs.exists():
            msg = 'Initial queryset {}is empty.'.format(
                'of chosen project_id={} '.format(self.project_id) if self.project_id else '')
            raise EmptyDataSetError(msg, feature_source=self.feature_source)
        return target_qs.distinct()

    def filter_by_project_id(self, queryset) -> Any:
        if not self.project_id:
            return queryset
        project_ids = [self.project_id] if isinstance(self.project_id, int) else self.project_id or []
        return queryset.filter(project_id__in=project_ids)

    def get_chunk_size(self, row_cost, memory_use=0.1, zeros=3):
        free_memory = psutil.virtual_memory().available
        chunk_size = free_memory * memory_use / row_cost
        len_chunk_size = len(str(int(chunk_size)))
        zeros = min([zeros, len_chunk_size - 1])
        return int(str(chunk_size)[0:len_chunk_size - zeros] + '0' * zeros)

    def get_feature_df(self) -> Tuple[pd.SparseDataFrame, List[Any]]:
        """
        Transform incoming data into pandas dataframe
        :return: tuple(features pandas.DataFrame, unqualified item id list)
        """
        # prepare features dataframe
        df = pd.SparseDataFrame()

        target_qs = self.get_queryset()
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
            source_qs = source_model.objects.filter(**{target_id_field+'__in': target_qs.values_list('id')})

            if hasattr(source_model, 'text_unit'):
                source_qs = source_qs.filter(**{self.unit_type_filter: self.unit_type})

            ids = sorted(source_qs.order_by(target_id_field).values_list(target_id_field,flat=True).distinct())
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

            # FIXME: pandas 0.25 has another way:
            # https://pandas.pydata.org/pandas-docs/stable/user_guide/sparse.html#sparse-migration
            df_ = pd.SparseDataFrame()

            for step in range(0, id_count, chunk_size):
                self.log_message(f'...process "{feature_source_item}" feature: "{self.source_item}s" range: {step}-{step + chunk_size}')

                chunk_qs = source_qs \
                    .filter(**{target_id_field + '__in': ids[step:step + chunk_size]}) \
                    .order_by(target_id_field, source_field) \
                    .values(target_id_field, source_field) \
                    .annotate(**aggregation)

                if not chunk_qs.exists():
                    continue

                chunk_df = pd.DataFrame.from_records(list(chunk_qs))
                del chunk_qs
                gc.collect()  # try to free up memory

                chunk_df[counter] = chunk_df[counter].astype(np.uint16)
                chunk_dft = chunk_df.pivot_table(
                    index=target_id_field, columns=source_field,
                    values=counter, aggfunc=sum)

                self.log_message(f'......chunk_df: {get_df_info(chunk_df)}')
                del chunk_df
                gc.collect()  # try to free up memory

                missed_columns = list(set(terms) - set(chunk_dft.columns))
                chunk_dft = chunk_dft.reindex(chunk_dft.columns.tolist() + missed_columns, axis=1) \
                    .fillna(0).astype(np.uint16)

                chunk_dfts = chunk_dft.fillna(0).to_sparse(fill_value=0)
                self.log_message(f'......chunk_dft: {get_df_info(chunk_dft)}')
                del chunk_dft
                gc.collect()  # try to free up memory

                df_ = df_.append(chunk_dfts).fillna(0)
                self.log_message(f'......chunk_dfts: {get_df_info(chunk_dfts)}')
                del chunk_dfts
                gc.collect()  # try to free up memory

                self.log_message(f'......df_: {get_df_info(df_)}')
                mem = psutil.virtual_memory()
                self.log_message(f'......available memory: {get_mb(mem.available)}M ({mem.percent}%)')

            if self.drop_empty_columns:
                df_ = df_.dropna(axis=1, how='all')

            # name columns by feature_source item like "term(account)", "duration(30)"
            df_.columns = ["%s(%s)" % (feature_source_item, str(i)) for i in df_.columns]

            # join feature_source_item-specific dataframe into results dataframe
            gc.collect()    # try to free up memory
            df = df.join(df_, how='outer')
            del df_
            gc.collect()    # try to free up memory

            self.log_message(f'df: {get_df_info(df)}')
            mem = psutil.virtual_memory()
            self.log_message(f'available memory: {get_mb(mem.available)}M ({mem.percent}%)')

        if df.empty:
            msg = 'No features of chosen "feature_source" options {} detected. ' \
                  'Empty Data Set.'.format(str(self.feature_source))
            raise EmptyDataSetError(msg, feature_source=self.feature_source)

        # item ids not included in feature df which don't have features at all
        initial_id_set = set(target_qs.values_list('id', flat=True))
        feature_id_set = set(df.index.tolist())
        unqualified_item_ids = sorted(list(initial_id_set.difference(feature_id_set)))

        self.log_message('count unqualified_item_ids: {}'.format(len(unqualified_item_ids)))

        if not self.drop_empty_rows and unqualified_item_ids:
            unqualified_items_df = pd.SparseDataFrame(index=unqualified_item_ids, columns=df.columns).fillna(0)

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
            self.log_message_routine(msg, msg_key)


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

    def filter_by_project_id(self, queryset) -> Any:
        if not self.project_id:
            return queryset
        project_ids = [self.project_id] if isinstance(self.project_id, int) else self.project_id or []
        return queryset.filter(document__project_id__in=project_ids)


class Document2VecFeatures(DocumentFeatures):
    """
    Replaces DocumentFeatures when the only feature source is "text"
    (full document text)
    """
    source_item = 'document'
    source_model = Document
    project_filter_key = 'project_id'
    unit_type_filter = 'textunit__unit_type'

    def __init__(self,
                 queryset: Optional[Union[QuerySet, List[Document]]] = None,
                 project_id: Optional[int] = None,
                 project_name_filter: Optional[str] = None,
                 unit_type: str = 'sentence',
                 feature_source: str = 'term',
                 drop_empty_rows=True,
                 drop_empty_columns=True,
                 external_feature_names=None,
                 log_message: Callable[[str, str], None] = None):
        super().__init__(queryset, project_id, project_name_filter,
                         unit_type, feature_source,
                         drop_empty_rows, drop_empty_columns,
                         external_feature_names, log_message)
        self.transformer = None  # type: Optional[BaseTransformer]
        self.project_ids = []  # type: List[str]

    def check_arguments(self):
        if ['text'] != self.feature_source:
            raise RuntimeError('The only feature source for Document2VecFeatures should be "text"')

    def build_doc2vec_model(self) -> None:
        transformer = Doc2VecTransformer(vector_size=100, window=10,
                                         min_count=10, dm=1)
        transformer_name = ''
        self.project_ids = [self.project_id] \
            if self.project_id and isinstance(self.project_id, int) else self.project_id or []
        if not self.project_ids:
            self.project_ids = list(self.queryset.values_list('project_id', flat=True).distinct())
            if not self.project_ids:
                error_msg = 'Document2VecFeatures has got no project_id and empty docs queryset'
                self.log_message(error_msg)
                raise RuntimeError(error_msg)

        if not self.queryset:
            self.queryset = Document.objects.filter(project_id__in=self.project_ids)

        model_builder_args = dict(project_ids=self.project_ids, transformer_name=transformer_name)
        model_builder = transformer.build_doc2vec_document_model  # source == 'document':
        doc2vec, trans_obj = model_builder(**model_builder_args)
        self.transformer = trans_obj

    def get_features(self) -> Features:
        """
        Aggregator method to transform incoming queryset into features and indexes
        """
        self.build_doc2vec_model()  # type: gensim.models.doc2vec.Doc2Vec
        data = DocumentText.objects.filter(document__project_id__in=self.project_ids).values_list(
            'document_id', 'full_text')
        vectors = Doc2VecTransformer.create_vectors(
            self.transformer,
            data,
            DocumentVector,
            'document_id')  # type: List[DocumentVector]

        item_names = []
        unqualified_item_ids = []
        unqualified_item_names = []
        for v in vectors:
            item_names.append(v.document.name)

        # feature names could be words instead of just "f0" ... by tagging documents
        # but this would require too much memory
        columns = ['id'] + [f'f{i}' for i in range(len(vectors[0].vector_value))]
        vectors_indexed = [[v.document.pk] + list(v.vector_value) for v in vectors]
        feature_df = pd.DataFrame(vectors_indexed,
                                  columns=columns)
        feature_df.set_index('id', inplace=True)

        res = Features(feature_df,
                       item_names,
                       unqualified_item_ids,
                       unqualified_item_names)

        return res


class TextUnit2VecFeatures(DocumentFeatures):
    """
    Replaces TextUnitFeatures when the only feature source is "text"
    (unit's text)
    """
    source_item = 'document'
    source_model = Document
    project_filter_key = 'project_id'
    unit_type_filter = 'textunit__unit_type'

    def __init__(self,
                 queryset: Optional[Union[QuerySet, List[Document]]] = None,
                 project_id: Optional[int] = None,
                 unit_type: str = 'sentence',
                 feature_source: str = 'term',
                 drop_empty_rows=True,
                 drop_empty_columns=True,
                 external_feature_names=None,
                 log_message: Callable[[str, str], None] = None):
        super().__init__(queryset, project_id, unit_type, feature_source,
                         drop_empty_rows, drop_empty_columns,
                         external_feature_names, log_message)
        self.transformer = None  # type: Optional[BaseTransformer]
        self.project_ids = []  # type: List[str]

    def check_arguments(self):
        if ['text'] != self.feature_source:
            raise RuntimeError('The only feature source for Document2VecFeatures should be "text"')
        if self.unit_type not in ('sentence', 'paragraph'):
            raise RuntimeError('The "unit_type" argument should be one of "sentence", "paragraph".')

    def build_doc2vec_model(self) -> None:
        transformer = Doc2VecTransformer(vector_size=100, window=10,
                                         min_count=10, dm=1)
        transformer_name = ''
        self.project_ids = [self.project_id] if self.project_id else []
        if not self.project_ids:
            self.project_ids = list(self.queryset.values_list('project_id', flat=True).distinct())
            if not self.project_ids:
                error_msg = 'Document2VecFeatures has got no project_id and empty docs queryset'
                self.log_message(error_msg)
                raise RuntimeError(error_msg)

        if not self.queryset:
            self.queryset = \
                TextUnitText.objects.filter(text_unit__unit_type=self.unit_type,
                                            text_unit__document__project_id__in=self.project_ids)

        model_builder_args = dict(project_ids=self.project_ids, transformer_name=transformer_name)
        model_builder = transformer.build_doc2vec_text_unit_model
        doc2vec, trans_obj = model_builder(**model_builder_args)
        self.transformer = trans_obj

    def get_features(self) -> Features:
        """
        Aggregator method to transform incoming queryset into features and indexes
        """
        self.build_doc2vec_model()  # type: gensim.models.doc2vec.Doc2Vec
        data = self.queryset.values_list(
            'text_unit_id', 'text')
        vectors = Doc2VecTransformer.create_vectors(
            self.transformer,
            data,
            TextUnitVector,
            'text_unit_id')  # type: List[TextUnitVector]

        item_names = []
        unqualified_item_ids = []
        unqualified_item_names = []
        for v in vectors:
            unit_name = f'[{v.text_unit.location_start}:{v.text_unit.location_end}]'
            item_names.append(unit_name)

        # feature names could be words instead of just "f0" ... by tagging documents
        # but this would require too much memory
        columns = ['id'] + [f'f{i}' for i in range(len(vectors[0].vector_value))]
        vectors_indexed = [[v.text_unit.pk] + list(v.vector_value) for v in vectors]
        feature_df = pd.DataFrame(vectors_indexed,
                                  columns=columns)
        feature_df.set_index('id', inplace=True)

        res = Features(feature_df,
                       item_names,
                       unqualified_item_ids,
                       unqualified_item_names)

        return res
