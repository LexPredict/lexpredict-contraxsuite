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

import pandas as pd
import psutil
import numpy as np

from django.db.models import Sum, Value, Q, Case, When, IntegerField

from apps.document.models import Document, TextUnit

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
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
    source_model = Document
    project_filter_key = 'project_id'
    unit_type_filter = 'textunit__unit_type'

    source_fields = dict(
        source_type='source_type',
        document_type='document_type',
        metadata='documentmetadata__metadata',
        date='textunit__dateusage__date',
        definition='textunit__definitionusage__definition',
        duration='textunit__datedurationusage__duration_days',
        court='textunit__courtusage__court__name',
        currency_name='textunit__currencyusage__currency',
        currency_value='textunit__currencyusage__amount',
        term='textunit__termusage__term__term',
        party='textunit__partyusage__party__name',
        geoentity='textunit__geoentityusage__entity__name')

    aggregation_functions = dict(
        source_type=Value('source_type'),
        document_type=Value('document_type'),
        metadata=Value('documentmetadata__metadata'),
        date=Sum('textunit__dateusage__count'),
        definition=Sum('textunit__definitionusage__count'),
        duration=Sum('textunit__datedurationusage__count'),
        court=Sum('textunit__courtusage__count'),
        currency_name=Sum('textunit__currencyusage__count'),
        currency_value=Sum('textunit__currencyusage__count'),
        term=Sum('textunit__termusage__count'),
        party=Sum('textunit__partyusage__count'),
        geoentity=Sum('textunit__geoentityusage__count'))

    def __init__(self,
                 queryset=None,
                 project_id=None,
                 unit_type='sentence',
                 feature_source='term',
                 drop_empty_rows=True,
                 drop_empty_columns=True,
                 external_feature_names=None):
        """
        :param queryset: Document/TextUnit queryset
        :param project_id: int
        :param unit_type: str - one of "sentence", "paragraph"
        :param feature_source: str or list[str] - source name - e.g. "term", or ["term", "date"]
        :param drop_empty_rows: bool - whether skip empty rows from resulted queryset
        :param drop_empty_columns: bool - whether skip empty columns in resulted dataframe
        :param external_feature_names: list of feature names to compose final matrix according with
        """
        self.queryset = queryset
        self.project_id = project_id
        self.unit_type = unit_type
        self.feature_source = [feature_source] if isinstance(feature_source, str) else feature_source
        self.drop_empty_rows = drop_empty_rows
        self.drop_empty_columns = drop_empty_columns
        self.external_feature_names = external_feature_names
        self.check()

    def check(self):
        """
        Validate incoming data
        """
        if self.unit_type not in ('sentence', 'paragraph'):
            raise RuntimeError('The "unit_type" argument should be one of "sentence", "paragraph".')
        if not isinstance(self.feature_source, (list, tuple)):
            raise RuntimeError('The "feature_source" argument should be of string or list type.')
        elif set(self.feature_source).difference(set(self.source_fields)):
            raise RuntimeError('The "feature_source" argument should contain only {}, but it includes {}'.format(
                str(list(self.source_fields.keys())), str(self.feature_source)))

    def get_queryset(self):
        """
        Get target model queryset (Document vs TextUnit)
        :return: queryset
        """
        target_qs = self.queryset or self.source_model.objects
        target_qs = target_qs.filter()
        if self.project_id:
            target_qs = target_qs.filter(**{self.project_filter_key: self.project_id})
        if not target_qs.exists():
            msg = 'Initial queryset {}is empty.'.format(
                'of chosen project_id={} '.format(self.project_id) if self.project_id else '')
            raise EmptyDataSetError(msg, feature_source=self.feature_source)
        return target_qs.distinct()

    def get_chunk_size(self, row_cost, memory_use=0.1, zeros=3):
        free_memory = psutil.virtual_memory().free
        chunk_size = free_memory * memory_use / row_cost
        len_chunk_size = len(str(int(chunk_size)))
        zeros = min([zeros, len_chunk_size - 1])
        return int(str(chunk_size)[0:len_chunk_size - zeros] + '0' * zeros)

    def get_feature_df(self):
        """
        Transform incoming data into pandas dataframe
        :return: tuple(features pandas.DataFrame, unqualified item id list)
        """
        # prepare features dataframe
        df = pd.SparseDataFrame()

        target_qs = self.get_queryset()
        target_id_field = 'id'
        counter = 'counter'

        for feature_source_item in self.feature_source:

            # get aggregation queryset parameters for .annotate function
            source_field = self.source_fields[feature_source_item]
            aggregation_function = self.aggregation_functions[feature_source_item]
            aggregation_function.filter = Q(**{self.unit_type_filter: self.unit_type})
            aggregation = {counter: aggregation_function}

            # use bool value for missing metadata
            if feature_source_item == 'metadata':
                aggregation = {
                    counter: Case(When(**{source_field + '__isnull': False}, then=Value(1)),
                                  default=Value(0), output_field=IntegerField())}

            # prepare feature_source_item-specific values queryset with total counts per ID/term
            term_source_qs = target_qs \
                .order_by(target_id_field, source_field) \
                .values(target_id_field, source_field) \
                .annotate(**aggregation) \
                .exclude(**{counter: None})

            # skip unqualified rows with zeros
            if self.drop_empty_rows:
                term_source_qs = term_source_qs.filter(**{counter + '__gt': 0})

            if not term_source_qs.exists():
                continue

            # unpack nested metadata values into features
            if feature_source_item == 'metadata':
                term_source_qs = [
                    {'id': item['id'], source_field: '%s: %s' % (k, str(v)), counter: 1} for item in
                    term_source_qs for k, v in item[source_field].items()]

            # FIXME: leave it just commented out - seems it doesn't work properly
            # use number of days since min value as feature value
            # if feature_source_item == 'date':
            #     min_value = df_[source_field].min().toordinal() - 1
            #     df_[counter] = df_.apply(lambda x: x[source_field].toordinal() - min_value, axis=1)

            # FIXME: leave it just commented out - seems it doesn't work properly
            # use amount value as feature value
            # elif feature_source_item in ['duration', 'currency_value']:
            #     df_[counter] = df_.apply(lambda x: x[source_field], axis=1)

            # try to decrease memory usage iterating over chunks and using sparse dataframes
            # Note: pivot_table takes extra memory so use lower memory limits
            ids = list(set(target_qs.values_list(target_id_field, flat=True)))
            id_count = len(ids)
            terms = sorted(list(term_source_qs.order_by(source_field)
                                .values_list(source_field, flat=True).distinct()))
            term_count = len(terms)

            print('id_count: ', id_count)
            print('term_count: ', term_count)

            chunk_size = self.get_chunk_size(term_count * 2)    # np.uint16 - 2 bytes

            print('chunk_size: ', chunk_size)

            # FIXME: pandas 0.25 has another way:
            # https://pandas.pydata.org/pandas-docs/stable/user_guide/sparse.html#sparse-migration
            df_ = pd.SparseDataFrame()

            for step in range(0, id_count, chunk_size):

                print('process range: {}-{}'.format(step, step + chunk_size))

                chunk_qs = term_source_qs.filter(
                    **{target_id_field + '__in': ids[step:step + chunk_size]})
                chunk_df = pd.DataFrame.from_records(list(chunk_qs))
                chunk_df[counter] = chunk_df[counter].astype(np.uint16)
                chunk_dft = chunk_df.pivot_table(
                    index=target_id_field, columns=source_field,
                    values=counter, aggfunc=sum)
                missed_columns = list(set(terms) - set(chunk_dft.columns))
                chunk_dft = chunk_dft.reindex(chunk_dft.columns.tolist() + missed_columns, axis=1) \
                    .fillna(0).astype(np.uint16)
                chunk_dfts = chunk_dft.fillna(0).to_sparse(fill_value=0)
                df_ = df_.append(chunk_dfts).fillna(0)

                print('chunk_df size: ', chunk_df.memory_usage().sum())
                print('chunk_dft size: ', chunk_dft.memory_usage().sum())
                print('chunk_dfts size: ', chunk_dfts.memory_usage().sum())
                print('df_ size: ', df_.memory_usage().sum())
                print('df_ shape: ', df_.shape)

            if self.drop_empty_columns:
                df_ = df_.dropna(axis=1, how='all')

            # name columns by feature_source item like "term(account)", "duration(30)"
            df_.columns = ["%s(%s)" % (feature_source_item, str(i)) for i in df_.columns]

            # join  feature_source_item-specific dataframe into results dataframe
            df = df.join(df_, how='outer')

            print('df size: ', df.memory_usage().sum())
            print('df shape: ', df.shape)

        if df.empty:
            msg = 'No features of chosen "feature_source" options {} detected. ' \
                  'Empty Data Set.'.format(str(self.feature_source))
            raise EmptyDataSetError(msg, feature_source=self.feature_source)

        # item ids not included in feature df which don't have features at all
        initial_id_set = set(target_qs.values_list(target_id_field, flat=True))
        feature_id_set = set(df.index.tolist())
        unqualified_item_ids = sorted(list(initial_id_set.difference(feature_id_set)))

        print('count unqualified_item_ids: ', len(unqualified_item_ids))

        if not self.drop_empty_rows and unqualified_item_ids:
            unqualified_items_df = pd.SparseDataFrame(index=unqualified_item_ids, columns=df.columns).fillna(0)

            print('unqualified_items_df size: ', unqualified_items_df.memory_usage().sum())
            print('unqualified_items_df shape: ', unqualified_items_df.shape)

            df = df.join(unqualified_items_df, how='outer')

            print('df size: ', df.memory_usage().sum())
            print('df shape: ', df.shape)

        return df, unqualified_item_ids

    def get_features(self):
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


class TextUnitFeatures(DocumentFeatures):
    """
    Collects features for TextUnits
    See DocumentFeatures docstring.
    """

    source_model = TextUnit
    project_filter_key = 'document__project_id'
    unit_type_filter = 'unit_type'

    source_fields = dict(
        source_type='document__source_type',
        document_type='document__document_type',
        metadata='document__documentmetadata__metadata',
        court='courtusage__court__name',
        currency_name='currencyusage__currency',
        currency_value='currencyusage__amount',
        date='dateusage__date',
        definition='definitionusage__definition',
        duration='datedurationusage__duration_days',
        term='termusage__term__term',
        party='partyusage__party__name',
        geoentity='geoentityusage__entity__name')

    aggregation_functions = dict(
        source_type=Value('document__source_type'),
        document_type=Value('document__document_type'),
        metadata=Value('document__documentmetadata__metadata'),
        date=Sum('dateusage__count'),
        definition=Sum('definitionusage__count'),
        duration=Sum('datedurationusage__count'),
        court=Sum('courtusage__count'),
        currency_name=Sum('currencyusage__count'),
        currency_value=Sum('currencyusage__count'),
        term=Sum('termusage__count'),
        party=Sum('partyusage__count'),
        geoentity=Sum('geoentityusage__count'))

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
        super().check()
        if self.queryset is None and self.project_id is None:
            raise RuntimeError(
                '''Without providing either "queryset" or "project_id"
                argument executing the task may be impossible.''')
